import json
from datetime import date
from pathlib import Path

from gestao.execucao_entregas import build_g02, shared_rows
from lib.periodos import build_periods_pe
from lib.validation_oracles import calculate


FIXTURES = Path(__file__).parents[1] / "fixtures" / "validation"


def atomic():
    return json.loads((FIXTURES / "g02_atomic.json").read_text(encoding="utf-8"))


def production_result():
    rows = atomic()
    grouped = {name: [row for row in rows if row["_extractor"] == name] for name in {row["_extractor"] for row in rows}}
    return build_g02(
        grouped["g02_entregas"], grouped["g02_progressos"], grouped["g02_planos"],
        grouped["g02_vinculos"], grouped["g02_atividades"], build_periods_pe(date(2026, 8, 31)),
        history_cutoff=date(2026, 8, 31), observation_date=date(2026, 9, 13),
    )


def test_g02_producao_e_oracle_independente_concordam():
    main, _, _ = production_result()
    assert main == calculate("G02", atomic())


def test_g02_exclui_evento_apos_corte_e_sanitiza_texto():
    _, history, _ = production_result()
    assert "2026-09-01" not in {row["data_progresso"] for row in history}
    assert all("\n" not in row["registro_execucao"] for row in history)


def test_g02_preserva_dona_e_executora_interunidades():
    main, _, _ = production_result()
    row = next(row for row in main if row["id_entrega"] == "e1" and row["visao"] == "executora")
    assert (row["unidade_dona_sigla"], row["unidade_executora_sigla"]) == ("CGOV", "GR2")


def test_g02_cobre_servidor_sem_vinculo():
    main, _, nominal = production_result()
    assert {row["id_servidor"] for row in nominal} == {"s1", "s2"}
    assert any(row["situacao_cobertura"] == "PT_SEM_ENTREGA" for row in main)


def test_g02_deduplica_servidor_com_dois_planos():
    main, _, _ = production_result()
    rows = [row for row in main if row["unidade_executora_sigla"] == "GR2" and row["id_entrega"] in {"e1", "e2"}]
    assert all(row["total_servidores"] == 1 for row in rows)


def test_g02_compartilhavel_suprime_escopo_menor_que_cinco():
    main, _, _ = production_result()
    assert shared_rows(main, eligible_servers=3) == []


def test_g02_nao_cria_score_sintetico():
    main, _, _ = production_result()
    assert all(not any("score" in key for key in row) for row in main)
