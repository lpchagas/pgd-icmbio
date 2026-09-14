from __future__ import annotations

from hypothesis import given, strategies as st

from lib.validation_oracles import calculate


@given(
    planned=st.floats(min_value=1.01, max_value=1_000_000, allow_nan=False, allow_infinity=False),
    actual=st.floats(min_value=0, max_value=2_000_000, allow_nan=False, allow_infinity=False),
)
def test_i03_rate_is_the_ratio_of_actual_to_normalized_goal(planned, actual):
    row = {
        "periodo": "Q1-2026",
        "unidade_sigla": "U1",
        "id_entrega": "E1",
        "meta_planejada": planned,
        "meta_executada": actual,
    }
    result = calculate("I03", [row])[0]
    assert result["taxa_atingimento_perc"] == round(100 * actual / planned, 2)


@given(st.integers(min_value=1, max_value=5))
def test_score_inversion_always_stays_on_one_to_five_scale(sequence):
    row = {
        "periodo": "M01-2026",
        "unidade_sigla": "U1",
        "id_avaliacao": "A1",
        "id_servidor": "S1",
        "plano_trabalho_id": "P1",
        "sequencia_nota": sequence,
    }
    score = calculate("I09", [row])[0]["media_nota_pt"]
    assert score == 6 - sequence
    assert 1 <= score <= 5


@given(st.lists(st.sampled_from(["E1", "E2", "E3"]), min_size=1, max_size=20))
def test_i05_counts_distinct_deliveries(deliveries):
    rows = [
        {
            "periodo": "M01-2026",
            "unidade_sigla": "U1",
            "id_servidor": "S1",
            "id_entrega": delivery,
        }
        for delivery in deliveries
    ]
    resultado = calculate("I05", rows)
    nominal = next(row for row in resultado if row["visao"] == "nominal")
    assert nominal["qtd_entregas_por_servidor"] == len(set(deliveries))
    # D07: a visão estatística descreve a mesma população sem identificá-la.
    estatistica = next(row for row in resultado if row["visao"] == "estatistica")
    assert estatistica["total_servidores"] == 1
    assert "id_servidor" not in estatistica
    assert estatistica["mediana_entregas_por_servidor"] == len(set(deliveries))
