"""Controles de divulgação para produtos gerenciais anonimizados."""
from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, MutableMapping, Sequence


K_MIN = 5
SUPPRESSED = "Suprimido (k<5)"
FORBIDDEN_FIELD_TOKENS = (
    "cpf",
    "email",
    "e_mail",
    "nome_servidor",
    "usuario_id",
    "id_servidor",
    "atividade_id",
    "id_atividade",
    "plano_trabalho_id",
    "id_plano_trabalho",
    "justificativa",
    "descricao_entrega",
    "nome_entrega",
    "ocorrencia",
    "afastamento",
    "recurso",
    "checklist",
)
_EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
_UUID = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b", re.I)
_CPF = re.compile(r"(?<![A-Za-z0-9])(?:\d{3}[.\s-]?){3}\d{2}(?![A-Za-z0-9])")


class PrivacyError(RuntimeError):
    pass


def count_band(value: int | float | str | None, k: int = K_MIN) -> str:
    try:
        count = int(float(value or 0))
    except (TypeError, ValueError):
        count = 0
    if count < k:
        return SUPPRESSED
    if count < 10:
        return "5–9"
    if count < 20:
        return "10–19"
    if count < 50:
        return "20–49"
    if count < 100:
        return "50–99"
    return "100+"


def quantity_band(value: int | float | str | None) -> str:
    """Generaliza quantidades não pessoais sem aplicar o limiar de pessoas."""
    try:
        count = int(float(value or 0))
    except (TypeError, ValueError):
        count = 0
    if count == 0:
        return "0"
    if count < 5:
        return "1–4"
    return count_band(count)


def rounded_percent(numerator: float, denominator: float) -> str:
    if denominator <= 0:
        return "N/D"
    return f"{numerator * 100.0 / denominator:.1f}%"


def eligible(distinct_people: int, k: int = K_MIN) -> bool:
    return distinct_people >= k


def apply_complementary_suppression(
    rows: Sequence[MutableMapping[str, object]],
    *,
    parent_keys: Sequence[str],
    count_key: str,
    suppressed_key: str = "suprimido",
) -> list[MutableMapping[str, object]]:
    """Oculta um segundo subtotal quando um único subtotal primário foi ocultado."""
    grouped: dict[tuple[object, ...], list[MutableMapping[str, object]]] = {}
    for row in rows:
        grouped.setdefault(tuple(row.get(key) for key in parent_keys), []).append(row)
    for siblings in grouped.values():
        hidden = [row for row in siblings if bool(row.get(suppressed_key))]
        visible = [row for row in siblings if not bool(row.get(suppressed_key))]
        if len(hidden) == 1 and visible:
            smallest = min(visible, key=lambda row: float(row.get(count_key) or 0))
            smallest[suppressed_key] = True
            smallest["motivo_supressao"] = "complementar"
    return list(rows)


def forbidden_fields(fields: Iterable[str]) -> list[str]:
    found: list[str] = []
    for field in fields:
        normalized = str(field).strip().lower()
        if any(token in normalized for token in FORBIDDEN_FIELD_TOKENS):
            found.append(str(field))
    return found


def redact_personal_identifiers(text: str) -> str:
    """Redação irreversível para evidências textuais; não persiste pseudônimos."""

    value = _EMAIL.sub("[EMAIL_REMOVIDO]", text)
    value = _UUID.sub("[ID_REMOVIDO]", value)
    return _CPF.sub("[CPF_REMOVIDO]", value)


def scan_text(text: str) -> list[str]:
    findings: list[str] = []
    if _EMAIL.search(text):
        findings.append("possível e-mail")
    if _UUID.search(text):
        findings.append("possível UUID")
    if _CPF.search(text):
        findings.append("possível CPF")
    first_line = text.splitlines()[0] if text.splitlines() else ""
    fields = re.split(r"[|,;]", first_line)
    findings.extend(f"campo proibido: {field}" for field in forbidden_fields(fields))
    return sorted(set(findings))


def scan_file(path: Path) -> list[str]:
    if path.suffix.lower() == ".pdf":
        # O texto-fonte é verificado antes da renderização; a validação do PDF
        # é feita pelo exportador com pypdf quando disponível.
        return []
    return scan_text(path.read_text(encoding="utf-8", errors="replace"))


def assert_safe_outputs(paths: Iterable[Path]) -> None:
    problems: list[str] = []
    for path in paths:
        problems.extend(f"{path.name}: {finding}" for finding in scan_file(path))
    if problems:
        raise PrivacyError("Produto bloqueado pela verificação LGPD:\n- " + "\n- ".join(problems))


@dataclass(frozen=True)
class DisclosureAssessment:
    k_minimo: int
    grupos_publicados: int
    grupos_suprimidos: int
    supressao_complementar_aplicada: bool
    risco_longitudinal_revisado: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "k_minimo": self.k_minimo,
            "grupos_publicados": self.grupos_publicados,
            "grupos_suprimidos": self.grupos_suprimidos,
            "supressao_complementar_aplicada": self.supressao_complementar_aplicada,
            "risco_longitudinal_revisado": self.risco_longitudinal_revisado,
        }


def previous_editions_exist(base: Path, current_month: str) -> bool:
    return any(path.name < current_month for path in base.glob("????-??") if path.is_dir())


def review_longitudinal(
    base: Path,
    current_month: str,
    scope_slug: str,
    current_rows: Sequence[Mapping[str, str]],
) -> list[str]:
    """Sinaliza mudanças suprimido→publicado entre edições para revisão humana."""
    previous = sorted(
        path for month in base.glob("????-??") if month.is_dir() and month.name < current_month
        for path in month.glob(f"indicadores_acumulados_{scope_slug}_*.csv")
    )
    if not previous:
        return []
    with previous[-1].open(encoding="utf-8-sig", errors="replace", newline="") as stream:
        old_rows = list(csv.DictReader(stream, delimiter="|"))
    old_status = {row.get("indicador", ""): row.get("situacao_divulgacao", "") for row in old_rows}
    warnings = []
    for row in current_rows:
        code = row.get("indicador", "")
        if old_status.get(code) == "suprimido_k" and row.get("situacao_divulgacao") == "publicado":
            warnings.append(f"{code}: passou de suprimido para publicado; revisar composição do grupo")
    return warnings
