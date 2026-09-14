"""Template publico sanitizado para diagnosticos de validacao.

Copie este arquivo para artefatos_local/ocde/diagnosticos/AAAA-MM/
antes de preencher consultas diagnosticas especificas. Credenciais devem vir
somente do .env local.
"""
from pathlib import Path
import sys

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "lib" / "__init__.py").exists())
sys.path.insert(0, str(ROOT))

from lib.csv_utils import diagnostic_csv_dir, write_pipe_csv
from lib.denodo_config import connect, get_config


QUERIES = [
    # ("q1", "contagem_base", "SELECT ..."),
]


def run_query(conn, sql):
    stmt = conn.createStatement()
    rs = stmt.executeQuery(sql)
    meta = rs.getMetaData()
    count = meta.getColumnCount()
    columns = [str(meta.getColumnLabel(i + 1)) for i in range(count)]
    rows = []
    while rs.next():
        rows.append([rs.getObject(i + 1) for i in range(count)])
    rs.close()
    stmt.close()
    return columns, rows


def main():
    if not QUERIES:
        raise RuntimeError("Preencha QUERIES antes de executar o diagnostico.")
    conn = connect(get_config(require_credentials=True))
    try:
        for number, slug, sql in QUERIES:
            columns, rows = run_query(conn, sql)
            output = diagnostic_csv_dir() / f"IND_OCDE_XX.4_{number}_{slug}.csv"
            write_pipe_csv(output, columns, rows)
            print(f"Arquivo salvo: {output}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
