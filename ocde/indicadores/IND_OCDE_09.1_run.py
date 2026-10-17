"""IND_OCDE_09.1_run.py — I09: Média da Avaliação do Plano de Trabalho por Unidade.

Instrumento: Plano de Trabalho (PT).
Periodicidade: 2025 trimestral (T3–T4) | 2026+ mensal (M01–M12). Base: 01/07/2025.

Correção de escala (19.06.2026): o SQL original usava JSON_UNQUOTE(tan.nota) com
CASE WHEN textual — que não funciona no Denodo VQL via JDBC (retorna NULL para todos
os registros). Substituído por (6 - tan.sequencia), que usa o campo inteiro nativo:
  sequencia=1 → Excepcional     → score 5
  sequencia=2 → Alto desempenho → score 4
  sequencia=3 → Adequado        → score 3
  sequencia=4 → Inadequado      → score 2
  sequencia=5 → Não executado   → score 1

Achado de validação (19.06.2026): com a correção, média nacional ~4,0
("Alto desempenho"), confirmando perfil ICMBio (9% Excepcional + 71% Alto desempenho).
A coluna total_planos_com_avaliacao (COUNT DISTINCT plano_trabalho_id) é a referência
correta para comparar com o PETRVS — o PETRVS exibe planos distintos (7.421), enquanto
total_avaliacoes_pt conta eventos de avaliação (20.664, ratio ~2,78×) por planos com
múltiplas consolidações mensais em 2026.

Decisão CGOV D11 (13.09.2026) — média por Plano de Trabalho:
  A métrica primária passou a ser calculada em dois passos — primeiro a média das
  notas de cada plano, depois a média dessas médias por unidade. Sem isso, um
  plano longo com muitas consolidações mensais pesava mais na média da unidade do
  que um plano curto, distorcendo a comparação entre unidades.

  media_nota_pt      = média das médias dos planos (métrica primária, D11)
  media_nota_pt_eventos = média simples sobre os eventos (fórmula anterior a
                          13.09.2026, preservada para a COCAGE comparar as duas
                          leituras durante a transição)

  nota_minima, nota_maxima e qtd_nota_1..5 continuam sobre o universo de eventos:
  são distribuições, não médias, e mudá-las esconderia a dispersão real.

D41 (3.0.3, 17.10.2026): o VQL devolve só contagens inteiras (qtd_nota_1..5 por
unidade e soma/contagem das notas por plano, em PLANOS_I09_SQL). As duas médias são
calculadas em Python com aritmética exata (Fraction) e arredondadas meio para cima
(D24, lib/arredondamento.py); a faixa de desempenho usa a média já arredondada. A média
em ponto flutuante do Denodo (3,57499… em vez de 3,575) gerava divergência de 0,01.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
import sys

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "lib" / "__init__.py").exists())
sys.path.insert(0, str(ROOT))

from lib.arredondamento import arredondar  # D24: meio para cima
from lib.csv_utils import indicator_csv_dir, write_pipe_csv
from lib.denodo_config import connect, get_config
from lib.estrutura_organizacional import insert_mesogrupo_column, load_mesogrupo_lookup
from lib.monthly_runner import query_rows
from lib.periodos import analysis_window, build_periods_pt, period_metadata

SQL_I09 = """
WITH parametros AS (
    SELECT
        CAST('{ini}' AS DATE) AS data_inicio,
        CAST('{fim}' AS DATE) AS data_fim,
        0                     AS incluir_excluidos
),
avaliacoes_pt AS (
    SELECT
        av.id                    AS id_avaliacao,
        pt.unidade_id,
        pt.usuario_id            AS id_servidor,
        ptc.plano_trabalho_id,
        (6 - tan.sequencia)      AS valor_nota
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
      AND (p.incluir_excluidos = 1 OR ptc.deleted_at IS NULL)  -- soft-delete da consolidação (regra §2.4)
      AND CAST(av.data_avaliacao AS DATE) BETWEEN p.data_inicio AND p.data_fim
      AND CAST(pt.data_inicio AS DATE) <= p.data_fim
      AND CAST(pt.data_fim   AS DATE) >= p.data_inicio
      AND (p.incluir_excluidos = 1 OR pt.deleted_at IS NULL)
),
contagens_por_unidade AS (
    -- D41 (3.0.3): só contagens inteiras; as médias são calculadas em Python, com
    -- aritmética exata, a partir de qtd_nota_1..5 e de PLANOS_I09_SQL.
    SELECT
        COALESCE(un.sigla, 'N.I.')                               AS unidade_sigla,
        COALESCE(un.nome,  'N.I.')                               AS unidade_nome,
        COUNT(avpt.id_avaliacao)                                 AS total_avaliacoes_pt,
        COUNT(DISTINCT avpt.plano_trabalho_id)                   AS total_planos_com_avaliacao,
        COUNT(DISTINCT avpt.id_servidor)                         AS total_servidores_avaliados,
        MIN(avpt.valor_nota)                                     AS nota_minima,
        MAX(avpt.valor_nota)                                     AS nota_maxima,
        SUM(CASE WHEN avpt.valor_nota = 1 THEN 1 ELSE 0 END)    AS qtd_nota_1,
        SUM(CASE WHEN avpt.valor_nota = 2 THEN 1 ELSE 0 END)    AS qtd_nota_2,
        SUM(CASE WHEN avpt.valor_nota = 3 THEN 1 ELSE 0 END)    AS qtd_nota_3,
        SUM(CASE WHEN avpt.valor_nota = 4 THEN 1 ELSE 0 END)    AS qtd_nota_4,
        SUM(CASE WHEN avpt.valor_nota = 5 THEN 1 ELSE 0 END)    AS qtd_nota_5
    FROM avaliacoes_pt avpt
    LEFT JOIN petrvs_icmbio_unidades un ON un.id = avpt.unidade_id
    GROUP BY COALESCE(un.sigla, 'N.I.'), COALESCE(un.nome, 'N.I.')
)
SELECT
    unidade_sigla,
    unidade_nome,
    total_avaliacoes_pt,
    total_planos_com_avaliacao,
    total_servidores_avaliados,
    nota_minima,
    nota_maxima,
    qtd_nota_1,
    qtd_nota_2,
    qtd_nota_3,
    qtd_nota_4,
    qtd_nota_5
