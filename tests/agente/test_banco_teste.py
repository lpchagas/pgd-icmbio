"""Banco de teste e backup do agente (plano §10, L6), sem MySQL.

A reescrita para ``pgd_agente_teste`` recusa qualquer SQL que ainda cite
``pgd_agente``; a conferência da conexão recusa a instância principal, outro
datadir e privilégios além do banco de teste; o ``backup.ps1`` (e o ``backup.sh``) só aceita destino
absoluto, fora da raiz do disco e fora de pasta versionada não ignorada.
"""
from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
DADOS = RAIZ / "agente" / "dados"

_spec = importlib.util.spec_from_file_location("banco_teste", DADOS / "banco_teste.py")
bt = importlib.util.module_from_spec(_spec)
sys.modules["banco_teste"] = bt  # dataclasses resolvem o módulo por nome
_spec.loader.exec_module(bt)


# --- Reescrita e recusa ----------------------------------------------------------------------

def test_schema_real_e_reescrito_so_para_o_banco_de_teste():
    comandos = bt.reescrever_para_teste((DADOS / "schema.sql").read_text(encoding="utf-8"))

    assert comandos[0].startswith("CREATE DATABASE IF NOT EXISTS pgd_agente_teste")
    assert comandos[1] == "USE pgd_agente_teste"
    assert sum(c.startswith("CREATE TABLE") for c in comandos) == 21
    assert sum(c.startswith("CREATE TRIGGER") for c in comandos) == 6
    assert not any(bt._PRODUCAO.search(c) for c in comandos)


def test_comentario_com_ponto_e_virgula_nao_quebra_instrucao():
    sql = "CREATE TABLE t (\n  a INT NULL, -- preenchido depois;\n  b INT\n);\nINSERT INTO t VALUES (1, 2); # fim;"
    assert bt.instrucoes(sql) == ["CREATE TABLE t (\n  a INT NULL, \n  b INT\n)", "INSERT INTO t VALUES (1, 2)"]


def test_literal_com_ponto_e_virgula_e_hifens_e_preservado():
    sql = "INSERT INTO t VALUES ('a; -- b', \"c;d\");"
    assert bt.instrucoes(sql) == ["INSERT INTO t VALUES ('a; -- b', \"c;d\")"]


@pytest.mark.parametrize("sql", [
    "USE pgd_agente_teste; INSERT INTO pgd_agente.execucoes_skill VALUES (1);",
    "USE pgd_agente_teste; SELECT * FROM `pgd_agente`.ref_unidades;",
    "USE mysql;",
    "CREATE DATABASE outro_banco;",
    "USE pgd_agente_teste; DROP DATABASE pgd_agente;",
    "USE pgd_agente_teste; GRANT ALL ON pgd_agente.* TO x;",
])
def test_sql_que_ainda_aponta_para_outro_banco_e_recusado(sql):
    with pytest.raises(bt.SQLRecusado):
        bt.reescrever_para_teste(sql)


# --- Conferência da conexão -----------------------------------------------------------------

class _Cursor:
    def __init__(self, linha, concessoes):
        self.linha, self.concessoes, self._ultimo = linha, concessoes, None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, sql, params=None):
        self._ultimo = sql

    def fetchone(self):
        return self.linha

    def fetchall(self):
        return [(c,) for c in self.concessoes]


class _Conexao:
    def __init__(self, porta=3307, datadir="C:/inst/data/", conta="pgd_teste@localhost", banco=None,
                 concessoes=("GRANT USAGE ON *.* TO `pgd_teste`@`localhost`",
                             "GRANT ALL PRIVILEGES ON `pgd_agente_teste`.* TO `pgd_teste`@`localhost`")):
        self.cursor_ = _Cursor((porta, datadir, conta, banco, "8.4.9"), list(concessoes))

    def cursor(self):
        return self.cursor_


def _conferir(conn, **extra):
    opcoes = dict(porta=3307, datadir=Path("C:/inst/data"), usuario="pgd_teste", banco_esperado=None,
                  privilegios_restritos_a="pgd_agente_teste")
    opcoes.update(extra)
    return bt.conferir(conn, **opcoes)


def test_conferencia_aceita_instancia_isolada_com_usuario_restrito():
    assert _conferir(_Conexao())["privilegios"] == "restritos a pgd_agente_teste"


@pytest.mark.parametrize("conexao, trecho", [
    (_Conexao(porta=3306), "porta"),
    (_Conexao(datadir="C:/ProgramData/MySQL/pgd_agente/data/"), "datadir"),
    (_Conexao(conta="root@localhost"), "conta"),
    (_Conexao(banco="pgd_agente"), "DATABASE()"),
    (_Conexao(concessoes=("GRANT ALL PRIVILEGES ON *.* TO `pgd_teste`@`localhost`",)), "global"),
    (_Conexao(concessoes=("GRANT USAGE ON *.* TO `pgd_teste`@`localhost`",
                          "GRANT SELECT ON `pgd_agente`.* TO `pgd_teste`@`localhost`")), "fora de pgd_agente_teste"),
])
def test_conferencia_recusa_outro_servidor_conta_ou_privilegio(conexao, trecho):
    with pytest.raises(bt.ConexaoRecusada, match=trecho):
        _conferir(conexao)


