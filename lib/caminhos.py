"""Raiz única do projeto (plano de reorganização, §4 e L4a).

Os módulos que antes calculavam a raiz por ``__file__`` a partir da própria
posição passam a importá-la daqui; assim, mover um módulo de pasta não muda o
caminho dos artefatos.
"""
from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
