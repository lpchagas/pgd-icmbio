import ast
import importlib.util
from pathlib import Path

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
    digest = "aae0e12345678901a4a5eed5bf4e79cd95d1fede347a43f0d7f9828e2fa93314"  # pragma: allowlist secret
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


# ---------------------------------------------------------------------------
# D14 — identificação nominal no G01 (IND_GEST_01, ex-PT_STATUS): permitida nos produtos internos da
# unidade, proibida no produto que circula fora dela.
# ---------------------------------------------------------------------------

IND_GEST_01 = Path(__file__).resolve().parents[2] / "gestao" / "IND_GEST_01" / "IND_GEST_01.1_run.py"


def _modulo_ind_gest_01() -> ast.Module:
    return ast.parse(IND_GEST_01.read_text(encoding="utf-8"))


def _constante(nome: str):
    for node in _modulo_ind_gest_01().body:
        if isinstance(node, ast.Assign) and any(
            isinstance(alvo, ast.Name) and alvo.id == nome for alvo in node.targets
        ):
            return ast.literal_eval(node.value)
    raise AssertionError(f"Constante {nome} ausente em IND_GEST_01.1_run.py")


def test_produtos_nominais_excluem_o_compartilhavel():
    nominais = _constante("PRODUTOS_NOMINAIS")
    assert "operacional" in nominais and "restrito" in nominais
    assert "compartilhavel" not in nominais, (
        "O produto que circula fora da unidade não pode trazer identificação nominal."
    )


def test_detalhe_nunca_e_gerado_para_o_produto_compartilhavel():
    fonte = IND_GEST_01.read_text(encoding="utf-8")
    assert 'if args.produto != "compartilhavel":' in fonte
    assert 'gest_artifact("01", f"2_detalhe_{args.produto}' in fonte


def _script_ind_gest_01():
    spec = importlib.util.spec_from_file_location("ind_gest_01_run", IND_GEST_01)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_painel_compartilhavel_mantem_supressao_k():
    painel = _script_ind_gest_01().montar_painel(
        {("U1", "Em execução"): 30, ("U2", "Rascunho"): 4, ("U2", "Em execução"): 3},
        "compartilhavel",
    )
    assert ["U1", "Em execução", 30] in painel
    assert all(linha[2] == "SUPRIMIDO_K" for linha in painel if linha[0] == "U2")


def test_painel_compartilhavel_aplica_supressao_complementar():
    """D17/F11: uma única célula oculta seria deduzível pelo total da unidade."""
    painel = _script_ind_gest_01().montar_painel(
        {("U1", "Em execução"): 40, ("U1", "Aguardando avaliação"): 8, ("U1", "Rascunho"): 2},
        "compartilhavel",
    )
    valores = {linha[1]: linha[2] for linha in painel}
    assert valores == {
        "Em execução": 40, "Aguardando avaliação": "SUPRIMIDO_K", "Rascunho": "SUPRIMIDO_K",
    }


def test_painel_restrito_nao_suprime():
    painel = _script_ind_gest_01().montar_painel({("U1", "Rascunho"): 2}, "restrito")
    assert painel == [["U1", "Rascunho", 2]]


def test_ind_gest_01_coleta_o_minimo_necessario():
    """D14: nome e id bastam para a chefia agir; e-mail, CPF e matrícula não."""
    fonte = IND_GEST_01.read_text(encoding="utf-8")
    sql = next(
        node.value for node in ast.walk(_modulo_ind_gest_01())
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
        and "petrvs_icmbio_planos_trabalhos" in node.value
    )
    assert "us.nome" in sql and "pt.usuario_id" in sql
    assert "us.email" not in sql
    assert "cpf" not in sql.lower()
    assert 'personal_columns = {"id_servidor", "servidor_nome", "status_alterado_por"}' in fonte
