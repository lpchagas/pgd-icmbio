"""REG_EXEC.1_run.py — Registro de execução do Plano de Entregas por período.

Objetivo (chefia da unidade de execução): responder "o Plano de Entregas deste
quadrimestre pode ser concluído, e o que ainda falta para isso".

Diferença para PT_STATUS: aquele é uma fotografia operacional ("qual PT está
parado agora"); este recorta UM período fechado do Plano de Entregas e cruza
o resultado das entregas com a execução dos planos de trabalho no período.

Duas regras estruturam a extração:

  RN-04  a conclusão do PE depende de TODOS os PT dos servidores da unidade no
         período terem sido registrados e avaliados. Um quadrimestre depende,
         portanto, de 4 ciclos mensais completos por servidor.
  RN-08  o progresso esperado é do planejamento e o registro informa o
         realizado — a meta da entrega nunca é derivada de contagem de
         atividades ou de conclusão de PT (caderno metodológico §1.3).

O universo dos ciclos vem dos PLANOS VIGENTES, não das consolidações
existentes: o ciclo que nunca foi aberto é exatamente o que a RN-04 precisa
enxergar, e ele não aparece em nenhuma consulta de consolidações.

Uso:
    python gestao/REG_EXEC.1_run.py --unidade CGOV --periodo Q2-2026 --dry-run
    python gestao/REG_EXEC.1_run.py --unidade CGOV --periodo Q2-2026 \
        --data-execucao 2026-09-14 --produto operacional --relatorio
    python gestao/REG_EXEC.1_run.py --unidade CGOV --incluir-subordinadas \
        --periodo Q2-2026 --produto restrito --relatorio
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from lib.csv_utils import PROJECT_ROOT as _ROOT, write_pipe_csv  # noqa: E402
from lib.denodo_config import connect, get_config  # noqa: E402
from lib.estrutura_organizacional import (  # noqa: E402
    insert_mesogrupo_column,
    load_mesogrupo_lookup,
)
from lib.periodos import (  # noqa: E402
    PeriodoDesconhecido,
    PeriodoIndisponivel,
    analysis_window,
    configure_execution_context,
    default_pe_period,
    periods_pt_within,
    resolve_period,
)
from ocde.relatorios.privacidade import assert_safe_outputs  # noqa: E402
from ocde.relatorios.textos_execucao import TextSanitizer  # noqa: E402

from gestao.comum import (  # noqa: E402
    expandir_subordinadas,
    quote_list,
    rotulo_de_escopo,
    run_query,
    siglas_de_argumentos,
)
from gestao.reg_exec_montagem import (  # noqa: E402
    montar_ciclos,
    montar_entregas,
    montar_painel,
    montar_vinculos,
    remover_colunas_pessoais,
)
from gestao.reg_exec_relatorio import render_markdown  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# Nomes de servidores, usados apenas em memória para alimentar o TextSanitizer
# nos produtos não nominais. Nunca são gravados fora do produto operacional.
SQL_NOMES = """
SELECT us.nome AS nome
FROM petrvs_icmbio_usuarios us
WHERE us.deleted_at IS NULL
  AND us.nome IS NOT NULL
"""

# Entregas do Plano de Entregas vigentes no período.
# O tratamento de data_fim NULL e deliberado: a coluna e anulavel e uma entrega
# sem prazo cadastrado precisa aparecer no registro como pendencia, nao sumir.
SQL_PE_ENTREGAS = """
SELECT
    ud.sigla  AS unidade_dona_sigla,
    ud.nome   AS unidade_dona_nome,
    ue.sigla  AS unidade_executora_sigla,
    pe.numero AS plano_numero,
    pe.status AS plano_status,
    pee.id    AS entrega_uuid,
    COALESCE(NULLIF(TRIM(pee.descricao), ''),
             NULLIF(TRIM(pee.descricao_entrega), '')) AS entrega_titulo,
    pee.descricao_meta   AS entrega_meta_texto,
    pee.destinatario     AS entrega_destinatario,
    pee.meta             AS meta_json,
    COALESCE(pee.progresso_esperado,  0) AS progresso_esperado,
    COALESCE(pee.progresso_realizado, 0) AS progresso_realizado,
    CAST(pee.data_inicio AS DATE) AS entrega_inicio,
    CAST(pee.data_fim    AS DATE) AS entrega_fim
