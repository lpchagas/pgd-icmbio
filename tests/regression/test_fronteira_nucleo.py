"""Fronteira de arquitetura (plano de reorganização, §8; ADR-009).

O núcleo analítico (lib, ocde, gestao, mgi) não importa o agente nem as
dependências exclusivas dele (MySQL e API de modelo). O agente pode usar o
núcleo, nunca o contrário.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.regression
ROOT = Path(__file__).resolve().parents[2]
NUCLEO = ("lib", "ocde", "gestao", "mgi")
PROIBIDOS = ("agente", "pymysql", "anthropic", "db")


def _imports(arquivo: Path) -> set[str]:
    arvore = ast.parse(arquivo.read_text(encoding="utf-8"))
    nomes: set[str] = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            nomes |= {alias.name.split(".")[0] for alias in no.names}
        elif isinstance(no, ast.ImportFrom) and no.module and not no.level:
            nomes.add(no.module.split(".")[0])
    return nomes


def test_nucleo_nao_importa_agente_nem_suas_dependencias():
    violacoes = [
        f"{arquivo.relative_to(ROOT).as_posix()}: {sorted(_imports(arquivo) & set(PROIBIDOS))}"
        for pasta in NUCLEO if (ROOT / pasta).is_dir()
        for arquivo in (ROOT / pasta).rglob("*.py")
        if _imports(arquivo) & set(PROIBIDOS)
    ]
    assert not violacoes, "\n".join(violacoes)


def test_agente_existe_na_raiz_do_monorepo():
    assert (ROOT / "agente" / "dados" / "versoes.py").is_file()
