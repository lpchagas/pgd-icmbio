"""Registra a decisão humana inicial sem refazer cálculos nem armazenar nomes."""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from lib.csv_utils import PROJECT_ROOT
from lib.periodos import ANALYSIS_TIMEZONE
from lib.validation_contracts import normalize_target


DEFAULT_BASELINE = PROJECT_ROOT / "artefatos_local" / "validacao" / "baselines.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifesto", type=Path, required=True)
    parser.add_argument("--alvo", action="append", required=True, help="Alvo repetível ou lista separada por vírgula.")
    parser.add_argument("--papel-aprovador", required=True, help="Papel institucional, não nome pessoal.")
    parser.add_argument("--decisao", choices=("HOMOLOGADO", "REPROVADO"), required=True)
    parser.add_argument("--justificativa", required=True)
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def approve(argv: list[str] | None = None) -> dict:
    args = build_parser().parse_args(argv)
    manifest = json.loads(args.manifesto.read_text(encoding="utf-8"))
    codes = []
    for value in args.alvo:
        codes.extend(normalize_target(item) for item in value.split(",") if item.strip())
    codes = list(dict.fromkeys(codes))
    if "G02" in codes and len(codes) > 1:
        raise ValueError("G02/D18 deve ser aprovado separadamente dos alvos da D15.")
    results = {item.get("alvo"): item for item in manifest.get("resultados", [])}
    missing = [code for code in codes if code not in results]
    if missing:
        raise ValueError(f"Alvo(s) ausente(s) do manifesto: {', '.join(missing)}")
    if args.decisao == "HOMOLOGADO" and manifest.get("modo") != "integrado":
        raise ValueError("Fixture não pode constituir baseline homologada.")
    if args.decisao == "HOMOLOGADO" and manifest.get("status_global") == "falha":
        raise ValueError("Manifesto com falha não pode formar baseline.")
    for code in codes:
        result = results[code]
        if args.decisao == "HOMOLOGADO" and result.get("status") not in {"sucesso", "pendente"}:
            raise ValueError(f"Resultado {code} incompleto ou com falha não pode ser homologado.")
        required_hashes = {"A1", "oracle", "production_sql", "extractors", "schema"}
        if args.decisao == "HOMOLOGADO" and not required_hashes <= set(result.get("hashes", {})):
            raise ValueError(f"Resultado {code} não contém todos os hashes metodológicos.")
    if any(token in args.papel_aprovador.lower() for token in ("@", ".com", ".gov")):
        raise ValueError("Informe um papel institucional, não e-mail ou nome de pessoa.")

    current = {}
    if args.baseline.is_file():
        current = json.loads(args.baseline.read_text(encoding="utf-8"))
    scope = manifest.get("escopo", {})
    scope_key = scope.get("chave") if isinstance(scope, dict) else str(scope)
    if not scope_key:
        raise ValueError("Manifesto sem chave explícita de escopo.")
    approved_at = datetime.now(ZoneInfo(ANALYSIS_TIMEZONE)).isoformat(timespec="seconds")
    for code in codes:
        result = results[code]
        previous = current.get(code, {})
        profiles_by_scope = dict(previous.get("profiles_by_scope", {}))
        profiles_by_scope[scope_key] = {
            profile.get("visao", "principal"): profile for profile in result.get("perfis_A2", [])
        }
        current[code] = {
            "status": args.decisao,
            "formula_version": result.get("formula_version"),
            "approved_run_id": manifest.get("run_id"),
            "approved_at": approved_at,
            "approved_by_role": args.papel_aprovador,
            "justificativa": args.justificativa,
            "fingerprint": manifest.get("fingerprint"),
            "hashes": result.get("hashes", {}),
            "profiles_by_scope": profiles_by_scope,
        }
    if not args.dry_run:
        args.baseline.parent.mkdir(parents=True, exist_ok=True)
        temporary = args.baseline.with_suffix(".tmp")
        temporary.write_text(json.dumps(current, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(args.baseline)
    return {"alvos": codes, "escopo": scope_key, "decisao": args.decisao, "dry_run": args.dry_run}


def main(argv: list[str] | None = None) -> int:
    print(json.dumps(approve(argv), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
