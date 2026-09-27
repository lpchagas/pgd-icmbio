"""IND_GEST_01.1_run.py — G01 · Situação dos Planos de Trabalho por unidade.

Indicador de gestão G01 (até 13.09.2026: PT_STATUS). Ficha:
docs/gestao/IND_GEST_01-situacao-planos-trabalho.md

Objetivo (gestor de equipe): responder "quais PTs da minha equipe estão em cada
status e quem devo procurar para destravar cada um".

Modelo de status do PETRVS — DUAS CAMADAS (confirmado no Denodo em 08.09.2026):

  Camada 1 — ciclo de vida do PLANO (planos_trabalhos.status):
      INCLUIDO -> AGUARDANDO_ASSINATURA -> ATIVO -> CONCLUIDO
                                             \\-> SUSPENSO / CANCELADO

  Camada 2 — ciclo de AVALIAÇÃO de cada período mensal
             (planos_trabalhos_consolidacoes.status):
      INCLUIDO (período aberto) -> CONCLUIDO (servidor enviou) -> AVALIADO

O status de negócio "aguardando avaliação" NÃO existe em planos_trabalhos.status —
ele vive na consolidação (status = CONCLUIDO). Por isso este script deriva
`status_negocio` cruzando as duas camadas, e não apenas lendo o campo `status`.

Data/hora da última mudança de status: vem de `status_justificativas`, tabela de
trilha de auditoria que registra cada transição com `codigo`, `created_at` e o
`usuario_id` de quem executou. Cobertura medida: 19.329/19.566 PTs ativos (98,8%).
Os 237 sem trilha são todos INCLUIDO (rascunhos que nunca transitaram) — para
esses, e para transições automáticas do sistema, cai no fallback `pt.updated_at`
(a coluna `origem_data_status` diz qual das duas fontes foi usada).

Identificação nominal — decisão CGOV D14 (13.09.2026):

  Este é um produto tático da chefia da unidade, não um indicador. Dizer a um
  gestor que ele tem "3 servidores aguardando assinatura" é inútil sem os nomes:
  a finalidade é permitir a cobrança e o destravamento, rotina ordinária do
  serviço público. Por isso os produtos `operacional` e `restrito` trazem
  `id_servidor` e `servidor_nome`.

  O produto `compartilhavel` continua **sem** detalhe nominal: só o painel
  agregado, com supressão de células de contagem inferior a 5 (`SUPRIMIDO_K`).
  Esse é o único produto que sai da unidade, e o gate de PII do A2
  (lib/validation_runner.py) segue valendo sobre ele.

  Dado pessoal é coletado no mínimo necessário para a finalidade: nome e
  identificador do servidor. CPF, e-mail e matrícula não são lidos nem
  persistidos — antes da D14 o `servidor_email` era selecionado sem uso claro e
  foi retirado da consulta.

Uso:
    python gestao/IND_GEST_01/IND_GEST_01.1_run.py --unidade CGGP
    python gestao/IND_GEST_01/IND_GEST_01.1_run.py --unidade CGGP --incluir-subordinadas
    python gestao/IND_GEST_01/IND_GEST_01.1_run.py --todas
    python gestao/IND_GEST_01/IND_GEST_01.1_run.py --unidade CGGP --incluir-encerrados
"""
from __future__ import annotations

import argparse
import sys
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from lib.csv_utils import PROJECT_ROOT as _ROOT, clean, write_pipe_csv  # noqa: E402
from lib.denodo_config import connect, get_config  # noqa: E402
from lib.periodos import (  # noqa: E402
    ANALYSIS_TIMEZONE,
    analysis_window,
    configure_execution_context,
)
from lib.validation_contracts import gest_artifact  # noqa: E402
from lib.estrutura_organizacional import (  # noqa: E402
    insert_mesogrupo_column,
    load_mesogrupo_lookup,
)
from ocde.relatorios.privacidade import K_MIN, apply_complementary_suppression  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Rótulos de negócio (Portaria/PETRVS) para os códigos brutos do banco.
ROTULO_PT = {
    "INCLUIDO": "Rascunho",
    "AGUARDANDO_ASSINATURA": "Aguardando assinatura",
    "ATIVO": "Em execução",
    "CONCLUIDO": "Concluído",
    "SUSPENSO": "Suspenso",
    "CANCELADO": "Cancelado",
}

# Status abertos = exigem ação de alguém. CONCLUIDO/CANCELADO são histórico.
STATUS_ABERTOS = ("INCLUIDO", "AGUARDANDO_ASSINATURA", "ATIVO", "SUSPENSO")

