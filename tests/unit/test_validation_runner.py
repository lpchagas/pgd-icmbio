from __future__ import annotations

import json

from lib.validation_runner import run


def test_fixture_cycle_generates_a3_a4_a5_for_all_targets(tmp_path, monkeypatch):
    monkeypatch.setenv("PGD_VALIDATION_OUTPUT_BASE", str(tmp_path))
    manifest = run([
        "--data-execucao", "2026-09-12", "--familia", "todas",
        "--alvo", "todos", "--modo", "fixture", "--salvar",
    ])
    assert manifest["status_global"] == "pendente"
    assert manifest["periodo_analise_inicio"] == "2025-07-01"
    assert manifest["periodo_analise_fim"] == "2026-08-31"
    assert len(manifest["resultados"]) == 14
    assert {item["decisao"] for item in manifest["resultados"]} == {"HOMOLOGACAO_INICIAL_PENDENTE"}
    output_dir = tmp_path / "2026-09" / "escopos" / "nacional-nacional"
    generated = list(output_dir.glob("*.5_relatorio_validacao_*.md"))
    assert len(generated) == 14
    persisted = json.loads((output_dir / ("manifesto_validacao_" + manifest["run_id"] + ".json")).read_text(encoding="utf-8"))
    assert persisted["status_global"] == "pendente"

    consolidated = run([
        "--data-execucao", "2026-09-12", "--familia", "todas",
        "--alvo", "todos", "--modo", "fixture", "--consolidar-existentes",
    ])
    assert consolidated["tipo"] == "protocolo_validacao_A1_A5_consolidado"
    assert len(consolidated["resultados"]) == 14


def test_unknown_target_fails(tmp_path, monkeypatch):
    monkeypatch.setenv("PGD_VALIDATION_OUTPUT_BASE", str(tmp_path))
    try:
        run(["--data-execucao", "2026-09-12", "--alvo", "I99"])
    except ValueError as exc:
        assert "desconhecido" in str(exc)
    else:
        raise AssertionError("alvo inválido deveria falhar")
