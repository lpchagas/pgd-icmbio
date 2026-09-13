from lib.ciclo_gerencial import STAGES, run
from lib.indicator_extraction import _manifest_filename


def test_cycle_dry_run_has_all_gates():
    manifest = run([
        "--data-execucao", "2026-09-12", "--regional", "GR2", "--dry-run"
    ])
    assert manifest["periodo_analise_inicio"] == "2025-07-01"
    assert manifest["periodo_analise_fim"] == "2026-08-31"
    assert manifest["status_global"] == "dry-run"
    assert tuple(manifest["plano_execucao"]) == STAGES

def test_partial_indicator_manifest_never_replaces_full_cycle_manifest():
    assert _manifest_filename(True, "run-1") == "manifesto_extracao_indicadores.json"
    assert _manifest_filename(False, "run-1") == "manifesto_extracao_indicadores_parcial_run-1.json"
