"""Extrações atômicas, somente leitura, para os oracles A3.

As consultas deliberadamente não agregam métricas de negócio. Elas apenas
selecionam os campos mínimos usados pelo cálculo Python independente.
"""
from __future__ import annotations

from typing import Any

from .denodo_config import connect, get_config
from .monthly_runner import query_rows
from .periodos import AnalysisWindow, build_periods_pe, build_periods_pt
from .validation_contracts import ValidationTarget


SQL: dict[str, str] = {
    "pt_modalidade": """
SELECT pt.usuario_id AS id_servidor,
       COALESCE(un.sigla, 'N.I.') AS unidade_sigla,
       COALESCE(NULLIF(TRIM(ins.modalidade_pgd), ''), 'N.I.') AS modalidade
FROM petrvs_icmbio_planos_trabalhos pt
JOIN petrvs_icmbio_usuarios us ON us.id = pt.usuario_id AND us.deleted_at IS NULL
LEFT JOIN (
    SELECT cpf, MIN(NULLIF(TRIM(modalidade_pgd), '')) AS modalidade_pgd
    FROM petrvs_icmbio_integracao_servidores
    WHERE cpf IS NOT NULL GROUP BY cpf
) ins ON ins.cpf = us.cpf
LEFT JOIN petrvs_icmbio_unidades un ON un.id = pt.unidade_id AND un.deleted_at IS NULL
WHERE pt.deleted_at IS NULL
  AND CAST(pt.data_inicio AS DATE) <= CAST('{fim}' AS DATE)
  AND CAST(pt.data_fim AS DATE) >= CAST('{ini}' AS DATE)
""",
    "pe_entregas": """
SELECT pee.id AS id_entrega,
       COALESCE(un.sigla, 'N.I.') AS unidade_sigla,
       pee.progresso_esperado AS meta_planejada,
       COALESCE(pee.progresso_realizado, 0) AS meta_executada,
       pe.status AS plano_status,
       CASE WHEN CAST(pee.data_fim AS DATE) BETWEEN CAST('{ini}' AS DATE)
                 AND CAST('{fim}' AS DATE) THEN 1 ELSE 0 END AS vence_no_periodo
FROM petrvs_icmbio_planos_entregas pe
JOIN petrvs_icmbio_planos_entregas_entregas pee
  ON pee.plano_entrega_id = pe.id AND pee.deleted_at IS NULL
LEFT JOIN petrvs_icmbio_unidades un ON un.id = pe.unidade_id AND un.deleted_at IS NULL
WHERE pe.deleted_at IS NULL
  AND CAST(pe.data_inicio AS DATE) <= CAST('{fim}' AS DATE)
  AND CAST(pe.data_fim AS DATE) >= CAST('{ini}' AS DATE)
""",
    "pt_entregas_executor": """
SELECT pt.id AS plano_trabalho_id,
       pt.usuario_id AS id_servidor,
       pte.plano_entrega_entrega_id AS id_entrega,
       COALESCE(executor.sigla, 'N.I.') AS unidade_sigla,
       COALESCE(dono.sigla, 'N.I.') AS unidade_dona_sigla,
       COALESCE(executor.sigla, 'N.I.') AS unidade_executora_sigla,
       pt.carga_horaria,
       pt.forma_contagem_carga_horaria,
       CAST(pt.data_inicio AS DATE) AS plano_inicio,
       CAST(pt.data_fim AS DATE) AS plano_fim,
       pte.forca_trabalho,
       CAST(CASE WHEN CAST(pt.data_inicio AS DATE) > CAST('{ini}' AS DATE)
                 THEN pt.data_inicio ELSE CAST('{ini}' AS DATE) END AS DATE) AS sobreposicao_inicio,
       CAST(CASE WHEN CAST(pt.data_fim AS DATE) < CAST('{fim}' AS DATE)
                 THEN pt.data_fim ELSE CAST('{fim}' AS DATE) END AS DATE) AS sobreposicao_fim
FROM petrvs_icmbio_planos_trabalhos pt
JOIN petrvs_icmbio_planos_trabalhos_entregas pte
  ON pte.plano_trabalho_id = pt.id AND pte.deleted_at IS NULL
LEFT JOIN petrvs_icmbio_planos_entregas_entregas pee
  ON pee.id = pte.plano_entrega_entrega_id AND pee.deleted_at IS NULL
LEFT JOIN petrvs_icmbio_planos_entregas pe
  ON pe.id = pee.plano_entrega_id AND pe.deleted_at IS NULL
LEFT JOIN petrvs_icmbio_unidades dono ON dono.id = pe.unidade_id AND dono.deleted_at IS NULL
LEFT JOIN petrvs_icmbio_unidades executor ON executor.id = pt.unidade_id AND executor.deleted_at IS NULL
WHERE pt.deleted_at IS NULL
  AND pte.plano_entrega_entrega_id IS NOT NULL
  AND CAST(pt.data_inicio AS DATE) <= CAST('{fim}' AS DATE)
  AND CAST(pt.data_fim AS DATE) >= CAST('{ini}' AS DATE)
""",
    "pt_capacidade_unidade": """
SELECT pt.id AS plano_trabalho_id,
       COALESCE(un.sigla, 'N.I.') AS unidade_sigla,
       pt.carga_horaria,
       pt.forma_contagem_carga_horaria,
       CAST(pt.data_inicio AS DATE) AS plano_inicio,
       CAST(pt.data_fim AS DATE) AS plano_fim,
       CAST(CASE WHEN CAST(pt.data_inicio AS DATE) > CAST('{ini}' AS DATE)
                 THEN pt.data_inicio ELSE CAST('{ini}' AS DATE) END AS DATE) AS sobreposicao_inicio,
       CAST(CASE WHEN CAST(pt.data_fim AS DATE) < CAST('{fim}' AS DATE)
                 THEN pt.data_fim ELSE CAST('{fim}' AS DATE) END AS DATE) AS sobreposicao_fim
FROM petrvs_icmbio_planos_trabalhos pt
LEFT JOIN petrvs_icmbio_unidades un ON un.id = pt.unidade_id AND un.deleted_at IS NULL
WHERE pt.deleted_at IS NULL
  AND pt.carga_horaria IS NOT NULL
  AND pt.carga_horaria > 0
  AND CAST(pt.data_inicio AS DATE) <= CAST('{fim}' AS DATE)
  AND CAST(pt.data_fim AS DATE) >= CAST('{ini}' AS DATE)
""",
    "avaliacoes_pt": """
SELECT av.id AS id_avaliacao,
       COALESCE(un.sigla, 'N.I.') AS unidade_sigla,
       pt.usuario_id AS id_servidor,
       pt.id AS plano_trabalho_id,
       tan.sequencia AS sequencia_nota
FROM petrvs_icmbio_avaliacoes av
JOIN petrvs_icmbio_planos_trabalhos_consolidacoes ptc
  ON ptc.id = av.plano_trabalho_consolidacao_id AND ptc.deleted_at IS NULL
JOIN petrvs_icmbio_planos_trabalhos pt
  ON pt.id = ptc.plano_trabalho_id AND pt.deleted_at IS NULL
JOIN petrvs_icmbio_tipos_avaliacoes_notas tan ON tan.id = av.tipo_avaliacao_nota_id
LEFT JOIN petrvs_icmbio_unidades un ON un.id = pt.unidade_id AND un.deleted_at IS NULL
WHERE av.deleted_at IS NULL
  AND CAST(av.data_avaliacao AS DATE) BETWEEN CAST('{ini}' AS DATE) AND CAST('{fim}' AS DATE)
  AND CAST(pt.data_inicio AS DATE) <= CAST('{fim}' AS DATE)
  AND CAST(pt.data_fim AS DATE) >= CAST('{ini}' AS DATE)
""",
    "avaliacoes_pe": """
SELECT av.id AS id_avaliacao,
       COALESCE(un.sigla, 'N.I.') AS unidade_sigla,
       tan.sequencia AS sequencia_nota
FROM petrvs_icmbio_avaliacoes av
JOIN petrvs_icmbio_planos_entregas pe
  ON pe.id = av.plano_entrega_id AND pe.deleted_at IS NULL
JOIN petrvs_icmbio_tipos_avaliacoes_notas tan ON tan.id = av.tipo_avaliacao_nota_id
LEFT JOIN petrvs_icmbio_unidades un ON un.id = pe.unidade_id AND un.deleted_at IS NULL
WHERE av.deleted_at IS NULL
  AND CAST(av.data_avaliacao AS DATE) BETWEEN CAST('{ini}' AS DATE) AND CAST('{fim}' AS DATE)
  AND CAST(pe.data_inicio AS DATE) <= CAST('{fim}' AS DATE)
  AND CAST(pe.data_fim AS DATE) >= CAST('{ini}' AS DATE)
""",
    "pt_status_planos": """
SELECT pt.id AS plano_trabalho_id,
       un.sigla AS unidade_sigla,
       pt.status AS status_codigo,
       pt.updated_at AS plano_updated_at
FROM petrvs_icmbio_planos_trabalhos pt
-- D17/F5: mesmo universo do A1 — plano de unidade ou servidor ativos.
JOIN petrvs_icmbio_unidades un ON un.id = pt.unidade_id AND un.deleted_at IS NULL
JOIN petrvs_icmbio_usuarios us ON us.id = pt.usuario_id AND us.deleted_at IS NULL
WHERE pt.deleted_at IS NULL
""",
    "pt_status_consolidacoes": """
SELECT c.id AS consolidacao_id,
       c.plano_trabalho_id,
       c.status AS consolidacao_status,
       c.data_inicio AS consolidacao_inicio,
       c.data_fim AS consolidacao_fim
FROM petrvs_icmbio_planos_trabalhos_consolidacoes c
WHERE c.deleted_at IS NULL
""",
    "pt_status_transicoes": """
SELECT sj.plano_trabalho_id,
       sj.codigo AS status_codigo_transicao,
       sj.created_at AS status_created_at
FROM petrvs_icmbio_status_justificativas sj
WHERE sj.deleted_at IS NULL
  AND sj.plano_trabalho_id IS NOT NULL
""",
}

