"""D39 (I03 3.1.0): realizado negativo não gera taxa, na produção e no oracle.

Sem abrir o Denodo: o A1 é importado como módulo (sem executar ``main``) e o SQL é lido
do código-fonte.
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import pytest

from lib.validation_contracts import TARGETS
from lib.validation_oracles import calculate

pytestmark = pytest.mark.regression

RAIZ = Path(__file__).resolve().parents[2]
FONTE_A1 = RAIZ / "ocde" / "indicadores" / "IND_OCDE_03.1_run.py"


def _a1():
    nome = "a1_ind_ocde_03_d39"
    spec = importlib.util.spec_from_file_location(nome, FONTE_A1)
    modulo = importlib.util.module_from_spec(spec)
    sys.modules[nome] = modulo
    spec.loader.exec_module(modulo)
    return modulo


def test_contrato_do_i03_sobe_para_3_1_0():
    assert TARGETS["I03"].formula_version == "3.1.0"


def test_oracle_deixa_taxa_vazia_e_marca_dado_inconsistente():
    linhas = [
        {"periodo": "Q2-2026", "unidade_sigla": "U1", "id_entrega": "E1",
         "meta_planejada": 100, "meta_executada": -200},
        {"periodo": "Q2-2026", "unidade_sigla": "U1", "id_entrega": "E2",
         "meta_planejada": 100, "meta_executada": 0},
    ]
    negativa, zerada = calculate("I03", linhas)
    assert negativa["taxa_atingimento_perc"] == ""
    assert negativa["status_entrega"] == "Dado inconsistente"
    assert negativa["meta_executada"] == -200.0  # realizado bruto preservado
    assert zerada["taxa_atingimento_perc"] == 0.0
    assert zerada["status_entrega"] == "Nao executada"


def test_sql_anula_taxa_e_classifica_pelo_realizado():
    fonte = FONTE_A1.read_text(encoding="utf-8")
    sql = re.search(r'SQL_I03\s*=\s*"""(.*?)"""', fonte, re.DOTALL).group(1)
    assert re.search(r"WHEN meta_executada < 0 THEN NULL", sql)
    assert re.search(r"WHEN meta_executada\s+<\s+0 THEN 'Dado inconsistente'", sql)
    assert "WHEN taxa_atingimento_perc <    0" not in sql


def test_meta_integral_sem_taxa_para_realizado_negativo():
    a1 = _a1()
    assert a1.parse_meta_integral('{"quantitativo": 10}', '{"quantitativo": -1}') == (
        "", "Dado inconsistente", "quantitativo",
    )
    assert a1.parse_meta_integral('{"porcentagem": 100}', '{"porcentagem": 50}') == (
        "50.0", "Em andamento", "porcentagem",
    )
