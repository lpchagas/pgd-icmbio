"""Regressão estática do SQL do REG_EXEC — não executa nada, lê o fonte.

Cada asserção corresponde a uma restrição real do Denodo VQL documentada em
docs/ e já responsável por bug histórico neste projeto: ausência de
`deleted_at IS NULL` inflando contagens, `DATE()`/`DATEDIFF` inexistentes,
CTE recursiva não suportada, divisão inteira truncando percentuais e
`JSON_UNQUOTE` devolvendo NULL silenciosamente.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.regression

FONTE = Path(__file__).resolve().parents[2] / "gestao" / "REG_EXEC.1_run.py"

# Tabelas de referência: não têm coluna de soft-delete.
TABELAS_SEM_SOFT_DELETE = {"petrvs_icmbio_tipos_avaliacoes_notas"}

SQL_ESPERADAS = (
    "SQL_PE_ENTREGAS", "SQL_PT_CICLOS", "SQL_PT_VIGENTES", "SQL_VINCULOS", "SQL_NOMES",
)


def fonte() -> str:
    assert FONTE.is_file(), f"entrypoint não encontrado: {FONTE}"
    return FONTE.read_text(encoding="utf-8")


def sql_constante(nome: str) -> str:
    achado = re.search(rf'^{re.escape(nome)}\s*=\s*"""(.*?)"""', fonte(), re.DOTALL | re.MULTILINE)
    assert achado, f"constante {nome} não encontrada"
    return achado.group(1)


def todas_as_sqls() -> dict[str, str]:
    return {nome: sql_constante(nome) for nome in SQL_ESPERADAS}


class TestSoftDelete:
    @pytest.mark.parametrize("nome", SQL_ESPERADAS)
    def test_toda_tabela_transacional_filtra_deleted_at(self, nome):
        sql = sql_constante(nome)
        faltando = []
        for achado in re.finditer(
            r"\b(?:FROM|JOIN)\s+(petrvs_icmbio_\w+)\s+(\w+)", sql, re.IGNORECASE
        ):
            tabela, alias = achado.group(1), achado.group(2)
            if tabela in TABELAS_SEM_SOFT_DELETE:
                continue
            if not re.search(rf"\b{re.escape(alias)}\.deleted_at\s+IS\s+NULL", sql, re.IGNORECASE):
                faltando.append(f"{tabela} AS {alias}")
        assert not faltando, f"{nome}: sem filtro de soft-delete em {faltando}"


class TestRestricoesDoVQL:
    @pytest.mark.parametrize("proibido", [
        r"\bDATEDIFF\b", r"\bTIMESTAMPDIFF\b", r"\bDATE\s*\(", r"\bJSON_UNQUOTE\b",
        r"WITH\s+RECURSIVE",
    ])
    def test_construcao_nao_suportada_ausente(self, proibido):
        for nome, sql in todas_as_sqls().items():
            assert not re.search(proibido, sql, re.IGNORECASE), f"{nome} usa {proibido}"

    def test_conversao_de_data_usa_cast(self):
        sql = sql_constante("SQL_PE_ENTREGAS")
        assert "CAST(pee.data_inicio AS DATE)" in sql
        assert "CAST(pee.data_fim    AS DATE)" in sql or "CAST(pee.data_fim AS DATE)" in sql

    def test_nenhuma_divisao_no_sql(self):
        # Todas as razões do REG_EXEC são calculadas em Python, onde são
        # testáveis; divisão no VQL é o caminho curto para truncamento.
        for nome, sql in todas_as_sqls().items():
            sem_comentarios = re.sub(r"--.*", "", sql)
            assert "/" not in sem_comentarios, f"{nome} faz divisão no SQL"


class TestRegrasDeNegocioNoSQL:
    def test_entrega_sem_prazo_nao_e_descartada(self):
        # data_fim é anulável; filtrá-la sem tratar NULL faria a entrega sem
        # prazo sumir do registro em vez de virar pendência.
        sql = sql_constante("SQL_PE_ENTREGAS")
        assert "pee.data_fim IS NULL" in sql
        assert re.search(r"pee\.data_fim IS NULL\s*\n?\s*OR", sql)

    def test_titulo_da_entrega_tem_fallback(self):
        sql = sql_constante("SQL_PE_ENTREGAS")
        assert "COALESCE(NULLIF(TRIM(pee.descricao), '')" in sql
        assert "NULLIF(TRIM(pee.descricao_entrega), '')" in sql

    def test_escala_de_avaliacao_usa_a_convencao_do_projeto(self):
        # A nota vem de tipos_avaliacoes_notas.sequencia invertida; ler o campo
        # diretamente trocaria os extremos da escala (bug de 12.06.2026).
        assert "6 - tan.sequencia" in sql_constante("SQL_PT_CICLOS")

    def test_universo_da_rn04_exclui_plano_cancelado(self):
        assert "pt.status <> 'CANCELADO'" in sql_constante("SQL_PT_VIGENTES")

    def test_vinculo_exige_entrega_de_pe(self):
        sql = sql_constante("SQL_VINCULOS")
        assert "pte.plano_entrega_entrega_id IS NOT NULL" in sql

    def test_escopo_casa_dona_e_executora(self):
        # Uma entrega da CGOV executada por outra unidade precisa continuar no
        # escopo — senão a força de trabalho some do registro.
        assert "{filtro_ambos}" in sql_constante("SQL_VINCULOS")


class TestHigieneDoEntrypoint:
    def test_nao_seleciona_email(self):
        # servidor_nome é removido no produto restrito; e-mail nunca é lido,
        # porque não há uso legítimo dele neste produto.
        for nome, sql in todas_as_sqls().items():
            assert "email" not in sql.lower(), f"{nome} seleciona e-mail"

    def test_nao_usa_data_corrente(self):
        # A reprodutibilidade depende de --data-execucao; date.today() tornaria
        # a apuração diferente a cada execução.
        assert "date.today()" not in fonte()

    def test_conexao_fechada_em_finally(self):
        texto = fonte()
        assert "finally:" in texto and "conn.close()" in texto
        assert texto.index("finally:") < texto.index("conn.close()")

    def test_sem_credencial_ou_cpf_literal(self):
        texto = fonte()
        assert not re.search(r"(?<!\d)\d{11}(?!\d)", texto)
        for proibido in ("DENODO_PASSWORD=", "senha", "password ="):
            assert proibido not in texto

    def test_usa_os_utilitarios_canonicos(self):
        texto = fonte()
        assert "from lib.csv_utils import" in texto and "write_pipe_csv" in texto
        assert "resolve_period" in texto and "periods_pt_within" in texto
