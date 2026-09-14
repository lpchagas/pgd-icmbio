from gestao.registry import REGISTRY, enabled_extractions, validate_registry


def test_registry_is_explicit_and_valid():
    assert validate_registry() == []
    assert list(REGISTRY) == ["status-pt", "execucao-entregas"]
    assert enabled_extractions()[0].code == "G01"
    assert enabled_extractions()[0].temporal_lenses == ("operacional",)
    assert [item.code for item in enabled_extractions()] == ["G01", "G02"]
    assert all(item.report_adapter for item in enabled_extractions())