def test_credencial_da_instancia_principal_e_recusada_antes_de_conectar(tmp_path):
    cnf = tmp_path / "x.cnf"
    cnf.write_text("[client]\nuser=root\npassword=nao-usada\nhost=127.0.0.1\nport=3306\n", encoding="utf-8")
    with pytest.raises(bt.ConexaoRecusada, match="principal"):
        bt.conectar(bt.ler_cnf(cnf))


def test_credencial_ausente_orienta_a_inicializar(tmp_path):
    with pytest.raises(bt.ConexaoRecusada, match="inicializar"):
        bt.ler_cnf(tmp_path / "teste.cnf")


# --- backup.ps1 ------------------------------------------------------------------------------

# Só no Windows: no WSL o powershell.exe da interoperabilidade receberia caminhos Linux.
POWERSHELL = (shutil.which("powershell.exe") or shutil.which("pwsh")) if os.name == "nt" else None


def _validar(destino: str) -> subprocess.CompletedProcess:
    return subprocess.run([POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(DADOS / "backup.ps1"),
                           "-Destino", destino, "-SomenteValidar"], capture_output=True, text=True, timeout=60)


@pytest.mark.skipif(POWERSHELL is None, reason="PowerShell do Windows indisponível")
@pytest.mark.parametrize("destino", ["relativo\\backups", "C:\\", str(RAIZ / "docs" / "backups")])
def test_backup_recusa_destino_invalido(destino):
    assert _validar(destino).returncode != 0


@pytest.mark.skipif(POWERSHELL is None, reason="PowerShell do Windows indisponível")
def test_backup_aceita_destino_absoluto_fora_do_git(tmp_path):
    resultado = _validar(str(tmp_path / "backups"))
    assert resultado.returncode == 0 and "destino validado" in resultado.stdout


# --- backup.sh e mysql_isolada.sh (Linux/WSL) ------------------------------------------------

BASH = shutil.which("bash") if os.name != "nt" else None


def _validar_sh(destino: str) -> subprocess.CompletedProcess:
    return subprocess.run([BASH, str(DADOS / "backup.sh"), "--destino", destino, "--somente-validar"],
                          capture_output=True, text=True, timeout=60)


@pytest.mark.skipif(BASH is None, reason="bash indisponível (Linux/WSL)")
@pytest.mark.parametrize("destino", ["relativo/backups", "/", str(RAIZ / "docs" / "backups")])
def test_backup_sh_recusa_destino_invalido(destino):
    assert _validar_sh(destino).returncode != 0


@pytest.mark.skipif(BASH is None, reason="bash indisponível (Linux/WSL)")
def test_backup_sh_aceita_destino_absoluto_fora_do_git(tmp_path):
    resultado = _validar_sh(str(tmp_path / "backups"))
    assert resultado.returncode == 0 and "destino validado" in resultado.stdout


@pytest.mark.skipif(BASH is None, reason="bash indisponível (Linux/WSL)")
def test_backup_sh_aceita_o_padrao_data_backups_ignorado():
    resultado = _validar_sh(str(RAIZ / "data" / "backups"))
    assert resultado.returncode == 0 and "destino validado" in resultado.stdout


@pytest.mark.skipif(BASH is None, reason="bash indisponível (Linux/WSL)")
def test_mysql_isolada_sh_sem_instancia_informa_parada_sem_criar_nada(tmp_path):
    base = tmp_path / "isolada"
    resultado = subprocess.run([BASH, str(DADOS / "mysql_isolada.sh"), "status"], capture_output=True, text=True,
                               timeout=60, env={**os.environ, "PGD_MYSQL_ISOLADA_DIR": str(base)})
    assert resultado.returncode == 0 and resultado.stdout.startswith("parada")
    assert not base.exists()


@pytest.mark.skipif(BASH is None, reason="bash indisponível (Linux/WSL)")
def test_mysql_isolada_sh_recusa_acao_desconhecida():
    assert subprocess.run([BASH, str(DADOS / "mysql_isolada.sh"), "apagar"], capture_output=True,
                          timeout=60).returncode == 2


def test_diretorio_padrao_da_instancia_coincide_com_o_script(monkeypatch, tmp_path):
    monkeypatch.delenv("PGD_MYSQL_ISOLADA_DIR", raising=False)
    if os.name == "nt":
        monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    else:
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    assert bt.diretorio_instancia() == tmp_path / "pgd-icmbio" / "mysql-isolada"