FROM petrvs_icmbio_planos_entregas_entregas pee
JOIN petrvs_icmbio_planos_entregas pe
     ON pe.id = pee.plano_entrega_id AND pe.deleted_at IS NULL
JOIN petrvs_icmbio_unidades ud
     ON ud.id = pe.unidade_id AND ud.deleted_at IS NULL
LEFT JOIN petrvs_icmbio_unidades ue
     ON ue.id = pee.unidade_id AND ue.deleted_at IS NULL
WHERE pee.deleted_at IS NULL
  AND CAST(pee.data_inicio AS DATE) <= CAST('{fim}' AS DATE)
  AND (pee.data_fim IS NULL
       OR CAST(pee.data_fim AS DATE) >= CAST('{inicio}' AS DATE))
  {filtro_dono}
ORDER BY ud.sigla, pe.numero, pee.data_fim, pee.id
"""

# Consolidacoes mensais dos planos de trabalho que tocam o periodo.
SQL_PT_CICLOS = """
WITH atividade_ciclo AS (
    SELECT a.plano_trabalho_consolidacao_id                        AS cid,
           COUNT(a.id)                                             AS atividades_total,
           SUM(CASE WHEN a.status = 'CONCLUIDO' THEN 1 ELSE 0 END) AS atividades_concluidas,
           SUM(COALESCE(a.tempo_planejado,  0))                    AS horas_planejadas,
           SUM(COALESCE(a.tempo_despendido, 0))                    AS horas_despendidas
    FROM petrvs_icmbio_atividades a
    WHERE a.deleted_at IS NULL
      AND a.plano_trabalho_consolidacao_id IS NOT NULL
    GROUP BY a.plano_trabalho_consolidacao_id
),
avaliacao_ciclo AS (
    SELECT av.plano_trabalho_consolidacao_id    AS cid,
           MIN(CAST(av.data_avaliacao AS DATE)) AS data_avaliacao,
           MAX(6 - tan.sequencia)               AS score_avaliacao
    FROM petrvs_icmbio_avaliacoes av
    JOIN petrvs_icmbio_tipos_avaliacoes_notas tan
         ON tan.id = av.tipo_avaliacao_nota_id
    WHERE av.deleted_at IS NULL
      AND av.plano_trabalho_consolidacao_id IS NOT NULL
    GROUP BY av.plano_trabalho_consolidacao_id
)
SELECT
    u.sigla   AS unidade_sigla,
    us.nome   AS servidor_nome,
    pt.numero AS plano_numero,
    c.status  AS consolidacao_status,
    CAST(c.data_inicio    AS DATE) AS ciclo_inicio,
    CAST(c.data_fim       AS DATE) AS ciclo_fim,
    CAST(c.data_conclusao AS DATE) AS ciclo_conclusao,
    av.data_avaliacao              AS ciclo_avaliacao,
    av.score_avaliacao             AS score_avaliacao,
    COALESCE(ac.atividades_total,      0) AS atividades_total,
    COALESCE(ac.atividades_concluidas, 0) AS atividades_concluidas,
    COALESCE(ac.horas_planejadas,      0) AS horas_planejadas,
    COALESCE(ac.horas_despendidas,     0) AS horas_despendidas
FROM petrvs_icmbio_planos_trabalhos_consolidacoes c
JOIN petrvs_icmbio_planos_trabalhos pt
     ON pt.id = c.plano_trabalho_id AND pt.deleted_at IS NULL
JOIN petrvs_icmbio_unidades u  ON u.id  = pt.unidade_id AND u.deleted_at IS NULL
JOIN petrvs_icmbio_usuarios us ON us.id = pt.usuario_id AND us.deleted_at IS NULL
LEFT JOIN avaliacao_ciclo av ON av.cid = c.id
LEFT JOIN atividade_ciclo ac ON ac.cid = c.id
WHERE c.deleted_at IS NULL
  AND CAST(c.data_inicio AS DATE) <= CAST('{fim}' AS DATE)
  AND CAST(c.data_fim    AS DATE) >= CAST('{inicio}' AS DATE)
  {filtro_executora}
