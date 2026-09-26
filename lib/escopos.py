"""Normalização de rótulos de escopo para chaves e diretórios de artefatos.

O ``ScopeSpec`` único e a resolução de escopo ficam em ``relatorios.escopo``
(L5, ESC-06): este módulo mantinha uma segunda ``ScopeSpec`` sem consumidores.
"""

from __future__ import annotations

import re
import unicodedata


def normalize(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    return " ".join(text.encode("ascii", "ignore").decode().upper().split())


def slug(value: object) -> str:
    normalized = normalize(value).lower().replace(" ", "-")
    return re.sub(r"[^a-z0-9_-]+", "-", normalized).strip("-") or "todos"
