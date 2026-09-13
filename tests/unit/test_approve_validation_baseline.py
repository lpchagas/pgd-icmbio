from __future__ import annotations

import json

import pytest

from tools.approve_validation_baseline import approve


def _manifest(path, mode="integrado"):
    payload = {
        "run_id": "20260912T120000-deadbeef",
        "modo": mode,
        "fingerprint": "f" * 64,
        "resultados": [{
            "alvo": "I01",
            "status": "pendente",
            "formula_version": "2.0.0",
            "hashes": {"A1": "a" * 64},
            "perfis_A2": [],
        }],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_fixture_cannot_be_homologated(tmp_path):
    manifest = tmp_path / "manifest.json"
    _manifest(manifest, mode="fixture")
    with pytest.raises(ValueError, match="Fixture"):
        approve([
            "--manifesto", str(manifest), "--alvo", "I01",
            "--papel-aprovador", "CGOV", "--decisao", "HOMOLOGADO",
            "--justificativa", "Definição de negócio aprovada.",
            "--baseline", str(tmp_path / "baseline.json"),
        ])


def test_integrated_manifest_creates_private_baseline(tmp_path):
    manifest = tmp_path / "manifest.json"
    baseline = tmp_path / "baseline.json"
    _manifest(manifest)
    approve([
        "--manifesto", str(manifest), "--alvo", "I01",
        "--papel-aprovador", "CGOV", "--decisao", "HOMOLOGADO",
        "--justificativa", "Definição de negócio aprovada.",
        "--baseline", str(baseline),
    ])
    saved = json.loads(baseline.read_text(encoding="utf-8"))["I01"]
    assert saved["status"] == "HOMOLOGADO"
    assert saved["approved_by_role"] == "CGOV"
