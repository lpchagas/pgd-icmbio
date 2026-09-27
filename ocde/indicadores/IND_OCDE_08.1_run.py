"""IND_OCDE_08.1_run.py — I08: Proporção de Horas por Entrega — Planejadas (%).

Instrumento: misto PT + PE — ciclo alinhado ao Plano de Entregas (PE).
Periodicidade: 2025 trimestral (T3–T4) | 2026+ quadrimestral (Q1–Q3). Base: 01/07/2025.

Calcula qual percentual da capacidade planejada de uma unidade foi alocado a
cada entrega. Responde: "Qual o peso relativo de cada entrega no esforço total
planejado da unidade?"

Decisão CGOV D10 (13.09.2026) — dupla perspectiva:
  Quando servidores de áreas diferentes colaboram na mesma entrega, dividir
  horas de uma unidade pela capacidade de outra produz um número sem
  significado. O indicador passa a emitir duas visões separadas e
  matematicamente coerentes, cada uma com numerador e denominador da mesma
  unidade:

    v1 — visão da unidade DONA do Plano de Entregas:
         horas alocadas às entregas que a unidade planejou (venham de onde
         vierem os executores) ÷ capacidade da própria unidade dona.
         Responde: quanto as entregas desta unidade consomem do tamanho dela.

    v2 — visão da unidade EXECUTORA do Plano de Trabalho:
         horas que os PTs da unidade dedicaram a entregas (de quem quer que
         sejam) ÷ capacidade da própria unidade executora.
         Responde: quanto desta unidade está comprometido com cada entrega.

  A coluna `proporcao_horas_perc` da v1 preserva o nome histórico, para não
  quebrar os painéis da COCAGE.

Decisão CGOV D09 (13.09.2026) — dias úteis institucionais:
  O rateio usa dias úteis, não dias corridos. Como o Denodo/VQL não os calcula,
  a consulta devolve linhas atômicas e a agregação acontece em Python, com
  lib.calendario — mesma abordagem do I07.

Denominador (capacidade da unidade): soma das horas proporcionais de todos os
PTs ativos cuja unidade é aquela, inclusive os sem entrega vinculada. Por isso
vem de consulta própria (SQL_I08_CAPACIDADE), espelhando o extractor
pt_capacidade_unidade que alimenta o oracle A3.

Correções anteriores preservadas (14.06.2026):
  1. A entrega é atribuída à unidade dona do PE, com fallback para a do PT.
  2. Filtro temporal do PE elimina entregas de ciclos anteriores.
  3. Prefixos petrvs_icmbio_ em todas as tabelas físicas (compatibilidade JDBC).

Nota: a proporção pode superar 100% quando algum vínculo tem forca_trabalho
acima de 100% — dado inválido no PETRVS, sinalizado pelo aviso de qualidade.
"""
from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
import sys

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "lib" / "__init__.py").exists())
sys.path.insert(0, str(ROOT))

from lib.arredondamento import arredondar  # D24: meio para cima
from lib.calendario import dias_uteis
from lib.csv_utils import indicator_csv_dir, write_pipe_csv
from lib.denodo_config import connect, get_config
from lib.estrutura_organizacional import insert_mesogrupo_column, load_mesogrupo_lookup
from lib.monthly_runner import query_rows
from lib.periodos import analysis_window, build_periods_pe, period_metadata

