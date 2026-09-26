"""versoes.py — Serviço de IDs e versões do modelo comum (v4 §3.2; AT-01 §6).

Única via de escrita para entidades versionáveis. Implementa as regras de ouro:

1. ID persistente        → UUID v4 + código legível (D3: "ENT-2026-0001", "R-014")
2. Nunca sobrescrever    → nova_versao_*() só INSERE em *_versoes e avança o
                           ponteiro versao_atual do cabeçalho (triggers no banco
                           rejeitam UPDATE/DELETE no histórico — AT-01 §6.3)
3. Rastreio de origem    → registrar_execucao() grava o contrato v4 §8.3 integral
4. Decisão humana à parte→ registrar_decisao()
5. Ausência vira pergunta→ registrar_pergunta()

Convenção transacional: todas as funções recebem `conn` e NÃO commitam —
o chamador decide o limite da transação (e o self-test usa rollback).

Uso:  python src/dados/versoes.py --teste   (smoke test com rollback; não grava nada)
"""

import argparse
import json
import sys
import uuid
from datetime import date

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from db import get_conn  # noqa: E402

# (tabela do cabeçalho, prefixo do código, largura do sequencial, código anual?)
_SERIES = {
    "entrega": ("entregas", "ENT", 4, True),
    "regra": ("regras_institucionais", "R", 3, False),
}


def novo_id() -> str:
    """UUID v4 — nunca colide com os UUIDs do PETRVS (convenção herdada)."""
    return str(uuid.uuid4())


def novo_codigo(conn, serie: str) -> str:
    """Próximo código legível da série ('ENT-2026-0001', 'R-014').

    Usa SELECT ... FOR UPDATE sobre o maior código existente para evitar
    corrida entre duas gerações concorrentes na mesma transação-pai.
    """
    tabela, prefixo, largura, anual = _SERIES[serie]
    base = f"{prefixo}-{date.today().year}-" if anual else f"{prefixo}-"
    with conn.cursor() as cur:
        cur.execute(
            f"SELECT codigo FROM {tabela} WHERE codigo LIKE %s "
            f"ORDER BY codigo DESC LIMIT 1 FOR UPDATE",
            (base + "%",),
        )
        row = cur.fetchone()
    seq = int(row["codigo"].rsplit("-", 1)[1]) + 1 if row else 1
    return f"{base}{seq:0{largura}d}"


# ---------------------------------------------------------------------------
# Entregas (cabeçalho `entregas` + payload em `entregas_versoes`)
# ---------------------------------------------------------------------------

_CAMPOS_ENTREGA = [
    "titulo", "descricao", "forma_geracao", "natureza_resultado", "demandante",
    "destinatario", "meta", "meta_final", "progresso_esperado", "prazo_inicio",
    "prazo_fim", "criterios_aceite", "evidencias_esperadas",
]
_CAMPOS_JSON = {"meta", "meta_final", "criterios_aceite", "evidencias_esperadas"}


def _payload_entrega(payload: dict) -> dict:
    faltantes = {"titulo", "forma_geracao", "natureza_resultado", "demandante",
                 "destinatario", "meta", "prazo_fim"} - payload.keys()
    if faltantes:
        raise ValueError(f"payload de entrega sem campos obrigatórios: {sorted(faltantes)}")
    row = {c: payload.get(c) for c in _CAMPOS_ENTREGA}
    for c in _CAMPOS_JSON:
        if row[c] is not None and not isinstance(row[c], str):
            row[c] = json.dumps(row[c], ensure_ascii=False)
    return row


def criar_entrega(conn, payload: dict, *, unidade_id=None, candidata_origem_id=None,
                  entrega_referencia_id=None, execucao_id=None,
                  motivo="criação inicial") -> dict:
    """Cria cabeçalho + versão 1. Devolve {'id', 'codigo', 'versao'}."""
    eid, codigo = novo_id(), novo_codigo(conn, "entrega")
    row = _payload_entrega(payload)
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO entregas (id, codigo, versao_atual, unidade_id,"
            " candidata_origem_id, entrega_referencia_id) VALUES (%s,%s,1,%s,%s,%s)",
            (eid, codigo, unidade_id, candidata_origem_id, entrega_referencia_id),
        )
        cur.execute(
            f"INSERT INTO entregas_versoes (id, entrega_id, versao,"
            f" {', '.join(_CAMPOS_ENTREGA)}, motivo_versao, execucao_id)"
            f" VALUES (%s,%s,1,{','.join(['%s'] * len(_CAMPOS_ENTREGA))},%s,%s)",
            (novo_id(), eid, *[row[c] for c in _CAMPOS_ENTREGA], motivo, execucao_id),
        )
    return {"id": eid, "codigo": codigo, "versao": 1}


