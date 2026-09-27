"""Seleção mutuamente exclusiva de escopos organizacionais (resolução única, L5/L7).

É o único caminho de resolução para os seletores ``regional``, ``unidade`` e
``lista_unidades``, usado pela extração OCDE, pelos relatórios, pelo ciclo
gerencial, pelo ``gestao.runner`` e pelo ``validation_runner``. Regras (plano §7.1):

- a subordinação segue a hierarquia do **PETRVS** (``unidade_pai_id``), lida do
  retrato local ``PETRVS_unidades.csv`` (decisão de 26/09/2026, provisória até a
  deliberação da Q1 pela CGOV); sem o retrato, esses seletores são **erro**;
- unidade inexistente é **erro** (nunca produto vazio);
- sigla repetida no PETRVS é **erro** quando as homônimas ficam dos dois lados do
  recorte (o filtro dos produtos é por sigla e não conseguiria separá-las); quando
  todas ficam dentro, o recorte é exato;
- ``mesogrupo`` e ``tipo_unidade`` são seletores por rótulo da estrutura oficial.

A chave do escopo é ``<tipo>-<valor>``; a de lista usa o hash das siglas, nunca o
caminho do arquivo. ``ScopeSpec.ids`` traz os ``id`` do PETRVS, raiz primeiro.
"""
from __future__ import annotations

import csv
import hashlib
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping

from lib.estrutura_organizacional import DEFAULT_ESTRUTURA_CSV, load_organization_structure
from lib.escopos import slug
from lib.unidades_petrvs import HierarquiaPetrvs, UnidadePetrvs, carregar_hierarquia


class EscopoInvalido(ValueError):
    """Seletor que não pode ser resolvido sem usar outro critério em silêncio."""


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
    # Escopo resolvido (plano §7.1): ids do PETRVS em ordem (raiz primeiro, depois
    # descendentes em largura). Vazio para nacional e para seletores por rótulo.
    ids: tuple[str, ...] = ()

    @property
    def key(self) -> str:
        if self.kind == "lista_unidades":
            resumo = hashlib.sha256("\n".join(sorted(self.units)).encode("utf-8")).hexdigest()[:12]
            return f"{slug(self.kind)}-{resumo}"
        return f"{slug(self.kind)}-{slug(self.value)}"

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
        result: dict[str, object] = {"tipo": self.kind, "valor": self.value, "chave": self.key}
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
    """Aceita TXT (uma sigla por linha) ou CSV; ignora cabeçalho conhecido e linhas '#'."""
    if not path.exists():
        raise FileNotFoundError(f"Lista de unidades não encontrada: {path}")
    values: set[str] = set()
    with path.open(encoding="utf-8-sig", errors="replace", newline="") as stream:
        sample = stream.read(2048)
        stream.seek(0)
        delimiter = ";" if sample.count(";") > sample.count(",") else ","
        for row in csv.reader(stream, delimiter=delimiter):
            if not row or row[0].lstrip().startswith("#"):
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
    if kind in ("nacional", "mesogrupo", "tipo_unidade"):
        return ScopeSpec(kind, normalize(value))

    hierarquia = carregar_hierarquia()
    if not hierarquia.unidades:
        raise EscopoInvalido(
            f"O seletor '{kind}' exige o cadastro de unidades do PETRVS (PETRVS_unidades.csv; "
            "gere com tools/atualizar_unidades_petrvs.py); sem ele não há outro critério aceito."
        )
    if kind == "regional":
        raiz = _unidade_unica(hierarquia, str(value))
        selecionadas = hierarquia.descendentes(raiz.id)
    elif kind == "unidade":
        selecionadas = [_unidade_unica(hierarquia, str(value))]
    else:  # lista_unidades
        selecionadas = [_unidade_unica(hierarquia, sigla) for sigla in sorted(load_unit_list(Path(value)))]
    _recusar_siglas_divididas(hierarquia, selecionadas)
    siglas = frozenset(normalize(unidade.sigla) for unidade in selecionadas if unidade.sigla)
    safe_value = "LISTA_FORNECIDA" if kind == "lista_unidades" else normalize(value)
    return ScopeSpec(kind, safe_value, siglas, tuple(unidade.id for unidade in selecionadas))