# Linhas atômicas por (entrega × plano de trabalho), carregando a unidade dona
# e a executora — as duas visões da D10 saem do mesmo universo.
SQL_I08 = """
WITH parametros AS (
    SELECT
        CAST('{ini}' AS DATE) AS data_inicio,
        CAST('{fim}' AS DATE) AS data_fim,
        0                     AS incluir_excluidos
)
SELECT
    COALESCE(dono.sigla, 'N.I.')     AS unidade_dona_sigla,
    COALESCE(dono.nome,  'N.I.')     AS unidade_dona_nome,
    COALESCE(exec.sigla, 'N.I.')     AS unidade_executora_sigla,
    COALESCE(exec.nome,  'N.I.')     AS unidade_executora_nome,
    pte.plano_entrega_entrega_id     AS id_entrega,
    COALESCE(
        NULLIF(TRIM(COALESCE(pee.descricao,         '')), ''),
        NULLIF(TRIM(COALESCE(pee.descricao_entrega, '')), ''),
        'N.I.'
    )                                AS nome_entrega,
    pt.id                            AS plano_trabalho_id,
    pt.carga_horaria,
    pt.forma_contagem_carga_horaria,
    CAST(pt.data_inicio AS DATE)     AS plano_inicio,
    CAST(pt.data_fim    AS DATE)     AS plano_fim,
    CAST(CASE WHEN CAST(pt.data_inicio AS DATE) > p.data_inicio
              THEN pt.data_inicio ELSE p.data_inicio END AS DATE) AS sobreposicao_inicio,
    CAST(CASE WHEN CAST(pt.data_fim AS DATE) < p.data_fim
              THEN pt.data_fim ELSE p.data_fim END AS DATE)       AS sobreposicao_fim,
    COALESCE(pte.forca_trabalho, 0)  AS forca_trabalho
FROM petrvs_icmbio_planos_trabalhos pt
JOIN petrvs_icmbio_planos_trabalhos_entregas pte
    ON pte.plano_trabalho_id = pt.id
   AND pte.deleted_at IS NULL
   AND pte.plano_entrega_entrega_id IS NOT NULL
LEFT JOIN petrvs_icmbio_planos_entregas_entregas pee
    ON pee.id = pte.plano_entrega_entrega_id
   AND pee.deleted_at IS NULL
LEFT JOIN petrvs_icmbio_planos_entregas pe
    ON pe.id = pee.plano_entrega_id
   AND pe.deleted_at IS NULL
LEFT JOIN petrvs_icmbio_unidades dono
    ON dono.id = COALESCE(pe.unidade_id, pt.unidade_id)
LEFT JOIN petrvs_icmbio_unidades exec
    ON exec.id = pt.unidade_id
CROSS JOIN parametros p
WHERE (p.incluir_excluidos = 1 OR pt.deleted_at IS NULL)
  AND pt.carga_horaria IS NOT NULL
  AND pt.carga_horaria > 0
  AND CAST(pt.data_inicio AS DATE) <= p.data_fim
  AND CAST(pt.data_fim   AS DATE) >= p.data_inicio
  AND pe.id IS NOT NULL
  AND CAST(pe.data_inicio AS DATE) <= p.data_fim
  AND CAST(pe.data_fim   AS DATE) >= p.data_inicio
"""

# Capacidade por unidade: todos os PTs ativos da unidade, inclusive os sem
# entrega vinculada. Denominador das duas visões.
SQL_I08_CAPACIDADE = """
WITH parametros AS (
    SELECT
        CAST('{ini}' AS DATE) AS data_inicio,
        CAST('{fim}' AS DATE) AS data_fim,
        0                     AS incluir_excluidos
)
SELECT
    COALESCE(un.sigla, 'N.I.')   AS unidade_sigla,
    pt.id                        AS plano_trabalho_id,
    pt.carga_horaria,
    pt.forma_contagem_carga_horaria,
    CAST(pt.data_inicio AS DATE) AS plano_inicio,
    CAST(pt.data_fim    AS DATE) AS plano_fim,
    CAST(CASE WHEN CAST(pt.data_inicio AS DATE) > p.data_inicio
              THEN pt.data_inicio ELSE p.data_inicio END AS DATE) AS sobreposicao_inicio,
    CAST(CASE WHEN CAST(pt.data_fim AS DATE) < p.data_fim
              THEN pt.data_fim ELSE p.data_fim END AS DATE)       AS sobreposicao_fim
FROM petrvs_icmbio_planos_trabalhos pt
LEFT JOIN petrvs_icmbio_unidades un
    ON un.id = pt.unidade_id
   AND un.deleted_at IS NULL
CROSS JOIN parametros p
WHERE (p.incluir_excluidos = 1 OR pt.deleted_at IS NULL)
  AND pt.carga_horaria IS NOT NULL
  AND pt.carga_horaria > 0
  AND CAST(pt.data_inicio AS DATE) <= p.data_fim
  AND CAST(pt.data_fim   AS DATE) >= p.data_inicio
"""