FROM contagens_por_unidade
ORDER BY unidade_sigla
"""

# D11 + D41 (3.0.3): soma e contagem das notas (inteiras) de cada plano de trabalho.
# Cada plano entra na média da unidade com peso 1, independentemente de quantas
# consolidações mensais acumulou; a média das médias é exata, em Python.
PLANOS_I09_SQL = """
WITH parametros AS (
    SELECT
        CAST('{ini}' AS DATE) AS data_inicio,
        CAST('{fim}' AS DATE) AS data_fim,
        0                     AS incluir_excluidos
),
avaliacoes_pt AS (
    SELECT
        av.id                    AS id_avaliacao,
        pt.unidade_id,
        ptc.plano_trabalho_id,
        (6 - tan.sequencia)      AS valor_nota
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
      AND (p.incluir_excluidos = 1 OR ptc.deleted_at IS NULL)  -- soft-delete da consolidação (regra §2.4)
      AND CAST(av.data_avaliacao AS DATE) BETWEEN p.data_inicio AND p.data_fim
      AND CAST(pt.data_inicio AS DATE) <= p.data_fim
      AND CAST(pt.data_fim   AS DATE) >= p.data_inicio
      AND (p.incluir_excluidos = 1 OR pt.deleted_at IS NULL)
)
SELECT
    COALESCE(un.sigla, 'N.I.')     AS unidade_sigla,
    COALESCE(un.nome,  'N.I.')     AS unidade_nome,
    avpt.plano_trabalho_id,
    SUM(avpt.valor_nota)           AS soma_notas_plano,
    COUNT(avpt.id_avaliacao)       AS qtd_avaliacoes_plano