ORDER BY u.sigla, us.nome, c.data_inicio
"""

# Universo de planos de trabalho vigentes no periodo — base da RN-04.
SQL_PT_VIGENTES = """
SELECT
    u.sigla   AS unidade_sigla,
    u.nome    AS unidade_nome,
    up.sigla  AS unidade_pai_sigla,
    us.nome   AS servidor_nome,
    pt.numero AS plano_numero,
    pt.status AS plano_status,
    CAST(pt.data_inicio AS DATE) AS plano_inicio,
    CAST(pt.data_fim    AS DATE) AS plano_fim
FROM petrvs_icmbio_planos_trabalhos pt
JOIN petrvs_icmbio_unidades u  ON u.id  = pt.unidade_id AND u.deleted_at IS NULL
JOIN petrvs_icmbio_usuarios us ON us.id = pt.usuario_id AND us.deleted_at IS NULL
LEFT JOIN petrvs_icmbio_unidades up
     ON up.id = u.unidade_pai_id AND up.deleted_at IS NULL
WHERE pt.deleted_at IS NULL
  AND pt.status <> 'CANCELADO'
  AND CAST(pt.data_inicio AS DATE) <= CAST('{fim}' AS DATE)
  AND CAST(pt.data_fim    AS DATE) >= CAST('{inicio}' AS DATE)
  {filtro_executora}
ORDER BY u.sigla, us.nome, pt.numero
"""

# Forca de trabalho declarada de cada PT em cada entrega do PE.
SQL_VINCULOS = """
SELECT
    ud.sigla  AS unidade_dona_sigla,
    ux.sigla  AS unidade_executora_sigla,
    us.nome   AS servidor_nome,
    pe.numero AS plano_entrega_numero,
    pee.id    AS entrega_uuid,
    pt.numero AS plano_trabalho_numero,
    pt.status AS plano_trabalho_status,
    COALESCE(pte.forca_trabalho, 0) AS forca_trabalho_perc,
    pt.carga_horaria                AS carga_horaria,
    pt.forma_contagem_carga_horaria AS forma_contagem_carga_horaria,
    CAST(pt.data_inicio AS DATE)    AS plano_inicio,
    CAST(pt.data_fim    AS DATE)    AS plano_fim
FROM petrvs_icmbio_planos_trabalhos_entregas pte
JOIN petrvs_icmbio_planos_trabalhos pt
     ON pt.id = pte.plano_trabalho_id AND pt.deleted_at IS NULL
JOIN petrvs_icmbio_usuarios us ON us.id = pt.usuario_id AND us.deleted_at IS NULL
JOIN petrvs_icmbio_unidades ux ON ux.id = pt.unidade_id AND ux.deleted_at IS NULL
JOIN petrvs_icmbio_planos_entregas_entregas pee
     ON pee.id = pte.plano_entrega_entrega_id AND pee.deleted_at IS NULL
JOIN petrvs_icmbio_planos_entregas pe
     ON pe.id = pee.plano_entrega_id AND pe.deleted_at IS NULL
JOIN petrvs_icmbio_unidades ud ON ud.id = pe.unidade_id AND ud.deleted_at IS NULL
WHERE pte.deleted_at IS NULL
  AND pte.plano_entrega_entrega_id IS NOT NULL
  AND CAST(pt.data_inicio AS DATE) <= CAST('{fim}' AS DATE)
  AND CAST(pt.data_fim    AS DATE) >= CAST('{inicio}' AS DATE)
  {filtro_ambos}
