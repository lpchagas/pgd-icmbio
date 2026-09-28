from datetime import date

from ocde.relatorios.textos_execucao import TextSanitizer, priority_assessment
from ocde.relatorios.analisar_execucao_pgd import _scope_sql
from ocde.relatorios.escopo import ScopeSpec


def test_sanitizer_removes_personal_data_and_keeps_business_text():
    result = TextSanitizer(["Maria da Silva"]).sanitize(
        "Maria da Silva entregará o produto; contato maria@example.org, CPF 123.456.789-01, telefone (61) 99999-0000."
    )
    assert "Maria da Silva" not in result.text
    assert "maria@example.org" not in result.text
    assert "123.456.789-01" not in result.text
    assert "99999-0000" not in result.text
    assert "entregará o produto" in result.text
    assert set(result.redactions) >= {"nome", "email", "cpf", "telefone"}


def test_sanitizer_keeps_year_ranges_and_sei_numbers():
    sanitizer = TextSanitizer(["Maria da Silva"])
    for text in (
        "Plano de Integridade do ICMBio 2025-2027 monitorado",
        "ciclo 2025 – 2027",
        "Processo SEI nº 02070.020242/2025-88",
        "Despacho Interlocutório - SEI nº 23687646",
    ):
        result = sanitizer.sanitize(text)
        assert result.text == text
        assert result.redactions == ()
    result = sanitizer.sanitize("Maria da Silva, telefone 3333-4444, ciclo 2025-2027")
    assert result.text == "[NOME_SUPRIMIDO], telefone [DADO_PESSOAL_TELEFONE], ciclo 2025-2027"
    assert set(result.redactions) == {"nome", "telefone"}


def test_pe_priority_uses_own_meta_not_pt_activity_completion():
    assessment = priority_assessment(
        {
            "tipo_registro": "PE",
            "status": "ATIVO",
            "data_fim": "2026-08-01",
            "progresso_esperado": "100",
            "progresso_realizado": "20",
        },
        date(2026, 9, 12),
    )
    assert "meta_pe_abaixo_do_pactuado" in assessment["gatilhos"]
    assert "prazo_vencido_sem_conclusao" in assessment["gatilhos"]
    assert assessment["prioridade"] == "crítica"


def test_text_query_is_restricted_to_hierarchy_units_when_available():
    scope = ScopeSpec("regional", "GR2", frozenset({"GR2", "COAGR2"}))
    clause = _scope_sql(scope, "PE")
    assert "UPPER(ud.sigla)" in clause
    assert "COAGR2" in clause
    assert _scope_sql(ScopeSpec("nacional", "NACIONAL"), "PE") == ""
