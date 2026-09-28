"""banco_teste.py — Banco de teste e restauração isolada do modelo comum (plano §10, L6).

O ``schema.sql`` e os dumps de ``backup.ps1`` trazem ``CREATE DATABASE``/``USE
pgd_agente``: o sufixo ``_teste`` sozinho não isola nada. Por isso:

- ``preparar``: aplica o schema em ``pgd_agente_teste`` com o usuário restrito da
  instância isolada. As instruções são reescritas para o destino de teste e
  **qualquer SQL que ainda cite ``pgd_agente`` é recusado**. Nunca usa o ``.cnf``
  administrativo do backup.
- ``restaurar``: restauração fiel de um dump na **segunda instância** (porta e datadir
  próprios), depois de conferir servidor, porta, datadir, conta, ``DATABASE()`` e
  privilégios. Recusa a instância principal.
- ``resumo``: tabelas, triggers, versão do schema e uma transação funcional (trigger de
  imutabilidade + ROLLBACK), sem expor dados.

A instância isolada é criada e ligada por ``mysql_isolada.ps1``; as credenciais ficam
em ``root.cnf`` e ``teste.cnf`` no diretório dela (fora do Git), nunca impressas.
"""
from __future__ import annotations

import argparse
import configparser
import json
import os
import re
import subprocess
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path

PRODUCAO = "pgd_agente"
TESTE = "pgd_agente_teste"
PORTA_PRINCIPAL = 3306
PORTA_ISOLADA = 3307
SCHEMA = Path(__file__).resolve().parent / "schema.sql"
MYSQL_BIN = Path(os.environ.get("PGD_MYSQL_BIN", r"C:\Program Files\MySQL\MySQL Server 8.4\bin"))


class SQLRecusado(ValueError):
    """Instrução que ainda aponta para o banco de produção ou para outro destino."""


class ConexaoRecusada(RuntimeError):
    """Servidor, conta ou privilégios diferentes do esperado."""


def diretorio_instancia() -> Path:
    padrao = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "pgd-icmbio" / "mysql-isolada"
    return Path(os.environ.get("PGD_MYSQL_ISOLADA_DIR", padrao))


# --- Reescrita e recusa (sem MySQL) ----------------------------------------------------------

def instrucoes(sql: str) -> list[str]:
    """Divide em instruções, sem comentários ``--``/``#``/``/* */`` fora de literais."""

    atuais: list[str] = []
    resultado: list[str] = []
    i, n, aspas = 0, len(sql), ""
    while i < n:
        c = sql[i]
        if aspas:
            atuais.append(c)
            if c == "\\" and i + 1 < n:
                atuais.append(sql[i + 1])
                i += 2
                continue
            if c == aspas:
                aspas = ""
            i += 1
            continue
        if c in "'\"`":
            aspas = c
            atuais.append(c)
        elif sql.startswith("--", i) and (i + 2 >= n or sql[i + 2] in " \t\r\n") or c == "#":
            fim = sql.find("\n", i)
            i = n if fim < 0 else fim
            continue
        elif sql.startswith("/*", i):
            fim = sql.find("*/", i + 2)
            i = n if fim < 0 else fim + 2
            continue
        elif c == ";":
            texto = "".join(atuais).strip()
            if texto:
                resultado.append(texto)
            atuais = []
        else:
            atuais.append(c)
        i += 1
    texto = "".join(atuais).strip()
    if texto:
        resultado.append(texto)
    return resultado


_CREATE_DB = re.compile(r"^CREATE\s+(DATABASE|SCHEMA)\s+(IF\s+NOT\s+EXISTS\s+)?`?(\w+)`?", re.IGNORECASE)
_USE = re.compile(r"^USE\s+`?(\w+)`?$", re.IGNORECASE)
_PRODUCAO = re.compile(rf"\b{PRODUCAO}\b", re.IGNORECASE)