COLUNAS_V1 = [
    "unidade_sigla", "unidade_nome", "id_entrega", "nome_entrega",
    "horas_planejadas_entrega", "total_horas_disponiveis_unidade",
    "proporcao_horas_perc",
]

COLUNAS_V2 = [
    "unidade_sigla", "unidade_nome", "id_entrega", "nome_entrega",
    "horas_executora", "capacidade_executora", "proporcao_executora_perc",
]


def _para_data(valor: object) -> date | None:
    if isinstance(valor, date):
        return valor
    if valor in (None, ""):
        return None
    try:
        return date.fromisoformat(str(valor)[:10])
    except ValueError:
        return None


def _para_float(valor: object) -> float:
    try:
        return float(str(valor).replace(",", "."))
    except (TypeError, ValueError):
        return 0.0


def horas_proporcionais(registro: dict) -> float:
    """Horas do PT dentro do período, rateadas por dias úteis (D09)."""

    inicio, fim = _para_data(registro.get("plano_inicio")), _para_data(registro.get("plano_fim"))
    sobre_ini = _para_data(registro.get("sobreposicao_inicio"))
    sobre_fim = _para_data(registro.get("sobreposicao_fim"))
    if not inicio or not fim or not sobre_ini or not sobre_fim:
        return 0.0
    base = _para_float(registro.get("carga_horaria"))
    if str(registro.get("forma_contagem_carga_horaria") or "").upper() == "DIAS":
        base *= 8.0
    denominador = dias_uteis(inicio, fim)
    if not denominador:
        return 0.0
    return base * dias_uteis(sobre_ini, sobre_fim) / denominador


def horas_alocadas(registro: dict) -> float:
    """Parcela das horas do PT atribuída a uma entrega, pela força de trabalho."""

    return horas_proporcionais(registro) * _para_float(registro.get("forca_trabalho")) / 100.0


def capacidades(columns: list[str], rows: list[list]) -> dict[str, float]:
    """Capacidade total por unidade — cada plano de trabalho conta uma vez."""

    total: dict[str, float] = {}
    vistos: set[tuple[str, str]] = set()
    for row in rows:
        registro = dict(zip(columns, row))
        unidade = str(registro.get("unidade_sigla", "N.I."))
        chave = (unidade, str(registro.get("plano_trabalho_id")))
        if chave in vistos:
            continue
        vistos.add(chave)
        total[unidade] = total.get(unidade, 0.0) + horas_proporcionais(registro)
    return total


def _agregar_visao(
    columns: list[str],
    rows: list[list],
    capacidade: dict[str, float],
    sigla_col: str,
    nome_col: str,
) -> list[list]:
    """Agrega horas por (unidade, entrega) sob uma das duas perspectivas da D10.

    D25: o vínculo plano de trabalho × entrega conta uma vez; vínculos repetidos no
    PETRVS são ignorados no cálculo e contados como alerta de qualidade.
    """

    acumulado: dict[tuple[str, str, str, str], float] = {}
    vistos: set[tuple] = set()
    duplicados = 0
    for row in rows:
        registro = dict(zip(columns, row))
        chave = (
            str(registro.get(sigla_col, "N.I.")),
            str(registro.get(nome_col, "N.I.")),
            str(registro.get("id_entrega", "")),
            str(registro.get("nome_entrega", "N.I.")),
        )
        vinculo = (chave, str(registro.get("plano_trabalho_id")))
        if vinculo in vistos:
            duplicados += 1
            continue
        vistos.add(vinculo)
        acumulado[chave] = acumulado.get(chave, 0.0) + horas_alocadas(registro)
    if duplicados:
        print(f"  ALERTA_QUALIDADE (D25): {duplicados} vínculo(s) plano de trabalho × entrega repetido(s) ignorado(s) na visão {sigla_col}.")

    agregadas = []
    for (sigla, nome, id_entrega, nome_entrega), horas in acumulado.items():
        disponivel = capacidade.get(sigla, 0.0)
        agregadas.append([
            sigla, nome, id_entrega, nome_entrega,
            arredondar(horas, 2), arredondar(disponivel, 2),
            arredondar(100.0 * horas / disponivel, 2) if disponivel else 0.0,
        ])
    agregadas.sort(key=lambda linha: (linha[0], -linha[6]))
    return agregadas


