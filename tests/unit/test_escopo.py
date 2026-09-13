from pathlib import Path

import pytest

from ocde.relatorios.escopo import ScopeSpec, UnitProfile, filter_rows, scope_from_values

pytestmark = pytest.mark.unit

ROWS = [
    {"unidade_sigla": "GR2", "mesogrupo": "GR2"},
    {"unidade_sigla": "UC-A", "mesogrupo": "UC na GR2"},
    {"unidade_sigla": "CT-X", "mesogrupo": "GR2"},
    {"unidade_sigla": "UC-B", "mesogrupo": "UC na GR1"},
]


def test_regional_gr2_inclui_regional_e_vinculadas():
    result = filter_rows(ROWS, ScopeSpec("regional", "GR2"))
    assert {row["unidade_sigla"] for row in result} == {"GR2", "UC-A", "CT-X"}


def test_unidade_exata_sem_fallback_nacional():
    assert filter_rows(ROWS, ScopeSpec("unidade", "INEXISTENTE")) == []


def test_tipo_unidade_usa_estrutura():
    profiles = {"UC-A": UnitProfile("UC-A", "UC na GR2", "UC")}
    result = filter_rows(ROWS, ScopeSpec("tipo_unidade", "UC"), profiles)
    assert [row["unidade_sigla"] for row in result] == ["UC-A"]


def test_seletores_sao_mutuamente_exclusivos():
    with pytest.raises(ValueError):
        scope_from_values(regional="GR2", unidade="UC-A")


def test_lista_nao_persiste_caminho(tmp_path: Path):
    path = tmp_path / "lista.csv"
    path.write_text("sigla\nUC-A\nCT-X\n", encoding="utf-8")
    scope = scope_from_values(lista_unidades=path)
    assert scope.value == "LISTA_FORNECIDA"
    assert scope.units == frozenset({"UC-A", "CT-X"})
    assert scope.as_dict() == {"tipo": "lista_unidades", "valor": "LISTA_FORNECIDA"}
    assert scope.label == "Lista de unidades selecionada"
