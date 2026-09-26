"""CSV and local artifact helpers."""
from __future__ import annotations

import csv
import os
import re
import sys
from datetime import date
from pathlib import Path
from typing import Iterable, Sequence


from .caminhos import PROJECT_ROOT  # raiz única (L4a); reexportada para os A1
INDICATOR_OUTPUT_BASE_ENV = "PGD_INDICATOR_OUTPUT_BASE"


def clean(value: object, default: str = "") -> str:
    if value is None:
        return default
    text = re.sub(r"[\r\n]+", " / ", str(value)).strip()
    return text or default


def artifact_month(today: date | None = None) -> str:
    if today is None:
        injected = os.environ.get("PGD_OUTPUT_MONTH")
        if injected:
            if not re.fullmatch(r"\d{4}-\d{2}", injected):
                raise ValueError("PGD_OUTPUT_MONTH deve usar o formato AAAA-MM.")
            return injected
        if "--month" in sys.argv:
            position = sys.argv.index("--month")
            if position + 1 >= len(sys.argv) or not re.fullmatch(r"\d{4}-\d{2}", sys.argv[position + 1]):
                raise ValueError("--month deve usar o formato AAAA-MM.")
            return sys.argv[position + 1]
        if "--data-execucao" in sys.argv:
            position = sys.argv.index("--data-execucao")
            if position + 1 >= len(sys.argv):
                raise ValueError("--data-execucao exige AAAA-MM-DD.")
            executed = date.fromisoformat(sys.argv[position + 1])
            return f"{executed.year:04d}-{executed.month:02d}"
    current = today or date.today()
    return f"{current.year:04d}-{current.month:02d}"


def indicator_csv_dir(month: str | None = None) -> Path:
    """Pasta de entrega mensal — todos os CSVs de indicadores num único diretório por mês.
    Exemplo: artefatos_local/ocde/entregas/2026-06/
    """
    override = os.environ.get(INDICATOR_OUTPUT_BASE_ENV)
    base = Path(override) if override else PROJECT_ROOT / "artefatos_local" / "ocde" / "entregas"
    return base / (month or artifact_month())


def diagnostic_csv_dir(month: str | None = None) -> Path:
    """Pasta de CSVs diagnósticos (uso interno — não enviar à COCAGE).
    Exemplo: artefatos_local/ocde/diagnosticos/2026-06/
    """
    return PROJECT_ROOT / "artefatos_local" / "ocde" / "diagnosticos" / (month or artifact_month())


def write_pipe_csv(path: Path, columns: Sequence[str], rows: Iterable[Sequence[object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle, delimiter="|")
        writer.writerow([clean(col) for col in columns])
        for row in rows:
            writer.writerow([clean(value) for value in row])
