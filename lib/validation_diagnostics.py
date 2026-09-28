"""Regras declarativas A4 aplicadas a registros atômicos, sem expor valores."""
from __future__ import annotations

import json
import re
from collections import Counter
from datetime import date
from typing import Any


Row = dict[str, Any]
PII_FIELD = re.compile(r"(?i)(cpf|email|telefone|endereco|nome_servidor|servidor_nome)")

ATOMIC_KEYS: dict[str, tuple[str, ...]] = {
    "I01": ("periodo", "unidade_sigla", "id_servidor"),
    "I02": ("periodo", "unidade_sigla", "id_entrega"),
    "I03": ("periodo", "unidade_sigla", "id_entrega"),
    "I04": ("periodo", "unidade_sigla", "id_entrega"),
    "I05": ("periodo", "unidade_sigla", "id_servidor", "id_entrega"),
    "I06": ("periodo", "unidade_sigla", "id_servidor", "id_entrega"),
    "I07": ("periodo", "unidade_sigla", "plano_trabalho_id", "id_entrega"),
    "I08": ("periodo", "unidade_sigla", "plano_trabalho_id", "id_entrega"),
    "I09": ("periodo", "id_avaliacao"),
    "I10": ("periodo", "id_avaliacao"),
    "I11": ("periodo", "id_avaliacao"),
    "I12": ("periodo", "instrumento", "id_avaliacao"),
}


def _date(value: Any) -> date | None:
    try:
        return date.fromisoformat(str(value)[:10]) if value not in (None, "") else None
    except ValueError:
        return None


def _number(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _finding(kind: str, message: str, severity: str = "bloqueante") -> dict[str, str]:
    return {"classe": kind, "severidade": severity, "mensagem": message}


def diagnose_atomic(code: str, rows: list[Row]) -> list[dict[str, str]]:
    """Retorna somente contagens e classes; identificadores atômicos não são divulgados."""

    findings: list[dict[str, str]] = []
    fields = set().union(*(row.keys() for row in rows)) if rows else set()
    pii = sorted(field for field in fields if PII_FIELD.search(field))
    if pii:
        findings.append(_finding("ANOMALIA_DE_DADOS", f"snapshot contém campos pessoais vedados: {pii}"))

    key_fields = ATOMIC_KEYS.get(code)
    if key_fields:
        keyed_rows = [
            row for row in rows if all(row.get(field) not in (None, "") for field in key_fields)
        ]
        keys = [tuple(str(row.get(field, "")) for field in key_fields) for row in keyed_rows]
        duplicates = sum(count - 1 for count in Counter(keys).values() if count > 1)
        if duplicates:
            findings.append(_finding("ANOMALIA_DE_DADOS", f"duplicidades atômicas: {duplicates}", "alerta"))

    missing_units = sum(
        "unidade_sigla" in row and str(row.get("unidade_sigla", "")).strip() in {"", "N.I."}
        for row in rows
    )
    if missing_units:
        findings.append(_finding("ANOMALIA_DE_DADOS", f"unidades não mapeadas: {missing_units}", "alerta"))

    orphan_deliveries = sum("id_entrega" in row and not row.get("id_entrega") for row in rows)
    if orphan_deliveries:
        findings.append(_finding("ANOMALIA_DE_DADOS", f"vínculos sem entrega: {orphan_deliveries}", "alerta" if code == "G02" else "bloqueante"))

    reversed_dates = 0
    for row in rows:
        for start_name, end_name in (
            ("plano_inicio", "plano_fim"),
            ("sobreposicao_inicio", "sobreposicao_fim"),
            ("consolidacao_inicio", "consolidacao_fim"),
        ):
            start, end = _date(row.get(start_name)), _date(row.get(end_name))
            reversed_dates += int(bool(start and end and start > end))
    if reversed_dates:
        # D26: no G01 as datas do plano não entram em nenhuma métrica; o achado é alerta.
        findings.append(_finding(
            "ANOMALIA_DE_DADOS", f"intervalos com datas invertidas: {reversed_dates}",
            "alerta" if code == "G01" else "bloqueante",
        ))

    invalid_sequences = sum(
        (number := _number(row.get("sequencia_nota"))) is not None and not 1 <= number <= 5
        for row in rows
    )
    if invalid_sequences:
        findings.append(_finding("ANOMALIA_DE_DADOS", f"notas fora da escala 1–5: {invalid_sequences}"))

    invalid_workforce = sum(
        (number := _number(row.get("forca_trabalho"))) is not None and not 0 <= number <= 100
        for row in rows
    )
    if invalid_workforce:
        findings.append(_finding("ANOMALIA_DE_DADOS", f"força de trabalho fora de 0–100: {invalid_workforce}"))

    invalid_json = 0
    for row in rows:
        for field, value in row.items():
            if field.endswith("_json") and value not in (None, ""):
                try:
                    json.loads(str(value))
                except json.JSONDecodeError:
                    invalid_json += 1
    if invalid_json:
        findings.append(_finding("ANOMALIA_DE_DADOS", f"campos JSON inválidos: {invalid_json}"))

    owner_executor = sum(
        bool(
            row.get("unidade_dona_sigla")
            and row.get("unidade_executora_sigla")
            and row["unidade_dona_sigla"] != row["unidade_executora_sigla"]
        )
        for row in rows
    )
    if owner_executor:
        findings.append(_finding(
            "DIVERGENCIA_SEMANTICA",
            f"vínculos com unidade dona diferente da executora: {owner_executor}",
            "informativo",
        ))
    return findings