# D17/F1: universo padrão = planos abertos + planos CONCLUIDO que ainda têm período
# entregue e não avaliado. O encerramento automático por data não esvazia a fila
# da chefia; sem essa condição, esses planos sumiam do painel embora a derivação
# os classifique como "Aguardando avaliação".
FILTRO_UNIVERSO_PADRAO = (
    "AND (pt.status IN ({abertos}) "
    "OR (pt.status = 'CONCLUIDO' AND c.qtd_aguardando_avaliacao > 0))"
)

# D14: produtos de uso interno da unidade, que trazem identificação nominal.
# "compartilhavel" fica de fora — é o único que circula fora da unidade.
PRODUTOS_NOMINAIS = ("operacional", "restrito")

SQL_IND_GEST_01 = """
WITH trilha AS (
    SELECT sj.plano_trabalho_id AS pid,
           sj.codigo            AS cod,
           MAX(sj.created_at)   AS dt
    FROM petrvs_icmbio_status_justificativas sj
    WHERE sj.deleted_at IS NULL
      AND sj.plano_trabalho_id IS NOT NULL
    GROUP BY sj.plano_trabalho_id, sj.codigo
),
-- D17/F3: a trilha tem transições com o mesmo (plano, código, created_at)
-- (140 grupos em 13.09.2026). Juntar a trilha bruta por created_at = MAX
-- duplicava o plano no painel; o responsável é resolvido aqui, uma linha por
-- (plano, código, data).
responsavel AS (
    SELECT sj.plano_trabalho_id AS pid,
           sj.codigo            AS cod,
           sj.created_at        AS dt,
           MAX(sj.usuario_id)   AS usuario_id
    FROM petrvs_icmbio_status_justificativas sj
    WHERE sj.deleted_at IS NULL
      AND sj.plano_trabalho_id IS NOT NULL
    GROUP BY sj.plano_trabalho_id, sj.codigo, sj.created_at
),
consolidacao AS (
    SELECT c.plano_trabalho_id AS pid,
           SUM(CASE WHEN c.status = 'CONCLUIDO' THEN 1 ELSE 0 END) AS qtd_aguardando_avaliacao,
           SUM(CASE WHEN c.status = 'INCLUIDO'  THEN 1 ELSE 0 END) AS qtd_periodos_abertos,
           SUM(CASE WHEN c.status = 'AVALIADO'  THEN 1 ELSE 0 END) AS qtd_periodos_avaliados,
           COUNT(*)                                                AS qtd_periodos_total,
           MAX(CASE WHEN c.status = 'CONCLUIDO' THEN c.data_fim END) AS periodo_pendente_fim
    FROM petrvs_icmbio_planos_trabalhos_consolidacoes c
    WHERE c.deleted_at IS NULL
    GROUP BY c.plano_trabalho_id
)
SELECT
    pt.id                                          AS plano_trabalho_id,
    u.sigla                                        AS unidade_sigla,
    u.nome                                         AS unidade_nome,
    up.sigla                                       AS unidade_pai_sigla,
    pt.usuario_id                                  AS id_servidor,
    us.nome                                        AS servidor_nome,
    pt.numero                                      AS plano_numero,
    CAST(pt.data_inicio AS DATE)                   AS plano_inicio,
    CAST(pt.data_fim AS DATE)                      AS plano_fim,
    pt.status                                      AS status_codigo,
    t.dt                                           AS status_desde_trilha,
    pt.updated_at                                  AS plano_updated_at,
    pt.avaliado_at                                 AS plano_avaliado_at,
    COALESCE(c.qtd_aguardando_avaliacao, 0)        AS periodos_aguardando_avaliacao,
    COALESCE(c.qtd_periodos_abertos, 0)            AS periodos_em_preenchimento,
    COALESCE(c.qtd_periodos_avaliados, 0)          AS periodos_avaliados,
    COALESCE(c.qtd_periodos_total, 0)              AS periodos_total,
    c.periodo_pendente_fim                         AS periodo_pendente_fim,
    resp.nome                                      AS status_alterado_por
FROM petrvs_icmbio_planos_trabalhos pt
JOIN petrvs_icmbio_unidades  u  ON u.id  = pt.unidade_id AND u.deleted_at IS NULL
JOIN petrvs_icmbio_usuarios  us ON us.id = pt.usuario_id AND us.deleted_at IS NULL
LEFT JOIN petrvs_icmbio_unidades up ON up.id = u.unidade_pai_id AND up.deleted_at IS NULL
LEFT JOIN trilha t ON t.pid = pt.id AND t.cod = pt.status
LEFT JOIN responsavel r ON r.pid = t.pid AND r.cod = t.cod AND r.dt = t.dt
-- D17/F4: exceção declarada à regra de soft-delete. Quem executou a transição
-- é fato de auditoria e continua valendo se o usuário foi desativado depois.
LEFT JOIN petrvs_icmbio_usuarios resp ON resp.id = r.usuario_id
LEFT JOIN consolidacao c ON c.pid = pt.id
WHERE pt.deleted_at IS NULL
  {filtro_status}
  {filtro_unidade}
ORDER BY u.sigla, us.nome, pt.numero
"""

