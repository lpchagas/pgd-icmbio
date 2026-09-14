"""Regras temporais canônicas dos indicadores e relatórios PGD/ICMBio.

A análise é sempre cumulativa, com início fixo em 01/07/2025 e fim no último
dia do mês anterior à execução. A data de execução pode ser injetada pela
variável PGD_ANALYSIS_EXECUTION_DATE (AAAA-MM-DD), tornando as extrações
reprodutíveis.
"""
from __future__ import annotations

import calendar
import os
import re
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


# ---------------------------------------------------------------------------
# Recorte por período nomeado
#
# A janela de análise é sempre cumulativa (01/07/2025 até o fim do mês anterior
# à execução). Alguns produtos — o registro de execução do Plano de Entregas,
# por exemplo — precisam falar de UM período fechado dentro dessa janela
# ("o Q2-2026"), sem que a janela cumulativa deixe de existir. As funções
# abaixo resolvem um rótulo canônico para as datas correspondentes, reusando
# build_periods_pe()/build_periods_pt() — a tabela de períodos continua
# definida em um lugar só.
# ---------------------------------------------------------------------------

class PeriodoDesconhecido(ValueError):
    """O rótulo não pertence à segmentação canônica de períodos."""


class PeriodoIndisponivel(ValueError):
    """O rótulo é canônico, mas está fora da janela de análise vigente."""


_PERIOD_LABEL = re.compile(r"^(T[1-4]|Q[1-3]|M(?:0[1-9]|1[0-2]))-(\d{4})$")


@dataclass(frozen=True)
class PeriodSpec:
    """Um período canônico já recortado contra a janela de análise."""

    rotulo: str
    ciclo_tipo: str
    familia: str
    inicio: date
    fim: date
    fim_efetivo: date
    status: str

    @property
    def duracao_dias(self) -> int:
        return (self.fim_efetivo - self.inicio).days + 1

    @property
    def encerrado(self) -> bool:
        return self.status == "encerrado"

    def as_dict(self) -> dict[str, str]:
        """Exatamente as chaves de period_metadata() — nem mais, nem menos.

        `familia` fica de fora de propósito: as colunas de metadado dos CSVs
        são um contrato com lib/validation_contracts.py e acrescentar uma
        chave aqui faria todo produto periódico divergir do contrato.
        """

        return {
            "ciclo_tipo": self.ciclo_tipo,
            "periodo": self.rotulo,
            "periodo_inicio": self.inicio.isoformat(),
            "periodo_fim": self.fim.isoformat(),
            "periodo_fim_efetivo": self.fim_efetivo.isoformat(),
            "periodo_status": self.status,
            "duracao_dias": str(self.duracao_dias),
        }

    def as_row(self) -> list[str]:
        values = self.as_dict()
        return [values[column] for column in period_metadata()]


_BUILDERS = {"pe": build_periods_pe, "pt": build_periods_pt}


def _catalog(familia: str, cutoff: date) -> dict[str, tuple]:
    return {
        label: (kind, start, scheduled_end, effective_end, status)
        for label, kind, start, scheduled_end, effective_end, status
        in _BUILDERS[familia](cutoff)
    }


def _families(familia: str) -> tuple[str, ...]:
    if familia == "auto":
        return ("pe", "pt")
    if familia not in _BUILDERS:
        raise ValueError(f"família inválida '{familia}'; use 'pe', 'pt' ou 'auto'.")
    return (familia,)


def resolve_period(
    rotulo: str,
    *,
    familia: str = "auto",
    analysis_end: date | None = None,
    exigir_encerrado: bool = False,
) -> PeriodSpec:
    """Resolve 'Q2-2026' para as datas do período, recortado na janela.

    Distingue três desfechos, porque confundi-los esconde erro de operação:
    rótulo inexistente (PeriodoDesconhecido), rótulo canônico mas posterior
    ao corte da janela (PeriodoIndisponivel) e rótulo disponível — que ainda
    pode estar aberto no corte (`status = 'parcial_no_corte'`).
    """

    label = str(rotulo).strip().upper()
    match = _PERIOD_LABEL.match(label)
    if not match:
        raise PeriodoDesconhecido(
            f"Rótulo de período inválido: {rotulo!r}. "
            "Use T3/T4-2025 (trimestral), Q1..Q3-AAAA (quadrimestral) "
            "ou M01..M12-AAAA (mensal)."
        )
    year = int(match.group(2))
    cutoff = analysis_end or analysis_window().fim
    families = _families(familia)

    for family in families:
        catalog = _catalog(family, cutoff)
        if label in catalog:
            kind, start, scheduled_end, effective_end, status = catalog[label]
            if exigir_encerrado and status != "encerrado":
                raise PeriodoIndisponivel(
                    f"{label} ainda não encerrou em {cutoff.isoformat()} "
                    f"(fim programado {scheduled_end.isoformat()})."
                )
            return PeriodSpec(
                rotulo=label,
                ciclo_tipo=kind,
                familia=family,
                inicio=start,
                fim=scheduled_end,
                fim_efetivo=effective_end,
                status=status,
            )

    horizon = date(year, 12, 31)
    if horizon >= ANALYSIS_START:
        for family in families:
            catalog = _catalog(family, horizon)
            if label in catalog:
                _kind, start, _scheduled, _effective, _status = catalog[label]
                raise PeriodoIndisponivel(
                    f"{label} começa em {start.isoformat()}, posterior ao corte "
                    f"{cutoff.isoformat()} da janela de análise. Rode com "
                    "--data-execucao em um mês posterior ao fim do período."
                )

    disponiveis: dict[str, date] = {}
    for family in families:
        for rot, (_kind, start, *_rest) in _catalog(family, cutoff).items():
            disponiveis.setdefault(rot, start)
    ordenados = sorted(disponiveis, key=lambda rot: (disponiveis[rot], rot))
    raise PeriodoDesconhecido(
        f"{label} não pertence à segmentação canônica desta janela. "
        f"Disponíveis: {', '.join(ordenados)}."
    )


def periods_pt_within(
    spec: PeriodSpec,
    analysis_end: date | None = None,
) -> list[PeriodSpec]:
    """Ciclos mensais de PT inteiramente contidos no período informado.

    Para Q2-2026 devolve M05, M06, M07 e M08 de 2026 — os quatro ciclos que a
    RN-04 exige verificar antes de concluir um Plano de Entregas quadrimestral.
    """

    cutoff = analysis_end or analysis_window().fim
    contidos: list[PeriodSpec] = []
    for label, kind, start, scheduled_end, effective_end, status in build_periods_pt(cutoff):
        if start >= spec.inicio and scheduled_end <= spec.fim:
            contidos.append(
                PeriodSpec(
                    rotulo=label,
                    ciclo_tipo=kind,
                    familia="pt",
                    inicio=start,
                    fim=scheduled_end,
                    fim_efetivo=effective_end,
                    status=status,
                )
            )
    return contidos


def default_pe_period(analysis_end: date | None = None) -> PeriodSpec | None:
    """Último período de PE encerrado na janela — default do ciclo mensal."""

    cutoff = analysis_end or analysis_window().fim
    encerrados = [
        entry for entry in build_periods_pe(cutoff) if entry[5] == "encerrado"
    ]
    if not encerrados:
        return None
    label, kind, start, scheduled_end, effective_end, status = encerrados[-1]
    return PeriodSpec(
        rotulo=label,
        ciclo_tipo=kind,
        familia="pe",
        inicio=start,
        fim=scheduled_end,
        fim_efetivo=effective_end,
        status=status,
    )
