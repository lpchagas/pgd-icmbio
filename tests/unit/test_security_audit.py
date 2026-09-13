from __future__ import annotations

import importlib.util
from pathlib import Path


MODULE = Path(__file__).resolve().parents[2] / "tools" / "security_audit.py"
SPEC = importlib.util.spec_from_file_location("security_audit", MODULE)
security_audit = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(security_audit)


def test_exact_secret_scan_never_returns_secret(tmp_path):
    secret = "valor-secreto-apenas-fixture"
    env = tmp_path / ".env"
    env.write_text(f"DENODO_PASSWORD={secret}\n", encoding="utf-8")
    (tmp_path / "doc.md").write_text(f"acidente: {secret}\n", encoding="utf-8")
    result = security_audit.scan_exact_secrets(tmp_path, env, ("DENODO_PASSWORD",))
    assert result["status"] == "falha"
    assert result["ocorrencias_fora_do_armazenamento"][0]["arquivo"] == "doc.md"
    assert secret not in str(result)


def test_env_is_an_authorized_location(tmp_path):
    env = tmp_path / ".env"
    env.write_text("DENODO_PASSWORD=segredo-local\n", encoding="utf-8")
    result = security_audit.scan_exact_secrets(tmp_path, env, ("DENODO_PASSWORD",))
    assert result["status"] == "sucesso"


def test_remediation_replaces_only_external_occurrence_and_preserves_env(tmp_path):
    secret = "valor-secreto-remediacao"
    env = tmp_path / ".env"
    exposed = tmp_path / "legacy.md"
    env.write_text(f"DENODO_PASSWORD={secret}\n", encoding="utf-8")
    exposed.write_text(f"legado: {secret}\n", encoding="utf-8")
    result = security_audit.remediate_exact_secrets(tmp_path, env, ("DENODO_PASSWORD",))
    assert result["status"] == "sucesso"
    assert result["arquivos_sanitizados"] == ["legacy.md"]
    assert secret in env.read_text(encoding="utf-8")
    assert secret not in exposed.read_text(encoding="utf-8")
