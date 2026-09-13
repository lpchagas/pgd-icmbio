"""Detecção determinística de drift para resultados analíticos."""
from __future__ import annotations

import math
from typing import Any

from .validation_contracts import DriftPolicy


def population_stability_index(
    baseline: dict[str, float], current: dict[str, float], epsilon: float = 1e-6
) -> float:
    categories = set(baseline) | set(current)
    base_total, current_total = sum(baseline.values()), sum(current.values())
    if base_total <= 0 or current_total <= 0:
        return 0.0
    value = 0.0
    for category in categories:
        expected = max(baseline.get(category, 0.0) / base_total, epsilon)
        observed = max(current.get(category, 0.0) / current_total, epsilon)
        value += (observed - expected) * math.log(observed / expected)
    return round(value, 6)


def assess_drift(
    current: dict[str, Any], baseline: dict[str, Any], policy: DriftPolicy
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if set(current.get("colunas", [])) != set(baseline.get("colunas", [])):
        findings.append({"classe": "MUDANCA_DE_SCHEMA", "severidade": "bloqueante", "mensagem": "schema diverge da baseline"})

    old_periods = baseline.get("volumetria_periodos_fechados", {})
    new_periods = current.get("volumetria_periodos_fechados", {})
    comparable = sorted(set(old_periods).intersection(new_periods))
    if comparable:
        changes = [
            abs(float(new_periods[period]) - float(old_periods[period]))
            * 100.0 / float(old_periods[period])
            for period in comparable if float(old_periods[period]) > 0
        ]
        change = max(changes, default=0.0)
        volume_label = "volumetria de ciclo fechado"
    elif not old_periods and not new_periods:
        old_rows, new_rows = baseline.get("linhas", 0), current.get("linhas", 0)
        change = abs(new_rows - old_rows) * 100.0 / old_rows if old_rows else 0.0
        volume_label = "volumetria operacional"
    else:
        # Não compara o total acumulado quando ainda não há ciclo fechado comum.
        change = 0.0
        volume_label = "volumetria sem ciclo fechado comparável"
    if change > policy.volume_blocking_pct:
        findings.append({"classe": "DRIFT_RELEVANTE", "severidade": "bloqueante", "mensagem": f"{volume_label} variou {change:.1f}%"})
    elif change > policy.volume_warning_pct:
        findings.append({"classe": "DRIFT_RELEVANTE", "severidade": "alerta", "mensagem": f"{volume_label} variou {change:.1f}%"})

    old_nulls, new_nulls = baseline.get("nulos", {}), current.get("nulos", {})
    for column in sorted(set(old_nulls) & set(new_nulls)):
        delta = new_nulls[column] - old_nulls[column]
        if delta > policy.null_blocking_pp:
            findings.append({"classe": "DRIFT_RELEVANTE", "severidade": "bloqueante", "mensagem": f"nulos em {column} aumentaram {delta:.1f} p.p."})
        elif delta > policy.null_warning_pp:
            findings.append({"classe": "DRIFT_RELEVANTE", "severidade": "alerta", "mensagem": f"nulos em {column} aumentaram {delta:.1f} p.p."})

    for column in sorted(set(baseline.get("distribuicoes", {})) & set(current.get("distribuicoes", {}))):
        psi = population_stability_index(
            baseline["distribuicoes"][column], current["distribuicoes"][column]
        )
        if psi > policy.psi_blocking:
            findings.append({"classe": "DRIFT_RELEVANTE", "severidade": "bloqueante", "mensagem": f"PSI {column}={psi:.3f}"})
        elif psi > policy.psi_warning:
            findings.append({"classe": "DRIFT_RELEVANTE", "severidade": "alerta", "mensagem": f"PSI {column}={psi:.3f}"})
    return findings
