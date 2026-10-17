"""IND_OCDE_05.1_run.py — I05: Distribuição das Entregas entre os Servidores.

Instrumento: Plano de Trabalho (PT).
Periodicidade: 2025 trimestral (T3–T4) | 2026+ mensal (M01–M12). Base: 01/07/2025.

O I05 calcula quantas entregas do PE cada servidor carrega no PT e compara
com a média dos demais servidores da mesma unidade, respondendo:
"A carga está distribuída de forma equitativa ou concentrada em poucos?"

Nota metodológica: a unidade é derivada de pt.unidade_id (unidade do servidor),
pois o I05 mede distribuição de carga entre servidores, não entre planejadores.
O filtro temporal incide sobre a vigência do PT: servidores ativos no período,
não sobre datas de conclusão de cada entrega.

Correção (24.05.2026): adicionado filtro pte.deleted_at IS NULL, ausente na
versão original. Sem esse filtro, registros excluídos logicamente em
planos_trabalhos_entregas inflavam a quantidade de entregas por servidor.

D43 (3.0.2, 17.10.2026): o VQL devolve só a contagem inteira de entregas por
servidor; a média da unidade (media_entregas_por_servidor_unidade) é calculada em
Python com aritmética exata (Fraction) e arredondada meio para cima (D24), e a
posição relativa compara com a média já arredondada. O ROUND(AVG(...)) em ponto
flutuante do Denodo gerava divergência de 0,01, como no I09 (D41). Os JOINs de
unidade e de usuário passam a filtrar deleted_at (regra 9).
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

SQL_I05 = """
WITH parametros AS (
    SELECT
        CAST('{ini}' AS DATE) AS data_inicio,
        CAST('{fim}' AS DATE) AS data_fim,
        0                     AS incluir_excluidos
),
vinculos_entregas AS (
    SELECT DISTINCT
        COALESCE(un.sigla, 'N.I.') AS unidade_sigla,
        COALESCE(un.nome,  'N.I.') AS unidade_nome,
        pt.usuario_id              AS id_servidor,
        COALESCE(us.nome,  'N.I.') AS nome_servidor,
        pte.plano_entrega_entrega_id AS id_entrega
    FROM petrvs_icmbio_planos_trabalhos pt
    JOIN petrvs_icmbio_planos_trabalhos_entregas pte
        ON pte.plano_trabalho_id = pt.id
    LEFT JOIN petrvs_icmbio_unidades un
        ON un.id = pt.unidade_id
       AND un.deleted_at IS NULL
    LEFT JOIN petrvs_icmbio_usuarios us
        ON us.id = pt.usuario_id
       AND us.deleted_at IS NULL
    CROSS JOIN parametros p
    WHERE CAST(pt.data_inicio AS DATE) <= p.data_fim
      AND CAST(pt.data_fim   AS DATE) >= p.data_inicio
      AND (p.incluir_excluidos = 1 OR pt.deleted_at  IS NULL)
      AND (p.incluir_excluidos = 1 OR pte.deleted_at IS NULL)
      AND pt.usuario_id IS NOT NULL
      AND pte.plano_entrega_entrega_id IS NOT NULL
),
entregas_por_servidor AS (
    SELECT
        unidade_sigla,
        MIN(unidade_nome)              AS unidade_nome,
        id_servidor,
        MIN(nome_servidor)             AS nome_servidor,
        COUNT(DISTINCT id_entrega)     AS qtd_entregas_por_servidor
    FROM vinculos_entregas
    GROUP BY unidade_sigla, id_servidor
)
SELECT
    e.unidade_sigla,
    e.unidade_nome,
    e.id_servidor,
    e.nome_servidor,
    e.qtd_entregas_por_servidor
