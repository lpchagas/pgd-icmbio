"""db.py — Conexão com o MySQL local do modelo comum (v4 §3.2; ADR-006).

Lê as variáveis MYSQL_* do .env na raiz do repositório. As funções deste
pacote recebem/devolvem conexões PyMySQL com autocommit desligado: quem
chama controla a transação (padrão exigido pelo versionamento imutável).
"""

import os
from pathlib import Path

import pymysql
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def get_conn() -> pymysql.connections.Connection:
    """Abre conexão com o banco pgd_agente (autocommit OFF, cursor dict)."""
    return pymysql.connect(
        host=os.environ.get("MYSQL_HOST", "127.0.0.1"),
        port=int(os.environ.get("MYSQL_PORT", "3306")),
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        database=os.environ.get("MYSQL_DATABASE", "pgd_agente"),
        charset="utf8mb4",
        autocommit=False,
        cursorclass=pymysql.cursors.DictCursor,
    )
