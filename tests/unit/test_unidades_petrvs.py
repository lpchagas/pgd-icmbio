"""Hierarquia de unidades do PETRVS usada na resolução de escopos (L7)."""
from __future__ import annotations

import json

import pytest

from lib.unidades_petrvs import HierarquiaPetrvs, UnidadePetrvs, carregar_hierarquia
from tools import atualizar_unidades_petrvs

pytestmark = pytest.mark.unit


def test_retrato_ausente_devolve_hierarquia_vazia(tmp_path):
    hierarquia = carregar_hierarquia(tmp_path / "PETRVS_unidades.csv")
    assert hierarquia.unidades == {} and hierarquia.sha256 == ""


def test_retrato_sem_colunas_obrigatorias_e_erro(tmp_path):
    caminho = tmp_path / "PETRVS_unidades.csv"
    caminho.write_text("id|sigla\nx|GR2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="nome, unidade_pai_id"):
        carregar_hierarquia(caminho)


def test_hash_identifica_o_retrato(fixtures_dir, tmp_path):
    original = fixtures_dir / "escopo" / "PETRVS_unidades.csv"
    copia = tmp_path / "PETRVS_unidades.csv"
    copia.write_bytes(original.read_bytes() + b"p-nova|99|NOVA|Nova|p-gr2\n")

    assert carregar_hierarquia(original).sha256 != carregar_hierarquia(copia).sha256
    assert len(carregar_hierarquia(copia).unidades) == len(carregar_hierarquia(original).unidades) + 1


def test_descendentes_em_largura_raiz_primeiro_e_sem_ciclo():
    unidades = [UnidadePetrvs("a", "1", "A", "A", "c"), UnidadePetrvs("b", "2", "B", "B", "a"),
                UnidadePetrvs("c", "3", "C", "C", "b")]  # ciclo a → b → c → a
    hierarquia = HierarquiaPetrvs({u.id: u for u in unidades})

    assert [u.id for u in hierarquia.descendentes("a")] == ["a", "b", "c"]


def test_por_sigla_normaliza_caixa_e_espacos(hierarquia_petrvs_sintetica):
    assert [u.id for u in hierarquia_petrvs_sintetica.por_sigla(" cgov ")] == ["p-cgov"]
    assert len(hierarquia_petrvs_sintetica.por_sigla("UC-DUP")) == 2


def test_atualizacao_dry_run_nao_conecta(capsys):
    assert atualizar_unidades_petrvs.main(["--dry-run"]) == 0
    saida = json.loads(capsys.readouterr().out)
    assert "deleted_at IS NULL" in saida["consulta"] and saida["destino"].endswith("PETRVS_unidades.csv")
