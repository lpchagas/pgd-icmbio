"""Oracles puros e independentes dos scripts A1.

As funções recebem registros atômicos normalizados e não importam SQL,
scripts de indicadores ou funções de cálculo da produção.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta
import re
from statistics import mean
from typing import Any, Callable, Iterable


Row = dict[str, Any]
UUID_VALUE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)


def independent_analysis_window(execution_date: str | date) -> tuple[date, date]:
    """Oracle temporal sem importar lib.periodos ou qualquer cálculo de produção."""

    execution = execution_date if isinstance(execution_date, date) else date.fromisoformat(execution_date)
    start = date(2025, 7, 1)
    end = date(execution.year, execution.month, 1) - timedelta(days=1)
    if end < start:
        raise ValueError("A data de execução antecede a primeira janela analítica válida.")
    return start, end


def _float(value: Any, default: float = 0.0) -> float:
    try:
        return float(str(value).replace(",", "."))
    except (TypeError, ValueError):
        return default


def _bool(value: Any, default: bool = False) -> bool:
    """Converte flags atômicas sem a ambiguidade de ``bool("0")``."""

    if value in (None, ""):
        return default
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "t", "sim", "s", "yes", "y"}:
        return True
    if normalized in {"0", "false", "f", "nao", "não", "n", "no"}:
        return False
    return default


def _date(value: Any) -> date | None:
    if isinstance(value, date):
        return value
    if value in (None, ""):
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def _active(records: Iterable[Row]) -> list[Row]:
    return [
        dict(row) for row in records
        if not row.get("deleted_at") and row.get("in_window", True)
    ]


def _sorted(rows: Iterable[Row], keys: tuple[str, ...]) -> list[Row]:
    return sorted(rows, key=lambda row: tuple(str(row.get(key, "")) for key in keys))


def _unique(records: Iterable[Row], *keys: str) -> list[Row]:
    result: list[Row] = []
    seen: set[tuple[str, ...]] = set()
    for position, row in enumerate(records):
        key = tuple(str(row.get(name, f"__missing__:{position}")) for name in keys)
        if key not in seen:
            seen.add(key)
            result.append(row)
    return result


def _group(records: Iterable[Row], *keys: str) -> dict[tuple[Any, ...], list[Row]]:
    result: dict[tuple[Any, ...], list[Row]] = defaultdict(list)
    for row in records:
        result[tuple(row.get(key, "N.I.") for key in keys)].append(row)
    return result


def oracle_i01(records: list[Row]) -> list[Row]:
    active = _active(records)
    for row in active:
        modality = str(row.get("modalidade") or "N.I.").strip()
        row["modalidade"] = "N.I." if UUID_VALUE.fullmatch(modality) else modality
    output: list[Row] = []
    by_period = _group(active, "periodo")
    for (period,), period_rows in by_period.items():
        all_users = {str(row["id_servidor"]) for row in period_rows if row.get("id_servidor")}
        for (modality,), rows in _group(period_rows, "modalidade").items():
            users = {str(row["id_servidor"]) for row in rows if row.get("id_servidor")}
            output.append({
                "visao": "institucional", "periodo": period, "modalidade": modality,
                "total_servidores": len(users),
                "proporcao_perc": round(100 * len(users) / len(all_users), 2) if all_users else 0.0,
            })
        for (unit,), unit_rows in _group(period_rows, "unidade_sigla").items():
            unit_users = {str(row["id_servidor"]) for row in unit_rows if row.get("id_servidor")}
            for (modality,), rows in _group(unit_rows, "modalidade").items():
                users = {str(row["id_servidor"]) for row in rows if row.get("id_servidor")}
                output.append({
                    "visao": "unidade", "periodo": period, "unidade_sigla": unit,
                    "modalidade": modality, "total_servidores": len(users),
                    "proporcao_na_unidade_perc": (
                        round(100 * len(users) / len(unit_users), 2) if unit_users else 0.0
                    ),
                })
    return _sorted(output, ("visao", "periodo", "unidade_sigla", "modalidade"))


def oracle_i02(records: list[Row]) -> list[Row]:
    output: list[Row] = []
    for (period, unit), rows in _group(_unique(_active(records), "periodo", "unidade_sigla", "id_entrega"), "periodo", "unidade_sigla").items():
        eligible = [row for row in rows if _float(row.get("meta_planejada")) > 0]
        total = len(eligible)
        completed = sum(
            _float(row.get("meta_executada")) >= _float(row.get("meta_planejada"))
            for row in eligible
        )
        due = sum(_bool(row.get("vence_no_periodo"), default=True) for row in eligible)
        assessed = [row for row in eligible if row.get("plano_status") in {"AVALIADO", "CONCLUIDO"}]
        output.append({
            "periodo": period, "unidade_sigla": unit,
            "total_no_ciclo": total, "total_vence_no_periodo": due,
            "total_concluidas": completed,
            "taxa_cumprimento_perc": round(100 * completed / total, 2) if total else 0.0,
            "total_em_plano_avaliado": len(assessed),
            "concluidas_em_plano_avaliado": sum(
                _float(row.get("meta_executada")) >= _float(row.get("meta_planejada"))
                for row in assessed
            ),
        })
    return _sorted(output, ("periodo", "unidade_sigla"))


def _normalized_goal(value: Any) -> float:
    raw = _float(value)
    return raw * 100 if 0 < raw <= 1 else raw


def _delivery_status(rate: float) -> str:
    if rate < 0:
        return "Dado inconsistente"
    if rate > 100:
        return "Superexecutada"
    if rate == 100:
        return "Concluida"
    if rate >= 70:
        return "Parcialmente cumprida"
    if rate > 0:
        return "Em andamento"
    return "Nao executada"


def oracle_i03(records: list[Row]) -> list[Row]:
    output: list[Row] = []
    for row in _unique(_active(records), "periodo", "unidade_sigla", "id_entrega"):
        if not _bool(row.get("vence_no_periodo"), default=True):
            continue
        planned = _normalized_goal(row.get("meta_planejada"))
        if planned <= 0:
            continue
        actual = _float(row.get("meta_executada"))
        rate = round(100 * actual / planned, 2)
        output.append({
            "periodo": row.get("periodo"), "unidade_sigla": row.get("unidade_sigla", "N.I."),
            "id_entrega": row.get("id_entrega"), "meta_planejada": planned,
            "meta_executada": actual, "taxa_atingimento_perc": rate,
            "status_entrega": _delivery_status(rate),
        })
    return _sorted(output, ("periodo", "unidade_sigla", "id_entrega"))


def oracle_i04(records: list[Row]) -> list[Row]:
    output: list[Row] = []
    unique = _unique(_active(records), "periodo", "unidade_sigla", "id_entrega")
    for (period, unit), rows in _group(unique, "periodo", "unidade_sigla").items():
        ratios = [
            abs(_float(row.get("meta_executada"))) / abs(_float(row.get("meta_planejada")))
            for row in rows if _float(row.get("meta_planejada")) > 0
        ]
        output.append({
            "periodo": period, "unidade_sigla": unit, "total_no_ciclo": len(ratios),
            "score_atingimento_perc": round(mean(ratios) * 100, 2) if ratios else 0.0,
        })
    return _sorted(output, ("periodo", "unidade_sigla"))


def oracle_i05(records: list[Row]) -> list[Row]:
    output: list[Row] = []
    for (period, unit), unit_rows in _group(_active(records), "periodo", "unidade_sigla").items():
        counts: dict[str, int] = {}
        for (user,), rows in _group(unit_rows, "id_servidor").items():
            counts[str(user)] = len({str(row.get("id_entrega")) for row in rows})
        average = round(mean(counts.values()), 2) if counts else 0.0
        for user, count in counts.items():
            output.append({
                "periodo": period, "unidade_sigla": unit, "id_servidor": user,
                "qtd_entregas_por_servidor": count,
                "media_entregas_por_servidor_unidade": average,
                "posicao_relativa_media": (
                    "Acima da media" if count > average else "Abaixo da media" if count < average else "Na media"
                ),
            })
    return _sorted(output, ("periodo", "unidade_sigla", "id_servidor"))


def oracle_i06(records: list[Row]) -> list[Row]:
    output: list[Row] = []
    for (period, unit), unit_rows in _group(_active(records), "periodo", "unidade_sigla").items():
        delivery_sizes: list[int] = []
        for _, rows in _group(unit_rows, "id_entrega").items():
            delivery_sizes.append(len({str(row.get("id_servidor")) for row in rows}))
        total = len(delivery_sizes)
        categories: dict[str, int] = defaultdict(int)
        for size in delivery_sizes:
            category = f"{size} servidor" if size == 1 else f"{size} servidores" if size < 4 else "4+ servidores"
            categories[category] += 1
        for category, count in categories.items():
            output.append({
                "periodo": period, "unidade_sigla": unit,
                "tamanho_grupo_responsavel": category,
                "total_entregas_na_categoria": count, "total_entregas_unidade": total,
                "pct_categoria": round(100 * count / total, 1) if total else 0.0,
            })
    return _sorted(output, ("periodo", "unidade_sigla", "tamanho_grupo_responsavel"))


def _allocated_hours(row: Row) -> tuple[float, float]:
    start, end = _date(row.get("plano_inicio")), _date(row.get("plano_fim"))
    overlap_start, overlap_end = _date(row.get("sobreposicao_inicio")), _date(row.get("sobreposicao_fim"))
    if not start or not end or not overlap_start or not overlap_end or end < start or overlap_end < overlap_start:
        return 0.0, 0.0
    base = _float(row.get("carga_horaria"))
    if row.get("forma_contagem_carga_horaria") == "DIAS":
        base *= 8.0
    proportional = base * ((overlap_end - overlap_start).days + 1) / ((end - start).days + 1)
    allocated = proportional * _float(row.get("forca_trabalho")) / 100.0
    return proportional, allocated


def oracle_i07(records: list[Row]) -> list[Row]:
    output: list[Row] = []
    for (period, unit, delivery), rows in _group(
        _unique(_active(records), "periodo", "unidade_sigla", "id_entrega", "plano_trabalho_id", "id_servidor"),
        "periodo", "unidade_sigla", "id_entrega"
    ).items():
        hours = sum(_allocated_hours(row)[1] for row in rows)
        plans = {str(row.get("plano_trabalho_id")) for row in rows}
        output.append({
            "periodo": period, "unidade_sigla": unit, "id_entrega": delivery,
            "total_horas_planejadas_entrega": round(hours, 2),
            "num_servidores_alocados": len(plans),
        })
    return _sorted(output, ("periodo", "unidade_sigla", "id_entrega"))


def oracle_i08(records: list[Row]) -> list[Row]:
    output: list[Row] = []
    source_rows = _active(records)
    active = _unique(
        (row for row in source_rows if row.get("_extractor") != "pt_capacidade_unidade"),
        "periodo", "unidade_sigla", "id_entrega", "plano_trabalho_id", "id_servidor"
    )
    capacity: dict[tuple[Any, Any], float] = defaultdict(float)
    seen_plans: set[tuple[Any, Any, Any]] = set()
    capacity_rows = [
        row for row in source_rows if row.get("_extractor") == "pt_capacidade_unidade"
    ]
    # Fixtures legadas podem não separar o universo de capacidade. O fallback
    # preserva esses testes, mas a execução integrada exige a fonte própria.
    for row in capacity_rows or active:
        key = (row.get("periodo"), row.get("unidade_sigla"), row.get("plano_trabalho_id"))
        if key not in seen_plans:
            seen_plans.add(key)
            capacity[key[:2]] += _allocated_hours(row)[0]
    for (period, unit, delivery), rows in _group(active, "periodo", "unidade_sigla", "id_entrega").items():
        hours = sum(_allocated_hours(row)[1] for row in rows)
        available = capacity[(period, unit)]
        output.append({
            "periodo": period, "unidade_sigla": unit, "id_entrega": delivery,
            "horas_planejadas_entrega": round(hours, 2),
            "total_horas_disponiveis_unidade": round(available, 2),
            "proporcao_horas_perc": round(100 * hours / available, 2) if available else 0.0,
        })
    return _sorted(output, ("periodo", "unidade_sigla", "id_entrega"))


def _score(row: Row) -> int:
    return 6 - int(_float(row.get("sequencia_nota")))


def oracle_i09(records: list[Row]) -> list[Row]:
    output: list[Row] = []
    unique = _unique(_active(records), "periodo", "id_avaliacao")
    for (period, unit), rows in _group(unique, "periodo", "unidade_sigla").items():
        values = [_score(row) for row in rows]
        result: Row = {
            "periodo": period, "unidade_sigla": unit, "total_avaliacoes_pt": len(values),
            "total_planos_com_avaliacao": len({str(row.get("plano_trabalho_id")) for row in rows}),
            "total_servidores_avaliados": len({str(row.get("id_servidor")) for row in rows}),
            "media_nota_pt": round(mean(values), 2), "nota_minima": min(values), "nota_maxima": max(values),
        }
        for note in range(1, 6):
            result[f"qtd_nota_{note}"] = values.count(note)
        output.append(result)
    return _sorted(output, ("periodo", "unidade_sigla"))


def _category_oracle(records: list[Row], sequence: int, count_name: str, percent_name: str) -> list[Row]:
    output: list[Row] = []
    unique = _unique(_active(records), "periodo", "id_avaliacao")
    for (period, unit), rows in _group(unique, "periodo", "unidade_sigla").items():
        count = sum(int(_float(row.get("sequencia_nota"))) == sequence for row in rows)
        output.append({
            "periodo": period, "unidade_sigla": unit, "total_avaliacoes_pt": len(rows),
            "total_servidores_avaliados": len({str(row.get("id_servidor")) for row in rows}),
            count_name: count, percent_name: round(100 * count / len(rows), 2) if rows else 0.0,
        })
    return _sorted(output, ("periodo", "unidade_sigla"))


def oracle_i10(records: list[Row]) -> list[Row]:
    return _category_oracle(records, 4, "qtd_inadequado", "perc_inadequado")


def oracle_i11(records: list[Row]) -> list[Row]:
    return _category_oracle(records, 1, "qtd_excepcional", "perc_excepcional")


def oracle_i12(records: list[Row]) -> list[Row]:
    output: list[Row] = []
    unique = _unique(_active(records), "periodo", "instrumento", "id_avaliacao")
    for (period, unit), rows in _group(unique, "periodo", "unidade_sigla").items():
        pt = [row for row in rows if row.get("instrumento") == "PT"]
        pe = [row for row in rows if row.get("instrumento") == "PE"]
        if not pt or not pe:
            continue
        pt_mean, pe_mean = round(mean(_score(row) for row in pt), 2), round(mean(_score(row) for row in pe), 2)
        directional = round(pt_mean - pe_mean, 2)
        absolute = round(abs(directional), 2)
        output.append({
            "periodo": period, "unidade_sigla": unit, "total_avaliacoes_pt": len(pt),
            "total_servidores_avaliados": len({str(row.get("id_servidor")) for row in pt}),
            "media_nota_pt": pt_mean, "total_avaliacoes_pe": len(pe), "media_nota_pe": pe_mean,
            "diferenca_absoluta": absolute, "diferenca_direcional": directional,
            "classificacao_coerencia": (
                "Coerente" if absolute <= 1 else "Divergencia moderada" if absolute <= 2 else "Alta divergencia"
            ),
            "direcao_divergencia": "PT > PE" if directional > 0 else "PE > PT" if directional < 0 else "Sem diferenca",
        })
    return _sorted(output, ("periodo", "unidade_sigla"))


def oracle_pt_status(records: list[Row]) -> list[Row]:
    labels = {
        "INCLUIDO": "Rascunho", "AGUARDANDO_ASSINATURA": "Aguardando assinatura",
        "ATIVO": "Em execução", "CONCLUIDO": "Concluído", "SUSPENSO": "Suspenso",
        "CANCELADO": "Cancelado",
    }
    plans: dict[str, dict[str, Any]] = {}
    for position, row in enumerate(_active(records)):
        source = row.get("_extractor")
        plan_id = str(row.get("plano_trabalho_id") or f"legacy:{position}")
        if source in (None, "pt_status_planos"):
            plans[plan_id] = {
                "unidade_sigla": str(row.get("unidade_sigla", "N.I.")),
                "status_codigo": str(row.get("status_codigo", "N.I.")),
                "aguardando": int(_float(row.get("periodos_aguardando_avaliacao"))),
                "plano_updated_at": row.get("plano_updated_at"),
                "status_desde": row.get("plano_updated_at"),
                "origem_data_status": "fallback_updated_at",
            }
    for row in _active(records):
        plan_id = str(row.get("plano_trabalho_id", ""))
        plan = plans.get(plan_id)
        if not plan:
            continue
        if row.get("_extractor") == "pt_status_consolidacoes" and row.get("consolidacao_status") == "CONCLUIDO":
            plan["aguardando"] += 1
        if (
            row.get("_extractor") == "pt_status_transicoes"
            and row.get("status_codigo_transicao") == plan["status_codigo"]
            and str(row.get("status_created_at") or "") > str(plan.get("status_desde") or "")
        ):
            plan["status_desde"] = row.get("status_created_at")
            plan["origem_data_status"] = "trilha_status_justificativas"

    counts: dict[tuple[str, str], int] = defaultdict(int)
    for plan in plans.values():
        status = plan["status_codigo"]
        if status not in {"INCLUIDO", "AGUARDANDO_ASSINATURA", "ATIVO", "SUSPENSO"}:
            continue
        business = (
            "Aguardando avaliação"
            if plan["aguardando"] > 0 and status in {"ATIVO", "CONCLUIDO"}
            else labels.get(status, status)
        )
        counts[(plan["unidade_sigla"], business)] += 1
    return [
        {"unidade_sigla": unit, "status_negocio": status, "qtd_planos": count}
        for (unit, status), count in sorted(counts.items())
    ]


ORACLES: dict[str, Callable[[list[Row]], list[Row]]] = {
    "I01": oracle_i01, "I02": oracle_i02, "I03": oracle_i03, "I04": oracle_i04,
    "I05": oracle_i05, "I06": oracle_i06, "I07": oracle_i07, "I08": oracle_i08,
    "I09": oracle_i09, "I10": oracle_i10, "I11": oracle_i11, "I12": oracle_i12,
    "PT_STATUS": oracle_pt_status,
}


def calculate(code: str, records: list[Row]) -> list[Row]:
    try:
        oracle = ORACLES[code.upper()]
    except KeyError as exc:
        raise ValueError(f"Oracle ausente para {code}") from exc
    return oracle(records)


def invariant_findings(rows: list[Row], keys: tuple[str, ...]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    seen: set[tuple[str, ...]] = set()
    for row in rows:
        key = tuple(str(row.get(column, "")) for column in keys)
        if key in seen:
            findings.append({"classe": "BUG_PROVAVEL", "mensagem": "chave duplicada no resultado do oracle"})
        seen.add(key)
        for name, value in row.items():
            if ("perc" in name or "proporcao" in name) and _float(value) < 0:
                findings.append({"classe": "ANOMALIA_DE_DADOS", "mensagem": f"{name} contém valor negativo"})
    return findings
