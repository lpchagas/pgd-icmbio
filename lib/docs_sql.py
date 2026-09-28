"""Extract and adapt public SQL references from docs/*.md."""
from __future__ import annotations

import re
from pathlib import Path


from .caminhos import PROJECT_ROOT  # raiz única (L4a)

TABLES = [
    "planos_trabalhos_consolidacoes",
    "planos_trabalhos_entregas",
    "planos_entregas_entregas",
    "tipos_avaliacoes_notas",
    "integracao_servidores",
    "planos_trabalhos",
    "planos_entregas",
    "avaliacoes",
    "unidades",
    "usuarios",
]


def read_doc(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def extract_python_string(markdown: str, name: str) -> str:
    pattern = rf"^{re.escape(name)}\s*=\s*\"\"\"\n(.*?)\n\"\"\""
    match = re.search(pattern, markdown, flags=re.MULTILINE | re.DOTALL)
    if not match:
        raise ValueError(f"Nao encontrei a string Python {name}.")
    return match.group(1)


def extract_first_sql_block(markdown: str) -> str:
    match = re.search(r"```sql\n(.*?)\n```", markdown, flags=re.DOTALL | re.IGNORECASE)
    if not match:
        raise ValueError("Nao encontrei bloco ```sql``` na documentacao.")
    return match.group(1)


def extract_indicator_sql(doc_path: str, indicator: str) -> str:
    markdown = read_doc(doc_path)
    for candidate in (f"SQL_I{indicator}", "SQL_PLANOS"):
        try:
            return extract_python_string(markdown, candidate)
        except ValueError:
            pass
    return extract_first_sql_block(markdown)


def adapt_for_jdbc(sql: str) -> str:
    adapted = sql
    for table in TABLES:
        adapted = re.sub(
            rf"\b(from|join)\s+(?!petrvs_icmbio_){table}\b",
            rf"\1 petrvs_icmbio_{table}",
            adapted,
            flags=re.IGNORECASE,
        )
    adapted = re.sub(
        r"\bdate\(([^()\n]+?)\)",
        r"CAST(\1 AS DATE)",
        adapted,
        flags=re.IGNORECASE,
    )
    # JSON_UNQUOTE() is a MySQL function not available in Denodo VQL.
    # The outer TRIM(BOTH '"' FROM ...) already handles quote removal from the field value.
    adapted = re.sub(r"\bJSON_UNQUOTE\(([^()]+)\)", r"\1", adapted, flags=re.IGNORECASE)
    return adapted


def set_period(sql: str, start: str, end: str) -> str:
    current = sql.replace("{ini}", start).replace("{fim}", end)
    current = re.sub(
        r"CAST\('[0-9]{4}-[0-9]{2}-[0-9]{2}'\s+AS\s+DATE\)(\s+as\s+data_inicio)",
        f"CAST('{start}' AS DATE)\\1",
        current,
        count=1,
        flags=re.IGNORECASE,
    )
    current = re.sub(
        r"CAST\('[0-9]{4}-[0-9]{2}-[0-9]{2}'\s+AS\s+DATE\)(\s+as\s+data_fim)",
        f"CAST('{end}' AS DATE)\\1",
        current,
        count=1,
        flags=re.IGNORECASE,
    )
    return current
