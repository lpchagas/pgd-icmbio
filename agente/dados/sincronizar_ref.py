"""sincronizar_ref.py — Espelhos Denodo → MySQL local (AT-01 §7; v4 §3.2).

Sincroniza:
  ref_unidades  — TODAS as unidades ativas do ICMBio (~811)
  ref_usuarios  — SOMENTE servidores das unidades-piloto (D2/Q8: CGOV e COCAGE),
                  campos mínimos — sem CPF, e-mail ou situação funcional (LGPD, v4 §11)

Padrão de acesso herdado do pgd-ocde-icmbio (JDBC via jpype; restrições VQL:
CAST em datas, sem window functions, prefixo petrvs_icmbio_ obrigatório).
Upsert idempotente (INSERT ... ON DUPLICATE KEY UPDATE) com sincronizado_em.
sincronizar() não encerra a transação: main() faz commit ou rollback (DP-L2-03).

Uso:  python src/dados/sincronizar_ref.py
"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # raiz do monorepo
from db import get_conn  # noqa: E402
from lib.denodo_config import connect, get_config  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PILOTO_SIGLAS = ["CGOV", "COCAGE"]  # Q8, respondida em 26.07.2026

SQL_UNIDADES = """
SELECT id, sigla, nome, path, unidade_pai_id, executora
FROM petrvs_icmbio_unidades
WHERE deleted_at IS NULL
"""

# Lotação via composição de unidades (unidades_integrantes)
SQL_USUARIOS_INTEGRANTES = """
SELECT DISTINCT u.id, u.nome, u.matricula, u.participa_pgd, ui.unidade_id
FROM petrvs_icmbio_usuarios u
JOIN petrvs_icmbio_unidades_integrantes ui ON ui.usuario_id = u.id
JOIN petrvs_icmbio_unidades un ON un.id = ui.unidade_id
WHERE u.deleted_at IS NULL
  AND ui.deleted_at IS NULL
  AND un.deleted_at IS NULL
  AND un.sigla IN ({siglas})
"""

# Fallback: quem tem plano de trabalho na unidade-piloto
SQL_USUARIOS_PT = """
SELECT DISTINCT u.id, u.nome, u.matricula, u.participa_pgd, pt.unidade_id
FROM petrvs_icmbio_usuarios u
JOIN petrvs_icmbio_planos_trabalhos pt ON pt.usuario_id = u.id
JOIN petrvs_icmbio_unidades un ON un.id = pt.unidade_id
WHERE u.deleted_at IS NULL
  AND pt.deleted_at IS NULL
  AND un.deleted_at IS NULL
  AND un.sigla IN ({siglas})
"""


def _denodo_conn():
    """Conexão pelo adaptador único do monorepo (ADR-012), que aceita os nomes antigos como aliases."""
    return connect(get_config(require_credentials=True))


def _query(conn, sql):
    stmt = conn.createStatement()
    rs = stmt.executeQuery(sql)
    n = rs.getMetaData().getColumnCount()
    rows = []
    while rs.next():
        rows.append([rs.getObject(i + 1) for i in range(n)])
    rs.close()
    stmt.close()
    return rows


def _s(v):
    """java/None → str limpa ou None."""
    if v is None:
        return None
    s = str(v).strip()
    return s or None


def _b(v):
    """java Boolean/bit/str → 0|1."""
    return 1 if str(v).strip().lower() in ("1", "true", "sim", "b'\\x01'") else 0


def sincronizar(mysql_conn, denodo):
    agora = datetime.now().replace(microsecond=0)
    siglas = ", ".join(f"'{s}'" for s in PILOTO_SIGLAS)

    # --- ref_unidades (completa) -------------------------------------------
    unidades = _query(denodo, SQL_UNIDADES)
    with mysql_conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO ref_unidades (id, sigla, nome, path, unidade_pai_id,"
            " executora, sincronizado_em) VALUES (%s,%s,%s,%s,%s,%s,%s)"
            " ON DUPLICATE KEY UPDATE sigla=VALUES(sigla), nome=VALUES(nome),"
            " path=VALUES(path), unidade_pai_id=VALUES(unidade_pai_id),"
            " executora=VALUES(executora), sincronizado_em=VALUES(sincronizado_em)",
            [(_s(r[0]), _s(r[1]) or "?", _s(r[2]) or "?", _s(r[3]), _s(r[4]),
              _b(r[5]), agora) for r in unidades],
        )
    print(f"ref_unidades: {len(unidades)} unidades sincronizadas")

    # --- ref_usuarios (só piloto) ------------------------------------------
    try:
        usuarios = _query(denodo, SQL_USUARIOS_INTEGRANTES.format(siglas=siglas))
        origem = "unidades_integrantes"
    except Exception as e:  # coluna/view divergente → fallback documentado
        print(f"  aviso: consulta por unidades_integrantes falhou ({e});"
              f" usando fallback por planos_trabalhos")
        usuarios = _query(denodo, SQL_USUARIOS_PT.format(siglas=siglas))
        origem = "planos_trabalhos"
    with mysql_conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO ref_usuarios (id, nome, matricula, participa_pgd,"
            " unidade_id, sincronizado_em) VALUES (%s,%s,%s,%s,%s,%s)"
            " ON DUPLICATE KEY UPDATE nome=VALUES(nome), matricula=VALUES(matricula),"
            " participa_pgd=VALUES(participa_pgd), unidade_id=VALUES(unidade_id),"
            " sincronizado_em=VALUES(sincronizado_em)",
            [(_s(r[0]), _s(r[1]) or "?", _s(r[2]), _b(r[3]), _s(r[4]), agora)
             for r in usuarios],
        )
    print(f"ref_usuarios: {len(usuarios)} servidores das unidades-piloto"
          f" {PILOTO_SIGLAS} (via {origem})")


def main():
    print("Conectando ao Denodo...")
    denodo = _denodo_conn()
    print("Conexao Denodo OK. Conectando ao MySQL local...")
    mysql_conn = get_conn()
    try:
        sincronizar(mysql_conn, denodo)
        mysql_conn.commit()  # DP-L2-03: o limite da transação é do chamador
        print("Concluido.")
    except BaseException:
        mysql_conn.rollback()
        raise
    finally:
        mysql_conn.close()
        denodo.close()


if __name__ == "__main__":
    main()
