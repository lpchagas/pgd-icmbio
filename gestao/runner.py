"""Executa somente análises de gestão registradas e gera manifesto verificável."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from lib.auditoria import minimal_subprocess_env, redact_log
from lib.csv_utils import PROJECT_ROOT
from lib.estrutura_organizacional import load_organization_structure
from lib.periodos import ANALYSIS_TIMEZONE, configure_execution_context

from .registry import REGISTRY, enabled_extractions, validate_registry


def _hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _inspect_csv(path: Path) -> dict:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream, delimiter="|")
        header = next(reader, [])
        rows = sum(1 for _ in reader)
    return {"arquivo": path.name, "linhas": rows, "colunas": header, "sha256": _hash(path)}


def _scope_group(parser: argparse.ArgumentParser) -> None:
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--escopo", choices=("nacional",))
    scope.add_argument("--regional")
    scope.add_argument("--unidade")
    scope.add_argument("--mesogrupo")
    scope.add_argument("--tipo-unidade")
    scope.add_argument("--lista-unidades", type=Path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extrai análises registradas de gestao/.")
    parser.add_argument("--analise", default="todas", choices=("todas", *REGISTRY))
    parser.add_argument("--data-execucao", required=True)
    parser.add_argument("--lente", default="ambas", choices=("acumulada", "operacional", "ambas"))
    _scope_group(parser)
    parser.add_argument("--produto", default="restrito", choices=("restrito", "compartilhavel"))
    parser.add_argument("--dry-run", action="store_true")
    return parser


def _list_values(path: Path) -> list[str]:
    values = [line.strip() for line in path.read_text(encoding="utf-8-sig").splitlines()]
    return [value for value in values if value and not value.startswith("#")]


def _scope_units(args: argparse.Namespace) -> tuple[str, list[str] | None]:
    if args.escopo == "nacional":
        return "nacional", None
    structure = load_organization_structure()
    if not structure.units_by_id:
        raise FileNotFoundError("ICMBIO_estrutura.csv é obrigatório para o seletor solicitado.")
    listed = _list_values(args.lista_unidades) if args.lista_unidades else None
    units = structure.select(
        regional=args.regional,
        unidade=args.unidade,
        mesogrupo=args.mesogrupo,
        tipo_unidade=args.tipo_unidade,
        lista_unidades=listed,
    )
    if not units:
        raise ValueError("O seletor de escopo não encontrou unidades.")
    label = next(
        f"{name}:{value}" for name, value in (
            ("regional", args.regional), ("unidade", args.unidade),
            ("mesogrupo", args.mesogrupo), ("tipo-unidade", args.tipo_unidade),
            ("lista-unidades", str(args.lista_unidades) if args.lista_unidades else None),
        ) if value
    )
    return label, sorted({unit.sigla for unit in units if unit.sigla})


def run(argv: list[str] | None = None) -> dict:
    args = build_parser().parse_args(argv)
    registry_problems = validate_registry()
    if registry_problems:
        raise RuntimeError("Registro de gestão inválido: " + "; ".join(registry_problems))
    window = configure_execution_context(args.data_execucao)
    scope_label, units = _scope_units(args)
    output_dir = PROJECT_ROOT / "artefatos_local" / "gestao" / window.mes_execucao
    selected = enabled_extractions() if args.analise == "todas" else [REGISTRY[args.analise]]
    requested_lenses = {"acumulada", "operacional"} if args.lente == "ambas" else {args.lente}
    results: list[dict] = []
    started = datetime.now(ZoneInfo(ANALYSIS_TIMEZONE))

    for extraction in selected:
        lenses = sorted(requested_lenses.intersection(extraction.temporal_lenses))
        if not lenses:
            results.append({
                "codigo": extraction.code,
                "status": "nao_aplicavel",
                "motivo": "A análise não oferece a lente solicitada.",
            })
            continue
        before = set(output_dir.glob(f"{extraction.code}.2_*.csv")) if output_dir.exists() else set()
        command = [
            sys.executable, str(extraction.entrypoint),
            "--data-execucao", window.data_execucao.isoformat(),
            "--produto", args.produto,
            "--out", str(output_dir),
        ]
        if units is None:
            command.append("--todas")
        else:
            for unit in units:
                command.extend(("--unidade", unit))
        if args.dry_run:
            command.append("--dry-run")
        completed = subprocess.run(
            command, cwd=PROJECT_ROOT, capture_output=True, text=True,
            encoding="utf-8", errors="replace", env=minimal_subprocess_env(),
        )
        after = set(output_dir.glob(f"{extraction.code}.2_*.csv")) if output_dir.exists() else set()
        files = [_inspect_csv(path) for path in sorted(after - before)]
        status = "dry-run" if args.dry_run and completed.returncode == 0 else "sucesso"
        if completed.returncode:
            status = "erro"
        elif not args.dry_run and not files:
            status = "erro_sem_artefato"
        results.append({
            "codigo": extraction.code,
            "nome": extraction.name,
            "lentes": lenses,
            "status": status,
            "schema": extraction.output_schema,
            "privacidade": args.produto,
            "contem_narrativa": extraction.contains_narrative,
            "arquivos": files,
            "erro": redact_log(completed.stderr[-1000:]) if completed.returncode else "",
        })

    failure = any(item["status"].startswith("erro") for item in results)
    manifest = {
        "tipo": "extracao_gestao",
        **window.as_dict(),
        "data_hora_extracao": datetime.now(ZoneInfo(ANALYSIS_TIMEZONE)).isoformat(timespec="seconds"),
        "lentes_solicitadas": sorted(requested_lenses),
        "escopo": scope_label,
        "produto": args.produto,
        "dry_run": args.dry_run,
        "status_global": "falha" if failure else "dry-run" if args.dry_run else "sucesso",
        "resultados": results,
    }
    if not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / f"manifesto_gestao_{args.produto}.json"
        path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        manifest["manifesto"] = str(path)
    return manifest


def main(argv: list[str] | None = None) -> int:
    manifest = run(argv)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 1 if manifest["status_global"] == "falha" else 0


if __name__ == "__main__":
    raise SystemExit(main())
