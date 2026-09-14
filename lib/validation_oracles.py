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


def _quantile(ordered: list[float], fraction: float) -> float:
    """Quantil por interpolação linear — reimplementado para manter independência."""

    if not ordered:
        return 0.0
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def oracle_i05(records: list[Row]) -> list[Row]:
    """Distribuição de entregas por servidor em duas visões (decisão CGOV D07).

    A visão nominal permanece como produto restrito; a visão estatística
    descreve a dispersão dentro da unidade sem identificar ninguém — a média
    sozinha não distingue uma equipe equilibrada de outra concentrada.
    """

    output: list[Row] = []
    for (period, unit), unit_rows in _group(_active(records), "periodo", "unidade_sigla").items():
        counts: dict[str, int] = {}
        for (user,), rows in _group(unit_rows, "id_servidor").items():
            counts[str(user)] = len({str(row.get("id_entrega")) for row in rows})
        average = round(mean(counts.values()), 2) if counts else 0.0
        for user, count in counts.items():
            output.append({
                "visao": "nominal",
                "periodo": period, "unidade_sigla": unit, "id_servidor": user,
                "qtd_entregas_por_servidor": count,
                "media_entregas_por_servidor_unidade": average,
                "posicao_relativa_media": (
                    "Acima da media" if count > average else "Abaixo da media" if count < average else "Na media"
                ),
            })
        ordered = sorted(float(value) for value in counts.values())
        total = len(ordered)
        middle = total // 2
        median = (
            ordered[middle] if total % 2
            else (ordered[middle - 1] + ordered[middle]) / 2
        ) if total else 0.0
        output.append({
            "visao": "estatistica",
            "periodo": period, "unidade_sigla": unit,
            "total_servidores": total,
            "media_entregas_por_servidor": average,
            "mediana_entregas_por_servidor": round(median, 2),
            "p25_entregas_por_servidor": round(_quantile(ordered, 0.25), 2),
            "p75_entregas_por_servidor": round(_quantile(ordered, 0.75), 2),
            "pct_servidores_sem_entrega": (
                round(100 * sum(1 for value in ordered if value == 0) / total, 2)
                if total else 0.0
            ),
        })
    return _sorted(output, ("visao", "periodo", "unidade_sigla", "id_servidor"))


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


def _pascoa_independente(ano: int) -> date:
    """Meeus/Butcher reimplementado — ver ``_dias_uteis_independente``."""

    a = ano % 19
    b, c = divmod(ano, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    j = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * j) // 451
    mes, dia = divmod(h + j - 7 * m + 114, 31)
    return date(ano, mes, dia + 1)


def _feriados_independentes(ano: int) -> set[date]:
    domingo = _pascoa_independente(ano)
    fixos = [(1, 1), (4, 21), (5, 1), (9, 7), (10, 12), (11, 2), (11, 15), (12, 25)]
    return {date(ano, mes, dia) for mes, dia in fixos} | {
        domingo - timedelta(days=48), domingo - timedelta(days=47),
        domingo - timedelta(days=2), domingo + timedelta(days=60),
    }


def _dias_uteis_independente(inicio: date, fim: date) -> int:
    """Contagem de dias úteis própria do oracle (decisão CGOV D09).

    Duplica deliberadamente :mod:`lib.calendario`: importar o módulo de produção
    quebraria a independência exigida por
    ``tests/regression/test_validation_independence.py``. A equivalência entre as
    duas implementações é provada em ``tests/unit/test_calendario.py``.
    """

    if fim < inicio:
        return 0
    total = 0
    dia = inicio
    feriados = _feriados_independentes(inicio.year) | _feriados_independentes(fim.year)
    while dia <= fim:
        if dia.weekday() < 5 and dia not in feriados:
            total += 1
        dia += timedelta(days=1)
    return total


