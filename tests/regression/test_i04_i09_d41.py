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
    assert TARGETS["I09"].formula_version == "3.0.3"


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


def test_sql_i09_so_devolve_contagens_inteiras():
    fonte = _fonte("09").read_text(encoding="utf-8")
    for constante in ("SQL_I09", "PLANOS_I09_SQL"):
        sql = re.search(rf'{constante}\s*=\s*"""(.*?)"""', fonte, re.DOTALL).group(1)
        assert "ROUND(" not in sql and "AVG(" not in sql


_COLUNAS = ["unidade_sigla", "unidade_nome", "total_avaliacoes_pt", "total_planos_com_avaliacao",
            "total_servidores_avaliados", "nota_minima", "nota_maxima",
            "qtd_nota_1", "qtd_nota_2", "qtd_nota_3", "qtd_nota_4", "qtd_nota_5"]
_PLANOS = ["unidade_sigla", "unidade_nome", "plano_trabalho_id", "soma_notas_plano", "qtd_avaliacoes_plano"]


def test_a1_i09_media_exata_e_meio_para_cima():
    a1 = _a1("09")
    # Planos com médias 4, 3 (=6/2), 3,7 (=37/10) e 3,6 (=18/5): média exata 3,575 → 3,58,
    # que a média em ponto flutuante (3,57499…) levava a 3,57.
    planos = [["U1", "Unid 1", "P1", "4", "1"], ["U1", "Unid 1", "P2", "6", "2"],
              ["U1", "Unid 1", "P3", "37", "10"], ["U1", "Unid 1", "P4", "18", "5"]]
    # Eventos: 18 avaliações, soma 65 → 3,6111… → 3,61.
    linha = ["U1", "Unid 1", "18", "4", "3", "2", "5", "0", "1", "6", "10", "1"]
    (saida,) = a1.montar_linhas(_COLUNAS, [linha], _PLANOS, planos)
    valor = dict(zip(a1.COLUNAS_I09, saida))
    assert valor["media_nota_pt"] == "3.58"
    assert valor["media_nota_pt_eventos"] == "3.61"
    assert valor["faixa_desempenho"] == "Alto desempenho"


def test_a1_i09_faixa_segue_a_media_arredondada_e_ordem_por_media():
    a1 = _a1("09")
    # U1: planos 3 e 3,99 → 3,495 → 3,5 (Alto desempenho, não Adequado); U2: plano 5.
    planos = [["U1", "N1", "P1", "3", "1"], ["U1", "N1", "P2", "399", "100"],
              ["U2", "N2", "P3", "5", "1"]]
    linhas = [["U1", "N1", "101", "2", "1", "3", "4", "0", "0", "1", "100", "0"],
              ["U2", "N2", "1", "1", "1", "5", "5", "0", "0", "0", "0", "1"]]
    saida = a1.montar_linhas(_COLUNAS, linhas, _PLANOS, planos)
    valores = [dict(zip(a1.COLUNAS_I09, linha)) for linha in saida]
    assert [v["unidade_sigla"] for v in valores] == ["U2", "U1"]
    assert valores[1]["media_nota_pt"] == "3.5"
    assert valores[1]["faixa_desempenho"] == "Alto desempenho"


def test_a1_i09_unidade_sem_plano_fica_sem_media():
    a1 = _a1("09")
    linha = ["U1", "N1", "0", "0", "0", "", "", "0", "0", "0", "0", "0"]
    (saida,) = a1.montar_linhas(_COLUNAS, [linha], _PLANOS, [])
    valor = dict(zip(a1.COLUNAS_I09, saida))
    assert valor["media_nota_pt"] == valor["media_nota_pt_eventos"] == valor["faixa_desempenho"] == ""
