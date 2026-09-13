"""Reusable public runners for monthly CSV generation."""
from __future__ import annotations

import argparse
import calendar
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

from .auditoria import audit_csv
from .csv_utils import clean, indicator_csv_dir, write_pipe_csv
from .denodo_config import connect, get_config
from .docs_sql import adapt_for_jdbc, extract_indicator_sql, set_period
from .periodos import analysis_window, build_periods_pe, build_periods_pt, configure_execution_context, period_metadata


def query_rows(conn, sql: str) -> tuple[list[str], list[list[str]]]:
    stmt = conn.createStatement()
    rs = stmt.executeQuery(sql)
    meta = rs.getMetaData()
    count = meta.getColumnCount()
    columns = [str(meta.getColumnLabel(i + 1)) for i in range(count)]
    rows: list[list[str]] = []
    while rs.next():
        rows.append([clean(rs.getObject(i + 1)) for i in range(count)])
    rs.close()
    stmt.close()
    return columns, rows


def parse_args(description: str) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--dry-run", action="store_true", help="Valida configuracao e mostra destino sem conectar.")
    parser.add_argument("--month", help="Pasta mensal de destino no formato AAAA-MM. Padrao: mes atual.")
    parser.add_argument(
        "--data-execucao",
        help="Data reprodutível da execução (AAAA-MM-DD); define o corte no mês anterior.",
    )
    return parser.parse_args()


def _select_periods(period_type: str, analysis_end: date) -> list[tuple[str, str, date, date, date, str]]:
    """Return the correct period list for the given instrument type (pe or pt)."""
    if period_type == "pt":
        return build_periods_pt(analysis_end)
    return build_periods_pe(analysis_end)


def run_sql_indicator(
    indicator: str,
    doc_path: str,
    output_slug: str,
    period_type: str = "pe",
) -> None:
    """Execute a parametric SQL indicator and write a monthly pipe-delimited CSV.

    Args:
        indicator:   Two-digit indicator number, e.g. "02".
        doc_path:    Relative path to the Markdown doc containing the SQL variable.
        output_slug: Descriptive slug for the output filename.
        period_type: "pe" for Plano de Entregas (quadrimestral from 2026) or
                     "pt" for Plano de Trabalho (monthly from 2026).
                     PE indicators: I02, I03, I04, I07, I08, I12.
                     PT indicators: I05, I06, I09, I10, I11.
    """
    args = parse_args(f"Executa indicador I{indicator} e gera CSV mensal.")
    window = configure_execution_context(args.data_execucao or analysis_window().data_execucao, args.month)
    sql_template = adapt_for_jdbc(extract_indicator_sql(doc_path, indicator))
    out_dir = indicator_csv_dir(args.month)
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    output = out_dir / f"IND_{indicator}.2_{output_slug}_{stamp}.csv"

    periods = _select_periods(period_type, window.fim)

    if args.dry_run:
        get_config(require_credentials=False)
        preview_period = periods[0]
        preview_sql = set_period(sql_template, str(preview_period[2]), str(preview_period[4]))
        print(f"Indicador: I{indicator}")
        print(f"Instrumento: {'PT (mensal 2026)' if period_type == 'pt' else 'PE (quadrimestral 2026)'}")
        print(f"Documento fonte: {doc_path}")
        print(f"Destino: {output}")
        print("Modo dry-run: nenhuma conexao Denodo sera aberta.")
        print("Primeiras linhas da SQL adaptada:")
        print("\n".join(preview_sql.splitlines()[:12]))
        return

    config = get_config(require_credentials=True)
    conn = connect(config)
    all_columns: list[str] | None = None
    all_rows: list[list[str]] = []
    meta_columns = period_metadata()

    try:
        for label, kind, start, scheduled_end, end, status in periods:
            sql = set_period(sql_template, str(start), str(end))
            print(f"Executando I{indicator} {label} ({start} a {end})...")
            columns, rows = query_rows(conn, sql)
            if all_columns is None:
                all_columns = meta_columns + columns
            duration = (end - start).days + 1
            for row in rows:
                all_rows.append([kind, label, str(start), str(scheduled_end), str(end), status, duration] + row)
            print(f"  {len(rows)} linhas retornadas.")
    finally:
        conn.close()

    if not all_rows:
        print("Nenhum dado retornado. CSV nao gerado.")
        return
    write_pipe_csv(output, all_columns or [], all_rows)
    print(f"Arquivo salvo: {output}")
    for message in audit_csv(output):
        print(message)


def parse_date(value: object) -> date | None:
    if value is None:
        return None
    try:
        return date.fromisoformat(str(value).strip()[:10])
    except ValueError:
        return None


