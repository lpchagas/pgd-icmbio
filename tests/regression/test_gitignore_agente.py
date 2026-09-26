"""Regras do .gitignore para o agente incorporado (plano de reorganização, §5).

A exceção SQL é restrita ao schema e às migrações numeradas do agente; dumps
continuam recusados mesmo dentro dela. Consulta o próprio Git, sem criar arquivos.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.regression
ROOT = Path(__file__).resolve().parents[2]


def _ignorado(caminho: str) -> bool:
    resultado = subprocess.run(["git", "-C", str(ROOT), "check-ignore", "-q", "--no-index", caminho], capture_output=True)
    if resultado.returncode not in (0, 1):
        pytest.skip("check-ignore exige o repositório Git")
    return resultado.returncode == 0


@pytest.mark.parametrize("caminho", [
    "agente/dados/schema.sql",
    "agente/dados/migracoes/002_estado_alvo.sql",
    "agente/docs/referencias-pgd/README.md",
    "docs/referencias-pgd/README.md",
    ".env.example",
    "requirements-agente.txt",
])
def test_versionaveis(caminho):
    assert not _ignorado(caminho)


@pytest.mark.parametrize("caminho", [
    "agente/dados/migracoes/002_backup.dump.sql",   # dump dentro da exceção
    "agente/dados/pgd_agente_20260901.sql",          # dump pelo nome
    "agente/dados/migracoes/pgd_agente_x.sql",
    "agente/dados/extra.sql",                        # SQL fora da exceção
    "lib/qualquer.sql",
    "agente/docs/referencias-pgd/norma.pdf",         # acervo privado no local intermediário
    "docs/referencias-pgd/norma.pdf",
    "agente/data/backups/pgd.sql",
    "data/vectorstore/indice.bin",
    "agente/testes_cgov/s01.md",
    ".env",
    "agente/.env",
    "CLAUDE.md",
    "agente/AGENTS.md",
])
def test_recusados(caminho):
    assert _ignorado(caminho)
