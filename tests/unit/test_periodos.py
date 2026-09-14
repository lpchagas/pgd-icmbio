from datetime import date
import os
from pathlib import Path

import pytest

from lib.denodo_config import platform_path
from lib.periodos import (
    PeriodoDesconhecido,
    PeriodoIndisponivel,
    analysis_window,
    build_periods,
    build_periods_pe,
    build_periods_pt,
    default_pe_period,
    period_metadata,
    periods_pt_within,
    resolve_period,
)

pytestmark = pytest.mark.unit


def labels(periods):
    return [period[0] for period in periods]


def test_janela_setembro_2026_exata():
    window = analysis_window(date(2026, 9, 11))
    assert window.inicio == date(2025, 7, 1)
    assert window.fim == date(2026, 8, 31)
    assert window.mes_execucao == "2026-09"


@pytest.mark.parametrize(
    "execution,expected",
    [
        (date(2026, 10, 1), date(2026, 9, 30)),
        (date(2027, 1, 31), date(2026, 12, 31)),
        (date(2028, 3, 17), date(2028, 2, 29)),
    ],
)
def test_ultimo_dia_mes_anterior(execution, expected):
    assert analysis_window(execution).fim == expected


def test_execucao_antes_da_base_falha():
    with pytest.raises(ValueError):
        analysis_window(date(2025, 7, 1))


def test_pe_setembro_exclui_q3_2026():
    periods = build_periods_pe(date(2026, 8, 31))
    assert labels(periods) == ["T3-2025", "T4-2025", "Q1-2026", "Q2-2026"]
    assert all(period[5] == "encerrado" for period in periods)


def test_pt_setembro_termina_em_m08():
    periods = build_periods_pt(date(2026, 8, 31))
    assert labels(periods)[:2] == ["T3-2025", "T4-2025"]
    assert labels(periods)[-1] == "M08-2026"
    assert "M09-2026" not in labels(periods)


def test_pe_parcial_e_truncado_no_corte():
    period = build_periods_pe(date(2026, 9, 30))[-1]
    assert period == (
        "Q3-2026", "quadrimestral", date(2026, 9, 1), date(2026, 12, 31),
        date(2026, 9, 30), "parcial_no_corte",
    )


def test_pt_ciclo_mensal_no_corte_fechado():
    period = build_periods_pt(date(2026, 9, 30))[-1]
    assert period[0] == "M09-2026"
    assert period[3] == period[4] == date(2026, 9, 30)
    assert period[5] == "encerrado"


def test_inicio_fixo_e_alias():
    assert build_periods is build_periods_pe
    assert build_periods_pe(date(2027, 1, 1))[0][2] == date(2025, 7, 1)


def test_period_metadata_contrato():
    assert period_metadata() == [
        "ciclo_tipo", "periodo", "periodo_inicio", "periodo_fim",
        "periodo_fim_efetivo", "periodo_status", "duracao_dias",
    ]


@pytest.mark.skipif(os.name == "nt", reason="Conversão aplicada somente no WSL/POSIX")
def test_caminho_windows_e_convertido_para_wsl():
    assert platform_path(r"C:\Users\Pessoa\driver.jar") == Path("/mnt/c/Users/Pessoa/driver.jar")


CORTE_Q2 = date(2026, 8, 31)


