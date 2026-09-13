"""Orquestrador retomável do ciclo gerencial mensal."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .auditoria import minimal_subprocess_env, redact_log
from .csv_utils import PROJECT_ROOT, indicator_csv_dir
from .periodos import ANALYSIS_TIMEZONE, configure_execution_context
from .validation_contracts import TARGETS, artifact_indicator_number


STAGES = (
    "preflight",
    "analysis_window",
    "extrair_indicadores",
    "extrair_gestao",
    "validar_contratos_a1_a2",
    "validar_oracles_a3",
    "diagnosticos_a4",
    "gerar_a5",
    "validar_periodicidade",
    "relatorio_extracao",
    "verificar_consistencia",
    "relatorio_gerencial_v2",
    "auditar_seguranca",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-execucao", required=True)
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--escopo", choices=("nacional",))
    scope.add_argument("--regional")
    scope.add_argument("--unidade")
    scope.add_argument("--mesogrupo")
    scope.add_argument("--tipo-unidade")
    scope.add_argument("--lista-unidades", type=Path)
    parser.add_argument("--produto", choices=("restrito", "compartilhavel", "ambos"), default="ambos")
    parser.add_argument("--lente", choices=("acumulada", "operacional", "ambas"), default="ambas")
    parser.add_argument("--reextrair", action="store_true")
    parser.add_argument("--retomar", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--salvar", action="store_true")
    parser.add_argument("--pdf", action="store_true")
    parser.add_argument("--consultar-denodo", action="store_true", help="Inclui evidências textuais PE/PT na V2.")
    parser.add_argument(
        "--denodo-python", default=os.environ.get("PGD_DENODO_PYTHON", sys.executable),
        help="Python com JPype compatível com a JVM/driver Denodo.",
    )
    parser.add_argument(
        "--test-python", default=os.environ.get("PGD_TEST_PYTHON", sys.executable),
        help="Python com pytest e dependências de desenvolvimento.",
    )
    return parser


def _scope_args(args: argparse.Namespace) -> list[str]:
    for name in ("escopo", "regional", "unidade", "mesogrupo", "tipo_unidade", "lista_unidades"):
        value = getattr(args, name)
        if value:
            return ["--" + name.replace("_", "-"), str(value)]
    raise ValueError("Escopo ausente")


def _run(command: list[str]) -> dict:
    started = datetime.now(ZoneInfo(ANALYSIS_TIMEZONE))
    completed = subprocess.run(
        command, cwd=PROJECT_ROOT, capture_output=True, text=True,
        encoding="utf-8", errors="replace", env=minimal_subprocess_env(),
    )
    return {
        "status": "sucesso" if completed.returncode == 0 else "falha",
        "inicio": started.isoformat(timespec="seconds"),
        "fim": datetime.now(ZoneInfo(ANALYSIS_TIMEZONE)).isoformat(timespec="seconds"),
        "comando": [Path(part).name if i == 1 and part.endswith(".py") else part for i, part in enumerate(command)],
        "saida_final": redact_log(completed.stdout[-1500:]),
        "erro_final": redact_log(completed.stderr[-1500:]),
    }


def _module_available(python: str, module: str) -> bool:
    try:
        completed = subprocess.run(
            [python, "-c", f"import {module}"], cwd=PROJECT_ROOT,
            capture_output=True, text=True, timeout=30, env=minimal_subprocess_env(),
        )
        return completed.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def _preflight(denodo_python: str, test_python: str) -> dict:
    required = [
        PROJECT_ROOT / ".env",
        PROJECT_ROOT / "lib" / "periodos.py",
        TARGETS["I01"].production_entrypoint,
        TARGETS["PT_STATUS"].production_entrypoint,
        PROJECT_ROOT / "artefatos_local" / "ocde" / "diagnosticos" / "ICMBIO_estrutura.csv",
    ]
    missing = [str(path.relative_to(PROJECT_ROOT)) for path in required if not path.exists()]
    dependencies = {
        "denodo_python_jpype": _module_available(denodo_python, "jpype"),
        "test_python_pytest": _module_available(test_python, "pytest"),
        "test_python_hypothesis": _module_available(test_python, "hypothesis"),
    }
    return {
        "status": "falha" if missing or not all(dependencies.values()) else "sucesso",
        "ausentes": missing,
        "dependencias": dependencies,
        "orientacao": "Configure PGD_DENODO_PYTHON e PGD_TEST_PYTHON quando JVM e pytest estiverem em runtimes distintos.",
    }


def _extraction_report(window) -> dict:
    directory = indicator_csv_dir(window.mes_execucao)
    # Aceita o nome atual (IND_OCDE_07.2_*) e o legado (IND_07.2_*), porque as
    # entregas anteriores a 13.09.2026 permanecem em artefatos_local/.
    codes = {
        number for path in directory.glob("IND_*.2_*.csv")
        for number in [artifact_indicator_number(path.name)] if number
    } if directory.exists() else set()
    missing = [f"I{number:02d}" for number in range(1, 13) if f"{number:02d}" not in codes]
    return {
        "status": "falha" if missing else "sucesso",
        "diretorio": str(directory),
        "indicadores_ausentes": missing,
    }


def run(argv: list[str] | None = None) -> dict:
    args = build_parser().parse_args(argv)
    window = configure_execution_context(args.data_execucao)
    final_path = indicator_csv_dir(window.mes_execucao) / "manifesto_ciclo_gerencial.json"
    manifest = {
        "tipo": "ciclo_gerencial_mensal",
        **window.as_dict(),
        "escopo": _scope_args(args),
        "produto": args.produto,
        "lente": args.lente,
        "etapas": {},
        "status_global": "em_execucao",
    }
    if args.retomar and final_path.exists():
        manifest = json.loads(final_path.read_text(encoding="utf-8"))
        manifest["status_global"] = "em_execucao"
    if args.dry_run:
        manifest["status_global"] = "dry-run"
        manifest["plano_execucao"] = list(STAGES)
        return manifest

    def perform(name: str, action) -> bool:
        if args.retomar and manifest.get("etapas", {}).get(name, {}).get("status") == "sucesso":
            return True
        result = action()
        manifest.setdefault("etapas", {})[name] = result
        final_path.parent.mkdir(parents=True, exist_ok=True)
        final_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        return result.get("status") == "sucesso"

    if not perform("preflight", lambda: _preflight(args.denodo_python, args.test_python)):
        manifest["status_global"] = "falha"
        return manifest
    perform("analysis_window", lambda: {"status": "sucesso", **window.as_dict()})

    indicator_cmd = [args.denodo_python, "-m", "lib.indicator_extraction", "--data-execucao", args.data_execucao, "--salvar-manifesto"]
    if args.reextrair:
        indicator_cmd.append("--reextrair")
    if not perform("extrair_indicadores", lambda: _run(indicator_cmd)):
        manifest["status_global"] = "falha"
        return manifest

    scope_args = _scope_args(args)
    products = ("restrito", "compartilhavel") if args.produto == "ambos" else (args.produto,)
    def run_management() -> dict:
        results = []
        for product in products:
            command = [args.denodo_python, "-m", "gestao.runner", "--analise", "todas",
                       "--data-execucao", args.data_execucao, "--lente", args.lente,
                       "--produto", product, *scope_args]
            results.append(_run(command))
        return {"status": "sucesso" if all(r["status"] == "sucesso" for r in results) else "falha", "execucoes": results}
    if not perform("extrair_gestao", run_management):
        manifest["status_global"] = "falha"
        return manifest

    validation_cmd = [
        args.denodo_python, "-m", "lib.validation_runner",
        "--familia", "todas", "--alvo", "todos",
        "--data-execucao", args.data_execucao,
        "--modo", "integrado", "--produto", args.produto,
        *scope_args,
    ]
    previous_validation = manifest.get("etapas", {}).get("validar_contratos_a1_a2", {})
    validation_result = (
        {"status": "sucesso", "retomado": True}
        if args.retomar and previous_validation.get("status") == "sucesso"
        else _run(validation_cmd)
    )
    if not perform("validar_contratos_a1_a2", lambda: validation_result):
        manifest["status_global"] = "falha"
        return manifest
    for validation_stage in ("validar_oracles_a3", "diagnosticos_a4", "gerar_a5"):
        perform(validation_stage, lambda stage=validation_stage: {
            "status": validation_result["status"],
            "execucao_compartilhada": "validar_contratos_a1_a2",
            "etapa_logica": stage,
        })

    tests_temporal = [args.test_python, "-m", "pytest", "-q", "tests/unit/test_periodos.py"]
    if not perform("validar_periodicidade", lambda: _run(tests_temporal)):
        manifest["status_global"] = "falha"
        return manifest
    if not perform("relatorio_extracao", lambda: _extraction_report(window)):
        manifest["status_global"] = "falha"
        return manifest
    consistency_cmd = [args.test_python, "-m", "pytest", "-q", "tests/unit", "tests/regression"]
    if not perform("verificar_consistencia", lambda: _run(consistency_cmd)):
        manifest["status_global"] = "falha"
        return manifest

    report_python = args.denodo_python if args.consultar_denodo else sys.executable
    report_cmd = [report_python, "-m", "ocde.relatorios.relatorio_v2", "--data-execucao", args.data_execucao,
                  "--produto", args.produto, "--lente", args.lente, *scope_args]
    if args.salvar or args.pdf:
        report_cmd.append("--salvar")
    if args.pdf:
        report_cmd.append("--pdf")
    if args.consultar_denodo:
        report_cmd.append("--consultar-denodo")
    if not perform("relatorio_gerencial_v2", lambda: _run(report_cmd)):
        manifest["status_global"] = "falha"
        return manifest

    def security() -> dict:
        from ocde.relatorios.privacidade import scan_file
        output_dir = PROJECT_ROOT / "artefatos_local" / "ocde" / "relatorios_v2" / window.mes_execucao
        findings = {
            path.name: scan_file(path)
            for path in output_dir.glob("*") if path.is_file() and path.suffix.lower() in {".md", ".csv", ".json"}
        } if output_dir.exists() else {}
        findings = {name: values for name, values in findings.items() if values}
        return {"status": "falha" if findings else "sucesso", "achados": findings}
    if not perform("auditar_seguranca", security):
        manifest["status_global"] = "falha"
        return manifest
    manifest["status_global"] = "sucesso"
    manifest["data_hora_conclusao"] = datetime.now(ZoneInfo(ANALYSIS_TIMEZONE)).isoformat(timespec="seconds")
    final_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def main(argv: list[str] | None = None) -> int:
    manifest = run(argv)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 1 if manifest["status_global"] == "falha" else 0


if __name__ == "__main__":
    raise SystemExit(main())
