from gestao.registry import REGISTRY, enabled_extractions, validate_registry


def test_registry_is_explicit_and_valid():
    assert validate_registry() == []
    assert list(REGISTRY) == ["status-pt"]
    assert enabled_extractions()[0].code == "G01"
    assert enabled_extractions()[0].temporal_lenses == ("operacional",)