class TestResolucaoDePeriodo:
    def test_q2_2026_e_o_quadrimestre_maio_agosto(self):
        spec = resolve_period("Q2-2026", analysis_end=CORTE_Q2)
        assert (spec.inicio, spec.fim, spec.fim_efetivo) == (
            date(2026, 5, 1), date(2026, 8, 31), date(2026, 8, 31))
        assert spec.ciclo_tipo == "quadrimestral"
        assert spec.status == "encerrado"
        assert spec.encerrado is True
        assert spec.duracao_dias == 123

    def test_rotulo_normalizado(self):
        assert resolve_period("  q2-2026 ", analysis_end=CORTE_Q2).rotulo == "Q2-2026"

    def test_periodo_posterior_ao_corte_e_indisponivel_nao_desconhecido(self):
        # A distinção importa: um é erro de digitação, o outro é execução cedo
        # demais — e a orientação ao operador é diferente em cada caso.
        with pytest.raises(PeriodoIndisponivel, match="posterior ao corte"):
            resolve_period("Q3-2026", analysis_end=CORTE_Q2)

    @pytest.mark.parametrize("rotulo", ["Q9-2026", "M13-2026", "X1-2026", "Q2", ""])
    def test_rotulo_fora_da_gramatica(self, rotulo):
        with pytest.raises(PeriodoDesconhecido):
            resolve_period(rotulo, analysis_end=CORTE_Q2)

    def test_periodo_anterior_a_base_oficial(self):
        with pytest.raises(PeriodoDesconhecido):
            resolve_period("Q1-2025", analysis_end=CORTE_Q2)

    def test_periodo_aberto_no_corte_e_marcado_parcial(self):
        spec = resolve_period("Q3-2026", analysis_end=date(2026, 10, 31))
        assert spec.status == "parcial_no_corte"
        assert spec.fim == date(2026, 12, 31)
        assert spec.fim_efetivo == date(2026, 10, 31)
        assert spec.encerrado is False

    def test_exigir_encerrado_recusa_periodo_aberto(self):
        with pytest.raises(PeriodoIndisponivel, match="não encerrou"):
            resolve_period("Q3-2026", analysis_end=date(2026, 10, 31), exigir_encerrado=True)

    def test_familia_explicita(self):
        assert resolve_period("T3-2025", analysis_end=CORTE_Q2, familia="pt").familia == "pt"
        assert resolve_period("T3-2025", analysis_end=CORTE_Q2).familia == "pe"
        assert resolve_period("M05-2026", analysis_end=CORTE_Q2, familia="pt").rotulo == "M05-2026"

    def test_familia_invalida(self):
        with pytest.raises(ValueError, match="família inválida"):
            resolve_period("Q2-2026", analysis_end=CORTE_Q2, familia="xx")

    def test_borda_inferior_coincide_com_a_base_oficial(self):
        assert resolve_period("T3-2025", analysis_end=CORTE_Q2).inicio == date(2025, 7, 1)

    def test_metadado_do_spec_respeita_o_contrato(self):
        spec = resolve_period("Q2-2026", analysis_end=CORTE_Q2)
        assert list(spec.as_dict()) == period_metadata()
        assert spec.as_row() == [
            "quadrimestral", "Q2-2026", "2026-05-01", "2026-08-31",
            "2026-08-31", "encerrado", "123",
        ]


class TestCiclosContidos:
    def test_quadrimestre_tem_quatro_ciclos_mensais(self):
        # RN-04: um PE quadrimestral depende de 4 ciclos mensais completos de
        # PT por servidor — nem 3, nem 5.
        spec = resolve_period("Q2-2026", analysis_end=CORTE_Q2)
        meses = periods_pt_within(spec, CORTE_Q2)
        assert [m.rotulo for m in meses] == [
            "M05-2026", "M06-2026", "M07-2026", "M08-2026"]
        assert all(m.status == "encerrado" for m in meses)
        assert all(m.familia == "pt" for m in meses)

    def test_cobertura_contigua_e_sem_sobreposicao(self):
        spec = resolve_period("Q2-2026", analysis_end=CORTE_Q2)
        meses = periods_pt_within(spec, CORTE_Q2)
        assert meses[0].inicio == spec.inicio
        assert meses[-1].fim == spec.fim
        for anterior, seguinte in zip(meses, meses[1:]):
            assert (seguinte.inicio - anterior.fim).days == 1

    def test_ano_bissexto(self):
        spec = resolve_period("Q1-2028", analysis_end=date(2028, 4, 30))
        fevereiro = [m for m in periods_pt_within(spec, date(2028, 4, 30))
                     if m.rotulo == "M02-2028"]
        assert fevereiro[0].fim == date(2028, 2, 29)

    def test_periodo_parcial_so_traz_meses_ja_fechados(self):
        spec = resolve_period("Q3-2026", analysis_end=date(2026, 10, 31))
        assert [m.rotulo for m in periods_pt_within(spec, date(2026, 10, 31))] == [
            "M09-2026", "M10-2026"]


class TestPeriodoPadrao:
    def test_execucao_em_setembro_2026_fecha_o_q2(self):
        spec = default_pe_period(CORTE_Q2)
        assert spec is not None
        assert spec.rotulo == "Q2-2026"
        assert spec.status == "encerrado"

    def test_apenas_periodos_encerrados_sao_elegiveis(self):
        assert default_pe_period(date(2026, 10, 31)).rotulo == "Q2-2026"
