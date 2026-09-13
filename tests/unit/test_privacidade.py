import pytest

from ocde.relatorios.privacidade import (
    SUPPRESSED,
    apply_complementary_suppression,
    count_band,
    forbidden_fields,
    redact_personal_identifiers,
    scan_text,
)

pytestmark = pytest.mark.unit


def test_faixas_e_k_minimo():
    assert count_band(4) == SUPPRESSED
    assert count_band(5) == "5–9"
    assert count_band(10) == "10–19"
    assert count_band(100) == "100+"


def test_detecta_identificadores_e_campos_livres():
    assert scan_text("campo|email\nvalor|alguem@exemplo.org")
    assert scan_text("valor\n123.456.789-00")
    assert scan_text("valor\n123e4567-e89b-12d3-a456-426614174000")
    assert "nome_servidor" in forbidden_fields(["indicador", "nome_servidor"])


def test_hash_sha256_nao_e_confundido_com_cpf():
    digest = "aae0e12345678901a4a5eed5bf4e79cd95d1fede347a43f0d7f9828e2fa93314"
    assert redact_personal_identifiers(digest) == digest
    assert scan_text(digest) == []
    assert "[CPF_REMOVIDO]" in redact_personal_identifiers("CPF 123.456.789-00")


def test_supressao_complementar_oculta_segundo_subtotal():
    rows = [
        {"pai": "GR2", "qtd": 3, "suprimido": True},
        {"pai": "GR2", "qtd": 7, "suprimido": False},
        {"pai": "GR2", "qtd": 20, "suprimido": False},
    ]
    result = apply_complementary_suppression(rows, parent_keys=["pai"], count_key="qtd")
    assert [row["suprimido"] for row in result] == [True, True, False]
    assert result[1]["motivo_supressao"] == "complementar"
