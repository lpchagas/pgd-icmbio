from pathlib import Path

import pytest

import relatorios.escopo as escopo
from lib.unidades_petrvs import HierarquiaPetrvs, UnidadePetrvs
from ocde.relatorios.escopo import EscopoInvalido, ScopeSpec, UnitProfile, filter_rows, scope_from_values

pytestmark = pytest.mark.unit

ROWS = [
    {"unidade_sigla": "GR2", "mesogrupo": "GR2"},
    {"unidade_sigla": "UC-A", "mesogrupo": "UC na GR2"},
    {"unidade_sigla": "CT-X", "mesogrupo": "GR2"},
    {"unidade_sigla": "UC-B", "mesogrupo": "UC na GR1"},
]


def _hierarquia(*args) -> HierarquiaPetrvs:
    unidades = [UnidadePetrvs("1", "1", "GR2", "GR2", ""), UnidadePetrvs("2", "2", "UC-A", "UC-A", "1"),
                UnidadePetrvs("3", "3", "CT-X", "CT-X", "1"), UnidadePetrvs("4", "4", "UC-B", "UC-B", "")]
    return HierarquiaPetrvs({u.id: u for u in unidades})


def test_regional_gr2_inclui_regional_e_vinculadas(monkeypatch):
    monkeypatch.setattr(escopo, "carregar_hierarquia", _hierarquia)
    result = filter_rows(ROWS, scope_from_values(regional="GR2"))
    assert {row["unidade_sigla"] for row in result} == {"GR2", "UC-A", "CT-X"}


def test_regional_sem_unidades_resolvidas_e_erro():
    with pytest.raises(EscopoInvalido):
        filter_rows(ROWS, ScopeSpec("regional", "GR2"))


def test_unidade_exata_sem_fallback_nacional():
    assert filter_rows(ROWS, ScopeSpec("unidade", "INEXISTENTE")) == []


def test_tipo_unidade_usa_estrutura():
    profiles = {"UC-A": UnitProfile("UC-A", "UC na GR2", "UC")}
    result = filter_rows(ROWS, ScopeSpec("tipo_unidade", "UC"), profiles)
    assert [row["unidade_sigla"] for row in result] == ["UC-A"]


def test_seletores_sao_mutuamente_exclusivos():
    with pytest.raises(ValueError):
        scope_from_values(regional="GR2", unidade="UC-A")


def test_lista_nao_persiste_caminho(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(escopo, "carregar_hierarquia", _hierarquia)
    path = tmp_path / "lista.csv"
    path.write_text("sigla\nUC-A\nCT-X\n", encoding="utf-8")
    scope = scope_from_values(lista_unidades=path)
    assert scope.value == "LISTA_FORNECIDA"
    assert scope.units == frozenset({"UC-A", "CT-X"})
    assert scope.as_dict()["valor"] == "LISTA_FORNECIDA"
    assert scope.key.startswith("lista_unidades-") and "lista" not in scope.key.split("-", 1)[1]
    assert scope.label == "Lista de unidades selecionada"
