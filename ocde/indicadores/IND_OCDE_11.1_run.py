"""IND_OCDE_11.1_run.py — I11: Percentual de Avaliações Excepcionais por Unidade.

Instrumento: Plano de Trabalho (PT).
Periodicidade: 2025 trimestral (T3–T4) | 2026+ mensal (M01–M12). Base: 01/07/2025.

Correção de escala (12.06.2026): o SQL original usava sequencia=5 para identificar
"Excepcional", mas sequencia=5 é "Não executado" no banco ICMBio. Resultado incorreto:
~0,02% de Excepcionais (apenas 4–9 registros em 35.000+).

Mapeamento correto da escala ICMBio (confirmado 12.06.2026):
  sequencia=1 → Excepcional     ← critério correto para I11
  sequencia=2 → Alto desempenho
  sequencia=3 → Adequado
  sequencia=4 → Inadequado
  sequencia=5 → Não executado

Resultado após correção: 9,23% de Excepcionais (1.922/20.812 em 2025).
Perfil ICMBio confirmado: 9% Excepcional + 71% Alto desempenho + 20% Adequado + 0,2% Inadequado.
BAV-AIUABA (6 avaliações, todas seq=2) e ACADEBIO (sem seq=1 em 2025) confirmados.

Interpretação: perc_excepcional >= 40% deve ser cruzado com I12 para distinguir
excelência genuína de leniência avaliativa (PT >> PE).
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "lib" / "__init__.py").exists())
sys.path.insert(0, str(ROOT))

from lib.csv_utils import indicator_csv_dir, write_pipe_csv
from lib.denodo_config import connect, get_config
from lib.estrutura_organizacional import insert_mesogrupo_column, load_mesogrupo_lookup
from lib.monthly_runner import query_rows
from lib.periodos import analysis_window, build_periods_pt, period_metadata

# D12 (CGOV, 13.09.2026): abaixo deste volume de avaliacoes o percentual e
# estatisticamente fragil. O indicador nao suprime a linha — exporta a
# volumetria para que o BI da COCAGE decida ocultar ou cinzentar a unidade.
VOLUME_MINIMO_AVALIACOES = 5

SQL_I11 = """
WITH parametros AS (
    SELECT
        CAST('{ini}' AS DATE) AS data_inicio,
        CAST('{fim}' AS DATE) AS data_fim,
        0                     AS incluir_excluidos
),
avaliacoes_pt AS (
    SELECT
        av.id          AS id_avaliacao,
        pt.unidade_id,
        pt.usuario_id  AS id_servidor,
        tan.sequencia  AS sequencia_nota
    FROM petrvs_icmbio_avaliacoes av
    JOIN petrvs_icmbio_planos_trabalhos_consolidacoes ptc
        ON ptc.id = av.plano_trabalho_consolidacao_id
    JOIN petrvs_icmbio_planos_trabalhos pt
        ON pt.id = ptc.plano_trabalho_id
    JOIN petrvs_icmbio_tipos_avaliacoes_notas tan
        ON tan.id = av.tipo_avaliacao_nota_id
    CROSS JOIN parametros p
    WHERE av.plano_trabalho_consolidacao_id IS NOT NULL
      AND (p.incluir_excluidos = 1 OR av.deleted_at IS NULL)
      AND CAST(av.data_avaliacao AS DATE) BETWEEN p.data_inicio AND p.data_fim
      AND CAST(pt.data_inicio AS DATE) <= p.data_fim
      AND CAST(pt.data_fim   AS DATE) >= p.data_inicio
      AND (p.incluir_excluidos = 1 OR pt.deleted_at IS NULL)
),
proporcao_por_unidade AS (
    SELECT
        COALESCE(un.sigla, 'N.I.')                                   AS unidade_sigla,
        COALESCE(un.nome,  'N.I.')                                   AS unidade_nome,
        COUNT(avpt.id_avaliacao)                                     AS total_avaliacoes_pt,
        COUNT(DISTINCT avpt.id_servidor)                             AS total_servidores_avaliados,
        SUM(CASE WHEN avpt.sequencia_nota = 1 THEN 1 ELSE 0 END)    AS qtd_excepcional,
        ROUND(
            SUM(CASE WHEN avpt.sequencia_nota = 1 THEN 1 ELSE 0 END) * 100.0
                / NULLIF(COUNT(avpt.id_avaliacao), 0),
            2
        )                                                            AS perc_excepcional
    FROM avaliacoes_pt avpt
    LEFT JOIN petrvs_icmbio_unidades un ON un.id = avpt.unidade_id
    GROUP BY COALESCE(un.sigla, 'N.I.'), COALESCE(un.nome, 'N.I.')
)
SELECT
    unidade_sigla,
    unidade_nome,
    total_avaliacoes_pt,
    total_servidores_avaliados,
    qtd_excepcional,
    perc_excepcional,
    CASE
        WHEN perc_excepcional >= 40 THEN 'Reconhecimento elevado'
        WHEN perc_excepcional >= 20 THEN 'Desempenho diferenciado'
        WHEN perc_excepcional >=  5 THEN 'Destaque pontual'
        ELSE 'Escala subutilizada'
    END AS nivel_reconhecimento,
    CASE WHEN total_avaliacoes_pt >= {volume_minimo} THEN 1 ELSE 0 END AS volume_suficiente
