"""Testes do calendário institucional (decisões CGOV D09 e D29)."""
from datetime import date

import pytest

from lib.calendario import (
    ANO_MAXIMO,
    ANO_MINIMO,
    dias_uteis,
    eh_dia_util,
    feriados_nacionais,
    pascoa,
    pontos_facultativos_federais,
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


def test_feriados_de_lei_incluem_fixos_paixao_e_consciencia_negra():
    feriados = feriados_nacionais(2026)
    assert date(2026, 1, 1) in feriados      # Confraternização
    assert date(2026, 4, 21) in feriados     # Tiradentes
    assert date(2026, 11, 20) in feriados    # Consciência Negra (Lei 14.759/2023) — faltava na D09
    assert date(2026, 12, 25) in feriados    # Natal
    assert date(2026, 4, 3) in feriados      # Sexta-Feira da Paixão
    assert date(2026, 2, 16) not in feriados  # Carnaval é ponto facultativo, não feriado de lei


@pytest.mark.parametrize("ano, esperado", [
    (2025, {date(2025, 3, 3), date(2025, 3, 4), date(2025, 6, 19), date(2025, 6, 20), date(2025, 10, 28)}),
    (2026, {date(2026, 2, 16), date(2026, 2, 17), date(2026, 4, 20), date(2026, 6, 4), date(2026, 6, 5),
            date(2026, 10, 28)}),
])
def test_pontos_facultativos_seguem_as_portarias_do_mgi(ano, esperado):
    assert pontos_facultativos_federais(ano) == esperado


def test_meio_expediente_e_ponto_facultativo_local_contam_como_dia_util():
    assert eh_dia_util(date(2026, 2, 18))    # Quarta-Feira de Cinzas (até 14h)
    assert eh_dia_util(date(2026, 12, 24))   # véspera de Natal (após 13h)
    assert eh_dia_util(date(2025, 5, 2))     # 02/05/2025: só onde houve decreto local


def test_ano_sem_portaria_usa_o_nucleo_recorrente():
    # 2027: Páscoa em 28/03 → Carnaval 08 e 09/02, Corpus Christi 27/05; mais 28/10.
    assert pontos_facultativos_federais(2027) == {
        date(2027, 2, 8), date(2027, 2, 9), date(2027, 5, 27), date(2027, 10, 28)}


def test_feriado_em_dia_de_semana_nao_e_dia_util():
    assert not eh_dia_util(date(2026, 4, 21))  # terça, Tiradentes
    assert eh_dia_util(date(2026, 4, 22))      # quarta seguinte


def test_fim_de_semana_nao_e_dia_util():
    assert not eh_dia_util(date(2026, 4, 18))  # sábado
    assert not eh_dia_util(date(2026, 4, 19))  # domingo


def test_contagem_de_um_mes_com_feriado():
    # Abril/2026: 30 dias, 22 dias de semana, menos Sexta-Feira da Paixão (03/04),
    # o ponto facultativo de 20/04 e Tiradentes (21/04).
    assert dias_uteis(date(2026, 4, 1), date(2026, 4, 30)) == 19


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
