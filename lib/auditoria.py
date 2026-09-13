"""Lightweight checks for generated monthly indicator CSV files."""
from __future__ import annotations

import csv
import os
import re
from pathlib import Path


_ALLOWED_ENV = {
    "PATH", "JAVA_HOME", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "TMPDIR",
    "LANG", "LC_ALL", "PYTHONPATH", "VIRTUAL_ENV", "APPDATA", "LOCALAPPDATA",
    "USERPROFILE", "DENODO_JDBC_JAR",
}
_SENSITIVE_ENV = re.compile(r"(?i)(password|passwd|senha|secret|token|cpf|denodo_user)")


def minimal_subprocess_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    """Ambiente mínimo: credenciais são recarregadas do .env apenas no processo que as usa."""

    env = {
        key: value for key, value in os.environ.items()
        if (key in _ALLOWED_ENV or key.startswith("PGD_")) and not _SENSITIVE_ENV.search(key)
    }
    if extra:
        env.update({key: value for key, value in extra.items() if not _SENSITIVE_ENV.search(key)})
    return env


def redact_log(text: str) -> str:
    """Remove da mensagem valores sensíveis eventualmente presentes no ambiente pai."""

    result = text
    for key, value in os.environ.items():
        if value and _SENSITIVE_ENV.search(key):
            result = result.replace(value, "[REDACTED]")
    return result


def audit_csv(path: Path) -> list[str]:
    messages: list[str] = []
    if not path.exists():
        return [f"ERRO: arquivo nao encontrado: {path}"]

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle, delimiter="|")
        try:
            header = next(reader)
        except StopIteration:
            return ["ERRO: CSV vazio."]
        row_count = 0
        bad_width = 0
        for row in reader:
            row_count += 1
            if len(row) != len(header):
                bad_width += 1

    messages.append(f"Linhas de dados: {row_count}")
    messages.append(f"Colunas: {len(header)}")
    if bad_width:
        messages.append(f"ALERTA: {bad_width} linhas com quantidade de colunas divergente.")
    else:
        messages.append("Estrutura CSV OK: todas as linhas tem a mesma quantidade de colunas.")
    return messages
