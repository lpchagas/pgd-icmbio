"""Carga privada em memória e consolidação anonimizada dos indicadores I01–I12."""
from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from statistics import mean
from typing import Iterable, Mapping

from lib.periodos import AnalysisWindow
from ocde.relatorios.escopo import ScopeSpec, UnitProfile, filter_rows
from ocde.relatorios.privacidade import SUPPRESSED, count_band, eligible, quantity_band


@dataclass(frozen=True)
class LoadedIndicator:
    indicator: str
    path: Path
    rows: tuple[dict[str, str], ...]
    excluded_outside_window: int


def _parse_date(value: object) -> date | None:
    try:
        return date.fromisoformat(str(value or "")[:10])
    except ValueError:
        return None


def _number(value: object) -> float:
    try:
        result = float(str(value).replace(",", "."))
        return result if math.isfinite(result) else 0.0
    except (TypeError, ValueError):
        return 0.0


def latest_indicator_files(month_dir: Path) -> dict[str, Path]:
    files: dict[str, Path] = {}
    for indicator in range(1, 13):
        code = f"{indicator:02d}"
        candidates = sorted(month_dir.glob(f"IND_{code}.2_*.csv"))
        if code == "01":
            scoped = [path for path in candidates if "_v2_" in path.name]
            candidates = scoped or candidates
        if candidates:
            files[code] = candidates[-1]
    return files


def load_indicator(path: Path, indicator: str, window: AnalysisWindow) -> LoadedIndicator:
    kept: list[dict[str, str]] = []
    excluded = 0
    with path.open(encoding="utf-8-sig", errors="replace", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="|")
        for original in reader:
            row = {str(key): str(value or "") for key, value in original.items() if key is not None}
            start = _parse_date(row.get("periodo_inicio"))
            scheduled_end = _parse_date(row.get("periodo_fim"))
            effective_source = _parse_date(row.get("periodo_fim_efetivo"))
            end = effective_source or scheduled_end
            if not start or not end or start > window.fim or end < window.inicio:
                excluded += 1
                continue
            effective = min(end, window.fim)
            if scheduled_end and scheduled_end > window.fim:
                row["periodo_status"] = "parcial_no_corte"
            elif row.get("periodo_status") not in {"encerrado", "parcial_no_corte"}:
                row["periodo_status"] = "encerrado"
            row["periodo_fim_efetivo"] = effective.isoformat()
            kept.append(row)
    return LoadedIndicator(indicator, path, tuple(kept), excluded)


def load_all(month_dir: Path, window: AnalysisWindow) -> dict[str, LoadedIndicator]:
    files = latest_indicator_files(month_dir)
    missing = [f"{item:02d}" for item in range(1, 13) if f"{item:02d}" not in files]
    if missing:
        raise FileNotFoundError("Indicadores ausentes na pasta mensal: " + ", ".join(missing))
    return {code: load_indicator(path, code, window) for code, path in files.items()}


def scoped_data(
    loaded: Mapping[str, LoadedIndicator],
    scope: ScopeSpec,
    profiles: Mapping[str, UnitProfile],
) -> dict[str, list[dict[str, object]]]:
    result: dict[str, list[dict[str, object]]] = {}
    for code, source in loaded.items():
        result[code] = filter_rows(source.rows, scope, profiles)
    return result


def people_count(rows: Iterable[Mapping[str, object]], start: date | None = None, end: date | None = None) -> int:
    ids: set[str] = set()
    for row in rows:
        identifier = str(row.get("id_servidor") or row.get("usuario_id") or "").strip()
        if not identifier:
            continue
        row_start = _parse_date(row.get("periodo_inicio"))
        row_end = _parse_date(row.get("periodo_fim_efetivo") or row.get("periodo_fim"))
        if start and end and row_start and row_end and (row_start > end or row_end < start):
            continue
        ids.add(identifier)
    return len(ids)


def people_counts_by_unit(rows: Iterable[Mapping[str, object]]) -> dict[str, int]:
    identifiers: dict[str, set[str]] = {}
    for row in rows:
        unit = str(row.get("unidade_sigla") or "").strip().upper()
        identifier = str(row.get("id_servidor") or row.get("usuario_id") or "").strip()
        if unit and identifier:
            identifiers.setdefault(unit, set()).add(identifier)
    return {unit: len(values) for unit, values in identifiers.items()}


EVALUATION_INDICATORS = {"09", "10", "11", "12"}


