"""IND_OCDE_07.1_run.py — I07: Horas por Entrega — Planejadas (Absolutas).

Instrumento: misto PT + PE — ciclo alinhado ao Plano de Entregas (PE).
Periodicidade: 2025 trimestral (T3–T4) | 2026+ quadrimestral (Q1–Q3). Base: 01/07/2025.

Calcula o total de horas planejadas alocadas a cada entrega do PE, somando
a contribuição proporcional de todos os servidores cujos PTs se sobrepõem
ao período e que têm a entrega vinculada.

  horas_alocadas = carga_horaria_horas
                   × (dias_uteis_sobrepostos / dias_uteis_do_plano)
                   × (forca_trabalho / 100)

  Quando forma_contagem_carga_horaria = 'DIAS', multiplica por 8 para converter.

Decisão CGOV D09 (13.09.2026) — dias úteis institucionais:
  O rateio era feito em dias corridos, o que superestimava a capacidade em meses
  curtos ou com feriados prolongados. Como o Denodo/VQL não calcula dias úteis
  (sem DATEDIFF, sem CTE recursiva, sem calendário), a SQL passou a devolver
  linhas atômicas por (entrega × plano de trabalho) e a agregação migrou para
  Python, usando lib.calendario.dias_uteis. O shape da consulta espelha
  lib/validation_extractors.py::SQL["pt_entregas_dono"], que alimenta o oracle
  A3 — as duas devem permanecer alinhadas.

  A coluna num_servidores_alocados foi renomeada para num_planos_trabalho_alocados:
  o COUNT DISTINCT sempre foi sobre plano_trabalho_id, e um servidor com dois PTs
  na mesma entrega era contado duas vezes sob o nome antigo.

Correções aplicadas em 14.06.2026 (documentadas no CLAUDE.md):
  1. Unidade: era pt.unidade_id (servidor). Corrigido para pe.unidade_id (dono
     da entrega via COALESCE com fallback para pt.unidade_id). Isso atribui cada
     entrega à unidade que planejou o PE, não à unidade do executor.
  2. Filtro temporal do PE: faltava no CTE linhas. Sem ele, entregas de PEs de
     ciclos anteriores reapareciam em cada período (1.700 duplicatas detectadas).
     Corrigido com CROSS JOIN parametros + WHERE pe.data_inicio/fim.

Resultado do run corrigido (14.06.2026): 18.461 linhas, zero duplicatas.
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

# Linhas atômicas: uma por (entrega × plano de trabalho). O rateio por dias
# úteis e a agregação acontecem em Python — ver docstring (decisão CGOV D09).
SQL_I07 = """
WITH parametros AS (
    SELECT
        CAST('{ini}' AS DATE) AS data_inicio,
        CAST('{fim}' AS DATE) AS data_fim,
        0                     AS incluir_excluidos
)
SELECT
    COALESCE(un.sigla, 'N.I.') AS unidade_sigla,
    COALESCE(un.nome,  'N.I.') AS unidade_nome,
    pte.plano_entrega_entrega_id AS id_entrega,
    COALESCE(
        NULLIF(TRIM(COALESCE(pee.descricao,         '')), ''),
        NULLIF(TRIM(COALESCE(pee.descricao_entrega, '')), ''),
        'N.I.'
    )                          AS nome_entrega,
    pe.id                      AS id_plano_entrega,
    CAST(pe.data_inicio AS DATE) AS inicio_vigencia_plano_entrega,
    CAST(pe.data_fim    AS DATE) AS fim_vigencia_plano_entrega,
    pt.id                      AS plano_trabalho_id,
    pt.carga_horaria,
    pt.forma_contagem_carga_horaria,
    CAST(pt.data_inicio AS DATE) AS plano_inicio,
    CAST(pt.data_fim    AS DATE) AS plano_fim,
    CAST(CASE WHEN CAST(pt.data_inicio AS DATE) > p.data_inicio
              THEN pt.data_inicio ELSE p.data_inicio END AS DATE) AS sobreposicao_inicio,
    CAST(CASE WHEN CAST(pt.data_fim AS DATE) < p.data_fim
              THEN pt.data_fim ELSE p.data_fim END AS DATE)       AS sobreposicao_fim,
    COALESCE(pte.forca_trabalho, 0) AS forca_trabalho
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
LEFT JOIN petrvs_icmbio_unidades un
    ON un.id = COALESCE(pe.unidade_id, pt.unidade_id)
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

# Colunas agregadas escritas no CSV, após as colunas de período.
COLUNAS_SAIDA = [
    "unidade_sigla",
    "unidade_nome",
    "id_entrega",
    "nome_entrega",
    "id_plano_entrega",
    "inicio_vigencia_plano_entrega",
    "fim_vigencia_plano_entrega",
    "total_horas_planejadas_entrega",
    "num_planos_trabalho_alocados",
]

