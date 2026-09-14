"""G02 — Execução das Entregas (PE histórico + fotografia operacional dos PT)."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from gestao.execucao_entregas import (  # noqa: E402
    HISTORY_COLUMNS, MAIN_COLUMNS, NOMINAL_COLUMNS, build_g02, shared_rows,
)
from lib.csv_utils import clean, write_pipe_csv  # noqa: E402
from lib.denodo_config import connect, get_config  # noqa: E402
from lib.monthly_runner import query_rows  # noqa: E402
from lib.periodos import ANALYSIS_TIMEZONE, build_periods_pe, configure_execution_context  # noqa: E402
from lib.validation_contracts import gest_artifact  # noqa: E402
from ocde.relatorios.textos_execucao import TextSanitizer  # noqa: E402


SQL_DELIVERIES = """
SELECT pee.id AS id_entrega, pe.id AS plano_entrega_id,
       COALESCE(un.sigla, 'N.I.') AS unidade_dona_sigla,
       COALESCE(NULLIF(TRIM(pee.descricao), ''), NULLIF(TRIM(pee.descricao_entrega), ''), 'N.I.') AS nome_entrega,
       CAST(pee.data_inicio AS DATE) AS entrega_inicio, CAST(pee.data_fim AS DATE) AS entrega_fim,
       pee.progresso_esperado AS meta_planejada
FROM petrvs_icmbio_planos_entregas pe
JOIN petrvs_icmbio_planos_entregas_entregas pee
  ON pee.plano_entrega_id = pe.id AND pee.deleted_at IS NULL
JOIN petrvs_icmbio_unidades un ON un.id = pe.unidade_id AND un.deleted_at IS NULL
WHERE pe.deleted_at IS NULL
  AND CAST(pe.data_inicio AS DATE) <= CAST('{fim_historico}' AS DATE)
  AND CAST(pe.data_fim AS DATE) >= CAST('{inicio}' AS DATE)
  {filtro_dona}
"""

SQL_PROGRESS = """
SELECT pr.id AS progresso_id, pr.plano_entrega_entrega_id AS id_entrega,
       CAST(pr.data_progresso AS DATE) AS data_progresso,
       pr.meta, pr.realizado, pr.progresso_esperado, pr.progresso_realizado,
       pr.registro_execucao
FROM petrvs_icmbio_planos_entregas_entregas_progressos pr
JOIN petrvs_icmbio_planos_entregas_entregas pee
  ON pee.id = pr.plano_entrega_entrega_id AND pee.deleted_at IS NULL
JOIN petrvs_icmbio_planos_entregas pe
  ON pe.id = pee.plano_entrega_id AND pe.deleted_at IS NULL
JOIN petrvs_icmbio_unidades un ON un.id = pe.unidade_id AND un.deleted_at IS NULL
WHERE pr.deleted_at IS NULL
  AND CAST(pr.data_progresso AS DATE) BETWEEN CAST('{inicio}' AS DATE) AND CAST('{fim_historico}' AS DATE)
  {filtro_dona}
"""

SQL_PLANS = """
SELECT pt.id AS plano_trabalho_id, pt.usuario_id AS id_servidor,
       {nome_servidor} pt.numero AS plano_numero,
       CAST(pt.data_inicio AS DATE) AS plano_inicio, CAST(pt.data_fim AS DATE) AS plano_fim,
       COALESCE(un.sigla, 'N.I.') AS unidade_executora_sigla
FROM petrvs_icmbio_planos_trabalhos pt
JOIN petrvs_icmbio_unidades un ON un.id = pt.unidade_id AND un.deleted_at IS NULL
{join_usuario}
WHERE pt.deleted_at IS NULL
  AND CAST(pt.data_inicio AS DATE) <= CAST('{data_execucao}' AS DATE)
  AND CAST(pt.data_fim AS DATE) >= CAST('{inicio}' AS DATE)
  {filtro_planos}