FROM avaliacoes_pt avpt
LEFT JOIN petrvs_icmbio_unidades un ON un.id = avpt.unidade_id
GROUP BY COALESCE(un.sigla, 'N.I.'), COALESCE(un.nome, 'N.I.'), avpt.plano_trabalho_id
"""

# Ordem das colunas do CSV (inalterada desde a D11).
COLUNAS_I09 = [
    "unidade_sigla", "unidade_nome", "total_avaliacoes_pt", "total_planos_com_avaliacao",
    "total_servidores_avaliados", "media_nota_pt", "media_nota_pt_eventos", "nota_minima",
    "nota_maxima", "qtd_nota_1", "qtd_nota_2", "qtd_nota_3", "qtd_nota_4", "qtd_nota_5",
    "faixa_desempenho",
]


def faixa_desempenho(media: float) -> str:
    if media >= 4.5:
        return "Excepcional"
    if media >= 3.5:
        return "Alto desempenho"
    if media >= 2.5:
        return "Adequado"
    if media >= 1.5:
        return "Inadequado"
    return "Nao executado"


def _inteiro(valor: object) -> int:
    texto = str(valor).replace(",", ".").strip()
    return int(float(texto)) if texto else 0


def _arredondar_fracao(valor: Fraction) -> str:
    """D24 sobre o valor exato: a fração vira decimal com folga de precisão antes do meio para cima."""

    exato = Decimal(valor.numerator) / Decimal(valor.denominator)
    return str(arredondar(float(exato.quantize(Decimal("1e-12"))), 2))


def montar_linhas(
    columns: list[str], rows: list[list[str]], plan_columns: list[str], plan_rows: list[list[str]]
) -> list[list[str]]:
    """D41 (3.0.3): médias exatas em Python a partir de contagens inteiras do VQL.

    media_nota_pt = média das médias por plano (D11); media_nota_pt_eventos = soma das
    notas ÷ total de avaliações. Ambas com Fraction e arredondamento meio para cima (D24);
    a faixa de desempenho usa a média já arredondada. Saída na ordem de COLUNAS_I09,
    ordenada por media_nota_pt decrescente e unidade.
    """

    medias_dos_planos: dict[tuple[str, str], list[Fraction]] = {}
    sigla_p, nome_p = plan_columns.index("unidade_sigla"), plan_columns.index("unidade_nome")
    soma_p, qtd_p = plan_columns.index("soma_notas_plano"), plan_columns.index("qtd_avaliacoes_plano")
    for plano in plan_rows:
        quantidade = _inteiro(plano[qtd_p])
        if quantidade:
            medias_dos_planos.setdefault((plano[sigla_p], plano[nome_p]), []).append(
                Fraction(_inteiro(plano[soma_p]), quantidade)
            )

    saida: list[tuple[Fraction | None, str, list[str]]] = []
    for row in rows:
        valor = dict(zip(columns, row))
        total = _inteiro(valor["total_avaliacoes_pt"])
        soma = sum(nota * _inteiro(valor[f"qtd_nota_{nota}"]) for nota in range(1, 6))
        eventos = _arredondar_fracao(Fraction(soma, total)) if total else ""
        planos = medias_dos_planos.get((valor["unidade_sigla"], valor["unidade_nome"]), [])
        media_planos = sum(planos, Fraction(0)) / len(planos) if planos else None
        media = _arredondar_fracao(media_planos) if media_planos is not None else ""
        valor.update({
            "media_nota_pt": media,
            "media_nota_pt_eventos": eventos,
            "faixa_desempenho": faixa_desempenho(float(media)) if media else "",
        })
        saida.append((media_planos, valor["unidade_sigla"], [valor[c] for c in COLUNAS_I09]))
    saida.sort(key=lambda item: (item[0] is None, -(item[0] or 0), item[1]))
    return [linha for _, _, linha in saida]


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
    output = out_dir / f"IND_OCDE_09.2_media_avaliacao_pt_{stamp}.csv"

    window = analysis_window()
    periods = build_periods_pt(window.fim)
    meta_cols = period_metadata()
    all_cols: list[str] | None = None
    all_rows: list[list] = []

    try:
        for label, kind, start, scheduled_end, end, status in periods:
            sql = SQL_I09.replace("{ini}", str(start)).replace("{fim}", str(end))
            print(f"Executando I09 {label} ({start} a {end})...")
            sql_planos = PLANOS_I09_SQL.replace("{ini}", str(start)).replace("{fim}", str(end))
            try:
                columns, rows = query_rows(conn, sql)
                plan_columns, plan_rows = query_rows(conn, sql_planos)
            except Exception as exc:
                # D33: falha em qualquer período interrompe o A1 sem gravar A2 parcial.
                raise SystemExit(f"ERRO: I09 {label}: {exc}") from exc
            if all_cols is None:
                all_cols = meta_cols + COLUNAS_I09
            duration = (end - start).days + 1
            for row in montar_linhas(columns, rows, plan_columns, plan_rows):
                all_rows.append([kind, label, str(start), str(scheduled_end), str(end), status, duration] + row)
            print(f"  {len(rows)} linhas retornadas.")
    finally:
        conn.close()

    if not all_rows:
        print("Nenhum dado retornado. CSV nao gerado.")
        return

    # mesogrupo so entra no CSV escrito — all_cols/all_rows seguem com as
    # posicoes originais para nao afetar as buscas por nome usadas abaixo.
    lookup = load_mesogrupo_lookup()
    csv_cols, csv_rows = insert_mesogrupo_column(all_cols or [], all_rows, lookup)

    write_pipe_csv(output, csv_cols, csv_rows)
    print(f"Arquivo salvo: {output}")

    # Busca por nome, nao por offset fixo: a insercao de colunas novas (como
    # media_nota_pt_eventos na D11) deslocava as posicoes e quebrava os avisos.
    cols = all_cols or []
    offset_total = cols.index("total_avaliacoes_pt")
    offset_media = cols.index("media_nota_pt")
    offset_status = cols.index("periodo_status")
    offset_unidade = cols.index("unidade_sigla")

    encerrados = [r for r in all_rows if r[offset_status] == "encerrado"]

    # Unidades com < 5 avaliacoes (resultado estatisticamente fragil)
    low_count = sum(1 for r in encerrados if int(r[offset_total] or 0) < 5)
    if low_count:
        print(f"  AVISO: {low_count} linha(s) com < 5 avaliacoes em periodos encerrados — resultados frageis.")

    # Unidades com media abaixo de 2.5 (Inadequado ou pior)
    criticas = [r for r in encerrados if _to_float(r[offset_media]) < 2.5 and r[offset_media] != ""]
    if criticas:
        unids = set(r[offset_unidade] for r in criticas)
        print(f"  AVISO: {len(unids)} unidade(s) com media < 2.5 (Inadequado) em periodos encerrados.")

    parciais = sum(1 for r in all_rows if r[offset_status] == "parcial_no_corte")
    if parciais:
        print(f"  NOTA: {parciais} linha(s) em ciclo parcial_no_corte — valores preliminares.")


if __name__ == "__main__":
    main()