SQL_UNIDADES_FILHAS = """
SELECT f.sigla
FROM petrvs_icmbio_unidades f
JOIN petrvs_icmbio_unidades p ON p.id = f.unidade_pai_id AND p.deleted_at IS NULL
WHERE f.deleted_at IS NULL
  AND UPPER(p.sigla) IN ({siglas})
"""


def quote_list(valores) -> str:
    """Monta uma lista SQL de literais com escape de aspas simples."""
    partes = []
    for valor in valores:
        escapado = str(valor).replace("'", "''")
        partes.append("'" + escapado + "'")
    return ", ".join(partes)


def run_query(conn, sql: str) -> tuple[list[str], list[list]]:
    stmt = conn.createStatement()
    rs = stmt.executeQuery(sql)
    meta = rs.getMetaData()
    total = meta.getColumnCount()
    cols = [str(meta.getColumnLabel(i + 1)) for i in range(total)]
    rows: list[list] = []
    while rs.next():
        rows.append([clean(rs.getObject(i + 1)) for i in range(total)])
    rs.close()
    stmt.close()
    return cols, rows


def expandir_subordinadas(conn, siglas: list[str], niveis: int = 3) -> list[str]:
    """Denodo VQL não tem CTE recursiva — expande a hierarquia por iteração."""
    acumulado = {s.upper() for s in siglas}
    fronteira = set(acumulado)
    for _ in range(niveis):
        if not fronteira:
            break
        sql = SQL_UNIDADES_FILHAS.format(siglas=quote_list(sorted(fronteira)))
        _, rows = run_query(conn, sql)
        filhas = {r[0].upper() for r in rows if r[0]}
        fronteira = filhas - acumulado
        acumulado |= filhas
    if fronteira:
        # D17/F10: há unidades 4 níveis abaixo de CGGP/DIPLAN; o corte não pode
        # ser silencioso.
        sql = SQL_UNIDADES_FILHAS.format(siglas=quote_list(sorted(fronteira)))
        _, rows = run_query(conn, sql)
        restantes = {r[0].upper() for r in rows if r[0]} - acumulado
        if restantes:
            print(f"AVISO: hierarquia cortada em {niveis} níveis; {len(restantes)} "
                  "unidade(s) mais profunda(s) ficaram fora. Use --niveis para ampliar.")
    return sorted(acumulado)


def montar_painel(resumo: dict[tuple[str, str], int], produto: str) -> list[list]:
    """Painel unidade × status. No compartilhável: k<5 e supressão complementar.

    D17/F11: suprimir só a célula pequena não basta. Se numa unidade uma única
    célula foi ocultada, qualquer total da unidade divulgado em outro produto
    permite deduzi-la; por isso a menor célula visível da mesma unidade também
    é ocultada.
    """
    linhas = [
        {"unidade_sigla": u, "status_negocio": s, "qtd_planos": n,
         "suprimido": produto == "compartilhavel" and n < K_MIN}
        for (u, s), n in sorted(resumo.items(), key=lambda kv: (kv[0][0], -kv[1]))
    ]
    if produto == "compartilhavel":
        apply_complementary_suppression(
            linhas, parent_keys=["unidade_sigla"], count_key="qtd_planos"
        )
    return [
        [linha["unidade_sigla"], linha["status_negocio"],
         "SUPRIMIDO_K" if linha["suprimido"] else linha["qtd_planos"]]
        for linha in linhas
    ]


