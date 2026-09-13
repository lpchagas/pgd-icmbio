from datetime import date

from lib.periodos import analysis_window
from ocde.relatorios.relatorio_v2 import _eligible_shared, render_report


def evidence(unit="UC-A"):
    return {
        "lente": "acumulada", "tipo_registro": "PE", "unidade_dona_sigla": unit,
        "unidade_executora_sigla": unit, "plano_numero": "PE-1", "status": "ATIVO",
        "data_fim": "2026-08-31", "texto_principal": "Entrega de fiscalização",
        "pontuacao_prioridade": 75, "prioridade": "crítica",
        "gatilhos": ["prazo_vencido_sem_conclusao"],
    }


def test_shareable_requires_k_for_every_named_unit():
    assert _eligible_shared([evidence()], {"UC-A": 4}) == []
    assert _eligible_shared([evidence()], {"UC-A": 5}) == [evidence()]


def test_v2_states_separation_between_pe_and_pt():
    report = render_report(
        window=analysis_window(date(2026, 9, 12)), scope_label="GR2", product="restrito",
        cumulative=[], temporal=[], evidence=[evidence()], denodo_used=True,
    )
    assert "Atividades de PT não são usadas como prova" in report
    assert "Unidade dona do PE e unidade executora" in report
    assert "01/07/2025 a 31/08/2026" in report
