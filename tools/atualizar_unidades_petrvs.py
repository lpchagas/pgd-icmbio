"""Atualiza o retrato local da hierarquia de unidades do PETRVS (L7).

Consulta somente leitura à view ``petrvs_icmbio_unidades`` (registros ativos; só
dados organizacionais: id, código, sigla, nome e unidade-mãe) e grava
``artefatos_local/ocde/diagnosticos/PETRVS_unidades.csv`` (privado, fora do Git).
Um retrato novo muda o hash da hierarquia e, portanto, o escopo resolvido dos
pilotos: aceites anteriores não são herdados em silêncio.

Uso: python -m tools.atualizar_unidades_petrvs [--dry-run]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

from lib.csv_utils import write_pipe_csv
from lib.unidades_petrvs import COLUNAS, DEFAULT_UNIDADES_PETRVS_CSV, carregar_hierarquia

SQL = (
    "SELECT id, codigo, sigla, nome, unidade_pai_id FROM petrvs_icmbio_unidades "
    "WHERE deleted_at IS NULL ORDER BY sigla, id"
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="Mostra a consulta e o destino sem conectar.")
    args = parser.parse_args(argv)
    destino: Path = DEFAULT_UNIDADES_PETRVS_CSV
    if args.dry_run:
        print(json.dumps({"consulta": SQL, "destino": str(destino)}, ensure_ascii=False, indent=2))
        return 0

    from lib.denodo_config import connect, get_config
    from lib.monthly_runner import query_rows

    conn = connect(get_config())
    try:
        colunas, linhas = query_rows(conn, SQL)
    finally:
        conn.close()
    if tuple(colunas) != COLUNAS or not linhas:
        raise RuntimeError("Consulta de unidades devolveu colunas inesperadas ou nenhuma linha.")
    temporario = destino.with_suffix(".csv.tmp")
    write_pipe_csv(temporario, list(colunas), linhas)
    os.replace(temporario, destino)
    hierarquia = carregar_hierarquia(destino)
    print(json.dumps({"arquivo": destino.name, "unidades": len(hierarquia.unidades),
                      "sha256": hierarquia.sha256}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