def nova_versao_entrega(conn, entrega_id: str, payload: dict, *, motivo: str,
                        execucao_id=None) -> dict:
    """Regra de ouro 2: INSERT da versão n+1; a anterior permanece intocada."""
    if not motivo or not motivo.strip():
        raise ValueError("motivo_versao é obrigatório")
    row = _payload_entrega(payload)
    with conn.cursor() as cur:
        cur.execute("SELECT codigo, versao_atual FROM entregas"
                    " WHERE id = %s AND deleted_at IS NULL FOR UPDATE", (entrega_id,))
        cab = cur.fetchone()
        if not cab:
            raise LookupError(f"entrega {entrega_id} inexistente ou excluída")
        nova = cab["versao_atual"] + 1
        cur.execute(
            f"INSERT INTO entregas_versoes (id, entrega_id, versao,"
            f" {', '.join(_CAMPOS_ENTREGA)}, motivo_versao, execucao_id)"
            f" VALUES (%s,%s,%s,{','.join(['%s'] * len(_CAMPOS_ENTREGA))},%s,%s)",
            (novo_id(), entrega_id, nova, *[row[c] for c in _CAMPOS_ENTREGA],
             motivo, execucao_id),
        )
        cur.execute("UPDATE entregas SET versao_atual = %s WHERE id = %s",
                    (nova, entrega_id))
    return {"id": entrega_id, "codigo": cab["codigo"], "versao": nova}


