"""Sanitização local e priorização transparente de textos de execução PE/PT."""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from typing import Iterable, Mapping


_EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
_CPF = re.compile(r"(?<!\d)(?:\d{3}[.\s-]?){3}\d{2}(?!\d)")
_PHONE = re.compile(r"(?<!\d)(?:\+?55\s*)?(?:\(?\d{2}\)?\s*)?9?\d{4}[-.\s]?\d{4}(?!\d)")
_ADDRESS = re.compile(
    r"\b(?:rua|avenida|av\.?|travessa|alameda|rodovia|estrada)\s+[^,;\n]{3,80}", re.I
)
_SPACE = re.compile(r"\s+")
# Intervalos de anos ("2025-2027"), processos SEI formatados ("02070.020242/2025-88") e documentos
# SEI citados com o prefixo ("SEI nº 23687646") não são dado pessoal; sem esta proteção, casavam o
# padrão de telefone de 8 dígitos.
PROTECTED_SPANS = re.compile(
    r"(?<![\w.-])(?:(?:19|20)\d{2} ?[-–] ?(?:19|20)\d{2}|\d{5}\.\d{6}/\d{4}-\d{2}"
    r"|SEI\s*(?:n[º°o]\.?\s*)?\d{7,10})(?!\w)",
    re.I,
)


def _fold(value: str) -> str:
    return unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().upper()


@dataclass(frozen=True)
class SanitizedText:
    text: str
    redactions: tuple[str, ...]


class TextSanitizer:
    """Remove PII sem enviar textos ou dicionários de nomes a serviços externos."""

    def __init__(self, person_names: Iterable[str] = ()) -> None:
        names = {_SPACE.sub(" ", str(name)).strip() for name in person_names}
        self._names = sorted((name for name in names if len(name) >= 4), key=len, reverse=True)

    def sanitize(self, value: object) -> SanitizedText:
        text = _SPACE.sub(" ", str(value or "").replace("\x00", " ")).strip()
        redactions: list[str] = []
        protected: list[str] = []

        def protect(match: re.Match[str]) -> str:
            protected.append(match.group(0))
            return f"[PROTEGIDO_{len(protected) - 1}]"

        text = PROTECTED_SPANS.sub(protect, text)
        for label, pattern in (
            ("email", _EMAIL), ("cpf", _CPF), ("telefone", _PHONE), ("endereco", _ADDRESS)
        ):
            text, count = pattern.subn(f"[DADO_PESSOAL_{label.upper()}]", text)
            if count:
                redactions.append(label)
        for index, span in enumerate(protected):
            text = text.replace(f"[PROTEGIDO_{index}]", span, 1)
        folded = _fold(text)
        for name in self._names:
            folded_name = _fold(name)
            start = folded.find(folded_name)
            while start >= 0:
                text = text[:start] + "[NOME_SUPRIMIDO]" + text[start + len(name):]
                folded = _fold(text)
                redactions.append("nome")
                start = folded.find(folded_name)
        return SanitizedText(text=text, redactions=tuple(sorted(set(redactions))))


def _number(value: object) -> float:
    try:
        return float(str(value or 0).replace(",", "."))
    except (TypeError, ValueError):
        return 0.0


def _date(value: object) -> date | None:
    try:
        return date.fromisoformat(str(value or "")[:10])
    except ValueError:
        return None


def priority_assessment(record: Mapping[str, object], reference_date: date) -> dict[str, object]:
    """Pontua evidências operacionais; não infere resultado do PE a partir do PT."""

    kind = str(record.get("tipo_registro") or "").upper()
    status = str(record.get("status") or "").upper()
    due = _date(record.get("data_fim") or record.get("prazo"))
    expected = _number(record.get("progresso_esperado"))
    actual = _number(record.get("progresso_realizado") or record.get("progresso"))
    score = 0
    triggers: list[str] = []
    if due and due < reference_date and status not in {"CONCLUIDO", "AVALIADO", "CANCELADO"}:
        score += 40
        triggers.append("prazo_vencido_sem_conclusao")
    if kind == "PE" and expected > 0 and actual < expected:
        gap = max(expected - actual, 0)
        score += min(35, round(gap * 0.35))
        triggers.append("meta_pe_abaixo_do_pactuado")
    if kind in {"PT", "ATIVIDADE"} and status in {"INCLUIDO", "SUSPENSO", "AGUARDANDO_ASSINATURA"}:
        score += 25
        triggers.append("status_operacional_requer_acao")
    if _number(record.get("tempo_despendido")) > _number(record.get("tempo_planejado")) > 0:
        score += 15
        triggers.append("esforco_acima_do_planejado")
    level = "crítica" if score >= 60 else "alta" if score >= 40 else "moderada" if score >= 20 else "rotina"
    return {"pontuacao_prioridade": min(score, 100), "prioridade": level, "gatilhos": triggers}
