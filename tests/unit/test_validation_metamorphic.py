from __future__ import annotations

from copy import deepcopy

from lib.validation_oracles import calculate


def test_pt_status_uses_atomic_consolidation_precedence_and_transition_date():
    rows = [
        {
            "_extractor": "pt_status_planos",
            "plano_trabalho_id": "P1",
            "unidade_sigla": "U1",
            "status_codigo": "ATIVO",
            "plano_updated_at": "2026-08-01T00:00:00",
        },
        {
            "_extractor": "pt_status_consolidacoes",
            "plano_trabalho_id": "P1",
            "consolidacao_id": "C1",
            "consolidacao_status": "CONCLUIDO",
        },
        {
            "_extractor": "pt_status_transicoes",
            "plano_trabalho_id": "P1",
            "status_codigo_transicao": "ATIVO",
            "status_created_at": "2026-08-02T00:00:00",
        },
    ]
    assert calculate("G01", rows) == [
        {"unidade_sigla": "U1", "status_negocio": "Aguardando avaliação", "qtd_planos": 1}
    ]


def test_i02_duplicate_input_is_deduplicated_by_business_key():
    base = {
        "periodo": "Q1-2026",
        "unidade_sigla": "U1",
        "id_entrega": "E1",
        "meta_planejada": 100,
        "meta_executada": 100,
        "vence_no_periodo": True,
    }
    single = calculate("I02", [base])[0]
    duplicated = calculate("I02", [base, deepcopy(base)])[0]
    assert single["total_no_ciclo"] == 1
    assert duplicated == single


def test_deleted_and_out_of_window_rows_are_neutral_together():
    base = {
        "periodo": "M01-2026",
        "unidade_sigla": "U1",
        "id_servidor": "S1",
        "id_entrega": "E1",
    }
    contaminated = [
        base,
        {**base, "id_entrega": "E2", "deleted_at": "2026-08-01"},
        {**base, "id_entrega": "E3", "in_window": False},
    ]
    assert calculate("I05", contaminated) == calculate("I05", [base])
