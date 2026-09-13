"""Denodo configuration loaded from a local .env file.

This module intentionally never stores credentials in source code. Public
scripts fail fast when required local environment values are missing.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def platform_path(value: str | Path) -> Path:
    """Converte caminhos Windows para o ponto de montagem equivalente no WSL."""

    raw = str(value or "")
    if os.name != "nt" and len(raw) >= 3 and raw[1] == ":" and raw[2] in "\\/":
        return Path("/mnt") / raw[0].lower() / raw[3:].replace("\\", "/")
    return Path(raw)


def load_dotenv(path: Path | None = None) -> None:
    env_path = path or PROJECT_ROOT / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


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


def get_config(require_credentials: bool = True) -> DenodoConfig:
    load_dotenv()
    java_home = os.environ.get("JAVA_HOME", "")
    jvm_dll = os.environ.get("DENODO_JVM_DLL")
    if not jvm_dll and java_home:
        jvm_dll = str(platform_path(java_home) / "bin" / "server" / "jvm.dll")
    driver_path = os.environ.get("DENODO_DRIVER_PATH", "")

    config = DenodoConfig(
        host=os.environ.get("DENODO_HOST", "denodo-pgd.dataprev.gov.br"),
        port=os.environ.get("DENODO_PORT", "443"),
        database=os.environ.get("DENODO_DATABASE", "petrvs_icmbio"),
        user=os.environ.get("DENODO_USER", ""),
        password=os.environ.get("DENODO_PASSWORD", ""),
        driver_path=platform_path(driver_path),
        jvm_dll=platform_path(jvm_dll or ""),
    )
    if require_credentials:
        missing = []
        if not config.user or config.user == "seu_cpf_aqui":
            missing.append("DENODO_USER")
        if not config.password or config.password == "sua_senha_aqui":
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