def derivar_status_negocio(
    registro: dict, *, incluir_nome: bool = True
) -> tuple[str, str, str, str]:
    """Retorna (status_negocio, data_status, origem_data, acao_sugerida)."""
    codigo = registro["status_codigo"]
    aguardando = int(registro["periodos_aguardando_avaliacao"] or 0)
    servidor = registro["servidor_nome"] if incluir_nome else "o servidor responsável"

    # Camada 2 tem precedência: um período enviado e não avaliado é a pendência
    # mais acionável para a chefia, mesmo com o plano ainda ATIVO.
    if aguardando > 0 and codigo in ("ATIVO", "CONCLUIDO"):
        status = "Aguardando avaliação"
        acao = f"Chefia deve avaliar {aguardando} período(s) já entregue(s) por {servidor}."
    else:
        status = ROTULO_PT.get(codigo, codigo)
        if codigo == "INCLUIDO":
            acao = f"Rascunho não enviado — cobrar {servidor} a submeter o plano."
        elif codigo == "AGUARDANDO_ASSINATURA":
            acao = f"Coletar assinatura de {servidor} e/ou da chefia (TCR pendente)."
        elif codigo == "ATIVO":
            abertos = int(registro["periodos_em_preenchimento"] or 0)
            if abertos:
                acao = f"Em execução — {abertos} período(s) em preenchimento por {servidor}."
            else:
                acao = "Em execução — sem pendência de período no momento."
        elif codigo == "CONCLUIDO":
            acao = "Encerrado, sem período pendente de avaliação — nenhuma ação."
        elif codigo == "SUSPENSO":
            acao = f"Plano suspenso — verificar com {servidor} o motivo e a retomada."
        else:
            acao = "Plano cancelado — nenhuma ação."

    trilha = registro["status_desde_trilha"]
    if trilha:
        return status, trilha, "trilha_status_justificativas", acao
    return status, registro["plano_updated_at"], "fallback_updated_at", acao


