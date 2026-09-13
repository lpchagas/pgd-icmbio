"""Extração agregada dos registros de execução de PE, PT, atividades e consolidações.

As consultas não selecionam nomes, textos livres, CPF ou e-mail. Contagens
exatas permanecem em memória; a função pública devolve somente faixas e taxas.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Mapping

from lib.monthly_runner import query_rows
from lib.periodos import AnalysisWindow
from ocde.relatorios.escopo import ScopeSpec, UnitProfile, unit_matches
from ocde.relatorios.privacidade import count_band, eligible, quantity_band, rounded_percent


SQL_PE = """
WITH pe_scope AS (
    SELECT pe.id, pe.unidade_id, pe.status, CAST(pe.data_fim AS DATE) AS fim
    FROM petrvs_icmbio_planos_entregas pe
    WHERE pe.deleted_at IS NULL
      AND CAST(pe.data_inicio AS DATE) <= CAST('{fim}' AS DATE)
      AND CAST(pe.data_fim AS DATE) >= CAST('{inicio}' AS DATE)
),
pe_base AS (
    SELECT id, unidade_id, status FROM pe_scope
    WHERE fim <= CAST('{fim}' AS DATE)
),
pe_agg AS (
    SELECT unidade_id,
           COUNT(DISTINCT id) AS planos_entregas,
           SUM(CASE WHEN status = 'AVALIADO' THEN 1 ELSE 0 END) AS planos_avaliados
    FROM pe_base GROUP BY unidade_id
),
entrega_agg AS (
    SELECT pb.unidade_id,
           COUNT(DISTINCT e.id) AS entregas,
           SUM(CASE WHEN e.progresso_esperado > 0
                     AND e.progresso_realizado >= e.progresso_esperado THEN 1 ELSE 0 END) AS entregas_concluidas,
           SUM(CASE WHEN e.progresso_esperado > 0 THEN 1 ELSE 0 END) AS entregas_com_meta
    FROM pe_base pb
    JOIN petrvs_icmbio_planos_entregas_entregas e
      ON e.plano_entrega_id = pb.id AND e.deleted_at IS NULL
    WHERE CAST(e.data_inicio AS DATE) <= CAST('{fim}' AS DATE)
      AND CAST(e.data_fim AS DATE) >= CAST('{inicio}' AS DATE)
    GROUP BY pb.unidade_id
),
eventos AS (
    SELECT pe.unidade_id, COUNT(*) AS transicoes_pe
    FROM petrvs_icmbio_status_justificativas sj
    JOIN pe_scope pe ON pe.id = sj.plano_entrega_id
    WHERE sj.deleted_at IS NULL
      AND CAST(sj.created_at AS DATE) BETWEEN CAST('{inicio}' AS DATE) AND CAST('{fim}' AS DATE)
    GROUP BY pe.unidade_id
)
SELECT u.sigla AS unidade_sigla,
       COALESCE(p.planos_entregas, 0) AS planos_entregas,
       COALESCE(p.planos_avaliados, 0) AS planos_avaliados,
       COALESCE(e.entregas, 0) AS entregas,
       COALESCE(e.entregas_com_meta, 0) AS entregas_com_meta,
       COALESCE(e.entregas_concluidas, 0) AS entregas_concluidas,
       COALESCE(v.transicoes_pe, 0) AS transicoes_pe