def _unidade_unica(hierarquia: HierarquiaPetrvs, sigla: str) -> UnidadePetrvs:
    candidatas = hierarquia.por_sigla(sigla)
    if not candidatas:
        raise EscopoInvalido(f"Unidade não localizada no cadastro do PETRVS: {normalize(sigla)}")
    if len(candidatas) > 1:
        raise EscopoInvalido(f"Sigla ambígua no PETRVS: {normalize(sigla)} ({len(candidatas)} unidades)")
    return candidatas[0]


def _recusar_siglas_divididas(hierarquia: HierarquiaPetrvs, selecionadas: list[UnidadePetrvs]) -> None:
    """O filtro dos produtos é por sigla: homônimas fora do recorte vazariam para dentro."""

    dentro = {unidade.id for unidade in selecionadas}
    divididas = sorted({
        normalize(unidade.sigla) for unidade in selecionadas
        if any(homonima.id not in dentro for homonima in hierarquia.por_sigla(unidade.sigla))
    })
    if divididas:
        raise EscopoInvalido(f"Sigla(s) ambígua(s) no escopo, com homônimas fora do recorte: {', '.join(divididas)}")


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
        # Subordinação só pela hierarquia resolvida em scope_from_values; sem ela,
        # não há fallback por rótulo de mesogrupo (ESC-01, plano §7.1).
        if not scope.units:
            raise EscopoInvalido(f"Escopo regional {scope.value} sem unidades resolvidas pela hierarquia.")
        return sigla in scope.units
    raise ValueError(f"Tipo de escopo desconhecido: {scope.kind}")


def filter_rows(
    rows: Iterable[Mapping[str, object]],
    scope: ScopeSpec,
    profiles: Mapping[str, UnitProfile] | None = None,
) -> list[dict[str, object]]:
    return [dict(row) for row in rows if unit_matches(row, scope, profiles)]


def resolver_para_runner(
    *,
    escopo: str | None = None,
    regional: str | None = None,
    unidade: str | None = None,
    mesogrupo: str | None = None,
    tipo_unidade: str | None = None,
    lista_unidades: str | Path | None = None,
) -> tuple[str, list[str] | None, str]:
    """(rótulo, siglas ou None para nacional, chave) para gestao.runner e validation_runner.

    regional, unidade e lista usam a resolução única (scope_from_values). mesogrupo e
    tipo_unidade selecionam pela estrutura (rótulos da própria estrutura), como antes.
    A chave é sempre a canônica de ScopeSpec (L5, ESC-04/05).
    """

    if escopo == "nacional" or not any((regional, unidade, mesogrupo, tipo_unidade, lista_unidades)):
        return "nacional", None, ScopeSpec("nacional", "NACIONAL").key
    if regional or unidade or lista_unidades:
        spec = scope_from_values(regional=regional, unidade=unidade, lista_unidades=lista_unidades)
        rotulo = {"regional": f"regional:{regional}", "unidade": f"unidade:{unidade}",
                  "lista_unidades": "lista-unidades:LISTA_FORNECIDA"}[spec.kind]
        return rotulo, sorted(spec.units), spec.key
    estrutura = load_organization_structure()
    if not estrutura.units_by_id:
        raise EscopoInvalido("O seletor solicitado exige a estrutura organizacional (ICMBIO_estrutura.csv).")
    kind, valor = ("mesogrupo", mesogrupo) if mesogrupo else ("tipo_unidade", tipo_unidade)
    unidades = estrutura.select(mesogrupo=mesogrupo, tipo_unidade=tipo_unidade)
    siglas = sorted({unidade.sigla.upper() for unidade in unidades if unidade.sigla})
    if not siglas:
        raise EscopoInvalido("O seletor de escopo não encontrou unidades.")
    rotulo = f"{'mesogrupo' if mesogrupo else 'tipo-unidade'}:{valor}"
    return rotulo, siglas, ScopeSpec(kind, normalize(valor)).key
