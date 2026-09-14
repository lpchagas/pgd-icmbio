"""Calendário institucional — feriados nacionais e contagem de dias úteis.

Criado pela decisão CGOV D09 (13.09.2026). O rateio de capacidade do I07/I08
usava dias corridos, o que superestima a força de trabalho disponível em meses
curtos ou com feriados prolongados. A partir daqui o rateio usa dias úteis.

Escopo deliberado — apenas feriados **nacionais de lei**:

  - fixos: Lei 662/1949 (01/01, 01/05, 07/09, 15/11, 25/12), Lei 6.802/1980
    (12/10 — Nossa Senhora Aparecida) e as datas acrescidas pela Lei 10.607/2002
    (21/04 — Tiradentes, 02/11 — Finados);
  - móveis derivados da Páscoa: Carnaval (segunda e terça), Sexta-Feira Santa e
    Corpus Christi.

Ficam **fora**: pontos facultativos (que não são feriado e variam por portaria
anual), feriados estaduais e municipais. Incluí-los exigiria uma tabela por
unidade organizacional, que a CGOV não deliberou; a fronteira está registrada
aqui para que a escolha seja auditável.

Nenhuma dependência externa: a lista é calculável e versionada, o que mantém o
resultado reprodutível no CI e nas fixtures sintéticas.
"""
from __future__ import annotations

from datetime import date, timedelta
from functools import lru_cache


# Janela de anos coberta pela deliberação. Fora dela a contagem falha de forma
# ruidosa em vez de devolver silenciosamente um número de dias úteis errado.
ANO_MINIMO = 2025
ANO_MAXIMO = 2030

# (mês, dia) — feriados nacionais de data fixa.
FERIADOS_FIXOS: tuple[tuple[int, int], ...] = (
    (1, 1),    # Confraternização Universal
    (4, 21),   # Tiradentes
    (5, 1),    # Dia do Trabalho
    (9, 7),    # Independência
    (10, 12),  # Nossa Senhora Aparecida
    (11, 2),   # Finados
    (11, 15),  # Proclamação da República
    (12, 25),  # Natal
)


def pascoa(ano: int) -> date:
    """Domingo de Páscoa pelo algoritmo de Meeus/Butcher (calendário gregoriano)."""

    a = ano % 19
    b, c = divmod(ano, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    j = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * j) // 451
    mes, dia = divmod(h + j - 7 * m + 114, 31)
    return date(ano, mes, dia + 1)


def _validar_ano(ano: int) -> None:
    if not ANO_MINIMO <= ano <= ANO_MAXIMO:
        raise ValueError(
            f"Ano {ano} fora da tabela de feriados homologada "
            f"({ANO_MINIMO}–{ANO_MAXIMO}). Estenda lib/calendario.py antes de usar."
        )


@lru_cache(maxsize=None)
def feriados_nacionais(ano: int) -> frozenset[date]:
    """Feriados nacionais de lei do ano, fixos e móveis."""

    _validar_ano(ano)
    domingo = pascoa(ano)
    moveis = (
        domingo - timedelta(days=48),  # Carnaval (segunda)
        domingo - timedelta(days=47),  # Carnaval (terça)
        domingo - timedelta(days=2),   # Sexta-Feira Santa
        domingo + timedelta(days=60),  # Corpus Christi
    )
    fixos = (date(ano, mes, dia) for mes, dia in FERIADOS_FIXOS)
    return frozenset((*fixos, *moveis))


def eh_dia_util(dia: date) -> bool:
    """Verdadeiro para dias de segunda a sexta que não sejam feriado nacional."""

    return dia.weekday() < 5 and dia not in feriados_nacionais(dia.year)


def dias_uteis(inicio: date, fim: date) -> int:
    """Dias úteis no intervalo fechado ``[inicio, fim]``; zero se invertido."""

    if fim < inicio:
        return 0
    _validar_ano(inicio.year)
    _validar_ano(fim.year)
    total = 0
    dia = inicio
    while dia <= fim:
        if eh_dia_util(dia):
            total += 1
        dia += timedelta(days=1)
    return total
