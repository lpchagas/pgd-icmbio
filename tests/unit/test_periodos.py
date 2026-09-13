from datetime import date
import os
from pathlib import Path

import pytest

from lib.denodo_config import platform_path
from lib.periodos import analysis_window, build_periods, build_periods_pe, build_periods_pt, period_metadata

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