def _allocated_hours(row: Row) -> tuple[float, float]:
    start, end = _date(row.get("plano_inicio")), _date(row.get("plano_fim"))
    overlap_start, overlap_end = _date(row.get("sobreposicao_inicio")), _date(row.get("sobreposicao_fim"))
    if not start or not end or not overlap_start or not overlap_end or end < start or overlap_end < overlap_start:
        return 0.0, 0.0
    base = _float(row.get("carga_horaria"))
    if row.get("forma_contagem_carga_horaria") == "DIAS":
        base *= 8.0
    # D09: rateio por dias úteis institucionais, não por dias corridos.
    denominador = _dias_uteis_independente(start, end)
    if not denominador:
        return 0.0, 0.0
    proportional = base * _dias_uteis_independente(overlap_start, overlap_end) / denominador
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
            # D09: a contagem é de planos de trabalho, não de pessoas — um
            # servidor com dois PTs na mesma entrega contava duas vezes sob o
            # nome antigo (num_servidores_alocados).
            "num_planos_trabalho_alocados": len(plans),
        })
    return _sorted(output, ("periodo", "unidade_sigla", "id_entrega"))


def oracle_i08(records: list[Row]) -> list[Row]:
    """Duas visões coerentes da proporção de horas (decisão CGOV D10).

    Numerador e denominador sempre da mesma unidade: a visão ``dona`` mede o
    quanto as entregas planejadas por uma unidade consomem da capacidade dela,
    e a visão ``executora`` mede o quanto da capacidade de uma unidade está
    comprometido com cada entrega, de quem quer que seja a entrega.
    """

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

    visoes = (
        ("dona", "unidade_dona_sigla",
         ("horas_planejadas_entrega", "total_horas_disponiveis_unidade", "proporcao_horas_perc")),
        ("executora", "unidade_executora_sigla",
         ("horas_executora", "capacidade_executora", "proporcao_executora_perc")),
    )
    for visao, sigla_key, (nome_horas, nome_capacidade, nome_perc) in visoes:
        grupos: dict[tuple[Any, Any, Any], list[Row]] = defaultdict(list)
        for row in active:
            # Fixtures antigas trazem só unidade_sigla; nesse caso as duas
            # visões coincidem, que é o comportamento anterior à D10.
            unit = row.get(sigla_key, row.get("unidade_sigla", "N.I."))
            grupos[(row.get("periodo"), unit, row.get("id_entrega"))].append(row)
        for (period, unit, delivery), rows in grupos.items():
            hours = sum(_allocated_hours(row)[1] for row in rows)
            available = capacity[(period, unit)]
            output.append({
                "visao": visao, "periodo": period, "unidade_sigla": unit,
                "id_entrega": delivery,
                nome_horas: round(hours, 2),
                nome_capacidade: round(available, 2),
                nome_perc: round(100 * hours / available, 2) if available else 0.0,
            })
    return _sorted(output, ("visao", "periodo", "unidade_sigla", "id_entrega"))


def _score(row: Row) -> int:
    return 6 - int(_float(row.get("sequencia_nota")))


def oracle_i09(records: list[Row]) -> list[Row]:
    output: list[Row] = []
    unique = _unique(_active(records), "periodo", "id_avaliacao")
    for (period, unit), rows in _group(unique, "periodo", "unidade_sigla").items():
        values = [_score(row) for row in rows]
        # D11: a métrica primária é a média das médias por plano de trabalho —
        # cada plano pesa 1, independentemente de quantas consolidações mensais
        # acumulou. A média sobre eventos fica como coluna de comparação.
        por_plano = [
            mean(_score(row) for row in plano_rows)
            for _, plano_rows in _group(rows, "plano_trabalho_id").items()
        ]
        result: Row = {
            "periodo": period, "unidade_sigla": unit, "total_avaliacoes_pt": len(values),
            "total_planos_com_avaliacao": len({str(row.get("plano_trabalho_id")) for row in rows}),
            "total_servidores_avaliados": len({str(row.get("id_servidor")) for row in rows}),
            "media_nota_pt": round(mean(por_plano), 2),
            "media_nota_pt_eventos": round(mean(values), 2),
            "nota_minima": min(values), "nota_maxima": max(values),
        }
        for note in range(1, 6):
            result[f"qtd_nota_{note}"] = values.count(note)
        output.append(result)
    return _sorted(output, ("periodo", "unidade_sigla"))