def obter_entrega(conn, entrega_id: str, versao: int | None = None) -> dict | None:
    """Versão atual (default) ou uma versão específica do histórico."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT e.codigo, e.estado, e.unidade_id, v.* FROM entregas e"
            " JOIN entregas_versoes v ON v.entrega_id = e.id"
            " AND v.versao = COALESCE(%s, e.versao_atual)"
            " WHERE e.id = %s AND e.deleted_at IS NULL",
            (versao, entrega_id),
        )
        return cur.fetchone()


# ---------------------------------------------------------------------------
# Regras institucionais (cabeçalho + versões) — mesmo padrão
# ---------------------------------------------------------------------------

_CAMPOS_REGRA = [
    "titulo", "descricao", "natureza", "fonte_id", "localizacao_fonte",
    "inicio_vigencia", "fim_vigencia", "confianca_extracao",
]


def criar_regra(conn, payload: dict, *, status="pendente", execucao_id=None) -> dict:
    faltantes = {"titulo", "descricao", "natureza", "fonte_id",
                 "confianca_extracao"} - payload.keys()
    if faltantes:
        raise ValueError(f"payload de regra sem campos obrigatórios: {sorted(faltantes)}")
    rid, codigo = novo_id(), novo_codigo(conn, "regra")
    with conn.cursor() as cur:
        cur.execute("INSERT INTO regras_institucionais (id, codigo, versao_atual, status)"
                    " VALUES (%s,%s,1,%s)", (rid, codigo, status))
        cur.execute(
            f"INSERT INTO regras_institucionais_versoes (id, regra_id, versao,"
            f" {', '.join(_CAMPOS_REGRA)}, execucao_id)"
            f" VALUES (%s,%s,1,{','.join(['%s'] * len(_CAMPOS_REGRA))},%s)",
            (novo_id(), rid, *[payload.get(c) for c in _CAMPOS_REGRA], execucao_id),
        )
    return {"id": rid, "codigo": codigo, "versao": 1}


def nova_versao_regra(conn, regra_id: str, payload: dict, *, execucao_id=None) -> dict:
    with conn.cursor() as cur:
        cur.execute("SELECT codigo, versao_atual FROM regras_institucionais"
                    " WHERE id = %s AND deleted_at IS NULL FOR UPDATE", (regra_id,))
        cab = cur.fetchone()
        if not cab:
            raise LookupError(f"regra {regra_id} inexistente ou excluída")
        nova = cab["versao_atual"] + 1
        cur.execute(
            f"INSERT INTO regras_institucionais_versoes (id, regra_id, versao,"
            f" {', '.join(_CAMPOS_REGRA)}, execucao_id)"
            f" VALUES (%s,%s,%s,{','.join(['%s'] * len(_CAMPOS_REGRA))},%s)",
            (novo_id(), regra_id, nova, *[payload.get(c) for c in _CAMPOS_REGRA],
             execucao_id),
        )
        cur.execute("UPDATE regras_institucionais SET versao_atual = %s WHERE id = %s",
                    (nova, regra_id))
    return {"id": regra_id, "codigo": cab["codigo"], "versao": nova}


# ---------------------------------------------------------------------------
# Governança: execuções, decisões humanas, perguntas pendentes
# ---------------------------------------------------------------------------

def registrar_execucao(conn, *, skill: str, versao_skill: str, entrada, saida,
                       modelo=None, confianca=None, regras_aplicadas=None,
                       fontes=None, requer_validacao_humana=False,
                       duracao_ms=None) -> str:
    """Regra de ouro 3 — persiste o contrato v4 §8.3. Devolve o rastreio_id."""
    xid = novo_id()
    dump = lambda v: v if v is None or isinstance(v, str) else json.dumps(v, ensure_ascii=False)  # noqa: E731
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO execucoes_skill (id, skill, versao_skill, modelo, entrada,"
            " saida, confianca, regras_aplicadas, fontes, requer_validacao_humana,"
            " duracao_ms) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (xid, skill, versao_skill, modelo, dump(entrada) or "{}",
             dump(saida) or "{}", confianca, dump(regras_aplicadas), dump(fontes),
             int(bool(requer_validacao_humana)), duracao_ms),
        )
    return xid


def registrar_decisao(conn, *, objeto_tipo: str, objeto_id: str, decisao: str,
                      decidido_por: str, objeto_versao=None, justificativa=None,
                      execucao_id=None) -> str:
    """Regra de ouro 4 — decisão humana separada da sugestão do agente."""
    did = novo_id()
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO decisoes_humanas (id, objeto_tipo, objeto_id, objeto_versao,"
            " decisao, justificativa, decidido_por, execucao_id)"
            " VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (did, objeto_tipo, objeto_id, objeto_versao, decisao, justificativa,
             decidido_por, execucao_id),
        )
    return did


def registrar_pergunta(conn, *, objeto_tipo: str, objeto_id: str, pergunta: str,
                       execucao_id: str) -> str:
    """Regra de ouro 5 — dado ausente vira pergunta registrada, nunca palpite."""
    pid = novo_id()
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO perguntas_pendentes (id, objeto_tipo, objeto_id, pergunta,"
            " execucao_id) VALUES (%s,%s,%s,%s,%s)",
            (pid, objeto_tipo, objeto_id, pergunta, execucao_id),
        )
    return pid


# ---------------------------------------------------------------------------
# Smoke test (rollback ao final — não grava nada)
# ---------------------------------------------------------------------------

def _teste():
    conn = get_conn()
    try:
        xid = registrar_execucao(conn, skill="S00", versao_skill="0.0-teste",
                                 entrada={"origem": "smoke"}, saida={"ok": True},
                                 confianca="alta")
        ent = criar_entrega(conn, {
            "titulo": "Relatório de teste elaborado",
            "forma_geracao": "projeto", "natureza_resultado": "produto",
            "demandante": "CGOV", "destinatario": "COCAGE",
            "meta": {"porcentagem": 100}, "prazo_fim": "2026-12-31",
        }, execucao_id=xid)
        v2 = nova_versao_entrega(conn, ent["id"], {
            "titulo": "Relatório de teste revisado e elaborado",
            "forma_geracao": "projeto", "natureza_resultado": "produto",
            "demandante": "CGOV", "destinatario": "COCAGE",
            "meta": {"porcentagem": 100}, "prazo_fim": "2026-12-31",
        }, motivo="teste de versionamento", execucao_id=xid)
        atual = obter_entrega(conn, ent["id"])
        v1 = obter_entrega(conn, ent["id"], versao=1)
        registrar_pergunta(conn, objeto_tipo="entrega", objeto_id=ent["id"],
                           pergunta="Qual produto existirá ao final?", execucao_id=xid)
        registrar_decisao(conn, objeto_tipo="entrega", objeto_id=ent["id"],
                          objeto_versao=2, decisao="aprovado", decidido_por="smoke-test")
        assert ent["codigo"].startswith("ENT-"), ent
        assert v2["versao"] == 2 and atual["versao"] == 2, (v2, atual)
        assert v1["titulo"] == "Relatório de teste elaborado", v1
        print(f"OK  execucao={xid[:8]}...  {ent['codigo']} v1->v{atual['versao']}"
              f"  (historico v1 preservado: '{v1['titulo']}')")
    finally:
        conn.rollback()
        conn.close()
        print("Rollback executado — nenhum dado gravado.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--teste", action="store_true", help="smoke test com rollback")
    if ap.parse_args().teste:
        _teste()
    else:
        ap.print_help()
