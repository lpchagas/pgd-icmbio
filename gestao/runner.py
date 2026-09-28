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
from lib.periodos import ANALYSIS_TIMEZONE, configure_execution_context
from lib.liberacao import exigir_execucao_autorizada
from relatorios.escopo import resolver_para_runner, scope_from_values

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
    parser.add_argument("--usar-existentes", action="store_true", help="Reconcilia artefatos já gerados no mesmo escopo.")
    return parser


def _seletor(args: argparse.Namespace) -> dict:
    valores = {nome: getattr(args, nome) for nome in ("regional", "unidade", "mesogrupo", "tipo_unidade", "lista_unidades")}
    valores = {nome: valor for nome, valor in valores.items() if valor}
    return valores or {"escopo": "nacional"}


def _scope_units(args: argparse.Namespace) -> tuple[str, list[str] | None, str]:
    """Resolução única de escopo (L5): mesmas regras e chave da extração OCDE e dos relatórios."""

    return resolver_para_runner(
        escopo=args.escopo, regional=args.regional, unidade=args.unidade,
        mesogrupo=args.mesogrupo, tipo_unidade=args.tipo_unidade, lista_unidades=args.lista_unidades,
    )


def run(argv: list[str] | None = None) -> dict:
    args = build_parser().parse_args(argv)
    registry_problems = validate_registry()
    if registry_problems:
        raise RuntimeError("Registro de gestão inválido: " + "; ".join(registry_problems))
    window = configure_execution_context(args.data_execucao)
    scope_label, units, scope_key = _scope_units(args)
    selected = enabled_extractions() if args.analise == "todas" else [REGISTRY[args.analise]]
    # Gate de liberação (L5): o produto restrito segue o uso atual; o compartilhável
    # fora dos pilotos exige elegibilidade das capacidades.
    liberacao = exigir_execucao_autorizada(
        "gestao.runner", scope_from_values(**_seletor(args)), args.produto,
        capacidades=[extraction.code for extraction in selected], final=args.produto == "compartilhavel",
    )
    output_dir = PROJECT_ROOT / "artefatos_local" / "gestao" / window.mes_execucao / "escopos" / scope_key
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
        if args.usar_existentes:
            candidates = sorted(output_dir.glob(f"{extraction.artifact_prefix}.2_*_{args.produto}_*.csv"), key=lambda path: (path.stat().st_mtime_ns, path.name)) if output_dir.exists() else []
            # Mantém somente a versão mais recente de cada visão (painel, detalhe,
            # entregas, histórico ou nominal), sem atravessar o diretório do escopo.
            latest_by_view: dict[str, Path] = {}
            for path in candidates:
                view = path.name.split(".2_", 1)[1].split(f"_{args.produto}_", 1)[0]
                latest_by_view[view] = path
            files = [_inspect_csv(path) for path in latest_by_view.values()]
            results.append({
                "codigo": extraction.code, "nome": extraction.name, "lentes": lenses,
                "status": "sucesso" if files else "erro_sem_artefato",
                "schema": extraction.output_schema, "privacidade": args.produto,
                "contem_narrativa": extraction.contains_narrative,
                "adaptador_relatorio": extraction.report_adapter,
                "arquivos": files, "erro": "",
            })
            continue
        before = set(output_dir.glob(f"{extraction.artifact_prefix}.2_*.csv")) if output_dir.exists() else set()
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
        after = set(output_dir.glob(f"{extraction.artifact_prefix}.2_*.csv")) if output_dir.exists() else set()
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
            "adaptador_relatorio": extraction.report_adapter,
            "arquivos": files,
            "erro": redact_log(completed.stderr[-1000:]) if completed.returncode else "",
        })

    failure = any(item["status"].startswith("erro") for item in results)
    manifest = {
        "tipo": "extracao_gestao",
        **window.as_dict(),
        "data_hora_extracao": datetime.now(ZoneInfo(ANALYSIS_TIMEZONE)).isoformat(timespec="seconds"),
        "lentes_solicitadas": sorted(requested_lenses),
        "escopo": {"rotulo": scope_label, "chave": scope_key, "unidades": units or []},
        "produto": args.produto,
        "liberacao": liberacao,
        "dry_run": args.dry_run,
        "artefatos_existentes_reconciliados": args.usar_existentes,
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
