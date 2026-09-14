"""Cálculo puro do G02 — execução de entregas em lentes PE e PT separadas."""
from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any, Iterable

from lib.csv_utils import clean

Row = dict[str, Any]


def _number(value: Any) -> float:
    try:
        return float(str(value or 0).replace(",", "."))
    except (TypeError, ValueError):
        return 0.0


def _day(value: Any) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def _unique(rows: Iterable[Row], key: str) -> list[Row]:
    result: list[Row] = []
    seen: set[str] = set()
    for row in rows:
        value = str(row.get(key) or "")
        if value and value not in seen:
            seen.add(value)
            result.append(dict(row))
    return result


def reconciliation(has_history: bool, has_link: bool, delivery_known: bool = True) -> str:
    if not delivery_known:
        return "PT_OU_VINCULO_SEM_ENTREGA_IDENTIFICAVEL"
    if has_history and has_link:
        return "HISTORICO_PE_E_EVIDENCIA_PT"
    if has_history:
        return "HISTORICO_PE_SEM_VINCULO_PT"
    if has_link:
        return "TRABALHO_PT_SEM_HISTORICO_PE"
    return "SEM_HISTORICO_PE_E_SEM_VINCULO_PT"


MAIN_COLUMNS = (
    "visao", "periodo", "periodo_inicio", "periodo_fim", "unidade_sigla",
    "unidade_dona_sigla", "unidade_executora_sigla", "id_entrega", "nome_entrega",
    "meta_planejada", "progresso_historico", "taxa_atingimento_perc",
    "total_registros_execucao", "data_ultimo_registro", "total_planos_trabalho",
    "total_servidores", "total_vinculos", "forca_trabalho_media_perc",
    "atividades_total", "atividades_iniciadas", "atividades_concluidas",
    "horas_planejadas", "horas_despendidas", "situacao_cobertura",
    "situacao_reconciliacao",
)

HISTORY_COLUMNS = (
    "periodo", "unidade_dona_sigla", "id_entrega", "nome_entrega",
    "data_progresso", "meta", "realizado", "progresso_esperado",
    "progresso_realizado", "registro_execucao",
)

NOMINAL_COLUMNS = (
    "unidade_executora_sigla", "unidade_dona_sigla", "id_servidor",
    "servidor_nome", "plano_trabalho_id", "plano_numero", "plano_inicio",
    "plano_fim", "id_entrega", "nome_entrega", "forca_trabalho",
    "atividades_total", "atividades_iniciadas", "atividades_concluidas",
    "horas_planejadas", "horas_despendidas",
)