def reescrever_para_teste(sql: str) -> list[str]:
    """Instruções apontadas para ``pgd_agente_teste``; recusa qualquer outro destino."""

    saida: list[str] = []
    for numero, instrucao in enumerate(instrucoes(sql), start=1):
        criar = _CREATE_DB.match(instrucao)
        usar = _USE.match(instrucao)
        if criar:
            if criar.group(3).lower() not in (PRODUCAO, TESTE):
                raise SQLRecusado(f"instrução {numero}: CREATE DATABASE para destino não previsto")
            instrucao = instrucao[: criar.start(3)] + TESTE + instrucao[criar.end(3):]
        elif usar:
            if usar.group(1).lower() not in (PRODUCAO, TESTE):
                raise SQLRecusado(f"instrução {numero}: USE para destino não previsto")
            instrucao = f"USE {TESTE}"
        if _PRODUCAO.search(instrucao.replace("`", "")):
            raise SQLRecusado(f"instrução {numero}: SQL ainda cita {PRODUCAO}")
        if re.match(r"^(DROP|ALTER)\s+(DATABASE|SCHEMA)\b", instrucao, re.IGNORECASE) and TESTE not in instrucao:
            raise SQLRecusado(f"instrução {numero}: DROP/ALTER DATABASE fora do destino de teste")
        saida.append(instrucao)
    return saida


# --- Conexão ------------------------------------------------------------------------------

@dataclass(frozen=True)
class Credencial:
    arquivo: Path
    usuario: str
    senha: str
    host: str
    porta: int


def ler_cnf(arquivo: Path) -> Credencial:
    if not arquivo.is_file():
        raise ConexaoRecusada(f"Credencial da instância isolada ausente: {arquivo.name} (rode mysql_isolada.ps1 inicializar)")
    parser = configparser.ConfigParser(interpolation=None)
    parser.read(arquivo, encoding="utf-8")
    cliente = parser["client"]
    return Credencial(arquivo, cliente["user"], cliente["password"], cliente.get("host", "127.0.0.1"),
                      int(cliente.get("port", PORTA_ISOLADA)))


def conectar(credencial: Credencial, banco: str | None = None):
    if credencial.porta == PORTA_PRINCIPAL:
        raise ConexaoRecusada("Porta da instância principal: esta ferramenta só usa a instância isolada.")
    import pymysql

    return pymysql.connect(host=credencial.host, port=credencial.porta, user=credencial.usuario,
                           password=credencial.senha, database=banco, charset="utf8mb4", autocommit=False)


def _normalizar_caminho(texto: str) -> str:
    return os.path.normcase(os.path.normpath(texto.replace("/", os.sep))).rstrip("\\/")


def conferir(conn, *, porta: int, datadir: Path, usuario: str, banco_esperado: str | None,
             privilegios_restritos_a: str | None) -> dict:
    """Confere servidor, porta, datadir, conta, DATABASE() e privilégios antes de executar."""

    with conn.cursor() as cur:
        cur.execute("SELECT @@port, @@datadir, CURRENT_USER(), DATABASE(), VERSION()")
        porta_real, datadir_real, conta, banco, versao = cur.fetchone()
        cur.execute("SHOW GRANTS")
        concessoes = [linha[0] for linha in cur.fetchall()]
    problemas = []
    if int(porta_real) != porta or porta == PORTA_PRINCIPAL:
        problemas.append(f"porta {porta_real} (esperada {porta})")
    if _normalizar_caminho(datadir_real) != _normalizar_caminho(str(datadir)):
        problemas.append("datadir diferente do da instância isolada")
    if conta.split("@", 1)[0] != usuario:
        problemas.append("conta diferente da esperada")
    if banco != banco_esperado:
        problemas.append(f"DATABASE() = {banco!r} (esperado {banco_esperado!r})")
    if privilegios_restritos_a:
        for concessao in concessoes:
            alvo = re.search(r"\bON\s+(\S+)\s+TO\b", concessao, re.IGNORECASE)
            escopo = alvo.group(1).replace("`", "") if alvo else ""
            if escopo == "*.*" and not concessao.upper().startswith("GRANT USAGE ON"):
                problemas.append("privilégio global além de USAGE")
            elif escopo not in ("*.*", f"{privilegios_restritos_a}.*"):
                problemas.append(f"privilégio fora de {privilegios_restritos_a}")
    if problemas:
        raise ConexaoRecusada("Conexão recusada: " + "; ".join(problemas))
    return {"porta": int(porta_real), "conta": usuario, "versao_servidor": versao, "database": banco,
            "privilegios": "restritos a " + privilegios_restritos_a if privilegios_restritos_a else "administrativos (instância isolada)"}


