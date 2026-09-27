"""Calendário institucional — dias não úteis e contagem de dias úteis.

Criado pela decisão CGOV D09 (13.09.2026) para o rateio de capacidade do I07/I08
por dias úteis. Revisado pela **D29** (27.09.2026), que separa duas camadas:

1. **Feriados nacionais de lei** — Lei 662/1949 (01/01, 01/05, 07/09, 15/11,
   25/12), Lei 6.802/1980 (12/10), Lei 10.607/2002 (21/04 e 02/11), Lei
   14.759/2023 (20/11, Consciência Negra, desde 2024) e a Sexta-Feira da Paixão.
   A versão D09 omitia o 20/11.
2. **Pontos facultativos federais de dia inteiro** — portaria anual do MGI para a
   administração federal direta, autárquica e fundacional:
   - 2025: Portaria MGI nº 9.783/2024 (Carnaval 03 e 04/03; Corpus Christi 19/06 e
     20/06; Dia do Servidor 28/10);
   - 2026: Portaria MGI nº 11.460/2025 (Carnaval 16 e 17/02; 20/04; Corpus Christi
     04/06 e 05/06; Dia do Servidor 28/10).
   A versão D09 tratava Carnaval e Corpus Christi como feriado de lei; agora eles
   estão na camada certa.

Regras de fronteira (D29):

- meio expediente (Quarta-Feira de Cinzas até 14h; 24/12 e 31/12 após 13h) conta como
  dia útil;
- ponto facultativo condicionado a decreto local (ex.: 02/05/2025, Portaria MGI nº
  3.197/2025) fica de fora, como os feriados estaduais e municipais;
- ano sem portaria cadastrada usa o **núcleo recorrente** (Carnaval segunda e
  terça, Corpus Christi e 28/10) até a portaria ser incluída na tabela.

Nenhuma dependência externa: a tabela é versionada e reprodutível no CI.
"""
from __future__ import annotations

from datetime import date, timedelta
from functools import lru_cache


# Janela de anos coberta. Fora dela a contagem falha de forma ruidosa em vez de
# devolver silenciosamente um número de dias úteis errado.
ANO_MINIMO = 2025
ANO_MAXIMO = 2030

# (mês, dia) — feriados nacionais de lei de data fixa.
FERIADOS_FIXOS: tuple[tuple[int, int], ...] = (
    (1, 1),    # Confraternização Universal
    (4, 21),   # Tiradentes
    (5, 1),    # Dia do Trabalho
    (9, 7),    # Independência
    (10, 12),  # Nossa Senhora Aparecida
    (11, 2),   # Finados
    (11, 15),  # Proclamação da República
    (11, 20),  # Zumbi e Consciência Negra (Lei 14.759/2023)
    (12, 25),  # Natal
)

# Pontos facultativos federais de dia inteiro, por portaria anual do MGI (D29).
PONTOS_FACULTATIVOS_PORTARIA: dict[int, tuple[date, ...]] = {
    2025: (  # Portaria MGI nº 9.783/2024
        date(2025, 3, 3), date(2025, 3, 4),      # Carnaval
        date(2025, 6, 19), date(2025, 6, 20),    # Corpus Christi e dia seguinte
        date(2025, 10, 28),                      # Dia do Servidor Público Federal
    ),
    2026: (  # Portaria MGI nº 11.460/2025
        date(2026, 2, 16), date(2026, 2, 17),    # Carnaval
        date(2026, 4, 20),                       # ponto facultativo
        date(2026, 6, 4), date(2026, 6, 5),      # Corpus Christi e dia seguinte
        date(2026, 10, 28),                      # Dia do Servidor Público Federal
    ),
}


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
    """Feriados nacionais de lei do ano: os fixos e a Sexta-Feira da Paixão."""

    _validar_ano(ano)
    fixos = (date(ano, mes, dia) for mes, dia in FERIADOS_FIXOS)
    return frozenset((*fixos, pascoa(ano) - timedelta(days=2)))


@lru_cache(maxsize=None)
def pontos_facultativos_federais(ano: int) -> frozenset[date]:
    """Pontos facultativos federais de dia inteiro (portaria do MGI ou núcleo recorrente)."""

    _validar_ano(ano)
    if ano in PONTOS_FACULTATIVOS_PORTARIA:
        return frozenset(PONTOS_FACULTATIVOS_PORTARIA[ano])
    domingo = pascoa(ano)
    return frozenset((
        domingo - timedelta(days=48),  # Carnaval (segunda)
        domingo - timedelta(days=47),  # Carnaval (terça)
        domingo + timedelta(days=60),  # Corpus Christi
        date(ano, 10, 28),             # Dia do Servidor Público Federal
    ))


def dias_nao_uteis(ano: int) -> frozenset[date]:
    """Feriados de lei mais pontos facultativos federais de dia inteiro."""

    return feriados_nacionais(ano) | pontos_facultativos_federais(ano)


def eh_dia_util(dia: date) -> bool:
    """Verdadeiro para dias de segunda a sexta que não sejam feriado nem ponto facultativo."""

    return dia.weekday() < 5 and dia not in dias_nao_uteis(dia.year)


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
