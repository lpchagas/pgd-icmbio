import pytest

from ocde.relatorios.expansao import initial_state, register_execution

pytestmark = pytest.mark.unit


def register(state, kind, value, **kwargs):
    return register_execution(
        state, scope_kind=kind, scope_value=value, month="2026-09",
        technical_ok=True, **kwargs,
    )


def test_gr2_sozinha_nunca_conclui_projeto():
    state = register(
        initial_state(), "regional", "GR2",
        management_review=True, privacy_review=True,
    )
    assert state["fase"] == "expansao_nacional_obrigatoria"
    assert state["projeto_concluido"] is False


def test_nacional_ainda_exige_todos_os_seletores():
    state = register(initial_state(), "regional", "GR2", management_review=True, privacy_review=True)
    state = register(state, "nacional", "NACIONAL", national_approved=True, national_reconciled=True)
    assert state["fase"] == "validacao_seletores_obrigatoria"
    assert state["projeto_concluido"] is False


def test_conclusao_exige_nacional_e_quatro_seletores():
    state = register(initial_state(), "regional", "GR2", management_review=True, privacy_review=True)
    state = register(state, "nacional", "NACIONAL", national_approved=True, national_reconciled=True)
    for kind in ("unidade", "mesogrupo", "tipo_unidade", "lista_unidades"):
        state = register(state, kind, "TESTE")
    assert state["fase"] == "concluido"
    assert state["projeto_concluido"] is True
