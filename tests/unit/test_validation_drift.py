from lib.validation_contracts import DriftPolicy
from lib.validation_drift import assess_drift, population_stability_index


def test_psi_zero_for_equal_distributions():
    assert population_stability_index({"a": 5, "b": 5}, {"a": 10, "b": 10}) == 0.0


def test_schema_change_is_blocking():
    findings = assess_drift(
        {"colunas": ["a", "b"], "linhas": 10, "nulos": {}},
        {"colunas": ["a"], "linhas": 10, "nulos": {}},
        DriftPolicy(),
    )
    assert findings[0]["classe"] == "MUDANCA_DE_SCHEMA"
    assert findings[0]["severidade"] == "bloqueante"


def test_null_and_volume_thresholds():
    findings = assess_drift(
        {"colunas": ["a"], "linhas": 170, "nulos": {"a": 20}},
        {"colunas": ["a"], "linhas": 100, "nulos": {"a": 0}},
        DriftPolicy(),
    )
    assert {item["classe"] for item in findings} == {"DRIFT_RELEVANTE"}
    assert {item["severidade"] for item in findings} == {"bloqueante"}

def test_cumulative_growth_outside_closed_common_cycles_is_not_drift():
    baseline = {
        "colunas": ["periodo"], "linhas": 200, "nulos": {},
        "volumetria_periodos_fechados": {"Q1-2026": 100, "Q2-2026": 100},
    }
    current = {
        "colunas": ["periodo"], "linhas": 1200, "nulos": {},
        "volumetria_periodos_fechados": {
            "Q1-2026": 100, "Q2-2026": 100, "Q3-2026": 1000
        },
    }
    assert assess_drift(current, baseline, DriftPolicy()) == []


def test_material_change_in_closed_common_cycle_is_blocking():
    baseline = {
        "colunas": ["periodo"], "linhas": 100, "nulos": {},
        "volumetria_periodos_fechados": {"Q1-2026": 100},
    }
    current = {
        "colunas": ["periodo"], "linhas": 170, "nulos": {},
        "volumetria_periodos_fechados": {"Q1-2026": 170},
    }
    findings = assess_drift(current, baseline, DriftPolicy())
    assert findings[0]["severidade"] == "bloqueante"
    assert "ciclo fechado" in findings[0]["mensagem"]
