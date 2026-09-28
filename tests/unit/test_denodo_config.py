"""Adaptador único de configuração Denodo e aliases do agente (ADR-012; relatório L1 v2 §4.3).

Nenhum teste lê o .env real: ENV_PATH aponta para um arquivo sintético.
"""
from __future__ import annotations

import subprocess
import sys
import types
from pathlib import Path

import pytest

import lib.denodo_config as dc

pytestmark = pytest.mark.unit

CHAVES = ("DENODO_HOST", "DENODO_PORT", "DENODO_DATABASE", "DENODO_USER", "DENODO_PASSWORD", "DENODO_PASS",
          "DENODO_DRIVER_PATH", "DENODO_JDBC_JAR", "DENODO_URL", "DENODO_JVM_DLL", "JAVA_HOME")
SENHA = "senha-sintetica-de-teste"  # pragma: allowlist secret
OUTRA = "outra-senha-sintetica"  # pragma: allowlist secret


@pytest.fixture
def env(tmp_path, monkeypatch):
    """Escreve um .env sintético, aponta o módulo para ele e limpa o processo."""

    for chave in CHAVES:
        monkeypatch.delenv(chave, raising=False)
    caminho = tmp_path / "projeto" / ".env"
    caminho.parent.mkdir()
    monkeypatch.setattr(dc, "ENV_PATH", caminho)

    def escrever(texto: str) -> Path:
        caminho.write_text(texto, encoding="utf-8")
        return caminho

    return escrever


BASE = "DENODO_USER=usuario-sintetico\nDENODO_JVM_DLL=C:/jre/bin/server/jvm.dll\n"


def test_configuracao_canonica_sem_aviso(env, capsys):
    env(BASE + f"DENODO_PASSWORD={SENHA}\nDENODO_DRIVER_PATH=C:/drivers/denodo.jar\n")

    config = dc.get_config()

    assert (config.password, config.jdbc_url) == (SENHA, "jdbc:denodo://denodo-pgd.dataprev.gov.br:443/petrvs_icmbio")
    assert "alias" not in capsys.readouterr().err


def test_configuracao_antiga_do_agente_por_aliases(env, capsys):
    env(BASE + f"DENODO_PASS={SENHA}\nDENODO_JDBC_JAR=C:/drivers/denodo.jar\n"
        "DENODO_URL=jdbc:denodo://denodo-pgd.dataprev.gov.br:443/petrvs_icmbio\n")

    config = dc.get_config()

    assert config.password == SENHA
    assert config.driver_path == dc.ancorar("C:/drivers/denodo.jar", dc.ENV_PATH.parent)
    assert (config.host, config.port, config.database) == ("denodo-pgd.dataprev.gov.br", "443", "petrvs_icmbio")
    erro = capsys.readouterr().err
    assert "DENODO_PASS é alias" in erro and "DENODO_JDBC_JAR é alias" in erro and SENHA not in erro


def test_canonica_e_alias_iguais_sao_aceitos_com_aviso(env, capsys):
    env(BASE + f"DENODO_PASSWORD={SENHA}\nDENODO_PASS={SENHA}\nDENODO_DRIVER_PATH=drivers/denodo.jar\n"
        "DENODO_JDBC_JAR=./drivers/../drivers/denodo.jar\n")

    config = dc.get_config()

    assert config.password == SENHA
    assert "DENODO_PASS é alias" in capsys.readouterr().err


def test_canonica_e_alias_diferentes_sao_erro_sem_expor_valores(env):
    env(BASE + f"DENODO_PASSWORD={SENHA}\nDENODO_PASS={OUTRA}\nDENODO_DRIVER_PATH=C:/d/denodo.jar\n")

    with pytest.raises(dc.DenodoConfigError) as erro:
        dc.get_config()

    assert "DENODO_PASSWORD" in str(erro.value) and SENHA not in str(erro.value) and OUTRA not in str(erro.value)


def test_driver_canonico_e_alias_apontando_para_arquivos_diferentes_e_erro(env):
    env(BASE + f"DENODO_PASSWORD={SENHA}\nDENODO_DRIVER_PATH=C:/a/denodo.jar\nDENODO_JDBC_JAR=C:/b/denodo.jar\n")

    with pytest.raises(dc.DenodoConfigError, match="DENODO_DRIVER_PATH"):
        dc.get_config()


def test_processo_prevalece_sobre_o_arquivo_chave_a_chave(env, monkeypatch):
    env(BASE + f"DENODO_PASSWORD={SENHA}\nDENODO_DRIVER_PATH=C:/d/denodo.jar\n")
    monkeypatch.setenv("DENODO_PASSWORD", OUTRA)

    assert dc.get_config().password == OUTRA


def test_canonica_no_arquivo_e_alias_no_processo_diferentes_sao_erro(env, monkeypatch):
    env(BASE + f"DENODO_PASSWORD={SENHA}\nDENODO_DRIVER_PATH=C:/d/denodo.jar\n")
    monkeypatch.setenv("DENODO_PASS", OUTRA)

    with pytest.raises(dc.DenodoConfigError):
        dc.get_config()


def test_driver_relativo_ancorado_no_diretorio_do_env_e_nao_no_de_trabalho(env, tmp_path, monkeypatch):
    env(BASE + f"DENODO_PASSWORD={SENHA}\nDENODO_DRIVER_PATH=drivers/denodo.jar\n")
    outro = tmp_path / "outro-diretorio"
    outro.mkdir()
    monkeypatch.chdir(outro)

    config = dc.get_config()

    assert config.driver_path == (dc.ENV_PATH.parent / "drivers" / "denodo.jar")
    assert config.driver_path.is_absolute()


