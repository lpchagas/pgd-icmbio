"""Hierarquia das unidades do PETRVS (``unidade_pai_id``) para resolver escopos (L7).

Decisão do responsável (26/09/2026, provisória até a CGOV deliberar a Q1 — fonte
primária da taxonomia): os seletores ``regional``, ``unidade`` e ``lista_unidades``
seguem a hierarquia do próprio PETRVS, de onde vêm os PE e os PT. A estrutura
oficial (``ICMBIO_estrutura.csv``) continua servindo aos rótulos de mesogrupo e tipo.

O cadastro é um retrato local, privado, da view ``petrvs_icmbio_unidades`` (só dados
organizacionais), gerado por ``tools/atualizar_unidades_petrvs.py``. O hash do arquivo
identifica a hierarquia usada em cada escopo resolvido.
"""
from __future__ import annotations

import csv
import hashlib
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from lib.caminhos import PROJECT_ROOT

DEFAULT_UNIDADES_PETRVS_CSV = PROJECT_ROOT / "artefatos_local" / "ocde" / "diagnosticos" / "PETRVS_unidades.csv"
COLUNAS = ("id", "codigo", "sigla", "nome", "unidade_pai_id")


def _normalizar(texto: object) -> str:
    return " ".join(str(texto or "").strip().upper().split())


@dataclass(frozen=True)
class UnidadePetrvs:
    id: str
    codigo: str
    sigla: str
    nome: str
    unidade_pai_id: str


@dataclass
class HierarquiaPetrvs:
    unidades: dict[str, UnidadePetrvs]
    sha256: str = ""
    _filhos: dict[str, list[str]] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        filhos: dict[str, list[str]] = defaultdict(list)
        for unidade in sorted(self.unidades.values(), key=lambda u: (_normalizar(u.sigla), u.id)):
            filhos[unidade.unidade_pai_id].append(unidade.id)
        self._filhos = dict(filhos)

    def por_sigla(self, sigla: str) -> list[UnidadePetrvs]:
        alvo = _normalizar(sigla)
        return [u for u in self.unidades.values() if _normalizar(u.sigla) == alvo]

    def descendentes(self, raiz_id: str) -> list[UnidadePetrvs]:
        """Raiz primeiro, depois descendentes em largura (ordem estável), sem ciclos."""

        resultado: list[UnidadePetrvs] = []
        pendentes, vistos = [raiz_id], set()
        while pendentes:
            atual = pendentes.pop(0)
            if atual in vistos:
                continue
            vistos.add(atual)
            if atual in self.unidades:
                resultado.append(self.unidades[atual])
            pendentes.extend(self._filhos.get(atual, []))
        return resultado


def carregar_hierarquia(caminho: Path | None = None) -> HierarquiaPetrvs:
    """Lê o retrato local; ausente ou vazio devolve hierarquia vazia (quem usa decide o erro)."""

    caminho = caminho or DEFAULT_UNIDADES_PETRVS_CSV
    if not caminho.is_file():
        return HierarquiaPetrvs({})
    dados = caminho.read_bytes()
    linhas = csv.DictReader(dados.decode("utf-8-sig").splitlines(), delimiter="|")
    faltantes = set(COLUNAS) - set(linhas.fieldnames or [])
    if faltantes:
        raise ValueError(f"{caminho.name} sem as colunas: {', '.join(sorted(faltantes))}")
    unidades = {}
    for linha in linhas:
        identificador = (linha["id"] or "").strip()
        if identificador:
            unidades[identificador] = UnidadePetrvs(
                identificador, (linha["codigo"] or "").strip(), (linha["sigla"] or "").strip(),
                (linha["nome"] or "").strip(), (linha["unidade_pai_id"] or "").strip(),
            )
    return HierarquiaPetrvs(unidades, hashlib.sha256(dados).hexdigest())
