"""Análise detalhada, local e anonimizada dos registros textuais de PE e PT."""
from __future__ import annotations

from typing import Mapping

from lib.monthly_runner import query_rows
from lib.periodos import AnalysisWindow
from relatorios.escopo import ScopeSpec, UnitProfile, unit_matches
from relatorios.textos_execucao import TextSanitizer, priority_assessment


SQL_NAMES = """
SELECT nome FROM petrvs_icmbio_usuarios
WHERE deleted_at IS NULL AND nome IS NOT NULL
"""

SQL_PE_TEXT = """
SELECT ud.sigla AS unidade_dona_sigla,
       ue.sigla AS unidade_executora_sigla,
       pe.numero AS plano_numero,
       pe.status AS status,
       CAST(e.data_inicio AS DATE) AS data_inicio,
       CAST(e.data_fim AS DATE) AS data_fim,
       COALESCE(NULLIF(TRIM(e.descricao), ''), NULLIF(TRIM(e.descricao_entrega), '')) AS texto_principal,
       e.descricao_meta AS texto_meta,
       e.destinatario AS texto_destinatario,
       e.progresso_esperado,
       e.progresso_realizado
FROM petrvs_icmbio_planos_entregas_entregas e
JOIN petrvs_icmbio_planos_entregas pe ON pe.id = e.plano_entrega_id AND pe.deleted_at IS NULL
JOIN petrvs_icmbio_unidades ud ON ud.id = pe.unidade_id AND ud.deleted_at IS NULL
LEFT JOIN petrvs_icmbio_unidades ue ON ue.id = e.unidade_id AND ue.deleted_at IS NULL
WHERE e.deleted_at IS NULL
  AND CAST(e.data_inicio AS DATE) <= CAST('{fim}' AS DATE)
  AND CAST(e.data_fim AS DATE) >= CAST('{inicio}' AS DATE)
  {scope_filter}
"""

SQL_PT_TEXT = """
SELECT ud.sigla AS unidade_dona_sigla,
       ux.sigla AS unidade_executora_sigla,
       pt.numero AS plano_numero,
       pt.status AS status,
       CAST(pt.data_inicio AS DATE) AS data_inicio,
       CAST(pt.data_fim AS DATE) AS data_fim,
       pte.descricao AS texto_principal,
       '' AS texto_meta,
       pte.orgao AS texto_destinatario,
       NULL AS progresso_esperado,
       NULL AS progresso_realizado
FROM petrvs_icmbio_planos_trabalhos_entregas pte
JOIN petrvs_icmbio_planos_trabalhos pt ON pt.id = pte.plano_trabalho_id AND pt.deleted_at IS NULL
JOIN petrvs_icmbio_unidades ux ON ux.id = pt.unidade_id AND ux.deleted_at IS NULL
LEFT JOIN petrvs_icmbio_planos_entregas_entregas e
       ON e.id = pte.plano_entrega_entrega_id AND e.deleted_at IS NULL
LEFT JOIN petrvs_icmbio_planos_entregas pe ON pe.id = e.plano_entrega_id AND pe.deleted_at IS NULL
LEFT JOIN petrvs_icmbio_unidades ud ON ud.id = pe.unidade_id AND ud.deleted_at IS NULL
WHERE pte.deleted_at IS NULL
  AND CAST(pt.data_inicio AS DATE) <= CAST('{fim}' AS DATE)
  AND CAST(pt.data_fim AS DATE) >= CAST('{inicio}' AS DATE)
  {scope_filter}
"""

SQL_ACTIVITY_TEXT = """
SELECT '' AS unidade_dona_sigla,
       ux.sigla AS unidade_executora_sigla,
       pt.numero AS plano_numero,
       a.status AS status,
       CAST(COALESCE(a.data_inicio, a.data_distribuicao) AS DATE) AS data_inicio,
       CAST(a.data_estipulada_entrega AS DATE) AS data_fim,
       a.descricao AS texto_principal,
       '' AS texto_meta,
       '' AS texto_destinatario,
       100 AS progresso_esperado,
       a.progresso AS progresso_realizado,
       a.tempo_planejado,
       a.tempo_despendido
FROM petrvs_icmbio_atividades a
JOIN petrvs_icmbio_planos_trabalhos pt ON pt.id = a.plano_trabalho_id AND pt.deleted_at IS NULL
JOIN petrvs_icmbio_unidades ux ON ux.id = pt.unidade_id AND ux.deleted_at IS NULL
WHERE a.deleted_at IS NULL
  AND CAST(a.data_distribuicao AS DATE) <= CAST('{fim}' AS DATE)
  AND (a.data_entrega IS NULL OR CAST(a.data_entrega AS DATE) >= CAST('{inicio}' AS DATE))
  {scope_filter}
"""


