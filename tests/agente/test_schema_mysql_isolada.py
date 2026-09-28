"""Schema aplicado na instância MySQL isolada (opt-in: -m mysql e PGD_MYSQL_TESTE=1).

Usa só o usuário restrito a ``pgd_agente_teste`` (``teste.cnf`` da instância criada
por ``agente/dados/mysql_isolada.ps1``); nunca o ``.cnf`` administrativo do backup.
"""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

import pytest

pytestmark = [
    pytest.mark.mysql,
    pytest.mark.skipif(os.environ.get("PGD_MYSQL_TESTE") != "1", reason="defina PGD_MYSQL_TESTE=1"),
]

DADOS = Path(__file__).resolve().parents[2] / "agente" / "dados"
_spec = importlib.util.spec_from_file_location("banco_teste", DADOS / "banco_teste.py")
bt = importlib.util.module_from_spec(_spec)
sys.modules["banco_teste"] = bt  # dataclasses resolvem o módulo por nome
_spec.loader.exec_module(bt)


def test_schema_aplicado_no_banco_de_teste_com_imutabilidade():
    resultado = bt.preparar(bt.diretorio_instancia())

    assert resultado["conferencia"]["privilegios"] == "restritos a pgd_agente_teste"
    assert resultado["resumo"] == {
        "banco": "pgd_agente_teste", "tabelas": 21, "triggers": 6, "versao_schema": "001",
        "transacao_funcional": {"trigger_imutabilidade_bloqueou_update": True, "rollback_restaurou_contagem": True},
    }


def test_usuario_de_teste_nao_alcanca_o_banco_de_producao():
    import pymysql

    conn = bt.conectar(bt.ler_cnf(bt.diretorio_instancia() / "teste.cnf"))
    try:
        with conn.cursor() as cur, pytest.raises(pymysql.err.OperationalError):
            cur.execute("SELECT COUNT(*) FROM pgd_agente.schema_migracoes")
    finally:
        conn.close()
