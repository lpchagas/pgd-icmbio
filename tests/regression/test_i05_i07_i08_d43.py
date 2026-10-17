"""D43: I05 3.0.2 (média exata em Python), I07 e I08 3.2.0 (força de trabalho fora de 0–100).

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
from lib.validation_diagnostics import diagnose_atomic
from lib.validation_oracles import calculate

pytestmark = pytest.mark.regression

RAIZ = Path(__file__).resolve().parents[2]


def _fonte(numero: str) -> Path:
    return RAIZ / "ocde" / "indicadores" / f"IND_OCDE_{numero}.1_run.py"


def _sql(numero: str, constante: str | None = None) -> str:
    fonte = _fonte(numero).read_text(encoding="utf-8")
    return re.search(rf'{constante or f"SQL_I{numero}"}\s*=\s*"""(.*?)"""', fonte, re.DOTALL).group(1)


def _a1(numero: str):
    nome = f"a1_ind_ocde_{numero}_d43"
    spec = importlib.util.spec_from_file_location(nome, _fonte(numero))
    modulo = importlib.util.module_from_spec(spec)
    sys.modules[nome] = modulo
    spec.loader.exec_module(modulo)
    return modulo


def test_versoes_de_formula_sobem():
    assert TARGETS["I05"].formula_version == "3.0.2"
    assert TARGETS["I07"].formula_version == "3.2.0"
    assert TARGETS["I08"].formula_version == "3.2.0"


# --- I05: média exata (Q3) ----------------------------------------------------------------

_COLUNAS_I05 = ["unidade_sigla", "unidade_nome", "id_servidor", "nome_servidor", "qtd_entregas_por_servidor"]


def test_sql_i05_so_devolve_contagens_e_filtra_soft_delete():
    sql = _sql("05")
    assert "ROUND(" not in sql and "AVG(" not in sql
    assert "un.deleted_at IS NULL" in sql and "us.deleted_at IS NULL" in sql


def test_a1_i05_media_exata_meio_para_cima_e_posicao():
    a1 = _a1("05")
    # 40 servidores, 143 entregas: média exata 3,575 → 3,58 (a média em ponto flutuante
    # do Denodo, 3,57499…, levava a 3,57).
    contagens = [4] * 23 + [3] * 17
    assert sum(contagens) == 143
    linhas = [["U1", "Unid 1", f"S{i}", f"Nome {i}", str(c)] for i, c in enumerate(contagens)]
    saida = a1.montar_v1(_COLUNAS_I05, linhas)
    valores = [dict(zip(a1.COLUNAS_V1, linha)) for linha in saida]
    assert {v["media_entregas_por_servidor_unidade"] for v in valores} == {"3.58"}
    assert {v["posicao_relativa_media"] for v in valores if v["qtd_entregas_por_servidor"] == "4"} == {"Acima da media"}
    assert {v["posicao_relativa_media"] for v in valores if v["qtd_entregas_por_servidor"] == "3"} == {"Abaixo da media"}


def test_a1_i05_media_por_unidade_preserva_ordem_e_na_media():
    a1 = _a1("05")
    linhas = [["U1", "N1", "S1", "A", "2"], ["U1", "N1", "S2", "B", "2"], ["U2", "N2", "S3", "C", "1"]]
    saida = a1.montar_v1(_COLUNAS_I05, linhas)
    assert [linha[2] for linha in saida] == ["S1", "S2", "S3"]
    assert [linha[5] for linha in saida] == ["2.0", "2.0", "1.0"]
    assert {linha[6] for linha in saida} == {"Na media"}


def test_oracle_i05_media_exata_igual_ao_a1():
    registros = [
        {"periodo": "M01-2026", "unidade_sigla": "U1", "id_servidor": f"S{i}", "id_entrega": f"E{j}"}
        for i, c in enumerate([4] * 23 + [3] * 17) for j in range(c)
    ]
    estatistica = [r for r in calculate("I05", registros) if r["visao"] == "estatistica"]
    assert estatistica[0]["media_entregas_por_servidor"] == 3.58


# --- I07 e I08: força de trabalho fora de 0–100 (Q1) e PT sem carga (Q4) -----------------

def _vinculo(**extra):
    base = {
        "periodo": "Q2-2026", "unidade_sigla": "U1", "unidade_dona_sigla": "U1",
        "unidade_executora_sigla": "U1", "id_entrega": "E1", "id_servidor": "S1",
        "carga_horaria": "8", "forma_contagem_carga_horaria": "DIAS",
        "plano_inicio": "2026-06-01", "plano_fim": "2026-06-30",
        "sobreposicao_inicio": "2026-06-01", "sobreposicao_fim": "2026-06-30",
        "_extractor": "pt_entregas_dono",
    }
    base.update(extra)
    return base


def test_oracle_i07_exclui_forca_invalida_e_pt_sem_carga():
    registros = [
        _vinculo(plano_trabalho_id="P1", forca_trabalho="50"),
        _vinculo(plano_trabalho_id="P2", forca_trabalho="150"),
        _vinculo(plano_trabalho_id="P3", forca_trabalho="-5"),
        _vinculo(plano_trabalho_id="P4", forca_trabalho="20", carga_horaria="0"),
        _vinculo(plano_trabalho_id="P5", forca_trabalho="20", carga_horaria=None),
    ]
    (linha,) = calculate("I07", registros)
    assert linha["num_planos_trabalho_alocados"] == 1
    so_p1 = calculate("I07", registros[:1])[0]["total_horas_planejadas_entrega"]
    assert linha["total_horas_planejadas_entrega"] == so_p1


def test_oracle_i07_entrega_so_com_vinculo_invalido_sai():
    assert calculate("I07", [_vinculo(plano_trabalho_id="P1", forca_trabalho="101")]) == []


def test_oracle_i08_exclui_forca_invalida_das_horas():
    capacidade = {
        "periodo": "Q2-2026", "unidade_sigla": "U1", "plano_trabalho_id": "P1",
        "carga_horaria": "8", "forma_contagem_carga_horaria": "DIAS",
        "plano_inicio": "2026-06-01", "plano_fim": "2026-06-30",
        "sobreposicao_inicio": "2026-06-01", "sobreposicao_fim": "2026-06-30",
        "_extractor": "pt_capacidade_unidade",
    }
    registros = [
        capacidade,
        _vinculo(plano_trabalho_id="P1", forca_trabalho="50"),
        _vinculo(plano_trabalho_id="P1", forca_trabalho="400", id_entrega="E2"),
    ]
    saida = calculate("I08", registros)
    assert {r["id_entrega"] for r in saida} == {"E1"}
    dona = next(r for r in saida if r["visao"] == "dona")
    assert dona["proporcao_horas_perc"] == 50.0


_COLUNAS_I07 = [
    "unidade_sigla", "unidade_nome", "id_entrega", "nome_entrega", "id_plano_entrega",
    "inicio_vigencia_plano_entrega", "fim_vigencia_plano_entrega", "plano_trabalho_id",
    "carga_horaria", "forma_contagem_carga_horaria", "plano_inicio", "plano_fim",
    "sobreposicao_inicio", "sobreposicao_fim", "forca_trabalho",
]


def _linha_i07(plano: str, forca: str, entrega: str = "E1") -> list[str]:
    return ["U1", "Unid 1", entrega, "Entrega", "PE1", "2026-05-01", "2026-08-31", plano,
            "8", "DIAS", "2026-06-01", "2026-06-30", "2026-06-01", "2026-06-30", forca]


def test_a1_i07_exclui_vinculo_invalido_das_horas_e_da_contagem(capsys):
    a1 = _a1("07")
    valido = a1.agregar(_COLUNAS_I07, [_linha_i07("P1", "50")])
    saida = a1.agregar(_COLUNAS_I07, [
        _linha_i07("P1", "50"), _linha_i07("P2", "150"), _linha_i07("P3", "-1"),
        _linha_i07("P4", "200", entrega="E2"),
    ])
    assert saida == valido
    assert saida[0][-1] == 1
    assert "ALERTA_QUALIDADE (D43): 3" in capsys.readouterr().out


def test_sql_i07_e_i08_filtram_soft_delete_da_unidade():
    assert "un.deleted_at IS NULL" in _sql("07")
    sql_i08 = _sql("08")
    assert "dono.deleted_at IS NULL" in sql_i08 and "exec.deleted_at IS NULL" in sql_i08


_COLUNAS_I08 = [
    "unidade_dona_sigla", "unidade_dona_nome", "unidade_executora_sigla", "unidade_executora_nome",
    "id_entrega", "nome_entrega", "plano_trabalho_id", "carga_horaria",
    "forma_contagem_carga_horaria", "plano_inicio", "plano_fim",
    "sobreposicao_inicio", "sobreposicao_fim", "forca_trabalho",
]


def test_a1_i08_exclui_vinculo_invalido_nas_duas_visoes():
    a1 = _a1("08")
    linhas = [
        ["U1", "N1", "U2", "N2", "E1", "Ent", "P1", "8", "DIAS", "2026-06-01", "2026-06-30",
         "2026-06-01", "2026-06-30", "50"],
        ["U1", "N1", "U2", "N2", "E2", "Ent", "P1", "8", "DIAS", "2026-06-01", "2026-06-30",
         "2026-06-01", "2026-06-30", "120"],
    ]
    capacidade = {"U1": 100.0, "U2": 100.0}
    for sigla, nome in (("unidade_dona_sigla", "unidade_dona_nome"),
                        ("unidade_executora_sigla", "unidade_executora_nome")):
        saida = a1._agregar_visao(_COLUNAS_I08, linhas, capacidade, sigla, nome)
        assert [linha[2] for linha in saida] == ["E1"]


# --- Validação: severidade do achado (Q1, Q2) --------------------------------------------

@pytest.mark.parametrize("alvo, severidade", [
    ("I05", "alerta"), ("I06", "alerta"), ("I07", "alerta"), ("I08", "alerta"), ("G02", "bloqueante"),
])
def test_forca_de_trabalho_fora_da_faixa_por_alvo(alvo, severidade):
    achados = diagnose_atomic(alvo, [{"forca_trabalho": "150"}])
    (achado,) = [a for a in achados if "força de trabalho" in a["mensagem"]]
    assert achado["severidade"] == severidade
