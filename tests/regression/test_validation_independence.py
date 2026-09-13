from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_oracles_do_not_import_production_formulas_or_sql():
    path = ROOT / "lib" / "validation_oracles.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
    forbidden = ("ocde.indicadores", "lib.monthly_runner", "lib.docs_sql")
    assert not any(name.startswith(forbidden) for name in imports)


def test_oracle_module_contains_no_denodo_sql():
    text = (ROOT / "lib" / "validation_oracles.py").read_text(encoding="utf-8").upper()
    assert "PETRVS_ICMBIO_" not in text
    assert "SELECT " not in text
