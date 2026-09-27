"""Arredondamento único dos indicadores (decisão CGOV D24, 27.09.2026).

Meio para cima (*half up*), como o ``ROUND`` do banco: 3,925 → 3,93 e 31,25 → 31,3.
O ``round()`` do Python arredonda para o par (3,925 → 3,92) e gerava divergências
entre os A1 que agregam em Python e os que agregam em SQL. O oracle tem a sua
própria implementação, por independência.
"""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal


def arredondar(valor: float, casas: int = 2) -> float:
    """Arredonda meio para cima; parte da representação decimal curta do float."""

    return float(Decimal(repr(float(valor))).quantize(Decimal(1).scaleb(-casas), rounding=ROUND_HALF_UP))