FROM (SELECT DISTINCT unidade_id FROM pe_scope) s
JOIN petrvs_icmbio_unidades u ON u.id = s.unidade_id AND u.deleted_at IS NULL
LEFT JOIN pe_agg p ON p.unidade_id = s.unidade_id
LEFT JOIN entrega_agg e ON e.unidade_id = s.unidade_id
LEFT JOIN eventos v ON v.unidade_id = s.unidade_id
"""


SQL_PT = """
WITH pt_base AS (
    SELECT pt.id, pt.unidade_id, pt.usuario_id, pt.status,
           CAST(pt.data_inicio AS DATE) AS inicio, CAST(pt.data_fim AS DATE) AS fim
    FROM petrvs_icmbio_planos_trabalhos pt
    WHERE pt.deleted_at IS NULL
      AND CAST(pt.data_inicio AS DATE) <= CAST('{fim}' AS DATE)
      AND CAST(pt.data_fim AS DATE) >= CAST('{inicio}' AS DATE)
),
pt_agg AS (
    SELECT unidade_id, COUNT(DISTINCT id) AS planos_trabalho,
           COUNT(DISTINCT usuario_id) AS servidores,
           SUM(CASE WHEN fim <= CAST('{fim}' AS DATE) THEN 1 ELSE 0 END) AS pt_status_elegiveis,
           SUM(CASE WHEN fim <= CAST('{fim}' AS DATE) AND status = 'CONCLUIDO' THEN 1 ELSE 0 END) AS pt_concluidos,
           SUM(CASE WHEN fim <= CAST('{fim}' AS DATE) AND status IN ('INCLUIDO','AGUARDANDO_ASSINATURA','ATIVO','SUSPENSO') THEN 1 ELSE 0 END) AS pt_abertos
    FROM pt_base GROUP BY unidade_id
),
atividade_agg AS (
    SELECT pb.unidade_id, COUNT(DISTINCT a.id) AS atividades,
           SUM(CASE WHEN a.status = 'CONCLUIDO'
                     AND CAST(a.data_entrega AS DATE) BETWEEN CAST('{inicio}' AS DATE) AND CAST('{fim}' AS DATE)
                    THEN 1 ELSE 0 END) AS atividades_concluidas,
           SUM(CASE WHEN CAST(a.data_distribuicao AS DATE) BETWEEN CAST('{inicio}' AS DATE) AND CAST('{fim}' AS DATE)
                    THEN COALESCE(a.tempo_planejado, 0) ELSE 0 END) AS horas_planejadas,
           SUM(CASE WHEN CAST(a.data_entrega AS DATE) BETWEEN CAST('{inicio}' AS DATE) AND CAST('{fim}' AS DATE)
                    THEN COALESCE(a.tempo_despendido, 0) ELSE 0 END) AS horas_despendidas
    FROM pt_base pb
    JOIN petrvs_icmbio_atividades a ON a.plano_trabalho_id = pb.id AND a.deleted_at IS NULL
    WHERE (CAST(a.data_distribuicao AS DATE) BETWEEN CAST('{inicio}' AS DATE) AND CAST('{fim}' AS DATE)
       OR CAST(a.data_inicio AS DATE) BETWEEN CAST('{inicio}' AS DATE) AND CAST('{fim}' AS DATE)
       OR CAST(a.data_entrega AS DATE) BETWEEN CAST('{inicio}' AS DATE) AND CAST('{fim}' AS DATE))
    GROUP BY pb.unidade_id
),
avaliacao_consolidacao AS (
    SELECT av.plano_trabalho_consolidacao_id,
           MIN(CAST(av.data_avaliacao AS DATE)) AS primeira_avaliacao
    FROM petrvs_icmbio_avaliacoes av
    WHERE av.deleted_at IS NULL
      AND av.plano_trabalho_consolidacao_id IS NOT NULL
    GROUP BY av.plano_trabalho_consolidacao_id
),
consolidacao_agg AS (
    SELECT pb.unidade_id, COUNT(DISTINCT c.id) AS consolidacoes,
           SUM(CASE WHEN ac.primeira_avaliacao BETWEEN CAST('{inicio}' AS DATE) AND CAST('{fim}' AS DATE)
                    THEN 1 ELSE 0 END) AS consol_avaliadas,
           SUM(CASE WHEN CAST(c.data_conclusao AS DATE) BETWEEN CAST('{inicio}' AS DATE) AND CAST('{fim}' AS DATE)
                     AND (ac.primeira_avaliacao IS NULL OR ac.primeira_avaliacao > CAST('{fim}' AS DATE))
                    THEN 1 ELSE 0 END) AS aguardando_avaliacao
    FROM pt_base pb
    JOIN petrvs_icmbio_planos_trabalhos_consolidacoes c
      ON c.plano_trabalho_id = pb.id AND c.deleted_at IS NULL
    LEFT JOIN avaliacao_consolidacao ac ON ac.plano_trabalho_consolidacao_id = c.id
    WHERE CAST(c.data_inicio AS DATE) <= CAST('{fim}' AS DATE)
      AND CAST(c.data_fim AS DATE) >= CAST('{inicio}' AS DATE)
    GROUP BY pb.unidade_id
),
eventos_pt AS (
    SELECT pb.unidade_id, COUNT(*) AS transicoes_pt
    FROM petrvs_icmbio_status_justificativas sj
    JOIN pt_base pb ON pb.id = sj.plano_trabalho_id
    WHERE sj.deleted_at IS NULL
      AND CAST(sj.created_at AS DATE) BETWEEN CAST('{inicio}' AS DATE) AND CAST('{fim}' AS DATE)
    GROUP BY pb.unidade_id
),
eventos_consolidacao AS (
    SELECT pb.unidade_id, COUNT(*) AS transicoes_consolidacao
    FROM petrvs_icmbio_status_justificativas sj
    JOIN petrvs_icmbio_planos_trabalhos_consolidacoes c
      ON c.id = sj.plano_trabalho_consolidacao_id AND c.deleted_at IS NULL
    JOIN pt_base pb ON pb.id = c.plano_trabalho_id
    WHERE sj.deleted_at IS NULL
      AND CAST(sj.created_at AS DATE) BETWEEN CAST('{inicio}' AS DATE) AND CAST('{fim}' AS DATE)
    GROUP BY pb.unidade_id
),
eventos_atividade AS (
    SELECT pb.unidade_id, COUNT(*) AS transicoes_atividade
    FROM petrvs_icmbio_status_justificativas sj
    JOIN petrvs_icmbio_atividades a ON a.id = sj.atividade_id AND a.deleted_at IS NULL
    JOIN pt_base pb ON pb.id = a.plano_trabalho_id
    WHERE sj.deleted_at IS NULL
      AND CAST(sj.created_at AS DATE) BETWEEN CAST('{inicio}' AS DATE) AND CAST('{fim}' AS DATE)
    GROUP BY pb.unidade_id
)
SELECT u.sigla AS unidade_sigla,
       p.planos_trabalho, p.servidores, p.pt_status_elegiveis, p.pt_concluidos, p.pt_abertos,
       COALESCE(a.atividades, 0) AS atividades,
       COALESCE(a.atividades_concluidas, 0) AS atividades_concluidas,
       COALESCE(a.horas_planejadas, 0) AS horas_planejadas,
       COALESCE(a.horas_despendidas, 0) AS horas_despendidas,
       COALESCE(c.consolidacoes, 0) AS consolidacoes,
       COALESCE(c.consol_avaliadas, 0) AS consol_avaliadas,
       COALESCE(c.aguardando_avaliacao, 0) AS aguardando_avaliacao,
       COALESCE(v.transicoes_pt, 0) AS transicoes_pt,
       COALESCE(vc.transicoes_consolidacao, 0) AS transicoes_consolidacao,
       COALESCE(va.transicoes_atividade, 0) AS transicoes_atividade
