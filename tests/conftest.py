"""Fixtures compartilhadas da suíte de testes do pgd-ocde-icmbio.

Nenhum teste desta suíte abre conexão de rede ou JDBC — ver tests/README.md
para a decisão de não mockar jpype/Denodo.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

# lib/ e ocde/ são pacotes na raiz do projeto (mesmo padrão de bootstrap usado
# pelos scripts IND_OCDE_XX.1_run.py) — necessário para "import lib.xxx"/"import ocde.xxx".
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def project_root() -> Path:
    return PROJECT_ROOT


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES_DIR


HIERARQUIA_SINTETICA = FIXTURES_DIR / "escopo" / "PETRVS_unidades.csv"
ESTRUTURA_SINTETICA = FIXTURES_DIR / "escopo" / "ICMBIO_estrutura.csv"


@pytest.fixture(autouse=True)
def bloquear_denodo(monkeypatch):
    """Nenhum teste abre o Denodo, nem em subprocesso (lib.denodo_config.connect recusa).

    Motivo (L7): um teste do executor de pilotos chegou ao modo real quando o cadastro
    passou a estar conferido e extraiu dados reais para o acervo privado.
    """
    monkeypatch.setenv("PGD_BLOQUEAR_DENODO", "1")


@pytest.fixture(autouse=True)
def hierarquia_petrvs_sintetica(monkeypatch):
    """Todo teste resolve escopos pela hierarquia sintética do PETRVS (L7).

    Sem isto, testes passariam localmente lendo o retrato privado
    (artefatos_local/.../PETRVS_unidades.csv) e falhariam num clone limpo.
    Testes que precisam de outra hierarquia sobrescrevem o mesmo ponto.
    """
    import relatorios.escopo as escopo
    from lib import liberacao
    from lib.unidades_petrvs import carregar_hierarquia

    from lib.estrutura_organizacional import load_organization_structure

    hierarquia = carregar_hierarquia(HIERARQUIA_SINTETICA)
    monkeypatch.setattr(escopo, "carregar_hierarquia", lambda *a: hierarquia)
    monkeypatch.setattr(liberacao, "carregar_hierarquia", lambda *a: hierarquia)
    # Trava D19: a estrutura oficial também é sintética (sem dicionário = sem conflito).
    estrutura = load_organization_structure(ESTRUTURA_SINTETICA, ESTRUTURA_SINTETICA.parent / "sem-dicionario.csv")
    monkeypatch.setattr(escopo, "load_organization_structure", lambda *a: estrutura)
    return hierarquia
