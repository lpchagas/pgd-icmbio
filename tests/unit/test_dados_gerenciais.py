import csv
from datetime import date

import pytest

from lib.periodos import analysis_window
from ocde.relatorios.dados_gerenciais import cumulative_summary, load_indicator, temporal_summary
from ocde.relatorios.registros_execucao import SQL_PE, SQL_PT

pytestmark = pytest.mark.unit


def test_setembro_exclui_q3_e_m09(tmp_path):
    path = tmp_path / "IND_02.2_teste.csv"
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=[
            "periodo", "periodo_inicio", "periodo_fim", "periodo_status", "total_no_ciclo", "total_concluidas"
        ], delimiter="|")
        writer.writeheader()
        writer.writerow({"periodo": "Q2-2026", "periodo_inicio": "2026-05-01", "periodo_fim": "2026-08-31", "periodo_status": "encerrado", "total_no_ciclo": 10, "total_concluidas": 8})
        writer.writerow({"periodo": "Q3-2026", "periodo_inicio": "2026-09-01", "periodo_fim": "2026-12-31", "periodo_status": "em_andamento", "total_no_ciclo": 10, "total_concluidas": 1})
    loaded = load_indicator(path, "02", analysis_window(date(2026, 9, 11)))
    assert [row["periodo"] for row in loaded.rows] == ["Q2-2026"]
    assert loaded.excluded_outside_window == 1


def test_k_menor_que_cinco_suprime_todo_painel():
    people = [
        {"id_servidor": str(item), "periodo_inicio": "2026-01-01", "periodo_fim": "2026-01-31"}
        for item in range(4)
    ]
    summary = cumulative_summary({"05": people})
    assert all(row["situacao_divulgacao"] == "suprimido_k" for row in summary)


def test_avaliacao_temporal_usa_servidores_avaliados_e_nao_total_do_escopo():
    people = [
        {"id_servidor": str(item), "periodo_inicio": "2026-05-01", "periodo_fim": "2026-05-31"}
        for item in range(10)
    ]
    evaluations = [
        {
            "periodo": "M05-2026", "periodo_inicio": "2026-05-01", "periodo_fim": "2026-05-31",
            "unidade_sigla": unit, "total_avaliacoes_pt": "3",
            "total_servidores_avaliados": "3", "media_nota_pt": "4.0",
        }
        for unit in ("U1", "U2")
    ]
    i09 = next(row for row in temporal_summary({"05": people, "09": evaluations}) if row["indicador"] == "I09")
    assert i09["situacao_divulgacao"] == "suprimido_k"
    assert i09["resultado"] == "Suprimido (k<5)"


def test_avaliacao_temporal_publica_com_cinco_servidores_avaliados():
    people = [
        {"id_servidor": str(item), "periodo_inicio": "2026-06-01", "periodo_fim": "2026-06-30"}
        for item in range(10)
    ]
    evaluations = [{
        "periodo": "M06-2026", "periodo_inicio": "2026-06-01", "periodo_fim": "2026-06-30",
        "total_avaliacoes_pt": "5", "total_servidores_avaliados": "5", "media_nota_pt": "4.0",
    }]
    i09 = next(row for row in temporal_summary({"05": people, "09": evaluations}) if row["indicador"] == "I09")
    assert i09["situacao_divulgacao"] == "publicado"
    assert i09["resultado"] == "4.0"


def test_avaliacao_acumulada_usa_maior_cobertura_de_um_ciclo_sem_somar_pessoas():
    people = [
        {"id_servidor": str(item), "periodo_inicio": "2026-05-01", "periodo_fim": "2026-06-30"}
        for item in range(10)
    ]
    evaluations = [
        {"periodo": period, "total_avaliacoes_pt": "3", "total_servidores_avaliados": "3", "media_nota_pt": "4.0"}
        for period in ("M05-2026", "M06-2026")
    ]
    i09 = next(row for row in cumulative_summary({"05": people, "09": evaluations}) if row["indicador"] == "I09")
    assert i09["situacao_divulgacao"] == "suprimido_k"


def test_estado_pe_parcial_sem_historico_fica_indisponivel():
    people = [
        {"id_servidor": str(item), "periodo_inicio": "2026-09-01", "periodo_fim": "2026-09-30"}
        for item in range(5)
    ]
    pe = [{
        "periodo": "Q3-2026", "periodo_inicio": "2026-09-01", "periodo_fim_efetivo": "2026-09-30",
        "periodo_status": "parcial_no_corte", "total_no_ciclo": "10", "total_concluidas": "9",
    }]
    rows = temporal_summary({"02": pe, "05": people})
    i02 = next(row for row in rows if row["indicador"] == "I02")
    assert i02["resultado"] == "N/D"
    assert "histórico" in i02["medida"]


def test_atividades_usam_tres_datas_de_referencia_independentes():
    assert "COALESCE(a.data_entrega, a.data_inicio, a.data_distribuicao)" not in SQL_PT
    for field in ("data_distribuicao", "data_inicio", "data_entrega"):
        assert f"CAST(a.{field} AS DATE) BETWEEN" in SQL_PT
    assert "a.status = 'CONCLUIDO'" in SQL_PT
    assert "AND CAST(a.data_entrega AS DATE) BETWEEN" in SQL_PT


def test_consolidacoes_usam_conclusao_e_avaliacao_ate_o_corte():
    assert "CAST(c.data_conclusao AS DATE) BETWEEN" in SQL_PT
    assert "MIN(CAST(av.data_avaliacao AS DATE)) AS primeira_avaliacao" in SQL_PT
    assert "ac.primeira_avaliacao > CAST('{fim}' AS DATE)" in SQL_PT


def test_status_pt_atual_so_e_usado_quando_plano_terminou_ate_o_corte():
    assert "AS pt_status_elegiveis" in SQL_PT
    assert "fim <= CAST('{fim}' AS DATE) AND status = 'CONCLUIDO'" in SQL_PT


def test_transicoes_cobrem_quatro_artefatos_pela_data_do_evento():
    assert "sj.plano_entrega_id" in SQL_PE
    for field in ("plano_trabalho_id", "plano_trabalho_consolidacao_id", "atividade_id"):
        assert f"sj.{field}" in SQL_PT
    assert SQL_PE.count("CAST(sj.created_at AS DATE) BETWEEN") == 1
    assert SQL_PT.count("CAST(sj.created_at AS DATE) BETWEEN") == 3