ORDER BY ud.sigla, pe.numero, us.nome
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--unidade", action="append", default=[],
                        help="Sigla da unidade (repetível ou separada por vírgula).")
    parser.add_argument("--incluir-subordinadas", action="store_true",
                        help="Inclui as unidades filhas na hierarquia (até 3 níveis).")
    parser.add_argument("--todas", action="store_true",
                        help="Todas as unidades do ICMBio.")
    parser.add_argument("--periodo", default=None,
                        help="Rótulo do período de PE (ex.: Q2-2026). "
                             "Padrão: último período de PE encerrado na janela.")
    parser.add_argument("--exigir-encerrado", action="store_true",
                        help="Recusa período ainda aberto no corte da janela.")
    parser.add_argument("--out", default=None, help="Diretório de saída.")
    parser.add_argument("--data-execucao", help="Data reprodutível da apuração (AAAA-MM-DD).")
    parser.add_argument(
        "--produto", choices=("operacional", "restrito", "compartilhavel"),
        default="operacional",
        help="operacional mantém os nomes dos servidores; restrito e compartilhavel os removem.",
    )
    parser.add_argument("--relatorio", action="store_true",
                        help="Além dos CSVs, renderiza o registro de execução em Markdown.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Valida argumentos, período, escopo e destino sem abrir conexão.")
    return parser


