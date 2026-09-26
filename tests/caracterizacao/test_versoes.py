"""Caracterização de versoes.py: criação, recuperação, imutabilidade e transação."""
from __future__ import annotations

import json
from datetime import date

import pytest

ENTREGA = {
    "titulo": "Relatório sintético elaborado",
    "forma_geracao": "projeto",
    "natureza_resultado": "produto",
    "demandante": "UNID-A",
    "destinatario": "UNID-B",
    "meta": {"porcentagem": 100},
    "prazo_fim": "2026-12-31",
}
REGRA = {"titulo": "Regra sintética", "descricao": "d", "natureza": "n", "fonte_id": "F-1", "confianca_extracao": "alta"}


class _Hoje(date):
    @classmethod
    def today(cls):
        return cls(2026, 9, 25)


@pytest.fixture
def versoes(carregar, monkeypatch):
    modulo = carregar("versoes")
    monkeypatch.setattr(modulo, "date", _Hoje)
    return modulo


def test_importar_nao_le_env_nem_abre_conexao(versoes):
    # db é substituído; o módulo real carregaria o .env ao ser importado.
    assert versoes.get_conn is versoes._dubles["db"].get_conn


def test_criar_entrega_inicia_serie_anual_e_grava_cabecalho_e_versao_1(versoes, conexao):
    conn = conexao()

    resultado = versoes.criar_entrega(conn, ENTREGA)

    assert resultado["codigo"] == "ENT-2026-0001" and resultado["versao"] == 1
    tipos = [c[1].split(" (")[0] for c in conn.comandos]
    assert tipos == [
        "SELECT codigo FROM entregas WHERE codigo LIKE %s ORDER BY codigo DESC LIMIT 1 FOR UPDATE",
        "INSERT INTO entregas",
        "INSERT INTO entregas_versoes",
    ]
    assert conn.comandos[0][2] == ("ENT-2026-%",)
    parametros_versao = conn.comandos[2][2]
    assert parametros_versao[1] == resultado["id"]
    assert json.loads(parametros_versao[2 + versoes._CAMPOS_ENTREGA.index("meta")]) == {"porcentagem": 100}
    assert parametros_versao[-2:] == ("criação inicial", None)


def test_codigo_continua_a_serie_existente(versoes, conexao):
    assert versoes.criar_entrega(conexao(respostas=[{"codigo": "ENT-2026-0041"}]), ENTREGA)["codigo"] == "ENT-2026-0042"
    assert versoes.criar_regra(conexao(respostas=[{"codigo": "R-014"}]), REGRA)["codigo"] == "R-015"


def test_payload_incompleto_falha_depois_de_reservar_codigo_e_antes_de_inserir(versoes, conexao):
    conn = conexao()

    with pytest.raises(ValueError, match="campos obrigatórios"):
        versoes.criar_entrega(conn, {"titulo": "sem o resto"})

    assert len(conn.sql("FOR UPDATE")) == 1
    assert conn.sql("INSERT") == []


def test_nova_versao_so_insere_historico_e_avanca_ponteiro(versoes, conexao):
    conn = conexao(respostas=[{"codigo": "ENT-2026-0007", "versao_atual": 2}])

    resultado = versoes.nova_versao_entrega(conn, "id-1", ENTREGA, motivo="revisão")

    assert resultado == {"id": "id-1", "codigo": "ENT-2026-0007", "versao": 3}
    assert conn.sql("INSERT INTO entregas_versoes")[0][2][1:3] == ("id-1", 3)
    assert conn.sql("UPDATE entregas SET versao_atual")[0][2] == (3, "id-1")
    assert not [c for c in conn.comandos if c[1].startswith(("UPDATE entregas_versoes", "DELETE"))]


def test_nova_versao_exige_motivo_e_cabecalho_existente(versoes, conexao):
    conn = conexao()
    with pytest.raises(ValueError, match="motivo_versao"):
        versoes.nova_versao_entrega(conn, "id-1", ENTREGA, motivo="  ")
    assert conn.comandos == []

    with pytest.raises(LookupError):
        versoes.nova_versao_entrega(conn, "id-inexistente", ENTREGA, motivo="revisão")
    assert conn.sql("INSERT") == []


def test_obter_entrega_usa_versao_atual_por_padrao(versoes, conexao):
    conn = conexao(respostas=[{"versao": 2}, {"versao": 1}])

    assert versoes.obter_entrega(conn, "id-1") == {"versao": 2}
    assert versoes.obter_entrega(conn, "id-1", versao=1) == {"versao": 1}
    assert [c[2] for c in conn.comandos] == [(None, "id-1"), (1, "id-1")]
    assert "COALESCE(%s, e.versao_atual)" in conn.comandos[0][1]


def test_funcoes_nao_encerram_a_transacao(versoes, conexao):
    conn = conexao(respostas=[None, {"codigo": "ENT-2026-0001", "versao_atual": 1}])

    xid = versoes.registrar_execucao(conn, skill="S00", versao_skill="0", entrada=None, saida={"ok": True})
    entrega = versoes.criar_entrega(conn, ENTREGA, execucao_id=xid)
    versoes.nova_versao_entrega(conn, entrega["id"], ENTREGA, motivo="revisão", execucao_id=xid)
    versoes.registrar_pergunta(conn, objeto_tipo="entrega", objeto_id=entrega["id"], pergunta="?", execucao_id=xid)
    versoes.registrar_decisao(conn, objeto_tipo="entrega", objeto_id=entrega["id"], decisao="aprovado", decidido_por="teste")

    assert (conn.commits, conn.rollbacks, conn.fechada) == (0, 0, False)
    parametros = conn.sql("INSERT INTO execucoes_skill")[0][2]
    assert parametros[4:6] == ("{}", '{"ok": true}')
    assert parametros[9] == 0


def test_falha_intermediaria_propaga_sem_commit(versoes, conexao, falha_injetada):
    conn = conexao(falhar_quando="INSERT INTO entregas_versoes")

    with pytest.raises(falha_injetada):
        versoes.criar_entrega(conn, ENTREGA)

    assert len(conn.sql("INSERT INTO entregas ")) == 1  # cabeçalho já enviado
    assert conn.commits == 0 and conn.rollbacks == 0   # desfazer cabe ao chamador


def test_smoke_faz_rollback_e_fecha_mesmo_com_falha(versoes, conexao, falha_injetada, monkeypatch):
    conn = conexao(falhar_quando="INSERT INTO entregas_versoes")
    monkeypatch.setattr(versoes, "get_conn", lambda: conn)

    with pytest.raises(falha_injetada):
        versoes._teste()

    assert (conn.commits, conn.rollbacks, conn.fechada) == (0, 1, True)


def test_defeito_conhecido_criar_entrega_nao_e_idempotente(versoes, conexao):
    """Registro de defeito preexistente (plano §9.2): pendência de ativação, não corrigida no L2."""

    conn = conexao()
    primeira = versoes.criar_entrega(conn, ENTREGA)
    segunda = versoes.criar_entrega(conn, ENTREGA)

    assert primeira["id"] != segunda["id"]
    assert len(conn.sql("INSERT INTO entregas ")) == 2
