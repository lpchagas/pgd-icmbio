"""Caracterização de sincronizar_ref.py: filtro por sigla, fallback, indisponibilidade e transação."""
from __future__ import annotations

import re

import pytest


class DenodoFalso:
    """Serve linhas por trecho de SQL; um trecho mapeado para exceção simula falha da view."""

    def __init__(self, respostas: dict) -> None:
        self.respostas = respostas
        self.consultas: list[str] = []
        self.fechada = False

    def createStatement(self):
        return self

    def executeQuery(self, sql: str):
        self.consultas.append(sql)
        for trecho, resposta in self.respostas.items():
            if trecho in sql:
                if isinstance(resposta, Exception):
                    raise resposta
                return _ResultSet(resposta)
        raise AssertionError("consulta não prevista na caracterização")

    def close(self) -> None:
        self.fechada = True


class _ResultSet:
    def __init__(self, linhas: list[list]) -> None:
        self.linhas, self.atual = linhas, -1

    def getMetaData(self):
        return self

    def getColumnCount(self) -> int:
        return len(self.linhas[0]) if self.linhas else 0

    def next(self) -> bool:
        self.atual += 1
        return self.atual < len(self.linhas)

    def getObject(self, i: int):
        return self.linhas[self.atual][i - 1]

    def close(self) -> None:
        return None


UNIDADES = [["u-1", " UNID-A ", "Unidade A", "/1", None, "true"], ["u-2", "", None, None, "u-1", "0"]]
USUARIOS = [["p-1", "Servidor Sintético", "000", "1", "u-1"]]


@pytest.fixture
def sinc(carregar):
    return carregar("sincronizar_ref")


def test_importar_nao_carrega_env(sinc):
    """DP-L2-04 corrigido no L3: antes, importar o módulo lia o .env da raiz."""

    assert sinc._dubles["dotenv"].chamadas == []


def test_piloto_e_filtro_por_sigla(sinc, conexao):
    denodo = DenodoFalso({"FROM petrvs_icmbio_unidades\n": UNIDADES, "unidades_integrantes": USUARIOS})
    conn = conexao()

    sinc.sincronizar(conn, denodo)

    assert sinc.PILOTO_SIGLAS == ["CGOV", "COCAGE"]
    assert "un.sigla IN ('CGOV', 'COCAGE')" in denodo.consultas[1]
    assert len(denodo.consultas) == 2


def test_consultas_de_usuarios_nao_trazem_cpf_email_ou_telefone(sinc):
    for sql in (sinc.SQL_USUARIOS_INTEGRANTES, sinc.SQL_USUARIOS_PT):
        colunas = re.search(r"SELECT DISTINCT (.*?)\n", sql).group(1)
        assert colunas in ("u.id, u.nome, u.matricula, u.participa_pgd, ui.unidade_id",
                           "u.id, u.nome, u.matricula, u.participa_pgd, pt.unidade_id")
        assert not re.search(r"cpf|email|telefone", sql, re.IGNORECASE)


def test_normalizacao_das_linhas_de_unidades(sinc, conexao):
    conn = conexao()

    sinc.sincronizar(conn, DenodoFalso({"FROM petrvs_icmbio_unidades\n": UNIDADES, "unidades_integrantes": USUARIOS}))

    (_, sql, linhas) = conn.sql("INSERT INTO ref_unidades")[0]
    assert "ON DUPLICATE KEY UPDATE" in sql
    assert [linha[:6] for linha in linhas] == [("u-1", "UNID-A", "Unidade A", "/1", None, 1), ("u-2", "?", "?", None, "u-1", 0)]
    assert linhas[0][6] == linhas[1][6] and linhas[0][6].microsecond == 0


def test_fallback_por_planos_de_trabalho_quando_integrantes_falha(sinc, conexao, capsys):
    denodo = DenodoFalso({
        "FROM petrvs_icmbio_unidades\n": UNIDADES,
        "unidades_integrantes": RuntimeError("view divergente"),
        "petrvs_icmbio_planos_trabalhos": USUARIOS,
    })
    conn = conexao()

    sinc.sincronizar(conn, denodo)

    assert "JOIN petrvs_icmbio_planos_trabalhos pt" in denodo.consultas[2]
    assert "via planos_trabalhos" in capsys.readouterr().out
    assert conn.commits == 0


