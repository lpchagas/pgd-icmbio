"""PT_STATUS.1_run.py — Situação dos Planos de Trabalho por unidade organizacional.

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
    python gestao/PT_STATUS.1_run.py --unidade CGGP
    python gestao/PT_STATUS.1_run.py --unidade CGGP --incluir-subordinadas
    python gestao/PT_STATUS.1_run.py --todas
    python gestao/PT_STATUS.1_run.py --unidade CGGP --incluir-encerrados
"""
from __future__ import annotations

import argparse
import sys
from datetime import date, datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from lib.csv_utils import PROJECT_ROOT as _ROOT, clean, write_pipe_csv  # noqa: E402
from lib.denodo_config import connect, get_config  # noqa: E402
from lib.periodos import analysis_window, configure_execution_context  # noqa: E402
from lib.estrutura_organizacional import (  # noqa: E402
    insert_mesogrupo_column,
    load_mesogrupo_lookup,
)

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

# D14: produtos de uso interno da unidade, que trazem identificação nominal.
# "compartilhavel" fica de fora — é o único que circula fora da unidade.
PRODUTOS_NOMINAIS = ("operacional", "restrito")

SQL_PT_STATUS = """
WITH trilha AS (
    SELECT sj.plano_trabalho_id AS pid,
           sj.codigo            AS cod,
           MAX(sj.created_at)   AS dt
    FROM petrvs_icmbio_status_justificativas sj
    WHERE sj.deleted_at IS NULL
      AND sj.plano_trabalho_id IS NOT NULL
    GROUP BY sj.plano_trabalho_id, sj.codigo
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
LEFT JOIN petrvs_icmbio_status_justificativas sjr
       ON sjr.plano_trabalho_id = pt.id
      AND sjr.codigo = pt.status
      AND sjr.created_at = t.dt
      AND sjr.deleted_at IS NULL
LEFT JOIN petrvs_icmbio_usuarios resp ON resp.id = sjr.usuario_id
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
    return sorted(acumulado)


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
            acao = "Encerrado e avaliado — nenhuma ação."
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
    return str((hoje - base).days)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unidade", action="append", default=[],
                        help="Sigla da unidade (repetível ou separada por vírgula).")
    parser.add_argument("--incluir-subordinadas", action="store_true",
                        help="Inclui as unidades filhas na hierarquia (até 3 níveis).")
    parser.add_argument("--todas", action="store_true",
                        help="Todas as unidades do ICMBio.")
    parser.add_argument("--incluir-encerrados", action="store_true",
                        help="Inclui PTs CONCLUIDO/CANCELADO (padrão: só os abertos).")
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
            siglas = expandir_subordinadas(conn, siglas)
            print(f"Hierarquia expandida: {len(siglas)} unidades.")

        filtro_unidade = ""
        if siglas:
            filtro_unidade = f"AND UPPER(u.sigla) IN ({quote_list(siglas)})"

        filtro_status = ""
        if not args.incluir_encerrados:
            filtro_status = f"AND pt.status IN ({quote_list(STATUS_ABERTOS)})"

        sql = SQL_PT_STATUS.format(filtro_status=filtro_status,
                                   filtro_unidade=filtro_unidade)
        print("Consultando planos de trabalho...")
        cols, rows = run_query(conn, sql)
        print(f"  {len(rows)} planos retornados.")
    finally:
        conn.close()

    if not rows:
        print("Nenhum plano encontrado para o filtro informado.")
        return

    idx = {name: i for i, name in enumerate(cols)}
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

    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    if args.todas:
        escopo = "TODAS"
    else:
        escopo = "_".join(siglas[:3])
        if len(siglas) > 3:
            escopo += f"_e_mais_{len(siglas) - 3}"

    if args.produto != "compartilhavel":
        detalhe = destino / f"PT_STATUS.2_detalhe_{args.produto}_{escopo}_{stamp}.csv"
        write_pipe_csv(detalhe, out_cols, out_rows)
        print(f"  Salvo: {detalhe}")

    painel_cols = ["unidade_sigla", "status_negocio", "qtd_planos"]
    painel_rows = [
        [u, s, n if args.produto != "compartilhavel" or n >= 5 else "SUPRIMIDO_K"]
        for (u, s), n in sorted(resumo.items(), key=lambda kv: (kv[0][0], -kv[1]))
    ]
    painel = destino / f"PT_STATUS.2_painel_{args.produto}_{escopo}_{stamp}.csv"
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