def metric_people_lower_bound(
    code: str,
    rows: Iterable[Mapping[str, object]],
    fallback: int,
) -> int:
    """Retorna cobertura de pessoas segura para decidir a divulgação.

    I09-I12 são agregados por unidade no A1 e, por isso, não persistem
    identificadores. O maior total distinto observado em uma única
    unidade/ciclo é usado como limite inferior conservador. Não se somam
    unidades nem ciclos, pois uma pessoa pode aparecer em mais de um grupo.
    """
    if code not in EVALUATION_INDICATORS:
        return fallback
    return max(
        (int(_number(row.get("total_servidores_avaliados"))) for row in rows),
        default=0,
    )


def _weighted(rows: list[Mapping[str, object]], value: str, weight: str) -> float | None:
    pairs = [(_number(row.get(value)), _number(row.get(weight))) for row in rows]
    denominator = sum(weight_value for _, weight_value in pairs if weight_value > 0)
    if denominator <= 0:
        values = [_number(row.get(value)) for row in rows if str(row.get(value) or "").strip()]
        return mean(values) if values else None
    return sum(value_number * weight_value for value_number, weight_value in pairs if weight_value > 0) / denominator


def _metric(code: str, rows: list[Mapping[str, object]]) -> tuple[str, float | None, float]:
    if code in {"02", "03", "04"}:
        # O PETRVS expõe o progresso atual, mas o histórico temporal ainda não
        # está validado para reconstruir um estado parcial no corte.
        rows = [row for row in rows if row.get("periodo_status") != "parcial_no_corte"]
    if not rows:
        label = "Estado parcial indisponível sem histórico confiável" if code in {"02", "03", "04"} else "Sem dados"
        return label, None, 0
    if code == "01":
        by_mode: dict[str, list[tuple[float, float]]] = {}
        for row in rows:
            by_mode.setdefault(str(row.get("modalidade") or "Não informada"), []).append((
                _number(row.get("proporcao_na_unidade_perc") or row.get("proporcao_perc")),
                max(_number(row.get("total_servidores")), 1),
            ))
        mode, values = max(
            by_mode.items(),
            key=lambda item: sum(value * weight for value, weight in item[1]) / sum(weight for _, weight in item[1]),
        )
        weighted_value = sum(value * weight for value, weight in values) / sum(weight for _, weight in values)
        return f"Maior participação: {mode}", weighted_value, sum(
            _number(row.get("total_servidores")) for row in rows
            )
    if code == "02":
        num = sum(_number(row.get("total_concluidas")) for row in rows)
        den = sum(_number(row.get("total_no_ciclo")) for row in rows)
        return "Cumprimento de entregas", (num * 100 / den if den else None), den
    if code == "03":
        vals = [_number(row.get("taxa_atingimento_perc")) for row in rows]
        return "Atingimento médio das metas", mean(vals) if vals else None, len(rows)
    if code == "04":
        return "Score médio de metas", _weighted(rows, "score_atingimento_perc", "total_no_ciclo"), sum(_number(r.get("total_no_ciclo")) for r in rows)
    if code == "05":
        vals = [_number(row.get("qtd_entregas_por_servidor")) for row in rows]
        return "Entregas médias por servidor", mean(vals) if vals else None, len(rows)
    if code == "06":
        one = [row for row in rows if str(row.get("tamanho_grupo_responsavel") or "").startswith("1")]
        num = sum(_number(row.get("total_entregas_na_categoria")) for row in one)
        # O total se repete por categoria; tomar o máximo por unidade/período evita dupla contagem.
        totals: dict[tuple[str, str], float] = {}
        for row in rows:
            key = (str(row.get("unidade_sigla")), str(row.get("periodo")))
            totals[key] = max(totals.get(key, 0), _number(row.get("total_entregas_unidade")))
        den = sum(totals.values())
        return "Entregas sob responsabilidade individual", (num * 100 / den if den else None), den
    if code == "07":
        total = sum(_number(row.get("total_horas_planejadas_entrega")) for row in rows)
        return "Horas planejadas por entrega", (total / len(rows) if rows else None), len(rows)
    if code == "08":
        vals = [_number(row.get("proporcao_horas_perc")) for row in rows]
        return "Participação média das entregas nas horas", mean(vals) if vals else None, len(rows)
    if code == "09":
        return "Nota média dos PT", _weighted(rows, "media_nota_pt", "total_avaliacoes_pt"), sum(_number(r.get("total_avaliacoes_pt")) for r in rows)
    if code == "10":
        num = sum(_number(row.get("qtd_inadequado")) for row in rows)
        den = sum(_number(row.get("total_avaliacoes_pt")) for row in rows)
        return "Avaliações inadequadas", (num * 100 / den if den else None), den
    if code == "11":
        num = sum(_number(row.get("qtd_excepcional")) for row in rows)
        den = sum(_number(row.get("total_avaliacoes_pt")) for row in rows)
        return "Avaliações excepcionais", (num * 100 / den if den else None), den
    if code == "12":
        return "Diferença média entre avaliações PT e PE", _weighted(rows, "diferenca_absoluta", "total_avaliacoes_pt"), sum(_number(r.get("total_avaliacoes_pt")) for r in rows)
    return "Indicador", None, len(rows)


