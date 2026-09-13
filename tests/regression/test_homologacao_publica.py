"""A publicação não pode inferir homologação institucional."""
import json
from pathlib import Path

import pytest

from lib.validation_contracts import TARGETS

pytestmark = pytest.mark.regression
ROOT = Path(__file__).resolve().parents[2]


def test_contratos_publicos_permanecem_pendentes():
    assert {target.baseline for target in TARGETS.values()} == {
        "HOMOLOGACAO_INICIAL_PENDENTE"
    }


def test_baseline_de_exemplo_nao_declara_homologacao():
    data = json.loads(
        (ROOT / "config" / "validation-baselines.example.json").read_text(encoding="utf-8")
    )
    targets = {key: value for key, value in data.items() if not key.startswith("_")}
    assert targets
    assert all(value.get("status") != "HOMOLOGADO" for value in targets.values())