def _dicts(colunas, linhas) -> list[dict]:
    return [dict(zip(colunas, linha)) for linha in linhas]


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    siglas = siglas_de_argumentos(args.unidade)
    if not siglas and not args.todas:
        parser.error("informe --unidade SIGLA ou --todas")

    window = configure_execution_context(
        args.data_execucao or analysis_window().data_execucao
    )

    if args.periodo:
        try:
            spec = resolve_period(
                args.periodo, familia="pe", analysis_end=window.fim,
                exigir_encerrado=args.exigir_encerrado,
            )
        except (PeriodoDesconhecido, PeriodoIndisponivel) as erro:
            parser.error(str(erro))
    else:
        spec = default_pe_period(window.fim)
        if spec is None:
            parser.error(
                "Nenhum período de PE encerrado na janela; informe --periodo explicitamente."
            )

    meses = periods_pt_within(spec, window.fim)
    destino = Path(args.out) if args.out else (
        _ROOT / "artefatos_local" / "gestao" / window.mes_execucao
    )
    escopo = rotulo_de_escopo(siglas, args.todas)

    print(f"Período: {spec.rotulo} ({spec.ciclo_tipo}) {spec.inicio} a {spec.fim_efetivo} "
          f"[{spec.status}]")
    print(f"Ciclos mensais de PT exigidos pela RN-04: "
          f"{', '.join(m.rotulo for m in meses) or 'nenhum'}")
    print(f"Janela acumulada de referência: {window.inicio} a {window.fim}")
    print(f"Produto: {args.produto}")
    print(f"Destino: {destino}")

    if args.dry_run:
        print("Modo dry-run: nenhuma conexão Denodo será aberta.")
        return

    conn = connect(get_config())
    print("Conexao Denodo OK.")
    try:
        if siglas and args.incluir_subordinadas:
            originais = set(siglas)
            siglas = expandir_subordinadas(conn, siglas)
            acrescentadas = sorted(set(siglas) - originais)
            print(f"Hierarquia expandida: {len(siglas)} unidades.")
        else:
            acrescentadas = []

        lista = quote_list(siglas) if siglas else ""
        filtro_dono = f"AND UPPER(ud.sigla) IN ({lista})" if siglas else ""
        filtro_executora = f"AND UPPER(u.sigla) IN ({lista})" if siglas else ""
        filtro_ambos = (
            f"AND (UPPER(ud.sigla) IN ({lista}) OR UPPER(ux.sigla) IN ({lista}))"
            if siglas else ""
        )
        janela = {"inicio": spec.inicio.isoformat(), "fim": spec.fim_efetivo.isoformat()}

        print("Consultando entregas do Plano de Entregas...")
        cols_pe, rows_pe = run_query(
            conn, SQL_PE_ENTREGAS.format(filtro_dono=filtro_dono, **janela)
        )
        print(f"  {len(rows_pe)} entregas.")

        print("Consultando planos de trabalho vigentes...")
        cols_vig, rows_vig = run_query(
            conn, SQL_PT_VIGENTES.format(filtro_executora=filtro_executora, **janela)
        )
        print(f"  {len(rows_vig)} planos.")

        print("Consultando consolidacoes mensais...")
        cols_cic, rows_cic = run_query(
            conn, SQL_PT_CICLOS.format(filtro_executora=filtro_executora, **janela)
        )
        print(f"  {len(rows_cic)} consolidacoes.")

        print("Consultando vinculos PT -> entrega...")
        cols_vin, rows_vin = run_query(
            conn, SQL_VINCULOS.format(filtro_ambos=filtro_ambos, **janela)
        )
        print(f"  {len(rows_vin)} vinculos.")

        nomes = [linha[0] for linha in run_query(conn, SQL_NOMES)[1]]
    finally:
        conn.close()

    entregas_reg = _dicts(cols_pe, rows_pe)
    vigentes_reg = _dicts(cols_vig, rows_vig)
    ciclos_reg = _dicts(cols_cic, rows_cic)
    vinculos_reg = _dicts(cols_vin, rows_vin)

    from gestao.reg_exec_regras import servidor_refs

    refs = servidor_refs([r.get("servidor_nome", "") for r in vigentes_reg])
    nominal = args.produto == "operacional"
    sanitizer = None if nominal else TextSanitizer(nomes)

    entregas = montar_entregas(entregas_reg, spec, sanitizer=sanitizer)
    ciclos = montar_ciclos(ciclos_reg, vigentes_reg, spec, meses, refs=refs)
    vinculos = montar_vinculos(vinculos_reg, spec, refs=refs)
    painel = montar_painel(*entregas, *ciclos, spec)

    if not nominal:
        ciclos = remover_colunas_pessoais(*ciclos)
        vinculos = remover_colunas_pessoais(*vinculos)

    lookup = load_mesogrupo_lookup()
    # A visão de entregas nomeia a unidade DONA do PE; a de ciclos, a executora.
    entregas = insert_mesogrupo_column(
        *entregas, lookup, sigla_col="unidade_dona_sigla", nome_col="unidade_dona_nome"
    )
    ciclos = insert_mesogrupo_column(*ciclos, lookup)

    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    sufixo = f"{args.produto}_{escopo}_{spec.rotulo}_{stamp}"
    gravados: list[Path] = []
    for nome, (colunas, linhas) in (
        ("entregas", entregas), ("ciclos_pt", ciclos),
        ("vinculos", vinculos), ("painel", painel),
    ):
        caminho = destino / f"REG_EXEC.2_{nome}_{sufixo}.csv"
        write_pipe_csv(caminho, colunas, linhas)
        gravados.append(caminho)
        print(f"  Salvo: {caminho}")

    if args.relatorio:
        markdown = render_markdown(
            spec=spec, escopo=escopo, produto=args.produto,
            emitido_em=window.data_execucao,
            entregas=entregas, ciclos=ciclos, vinculos=vinculos, painel=painel,
            unidades_expandidas=acrescentadas,
            procedencia={
                "janela_acumulada": f"{window.inicio} a {window.fim}",
                "periodo_recorte": f"{spec.inicio} a {spec.fim_efetivo} ({spec.status})",
                "produto": args.produto,
                "arquivos": ", ".join(caminho.name for caminho in gravados),
            },
        )
        caminho_md = destino / f"REG_EXEC.5_registro_execucao_{sufixo}.md"
        caminho_md.parent.mkdir(parents=True, exist_ok=True)
        caminho_md.write_text(markdown, encoding="utf-8")
        gravados.append(caminho_md)
        print(f"  Salvo: {caminho_md}")

    if nominal:
        print("\nATENCAO: o produto 'operacional' contem nomes de servidores. "
              "Mantenha os arquivos em artefatos_local/ e nao anexe ao SEI nem "
              "a drive compartilhada sem gerar a versao 'restrito'.")
    else:
        assert_safe_outputs(gravados)
        print("\nVarredura de privacidade: nenhum achado nos arquivos gravados.")

    for linha in painel[1]:
        print(f"  painel: {linha}")


if __name__ == "__main__":
    main()
