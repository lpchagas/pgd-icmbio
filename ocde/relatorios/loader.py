"""loader.py — Carregamento e normalização dos CSVs dos indicadores OCDE/ICMBio."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
ENTREGAS_BASE = ROOT / "artefatos_local" / "ocde" / "entregas"


def periodo_sort_key(label: str) -> tuple[int, int]:
    """Converte rótulo de período em (ano, mes) para ordenação cronológica.

    Suporta: T1-2025 (trimestral), M03-2026 (mensal), Q2-2026 (quadrimestral).
    """
    parts = label.split("-")
    try:
        year = int(parts[-1])
        prefix = parts[0]
        if prefix.startswith("T"):
            return (year, (int(prefix[1:]) - 1) * 3 + 1)
        if prefix.startswith("M"):
            return (year, int(prefix[1:]))
        if prefix.startswith("Q"):
            return (year, (int(prefix[1:]) - 1) * 4 + 1)
    except (ValueError, IndexError):
        pass
    return (9999, 0)

# Colunas numéricas por indicador (chave "01v1" = I01 variante v1)
_NUM: dict[str, list[str]] = {
    "01v1": ["proporcao_perc"],
    "01v2": ["proporcao_na_unidade_perc", "total_servidores"],
    "02":   ["taxa_cumprimento_perc", "total_cadastradas", "total_concluidas",
             "total_no_ciclo", "total_em_plano_avaliado"],
    "03":   ["taxa_atingimento_perc", "meta_planejada", "meta_executada",
             "progresso_esperado", "progresso_realizado"],
    "04":   ["score_atingimento_perc", "total_cadastradas", "total_no_ciclo"],
    "05":   ["qtd_entregas_por_servidor", "media_entregas_por_servidor_unidade",
             "total_entregas_unidade", "total_servidores_unidade"],
    "06":   ["pct_categoria", "total_entregas_na_categoria", "total_entregas_unidade"],
    "07":   ["total_horas_planejadas_entrega", "num_servidores_alocados",
             "carga_horaria_periodo"],
    "08":   ["proporcao_horas_perc", "horas_planejadas_entrega",
             "total_horas_disponiveis_unidade"],
    "09":   ["media_nota_pt", "total_avaliacoes_pt",
             "qtd_nota_1", "qtd_nota_2", "qtd_nota_3", "qtd_nota_4", "qtd_nota_5"],
    "10":   ["perc_inadequado", "qtd_inadequado", "total_avaliacoes_pt"],
    "11":   ["perc_excepcional", "qtd_excepcional", "total_avaliacoes_pt"],
    "12":   ["media_nota_pt", "media_nota_pe", "diferenca_absoluta", "diferenca_direcional"],
}


def find_mes_dir(mes: Optional[str] = None) -> Path:
    """Retorna a pasta do mês solicitado (ou o mais recente disponível)."""
    if mes:
        d = ENTREGAS_BASE / mes
        if not d.exists():
            raise FileNotFoundError(f"Pasta não encontrada: {d}")
        return d
    meses = sorted(d for d in ENTREGAS_BASE.iterdir()
                   if d.is_dir() and d.name[:4].isdigit())
    if not meses:
        raise FileNotFoundError(f"Nenhuma pasta de mês em {ENTREGAS_BASE}")
    return meses[-1]


def load_ind(mes_dir: Path, ind: str, variant: str = "") -> Optional[pd.DataFrame]:
    """Carrega o CSV mais recente do indicador `ind`. `variant`: 'v1' ou 'v2' para I01."""
    # Aceita IND_OCDE_XX (atual) e IND_XX (entregas anteriores a 13.09.2026).
    # A ordenação por nome coloca o prefixo legado antes do atual, de modo que
    # o último elemento é sempre a geração mais nova disponível.
    files = sorted(
        set(mes_dir.glob(f"IND_{ind}.*.csv")) | set(mes_dir.glob(f"IND_OCDE_{ind}.*.csv"))
    )
    if variant:
        files = [f for f in files if variant in f.name]
    if not files:
        return None
    df = pd.read_csv(files[-1], sep="|", encoding="utf-8-sig", low_memory=False)
    key = ind + variant
    for col in _NUM.get(key, _NUM.get(ind, [])):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def filter_unidade(df: pd.DataFrame, unidade: Optional[str]) -> pd.DataFrame:
    """Filtra por sigla de unidade (regex, case-insensitive)."""
    if not unidade or "unidade_sigla" not in df.columns:
        return df
    mask = df["unidade_sigla"].str.upper().str.contains(
        unidade.upper(), na=False, regex=True
    )
    result = df[mask]
    if result.empty:
        print(f"[Aviso] Unidade '{unidade}' não encontrada — usando dados nacionais.",
              file=sys.stderr)
        return df
    return result


def periodos_encerrados(df: pd.DataFrame) -> pd.DataFrame:
    """Retorna apenas linhas de períodos encerrados."""
    if "periodo_status" in df.columns:
        return df[df["periodo_status"] == "encerrado"].copy()
    return df.copy()


def ultimo_periodo_encerrado(df: pd.DataFrame) -> str:
    """Retorna o rótulo do último período encerrado no DataFrame (ordem cronológica)."""
    enc = periodos_encerrados(df)
    if enc.empty or "periodo" not in enc.columns:
        return ""
    return sorted(enc["periodo"].unique(), key=periodo_sort_key)[-1]


def dois_ultimos_periodos(df: pd.DataFrame) -> tuple[str, str]:
    """Retorna (penúltimo, último) período encerrado (cronológico). Se só há um, retorna ("", ultimo)."""
    enc = periodos_encerrados(df)
    if enc.empty or "periodo" not in enc.columns:
        return "", ""
    pers = sorted(enc["periodo"].unique(), key=periodo_sort_key)
    if len(pers) == 1:
        return "", pers[-1]
    return pers[-2], pers[-1]
