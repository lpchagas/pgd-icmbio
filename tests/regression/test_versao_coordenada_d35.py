"""Versão coordenada D35 (decisões CGOV D22–D27, D29, D31 e D33, 27/09/2026).

Cada teste cobre uma decisão sem abrir o Denodo: A1 importados como módulo (sem
executar ``main``), oracle puro e o harness do replay com execuções sintéticas.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

from lib import validation_oracles as vo
from lib.arredondamento import arredondar
from tools import replay_producao as rp

pytestmark = pytest.mark.regression

RAIZ = Path(__file__).resolve().parents[2]


def _a1(numero: str):
    caminho = RAIZ / "ocde" / "indicadores" / f"IND_OCDE_{numero}.1_run.py"
    nome = f"a1_ind_ocde_{numero}"
    spec = importlib.util.spec_from_file_location(nome, caminho)
    modulo = importlib.util.module_from_spec(spec)
    sys.modules[nome] = modulo
    spec.loader.exec_module(modulo)
    return modulo


# --- D24: arredondamento meio para cima ---------------------------------------------------------

@pytest.mark.parametrize("valor, casas, esperado", [
    (3.925, 2, 3.93), (31.25, 1, 31.3), (2.675, 2, 2.68), (0.125, 2, 0.13), (-1.005, 2, -1.01), (10.0, 2, 10.0),
])
def test_d24_producao_e_oracle_arredondam_meio_para_cima(valor, casas, esperado):
    assert arredondar(valor, casas) == esperado == vo._arred(valor, casas)


def test_d24_oracle_nao_usa_mais_o_round_do_python():
    fonte = (RAIZ / "lib" / "validation_oracles.py").read_text(encoding="utf-8")
    codigo = re.sub(r'""".*?"""', "", fonte, flags=re.DOTALL)
    assert not re.search(r"(?<![\w.])round\(", codigo)


# --- D23: unidade sem entrega no ciclo não gera linha --------------------------------------------

def test_d23_oracle_i02_e_i04_omitem_unidade_sem_entrega_elegivel():
    registros = [
        {"periodo": "T3-2025", "unidade_sigla": "A", "id_entrega": "e1", "meta_planejada": 100, "meta_executada": 100},
        {"periodo": "T3-2025", "unidade_sigla": "B", "id_entrega": "e2", "meta_planejada": 0, "meta_executada": 0},
    ]
    assert [r["unidade_sigla"] for r in vo.oracle_i02(registros)] == ["A"]
    assert [r["unidade_sigla"] for r in vo.oracle_i04(registros)] == ["A"]


# --- D22: I03 exige plano sobreposto ao período ---------------------------------------------------

def test_d22_i03_filtra_plano_sobreposto_e_conta_o_alerta():
    fonte = (RAIZ / "ocde" / "indicadores" / "IND_OCDE_03.1_run.py").read_text(encoding="utf-8")
    sql = re.search(r'SQL_I03\s*=\s*"""(.*?)"""', fonte, re.DOTALL).group(1)
    assert "CAST(pe.data_inicio AS DATE) <= p.data_fim" in sql
    assert "CAST(pe.data_fim AS DATE) >= p.data_inicio" in sql
    assert "ALERTA_QUALIDADE (D22)" in fonte
    ficha = (RAIZ / "docs" / "ocde" / "06.2.2-i03.md").read_text(encoding="utf-8")
    assert "CAST(pe.data_inicio AS DATE) <= p.data_fim" in ficha


# --- D25: vínculo plano de trabalho × entrega conta uma vez ---------------------------------------

def _linha_i07(pt: str) -> dict:
    return {
        "unidade_sigla": "U", "unidade_nome": "Unidade", "id_entrega": "e1", "nome_entrega": "Entrega",
        "id_plano_entrega": "pe1", "inicio_vigencia_plano_entrega": "2026-03-01",
        "fim_vigencia_plano_entrega": "2026-06-30", "plano_trabalho_id": pt, "carga_horaria": "8",
        "forma_contagem_carga_horaria": "HORAS", "plano_inicio": "2026-04-01", "plano_fim": "2026-04-30",
        "sobreposicao_inicio": "2026-04-01", "sobreposicao_fim": "2026-04-30", "forca_trabalho": "50.00",
    }


def test_d25_i07_ignora_vinculo_repetido_e_alerta(capsys):
    a1 = _a1("07")
    colunas = list(_linha_i07("x"))
    unico = a1.agregar(colunas, [list(_linha_i07("pt1").values()), list(_linha_i07("pt2").values())])
    repetido = a1.agregar(colunas, [list(_linha_i07(pt).values()) for pt in ("pt1", "pt1", "pt1", "pt2")])

    assert repetido == unico
    assert "ALERTA_QUALIDADE (D25): 2 vínculo(s)" in capsys.readouterr().out


def test_d25_i08_ignora_vinculo_repetido_nas_duas_visoes():
    a1 = _a1("08")
    colunas = ["unidade_dona_sigla", "unidade_dona_nome", "id_entrega", "nome_entrega", "plano_trabalho_id",
               "carga_horaria", "forma_contagem_carga_horaria", "plano_inicio", "plano_fim",
               "sobreposicao_inicio", "sobreposicao_fim", "forca_trabalho"]
    linha = lambda pt: ["U", "Unidade", "e1", "Entrega", pt, "8", "HORAS", "2026-04-01", "2026-04-30",  # noqa: E731
                        "2026-04-01", "2026-04-30", "50.00"]
    capacidade = {"U": 100.0}
    unico = a1._agregar_visao(colunas, [linha("pt1")], capacidade, "unidade_dona_sigla", "unidade_dona_nome")
    repetido = a1._agregar_visao(colunas, [linha("pt1")] * 3, capacidade, "unidade_dona_sigla", "unidade_dona_nome")
    assert repetido == unico


# --- D33: falha de período encerra o A1 sem gravar ------------------------------------------------

@pytest.mark.parametrize("numero", [f"{n:02d}" for n in range(2, 13)])
def test_d33_nenhum_a1_engole_falha_de_periodo(numero):
    fonte = (RAIZ / "ocde" / "indicadores" / f"IND_OCDE_{numero}.1_run.py").read_text(encoding="utf-8")
    assert not re.search(r'print\(f"  ERRO: \{exc\}"\)\s*\n\s*continue', fonte)
    assert f'raise SystemExit(f"ERRO: I{numero} {{label}}' in fonte


def test_d33_replay_de_periodo_sem_linhas_termina_com_erro(tmp_path):
    """Sem linhas congeladas para um período, o A1 corrente falha em vez de seguir."""

    fixtures = tmp_path / "I02"
    fixtures.mkdir()
    original = json.loads((rp.FIXTURES_DIR / "I02" / "consultas.json").read_text(encoding="utf-8"))
    original["consultas"] = original["consultas"][1:]  # some o primeiro período
    (fixtures / "consultas.json").write_text(json.dumps(original, ensure_ascii=False), encoding="utf-8")

    relatorio = rp.replay("I02", str(RAIZ), str(RAIZ), "2026-09-13", fixtures=fixtures)
    assert relatorio["status"] == "erro"
    assert "terminou com código" in relatorio["erro"]


# --- D27: supressão do G02 compartilhável por propriedades ----------------------------------------

def _g02(unidade: str, entrega: str, servidores: int) -> dict:
    return {"visao": "acumulada", "periodo": "Q1-2026", "unidade_sigla": unidade, "id_entrega": entrega,
            "total_servidores": servidores, "taxa_atingimento_perc": 50.0}


CHAVES = ("visao", "periodo", "unidade_sigla", "id_entrega")
PLANOS = [{"_extractor": "g02_planos", "id_servidor": f"s{i}"} for i in range(8)]
ORACLE = [_g02("A", "e1", 7), _g02("A", "e2", 6), _g02("A", "e3", 2), _g02("B", "e4", 9)]


def test_d27_supressao_correta_passa_e_devolve_as_celulas_visiveis():
    # A perde e3 (<5) e uma complementar (a menor visível: e2); B fica inteira.
    producao = [_g02("A", "e1", 7), _g02("B", "e4", 9)]
    esperado, achados = vo.verificar_supressao_compartilhavel(producao, ORACLE, PLANOS, CHAVES)
    assert achados == []
    assert sorted(r["id_entrega"] for r in esperado) == ["e1", "e4"]


@pytest.mark.parametrize("producao, trecho", [
    ([_g02("A", "e1", 7), _g02("A", "e3", 2), _g02("B", "e4", 9)], "abaixo de k"),
    ([_g02("A", "e1", 7), _g02("A", "e2", 6), _g02("B", "e4", 9)], "supressão complementar"),
    ([_g02("A", "e1", 7), _g02("B", "e4", 9), _g02("C", "e9", 8)], "inexistente"),
])
def test_d27_supressao_incorreta_e_bug(producao, trecho):
    _, achados = vo.verificar_supressao_compartilhavel(producao, ORACLE, PLANOS, CHAVES)
    assert any(trecho in a["mensagem"] for a in achados)


def test_d27_escopo_abaixo_de_k_nao_publica_nada():
    poucos = PLANOS[:3]
    assert vo.verificar_supressao_compartilhavel([], ORACLE, poucos, CHAVES) == ([], [])
    _, achados = vo.verificar_supressao_compartilhavel([_g02("B", "e4", 9)], ORACLE, poucos, CHAVES)
    assert achados and "abaixo de k" in achados[0]["mensagem"]


# --- Harness do replay: entrada opcional ----------------------------------------------------------

def _execucao(consultas: list[tuple[str, str]]) -> dict:
    return {
        "returncode": 0, "stdout": "", "stderr": "", "colisoes": [], "arquivos": {"x.csv": "x"},
        "registro": {"ativo": True, "fora_da_raiz": [],
                     "consultas": [{"inicio": "2026-01-01", "fim": "2026-04-30", "nome": n, "servida": True}
                                   for n, _ in consultas]},
    }


@pytest.mark.parametrize("servidas, valido", [
    ([("", "")], True),                                   # versão sem a consulta opcional
    ([("", ""), ("alerta_d22", "")], True),               # versão que a emite
    ([("", ""), ("alerta_d22", ""), ("alerta_d22", "")], False),  # repetida
    ([("alerta_d22", "")], False),                        # falta a obrigatória
])
def test_harness_aceita_entrada_opcional_zero_ou_uma_vez(tmp_path, servidas, valido):
    (tmp_path / "consultas.json").write_text(json.dumps({"consultas": [
        {"inicio": "2026-01-01", "fim": "2026-04-30"},
        {"inicio": "2026-01-01", "fim": "2026-04-30", "nome": "alerta_d22", "opcional": True},
    ]}), encoding="utf-8")
    if valido:
        rp._validar_execucao("candidato", _execucao(servidas), tmp_path)
    else:
        with pytest.raises(rp.ReplayError, match="diferem das fixtures"):
            rp._validar_execucao("candidato", _execucao(servidas), tmp_path)


# --- D31: rótulo do I11 --------------------------------------------------------------------------

def test_d31_i11_rotulo_neutro_e_faixa_so_com_volume():
    fonte = (RAIZ / "ocde" / "indicadores" / "IND_OCDE_11.1_run.py").read_text(encoding="utf-8")
    sql = re.search(r'SQL_I11\s*=\s*"""(.*?)"""', fonte, re.DOTALL).group(1)
    assert "Escala subutilizada" not in sql
    assert "'Uso baixo da nota máxima'" in sql
    assert sql.index("'Amostra insuficiente'") < sql.index("'Reconhecimento elevado'")


# --- Soft-delete da consolidação (correção na revalidação) ----------------------------------------

@pytest.mark.parametrize("numero, variavel", [("09", "SQL_I09"), ("10", "SQL_I10"), ("11", "SQL_I11"), ("12", "SQL_I12")])
def test_avaliacoes_de_pt_filtram_consolidacao_excluida(numero, variavel):
    fonte = (RAIZ / "ocde" / "indicadores" / f"IND_OCDE_{numero}.1_run.py").read_text(encoding="utf-8")
    sql = re.search(variavel + r'\s*=\s*"""(.*?)"""', fonte, re.DOTALL).group(1)
    assert "consolidacoes ptc" in sql
    assert "ptc.deleted_at IS NULL" in sql
