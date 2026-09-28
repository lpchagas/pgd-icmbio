"""Materialização das skills (tools/bootstrap_skills.py): não regride o que já evoluiu (L4d)."""
from __future__ import annotations

import json

import pytest

import tools.bootstrap_skills as bootstrap

pytestmark = pytest.mark.unit


@pytest.fixture
def raiz(tmp_path, monkeypatch):
    monkeypatch.setattr(bootstrap, "ROOT", tmp_path)
    monkeypatch.setattr(bootstrap, "SKILLS", tmp_path / ".agents" / "skills")
    monkeypatch.setattr(bootstrap, "MANIFEST", tmp_path / ".agents" / "skills-manifest.json")
    return tmp_path


def test_materializa_do_zero_e_e_idempotente(raiz, capsys):
    assert bootstrap.main([]) == 0
    skills = raiz / ".agents" / "skills"
    assert len(list(skills.glob("*/SKILL.md"))) == len(bootstrap.CATALOG)
    assert json.loads((raiz / ".agents" / "skills-manifest.json").read_text(encoding="utf-8"))["skills"]

    antes = {p: p.stat().st_mtime_ns for p in (raiz / ".agents").rglob("*") if p.is_file()}
    capsys.readouterr()
    assert bootstrap.main([]) == 0
    assert "preservados" not in capsys.readouterr().out
    assert {p: p.stat().st_mtime_ns for p in antes} == antes  # nada regravado


def test_preserva_skill_e_manifesto_que_evoluiram(raiz, capsys):
    bootstrap.main([])
    skill = raiz / ".agents" / "skills" / "status-pt" / "SKILL.md"
    manifesto = raiz / ".agents" / "skills-manifest.json"
    skill.write_text("texto revisado à mão\n", encoding="utf-8")
    manifesto.write_text('{"schema_version": 2}', encoding="utf-8")
    capsys.readouterr()

    bootstrap.main([])

    saida = capsys.readouterr().out
    assert skill.read_text(encoding="utf-8") == "texto revisado à mão\n"
    assert manifesto.read_text(encoding="utf-8") == '{"schema_version": 2}'
    assert "2 arquivos existentes e diferentes preservados" in saida

    bootstrap.main(["--forcar"])
    assert skill.read_text(encoding="utf-8") == bootstrap.skill_text("status-pt", bootstrap.CATALOG["status-pt"])


def test_pontos_de_entrada_nao_usam_as_pontes_de_relatorios():
    assert not [nome for nome, spec in bootstrap.CATALOG.items() if "ocde.relatorios" in spec["entrypoint"]]
