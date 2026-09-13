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


# ---------------------------------------------------------------------------
# D17 — correções de método do G01 (formula_version 4.0.0)
# ---------------------------------------------------------------------------

import importlib.util  # noqa: E402
from datetime import date  # noqa: E402

from lib.validation_oracles import calculate  # noqa: E402


def _script():
    path = TARGETS["G01"].production_entrypoint
    spec = importlib.util.spec_from_file_location("ind_gest_01_run", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _plano(pid, status, unidade="U1"):
    return {"_extractor": "pt_status_planos", "plano_trabalho_id": pid,
            "unidade_sigla": unidade, "status_codigo": status,
            "plano_updated_at": "2026-08-01T00:00:00"}


def _consolidacao(pid, status):
    return {"_extractor": "pt_status_consolidacoes", "plano_trabalho_id": pid,
            "consolidacao_id": f"C-{pid}-{status}", "consolidacao_status": status}


def test_f1_concluido_com_periodo_pendente_entra_na_fila():
    rows = [_plano("P1", "CONCLUIDO"), _consolidacao("P1", "CONCLUIDO")]
    assert calculate("G01", rows) == [
        {"unidade_sigla": "U1", "status_negocio": "Aguardando avaliação", "qtd_planos": 1}
    ]


def test_f1_concluido_sem_pendencia_continua_fora():
    rows = [_plano("P1", "CONCLUIDO"), _consolidacao("P1", "AVALIADO")]
    assert calculate("G01", rows) == []


def test_f1_filtro_padrao_do_a1_inclui_concluido_pendente():
    filtro = _script().FILTRO_UNIVERSO_PADRAO
    assert "pt.status = 'CONCLUIDO' AND c.qtd_aguardando_avaliacao > 0" in filtro


def test_metamorfico_plano_cancelado_nao_altera_painel_padrao():
    base = [_plano("P1", "ATIVO"), _consolidacao("P1", "INCLUIDO")]
    com_cancelado = base + [_plano("P2", "CANCELADO"), _consolidacao("P2", "CONCLUIDO")]
    assert calculate("G01", base) == calculate("G01", com_cancelado)


def test_f3_responsavel_resolvido_sem_join_na_trilha_bruta():
    sql = _script().SQL_IND_GEST_01
    assert "responsavel AS (" in sql
    assert "GROUP BY sj.plano_trabalho_id, sj.codigo, sj.created_at" in sql
    assert "sjr" not in sql


def test_f7_data_posterior_a_fotografia_nao_gera_dias_negativos():
    dias = _script().dias_parado
    assert dias("2026-09-10T08:00:00", date(2026, 9, 13)) == "3"
    assert dias("2026-09-20T08:00:00", date(2026, 9, 13)) == ""


def test_f5_extrator_do_oracle_usa_o_universo_do_a1():
    from lib.validation_extractors import SQL
    sql = SQL["pt_status_planos"]
    assert "JOIN petrvs_icmbio_usuarios us" in sql
    assert "LEFT JOIN petrvs_icmbio_unidades" not in sql


def test_formula_version_d17():
    assert TARGETS["G01"].formula_version == "4.0.0"
    assert REGISTRY["status-pt"].invariants == TARGETS["G01"].invariants


def test_a2_da_gestao_e_buscado_pelo_produto():
    from lib.validation_runner import _a2_pattern
    target = TARGETS["G01"]
    contract = target.outputs[0]
    assert _a2_pattern(target, contract, "restrito") == "IND_GEST_01.2_painel_restrito_*.csv"
    assert _a2_pattern(target, contract, "ambos") == "IND_GEST_01.2_painel_restrito_*.csv"
    assert _a2_pattern(target, contract, "compartilhavel") == "IND_GEST_01.2_painel_compartilhavel_*.csv"
    ocde = TARGETS["I02"]
    assert _a2_pattern(ocde, ocde.outputs[0], "compartilhavel") == ocde.outputs[0].pattern


def test_celula_suprimida_nao_conta_como_divergencia():
    from lib.validation_runner import _compare
    target = TARGETS["G01"]
    oracle = [{"unidade_sigla": "U1", "status_negocio": "Rascunho", "qtd_planos": 3}]
    suprimido = [{"unidade_sigla": "U1", "status_negocio": "Rascunho", "qtd_planos": "SUPRIMIDO_K"}]
    errado = [{"unidade_sigla": "U1", "status_negocio": "Rascunho", "qtd_planos": "4"}]
    assert _compare(target, target.outputs[0], suprimido, oracle) == []
    assert _compare(target, target.outputs[0], errado, oracle)