FROM entregas_por_servidor e
ORDER BY e.unidade_sigla, e.qtd_entregas_por_servidor DESC, e.nome_servidor
"""

# Colunas da v1, na ordem histórica do CSV: as duas últimas são calculadas em Python (D43).
COLUNAS_V1 = [
    "unidade_sigla", "unidade_nome", "id_servidor", "nome_servidor",
    "qtd_entregas_por_servidor", "media_entregas_por_servidor_unidade",
    "posicao_relativa_media",
]


COLUNAS_V2 = [
    "unidade_sigla", "unidade_nome", "total_servidores",
    "media_entregas_por_servidor", "mediana_entregas_por_servidor",
    "p25_entregas_por_servidor", "p75_entregas_por_servidor",
    "pct_servidores_sem_entrega",
]


def _inteiro(valor: object) -> int:
    texto = str(valor).replace(",", ".").strip()
    return int(float(texto)) if texto else 0


def _arredondar_fracao(valor: Fraction) -> str:
    """D24 sobre o valor exato: a fração vira decimal com folga de precisão antes do meio para cima."""

    exato = Decimal(valor.numerator) / Decimal(valor.denominator)
    return str(arredondar(float(exato.quantize(Decimal("1e-12"))), 2))


def montar_v1(columns: list[str], rows: list[list[str]]) -> list[list[str]]:
    """D43 (3.0.2): média da unidade exata em Python, a partir das contagens inteiras.

    Mantém a ordem do VQL e devolve as linhas na ordem de COLUNAS_V1. A posição
    relativa compara a contagem do servidor com a média já arredondada.
    """

    sigla, qtd = columns.index("unidade_sigla"), columns.index("qtd_entregas_por_servidor")
    contagens: dict[str, list[int]] = {}
    for row in rows:
        contagens.setdefault(row[sigla], []).append(_inteiro(row[qtd]))
    medias = {
        unidade: _arredondar_fracao(Fraction(sum(valores), len(valores)))
        for unidade, valores in contagens.items()
    }

    saida: list[list[str]] = []
    for row in rows:
        valor = dict(zip(columns, row))
        media = medias[valor["unidade_sigla"]]
        contagem = _inteiro(valor["qtd_entregas_por_servidor"])
        valor["media_entregas_por_servidor_unidade"] = media
        valor["posicao_relativa_media"] = (
            "Acima da media" if contagem > float(media)
            else "Abaixo da media" if contagem < float(media) else "Na media"
        )
        saida.append([valor[coluna] for coluna in COLUNAS_V1])
    return saida


def _quantil(ordenados: list[float], fracao: float) -> float:
    """Quantil por interpolação linear, igual ao método padrão do pandas."""

    if not ordenados:
        return 0.0
    posicao = (len(ordenados) - 1) * fracao
    inferior = int(posicao)
    superior = min(inferior + 1, len(ordenados) - 1)
    peso = posicao - inferior
    return ordenados[inferior] * (1 - peso) + ordenados[superior] * peso


def distribuicao_estatistica(
    all_cols: list[str], all_rows: list[list], meta_cols: list[str]
) -> tuple[list[str], list[list]]:
    """Visão agregada por unidade, sem identificação nominal (decisão CGOV D07).

    A média sozinha esconde concentração: uma unidade com um servidor carregando
    vinte entregas e cinco sem nenhuma tem a mesma média de outra em que todos
    carregam quatro. Mediana e quartis separam os dois casos.
    """

    idx_unidade = all_cols.index("unidade_sigla")
    idx_nome = all_cols.index("unidade_nome")
    idx_qtd = all_cols.index("qtd_entregas_por_servidor")
    n_meta = len(meta_cols)

    grupos: dict[tuple, list[float]] = {}
    for row in all_rows:
        chave = tuple(row[:n_meta]) + (row[idx_unidade], row[idx_nome])
        try:
            valor = float(str(row[idx_qtd]).replace(",", "."))
        except (TypeError, ValueError):
            valor = 0.0
        grupos.setdefault(chave, []).append(valor)

    linhas: list[list] = []
    for chave, valores in grupos.items():
        ordenados = sorted(valores)
        total = len(ordenados)
        zerados = sum(1 for valor in ordenados if valor == 0)
        meio = total // 2
        mediana = (
            ordenados[meio] if total % 2
            else (ordenados[meio - 1] + ordenados[meio]) / 2
        )
        linhas.append(list(chave) + [
            total,
            arredondar(sum(ordenados) / total, 2),
            arredondar(mediana, 2),
            arredondar(_quantil(ordenados, 0.25), 2),
            arredondar(_quantil(ordenados, 0.75), 2),
            arredondar(100.0 * zerados / total, 2),
        ])
    linhas.sort(key=lambda linha: (linha[1], linha[n_meta]))
    return meta_cols + COLUNAS_V2, linhas


def main() -> None:
    config = get_config(require_credentials=True)
    conn = connect(config)
    out_dir = indicator_csv_dir()
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    output = out_dir / f"IND_OCDE_05.2_v1_distribuicao_entregas_servidores_{stamp}.csv"
    output_v2 = out_dir / f"IND_OCDE_05.2_v2_distribuicao_estatistica_{stamp}.csv"

    window = analysis_window()
    periods = build_periods_pt(window.fim)
    meta_cols = period_metadata()
    all_cols: list[str] | None = None
    all_rows: list[list] = []

    try:
        for label, kind, start, scheduled_end, end, status in periods:
            sql = SQL_I05.replace("{ini}", str(start)).replace("{fim}", str(end))
            print(f"Executando I05 {label} ({start} a {end})...")
            try:
                columns, rows = query_rows(conn, sql)
            except Exception as exc:
                # D33: falha em qualquer período interrompe o A1 sem gravar A2 parcial.
                raise SystemExit(f"ERRO: I05 {label}: {exc}") from exc
            if all_cols is None:
                all_cols = meta_cols + COLUNAS_V1
            duration = (end - start).days + 1
            for row in montar_v1(columns, rows):
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
    print(f"Arquivo salvo (v1, nominal — uso restrito): {output}")

    # D07: visao estatistica agregada, sem identificacao de servidor.
    cols_v2, rows_v2 = distribuicao_estatistica(all_cols or [], all_rows, meta_cols)
    csv_cols_v2, csv_rows_v2 = insert_mesogrupo_column(cols_v2, rows_v2, lookup)
    write_pipe_csv(output_v2, csv_cols_v2, csv_rows_v2)
    print(f"Arquivo salvo (v2, estatistica agregada): {output_v2}")

    # Aviso de qualidade: servidores com 0 entregas (PT ativo mas sem vinculos)
    # Busca por nome, nao por offset fixo: a insercao de colunas novas
    # deslocava as posicoes e quebrava os avisos (ver CGOV D09/D11).
    cols = all_cols or []
    offset_qtd = cols.index("qtd_entregas_por_servidor")
    sem_entregas = sum(1 for r in all_rows if str(r[offset_qtd]) == "0")
    if sem_entregas:
        print(f"  AVISO: {sem_entregas} servidor(es) com 0 entregas vinculadas — verificar preenchimento do PT.")


if __name__ == "__main__":
    main()
