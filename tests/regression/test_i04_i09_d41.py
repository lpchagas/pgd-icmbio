"""D41: I04 2.1.0 (sem ABS, realizado negativo fora da média) e I09 3.0.2 (D24 em Python).

Sem abrir o Denodo: os A1 são importados como módulo (sem executar ``main``) e o SQL é
lido do código-fonte.
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


def _fonte(numero: str) -> Path:
    return RAIZ / "ocde" / "indicadores" / f"IND_OCDE_{numero}.1_run.py"


def _sql(numero: str) -> str:
    fonte = _fonte(numero).read_text(encoding="utf-8")
    return re.search(rf'SQL_I{numero}\s*=\s*"""(.*?)"""', fonte, re.DOTALL).group(1)


def _a1(numero: str):
    nome = f"a1_ind_ocde_{numero}_d41"
    spec = importlib.util.spec_from_file_location(nome, _fonte(numero))
    modulo = importlib.util.module_from_spec(spec)
    sys.modules[nome] = modulo
    spec.loader.exec_module(modulo)
    return modulo


def test_versoes_de_formula_sobem():
    assert TARGETS["I04"].formula_version == "2.1.0"
    assert TARGETS["I09"].formula_version == "3.0.2"


def test_oracle_i04_tira_negativo_da_media_e_mantem_no_ciclo():
    linhas = [
        {"periodo": "Q1-2026", "unidade_sigla": "U1", "id_entrega": "E1",
         "meta_planejada": 100, "meta_executada": 80},
        {"periodo": "Q1-2026", "unidade_sigla": "U1", "id_entrega": "E2",
         "meta_planejada": 100, "meta_executada": -200},
    ]
    (resultado,) = calculate("I04", linhas)
    assert resultado["total_no_ciclo"] == 2
    assert resultado["score_atingimento_perc"] == 80.0


def test_oracle_i04_omite_unidade_so_com_negativos():
    linha = {"periodo": "Q1-2026", "unidade_sigla": "U1", "id_entrega": "E1",
             "meta_planejada": 100, "meta_executada": -1}
    assert calculate("I04", [linha]) == []


def test_sql_i04_sem_abs_e_sem_unidade_sem_score():
    sql = _sql("04")
    assert "ABS(" not in sql
    assert "WHEN COALESCE(pee.progresso_realizado, 0) < 0 THEN NULL" in sql
    assert "WHERE r.score_atingimento_perc IS NOT NULL" in sql


def test_sql_i09_nao_arredonda_as_medias():
    sql = _sql("09")
    assert "ROUND(" not in sql


def test_a1_i09_arredonda_meio_para_cima_e_recalcula_a_faixa():
    a1 = _a1("09")
    colunas = ["unidade_sigla", "media_nota_pt", "media_nota_pt_eventos", "faixa_desempenho"]
    linha = a1.arredondar_medias(colunas, ["U1", "3.575", "3.4949", "Alto desempenho"])
    assert linha == ["U1", "3.58", "3.49", "Alto desempenho"]
    # 3.495 arredonda para 3.5: a faixa segue o valor publicado, não o bruto do VQL.
    linha = a1.arredondar_medias(colunas, ["U1", "3.495", "3.495", "Adequado"])
    assert linha[1] == "3.5" and linha[3] == "Alto desempenho"
