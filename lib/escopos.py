"""Selecao organizacional canonica e isolamento de artefatos por escopo."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import unicodedata


def normalize(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    return " ".join(text.encode("ascii", "ignore").decode().upper().split())


def slug(value: object) -> str:
    normalized = normalize(value).lower().replace(" ", "-")
    return re.sub(r"[^a-z0-9_-]+", "-", normalized).strip("-") or "todos"


@dataclass(frozen=True)
class UnitProfile:
    id: str
    sigla: str
    nome: str = ""
    regional: str = ""
    mesogrupo: str = ""
    tipo: str = ""


@dataclass(frozen=True)
class ScopeSpec:
    kind: str
    value: str
    units: tuple[UnitProfile, ...] = ()

    @property
    def key(self) -> str:
        return f"{slug(self.kind)}-{slug(self.value)}"

    @property
    def label(self) -> str:
        return "Nacional" if self.kind == "nacional" else f"{self.kind}: {self.value}"

    def as_dict(self) -> dict[str, object]:
        return {
            "tipo": self.kind,
            "valor": self.value,
            "chave": self.key,
            "rotulo": self.label,
            "unidades": [unit.sigla for unit in self.units],
            "total_unidades": len(self.units),
        }


def scoped_month_dir(base: Path, month: str, scope: ScopeSpec) -> Path:
    return base / month / "escopos" / scope.key