FROM pt_agg p
JOIN petrvs_icmbio_unidades u ON u.id = p.unidade_id AND u.deleted_at IS NULL
LEFT JOIN atividade_agg a ON a.unidade_id = p.unidade_id
LEFT JOIN consolidacao_agg c ON c.unidade_id = p.unidade_id
LEFT JOIN eventos_pt v ON v.unidade_id = p.unidade_id
LEFT JOIN eventos_consolidacao vc ON vc.unidade_id = p.unidade_id
LEFT JOIN eventos_atividade va ON va.unidade_id = p.unidade_id
"""


def _number(value: object) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _query(conn, template: str, window: AnalysisWindow) -> list[dict[str, str]]:
    sql = template.format(inicio=window.inicio.isoformat(), fim=window.fim.isoformat())
    columns, rows = query_rows(conn, sql)
    return [dict(zip(columns, row)) for row in rows]


def _progress_events(conn, window: AnalysisWindow) -> tuple[dict[str, float], str]:
    """Descobre o esquema da trilha de progresso e conta apenas eventos no corte."""
    try:
        columns, _ = query_rows(
            conn, "SELECT * FROM petrvs_icmbio_planos_entregas_entregas_progressos WHERE 1 = 0"
        )
        names = {column.lower(): column for column in columns}
        fk = names.get("plano_entrega_entrega_id")
        reference = next((names[item] for item in (
            "data_progresso", "data_referencia", "created_at", "updated_at"
        ) if item in names), None)
        if not fk or not reference:
            return {}, "indisponível: colunas de vínculo/data não identificadas"
        active = "AND p.deleted_at IS NULL" if "deleted_at" in names else ""
        sql = f"""
SELECT u.sigla AS unidade_sigla, COUNT(*) AS eventos_progresso
FROM petrvs_icmbio_planos_entregas_entregas_progressos p
JOIN petrvs_icmbio_planos_entregas_entregas e ON e.id = p.{fk} AND e.deleted_at IS NULL
JOIN petrvs_icmbio_planos_entregas pe ON pe.id = e.plano_entrega_id AND pe.deleted_at IS NULL
JOIN petrvs_icmbio_unidades u ON u.id = pe.unidade_id AND u.deleted_at IS NULL
WHERE CAST(p.{reference} AS DATE) BETWEEN CAST('{window.inicio}' AS DATE) AND CAST('{window.fim}' AS DATE)
  {active}