CHAVE = (
    "unidade_sigla", "unidade_nome", "id_entrega", "nome_entrega",
    "id_plano_entrega", "inicio_vigencia_plano_entrega", "fim_vigencia_plano_entrega",
)


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


def horas_alocadas(registro: dict) -> float:
    """Horas do plano de trabalho atribuíveis à entrega, rateadas por dias úteis."""

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
    proporcional = base * dias_uteis(sobre_ini, sobre_fim) / denominador
    return proporcional * _para_float(registro.get("forca_trabalho")) / 100.0


def agregar(columns: list[str], rows: list[list]) -> list[list]:
    """Agrega as linhas atômicas por entrega, somando horas e contando planos.

    D25: o vínculo plano de trabalho × entrega conta uma vez; vínculos repetidos no
    PETRVS são ignorados no cálculo e contados como alerta de qualidade.
    """

    acumulado: dict[tuple, dict] = {}
    vistos: set[tuple] = set()
    duplicados = 0
    for row in rows:
        registro = dict(zip(columns, row))
        chave = tuple(str(registro.get(nome, "")) for nome in CHAVE)
        vinculo = (chave, str(registro.get("plano_trabalho_id")))
        if vinculo in vistos:
            duplicados += 1
            continue
        vistos.add(vinculo)
        item = acumulado.setdefault(chave, {"horas": 0.0, "planos": set()})
        item["horas"] += horas_alocadas(registro)
        item["planos"].add(str(registro.get("plano_trabalho_id")))
    agregadas = [
        [*chave, arredondar(item["horas"], 2), len(item["planos"])]
        for chave, item in acumulado.items()
    ]
    # Mesma ordenação da versão SQL: unidade, depois horas decrescentes.
    agregadas.sort(key=lambda linha: (linha[0], -linha[7]))
    if duplicados:
        print(f"  ALERTA_QUALIDADE (D25): {duplicados} vínculo(s) plano de trabalho × entrega repetido(s) ignorado(s).")
    return agregadas


def main() -> None:
    config = get_config(require_credentials=True)
    conn = connect(config)
    out_dir = indicator_csv_dir()
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    output = out_dir / f"IND_OCDE_07.2_horas_por_entrega_{stamp}.csv"

    window = analysis_window()
    periods = build_periods_pe(window.fim)
    meta_cols = period_metadata()
    all_cols = meta_cols + COLUNAS_SAIDA
    all_rows: list[list] = []

    try:
        for label, kind, start, scheduled_end, end, status in periods:
            sql = SQL_I07.replace("{ini}", str(start)).replace("{fim}", str(end))
            print(f"Executando I07 {label} ({start} a {end})...")
            try:
                columns, rows = query_rows(conn, sql)
            except Exception as exc:
                # D33: falha em qualquer período interrompe o A1 sem gravar A2 parcial.
                raise SystemExit(f"ERRO: I07 {label}: {exc}") from exc
            agregadas = agregar(columns, rows)
            duration = (end - start).days + 1
            for row in agregadas:
                all_rows.append([kind, label, str(start), str(scheduled_end), str(end), status, duration] + row)
            print(f"  {len(rows)} vinculos -> {len(agregadas)} entregas agregadas.")
    finally:
        conn.close()

    if not all_rows:
        print("Nenhum dado retornado. CSV nao gerado.")
        return

    # mesogrupo so entra no CSV escrito — all_cols/all_rows seguem com as
    # posicoes originais para nao quebrar as buscas por nome abaixo.
    lookup = load_mesogrupo_lookup()
    csv_cols, csv_rows = insert_mesogrupo_column(all_cols, all_rows, lookup)

    write_pipe_csv(output, csv_cols, csv_rows)
    print(f"Arquivo salvo: {output}")

    # Aviso de qualidade: entregas com total_horas_planejadas_entrega = 0
    offset_horas = all_cols.index("total_horas_planejadas_entrega")
    zeros = sum(1 for r in all_rows if str(r[offset_horas]) in ("0", "0.0", "0.00"))
    if zeros:
        pct = round(zeros * 100.0 / len(all_rows), 1)
        if pct > 10:
            print(f"  ALERTA: {pct}% das entregas com total_horas_planejadas_entrega = 0 — verificar carga_horaria e forca_trabalho.")
        else:
            print(f"  Info: {zeros} entrega(s) com total_horas = 0 ({pct}%).")

    # Aviso de ciclo parcial no corte
    offset_status = all_cols.index("periodo_status")
    parciais = sum(1 for r in all_rows if str(r[offset_status]) == "parcial_no_corte")
    if parciais:
        print(f"  AVISO: {parciais} linha(s) de ciclos parciais no corte — resultados preliminares.")


if __name__ == "__main__":
    main()
