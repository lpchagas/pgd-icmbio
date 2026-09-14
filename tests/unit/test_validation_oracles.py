from __future__ import annotations

import json
from pathlib import Path

import pytest

from lib.validation_contracts import TARGETS, validate_registry
from lib.validation_oracles import calculate, independent_analysis_window


FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "validation"


def _values(name: str):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _project(rows, keys):
    return [{key: row.get(key) for key in keys} for row in rows]


def test_registry_covers_all_indicators_and_management():
    assert set(TARGETS) == {*(f"I{i:02d}" for i in range(1, 13)), "G01", "G02"}
    assert validate_registry() == []


def _fixture(code):
    if code == "G02":
        return _values("g02_atomic.json"), _values("g02_expected.json")
    return _values("atomic.json")[code], _values("expected.json")[code]


@pytest.mark.parametrize("code", sorted(TARGETS))
def test_oracle_matches_reviewed_fixture(code):
    atomic, expected = _fixture(code)
    actual = calculate(code, atomic)
    keys = sorted(set().union(*(row.keys() for row in expected)))
    assert _project(actual, keys) == _project(expected, keys)


@pytest.mark.parametrize("code", sorted(TARGETS))
def test_oracle_is_invariant_to_row_order(code):
    rows, _ = _fixture(code)
    assert calculate(code, rows) == calculate(code, list(reversed(rows)))


@pytest.mark.parametrize("code", sorted(TARGETS))
def test_soft_deleted_record_does_not_change_result(code):
    rows, _ = _fixture(code)
    deleted = {**rows[0], "deleted_at": "2026-01-01"}
    assert calculate(code, rows) == calculate(code, rows + [deleted])


def test_i03_keeps_documented_superexecution():
    values = calculate("I03", _values("atomic.json")["I03"])
    assert values[-1]["taxa_atingimento_perc"] == 120.0
    assert values[-1]["status_entrega"] == "Superexecutada"


def test_i10_and_i11_use_raw_sequence_categories():
    atomic = _values("atomic.json")
    assert calculate("I10", atomic["I10"])[0]["qtd_inadequado"] == 1
    assert calculate("I11", atomic["I11"])[0]["qtd_excepcional"] == 1


def test_i12_direction_is_pt_minus_pe():
    result = calculate("I12", _values("atomic.json")["I12"])[0]
    assert result["diferenca_direcional"] == 1.0
    assert result["direcao_divergencia"] == "PT > PE"


def test_independent_window_handles_cutoff_year_turn_and_leap_year():
    assert independent_analysis_window("2026-09-12") == (
        __import__("datetime").date(2025, 7, 1), __import__("datetime").date(2026, 8, 31)
    )
    assert independent_analysis_window("2027-01-15")[1].isoformat() == "2026-12-31"
    assert independent_analysis_window("2028-03-01")[1].isoformat() == "2028-02-29"


@pytest.mark.parametrize("code", sorted(TARGETS))
def test_oracle_is_idempotent_and_ignores_explicitly_out_of_window(code):
    rows, _ = _fixture(code)
    first = calculate(code, rows)
    assert calculate(code, rows) == first
    outside = {**rows[0], "in_window": False}
    assert calculate(code, rows + [outside]) == first


def test_i03_zero_denominator_is_excluded():
    row = {"periodo": "Q1-2026", "unidade_sigla": "U1", "id_entrega": "E0",
           "meta_planejada": 0, "meta_executada": 10}
    assert calculate("I03", [row]) == []


def test_unit_split_and_recombine_is_stable_for_i04():
    rows = _values("atomic.json")["I04"]
    whole = calculate("I04", rows)
    split = calculate("I04", [row for row in rows if row["unidade_sigla"] == "U1"])
    split += calculate("I04", [row for row in rows if row["unidade_sigla"] == "U2"])
    assert sorted(split, key=lambda row: (row["periodo"], row["unidade_sigla"])) == whole

def test_i03_treats_jdbc_string_zero_as_false():
    rows = [
        {"periodo": "Q1-2026", "unidade_sigla": "U1", "id_entrega": "E1",
         "meta_planejada": "100", "meta_executada": "50", "vence_no_periodo": "0"},
        {"periodo": "Q1-2026", "unidade_sigla": "U1", "id_entrega": "E2",
         "meta_planejada": "100", "meta_executada": "100", "vence_no_periodo": "1"},
    ]
    result = calculate("I03", rows)
    assert [row["id_entrega"] for row in result] == ["E2"]


def test_i08_uses_independent_capacity_universe():
    rows = [
        {"_extractor": "pt_entregas_dono", "periodo": "Q1-2026",
         "unidade_sigla": "U1", "id_entrega": "E1", "plano_trabalho_id": "P1",
         "id_servidor": "S1", "plano_inicio": "2026-01-01", "plano_fim": "2026-01-10",
         "sobreposicao_inicio": "2026-01-01", "sobreposicao_fim": "2026-01-10",
         "carga_horaria": "100", "forma_contagem_carga_horaria": "HORAS",
         "forca_trabalho": "50"},
        {"_extractor": "pt_capacidade_unidade", "periodo": "Q1-2026",
         "unidade_sigla": "U1", "plano_trabalho_id": "P1",
         "plano_inicio": "2026-01-01", "plano_fim": "2026-01-10",
         "sobreposicao_inicio": "2026-01-01", "sobreposicao_fim": "2026-01-10",
         "carga_horaria": "100", "forma_contagem_carga_horaria": "HORAS"},
        {"_extractor": "pt_capacidade_unidade", "periodo": "Q1-2026",
         "unidade_sigla": "U1", "plano_trabalho_id": "P2",
         "plano_inicio": "2026-01-01", "plano_fim": "2026-01-10",
         "sobreposicao_inicio": "2026-01-01", "sobreposicao_fim": "2026-01-10",
         "carga_horaria": "100", "forma_contagem_carga_horaria": "HORAS"},
    ]
    result = calculate("I08", rows)[0]
    assert result["horas_planejadas_entrega"] == 50.0
    assert result["total_horas_disponiveis_unidade"] == 200.0
    assert result["proporcao_horas_perc"] == 25.0

def test_i01_maps_technical_uuid_modality_to_not_informed():
    rows = [{
        "periodo": "M01-2026", "unidade_sigla": "U1", "id_servidor": "S1",
        "modalidade": "123e4567-e89b-12d3-a456-426614174000",
    }]
    result = calculate("I01", rows)
    assert {row["modalidade"] for row in result} == {"N.I."}
