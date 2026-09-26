"""Runner oficial dos indicadores OCDE/PGD.

As skills apenas encaminham para este módulo. A regra temporal, os destinos e
o manifesto permanecem no código do projeto para evitar implementações
divergentes entre Codex, Claude Code e Antigravity.
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .auditoria import minimal_subprocess_env, redact_log
from .csv_utils import PROJECT_ROOT, indicator_csv_dir
from .escopos import slug
from .periodos import ANALYSIS_TIMEZONE, configure_execution_context
from .validation_contracts import TARGETS, ocde_artifact
from relatorios.escopo import filter_rows, load_unit_profiles, scope_from_values


INDICATORS: tuple[tuple[str, str, str, int], ...] = tuple(
    (target.code[1:], target.production_entrypoint.name, target.name, len(target.outputs))
    for target in TARGETS.values() if target.family == "ocde"
)


@dataclass
class FileEvidence:
    arquivo: str
    linhas_dados: int
    sha256: str
    colunas: list[str]
    schema_sha256: str
    data_minima: str | None
    data_maxima: str | None


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _csv_evidence(path: Path) -> FileEvidence:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="|")
        columns = reader.fieldnames or []
        rows = list(reader)
    dates = [
        value[:10] for row in rows
        for column in ("periodo_inicio", "periodo_fim_efetivo", "data_referencia")
        for value in [row.get(column, "")] if value
    ]
    schema_hash = hashlib.sha256(
        json.dumps(columns, ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    return FileEvidence(
        arquivo=path.name, linhas_dados=len(rows), sha256=_sha256(path),
        colunas=columns, schema_sha256=schema_hash,
        data_minima=min(dates) if dates else None, data_maxima=max(dates) if dates else None,
    )


def _sql_hash(path: Path) -> str:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    sql = [
        node.value for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
        and "SELECT" in node.value.upper()
    ]
    return hashlib.sha256("\n".join(sql).encode("utf-8")).hexdigest()


def _indicator_files(directory: Path, number: str) -> set[Path]:
    return {path.resolve() for path in directory.glob(ocde_artifact(number, "2_*.csv"))}


def _normalize_indicator(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip().upper().removeprefix("I")
    if not re.fullmatch(r"\d{1,2}", normalized):
        raise ValueError("--so deve identificar I01 a I12.")
    normalized = normalized.zfill(2)
    if normalized not in {item[0] for item in INDICATORS}:
        raise ValueError("--so deve identificar I01 a I12.")
    return normalized


def _manifest_filename(full_cycle: bool, run_id: str) -> str:
    return (
        "manifesto_extracao_indicadores.json"
        if full_cycle else f"manifesto_extracao_indicadores_parcial_{run_id}.json"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extrai os indicadores OCDE/PGD.")
    parser.add_argument("--data-execucao", required=True, help="AAAA-MM-DD")
    parser.add_argument("--so", help="Executa somente IXX; não conclui o ciclo mensal.")
    parser.add_argument("--reextrair", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--salvar-manifesto", action="store_true")
    parser.add_argument("--usar-existentes", action="store_true", help="Monta o manifesto do escopo sem consultar novamente.")
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--escopo", choices=("nacional",))
    scope.add_argument("--regional")
    scope.add_argument("--unidade")
    scope.add_argument("--mesogrupo")
    scope.add_argument("--tipo-unidade")
    scope.add_argument("--lista-unidades", type=Path)
    return parser


def _persist_scoped(source: Path, destination: Path, scope) -> bool:
    if scope.kind == "nacional":
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        return True
    with source.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="|")
        header = reader.fieldnames or []
        rows = list(reader)
    if "visao" in header:
        rows = [row for row in rows if not (source.name.startswith("IND_OCDE_01.") and row.get("visao") == "institucional")]
    rows = filter_rows(rows, scope, load_unit_profiles())
    if not rows and source.name.startswith("IND_OCDE_01."):
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=header, delimiter="|")
        writer.writeheader()
        writer.writerows(rows)
    return True


def run(argv: list[str] | None = None) -> dict:
    args = build_parser().parse_args(argv)
    only = _normalize_indicator(args.so)
    window = configure_execution_context(args.data_execucao)
    scope = scope_from_values(
        escopo=args.escopo or ("nacional" if not any((args.regional, args.unidade, args.mesogrupo, args.tipo_unidade, args.lista_unidades)) else None), regional=args.regional, unidade=args.unidade,
        mesogrupo=args.mesogrupo, tipo_unidade=args.tipo_unidade,
        lista_unidades=args.lista_unidades,
    )
    scope_key = f"{slug(scope.kind)}-{slug(scope.value)}"
    output_dir = indicator_csv_dir(window.mes_execucao) / "escopos" / scope_key
    selected = [item for item in INDICATORS if only in (None, item[0])]
    started = datetime.now(ZoneInfo(ANALYSIS_TIMEZONE))
    run_fingerprint = hashlib.sha256(
        json.dumps({"window": window.as_dict(), "selected": [item[0] for item in selected]}, sort_keys=True).encode("utf-8")
    ).hexdigest()[:8]
    run_id = f"{started.strftime('%Y%m%dT%H%M%S')}-{run_fingerprint}"
    results: list[dict] = []

    staging_context = tempfile.TemporaryDirectory(prefix="pgd-ocde-a2-")
    staging_base = Path(staging_context.name)
    for number, script_name, name, expected_files in selected:
        script = PROJECT_ROOT / "ocde" / "indicadores" / script_name
        target = TARGETS[f"I{number}"]
        if args.usar_existentes:
            created: list[Path] = []
            for contract in target.outputs:
                if scope.kind != "nacional" and number == "01" and contract.view == "institucional":
                    continue
                candidates = sorted(output_dir.glob(contract.pattern), key=lambda path: (path.stat().st_mtime_ns, path.name))
                if candidates:
                    created.append(candidates[-1])
            results.append({
                "indicador": f"I{number}", "nome": name,
                "status": "sucesso" if created else "erro_sem_artefato",
                "formula_version": target.formula_version, "hash_A1": _sha256(script),
                "hash_sql": _sql_hash(script), "duracao_segundos": 0.0,
                "arquivos": [asdict(_csv_evidence(path)) for path in created], "erro": "",
            })
            continue
        staging_dir = staging_base / window.mes_execucao
        before = _indicator_files(staging_dir, number) if staging_dir.exists() else set()
        command = [
            sys.executable,
            str(script),
            "--data-execucao",
            window.data_execucao.isoformat(),
            "--month",
            window.mes_execucao,
        ]
        if args.dry_run:
            command.append("--dry-run")
        step_started = datetime.now(ZoneInfo(ANALYSIS_TIMEZONE))
        completed = (
            subprocess.CompletedProcess(command, 0, stdout="dry-run: contrato A1 validado", stderr="")
            if args.dry_run
            else subprocess.run(
                command,
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env={**minimal_subprocess_env(), "PGD_INDICATOR_OUTPUT_BASE": str(staging_base)},
            )
        )
        after = _indicator_files(staging_dir, number) if staging_dir.exists() else set()
        staged = sorted(after - before)
        created = []
        for source in staged:
            destination = output_dir / source.name
            if _persist_scoped(source, destination, scope):
                created.append(destination)
        evidence = [asdict(_csv_evidence(path)) for path in created]
        status = "dry-run" if args.dry_run and completed.returncode == 0 else "sucesso"
        if completed.returncode != 0:
            status = "erro"
        elif not args.dry_run and not created:
            status = "erro_sem_artefato"
        results.append(
            {
                "indicador": f"I{number}",
                "nome": name,
                "status": status,
                "formula_version": target.formula_version,
                "hash_A1": _sha256(script),
                "hash_sql": _sql_hash(script),
                "duracao_segundos": round(
                    (datetime.now(ZoneInfo(ANALYSIS_TIMEZONE)) - step_started).total_seconds(), 3
                ),
                "arquivos": evidence,
                "erro": redact_log(completed.stderr[-1000:]) if completed.returncode else "",
            }
        )

    failures = [item for item in results if item["status"].startswith("erro")]
    full_cycle = only is None
    manifest = {
        "tipo": "extracao_indicadores_ocde",
        "run_id": run_id,
        **window.as_dict(),
        "data_hora_inicio": started.isoformat(timespec="seconds"),
        "data_hora_fim": datetime.now(ZoneInfo(ANALYSIS_TIMEZONE)).isoformat(timespec="seconds"),
        "fuso_horario": ANALYSIS_TIMEZONE,
        "reextracao_solicitada": args.reextrair,
        "artefatos_existentes_reconciliados": args.usar_existentes,
        "dry_run": args.dry_run,
        "ciclo_completo": full_cycle,
        "status_global": (
            "falha" if failures else "dry-run" if args.dry_run else "sucesso" if full_cycle else "parcial"
        ),
        "escopo": {**scope.as_dict(), "chave": scope_key},
        "resultados": results,
    }
    if args.salvar_manifesto and not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)
        manifest_name = _manifest_filename(full_cycle, run_id)
        path = output_dir / manifest_name
        path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        manifest["manifesto"] = str(path)
    staging_context.cleanup()
    return manifest


def main(argv: list[str] | None = None) -> int:
    manifest = run(argv)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 1 if manifest["status_global"] == "falha" else 0


if __name__ == "__main__":
    raise SystemExit(main())
