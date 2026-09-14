from gestao.registry import REGISTRY, enabled_extractions, validate_registry


def test_registry_is_explicit_and_valid():
    assert validate_registry() == []
    assert list(REGISTRY) == ["status-pt", "registro-execucao-pe"]
    assert enabled_extractions()[0].code == "PT_STATUS"
    assert enabled_extractions()[0].temporal_lenses == ("operacional",)


def test_registro_execucao_pe_registrado():
    extraction = REGISTRY["registro-execucao-pe"]
    assert extraction.code == "REG_EXEC"
    assert extraction.entrypoint.is_file()
    assert extraction.business_keys == ("periodo", "unidade_sigla")
    # Anexo A do caderno metodológico: contagem é igualdade exata; percentual
    # tolera 0,05 p.p.; horas e scores toleram 0,01.
    assert extraction.tolerances == {
        "counts": 0.0, "percentages": 0.05, "hours": 0.01, "scores": 0.01,
    }
    assert "rn04_cobertura_dos_ciclos" in extraction.invariants
    assert extraction.baseline == "HOMOLOGACAO_INICIAL_PENDENTE"