SQL["pt_entregas_dono"] = SQL["pt_entregas_executor"].replace(
    "COALESCE(executor.sigla, 'N.I.') AS unidade_sigla",
    "COALESCE(dono.sigla, 'N.I.') AS unidade_sigla",
).replace(
    "AND CAST(pt.data_fim AS DATE) >= CAST('{ini}' AS DATE)",
    "AND CAST(pt.data_fim AS DATE) >= CAST('{ini}' AS DATE)\n"
    "  AND CAST(pe.data_inicio AS DATE) <= CAST('{fim}' AS DATE)\n"
    "  AND CAST(pe.data_fim AS DATE) >= CAST('{ini}' AS DATE)",
)

SQL.update({
    "g02_entregas": """
SELECT pee.id AS id_entrega, COALESCE(un.sigla, 'N.I.') AS unidade_dona_sigla,
       COALESCE(NULLIF(TRIM(pee.descricao), ''), NULLIF(TRIM(pee.descricao_entrega), ''), 'N.I.') AS nome_entrega,
       CAST(pee.data_inicio AS DATE) AS entrega_inicio, CAST(pee.data_fim AS DATE) AS entrega_fim,
       pee.progresso_esperado AS meta_planejada
FROM petrvs_icmbio_planos_entregas pe
JOIN petrvs_icmbio_planos_entregas_entregas pee ON pee.plano_entrega_id = pe.id AND pee.deleted_at IS NULL
JOIN petrvs_icmbio_unidades un ON un.id = pe.unidade_id AND un.deleted_at IS NULL
WHERE pe.deleted_at IS NULL AND CAST(pe.data_inicio AS DATE) <= CAST('{fim}' AS DATE)
  AND CAST(pe.data_fim AS DATE) >= CAST('{ini}' AS DATE)
""",
    "g02_progressos": """
SELECT pr.id AS progresso_id, pr.plano_entrega_entrega_id AS id_entrega,
       CAST(pr.data_progresso AS DATE) AS data_progresso, pr.meta, pr.realizado,
       pr.progresso_esperado, pr.progresso_realizado, pr.registro_execucao
FROM petrvs_icmbio_planos_entregas_entregas_progressos pr
JOIN petrvs_icmbio_planos_entregas_entregas pee ON pee.id = pr.plano_entrega_entrega_id AND pee.deleted_at IS NULL
JOIN petrvs_icmbio_planos_entregas pe ON pe.id = pee.plano_entrega_id AND pe.deleted_at IS NULL
JOIN petrvs_icmbio_unidades un ON un.id = pe.unidade_id AND un.deleted_at IS NULL
WHERE pr.deleted_at IS NULL AND CAST(pr.data_progresso AS DATE) BETWEEN CAST('{ini}' AS DATE) AND CAST('{fim}' AS DATE)
""",
    "g02_planos": """
SELECT pt.id AS plano_trabalho_id, pt.usuario_id AS id_servidor,
       CAST(pt.data_inicio AS DATE) AS plano_inicio, CAST(pt.data_fim AS DATE) AS plano_fim,
       COALESCE(un.sigla, 'N.I.') AS unidade_executora_sigla
FROM petrvs_icmbio_planos_trabalhos pt
JOIN petrvs_icmbio_unidades un ON un.id = pt.unidade_id AND un.deleted_at IS NULL
WHERE pt.deleted_at IS NULL AND CAST(pt.data_inicio AS DATE) <= CAST('{observacao}' AS DATE)
  AND CAST(pt.data_fim AS DATE) >= CAST('{ini}' AS DATE)
""",
    "g02_vinculos": """
SELECT pte.id AS vinculo_id, pte.plano_trabalho_id,
       pte.plano_entrega_entrega_id AS id_entrega, pte.forca_trabalho
FROM petrvs_icmbio_planos_trabalhos_entregas pte
JOIN petrvs_icmbio_planos_trabalhos pt ON pt.id = pte.plano_trabalho_id AND pt.deleted_at IS NULL
JOIN petrvs_icmbio_unidades exec ON exec.id = pt.unidade_id AND exec.deleted_at IS NULL
LEFT JOIN petrvs_icmbio_planos_entregas_entregas pee ON pee.id = pte.plano_entrega_entrega_id AND pee.deleted_at IS NULL
LEFT JOIN petrvs_icmbio_planos_entregas pe ON pe.id = pee.plano_entrega_id AND pe.deleted_at IS NULL
LEFT JOIN petrvs_icmbio_unidades dona ON dona.id = pe.unidade_id AND dona.deleted_at IS NULL
WHERE pte.deleted_at IS NULL AND CAST(pt.data_inicio AS DATE) <= CAST('{observacao}' AS DATE)
  AND CAST(pt.data_fim AS DATE) >= CAST('{ini}' AS DATE)
""",
    "g02_atividades": """
SELECT a.id AS atividade_id, a.plano_trabalho_id, a.status,
       CAST(a.data_inicio AS DATE) AS data_inicio, CAST(a.data_entrega AS DATE) AS data_entrega,
       a.tempo_planejado, a.tempo_despendido
FROM petrvs_icmbio_atividades a
JOIN petrvs_icmbio_planos_trabalhos pt ON pt.id = a.plano_trabalho_id AND pt.deleted_at IS NULL
JOIN petrvs_icmbio_unidades exec ON exec.id = pt.unidade_id AND exec.deleted_at IS NULL
WHERE a.deleted_at IS NULL AND CAST(pt.data_inicio AS DATE) <= CAST('{observacao}' AS DATE)
  AND CAST(pt.data_fim AS DATE) >= CAST('{ini}' AS DATE)
""",
})


