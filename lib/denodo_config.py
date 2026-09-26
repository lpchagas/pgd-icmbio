"""Denodo configuration loaded from a local .env file.

This module intentionally never stores credentials in source code. Public
scripts fail fast when required local environment values are missing.

Único adaptador de configuração Denodo do monorepo (ADR-012). Aceita
temporariamente os nomes antigos do agente como aliases:

- ``DENODO_PASS``      -> ``DENODO_PASSWORD``
- ``DENODO_JDBC_JAR``  -> ``DENODO_DRIVER_PATH``
- ``DENODO_URL``       -> ``DENODO_HOST``, ``DENODO_PORT``, ``DENODO_DATABASE``

Regras (relatório L1 v2, §4.3): o processo prevalece sobre o arquivo, chave a
chave; canônica e alias com valores efetivos diferentes são erro, sem exibir
valores; iguais são aceitos com aviso. Caminhos relativos do driver são
ancorados no diretório do ``.env``, nunca no diretório de trabalho. A URL só é
aceita na forma ``jdbc:denodo://host:porta/base``. O ``.env`` segue a mesma
gramática estrita da auditoria de segredos: o que ela recusa, a execução recusa.
"""
from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / ".env"

_URL = re.compile(r"^jdbc:denodo://(?P<host>[^/:?;#%\s]+):(?P<port>\d+)/(?P<database>[^/?;#%\s]+)$", re.IGNORECASE)


class DenodoConfigError(RuntimeError):
    """Configuração inválida ou conflitante (a mensagem nunca contém valores)."""


def platform_path(value: str | Path) -> Path:
    """Converte caminhos Windows para o ponto de montagem equivalente no WSL."""

    raw = str(value or "")
    if os.name != "nt" and len(raw) >= 3 and raw[1] == ":" and raw[2] in "\\/":
        return Path("/mnt") / raw[0].lower() / raw[3:].replace("\\", "/")
    return Path(raw)


def load_dotenv(path: Path | None = None) -> None:
    """Carrega o .env com a gramática estrita da auditoria; o processo prevalece."""

    env_path = path or ENV_PATH
    if not env_path.exists():
        return
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    from tools.security_audit import parse_env_text

    values, refused = parse_env_text(env_path.read_text(encoding="utf-8"))
    if refused:
        raise DenodoConfigError(
            f"Linha(s) {refused} do .env com sintaxe não suportada (a mesma recusada pela auditoria)."
        )
    for key, value in values.items():
        os.environ.setdefault(key, value)


@dataclass(frozen=True)
class DenodoConfig:
    host: str
    port: str
    database: str
    user: str
    password: str
    driver_path: Path
    jvm_dll: Path

    @property
    def jdbc_url(self) -> str:
        return f"jdbc:denodo://{self.host}:{self.port}/{self.database}"


def _valor(chave: str) -> str:
    return os.environ.get(chave, "").strip()


def _aviso_alias(alias: str, canonica: str) -> None:
    print(f"Aviso: {alias} é alias temporário de {canonica} (ADR-012); prefira o nome canônico.", file=sys.stderr)


def _efetivo(canonica: str, alias: str, normalizar=lambda v: v) -> str:
    atual, antigo = _valor(canonica), _valor(alias)
    if atual and antigo:
        if normalizar(atual) != normalizar(antigo):
            raise DenodoConfigError(f"{canonica} e o alias {alias} têm valores diferentes; mantenha só um.")
        _aviso_alias(alias, canonica)
        return atual
    if antigo:
        _aviso_alias(alias, canonica)
        return antigo
    return atual


def ancorar(valor: str, ancora: Path = PROJECT_ROOT) -> Path:
    """Caminho do driver: absoluto como veio, ou relativo ao diretório do .env."""

    caminho = platform_path(valor)
    if not caminho.is_absolute():
        caminho = ancora / caminho
    return Path(os.path.normpath(caminho))


def _mesmo_caminho(ancora: Path):
    return lambda valor: os.path.normcase(str(ancorar(valor, ancora)))


def _destino_da_url() -> dict[str, str]:
    url = _valor("DENODO_URL")
    if not url:
        return {}
    if re.search(r"[?;%#]", url):
        raise DenodoConfigError("DENODO_URL com parâmetros ou codificação não é aceita (denodo_url_com_parametros).")
    achado = _URL.match(url)
    if not achado:
        raise DenodoConfigError("DENODO_URL incompleta: use jdbc:denodo://host:porta/base (denodo_url_incompleta).")
    return {"DENODO_HOST": achado["host"], "DENODO_PORT": achado["port"], "DENODO_DATABASE": achado["database"]}


def get_config(require_credentials: bool = True) -> DenodoConfig:
    load_dotenv()
    ancora = ENV_PATH.parent
    java_home = _valor("JAVA_HOME")
    jvm_dll = _valor("DENODO_JVM_DLL")
    if not jvm_dll and java_home:
        jvm_dll = str(platform_path(java_home) / "bin" / "server" / "jvm.dll")
    driver_path = _efetivo("DENODO_DRIVER_PATH", "DENODO_JDBC_JAR", _mesmo_caminho(ancora))
    password = _efetivo("DENODO_PASSWORD", "DENODO_PASS")

    destino = {"DENODO_HOST": "denodo-pgd.dataprev.gov.br", "DENODO_PORT": "443", "DENODO_DATABASE": "petrvs_icmbio"}
    pela_url = _destino_da_url()
    if pela_url:
        _aviso_alias("DENODO_URL", "DENODO_HOST/DENODO_PORT/DENODO_DATABASE")
    for chave, padrao in destino.items():
        explicito = _valor(chave)
        if explicito and chave in pela_url and explicito.lower() != pela_url[chave].lower():
            raise DenodoConfigError(f"{chave} e DENODO_URL indicam destinos diferentes; mantenha só um.")
        destino[chave] = explicito or pela_url.get(chave) or padrao

    config = DenodoConfig(
        host=destino["DENODO_HOST"],
        port=destino["DENODO_PORT"],
        database=destino["DENODO_DATABASE"],
        user=_valor("DENODO_USER"),
        password=password,
        driver_path=ancorar(driver_path, ancora) if driver_path else Path(),
        jvm_dll=platform_path(jvm_dll or ""),
    )
    if require_credentials:
        missing = []
        if not config.user or config.user == "seu_cpf_aqui":
            missing.append("DENODO_USER")
        if not config.password or config.password == "sua_senha_aqui":  # pragma: allowlist secret
            missing.append("DENODO_PASSWORD")
        if not driver_path or "SEU_USUARIO" in driver_path:
            missing.append("DENODO_DRIVER_PATH")
        if not jvm_dll:
            missing.append("JAVA_HOME ou DENODO_JVM_DLL")
        if missing:
            joined = ", ".join(missing)
            raise RuntimeError(f"Configure {joined} no arquivo .env antes de executar.")
    return config


def connect(config: DenodoConfig):
    import jpype
    import jpype.imports  # noqa: F401

    if not jpype.isJVMStarted():
        jpype.startJVM(str(config.jvm_dll), classpath=[str(config.driver_path)])
        print("JVM iniciada.")

    manager = jpype.JClass("java.sql.DriverManager")
    props = jpype.JClass("java.util.Properties")()
    props.setProperty("user", config.user)
    props.setProperty("password", config.password)
    return manager.getConnection(config.jdbc_url, props)
