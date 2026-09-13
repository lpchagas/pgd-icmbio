"""Namespace IND_GEST_ da família de gestão (D17) e alias legado PT_STATUS."""
from __future__ import annotations

import pytest

from gestao.registry import REGISTRY
from lib.validation_contracts import (
    TARGETS,
    gest_artifact,
    normalize_target,
    selected_targets,
    target_artifact_prefix,
)


@pytest.mark.parametrize("value", ["G01", "g01", "IND_GEST_01", "ind_gest_01", "PT_STATUS", " pt_status "])
def test_aliases_resolvem_para_g01(value):
    assert normalize_target(value) == "G01"


@pytest.mark.parametrize("value", ["I07", "IND_07", "IND_OCDE_07"])
def test_alias_ocde_nao_e_afetado(value):
    assert normalize_target(value) == "I07"


def test_prefixo_de_artefato_por_familia():
    assert target_artifact_prefix("G01", "gestao") == "IND_GEST_01"
    assert target_artifact_prefix("I07", "ocde") == "IND_OCDE_07"
    assert gest_artifact("01", "2_painel_*.csv") == "IND_GEST_01.2_painel_*.csv"


def test_contrato_e_registro_apontam_para_a_subpasta():
    entrypoint = TARGETS["G01"].production_entrypoint
    assert entrypoint.parent.name == "IND_GEST_01"
    assert entrypoint.is_file()
    extraction = REGISTRY["status-pt"]
    assert extraction.entrypoint == entrypoint
    assert extraction.artifact_prefix == "IND_GEST_01"
    assert TARGETS["G01"].outputs[0].pattern.startswith("IND_GEST_01.2_")


def test_selecao_pelo_codigo_legado():
    assert [target.code for target in selected_targets("gestao", "PT_STATUS")] == ["G01"]