FROM proporcao_por_unidade
ORDER BY perc_excepcional DESC, unidade_sigla
"""


def _to_float(value: object) -> float:
    try:
        return float(str(value).replace(",", "."))
    except (ValueError, TypeError):
        return 0.0


def main() -> None:
    config = get_config(require_credentials=True)
    conn = connect(config)
    out_dir = indicator_csv_dir()
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    output = out_dir / f"IND_OCDE_11.2_perc_excepcional_pt_{stamp}.csv"

    window = analysis_window()
    periods = build_periods_pt(window.fim)
    meta_cols = period_metadata()
    all_cols: list[str] | None = None
    all_rows: list[list] = []

    try:
        for label, kind, start, scheduled_end, end, status in periods:
            sql = SQL_I11.replace("{ini}", str(start)).replace("{fim}", str(end)).replace(
                "{volume_minimo}", str(VOLUME_MINIMO_AVALIACOES)
            )
            print(f"Executando I11 {label} ({start} a {end})...")
            try:
                columns, rows = query_rows(conn, sql)
            except Exception as exc:
                print(f"  ERRO: {exc}")
                continue
            if all_cols is None:
                all_cols = meta_cols + columns
            duration = (end - start).days + 1
            for row in rows:
                all_rows.append([kind, label, str(start), str(scheduled_end), str(end), status, duration] + row)
            print(f"  {len(rows)} linhas retornadas.")
    finally:
        conn.close()

    if not all_rows:
        print("Nenhum dado retornado. CSV nao gerado.")
        return

    # mesogrupo so entra no CSV escrito — all_cols/all_rows seguem com as
    # posicoes originais para nao quebrar os offsets fixos usados abaixo.
    lookup = load_mesogrupo_lookup()
    csv_cols, csv_rows = insert_mesogrupo_column(all_cols or [], all_rows, lookup)

    write_pipe_csv(output, csv_cols, csv_rows)
    print(f"Arquivo salvo: {output}")

    # Colunas apos meta_cols: sigla(0) nome(1) total_av(2) total_servidores(3) qtd_exc(4) perc_exc(5) nivel(6)
    # Busca por nome, nao por offset fixo: a insercao de colunas novas
    # deslocava as posicoes e quebrava os avisos (ver CGOV D09/D11).
    cols = all_cols or []
    offset_total = cols.index("total_avaliacoes_pt")
    offset_perc = cols.index("perc_excepcional")
    offset_nivel = cols.index("nivel_reconhecimento")
    offset_status = cols.index("periodo_status")
    offset_unidade = cols.index("unidade_sigla")

    encerrados = [r for r in all_rows if r[offset_status] == "encerrado"]

    # Alerta de possivel leniencia avaliativa (perc >= 40% requer cruzamento com I12)
    leniencia = [r for r in encerrados if _to_float(r[offset_perc]) >= 40]
    if leniencia:
        unids = set(r[offset_unidade] for r in leniencia)
        print(f"  AVISO: {len(unids)} unidade(s) com perc_excepcional >= 40% em periodos encerrados"
              f" — cruzar com I12 para distinguir excelencia genuina de leniencia avaliativa.")

    # Escala subutilizada: nota maxima praticamente ausente
    subutilizadas = [r for r in encerrados if r[offset_nivel] == "Escala subutilizada"]
    if subutilizadas:
        unids = set(r[offset_unidade] for r in subutilizadas)
        print(f"  NOTA: {len(unids)} unidade(s) com 'Escala subutilizada' — nota Excepcional quase ausente.")

    # Unidades com < 5 avaliacoes (resultado fragil)
    low_count = sum(
        1 for r in encerrados
        if int(r[offset_total] or 0) < VOLUME_MINIMO_AVALIACOES
    )
    if low_count:
        print(f"  NOTA: {low_count} linha(s) com < 5 avaliacoes em periodos encerrados — percentuais frageis.")

    parciais = sum(1 for r in all_rows if r[offset_status] == "parcial_no_corte")
    if parciais:
        print(f"  NOTA: {parciais} linha(s) em ciclo parcial_no_corte — valores preliminares.")


if __name__ == "__main__":
    main()