def _format_value(code: str, value: float | None) -> str:
    if value is None:
        return "N/D"
    suffix = "%" if code in {"01", "02", "03", "04", "06", "08", "10", "11"} else ""
    return f"{value:.1f}{suffix}"


def cumulative_summary(
    data: Mapping[str, list[dict[str, object]]], *, enforce_k: bool = True
) -> list[dict[str, str]]:
    people = people_count(data.get("05", []))
    result: list[dict[str, str]] = []
    for code in [f"{item:02d}" for item in range(1, 13)]:
        label, value, observations = _metric(code, data.get(code, []))
        support_people = metric_people_lower_bound(code, data.get(code, []), people)
        meets_k = (not enforce_k) or (
            eligible(support_people) and (code not in EVALUATION_INDICATORS or observations >= 5)
        )
        allowed = meets_k and value is not None
        status = "publicado" if allowed else ("suprimido_k" if not meets_k else "sem_dados")
        result.append(
            {
                "indicador": f"I{code}",
                "medida": label,
                "resultado": _format_value(code, value) if allowed else (SUPPRESSED if status == "suprimido_k" else "N/D"),
                "observacoes_faixa": (
                    str(int(observations)) if not enforce_k
                    else quantity_band(observations) if status != "suprimido_k" else SUPPRESSED
                ),
                "servidores_distintos_faixa": (
                    str(support_people) if not enforce_k else count_band(support_people)
                ),
                "situacao_divulgacao": status,
            }
        )
    return result


def temporal_summary(
    data: Mapping[str, list[dict[str, object]]], *, enforce_k: bool = True
) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for code in [f"{item:02d}" for item in range(1, 13)]:
        rows = data.get(code, [])
        periods = sorted({str(row.get("periodo") or "") for row in rows if row.get("periodo")})
        for period in periods:
            selected = [row for row in rows if str(row.get("periodo")) == period]
            start_dates = [_parse_date(row.get("periodo_inicio")) for row in selected]
            end_dates = [_parse_date(row.get("periodo_fim_efetivo") or row.get("periodo_fim")) for row in selected]
            starts = [value for value in start_dates if value]
            ends = [value for value in end_dates if value]
            start, end = (min(starts), max(ends)) if starts and ends else (None, None)
            people = people_count(data.get("05", []), start, end) if start and end else 0
            support_people = metric_people_lower_bound(code, selected, people)
            label, value, observations = _metric(code, selected)
            meets_k = (not enforce_k) or (
                eligible(support_people) and (code not in EVALUATION_INDICATORS or observations >= 5)
            )
            allowed = meets_k and value is not None
            disclosure = "publicado" if allowed else ("suprimido_k" if not meets_k else "sem_dados")
            status = "parcial_no_corte" if any(row.get("periodo_status") == "parcial_no_corte" for row in selected) else "encerrado"
            result.append(
                {
                    "indicador": f"I{code}",
                    "periodo": period,
                    "periodo_inicio": start.isoformat() if start else "",
                    "periodo_fim_efetivo": end.isoformat() if end else "",
                    "periodo_status": status,
                    "medida": label,
                    "resultado": _format_value(code, value) if allowed else (SUPPRESSED if disclosure == "suprimido_k" else "N/D"),
                    "observacoes_faixa": (
                        str(int(observations)) if not enforce_k
                        else quantity_band(observations) if disclosure != "suprimido_k" else SUPPRESSED
                    ),
                    "servidores_distintos_faixa": (
                        str(support_people) if not enforce_k else count_band(support_people)
                    ),
                    "situacao_divulgacao": disclosure,
                }
            )
    return result