"""

SQL_LINKS = """
SELECT pte.id AS vinculo_id, pte.plano_trabalho_id,
       pte.plano_entrega_entrega_id AS id_entrega, pte.forca_trabalho
FROM petrvs_icmbio_planos_trabalhos_entregas pte
JOIN petrvs_icmbio_planos_trabalhos pt
  ON pt.id = pte.plano_trabalho_id AND pt.deleted_at IS NULL
JOIN petrvs_icmbio_unidades un ON un.id = pt.unidade_id AND un.deleted_at IS NULL
LEFT JOIN petrvs_icmbio_planos_entregas_entregas pee
  ON pee.id = pte.plano_entrega_entrega_id AND pee.deleted_at IS NULL
LEFT JOIN petrvs_icmbio_planos_entregas pe
  ON pe.id = pee.plano_entrega_id AND pe.deleted_at IS NULL
LEFT JOIN petrvs_icmbio_unidades dona ON dona.id = pe.unidade_id AND dona.deleted_at IS NULL
WHERE pte.deleted_at IS NULL
  AND CAST(pt.data_inicio AS DATE) <= CAST('{data_execucao}' AS DATE)
  AND CAST(pt.data_fim AS DATE) >= CAST('{inicio}' AS DATE)
  {filtro_ambos}
"""

SQL_ACTIVITIES = """
SELECT a.id AS atividade_id, a.plano_trabalho_id, a.status,
       CAST(a.data_inicio AS DATE) AS data_inicio, CAST(a.data_entrega AS DATE) AS data_entrega,
       a.tempo_planejado, a.tempo_despendido
FROM petrvs_icmbio_atividades a
JOIN petrvs_icmbio_planos_trabalhos pt
  ON pt.id = a.plano_trabalho_id AND pt.deleted_at IS NULL
JOIN petrvs_icmbio_unidades un ON un.id = pt.unidade_id AND un.deleted_at IS NULL
WHERE a.deleted_at IS NULL
  AND CAST(pt.data_inicio AS DATE) <= CAST('{data_execucao}' AS DATE)
  AND CAST(pt.data_fim AS DATE) >= CAST('{inicio}' AS DATE)
  {filtro_planos}