def month_periods(first: date, last: date, analysis_end: date):
    current = date(first.year, first.month, 1)
    cutoff = min(last, analysis_end)
    while current <= cutoff:
        end_day = calendar.monthrange(current.year, current.month)[1]
        end = min(date(current.year, current.month, end_day), cutoff)
        yield f"{current.year}-{current.month:02d}", current, end
        month = current.month % 12 + 1
        year = current.year + (1 if current.month == 12 else 0)
        current = date(year, month, 1)


def run_i01(doc_path: str = "docs/ocde/06.1.1-i01.md") -> None:
    args = parse_args("Executa indicador I01 e gera CSVs mensais.")
    window = configure_execution_context(args.data_execucao or analysis_window().data_execucao, args.month)
    sql = adapt_for_jdbc(extract_indicator_sql(doc_path, "01"))
    out_dir = indicator_csv_dir(args.month)
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_total = out_dir / f"IND_01.2_v1_proporcao_mensal_{stamp}.csv"
    output_unit = out_dir / f"IND_01.2_v2_proporcao_unidade_mensal_{stamp}.csv"

    if args.dry_run:
        get_config(require_credentials=False)
        print("Indicador: I01")
        print("Instrumento: PT (mensal — agregacao inferida das datas dos planos)")
        print(f"Documento fonte: {doc_path}")
        print(f"Destinos: {output_total} | {output_unit}")
        print("Modo dry-run: nenhuma conexao Denodo sera aberta.")
        print("Primeiras linhas da SQL adaptada:")
        print("\n".join(sql.splitlines()[:12]))
        return

    config = get_config(require_credentials=True)
    conn = connect(config)
    try:
        columns, rows = query_rows(conn, sql)
    finally:
        conn.close()

    positions = {name: idx for idx, name in enumerate(columns)}
    plans = []
    for row in rows:
        start = parse_date(row[positions["plano_inicio"]])
        end = parse_date(row[positions["plano_fim"]])
        if not start or not end:
            continue
        plans.append(
            {
                "usuario_id": row[positions["usuario_id"]],
                "unidade_sigla": clean(row[positions["unidade_sigla"]], "N.I."),
                "unidade_nome": clean(row[positions["unidade_nome"]], "N.I."),
                "modalidade": clean(row[positions["modalidade"]], "N.I."),
                "inicio": start,
                "fim": end,
            }
        )

    if not plans:
        print("Nenhum plano retornado. CSV nao gerado.")
        return

    first = min(plan["inicio"] for plan in plans)
    last = min(max(plan["fim"] for plan in plans), window.fim)
    total_rows = []
    unit_rows = []

    for label, start, end in month_periods(first, last, window.fim):
        active = [plan for plan in plans if plan["inicio"] <= end and plan["fim"] >= start]
        by_mode: dict[str, set[str]] = defaultdict(set)
        by_unit_mode: dict[tuple[str, str, str], set[str]] = defaultdict(set)
        by_unit_total: dict[tuple[str, str], set[str]] = defaultdict(set)
        for plan in active:
            user = str(plan["usuario_id"])
            mode = str(plan["modalidade"])
            unit = (str(plan["unidade_sigla"]), str(plan["unidade_nome"]))
            by_mode[mode].add(user)
            by_unit_mode[(unit[0], unit[1], mode)].add(user)
            by_unit_total[unit].add(user)

        total_users = len(set().union(*by_mode.values())) if by_mode else 0
        for mode, users in sorted(by_mode.items()):
            percent = round(len(users) * 100.0 / total_users, 2) if total_users else 0
            total_rows.append([label, start, end, mode, len(users), percent])

        for (sigla, nome, mode), users in sorted(by_unit_mode.items()):
            denominator = len(by_unit_total[(sigla, nome)])
            percent = round(len(users) * 100.0 / denominator, 2) if denominator else 0
            unit_rows.append([label, start, end, sigla, nome, mode, len(users), percent])

    write_pipe_csv(
        output_total,
        ["periodo", "periodo_inicio", "periodo_fim", "modalidade", "total_servidores", "percentual"],
        total_rows,
    )
    write_pipe_csv(
        output_unit,
        [
            "periodo",
            "periodo_inicio",
            "periodo_fim",
            "unidade_sigla",
            "unidade_nome",
            "modalidade",
            "total_servidores",
            "percentual_unidade",
        ],
        unit_rows,
    )
    print(f"Arquivo salvo: {output_total}")
    print(f"Arquivo salvo: {output_unit}")
    for output in (output_total, output_unit):
        print(output.name)
        for message in audit_csv(output):
            print(f"  {message}")
