"""Regras temporais canônicas dos indicadores e relatórios PGD/ICMBio.

A análise é sempre cumulativa, com início fixo em 01/07/2025 e fim no último
dia do mês anterior à execução. A data de execução pode ser injetada pela
variável PGD_ANALYSIS_EXECUTION_DATE (AAAA-MM-DD), tornando as extrações
reprodutíveis.
"""
from __future__ import annotations

import calendar
import os
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo


ANALYSIS_START = date(2025, 7, 1)
ANALYSIS_TIMEZONE = "America/Sao_Paulo"
EXECUTION_DATE_ENV = "PGD_ANALYSIS_EXECUTION_DATE"
OUTPUT_MONTH_ENV = "PGD_OUTPUT_MONTH"


@dataclass(frozen=True)
class AnalysisWindow:
    """Janela cumulativa de referência de uma execução mensal."""

    inicio: date
    fim: date
    mes_execucao: str
    data_execucao: date

    def as_dict(self) -> dict[str, str]:
        return {
            "periodo_analise_inicio": self.inicio.isoformat(),
            "periodo_analise_fim": self.fim.isoformat(),
            "mes_execucao": self.mes_execucao,
            "data_execucao": self.data_execucao.isoformat(),
        }


def _parse_date(value: date | str) -> date:
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"Data inválida '{value}'; use AAAA-MM-DD.") from exc


def execution_date(value: date | str | None = None) -> date:
    """Resolve a data explícita, injetada ou local em São Paulo."""

    if value is not None:
        return _parse_date(value)
    injected = os.environ.get(EXECUTION_DATE_ENV)
    if injected:
        return _parse_date(injected)
    if "--data-execucao" in sys.argv:
        position = sys.argv.index("--data-execucao")
        if position + 1 >= len(sys.argv):
            raise ValueError("--data-execucao exige AAAA-MM-DD.")
        return _parse_date(sys.argv[position + 1])
    return datetime.now(ZoneInfo(ANALYSIS_TIMEZONE)).date()


def analysis_window(value: date | str | None = None) -> AnalysisWindow:
    """Retorna 01/07/2025 até o último dia do mês anterior à execução."""

    executed_at = execution_date(value)
    first_of_month = date(executed_at.year, executed_at.month, 1)
    analysis_end = first_of_month - timedelta(days=1)
    if analysis_end < ANALYSIS_START:
        raise ValueError(
            "A data de execução resulta em janela anterior à base oficial "
            f"{ANALYSIS_START.isoformat()}."
        )
    return AnalysisWindow(
        inicio=ANALYSIS_START,
        fim=analysis_end,
        mes_execucao=f"{executed_at.year:04d}-{executed_at.month:02d}",
        data_execucao=executed_at,
    )


def configure_execution_context(value: date | str, output_month: str | None = None) -> AnalysisWindow:
    """Injeta o contexto temporal para subprocessos e módulos legados."""

    window = analysis_window(value)
    os.environ[EXECUTION_DATE_ENV] = window.data_execucao.isoformat()
    os.environ[OUTPUT_MONTH_ENV] = output_month or window.mes_execucao
    return window


def _periods_until(
    raw: list[tuple[str, str, date, date]],
    analysis_end: date | None,
) -> list[tuple[str, str, date, date, date, str]]:
    cutoff = analysis_end or analysis_window().fim
    if cutoff < ANALYSIS_START:
        raise ValueError("analysis_end não pode ser anterior a 01/07/2025.")

    periods: list[tuple[str, str, date, date, date, str]] = []
    for label, kind, start, scheduled_end in raw:
        if start > cutoff:
            continue
        effective_end = min(scheduled_end, cutoff)
        status = "encerrado" if scheduled_end <= cutoff else "parcial_no_corte"
        periods.append((label, kind, start, scheduled_end, effective_end, status))
    return periods


def build_periods_pe(
    analysis_end: date | None = None,
) -> list[tuple[str, str, date, date, date, str]]:
    """Períodos de PE contidos na janela, truncados na data final."""

    cutoff = analysis_end or analysis_window().fim
    raw: list[tuple[str, str, date, date]] = [
        ("T3-2025", "trimestral", date(2025, 7, 1), date(2025, 9, 30)),
        ("T4-2025", "trimestral", date(2025, 10, 1), date(2025, 12, 31)),
    ]
    for year in range(2026, cutoff.year + 1):
        raw.extend(
            [
                (f"Q1-{year}", "quadrimestral", date(year, 1, 1), date(year, 4, 30)),
                (f"Q2-{year}", "quadrimestral", date(year, 5, 1), date(year, 8, 31)),
                (f"Q3-{year}", "quadrimestral", date(year, 9, 1), date(year, 12, 31)),
            ]
        )
    return _periods_until(raw, cutoff)


def build_periods_pt(
    analysis_end: date | None = None,
) -> list[tuple[str, str, date, date, date, str]]:
    """Períodos de PT contidos na janela, truncados na data final."""

    cutoff = analysis_end or analysis_window().fim
    raw: list[tuple[str, str, date, date]] = [
        ("T3-2025", "trimestral", date(2025, 7, 1), date(2025, 9, 30)),
        ("T4-2025", "trimestral", date(2025, 10, 1), date(2025, 12, 31)),
    ]
    for year in range(2026, cutoff.year + 1):
        for month in range(1, 13):
            last_day = calendar.monthrange(year, month)[1]
            raw.append(
                (f"M{month:02d}-{year}", "mensal", date(year, month, 1), date(year, month, last_day))
            )
    return _periods_until(raw, cutoff)


build_periods = build_periods_pe


def period_metadata() -> list[str]:
    return [
        "ciclo_tipo",
        "periodo",
        "periodo_inicio",
        "periodo_fim",
        "periodo_fim_efetivo",
        "periodo_status",
        "duracao_dias",
    ]
