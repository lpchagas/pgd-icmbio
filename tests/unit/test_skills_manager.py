import json
import os

import pytest

import tools.skills_manager as manager
from tools.skills_manager import _redact_path, _windows_to_local, install, metadata, validate_package


def test_valid_minimal_skill(tmp_path):
    skill_dir = tmp_path / "minha-skill"
    (skill_dir / "tests").mkdir(parents=True)
    skill = skill_dir / "SKILL.md"
    skill.write_text(
        "---\nname: minha-skill\ndescription: Executa uma tarefa de teste claramente delimitada e verificável.\n---\n\nUse o módulo canônico.\n",
        encoding="utf-8",
    )
    (skill_dir / "tests" / "prompts.json").write_text(
        json.dumps({"positive": [str(i) for i in range(5)], "negative": [str(i) for i in range(5)]}),
        encoding="utf-8",
    )
    assert metadata(skill)["name"] == "minha-skill"
    assert validate_package("minha-skill", {"status": "active"}, tmp_path) == []


def test_rejects_noncanonical_name_and_missing_tests(tmp_path):
    skill_dir = tmp_path / "nome_invalido"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\nname: nome_invalido\ndescription: Descrição suficientemente longa para o teste do contrato.\n---\n",
        encoding="utf-8",
    )
    findings = validate_package("nome_invalido", {"status": "active"}, tmp_path)
    assert "nome não segue kebab-case" in findings
    assert "tests/prompts.json ausente" in findings



def test_windows_executable_path_is_supported_and_redacted():
    expected = "C:\\Tools\\codex.exe" if os.name == "nt" else "/mnt/c/Tools/codex.exe"
    assert _windows_to_local("C:\\Tools\\codex.exe") == expected
    assert _redact_path("C:\\Users\\pessoa\\codex.exe") == "%USERPROFILE%\\codex.exe"


def test_install_is_idempotent_for_correct_symlink(tmp_path, monkeypatch):
    canonical = tmp_path / ".agents" / "skills"
    source = canonical / "skill-a"
    source.mkdir(parents=True)
    (source / "SKILL.md").write_text("conteúdo", encoding="utf-8")
    claude = tmp_path / ".claude" / "skills"
    claude.mkdir(parents=True)
    try:
        (claude / "skill-a").symlink_to(source, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"ambiente sem privilégio para criar symlink: {exc}")
    monkeypatch.setattr(manager, "CANONICAL", canonical)
    monkeypatch.setattr(manager, "CLAUDE", claude)
    monkeypatch.setattr(manager, "CODEX_LEGACY", tmp_path / ".codex" / "skills")
    assert install(apply=False)["acoes"] == []