def _query_dicts(conn, sql: str) -> list[dict[str, str]]:
    columns, rows = query_rows(conn, sql)
    return [dict(zip(columns, row)) for row in rows]


def _matches_scope(
    row: Mapping[str, object], scope: ScopeSpec, profiles: Mapping[str, UnitProfile]
) -> bool:
    if scope.kind == "nacional":
        return True
    for key in ("unidade_dona_sigla", "unidade_executora_sigla"):
        sigla = str(row.get(key) or "").strip()
        if sigla and unit_matches({"unidade_sigla": sigla}, scope, profiles):
            return True
    return False


def _scope_sql(scope: ScopeSpec, kind: str) -> str:
    """Reduz o volume no Denodo; a validação definitiva ainda ocorre em memória."""

    if scope.kind == "nacional":
        return ""
    units = set(scope.units)
    if scope.kind == "unidade":
        units.add(scope.value)
    if not units:
        return ""
    literals = ", ".join("'" + unit.replace("'", "''") + "'" for unit in sorted(units))
    if kind == "PE":
        return f"AND (UPPER(ud.sigla) IN ({literals}) OR UPPER(ue.sigla) IN ({literals}))"
    if kind == "PT":
        return f"AND (UPPER(ud.sigla) IN ({literals}) OR UPPER(ux.sigla) IN ({literals}))"
    return f"AND UPPER(ux.sigla) IN ({literals})"


def extract_textual_evidence(
    conn,
    window: AnalysisWindow,
    scope: ScopeSpec,
    profiles: Mapping[str, UnitProfile],
    *,
    lens: str = "acumulada",
    sanitizer: TextSanitizer | None = None,
) -> list[dict[str, object]]:
    """Retorna somente textos sanitizados e campos de negócio, nunca UUIDs ou pessoas."""

    if lens not in {"acumulada", "operacional"}:
        raise ValueError("lens deve ser acumulada ou operacional")
    if sanitizer is None:
        names = [row[0] for _, rows in [query_rows(conn, SQL_NAMES)] for row in rows if row]
        sanitizer = TextSanitizer(names)
    end = window.fim if lens == "acumulada" else window.data_execucao
    sources = (
        ("PE", SQL_PE_TEXT),
        ("PT", SQL_PT_TEXT),
        ("ATIVIDADE", SQL_ACTIVITY_TEXT),
    )
    evidence: list[dict[str, object]] = []
    for kind, template in sources:
        sql = template.format(
            inicio=window.inicio.isoformat(), fim=end.isoformat(),
            scope_filter=_scope_sql(scope, kind),
        )
        for row in _query_dicts(conn, sql):
            if not _matches_scope(row, scope, profiles):
                continue
            sanitized = {
                key: sanitizer.sanitize(row.get(key)).text
                for key in ("texto_principal", "texto_meta", "texto_destinatario")
            }
            redactions = sorted({
                item
                for key in ("texto_principal", "texto_meta", "texto_destinatario")
                for item in sanitizer.sanitize(row.get(key)).redactions
            })
            public = {
                "lente": lens,
                "tipo_registro": kind,
                "unidade_dona_sigla": row.get("unidade_dona_sigla", ""),
                "unidade_executora_sigla": row.get("unidade_executora_sigla", ""),
                "plano_numero": row.get("plano_numero", ""),
                "status": row.get("status", ""),
                "data_inicio": row.get("data_inicio", ""),
                "data_fim": row.get("data_fim", ""),
                **sanitized,
                "progresso_esperado": row.get("progresso_esperado", ""),
                "progresso_realizado": row.get("progresso_realizado", ""),
                "tempo_planejado": row.get("tempo_planejado", ""),
                "tempo_despendido": row.get("tempo_despendido", ""),
                "redacoes_aplicadas": ",".join(redactions),
            }
            public.update(priority_assessment(public, end))
            evidence.append(public)
    return sorted(
        evidence,
        key=lambda row: (-int(row["pontuacao_prioridade"]), str(row["unidade_dona_sigla"]), str(row["plano_numero"])),
    )