def build_g02(
    deliveries: list[Row], progress: list[Row], plans: list[Row], links: list[Row],
    activities: list[Row], periods: Iterable[tuple[str, str, date, date, date, str]],
    *, history_cutoff: date, observation_date: date,
) -> tuple[list[Row], list[Row], list[Row]]:
    """Reconcilia PE histórico e fotografia PT sem projetar a fotografia para o passado."""
    deliveries = _unique((r for r in deliveries if not r.get("deleted_at")), "id_entrega")
    plans = _unique((r for r in plans if not r.get("deleted_at")), "plano_trabalho_id")
    links = _unique((r for r in links if not r.get("deleted_at")), "vinculo_id")
    activities = _unique((r for r in activities if not r.get("deleted_at")), "atividade_id")
    progress = _unique((r for r in progress if not r.get("deleted_at")), "progresso_id")
    progress = [r for r in progress if (_day(r.get("data_progresso")) or date.max) <= history_cutoff]

    delivery_by_id = {str(r["id_entrega"]): r for r in deliveries}
    plan_by_id = {str(r["plano_trabalho_id"]): r for r in plans}
    progress_by_delivery: dict[str, list[Row]] = defaultdict(list)
    links_by_delivery: dict[str, list[Row]] = defaultdict(list)
    links_by_plan: dict[str, list[Row]] = defaultdict(list)
    activities_by_plan: dict[str, list[Row]] = defaultdict(list)
    for row in progress:
        progress_by_delivery[str(row.get("id_entrega") or "")].append(row)
    for row in links:
        links_by_delivery[str(row.get("id_entrega") or "")].append(row)
        links_by_plan[str(row.get("plano_trabalho_id") or "")].append(row)
    for row in activities:
        activities_by_plan[str(row.get("plano_trabalho_id") or "")].append(row)

    main: list[Row] = []
    history: list[Row] = []
    nominal: list[Row] = []
    period_list = list(periods)
    for delivery_id, delivery in delivery_by_id.items():
        owner = clean(delivery.get("unidade_dona_sigla"), "N.I.")
        name = clean(delivery.get("nome_entrega"), "N.I.")
        events = sorted(progress_by_delivery.get(delivery_id, []), key=lambda r: str(r.get("data_progresso") or ""))
        delivery_links = links_by_delivery.get(delivery_id, [])
        executors = sorted({clean(plan_by_id.get(str(link.get("plano_trabalho_id")), {}).get("unidade_executora_sigla"), "N.I.") for link in delivery_links})
        views = [("dona", owner, "MULTIPLAS" if len(executors) > 1 else (executors[0] if executors else "SEM_VINCULO"))]
        views += [("executora", executor, executor) for executor in executors]
        for label, _kind, start, _scheduled, end, _status in period_list:
            if end > history_cutoff:
                continue
            if (_day(delivery.get("entrega_inicio")) or date.min) > end or (_day(delivery.get("entrega_fim")) or date.max) < start:
                continue
            period_events = [event for event in events if start <= (_day(event.get("data_progresso")) or date.min) <= end]
            historical_events = [event for event in events if (_day(event.get("data_progresso")) or date.max) <= end]
            latest = historical_events[-1] if historical_events else {}
            for view, unit, executor in views:
                selected_links = delivery_links if view == "dona" else [link for link in delivery_links if clean(plan_by_id.get(str(link.get("plano_trabalho_id")), {}).get("unidade_executora_sigla"), "N.I.") == unit]
                plan_ids = {str(link.get("plano_trabalho_id")) for link in selected_links}
                people = {str(plan_by_id.get(pid, {}).get("id_servidor") or "") for pid in plan_ids} - {""}
                acts = [item for pid in plan_ids for item in activities_by_plan.get(pid, [])]
                planned = _number(latest.get("progresso_esperado", delivery.get("meta_planejada")))
                actual = _number(latest.get("progresso_realizado", latest.get("realizado")))
                main.append({
                    "visao": view, "periodo": label, "periodo_inicio": start.isoformat(),
                    "periodo_fim": end.isoformat(), "unidade_sigla": unit,
                    "unidade_dona_sigla": owner, "unidade_executora_sigla": executor,
                    "id_entrega": delivery_id, "nome_entrega": name,
                    "meta_planejada": planned, "progresso_historico": actual,
                    "taxa_atingimento_perc": round(100 * actual / planned, 2) if planned else "",
                    "total_registros_execucao": len(period_events),
                    "data_ultimo_registro": latest.get("data_progresso", ""),
                    "total_planos_trabalho": len(plan_ids), "total_servidores": len(people),
                    "total_vinculos": len(selected_links),
                    "forca_trabalho_media_perc": round(sum(_number(x.get("forca_trabalho")) for x in selected_links) / len(selected_links), 2) if selected_links else 0,
                    "atividades_total": len(acts),
                    "atividades_iniciadas": sum(bool(x.get("data_inicio")) for x in acts),
                    "atividades_concluidas": sum(str(x.get("status") or "").upper() == "CONCLUIDO" for x in acts),
                    "horas_planejadas": round(sum(_number(x.get("tempo_planejado")) for x in acts), 2),
                    "horas_despendidas": round(sum(_number(x.get("tempo_despendido")) for x in acts), 2),
                    "situacao_cobertura": "COM_VINCULO_PT" if selected_links else "SEM_VINCULO_PT",
                    "situacao_reconciliacao": reconciliation(bool(historical_events), bool(selected_links)),
                })
        for event in events:
            event_day = _day(event.get("data_progresso"))
            period_label = next((p[0] for p in period_list if event_day and p[2] <= event_day <= p[4]), "FORA_DOS_CICLOS")
            history.append({
                "periodo": period_label, "unidade_dona_sigla": owner,
                "id_entrega": delivery_id, "nome_entrega": name,
                "data_progresso": event.get("data_progresso", ""), "meta": event.get("meta", ""),
                "realizado": event.get("realizado", ""), "progresso_esperado": event.get("progresso_esperado", ""),
                "progresso_realizado": event.get("progresso_realizado", ""),
                "registro_execucao": clean(event.get("registro_execucao")),
            })

    # A fotografia operacional inclui todos os PT elegíveis, inclusive sem vínculo.
    uncovered_by_unit: dict[str, list[Row]] = defaultdict(list)
    for plan_id, plan in plan_by_id.items():
        plan_links = links_by_plan.get(plan_id, [])
        acts = activities_by_plan.get(plan_id, [])
        if not plan_links:
            plan_links = [{"id_entrega": "", "forca_trabalho": ""}]
            uncovered_by_unit[clean(plan.get("unidade_executora_sigla"), "N.I.")].append(plan)
        for link in plan_links:
            delivery = delivery_by_id.get(str(link.get("id_entrega") or ""), {})
            nominal.append({
                "unidade_executora_sigla": clean(plan.get("unidade_executora_sigla"), "N.I."),
                "unidade_dona_sigla": clean(delivery.get("unidade_dona_sigla"), "N.I."),
                "id_servidor": plan.get("id_servidor", ""), "servidor_nome": clean(plan.get("servidor_nome")),
                "plano_trabalho_id": plan_id, "plano_numero": plan.get("plano_numero", ""),
                "plano_inicio": plan.get("plano_inicio", ""), "plano_fim": plan.get("plano_fim", ""),
                "id_entrega": link.get("id_entrega", ""), "nome_entrega": clean(delivery.get("nome_entrega")),
                "forca_trabalho": link.get("forca_trabalho", ""), "atividades_total": len(acts),
                "atividades_iniciadas": sum(bool(x.get("data_inicio")) for x in acts),
                "atividades_concluidas": sum(str(x.get("status") or "").upper() == "CONCLUIDO" for x in acts),
                "horas_planejadas": round(sum(_number(x.get("tempo_planejado")) for x in acts), 2),
                "horas_despendidas": round(sum(_number(x.get("tempo_despendido")) for x in acts), 2),
            })
    for unit, uncovered in uncovered_by_unit.items():
        plan_ids = {str(row.get("plano_trabalho_id")) for row in uncovered}
        people = {str(row.get("id_servidor")) for row in uncovered if row.get("id_servidor")}
        acts = [item for pid in plan_ids for item in activities_by_plan.get(pid, [])]
        main.append({
            "visao": "executora", "periodo": f"FOTOGRAFIA-{observation_date.isoformat()}",
            "periodo_inicio": observation_date.isoformat(), "periodo_fim": observation_date.isoformat(),
            "unidade_sigla": unit, "unidade_dona_sigla": "N.I.",
            "unidade_executora_sigla": unit, "id_entrega": f"SEM_ENTREGA:{unit}",
            "nome_entrega": "PT sem entrega identificável", "meta_planejada": "",
            "progresso_historico": "", "taxa_atingimento_perc": "",
            "total_registros_execucao": 0, "data_ultimo_registro": "",
            "total_planos_trabalho": len(plan_ids), "total_servidores": len(people),
            "total_vinculos": 0, "forca_trabalho_media_perc": 0,
            "atividades_total": len(acts),
            "atividades_iniciadas": sum(bool(x.get("data_inicio")) for x in acts),
            "atividades_concluidas": sum(str(x.get("status") or "").upper() == "CONCLUIDO" for x in acts),
            "horas_planejadas": round(sum(_number(x.get("tempo_planejado")) for x in acts), 2),
            "horas_despendidas": round(sum(_number(x.get("tempo_despendido")) for x in acts), 2),
            "situacao_cobertura": "PT_SEM_ENTREGA",
            "situacao_reconciliacao": reconciliation(False, True, False),
        })
    orphan_by_unit: dict[str, list[Row]] = defaultdict(list)
    for link in links:
        if str(link.get("id_entrega") or "") not in delivery_by_id:
            plan = plan_by_id.get(str(link.get("plano_trabalho_id") or ""), {})
            orphan_by_unit[clean(plan.get("unidade_executora_sigla"), "N.I.")].append(link)
    for unit, orphan_links in orphan_by_unit.items():
        plan_ids = {str(row.get("plano_trabalho_id")) for row in orphan_links}
        people = {str(plan_by_id.get(pid, {}).get("id_servidor") or "") for pid in plan_ids} - {""}
        main.append({
            "visao": "executora", "periodo": f"FOTOGRAFIA-{observation_date.isoformat()}",
            "periodo_inicio": observation_date.isoformat(), "periodo_fim": observation_date.isoformat(),
            "unidade_sigla": unit, "unidade_dona_sigla": "N.I.",
            "unidade_executora_sigla": unit, "id_entrega": f"VINCULO_SEM_ENTREGA:{unit}",
            "nome_entrega": "Vínculo sem entrega de PE identificável", "meta_planejada": "",
            "progresso_historico": "", "taxa_atingimento_perc": "",
            "total_registros_execucao": 0, "data_ultimo_registro": "",
            "total_planos_trabalho": len(plan_ids), "total_servidores": len(people),
            "total_vinculos": len(orphan_links), "forca_trabalho_media_perc": round(sum(_number(x.get("forca_trabalho")) for x in orphan_links) / len(orphan_links), 2),
            "atividades_total": 0, "atividades_iniciadas": 0, "atividades_concluidas": 0,
            "horas_planejadas": 0, "horas_despendidas": 0,
            "situacao_cobertura": "VINCULO_SEM_ENTREGA",
            "situacao_reconciliacao": reconciliation(False, True, False),
        })
    main.sort(key=lambda r: (str(r["periodo"]), str(r["visao"]), str(r["unidade_sigla"]), str(r["id_entrega"])))
    history.sort(key=lambda r: (str(r["data_progresso"]), str(r["id_entrega"])))
    nominal.sort(key=lambda r: (str(r["unidade_executora_sigla"]), str(r["servidor_nome"]), str(r["plano_trabalho_id"])))
    return main, history, nominal


def shared_rows(rows: list[Row], eligible_servers: int, k: int = 5) -> list[Row]:
    """Remove detalhe quando o escopo ou a célula entrega/unidade não atinge k."""
    if eligible_servers < k:
        return []
    visible = [dict(row) for row in rows if int(row.get("total_servidores") or 0) >= k]
    # Supressão complementar: se uma unidade perdeu alguma célula, oculta também
    # sua menor célula visível, impedindo dedução por totais externos.
    all_units = {str(row.get("unidade_sigla")) for row in rows}
    for unit in all_units:
        original = [row for row in rows if str(row.get("unidade_sigla")) == unit]
        kept = [row for row in visible if str(row.get("unidade_sigla")) == unit]
        if len(kept) < len(original) and kept:
            smallest = min(kept, key=lambda row: int(row.get("total_servidores") or 0))
            visible.remove(smallest)
    return visible
