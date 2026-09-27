"""Reextração do relatório cumulativo (L4e): roda os A1 do contrato, sem driver privado."""
from __future__ import annotations

from datetime import date
from types import SimpleNamespace

import pytest

from lib.validation_contracts import TARGETS
from relatorios import relatorio_cumulativo as rc

pytestmark = pytest.mark.unit


def test_reextrair_roda_os_12_a1_do_contrato_na_area_temporaria(monkeypatch, tmp_path):
    comandos = []
    monkeypatch.setenv("PGD_INDICATOR_OUTPUT_BASE", str(tmp_path))
    monkeypatch.setattr(rc.subprocess, "run", lambda comando, **kw: comandos.append((comando, kw)))
    janela = SimpleNamespace(data_execucao=date(2026, 9, 27), mes_execucao="2026-09")

    rc.reextrair_indicadores(janela)

    esperados = [t.production_entrypoint for t in TARGETS.values() if t.family == "ocde"]
    assert [c[1] for c, _ in comandos] == [str(p) for p in esperados] and len(esperados) == 12
    for comando, kw in comandos:
        assert comando[2:] == ["--data-execucao", "2026-09-27", "--month", "2026-09"]
        assert kw["check"] is True and kw["env"]["PGD_INDICATOR_OUTPUT_BASE"] == str(tmp_path)
        assert ".codex" not in comando[1] and ".agents" not in comando[1]


def test_reextrair_interrompe_na_primeira_falha(monkeypatch):
    chamados = []

    def falha(comando, **kw):
        chamados.append(comando)
        raise rc.subprocess.CalledProcessError(1, comando)

    monkeypatch.setattr(rc.subprocess, "run", falha)
    with pytest.raises(rc.subprocess.CalledProcessError):
        rc.reextrair_indicadores(SimpleNamespace(data_execucao=date(2026, 9, 27), mes_execucao="2026-09"))
    assert len(chamados) == 1