def test_sincronizar_nao_encerra_a_transacao(sinc, conexao):
    """DP-L2-03 corrigido no L3: antes, sincronizar() fazia commit interno.

    Agora segue a convenção de versoes.py: quem chama decide o limite da transação.
    """

    conn = conexao()
    sinc.sincronizar(conn, DenodoFalso({"FROM petrvs_icmbio_unidades\n": UNIDADES, "unidades_integrantes": USUARIOS}))

    assert conn.commits == 0 and conn.rollbacks == 0


def test_main_commita_uma_vez_no_sucesso(sinc, conexao, monkeypatch):
    denodo = DenodoFalso({"FROM petrvs_icmbio_unidades\n": UNIDADES, "unidades_integrantes": USUARIOS})
    conn = conexao()
    monkeypatch.setattr(sinc, "_denodo_conn", lambda: denodo)
    monkeypatch.setattr(sinc, "get_conn", lambda: conn)

    sinc.main()

    assert (conn.commits, conn.rollbacks, conn.fechada, denodo.fechada) == (1, 0, True, True)


def test_falha_no_meio_faz_rollback_explicito_no_main(sinc, conexao, falha_injetada, monkeypatch):
    """DP-L2-03 corrigido no L3: antes, a falha dependia do close() para descartar a transação."""

    denodo = DenodoFalso({"FROM petrvs_icmbio_unidades\n": UNIDADES, "unidades_integrantes": USUARIOS})
    conn = conexao(falhar_quando="INSERT INTO ref_usuarios")
    monkeypatch.setattr(sinc, "_denodo_conn", lambda: denodo)
    monkeypatch.setattr(sinc, "get_conn", lambda: conn)

    with pytest.raises(falha_injetada):
        sinc.main()

    assert len(conn.sql("INSERT INTO ref_unidades")) == 1
    assert (conn.commits, conn.rollbacks, conn.fechada) == (0, 1, True)


def test_denodo_indisponivel_interrompe_antes_de_abrir_mysql(sinc, monkeypatch):
    def indisponivel():
        raise ConnectionError("Denodo indisponível")

    monkeypatch.setattr(sinc, "_denodo_conn", indisponivel)
    # get_conn continua o dublê que falha se chamado.

    with pytest.raises(ConnectionError):
        sinc.main()


def test_main_fecha_as_duas_conexoes_quando_a_sincronizacao_falha(sinc, conexao, monkeypatch):
    denodo = DenodoFalso({"FROM petrvs_icmbio_unidades\n": RuntimeError("timeout")})
    conn = conexao()
    monkeypatch.setattr(sinc, "_denodo_conn", lambda: denodo)
    monkeypatch.setattr(sinc, "get_conn", lambda: conn)

    with pytest.raises(RuntimeError, match="timeout"):
        sinc.main()

    assert conn.fechada and denodo.fechada
    assert conn.commits == 0 and conn.rollbacks == 1


def test_conexao_denodo_usa_o_adaptador_unico_do_nucleo(sinc, monkeypatch):
    """Teste sintético do adaptador agente -> núcleo (plano §8, ADR-012).

    Antes do L3, o agente lia DENODO_JDBC_JAR/DENODO_PASS/DENODO_URL diretamente;
    agora usa lib.denodo_config, que aceita esses nomes como aliases.
    """

    import lib.denodo_config

    assert (sinc.get_config, sinc.connect) == (lib.denodo_config.get_config, lib.denodo_config.connect)
    chamadas = []
    config = object()
    monkeypatch.setattr(sinc, "get_config", lambda require_credentials: chamadas.append(require_credentials) or config)
    monkeypatch.setattr(sinc, "connect", lambda recebido: ("conexao", recebido))

    assert sinc._denodo_conn() == ("conexao", config)
    assert chamadas == [True]


def test_adaptador_do_agente_importa_o_nucleo_da_mesma_arvore(sinc):
    import lib.denodo_config

    fonte = sinc.Path(sinc.__file__).read_text(encoding="utf-8")
    assert "from lib.denodo_config import connect, get_config" in fonte
    assert sinc.Path(lib.denodo_config.__file__).resolve().parents[1] == sinc.Path(sinc.__file__).resolve().parents[2]