def main() -> None:
    config = get_config(require_credentials=True)
    conn = connect(config)
    out_dir = indicator_csv_dir()
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_v1 = out_dir / f"IND_OCDE_08.2_v1_proporcao_horas_dona_{stamp}.csv"
    output_v2 = out_dir / f"IND_OCDE_08.2_v2_proporcao_horas_executora_{stamp}.csv"

    window = analysis_window()
    periods = build_periods_pe(window.fim)
    meta_cols = period_metadata()
    cols_v1 = meta_cols + COLUNAS_V1
    cols_v2 = meta_cols + COLUNAS_V2
    rows_v1: list[list] = []
    rows_v2: list[list] = []

    try:
        for label, kind, start, scheduled_end, end, status in periods:
            print(f"Executando I08 {label} ({start} a {end})...")
            try:
                cap_cols, cap_rows = query_rows(
                    conn,
                    SQL_I08_CAPACIDADE.replace("{ini}", str(start)).replace("{fim}", str(end)),
                )
                columns, rows = query_rows(
                    conn, SQL_I08.replace("{ini}", str(start)).replace("{fim}", str(end))
                )
            except Exception as exc:
                # D33: falha em qualquer período interrompe o A1 sem gravar A2 parcial.
                raise SystemExit(f"ERRO: I08 {label}: {exc}") from exc

            capacidade = capacidades(cap_cols, cap_rows)
            meta = [kind, label, str(start), str(scheduled_end), str(end), status,
                    (end - start).days + 1]
            dona = _agregar_visao(
                columns, rows, capacidade, "unidade_dona_sigla", "unidade_dona_nome"
            )
            executora = _agregar_visao(
                columns, rows, capacidade, "unidade_executora_sigla", "unidade_executora_nome"
            )
            rows_v1.extend(meta + linha for linha in dona)
            rows_v2.extend(meta + linha for linha in executora)
            print(f"  {len(rows)} vinculos -> {len(dona)} linhas (dona) "
                  f"| {len(executora)} linhas (executora).")
    finally:
        conn.close()

    if not rows_v1:
        print("Nenhum dado retornado. CSV nao gerado.")
        return

    lookup = load_mesogrupo_lookup()
    for output, cols, rows, rotulo in (
        (output_v1, cols_v1, rows_v1, "unidade dona do PE"),
        (output_v2, cols_v2, rows_v2, "unidade executora do PT"),
    ):
        csv_cols, csv_rows = insert_mesogrupo_column(cols, rows, lookup)
        write_pipe_csv(output, csv_cols, csv_rows)
        print(f"Arquivo salvo ({rotulo}): {output}")

    # Busca por nome, nao por offset fixo: a insercao de colunas novas
    # deslocava as posicoes e quebrava os avisos (ver CGOV D09/D11).
    cols = cols_v1
    offset_perc = cols.index("proporcao_horas_perc")
    offset_status = cols.index("periodo_status")
    acima_100 = sum(1 for r in rows_v1 if _para_float(r[offset_perc]) > 100.0)
    if acima_100:
        print(f"  AVISO: {acima_100} entrega(s) com proporcao > 100% — verificar forca_trabalho no PETRVS.")

    parciais = sum(1 for r in rows_v1 if str(r[offset_status]) == "parcial_no_corte")
    if parciais:
        print(f"  AVISO: {parciais} linha(s) de ciclos parciais no corte — resultados preliminares.")


if __name__ == "__main__":
    main()