def dias_parado(data_status: str, hoje: date) -> str:
    if not data_status:
        return ""
    try:
        base = datetime.strptime(data_status[:10], "%Y-%m-%d").date()
    except ValueError:
        return ""
    # D17/F7: o Denodo é ao vivo. Com --data-execucao retroativa, uma transição
    # posterior à fotografia daria dias negativos; sai vazio em vez de um número falso.
    if base > hoje:
        return ""
    return str((hoje - base).days)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unidade", action="append", default=[],
                        help="Sigla da unidade (repetível ou separada por vírgula).")
    parser.add_argument("--incluir-subordinadas", action="store_true",
                        help="Inclui as unidades filhas na hierarquia.")
    parser.add_argument("--niveis", type=int, default=3,
                        help="Profundidade de --incluir-subordinadas (padrão: 3).")
    parser.add_argument("--todas", action="store_true",
                        help="Todas as unidades do ICMBio.")
    parser.add_argument("--incluir-encerrados", action="store_true",
                        help="Inclui todos os PTs CONCLUIDO/CANCELADO (padrão: abertos "
                             "e concluídos com período aguardando avaliação).")
    parser.add_argument("--out", default=None, help="Diretório de saída.")
    parser.add_argument("--data-execucao", help="Data reprodutível da fotografia (AAAA-MM-DD).")
    parser.add_argument(
        "--produto", choices=("operacional", "restrito", "compartilhavel"),
        default="operacional",
        help="operacional e restrito trazem identificação nominal para ação da chefia (D14); compartilhavel gera somente painel agregado com k>=5.",
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Valida argumentos, janela, destino e SQL sem abrir conexão.")
    args = parser.parse_args()

    siglas: list[str] = []
    for item in args.unidade:
        siglas.extend(s.strip().upper() for s in item.split(",") if s.strip())
    if not siglas and not args.todas:
        parser.error("informe --unidade SIGLA ou --todas")

    window = configure_execution_context(args.data_execucao or analysis_window().data_execucao)
    hoje = window.data_execucao
    destino = Path(args.out) if args.out else (
        _ROOT / "artefatos_local" / "gestao" / window.mes_execucao
    )
    if args.dry_run:
        print(f"Data da fotografia: {hoje.isoformat()}")
        print(f"Janela acumulada de referência: {window.inicio} a {window.fim}")
        print(f"Produto: {args.produto}")
        print(f"Destino: {destino}")
        print("Modo dry-run: nenhuma conexão Denodo será aberta.")
        return

    conn = connect(get_config())
    print("Conexao Denodo OK.")
    try:
        if siglas and args.incluir_subordinadas:
            siglas = expandir_subordinadas(conn, siglas, args.niveis)
            print(f"Hierarquia expandida: {len(siglas)} unidades.")

        filtro_unidade = ""
        if siglas:
            filtro_unidade = f"AND UPPER(u.sigla) IN ({quote_list(siglas)})"

        filtro_status = ""
        if not args.incluir_encerrados:
            filtro_status = FILTRO_UNIVERSO_PADRAO.format(abertos=quote_list(STATUS_ABERTOS))

        sql = SQL_IND_GEST_01.format(filtro_status=filtro_status,
                                   filtro_unidade=filtro_unidade)
        print("Consultando planos de trabalho...")
        cols, rows = run_query(conn, sql)
        print(f"  {len(rows)} planos retornados.")
    finally:
        conn.close()

    if not rows:
        print("Nenhum plano encontrado para o filtro informado.")
        return

    # D17/F3: uma linha por plano é invariante do painel. A chave interna só serve
    # a esta verificação e não é persistida.
    duplicados = len(rows) - len({row[0] for row in rows})
    if duplicados:
        raise RuntimeError(f"{duplicados} plano(s) duplicado(s) na consulta; painel abortado.")
    cols, rows = cols[1:], [row[1:] for row in rows]

    idx = {name: i for i, name in enumerate(cols)}
    # D26: plano com fim anterior ao início é dado inválido na origem. O G01 não usa
    # essas datas em nenhuma métrica (a duração vem da trilha de status); o registro
    # segue no painel e é contado como alerta para correção no PETRVS.
    invertidos = sum(
        1 for row in rows
        if row[idx["plano_inicio"]] and row[idx["plano_fim"]]
        and str(row[idx["plano_fim"]])[:10] < str(row[idx["plano_inicio"]])[:10]
    )
    if invertidos:
        print(f"  ALERTA_QUALIDADE (D26): {invertidos} plano(s) com data de fim anterior à de início.")
    derivadas = ["status_negocio", "data_ultima_mudanca_status", "origem_data_status",
                 "dias_no_status_atual", "acao_sugerida"]
    personal_columns = {"id_servidor", "servidor_nome", "status_alterado_por"}
    # D14: a chefia precisa dos nomes para agir; só o produto que sai da
    # unidade (compartilhavel) é despersonalizado.
    nominal = args.produto in PRODUTOS_NOMINAIS
    persisted_columns = (
        cols if nominal
        else [column for column in cols if column not in personal_columns]
    )
    out_cols = persisted_columns + derivadas
    out_rows: list[list] = []
    resumo: dict[tuple[str, str], int] = {}

    for row in rows:
        registro = {name: row[i] for name, i in idx.items()}
        status, data_status, origem, acao = derivar_status_negocio(
            registro, incluir_nome=nominal
        )
        persisted_row = (
            row if nominal
            else [row[idx[column]] for column in persisted_columns]
        )
        out_rows.append(persisted_row + [status, data_status, origem,
                                         dias_parado(data_status, hoje), acao])
        chave = (registro["unidade_sigla"], status)
        resumo[chave] = resumo.get(chave, 0) + 1

    lookup = load_mesogrupo_lookup()
    out_cols, out_rows = insert_mesogrupo_column(out_cols, out_rows, lookup)

    stamp = datetime.now(ZoneInfo(ANALYSIS_TIMEZONE)).strftime("%Y%m%d_%H%M")
    if args.todas:
        escopo = "TODAS"
    else:
        escopo = "_".join(siglas[:3])
        if len(siglas) > 3:
            escopo += f"_e_mais_{len(siglas) - 3}"

    if args.produto != "compartilhavel":
        detalhe = destino / gest_artifact("01", f"2_detalhe_{args.produto}_{escopo}_{stamp}.csv")
        write_pipe_csv(detalhe, out_cols, out_rows)
        print(f"  Salvo: {detalhe}")

    painel_cols = ["unidade_sigla", "status_negocio", "qtd_planos"]
    painel_rows = montar_painel(resumo, args.produto)
    painel = destino / gest_artifact("01", f"2_painel_{args.produto}_{escopo}_{stamp}.csv")
    write_pipe_csv(painel, painel_cols, painel_rows)
    print(f"  Salvo: {painel}")

    print("\nResumo por status:")
    totais: dict[str, int] = {}
    for (_, status), n in resumo.items():
        totais[status] = totais.get(status, 0) + n
    for status, n in sorted(totais.items(), key=lambda kv: -kv[1]):
        print(f"  {status:<26} {n:>6}")
    print(f"\nTotal: {len(out_rows)} planos | {len({u for u, _ in resumo})} unidades")


if __name__ == "__main__":
    main()
