"""classificador.py — Semáforos e classificação de desempenho por indicador."""
from __future__ import annotations

from typing import Optional

import pandas as pd

VERDE    = "🟢 Verde"
AMARELO  = "🟡 Amarelo"
VERMELHO = "🔴 Vermelho"
CINZA    = "⚪ N/D"

# Limiares de classificação por indicador.
# lv = limiar para Verde | la = limiar para Amarelo | maior = True (maior valor = melhor)
LIMIARES: dict[str, dict] = {
    "i02": dict(lv=80.0,  la=60.0,  maior=True),   # taxa_cumprimento_perc
    "i03": dict(lv=80.0,  la=60.0,  maior=True),   # taxa_atingimento_perc (mediana)
    "i04": dict(lv=80.0,  la=60.0,  maior=True),   # score_atingimento_perc
    "i06": dict(lv=30.0,  la=50.0,  maior=False),  # % de entregas sob 1 servidor
    "i09": dict(lv=3.5,   la=2.5,   maior=True),   # media_nota_pt (escala 1–5)
    "i10": dict(lv=5.0,   la=10.0,  maior=False),  # perc_inadequado
    "i11": dict(lv=15.0,  la=5.0,   maior=True),   # perc_excepcional
    "i12": dict(lv=90.0,  la=70.0,  maior=True),   # % unidades coerentes
}


def semaforo(valor: Optional[float], ind: str) -> str:
    """Retorna o semáforo (verde/amarelo/vermelho) para `valor` conforme limiares do indicador `ind`."""
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return CINZA
    cfg = LIMIARES.get(ind, {})
    lv   = cfg.get("lv", 80.0)
    la   = cfg.get("la", 60.0)
    maior = cfg.get("maior", True)
    if maior:
        return VERDE if valor >= lv else (AMARELO if valor >= la else VERMELHO)
    else:
        return VERDE if valor <= lv else (AMARELO if valor <= la else VERMELHO)


def semaforo_eixo1() -> str:
    """Eixo 1 é informativo — sem limiar de alerta definido."""
    return "ℹ️ Informativo"


def semaforo_eixo2(media_i02: Optional[float], media_i04: Optional[float]) -> str:
    vals = [semaforo(media_i02, "i02"), semaforo(media_i04, "i04")]
    if VERMELHO in vals:
        return VERMELHO
    if AMARELO in vals:
        return AMARELO
    if CINZA in vals and len([v for v in vals if v != CINZA]) == 0:
        return CINZA
    return VERDE


def semaforo_eixo3(media_conc_i06: Optional[float]) -> str:
    """Eixo 3 — usa I06 como indicador principal de risco (concentração de responsabilidade)."""
    return semaforo(media_conc_i06, "i06")


def semaforo_eixo4(media_i09: Optional[float],
                   perc_i10: Optional[float],
                   coer_i12: Optional[float]) -> str:
    vals = [semaforo(media_i09, "i09"),
            semaforo(perc_i10,  "i10"),
            semaforo(coer_i12,  "i12")]
    if VERMELHO in vals:
        return VERMELHO
    if AMARELO in vals:
        return AMARELO
    if all(v == CINZA for v in vals):
        return CINZA
    return VERDE


def painel_semaforo(dados: dict[str, str]) -> str:
    """Gera tabela Markdown com painel de semáforos.

    `dados`: dict {label: semaforo_str}, ex: {"Eixo 2 — Execução": "🟢 Verde"}
    """
    linhas = ["| Área | Situação |", "|---|---|"]
    for label, sem in dados.items():
        linhas.append(f"| {label} | {sem} |")
    return "\n".join(linhas) + "\n"