def test_driver_relativo_pela_cli_chamada_de_outro_diretorio(tmp_path):
    projeto = tmp_path / "projeto"
    projeto.mkdir()
    (projeto / ".env").write_text(BASE + f"DENODO_PASSWORD={SENHA}\nDENODO_JDBC_JAR=drivers/denodo.jar\n", encoding="utf-8")
    outro = tmp_path / "cwd"
    outro.mkdir()
    codigo = (
        "import lib.denodo_config as dc\n"
        "from pathlib import Path\n"
        f"dc.ENV_PATH = Path({str(projeto / '.env')!r})\n"
        "print(dc.get_config().driver_path)\n"
    )
    ambiente = {k: v for k, v in __import__("os").environ.items() if k not in CHAVES}
    ambiente["PYTHONPATH"] = str(dc.PROJECT_ROOT)

    saida = subprocess.run([sys.executable, "-c", codigo], cwd=outro, env=ambiente, capture_output=True, text=True, check=True)

    assert Path(saida.stdout.strip()) == projeto / "drivers" / "denodo.jar"


@pytest.mark.parametrize("url, codigo", [
    ("jdbc:denodo://host.exemplo:443", "denodo_url_incompleta"),
    ("jdbc:denodo://host.exemplo/petrvs_icmbio", "denodo_url_incompleta"),
    ("jdbc:denodo://host.exemplo:443/", "denodo_url_incompleta"),
    ("jdbc:denodo://host.exemplo:443/petrvs_icmbio?ssl=true", "denodo_url_com_parametros"),
    ("jdbc:denodo://host.exemplo:443/petrvs_icmbio;timeout=5", "denodo_url_com_parametros"),
    ("jdbc:denodo://host.exemplo:443/petrvs%5Ficmbio", "denodo_url_com_parametros"),
])
def test_url_incompleta_ou_com_parametros_e_recusada(env, url, codigo):
    env(BASE + f"DENODO_PASSWORD={SENHA}\nDENODO_DRIVER_PATH=C:/d/denodo.jar\nDENODO_URL={url}\n")

    with pytest.raises(dc.DenodoConfigError, match=codigo):
        dc.get_config()


def test_url_coerente_com_canonicas_e_aceita_e_divergente_e_erro(env):
    base = BASE + f"DENODO_PASSWORD={SENHA}\nDENODO_DRIVER_PATH=C:/d/denodo.jar\nDENODO_URL=jdbc:denodo://host.exemplo:443/base\n"
    env(base + "DENODO_HOST=HOST.exemplo\nDENODO_PORT=443\n")
    assert dc.get_config().jdbc_url == "jdbc:denodo://HOST.exemplo:443/base"

    env(base + "DENODO_DATABASE=outra_base\n")
    with pytest.raises(dc.DenodoConfigError, match="DENODO_DATABASE"):
        dc.get_config()


def test_env_com_sintaxe_recusada_pela_auditoria_e_recusado_na_execucao(env):
    env(BASE + "DENODO_PASSWORD=${OUTRA_VARIAVEL}\n")

    with pytest.raises(dc.DenodoConfigError, match=r"Linha\(s\) \[3\]"):
        dc.get_config()


def test_driver_ausente_e_placeholder_sao_recusados(env):
    env(BASE + f"DENODO_PASSWORD={SENHA}\n")
    with pytest.raises(RuntimeError, match="DENODO_DRIVER_PATH"):
        dc.get_config()

    env(BASE + f"DENODO_PASSWORD={SENHA}\nDENODO_DRIVER_PATH=C:/Users/SEU_USUARIO/driver.jar\n")
    with pytest.raises(RuntimeError, match="DENODO_DRIVER_PATH"):
        dc.get_config()


def test_connect_nao_reinicia_jvm_ja_iniciada(monkeypatch):
    monkeypatch.delenv("PGD_BLOQUEAR_DENODO")  # jpype falso abaixo: nenhuma conexão real
    chamadas = []
    jpype = types.ModuleType("jpype")
    jpype.isJVMStarted = lambda: True
    jpype.startJVM = lambda *a, **k: chamadas.append("startJVM")

    class Propriedades(dict):
        def setProperty(self, chave, valor):
            self[chave] = valor

    class Gerenciador:
        @staticmethod
        def getConnection(url, props):
            return ("conexao", url, sorted(props))

    jpype.JClass = lambda nome: {"java.sql.DriverManager": Gerenciador, "java.util.Properties": Propriedades}[nome]
    monkeypatch.setitem(sys.modules, "jpype", jpype)
    monkeypatch.setitem(sys.modules, "jpype.imports", types.ModuleType("jpype.imports"))
    config = dc.DenodoConfig("h", "1", "b", "u", SENHA, Path("d.jar"), Path("jvm.dll"))

    assert dc.connect(config) == ("conexao", "jdbc:denodo://h:1/b", ["password", "user"])
    assert chamadas == []


def test_trava_da_suite_recusa_conexao_real():
    """PGD_BLOQUEAR_DENODO=1 (conftest) impede qualquer conexão, antes de iniciar a JVM."""

    from lib.denodo_config import connect

    with pytest.raises(RuntimeError, match="PGD_BLOQUEAR_DENODO"):
        connect(object())
