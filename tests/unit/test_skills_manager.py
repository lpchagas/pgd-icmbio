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


# ─── L4d: link de descoberta pela plataforma (junção no Windows) ─────────────


@pytest.fixture
def skills(tmp_path, monkeypatch):
    canonical = tmp_path / ".agents" / "skills"
    for nome in ("skill-a", "skill-b"):
        (canonical / nome).mkdir(parents=True)
        (canonical / nome / "SKILL.md").write_text(f"conteúdo {nome}", encoding="utf-8")
    claude = tmp_path / ".claude" / "skills"
    monkeypatch.setattr(manager, "CANONICAL", canonical)
    monkeypatch.setattr(manager, "CLAUDE", claude)
    monkeypatch.setattr(manager, "CODEX_LEGACY", tmp_path / ".codex" / "skills")
    return canonical, claude


def test_tipo_de_link_pela_plataforma():
    assert manager.link_type() == ("juncao" if os.name == "nt" else "symlink")


def test_install_cria_links_e_e_idempotente(skills):
    canonical, claude = skills

    plano = install(apply=False)
    assert [(a["action"], a["anterior"]) for a in plano["acoes"]] == [(manager.link_type(), None)] * 2
    assert not claude.exists()

    install(apply=True)
    for nome in ("skill-a", "skill-b"):
        assert manager._is_link(claude / nome)
        assert (claude / nome / "SKILL.md").read_text(encoding="utf-8") == f"conteúdo {nome}"
    assert install(apply=False)["acoes"] == []
    assert install(apply=True)["acoes"] == []


def test_install_substitui_link_errado_sem_tocar_o_destino(skills, tmp_path):
    canonical, claude = skills
    outro = tmp_path / "outro"
    outro.mkdir()
    (outro / "SKILL.md").write_text("não apagar", encoding="utf-8")
    claude.mkdir(parents=True)
    manager._create_link(outro, claude / "skill-a")

    resultado = install(apply=True)

    assert {a["target"].rsplit(os.sep, 1)[-1]: a["anterior"] for a in resultado["acoes"]} == {
        "skill-a": "link", "skill-b": None}
    assert (claude / "skill-a" / "SKILL.md").read_text(encoding="utf-8") == "conteúdo skill-a"
    assert (outro / "SKILL.md").read_text(encoding="utf-8") == "não apagar"
    assert not (canonical.parent / "skill-backups").exists()  # link não vai para o backup


def test_install_move_pasta_real_para_o_backup(skills):
    canonical, claude = skills
    (claude / "skill-b").mkdir(parents=True)
    (claude / "skill-b" / "nota.md").write_text("cópia local", encoding="utf-8")

    resultado = install(apply=True)

    backups = list((canonical.parent / "skill-backups").glob("*/claude-skill-b/nota.md"))
    assert len(backups) == 1 and backups[0].read_text(encoding="utf-8") == "cópia local"
    assert manager._is_link(claude / "skill-b")
    assert resultado["backup"]


def test_is_link_nao_confunde_pasta_real(tmp_path):
    pasta = tmp_path / "real"
    pasta.mkdir()
    assert not manager._is_link(pasta)
    assert not manager._is_link(tmp_path / "ausente")
    manager._create_link(pasta, tmp_path / "link")
    assert manager._is_link(tmp_path / "link")