# D12 (CGOV, 13.09.2026): abaixo deste volume o percentual é estatisticamente
# frágil. A linha não é suprimida — a volumetria é exportada para que o BI
# decida ocultar ou cinzentar a unidade.
VOLUME_MINIMO_AVALIACOES = 5


def _category_oracle(records: list[Row], sequence: int, count_name: str, percent_name: str) -> list[Row]:
    output: list[Row] = []
    unique = _unique(_active(records), "periodo", "id_avaliacao")
    for (period, unit), rows in _group(unique, "periodo", "unidade_sigla").items():
        count = sum(int(_float(row.get("sequencia_nota"))) == sequence for row in rows)
        output.append({
            "periodo": period, "unidade_sigla": unit, "total_avaliacoes_pt": len(rows),
            "total_servidores_avaliados": len({str(row.get("id_servidor")) for row in rows}),
            count_name: count, percent_name: round(100 * count / len(rows), 2) if rows else 0.0,
            "volume_suficiente": 1 if len(rows) >= VOLUME_MINIMO_AVALIACOES else 0,
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


def oracle_ind_gest_01(records: list[Row]) -> list[Row]:
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
        # D17/F1: concluído com período entregue e não avaliado continua na fila.
        pending_closed = status == "CONCLUIDO" and plan["aguardando"] > 0
        if status not in {"INCLUIDO", "AGUARDANDO_ASSINATURA", "ATIVO", "SUSPENSO"} and not pending_closed:
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


def _g02_periods(cutoff: date) -> list[tuple[str, date, date]]:
    raw = [
        ("T3-2025", date(2025, 7, 1), date(2025, 9, 30)),
        ("T4-2025", date(2025, 10, 1), date(2025, 12, 31)),
        ("Q1-2026", date(2026, 1, 1), date(2026, 4, 30)),
        ("Q2-2026", date(2026, 5, 1), date(2026, 8, 31)),
    ]
    return [(label, start, min(end, cutoff)) for label, start, end in raw if start <= cutoff]


def _g02_reconciliation(history: bool, links: bool) -> str:
    if history and links:
        return "HISTORICO_PE_E_EVIDENCIA_PT"
    if history:
        return "HISTORICO_PE_SEM_VINCULO_PT"
    if links:
        return "TRABALHO_PT_SEM_HISTORICO_PE"
    return "SEM_HISTORICO_PE_E_SEM_VINCULO_PT"


def oracle_ind_gest_02(records: list[Row]) -> list[Row]:
    """Oracle independente da implementação de produção do G02."""
    names = ("g02_entregas", "g02_progressos", "g02_planos", "g02_vinculos", "g02_atividades")
    buckets = {name: [] for name in names}
    for row in records:
        source = str(row.get("_extractor") or "")
        if source in buckets and not row.get("deleted_at"):
            buckets[source].append(dict(row))
    all_rows = [row for values in buckets.values() for row in values]
    cutoff = _date(next((row.get("_history_cutoff") for row in all_rows if row.get("_history_cutoff")), "2026-08-31")) or date(2026, 8, 31)
    deliveries = {str(row.get("id_entrega")): row for row in _unique(buckets["g02_entregas"], "id_entrega")}
    plans = {str(row.get("plano_trabalho_id")): row for row in _unique(buckets["g02_planos"], "plano_trabalho_id")}
    progress = _group(_unique(buckets["g02_progressos"], "progresso_id"), "id_entrega")
    links = _group(_unique(buckets["g02_vinculos"], "vinculo_id"), "id_entrega")
    links_by_plan = _group(_unique(buckets["g02_vinculos"], "vinculo_id"), "plano_trabalho_id")
    activities = _group(_unique(buckets["g02_atividades"], "atividade_id"), "plano_trabalho_id")
    output: list[Row] = []
    for delivery_id, delivery in deliveries.items():
        owner = str(delivery.get("unidade_dona_sigla") or "N.I.")
        events = sorted(progress.get((delivery_id,), []), key=lambda row: str(row.get("data_progresso") or ""))
        delivery_links = links.get((delivery_id,), [])
        executors = sorted({str(plans.get(str(link.get("plano_trabalho_id")), {}).get("unidade_executora_sigla") or "N.I.") for link in delivery_links})
        views = [("dona", owner, "MULTIPLAS" if len(executors) > 1 else (executors[0] if executors else "SEM_VINCULO"))]
        views.extend(("executora", executor, executor) for executor in executors)
        for label, start, end in _g02_periods(cutoff):
            if (_date(delivery.get("entrega_inicio")) or date.min) > end or (_date(delivery.get("entrega_fim")) or date.max) < start:
                continue
            within = [row for row in events if start <= (_date(row.get("data_progresso")) or date.min) <= end]
            historical = [row for row in events if (_date(row.get("data_progresso")) or date.max) <= end]
            latest = historical[-1] if historical else {}
            for view, unit, executor in views:
                selected = delivery_links if view == "dona" else [row for row in delivery_links if str(plans.get(str(row.get("plano_trabalho_id")), {}).get("unidade_executora_sigla") or "N.I.") == unit]
                plan_ids = {str(row.get("plano_trabalho_id")) for row in selected}
                people = {str(plans.get(pid, {}).get("id_servidor") or "") for pid in plan_ids} - {""}
                acts = [row for pid in plan_ids for row in activities.get((pid,), [])]
                planned = _float(latest.get("progresso_esperado", delivery.get("meta_planejada")))
                actual = _float(latest.get("progresso_realizado", latest.get("realizado")))
                output.append({
                    "visao": view, "periodo": label, "periodo_inicio": start.isoformat(), "periodo_fim": end.isoformat(),
                    "unidade_sigla": unit, "unidade_dona_sigla": owner,
                    "unidade_executora_sigla": executor, "id_entrega": delivery_id,
                    "nome_entrega": delivery.get("nome_entrega", "N.I."),
                    "meta_planejada": planned, "progresso_historico": actual,
                    "taxa_atingimento_perc": round(100 * actual / planned, 2) if planned else "",
                    "total_registros_execucao": len(within), "data_ultimo_registro": latest.get("data_progresso", ""),
                    "total_planos_trabalho": len(plan_ids), "total_servidores": len(people),
                    "total_vinculos": len(selected),
                    "forca_trabalho_media_perc": round(sum(_float(row.get("forca_trabalho")) for row in selected) / len(selected), 2) if selected else 0,
                    "atividades_total": len(acts), "atividades_iniciadas": sum(bool(row.get("data_inicio")) for row in acts),
                    "atividades_concluidas": sum(str(row.get("status") or "").upper() == "CONCLUIDO" for row in acts),
                    "horas_planejadas": round(sum(_float(row.get("tempo_planejado")) for row in acts), 2),
                    "horas_despendidas": round(sum(_float(row.get("tempo_despendido")) for row in acts), 2),
                    "situacao_cobertura": "COM_VINCULO_PT" if selected else "SEM_VINCULO_PT",
                    "situacao_reconciliacao": _g02_reconciliation(bool(historical), bool(selected)),
                })
    observation = _date(next((row.get("_observation_date") for row in all_rows if row.get("_observation_date")), cutoff)) or cutoff
    uncovered: dict[str, list[Row]] = defaultdict(list)
    for plan_id, plan in plans.items():
        if not links_by_plan.get((plan_id,), []):
            uncovered[str(plan.get("unidade_executora_sigla") or "N.I.")].append(plan)
    for unit, unit_plans in uncovered.items():
        plan_ids = {str(row.get("plano_trabalho_id")) for row in unit_plans}
        people = {str(row.get("id_servidor") or "") for row in unit_plans} - {""}
        acts = [row for pid in plan_ids for row in activities.get((pid,), [])]
        output.append({
            "visao": "executora", "periodo": f"FOTOGRAFIA-{observation.isoformat()}",
            "periodo_inicio": observation.isoformat(), "periodo_fim": observation.isoformat(),
            "unidade_sigla": unit, "unidade_dona_sigla": "N.I.", "unidade_executora_sigla": unit,
            "id_entrega": f"SEM_ENTREGA:{unit}", "nome_entrega": "PT sem entrega identificável",
            "meta_planejada": "", "progresso_historico": "", "taxa_atingimento_perc": "",
            "total_registros_execucao": 0, "data_ultimo_registro": "",
            "total_planos_trabalho": len(plan_ids), "total_servidores": len(people),
            "total_vinculos": 0, "forca_trabalho_media_perc": 0,
            "atividades_total": len(acts), "atividades_iniciadas": sum(bool(row.get("data_inicio")) for row in acts),
            "atividades_concluidas": sum(str(row.get("status") or "").upper() == "CONCLUIDO" for row in acts),
            "horas_planejadas": round(sum(_float(row.get("tempo_planejado")) for row in acts), 2),
            "horas_despendidas": round(sum(_float(row.get("tempo_despendido")) for row in acts), 2),
            "situacao_cobertura": "PT_SEM_ENTREGA", "situacao_reconciliacao": "PT_OU_VINCULO_SEM_ENTREGA_IDENTIFICAVEL",
        })
    orphan_groups: dict[str, list[Row]] = defaultdict(list)
    for row in buckets["g02_vinculos"]:
        if str(row.get("id_entrega") or "") not in deliveries:
            plan = plans.get(str(row.get("plano_trabalho_id") or ""), {})
            orphan_groups[str(plan.get("unidade_executora_sigla") or "N.I.")].append(row)
    for unit, orphan_links in orphan_groups.items():
        plan_ids = {str(row.get("plano_trabalho_id")) for row in orphan_links}
        people = {str(plans.get(pid, {}).get("id_servidor") or "") for pid in plan_ids} - {""}
        output.append({
            "visao": "executora", "periodo": f"FOTOGRAFIA-{observation.isoformat()}",
            "periodo_inicio": observation.isoformat(), "periodo_fim": observation.isoformat(),
            "unidade_sigla": unit, "unidade_dona_sigla": "N.I.", "unidade_executora_sigla": unit,
            "id_entrega": f"VINCULO_SEM_ENTREGA:{unit}", "nome_entrega": "Vínculo sem entrega de PE identificável",
            "meta_planejada": "", "progresso_historico": "", "taxa_atingimento_perc": "",
            "total_registros_execucao": 0, "data_ultimo_registro": "",
            "total_planos_trabalho": len(plan_ids), "total_servidores": len(people),
            "total_vinculos": len(orphan_links),
            "forca_trabalho_media_perc": round(sum(_float(row.get("forca_trabalho")) for row in orphan_links) / len(orphan_links), 2),
            "atividades_total": 0, "atividades_iniciadas": 0, "atividades_concluidas": 0,
            "horas_planejadas": 0, "horas_despendidas": 0,
            "situacao_cobertura": "VINCULO_SEM_ENTREGA", "situacao_reconciliacao": "PT_OU_VINCULO_SEM_ENTREGA_IDENTIFICAVEL",
        })
    return _sorted(output, ("periodo", "visao", "unidade_sigla", "id_entrega"))


ORACLES: dict[str, Callable[[list[Row]], list[Row]]] = {
    "I01": oracle_i01, "I02": oracle_i02, "I03": oracle_i03, "I04": oracle_i04,
    "I05": oracle_i05, "I06": oracle_i06, "I07": oracle_i07, "I08": oracle_i08,
    "I09": oracle_i09, "I10": oracle_i10, "I11": oracle_i11, "I12": oracle_i12,
    "G01": oracle_ind_gest_01, "G02": oracle_ind_gest_02,
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
