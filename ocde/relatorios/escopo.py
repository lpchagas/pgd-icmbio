"""Seleção mutuamente exclusiva de escopos organizacionais do relatório."""
from __future__ import annotations

import csv
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping

from lib.estrutura_organizacional import DEFAULT_ESTRUTURA_CSV, load_organization_structure


def normalize(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or "")).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", text.strip().upper())


@dataclass(frozen=True)
class UnitProfile:
    sigla: str
    mesogrupo: str = ""
    tipo: str = ""


@dataclass(frozen=True)
class ScopeSpec:
    kind: str
    value: str
    units: frozenset[str] = frozenset()

    @property
    def label(self) -> str:
        labels = {
            "nacional": "ICMBio — nacional",
            "regional": f"Regional {self.value}",
            "unidade": f"Unidade {self.value}",
            "mesogrupo": f"Mesogrupo {self.value}",
            "tipo_unidade": f"Tipo de unidade {self.value}",
            "lista_unidades": "Lista de unidades selecionada",
        }
        return labels[self.kind]

    def as_dict(self) -> dict[str, object]:
        result: dict[str, object] = {"tipo": self.kind, "valor": self.value}
        return result


def load_unit_profiles(path: Path = DEFAULT_ESTRUTURA_CSV) -> dict[str, UnitProfile]:
    """Carrega apenas sigla, mesogrupo e tipo da estrutura institucional privada."""
    if not path.exists():
        return {}
    with path.open(encoding="utf-8-sig", errors="replace", newline="") as stream:
        lines = stream.readlines()
    if len(lines) < 2:
        return {}
    reader = csv.DictReader(lines[1:])
    profiles: dict[str, UnitProfile] = {}
    for row in reader:
        sigla = normalize(row.get("sigla"))
        if sigla:
            profiles[sigla] = UnitProfile(
                sigla=sigla,
                mesogrupo=str(row.get("mesogrupo") or "").strip(),
                tipo=str(row.get("tipo") or "").strip(),
            )
    return profiles


def load_unit_list(path: Path) -> frozenset[str]:
    """Aceita TXT (uma sigla por linha) ou CSV; ignora cabeçalho conhecido."""
    if not path.exists():
        raise FileNotFoundError(f"Lista de unidades não encontrada: {path}")
    values: set[str] = set()
    with path.open(encoding="utf-8-sig", errors="replace", newline="") as stream:
        sample = stream.read(2048)
        stream.seek(0)
        delimiter = ";" if sample.count(";") > sample.count(",") else ","
        for row in csv.reader(stream, delimiter=delimiter):
            if not row:
                continue
            value = normalize(row[0])
            if value and value not in {"SIGLA", "UNIDADE", "UNIDADE_SIGLA"}:
                values.add(value)
    if not values:
        raise ValueError("A lista de unidades está vazia.")
    return frozenset(values)


def scope_from_values(
    *,
    escopo: str | None = None,
    regional: str | None = None,
    unidade: str | None = None,
    mesogrupo: str | None = None,
    tipo_unidade: str | None = None,
    lista_unidades: str | Path | None = None,
) -> ScopeSpec:
    selected = [
        ("nacional", escopo) if escopo else None,
        ("regional", regional) if regional else None,
        ("unidade", unidade) if unidade else None,
        ("mesogrupo", mesogrupo) if mesogrupo else None,
        ("tipo_unidade", tipo_unidade) if tipo_unidade else None,
        ("lista_unidades", str(lista_unidades)) if lista_unidades else None,
    ]
    selected = [item for item in selected if item]
    if len(selected) != 1:
        raise ValueError("Informe exatamente um seletor de escopo.")
    kind, value = selected[0]
    if kind == "nacional" and normalize(value) != "NACIONAL":
        raise ValueError("O único valor aceito por --escopo é 'nacional'.")
    units = load_unit_list(Path(value)) if kind == "lista_unidades" else frozenset()
    if kind == "regional":
        structure = load_organization_structure()
        root = structure.unit_for_sigla(str(value))
        if root:
            units = frozenset(
                normalize(unit.sigla)
                for unit in structure.descendants(root.icmbio_id)
                if unit.sigla
            )
    safe_value = "LISTA_FORNECIDA" if kind == "lista_unidades" else normalize(value)
    return ScopeSpec(kind, safe_value, units)


def unit_matches(
    row: Mapping[str, object],
    scope: ScopeSpec,
    profiles: Mapping[str, UnitProfile] | None = None,
) -> bool:
    if scope.kind == "nacional":
        return True
    sigla = normalize(row.get("unidade_sigla"))
    mesogrupo = normalize(row.get("mesogrupo"))
    profile = (profiles or {}).get(sigla)
    if scope.kind == "unidade":
        return sigla == scope.value
    if scope.kind == "lista_unidades":
        return sigla in scope.units
    if scope.kind == "mesogrupo":
        return mesogrupo == scope.value or (profile is not None and normalize(profile.mesogrupo) == scope.value)
    if scope.kind == "tipo_unidade":
        return profile is not None and normalize(profile.tipo) == scope.value
    if scope.kind == "regional":
        # Fonte normativa de subordinação: grafo id_mae. Mesogrupo é apenas
        # fallback para ambientes sem as tabelas privadas de estrutura.
        if scope.units:
            return sigla in scope.units
        return (
            sigla == scope.value
            or mesogrupo in {scope.value, f"UC NA {scope.value}"}
            or (profile is not None and normalize(profile.mesogrupo) in {scope.value, f"UC NA {scope.value}"})
        )
    raise ValueError(f"Tipo de escopo desconhecido: {scope.kind}")


def filter_rows(
    rows: Iterable[Mapping[str, object]],
    scope: ScopeSpec,
    profiles: Mapping[str, UnitProfile] | None = None,
) -> list[dict[str, object]]:
    return [dict(row) for row in rows if unit_matches(row, scope, profiles)]