GROUP BY u.sigla
"""
        event_columns, event_rows = query_rows(conn, sql)
        mapped = [dict(zip(event_columns, row)) for row in event_rows]
        return {str(row["unidade_sigla"]): _number(row["eventos_progresso"]) for row in mapped}, "disponível e filtrado pela data do evento"
    except Exception as exc:
        return {}, f"indisponível nesta extração: {type(exc).__name__}"


def extract_execution(
    conn,
    window: AnalysisWindow,
    scope: ScopeSpec,
    profiles: Mapping[str, UnitProfile],
    people_by_unit: Mapping[str, int],
    total_people: int,
) -> list[dict[str, str]]:
    pe = [row for row in _query(conn, SQL_PE, window) if unit_matches(row, scope, profiles)]
    pt = [row for row in _query(conn, SQL_PT, window) if unit_matches(row, scope, profiles)]
    progress_by_unit, progress_status = _progress_events(conn, window)
    by_unit: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for row in pe + pt:
        unit = str(row.get("unidade_sigla") or "")
        for key, value in row.items():
            if key != "unidade_sigla":
                by_unit[unit][key] += _number(value)
    for unit in by_unit:
        by_unit[unit]["eventos_progresso"] = progress_by_unit.get(unit, 0)

    rows_out: list[dict[str, str]] = []
    has_low_unit = any(not eligible(int(people_by_unit.get(unit.upper(), 0))) for unit in by_unit)
    for unit, values in sorted(by_unit.items()):
        people = int(people_by_unit.get(unit.upper(), 0))
        if not eligible(people):
            continue
        if not has_low_unit:
            rows_out.append(_public_row(unit, values, people, "unidade", progress_status))

    if eligible(total_people):
        totals: dict[str, float] = defaultdict(float)
        for values in by_unit.values():
            for key, value in values.items():
                totals[key] += value
        rows_out.insert(0, _public_row("TOTAL_DO_ESCOPO", totals, total_people, "escopo", progress_status))
    return rows_out


def _public_row(unit: str, values: Mapping[str, float], people: int, level: str, progress_status: str) -> dict[str, str]:
    return {
        "nivel_agregacao": level,
        "unidade_sigla": unit,
        "servidores_faixa": count_band(people),
        "planos_entregas_faixa": quantity_band(values.get("planos_entregas")),
        "entregas_faixa": quantity_band(values.get("entregas")),
        "cumprimento_entregas": rounded_percent(values.get("entregas_concluidas", 0), values.get("entregas_com_meta", 0)),
        "planos_trabalho_faixa": quantity_band(values.get("planos_trabalho")),
        "pt_status_cobertura_faixa": quantity_band(values.get("pt_status_elegiveis")),
        "pt_concluidos_percentual": rounded_percent(values.get("pt_concluidos", 0), values.get("pt_status_elegiveis", 0)),
        "atividades_faixa": quantity_band(values.get("atividades")),
        "atividades_concluidas_percentual": rounded_percent(values.get("atividades_concluidas", 0), values.get("atividades", 0)),
        "consolidacoes_faixa": quantity_band(values.get("consolidacoes")),
        "consolidacoes_avaliadas_percentual": rounded_percent(values.get("consol_avaliadas", 0), values.get("consolidacoes", 0)),
        "aguardando_avaliacao_faixa": quantity_band(values.get("aguardando_avaliacao")),
        "transicoes_pe_faixa": quantity_band(values.get("transicoes_pe")),
        "transicoes_pt_faixa": quantity_band(values.get("transicoes_pt")),
        "transicoes_consolidacao_faixa": quantity_band(values.get("transicoes_consolidacao")),
        "transicoes_atividade_faixa": quantity_band(values.get("transicoes_atividade")),
        "eventos_progresso_faixa": quantity_band(values.get("eventos_progresso")),
        "horas_planejadas_faixa": quantity_band(values.get("horas_planejadas")),
        "horas_despendidas_faixa": quantity_band(values.get("horas_despendidas")),
        "observacao_temporal": "estado atual usado apenas para instrumentos encerrados até o corte; eventos filtrados pela data de referência",
        "historico_progresso": progress_status,
    }
