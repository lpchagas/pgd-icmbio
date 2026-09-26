"""Caracterização da camada de dados do agente (plano de reorganização, §9.2, L2).

Protege o comportamento que existe hoje em versoes.py e sincronizar_ref.py,
inclusive os defeitos conhecidos, para que a migração estrutural (L3) não o
altere em silêncio. Nada aqui abre MySQL, Denodo ou JVM, nem lê o .env: os
módulos são carregados com db, dotenv e jpype substituídos por dublês.
"""
from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
# src/dados hoje; agente/dados depois do L3 (mesma profundidade).
DADOS = next(p for p in (RAIZ / "agente" / "dados", RAIZ / "src" / "dados") if p.is_dir())


class FalhaInjetada(RuntimeError):
    pass


class CursorFalso:
    def __init__(self, conn: "ConexaoFalsa") -> None:
        self.conn = conn

    def __enter__(self) -> "CursorFalso":
        return self

    def __exit__(self, *exc) -> bool:
        return False

    def _registrar(self, tipo: str, sql: str, params) -> None:
        sql = " ".join(sql.split())
        self.conn.comandos.append((tipo, sql, params))
        if self.conn.falhar_quando and self.conn.falhar_quando in sql:
            raise FalhaInjetada(sql)

    def execute(self, sql: str, params=None) -> None:
        self._registrar("execute", sql, params)

    def executemany(self, sql: str, seq) -> None:
        self._registrar("executemany", sql, list(seq))

    def fetchone(self):
        return self.conn.respostas.pop(0) if self.conn.respostas else None


class ConexaoFalsa:
    """Registra SQL, commits, rollbacks e fechamento; falha no trecho indicado."""

    def __init__(self, respostas=None, falhar_quando: str | None = None) -> None:
        self.respostas = list(respostas or [])
        self.falhar_quando = falhar_quando
        self.comandos: list[tuple] = []
        self.commits = 0
        self.rollbacks = 0
        self.fechada = False

    def cursor(self) -> CursorFalso:
        return CursorFalso(self)

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1

    def close(self) -> None:
        self.fechada = True

    def sql(self, trecho: str) -> list[tuple]:
        return [c for c in self.comandos if trecho in c[1]]


def _proibido(nome: str):
    def chamada(*args, **kwargs):
        raise AssertionError(f"{nome} real não pode ser chamado na caracterização")
    return chamada


@pytest.fixture
def carregar(monkeypatch):
    """Carrega um módulo de DADOS com db/dotenv/jpype substituídos e sys.path restaurado."""

    monkeypatch.setattr(sys, "path", list(sys.path))
    db = types.ModuleType("db")
    db.get_conn = _proibido("get_conn")
    dotenv = types.ModuleType("dotenv")
    dotenv.chamadas = []
    dotenv.load_dotenv = lambda caminho=None, *a, **k: dotenv.chamadas.append(Path(caminho))
    jpype = types.ModuleType("jpype")
    jpype.isJVMStarted = _proibido("jpype.isJVMStarted")
    jpype.startJVM = _proibido("jpype.startJVM")
    jpype.JClass = _proibido("jpype.JClass")
    for nome, modulo in (("db", db), ("dotenv", dotenv), ("jpype", jpype)):
        monkeypatch.setitem(sys.modules, nome, modulo)

    def _carregar(nome: str):
        spec = importlib.util.spec_from_file_location(f"caracterizacao_{nome}", DADOS / f"{nome}.py")
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)
        modulo._dubles = {"db": db, "dotenv": dotenv, "jpype": jpype}
        return modulo

    return _carregar


@pytest.fixture
def conexao():
    """Fábrica de ConexaoFalsa(respostas=..., falhar_quando=...)."""

    return ConexaoFalsa


@pytest.fixture
def falha_injetada():
    return FalhaInjetada
