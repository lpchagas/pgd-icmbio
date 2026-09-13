"""Testes do calendário institucional (decisão CGOV D09)."""
from datetime import date

import pytest

from lib.calendario import (
    ANO_MAXIMO,
    ANO_MINIMO,
    dias_uteis,
    eh_dia_util,
    feriados_nacionais,
    pascoa,
)
from lib.validation_oracles import _dias_uteis_independente

pytestmark = pytest.mark.unit


# Datas conferidas contra o calendário gregoriano publicado.
PASCOAS = {
    2025: date(2025, 4, 20),
    2026: date(2026, 4, 5),
    2027: date(2027, 3, 28),
    2028: date(2028, 4, 16),
    2029: date(2029, 4, 1),
    2030: date(2030, 4, 21),
}


@pytest.mark.parametrize("ano,esperado", sorted(PASCOAS.items()))
def test_pascoa_confere_com_o_calendario(ano, esperado):
    assert pascoa(ano) == esperado


def test_feriados_incluem_fixos_e_moveis():
    feriados = feriados_nacionais(2026)
    assert date(2026, 1, 1) in feriados      # Confraternização
    assert date(2026, 4, 21) in feriados     # Tiradentes
    assert date(2026, 12, 25) in feriados    # Natal
    assert date(2026, 2, 16) in feriados     # Carnaval (segunda)
    assert date(2026, 2, 17) in feriados     # Carnaval (terça)
    assert date(2026, 4, 3) in feriados      # Sexta-Feira Santa
    assert date(2026, 6, 4) in feriados      # Corpus Christi


def test_feriado_em_dia_de_semana_nao_e_dia_util():
    assert not eh_dia_util(date(2026, 4, 21))  # terça, Tiradentes
    assert eh_dia_util(date(2026, 4, 22))      # quarta seguinte


def test_fim_de_semana_nao_e_dia_util():
    assert not eh_dia_util(date(2026, 4, 18))  # sábado
    assert not eh_dia_util(date(2026, 4, 19))  # domingo


def test_contagem_de_um_mes_com_feriado():
    # Abril/2026: 30 dias, 22 dias de semana, menos Sexta-Feira Santa (03/04)
    # e Tiradentes (21/04).
    assert dias_uteis(date(2026, 4, 1), date(2026, 4, 30)) == 20


def test_intervalo_fechado_inclui_as_bordas():
    assert dias_uteis(date(2026, 4, 6), date(2026, 4, 6)) == 1   # segunda
    assert dias_uteis(date(2026, 4, 4), date(2026, 4, 5)) == 0   # sáb + dom


def test_intervalo_invertido_devolve_zero():
    assert dias_uteis(date(2026, 4, 30), date(2026, 4, 1)) == 0


def test_ano_fora_da_tabela_falha_de_forma_ruidosa():
    with pytest.raises(ValueError, match="fora da tabela"):
        feriados_nacionais(ANO_MAXIMO + 1)
    with pytest.raises(ValueError, match="fora da tabela"):
        dias_uteis(date(ANO_MINIMO - 1, 1, 1), date(ANO_MINIMO - 1, 12, 31))


def test_oracle_replica_a_producao_em_toda_a_janela():
    """A duplicação do cálculo no oracle é deliberada — mas deve concordar.

    lib.validation_oracles não pode importar módulos de cálculo de produção
    (tests/regression/test_validation_independence.py), então reimplementa a
    contagem de dias úteis. Este teste é a ponte entre as duas implementações.
    """
    for ano in range(ANO_MINIMO, ANO_MAXIMO + 1):
        for mes in range(1, 13):
            inicio = date(ano, mes, 1)
            # Intervalos que atravessam o fim do ano são cobertos até o limite
            # da tabela homologada; além dele a produção falha de propósito.
            fim = date(ano, 12, 31) if mes == 12 else date(ano, mes + 1, 1)
            assert dias_uteis(inicio, fim) == _dias_uteis_independente(inicio, fim), (
                f"divergência em {ano}-{mes:02d}"
            )

    # Virada de ano dentro da janela homologada.
    for ano in range(ANO_MINIMO, ANO_MAXIMO):
        inicio, fim = date(ano, 12, 15), date(ano + 1, 1, 15)
        assert dias_uteis(inicio, fim) == _dias_uteis_independente(inicio, fim)
