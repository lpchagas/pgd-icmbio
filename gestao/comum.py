"""Helpers compartilhados pelas extrações de gestão contra o Denodo.

Extraídos de gestao/PT_STATUS.1_run.py quando REG_EXEC passou a precisar da
mesma expansão hierárquica. Manter duas cópias da expansão por unidade_pai_id
garantiria que elas divergissem na primeira mudança de profundidade.
"""
from __future__ import annotations

from lib.csv_utils import clean


SQL_UNIDADES_FILHAS = """
SELECT f.sigla
FROM petrvs_icmbio_unidades f
JOIN petrvs_icmbio_unidades p ON p.id = f.unidade_pai_id AND p.deleted_at IS NULL
WHERE f.deleted_at IS NULL
  AND UPPER(p.sigla) IN ({siglas})
"""


def quote_list(valores) -> str:
    """Monta uma lista SQL de literais com escape de aspas simples."""
    partes = []
    for valor in valores:
        escapado = str(valor).replace("'", "''")
        partes.append("'" + escapado + "'")
    return ", ".join(partes)


def run_query(conn, sql: str) -> tuple[list[str], list[list]]:
    stmt = conn.createStatement()
    rs = stmt.executeQuery(sql)
    meta = rs.getMetaData()
    total = meta.getColumnCount()
    cols = [str(meta.getColumnLabel(i + 1)) for i in range(total)]
    rows: list[list] = []
    while rs.next():
        rows.append([clean(rs.getObject(i + 1)) for i in range(total)])
    rs.close()
    stmt.close()
    return cols, rows


def expandir_subordinadas(conn, siglas: list[str], niveis: int = 3) -> list[str]:
    """Denodo VQL não tem CTE recursiva — expande a hierarquia por iteração."""
    acumulado = {s.upper() for s in siglas}
    fronteira = set(acumulado)
    for _ in range(niveis):
        if not fronteira:
            break
        sql = SQL_UNIDADES_FILHAS.format(siglas=quote_list(sorted(fronteira)))
        _, rows = run_query(conn, sql)
        filhas = {r[0].upper() for r in rows if r[0]}
        fronteira = filhas - acumulado
        acumulado |= filhas
    return sorted(acumulado)


def siglas_de_argumentos(valores: list[str]) -> list[str]:
    """Aceita --unidade repetido e/ou 'A,B,C' numa única ocorrência."""
    siglas: list[str] = []
    for item in valores:
        siglas.extend(parte.strip().upper() for parte in item.split(",") if parte.strip())
    return list(dict.fromkeys(siglas))


def rotulo_de_escopo(siglas: list[str], todas: bool) -> str:
    """Nome curto e estável para compor nomes de arquivo."""
    if todas:
        return "TODAS"
    escopo = "_".join(siglas[:3])
    if len(siglas) > 3:
        escopo += f"_e_mais_{len(siglas) - 3}"
    return escopo