"""


def _quoted(values: list[str]) -> str:
    return ", ".join("'" + value.replace("'", "''").upper() + "'" for value in values)


def _records(connection, sql: str) -> list[dict]:
    columns, rows = query_rows(connection, sql)
    return [{name: clean(value) for name, value in zip(columns, row)} for row in rows]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unidade", action="append", default=[])
    parser.add_argument("--todas", action="store_true")
    parser.add_argument("--data-execucao", required=True)
    parser.add_argument("--produto", choices=("restrito", "compartilhavel"), default="restrito")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    units = sorted({part.strip().upper() for item in args.unidade for part in item.split(",") if part.strip()})
    if not args.todas and not units:
        raise SystemExit("informe --unidade SIGLA ou --todas")
    window = configure_execution_context(args.data_execucao)
    destination = args.out or PROJECT_ROOT / "artefatos_local" / "gestao" / window.mes_execucao
    if args.dry_run:
        print(json.dumps({"codigo": "G02", "data_execucao": str(window.data_execucao), "fim_historico": str(window.fim), "unidades": units or ["TODAS"], "destino": str(destination)}, ensure_ascii=False))
        return 0
    unit_filter = f"AND UPPER(un.sigla) IN ({_quoted(units)})" if units else ""
    unit_list = _quoted(units)
    filter_both = f"AND (UPPER(un.sigla) IN ({unit_list}) OR UPPER(dona.sigla) IN ({unit_list}))" if units else ""
    filter_plans = ""
    if units:
        filter_plans = f"""AND (UPPER(un.sigla) IN ({unit_list}) OR EXISTS (
            SELECT 1 FROM petrvs_icmbio_planos_trabalhos_entregas vx
            JOIN petrvs_icmbio_planos_entregas_entregas ex ON ex.id = vx.plano_entrega_entrega_id AND ex.deleted_at IS NULL
            JOIN petrvs_icmbio_planos_entregas px ON px.id = ex.plano_entrega_id AND px.deleted_at IS NULL
            JOIN petrvs_icmbio_unidades ux ON ux.id = px.unidade_id AND ux.deleted_at IS NULL
            WHERE vx.deleted_at IS NULL AND vx.plano_trabalho_id = pt.id AND UPPER(ux.sigla) IN ({unit_list})
        ))"""
    params = {"inicio": window.inicio, "fim_historico": window.fim, "data_execucao": window.data_execucao, "filtro_dona": "", "filtro_executora": unit_filter, "filtro_ambos": filter_both, "filtro_planos": filter_plans}
    connection = connect(get_config())
    try:
        deliveries = _records(connection, SQL_DELIVERIES.format(**params))
        progress = _records(connection, SQL_PROGRESS.format(**params))
        join_user = "JOIN petrvs_icmbio_usuarios us ON us.id = pt.usuario_id AND us.deleted_at IS NULL" if args.produto == "restrito" else ""
        server_name = "us.nome AS servidor_nome," if args.produto == "restrito" else ""
        plans = _records(connection, SQL_PLANS.format(**params, join_usuario=join_user, nome_servidor=server_name))
        links = _records(connection, SQL_LINKS.format(**params))
        activities = _records(connection, SQL_ACTIVITIES.format(**params))
    finally:
        connection.close()
    sanitizer = TextSanitizer(
        row.get("servidor_nome", "") for row in plans if args.produto == "restrito"
    )
    for delivery in deliveries:
        delivery["nome_entrega"] = sanitizer.sanitize(delivery.get("nome_entrega")).text
    for event in progress:
        event["registro_execucao"] = sanitizer.sanitize(event.get("registro_execucao")).text
    if units:
        linked_ids = {str(row.get("id_entrega")) for row in links if row.get("id_entrega")}
        deliveries = [row for row in deliveries if str(row.get("unidade_dona_sigla", "")).upper() in units or str(row.get("id_entrega")) in linked_ids]
        allowed_delivery_ids = {str(row.get("id_entrega")) for row in deliveries}
        progress = [row for row in progress if str(row.get("id_entrega")) in allowed_delivery_ids]
    main_rows, history, nominal = build_g02(deliveries, progress, plans, links, activities, build_periods_pe(window.fim), history_cutoff=window.fim, observation_date=window.data_execucao)
    if units:
        main_rows = [row for row in main_rows if str(row.get("unidade_sigla", "")).upper() in units]
    eligible_servers = len({str(row.get("id_servidor")) for row in plans if row.get("id_servidor")})
    if args.produto == "compartilhavel":
        main_rows = shared_rows(main_rows, eligible_servers)
        history = []
        nominal = []
    stamp = datetime.now(ZoneInfo(ANALYSIS_TIMEZONE)).strftime("%Y%m%d_%H%M%S")
    scope = "TODAS" if not units else "_".join(units[:3])
    write_pipe_csv(destination / gest_artifact("02", f"2_entregas_{args.produto}_{scope}_{stamp}.csv"), MAIN_COLUMNS, ([row.get(column, "") for column in MAIN_COLUMNS] for row in main_rows))
    if args.produto == "restrito":
        write_pipe_csv(destination / gest_artifact("02", f"2_historico_restrito_{scope}_{stamp}.csv"), HISTORY_COLUMNS, ([row.get(column, "") for column in HISTORY_COLUMNS] for row in history))
        write_pipe_csv(destination / gest_artifact("02", f"2_nominal_restrito_{scope}_{stamp}.csv"), NOMINAL_COLUMNS, ([row.get(column, "") for column in NOMINAL_COLUMNS] for row in nominal))
    print(json.dumps({"codigo": "G02", "entregas": len(main_rows), "historico": len(history), "servidores_elegiveis": eligible_servers, "fotografia": str(window.data_execucao), "corte_historico": str(window.fim)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
