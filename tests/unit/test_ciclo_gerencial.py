from pathlib import Path

import pytest

import relatorios.escopo as escopo
from lib.ciclo_gerencial import STAGES, run
from lib.estrutura_organizacional import OrganizationStructure, load_organization_structure
from lib.indicator_extraction import _manifest_filename

ESTRUTURA = Path(__file__).resolve().parents[1] / "fixtures" / "escopo" / "ICMBIO_estrutura.csv"


@pytest.fixture(autouse=True)
def estrutura_sintetica(monkeypatch):
    """Estrutura sintética sem a homônima UC-DUP da GR1: o teste não depende do acervo privado."""

    completa = load_organization_structure(ESTRUTURA, ESTRUTURA.parent / "sem-dicionario.csv")
    unidades = {i: u for i, u in completa.units_by_id.items() if i != "22"}
    monkeypatch.setattr(escopo, "load_organization_structure", lambda: OrganizationStructure(unidades, {}))


def test_cycle_dry_run_has_all_gates():
    manifest = run([
        "--data-execucao", "2026-09-12", "--regional", "GR2", "--dry-run"
    ])
    assert manifest["periodo_analise_inicio"] == "2025-07-01"
    assert manifest["periodo_analise_fim"] == "2026-08-31"
    assert manifest["status_global"] == "dry-run"
    assert tuple(manifest["plano_execucao"]) == STAGES


def test_cycle_dry_run_reports_resolved_scope_destination_and_targets():
    manifest = run([
        "--data-execucao", "2026-09-14", "--unidade", "CGOV", "--dry-run"
    ])

    assert manifest["escopo_resolvido"] == {
        "tipo": "unidade",
        "valor": "CGOV",
        "chave": "unidade-cgov",
    }
    normalized_destination = manifest["pasta_destino"].replace("\\", "/")
    assert normalized_destination.endswith(
        "artefatos_local/ocde/entregas/2026-09/escopos/unidade-cgov"
    )
    assert manifest["alvos_previstos"] == [
        *(f"I{number:02d}" for number in range(1, 13)),
        "G01",
        "G02",
    ]


def test_partial_indicator_manifest_never_replaces_full_cycle_manifest():
    assert _manifest_filename(True, "run-1") == "manifesto_extracao_indicadores.json"
    assert _manifest_filename(False, "run-1") == "manifesto_extracao_indicadores_parcial_run-1.json"
