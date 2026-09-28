"""Marco obrigatório GR2 → nacional → seletores e critério final de conclusão.

Registro histórico da política ``gr2-v1``. Desde o L5 a liberação além dos pilotos é
decidida por ``lib.liberacao`` (três aceites e deliberação); estes registros ficam
marcados com a política de origem, sem reinterpretação.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


TIMEZONE = ZoneInfo("America/Sao_Paulo")
POLITICA = "gr2-v1"


def initial_state() -> dict[str, Any]:
    return {
        "politica": POLITICA,
        "fase": "piloto_gr2",
        "projeto_concluido": False,
        "gr2": {"execucao_tecnica": False, "revisao_gerencial": False, "revisao_lgpd": False},
        "nacional": {"execucao_tecnica": False, "aprovado": False, "reconciliado": False},
        "seletores_validados": {
            "unidade": False,
            "mesogrupo": False,
            "tipo_unidade": False,
            "lista_unidades": False,
        },
        "historico_execucoes": [],
    }


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return initial_state()
    with path.open(encoding="utf-8") as stream:
        stored = json.load(stream)
    base = initial_state()
    base["fase"] = stored.get("fase", base["fase"])
    base["projeto_concluido"] = stored.get("projeto_concluido", False)
    base["politica"] = stored.get("politica", POLITICA)
    base["historico_execucoes"] = [
        {"politica": POLITICA, **item} if isinstance(item, dict) else item
        for item in stored.get("historico_execucoes", [])
    ]
    base["gr2"].update(stored.get("gr2", {}))
    base["nacional"].update(stored.get("nacional", {}))
    base["seletores_validados"].update(stored.get("seletores_validados", {}))
    return base


def register_execution(
    state: dict[str, Any],
    *,
    scope_kind: str,
    scope_value: str,
    month: str,
    technical_ok: bool,
    management_review: bool = False,
    privacy_review: bool = False,
    national_approved: bool = False,
    national_reconciled: bool = False,
) -> dict[str, Any]:
    state["historico_execucoes"].append(
        {
            "momento": datetime.now(TIMEZONE).isoformat(timespec="seconds"),
            "mes_execucao": month,
            "tipo_escopo": scope_kind,
            "valor_escopo": scope_value,
            "validacao_tecnica": technical_ok,
            "politica": POLITICA,
        }
    )
    if scope_kind == "regional" and scope_value == "GR2":
        state["gr2"]["execucao_tecnica"] = bool(technical_ok)
        state["gr2"]["revisao_gerencial"] |= bool(management_review)
        state["gr2"]["revisao_lgpd"] |= bool(privacy_review)
    elif scope_kind == "nacional":
        state["nacional"]["execucao_tecnica"] |= bool(technical_ok)
        state["nacional"]["aprovado"] |= bool(national_approved)
        state["nacional"]["reconciliado"] |= bool(national_reconciled)
    elif scope_kind in state["seletores_validados"]:
        state["seletores_validados"][scope_kind] |= bool(technical_ok)

    gr2_ok = all(state["gr2"].values())
    national_ok = all(state["nacional"].values())
    selectors = state["seletores_validados"]
    selectors_ok = all(selectors.values())
    if not gr2_ok:
        state["fase"] = "piloto_gr2"
    elif not national_ok:
        state["fase"] = "expansao_nacional_obrigatoria"
    elif not selectors_ok:
        state["fase"] = "validacao_seletores_obrigatoria"
    else:
        state["fase"] = "concluido"
    state["projeto_concluido"] = gr2_ok and national_ok and selectors_ok
    return state


def save_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as stream:
        json.dump(state, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