def _records(columns: list[str], rows: list[list[Any]]) -> list[dict[str, Any]]:
    return [dict(zip(columns, row)) for row in rows]


def _periods(target: ValidationTarget, window: AnalysisWindow):
    if target.family == "gestao":
        return [("operacional", "operacional", window.inicio, window.fim, window.fim, "fotografia")]
    return build_periods_pt(window.fim) if target.temporal_lenses == ("pt",) else build_periods_pe(window.fim)


def extract_atomic(target: ValidationTarget, window: AnalysisWindow, units: set[str] | None = None) -> list[dict[str, Any]]:
    """Executa apenas SELECTs atômicos registrados para um alvo."""

    conn = connect(get_config(require_credentials=True))
    records: list[dict[str, Any]] = []
    try:
        if target.code == "G02":
            quoted = ", ".join("'" + unit.replace("'", "''") + "'" for unit in sorted(units or []))
            owner_exists = f""" OR EXISTS (SELECT 1 FROM petrvs_icmbio_planos_trabalhos_entregas sx JOIN petrvs_icmbio_planos_trabalhos sp ON sp.id = sx.plano_trabalho_id AND sp.deleted_at IS NULL JOIN petrvs_icmbio_unidades su ON su.id = sp.unidade_id AND su.deleted_at IS NULL WHERE sx.deleted_at IS NULL AND sx.plano_entrega_entrega_id = pee.id AND UPPER(su.sigla) IN ({quoted}))"""
            plan_exists = f""" OR EXISTS (SELECT 1 FROM petrvs_icmbio_planos_trabalhos_entregas sx JOIN petrvs_icmbio_planos_entregas_entregas se ON se.id = sx.plano_entrega_entrega_id AND se.deleted_at IS NULL JOIN petrvs_icmbio_planos_entregas sp ON sp.id = se.plano_entrega_id AND sp.deleted_at IS NULL JOIN petrvs_icmbio_unidades su ON su.id = sp.unidade_id AND su.deleted_at IS NULL WHERE sx.deleted_at IS NULL AND sx.plano_trabalho_id = pt.id AND UPPER(su.sigla) IN ({quoted}))"""
            for extractor in target.atomic_extractors:
                sql = SQL[extractor].replace("{ini}", str(window.inicio)).replace("{fim}", str(window.fim)).replace("{observacao}", str(window.data_execucao))
                if units:
                    if extractor in {"g02_entregas", "g02_progressos"}:
                        sql += f"\nAND (UPPER(un.sigla) IN ({quoted}){owner_exists})"
                    elif extractor == "g02_planos":
                        sql += f"\nAND (UPPER(un.sigla) IN ({quoted}){plan_exists})"
                    elif extractor == "g02_vinculos":
                        sql += f"\nAND (UPPER(exec.sigla) IN ({quoted}) OR UPPER(dona.sigla) IN ({quoted}))"
                    elif extractor == "g02_atividades":
                        sql += f"\nAND (UPPER(exec.sigla) IN ({quoted}){plan_exists})"
                columns, rows = query_rows(conn, sql)
                for record in _records(columns, rows):
                    record["_extractor"] = extractor
                    record["_history_cutoff"] = window.fim.isoformat()
                    record["_observation_date"] = window.data_execucao.isoformat()
                    records.append(record)
            return records
        for label, _kind, start, _scheduled, end, _status in _periods(target, window):
            for extractor in target.atomic_extractors:
                template = SQL[extractor]
                if units:
                    quoted = ", ".join("'" + unit.replace("'", "''") + "'" for unit in sorted(units))
                    if extractor in {"pt_modalidade", "pe_entregas", "pt_capacidade_unidade", "avaliacoes_pt", "avaliacoes_pe", "pt_status_planos"}:
                        template += f"\nAND UPPER(un.sigla) IN ({quoted})"
                    elif extractor == "pt_entregas_executor":
                        template += f"\nAND UPPER(executor.sigla) IN ({quoted})"
                    elif extractor == "pt_entregas_dono":
                        condition = f"UPPER(dono.sigla) IN ({quoted})"
                        if target.code == "I08":
                            condition += f" OR UPPER(executor.sigla) IN ({quoted})"
                        template += f"\nAND ({condition})"
                    elif extractor == "pt_status_consolidacoes":
                        template += f"\nAND c.plano_trabalho_id IN (SELECT pt.id FROM petrvs_icmbio_planos_trabalhos pt JOIN petrvs_icmbio_unidades un ON un.id = pt.unidade_id AND un.deleted_at IS NULL WHERE pt.deleted_at IS NULL AND UPPER(un.sigla) IN ({quoted}))"
                    elif extractor == "pt_status_transicoes":
                        template += f"\nAND sj.plano_trabalho_id IN (SELECT pt.id FROM petrvs_icmbio_planos_trabalhos pt JOIN petrvs_icmbio_unidades un ON un.id = pt.unidade_id AND un.deleted_at IS NULL WHERE pt.deleted_at IS NULL AND UPPER(un.sigla) IN ({quoted}))"
                columns, rows = query_rows(
                    conn, template.replace("{ini}", str(start)).replace("{fim}", str(end))
                )
                for record in _records(columns, rows):
                    record["periodo"] = label
                    record["_extractor"] = extractor
                    if target.code == "I12":
                        record["instrumento"] = "PT" if extractor == "avaliacoes_pt" else "PE"
                    records.append(record)
    finally:
        conn.close()
    return records