# --- Operações ------------------------------------------------------------------------------

def resumo(conn, banco: str) -> dict:
    """Estrutura e transação funcional, sem ler conteúdo das tabelas."""

    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = %s AND table_type = 'BASE TABLE'", (banco,))
        tabelas = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM information_schema.triggers WHERE trigger_schema = %s", (banco,))
        triggers = cur.fetchone()[0]
        cur.execute(f"SELECT MAX(versao) FROM `{banco}`.schema_migracoes")
        versao = cur.fetchone()[0]
        cur.execute(f"SELECT COUNT(*) FROM `{banco}`.execucoes_skill")
        antes = cur.fetchone()[0]
        identificador = str(uuid.uuid4())
        cur.execute(f"INSERT INTO `{banco}`.execucoes_skill (id, skill, versao_skill, entrada, saida) "
                    "VALUES (%s, 'S00', 'l6-teste', '{}', '{}')", (identificador,))
        try:
            cur.execute(f"UPDATE `{banco}`.execucoes_skill SET versao_skill = 'x' WHERE id = %s", (identificador,))
            trigger_bloqueou = False
        except Exception as exc:  # noqa: BLE001 — o driver sinaliza o SIGNAL 45000 como erro
            trigger_bloqueou = "imutavel" in str(exc)
        conn.rollback()
        cur.execute(f"SELECT COUNT(*) FROM `{banco}`.execucoes_skill")
        depois = cur.fetchone()[0]
    return {"banco": banco, "tabelas": tabelas, "triggers": triggers, "versao_schema": versao,
            "transacao_funcional": {"trigger_imutabilidade_bloqueou_update": trigger_bloqueou,
                                    "rollback_restaurou_contagem": antes == depois}}


def preparar(diretorio: Path, schema: Path = SCHEMA) -> dict:
    credencial = ler_cnf(diretorio / "teste.cnf")
    comandos = reescrever_para_teste(schema.read_text(encoding="utf-8"))
    conn = conectar(credencial)
    try:
        conferencia = conferir(conn, porta=PORTA_ISOLADA, datadir=diretorio / "data", usuario=credencial.usuario,
                               banco_esperado=None, privilegios_restritos_a=TESTE)
        with conn.cursor() as cur:
            cur.execute(f"DROP DATABASE IF EXISTS {TESTE}")
            for comando in comandos:
                cur.execute(comando)
        conn.commit()
        return {"conferencia": conferencia, "instrucoes": len(comandos), "resumo": resumo(conn, TESTE)}
    finally:
        conn.close()


def restaurar(diretorio: Path, dump: Path) -> dict:
    credencial = ler_cnf(diretorio / "root.cnf")
    conn = conectar(credencial)
    try:
        conferencia = conferir(conn, porta=PORTA_ISOLADA, datadir=diretorio / "data", usuario=credencial.usuario,
                               banco_esperado=None, privilegios_restritos_a=None)
    finally:
        conn.close()
    with dump.open("rb") as entrada:
        concluido = subprocess.run(
            [str(MYSQL_BIN / "mysql.exe"), f"--defaults-extra-file={credencial.arquivo}", "--protocol=TCP"],
            stdin=entrada, capture_output=True, check=False,
        )
    if concluido.returncode:
        raise RuntimeError(f"mysql falhou na restauração (exit {concluido.returncode})")
    conn = conectar(credencial)
    try:
        return {"conferencia": conferencia, "dump": dump.name, "resumo": resumo(conn, PRODUCAO)}
    finally:
        conn.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    comandos = parser.add_subparsers(dest="comando", required=True)
    comandos.add_parser("preparar", help="Aplica schema.sql em pgd_agente_teste (usuário restrito).")
    restauracao = comandos.add_parser("restaurar", help="Restaura um dump na instância isolada.")
    restauracao.add_argument("--dump", type=Path, required=True)
    args = parser.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        resultado = preparar(diretorio_instancia()) if args.comando == "preparar" else restaurar(diretorio_instancia(), args.dump)
    except (SQLRecusado, ConexaoRecusada) as exc:
        print(f"Recusado: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(resultado, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
