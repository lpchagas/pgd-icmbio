"""Runner unificado do protocolo automatizado A1--A5."""
from __future__ import annotations

import argparse
import ast
from collections import Counter
import csv
import hashlib
import json
import math
import os
import re
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from .csv_utils import PROJECT_ROOT
from .periodos import ANALYSIS_TIMEZONE, AnalysisWindow, configure_execution_context
from .validation_contracts import (
    OutputContract,
    ValidationTarget,
    selected_targets,
    target_artifact_prefix,
    validate_registry,
)
from .validation_extractors import SQL as ATOMIC_SQL, extract_atomic
from .validation_diagnostics import diagnose_atomic
from .validation_drift import assess_drift
from .validation_oracles import (
    calculate, independent_analysis_window, invariant_findings, verificar_supressao_compartilhavel,
)


VALIDATION_OUTPUT_BASE_ENV = "PGD_VALIDATION_OUTPUT_BASE"
FIXTURE_DIR = PROJECT_ROOT / "tests" / "fixtures" / "validation"
PERSONAL_COLUMN = re.compile(r"(?i)(cpf|email|telefone|endereco|nome_servidor|servidor_nome)")
PROFILE_CATEGORY = re.compile(r"(?i)(status|modalidade|grupo|faixa|categoria|classificacao|direcao|alerta|tipo_meta)")
UUID_VALUE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)
STAGE_ORDER = {"A1": 1, "A2": 2, "A3": 3, "A4": 4, "A5": 5, "todas": 5}
# Marcador de célula ocultada por k-anonimato nos painéis compartilháveis de gestão.
SUPPRESSED_CELL = "SUPRIMIDO_K"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sql_hash(path: Path) -> str:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    values = [
        node.value for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
        and "SELECT" in node.value.upper()
    ]
    return hashlib.sha256("\n".join(values).encode("utf-8")).hexdigest()


def _json_hash(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _run_id(window: AnalysisWindow, targets: list[ValidationTarget]) -> str:
    stamp = datetime.now(ZoneInfo(ANALYSIS_TIMEZONE)).strftime("%Y%m%dT%H%M%S")
    fingerprint = _json_hash({"window": window.as_dict(), "targets": [t.code for t in targets]})[:8]
    return f"{stamp}-{fingerprint}"


def _output_base(window: AnalysisWindow, scope_key: str) -> Path:
    override = os.environ.get(VALIDATION_OUTPUT_BASE_ENV)
    return (Path(override) if override else PROJECT_ROOT / "artefatos_local" / "validacao") / window.mes_execucao / "escopos" / scope_key


def _definition_hash(path: Path, names: set[str]) -> str:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    chunks = [ast.get_source_segment(source, node) or "" for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names]
    return hashlib.sha256("\n".join(chunks).encode("utf-8")).hexdigest()


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], list[str]]:
    problems: list[str] = []
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="|")
        header = reader.fieldnames or []
        rows = list(reader)
    if not header:
        problems.append("CSV vazio ou sem cabeçalho")
    if any(None in row for row in rows):
        problems.append("há linhas com largura divergente")
    return header, rows, problems


def _latest(pattern: str, directory: Path) -> Path | None:
    files = sorted(directory.glob(pattern), key=lambda path: (path.stat().st_mtime_ns, path.name))
    return files[-1] if files else None


def _a2_pattern(target: ValidationTarget, contract: OutputContract, product: str) -> str:
    """Padrão do A2 a validar, restrito ao produto na família de gestão.

    Os CSVs de gestão levam o produto no nome (``IND_GEST_01.2_painel_restrito_…``).
    Sem esse filtro, o arquivo mais recente vencia: validar ``restrito`` logo
    depois de gerar o ``compartilhavel`` comparava o oracle com células
    suprimidas. ``ambos`` compara com o restrito, que traz os valores.
    """
    if target.family != "gestao" or not contract.pattern.endswith("_*.csv"):
        return contract.pattern
    file_product = "compartilhavel" if product == "compartilhavel" else "restrito"
    return f"{contract.pattern[:-len('*.csv')]}{file_product}_*.csv"


def _contract_check(
    target: ValidationTarget,
    contract: OutputContract,
    path: Path | None,
    window: AnalysisWindow,
    units: set[str] | None = None,
    product: str = "restrito",
) -> tuple[list[dict[str, Any]], list[dict[str, str]], dict[str, Any]]:
    findings: list[dict[str, str]] = []
    if path is None:
        return [], [{"classe": "FALHA_TECNICA", "mensagem": f"A2 ausente: {contract.pattern}"}], {}
    header, rows, csv_problems = _read_csv(path)
    source_has_rows = bool(rows)
    if units is not None and "unidade_sigla" in header:
        rows = [row for row in rows if str(row.get("unidade_sigla", "")).upper() in units]
    findings.extend({"classe": "FALHA_TECNICA", "mensagem": value} for value in csv_problems)
    missing = sorted(set(contract.required_columns) - set(header))
    if missing:
        findings.append({"classe": "MUDANCA_DE_SCHEMA", "mensagem": f"colunas ausentes: {missing}"})
    if not source_has_rows and not contract.allow_empty and units is None:
        findings.append({"classe": "ANOMALIA_DE_DADOS", "mensagem": "A2 sem linhas"})
    seen: set[tuple[str, ...]] = set()
    for row in rows:
        key = tuple(row.get(column, "") for column in contract.business_keys)
        if key in seen:
            findings.append({"classe": "BUG_PROVAVEL", "mensagem": "chave A2 duplicada detectada"})
            break
        seen.add(key)
        for column in ("periodo_inicio", "periodo_fim_efetivo"):
            value = row.get(column)
            upper = window.data_execucao.isoformat() if target.code == "G02" and str(row.get("periodo", "")).startswith("FOTOGRAFIA-") else window.fim.isoformat()
            if value and (value < window.inicio.isoformat() or value > upper):
                findings.append({"classe": "ANOMALIA_DE_DADOS", "mensagem": f"{column} fora da janela: {value}"})
                break
    personal = sorted(column for column in header if PERSONAL_COLUMN.search(column))
    if personal and product == "compartilhavel":
        findings.append({"classe": "ANOMALIA_DE_DADOS", "mensagem": f"colunas pessoais: {personal}"})
    closed_period_counts = Counter(
        str(row.get("periodo"))
        for row in rows
        if row.get("periodo")
        and str(row.get("periodo_status", "")).lower() != "parcial_no_corte"
    )
    distributions: dict[str, dict[str, int]] = {}
    for column in header:
        if not PROFILE_CATEGORY.search(column):
            continue
        counts = Counter(
            "N.I." if UUID_VALUE.fullmatch(str(row.get(column) or ""))
            else str(row.get(column) or "N.I.")
            for row in rows
        )
        if len(counts) <= 50:
            distributions[column] = dict(sorted(counts.items()))
    profile = {
        "arquivo": path.name,
        "visao": contract.view,
        "sha256": _sha256(path),
        "linhas": len(rows),
        "volumetria_periodos_fechados": dict(sorted(closed_period_counts.items())),
        "distribuicoes": distributions,
        "colunas": header,
        "nulos": {
            column: round(100 * sum(not row.get(column) for row in rows) / len(rows), 2) if rows else 0.0
            for column in header
        },
    }
    return rows, findings, profile


def _number(value: Any) -> float | None:
    try:
        number = float(str(value).replace(",", "."))
        return number if math.isfinite(number) else None
    except (TypeError, ValueError):
        return None


def _tolerance(metric: str, target: ValidationTarget) -> float:
    if any(token in metric for token in ("perc", "proporcao", "taxa")):
        return target.tolerances.percentages
    if "hora" in metric:
        return target.tolerances.hours
    if any(token in metric for token in ("media", "score", "diferenca")):
        return target.tolerances.scores
    return target.tolerances.counts


def _compare(
    target: ValidationTarget,
    contract: OutputContract,
    production: list[dict[str, Any]],
    oracle: list[dict[str, Any]],
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    expected_rows = oracle if contract.view == "entregas" else [row for row in oracle if row.get("visao", contract.view) == contract.view]
    actual = {tuple(str(row.get(key, "")) for key in contract.business_keys): row for row in production}
    expected = {tuple(str(row.get(key, "")) for key in contract.business_keys): row for row in expected_rows}
    if set(actual) != set(expected):
        findings.append({
            "classe": "BUG_PROVAVEL",
            "mensagem": f"chaves A1/A3 divergentes: somente_A1={len(set(actual)-set(expected))}; somente_A3={len(set(expected)-set(actual))}",
        })
    numeric_differences: dict[str, list[float]] = {}
    incompatible: dict[str, int] = {}
    for key in set(actual) & set(expected):
        for metric in contract.metrics:
            if str(actual[key].get(metric, "")) == SUPPRESSED_CELL:
                # Célula ocultada por controle de divulgação: não há valor a comparar.
                continue
            left, right = _number(actual[key].get(metric)), _number(expected[key].get(metric))
            if left is None or right is None:
                if str(actual[key].get(metric, "")) != str(expected[key].get(metric, "")):
                    incompatible[metric] = incompatible.get(metric, 0) + 1
                continue
            difference = abs(left - right)
            if difference > _tolerance(metric, target):
                numeric_differences.setdefault(metric, []).append(difference)
    for metric, count in sorted(incompatible.items()):
        findings.append({
            "classe": "BUG_PROVAVEL",
            "mensagem": f"{metric}: valores incompatíveis em {count} chave(s)",
        })
    for metric, differences in sorted(numeric_differences.items()):
        findings.append({
            "classe": "BUG_PROVAVEL",
            "mensagem": f"{metric}: {len(differences)} divergência(s); diferença absoluta máxima={max(differences):.6f}",
        })
    return findings


def _load_fixture(code: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if code == "G02":
        atomic = json.loads((FIXTURE_DIR / "g02_atomic.json").read_text(encoding="utf-8"))
        expected = json.loads((FIXTURE_DIR / "g02_expected.json").read_text(encoding="utf-8"))
        return atomic, expected
    atomic = json.loads((FIXTURE_DIR / "atomic.json").read_text(encoding="utf-8"))[code]
    expected = json.loads((FIXTURE_DIR / "expected.json").read_text(encoding="utf-8"))[code]
    return atomic, expected


def _scope_units(args: argparse.Namespace) -> tuple[str, set[str] | None, str]:
    """Resolução única de escopo (L5): mesmas regras e chave da extração OCDE e do gestao.runner."""

    from relatorios.escopo import resolver_para_runner

    label, units, key = resolver_para_runner(
        escopo=args.escopo, regional=args.regional, unidade=args.unidade,
        mesogrupo=args.mesogrupo, tipo_unidade=args.tipo_unidade, lista_unidades=args.lista_unidades,
    )
    return label, (set(units) if units is not None else None), key


def _filter_atomic(records: list[dict[str, Any]], units: set[str] | None, target_code: str = "") -> list[dict[str, Any]]:
    if units is None:
        return records
    if target_code == "I08":
        return [
            row for row in records
            if (
                str(row.get("unidade_dona_sigla", "")).upper() in units
                or str(row.get("unidade_executora_sigla", "")).upper() in units
                or str(row.get("unidade_sigla", "")).upper() in units
            )
        ]
    if target_code == "G02":
        allowed_plans = {
            str(row.get("plano_trabalho_id")) for row in records
            if row.get("_extractor") == "g02_planos"
            and str(row.get("unidade_executora_sigla", "")).upper() in units
        }
        owner_deliveries = {
            str(row.get("id_entrega")) for row in records
            if row.get("_extractor") == "g02_entregas"
            and str(row.get("unidade_dona_sigla", "")).upper() in units
        }
        linked_deliveries = {
            str(row.get("id_entrega")) for row in records
            if row.get("_extractor") == "g02_vinculos"
            and str(row.get("plano_trabalho_id")) in allowed_plans
        }
        allowed_deliveries = owner_deliveries | linked_deliveries
        owner_plans = {
            str(row.get("plano_trabalho_id")) for row in records
            if row.get("_extractor") == "g02_vinculos"
            and str(row.get("id_entrega")) in owner_deliveries
        }
        allowed_plans |= owner_plans
        result = []
        for row in records:
            source = row.get("_extractor")
            keep = (
                source in {"g02_entregas", "g02_progressos"} and str(row.get("id_entrega")) in allowed_deliveries
            ) or (
                source in {"g02_planos", "g02_atividades"} and str(row.get("plano_trabalho_id")) in allowed_plans
            ) or (
                source == "g02_vinculos" and (str(row.get("plano_trabalho_id")) in allowed_plans or str(row.get("id_entrega")) in allowed_deliveries)
            )
            if keep:
                result.append(row)
        return result
    allowed_plans = {
        str(row.get("plano_trabalho_id")) for row in records
        if "unidade_sigla" in row
        and str(row.get("unidade_sigla", "")).upper() in units
        and row.get("plano_trabalho_id")
    }
    return [
        row for row in records
        if (
            ("unidade_sigla" in row and str(row.get("unidade_sigla", "")).upper() in units)
            or ("unidade_sigla" not in row and row.get("plano_trabalho_id") and str(row["plano_trabalho_id"]) in allowed_plans)
            or ("unidade_sigla" not in row and not row.get("plano_trabalho_id"))
        )
    ]


def _has_blocking(findings: list[dict[str, Any]]) -> bool:
    return any(item.get("severidade", "bloqueante") == "bloqueante" for item in findings)


def _markdown(title: str, payload: dict[str, Any]) -> str:
    lines = [f"# {title}", "", f"**Run:** `{payload['run_id']}`", f"**Status:** `{payload['status']}`", ""]
    lines.extend(["## Janela", "", f"{payload['periodo_analise_inicio']} a {payload['periodo_analise_fim']}", ""])
    lines.extend(["## Evidências", ""])
    for finding in payload.get("achados", []):
        severity = finding.get("severidade", "bloqueante")
        lines.append(f"- **{finding['classe']}** [{severity}] — {finding['mensagem']}")
    if not payload.get("achados"):
        lines.append("- Nenhuma divergência encontrada.")
    lines.extend(["", "## Rastreabilidade", "", f"- Oracle: `{payload.get('oracle_hash', '')}`", f"- Snapshot: `{payload.get('snapshot_hash', '')}`", ""])
    return "\n".join(lines)


def _baseline_status(
    target: ValidationTarget, mode: str, passed: bool, hashes: dict[str, str], scope_key: str
) -> str:
    if not passed:
        return "FALHA_TECNICA"
    if mode == "fixture":
        # Fixture demonstra coerência técnica, mas nunca constitui homologação.
        return "HOMOLOGACAO_INICIAL_PENDENTE"
    baseline_path = PROJECT_ROOT / "artefatos_local" / "validacao" / "baselines.json"
    if not baseline_path.exists():
        return "HOMOLOGACAO_INICIAL_PENDENTE"
    values = json.loads(baseline_path.read_text(encoding="utf-8"))
    baseline = values.get(target.code, {})
    if baseline.get("formula_version") != target.formula_version or baseline.get("status") != "HOMOLOGADO":
        return "HOMOLOGACAO_INICIAL_PENDENTE"
    stable = ("A1", "oracle", "production_sql", "extractors", "schema")
    if any(baseline.get("hashes", {}).get(key) != hashes.get(key) for key in stable):
        return "HOMOLOGACAO_INICIAL_PENDENTE"
    if scope_key not in baseline.get("profiles_by_scope", {}):
        return "HOMOLOGACAO_INICIAL_PENDENTE"
    return "CERTIFICADO_AUTOMATICAMENTE"


def _validate_target(
    target: ValidationTarget,
    mode: str,
    window: AnalysisWindow,
    run_id: str,
    output_dir: Path,
    *,
    stage: str = "todas",
    units: set[str] | None = None,
    product: str = "restrito",
    atomic_cache: dict[tuple[Any, ...], list[dict[str, Any]]] | None = None,
    scope_key: str = "nacional-nacional",
) -> dict[str, Any]:
    requested_stage = STAGE_ORDER[stage]
    findings: list[dict[str, str]] = []
    independent_start, independent_end = independent_analysis_window(window.data_execucao)
    if (independent_start, independent_end) != (window.inicio, window.fim):
        findings.append({
            "classe": "BUG_PROVAVEL",
            "mensagem": "janela da produção diverge do oracle temporal independente",
        })
    profiles: list[dict[str, Any]] = []
    production_by_view: dict[str, list[dict[str, Any]]] = {}
    if mode == "fixture":
        atomic, expected_fixture = _load_fixture(target.code)
    else:
        cache_key = (target.atomic_extractors, target.temporal_lenses, target.family, window.fim.isoformat())
        if atomic_cache is not None and cache_key in atomic_cache:
            extracted = atomic_cache[cache_key]
        else:
            extracted = extract_atomic(target, window, units)
            if atomic_cache is not None:
                atomic_cache[cache_key] = extracted
        atomic = _filter_atomic(extracted, units, target.code)
        expected_fixture = []
        a2_dir = PROJECT_ROOT / "artefatos_local" / ("ocde/entregas" if target.family == "ocde" else "gestao") / window.mes_execucao / "escopos" / scope_key
        contracts = [
            contract for contract in target.outputs
            if not (units is not None and target.code == "I01" and contract.view == "institucional")
        ]
        for contract in contracts:
            path = _latest(_a2_pattern(target, contract, product), a2_dir)
            rows, contract_findings, profile = _contract_check(
                target, contract, path, window, units, product
            )
            findings.extend(contract_findings)
            if profile:
                profiles.append(profile)
            production_by_view[contract.view] = rows

    if requested_stage >= STAGE_ORDER["A4"]:
        findings.extend(diagnose_atomic(target.code, atomic))

    if mode == "integrado" and requested_stage >= STAGE_ORDER["A2"]:
        baseline_path = PROJECT_ROOT / "artefatos_local" / "validacao" / "baselines.json"
        if baseline_path.is_file():
            baseline = json.loads(baseline_path.read_text(encoding="utf-8")).get(target.code, {})
            for profile in profiles:
                reference = baseline.get("profiles_by_scope", {}).get(scope_key, {}).get(profile["visao"])
                if reference:
                    findings.extend(assess_drift(profile, reference, target.drift_policy))

    if requested_stage < STAGE_ORDER["A3"]:
        # A1/A2 encerram aqui: a classificação precisa considerar apenas os
        # achados já coletados, sem depender do bloco A3 abaixo.
        return {
            "alvo": target.code,
            "etapa": stage,
            "status": "sucesso" if not _has_blocking(findings) else "falha",
            "achados": findings,
            "hash_A1": _sha256(target.production_entrypoint),
            "perfis_A2": profiles,
        }

    oracle = calculate(target.code, atomic)
    if units is not None and target.code in {"G02", "I08"}:
        oracle = [row for row in oracle if str(row.get("unidade_sigla", "")).upper() in units]
    active_contracts = [
        contract for contract in target.outputs
        if not (units is not None and target.code == "I01" and contract.view == "institucional")
    ]
    for contract in active_contracts:
        expected_for_view = (
            expected_fixture
            if contract.view == "entregas"
            else [row for row in expected_fixture if row.get("visao", contract.view) == contract.view]
        )
        if mode == "fixture":
            findings.extend(_compare(target, contract, expected_for_view, oracle))
        elif target.code == "G02" and product == "compartilhavel":
            # D27: o compartilhável é validado pelas propriedades da supressão e pelos
            # valores das células visíveis.
            producao = production_by_view.get(contract.view, [])
            esperado, achados_supressao = verificar_supressao_compartilhavel(
                producao, oracle, atomic, contract.business_keys
            )
            findings.extend(achados_supressao)
            findings.extend(_compare(target, contract, producao, esperado))
        else:
            findings.extend(_compare(target, contract, production_by_view.get(contract.view, []), oracle))
        oracle_view = oracle if contract.view == "entregas" else [row for row in oracle if row.get("visao", contract.view) == contract.view]
        findings.extend(invariant_findings(oracle_view, contract.business_keys))

    oracle_path = Path(__file__).with_name("validation_oracles.py")
    blocking = _has_blocking(findings)
    payload: dict[str, Any] = {
        "tipo": "A3_validacao_independente", "run_id": run_id, "alvo": target.code,
        "familia": target.family, "modo": mode, **window.as_dict(),
        "formula_version": target.formula_version, "oracle_hash": _definition_hash(oracle_path, {target.oracle_name}),
        "snapshot_hash": _json_hash(atomic), "registros_atomicos": len(atomic),
        "linhas_oracle": len(oracle), "perfis_A2": profiles, "achados": findings,
        "status": "sucesso" if not blocking else "falha",
    }
    prefix = target_artifact_prefix(target.code, target.family)
    output_dir.mkdir(parents=True, exist_ok=True)
    a3_json = output_dir / f"{prefix}.3_validacao_independente_{run_id}.json"
    a3_md = output_dir / f"{prefix}.3_validacao_independente_{run_id}.md"
    a3_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    a3_md.write_text(_markdown(f"A3 — Validação independente {target.code}", payload), encoding="utf-8")

    classes = sorted({item["classe"] for item in findings}) or ["SEM_DIVERGENCIA"]
    a4 = {
        "tipo": "A4_diagnostico_automatico", "run_id": run_id, "alvo": target.code,
        **window.as_dict(), "classificacoes": classes, "achados": findings,
        "status": "sucesso" if not blocking else "falha",
    }
    a4_json = output_dir / f"{prefix}.4_diagnostico_{run_id}.json"
    a4_md = output_dir / f"{prefix}.4_diagnostico_{run_id}.md"
    if requested_stage >= STAGE_ORDER["A4"]:
        a4_json.write_text(json.dumps(a4, ensure_ascii=False, indent=2), encoding="utf-8")
        a4_md.write_text(_markdown(f"A4 — Diagnóstico automático {target.code}", {**payload, **a4}), encoding="utf-8")
        if findings:
            detail = output_dir / f"{prefix}.4_q1_achados_{run_id}.csv"
            with detail.open("w", encoding="utf-8-sig", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=("classe", "severidade", "mensagem"), delimiter="|")
                writer.writeheader()
                writer.writerows(findings)

    validation_hashes = {
        "A1": _sha256(target.production_entrypoint),
        "oracle": payload["oracle_hash"],
        "production_sql": _sql_hash(target.production_entrypoint),
        "extractors": _json_hash({name: ATOMIC_SQL[name] for name in target.atomic_extractors}),
        "schema": _json_hash([asdict(contract) for contract in target.outputs]),
        "snapshot": payload["snapshot_hash"],
        "A2_profile": _json_hash(profiles),
    }
    decision = (
        "AGUARDANDO_DECISAO"
        if blocking and any(item["classe"] in {"DIVERGENCIA_SEMANTICA", "DECISAO_METODOLOGICA"} for item in findings)
        else _baseline_status(target, mode, not blocking, validation_hashes, scope_key)
    )
    a5 = {
        "tipo": "A5_relatorio_validacao", "run_id": run_id, "alvo": target.code,
        "nome": target.name, **window.as_dict(), "formula_version": target.formula_version,
        "modo": mode, "cobertura": {"atomicos": len(atomic), "oracle": len(oracle)},
        "comparacao": "A1 x oracle Python independente" if mode == "integrado" else "fixture x oracle",
        "diagnosticos": classes, "riscos": [item["mensagem"] for item in findings if item.get("severidade", "bloqueante") != "informativo"],
        "recomendacao": "Homologar o baseline inicial." if decision == "HOMOLOGACAO_INICIAL_PENDENTE" else "Acionar a CGOV." if decision == "AGUARDANDO_DECISAO" else "Manter recertificação automática." if not blocking else "Corrigir achados bloqueantes e revalidar.",
        "hashes": validation_hashes,
        "decisao": decision, "status": "sucesso" if decision in {"CERTIFICADO_AUTOMATICAMENTE", "HOMOLOGADO"} else "pendente" if decision == "HOMOLOGACAO_INICIAL_PENDENTE" else "falha",
        "artefatos": [a3_json.name, a3_md.name, a4_json.name, a4_md.name],
    }
    a5_md = output_dir / f"{prefix}.5_relatorio_validacao_{run_id}.md"
    if requested_stage >= STAGE_ORDER["A5"]:
        a5["artefatos"].append(a5_md.name)
        a5_md.write_text(_a5_markdown(target, {**payload, **a5}), encoding="utf-8")
    else:
        a5["etapa"] = stage
        a5["artefatos"] = [name for name in a5["artefatos"] if (output_dir / name).exists()]
    return a5


def _a5_markdown(target: ValidationTarget, payload: dict[str, Any]) -> str:
    coverage = payload.get("cobertura", {})
    lines = [
        f"# A5 — Relatório de validação {target.code}", "",
        f"**Objetivo:** {target.name}",
        "**Versão metodológica:** `{}`".format(payload["formula_version"]),
        "**Run:** `{}`".format(payload["run_id"]),
        "**Decisão:** `{}`".format(payload["decisao"]), "",
        "## Janela e escopo", "",
        "- Período: {} a {}".format(payload["periodo_analise_inicio"], payload["periodo_analise_fim"]),
        "- Modo: {}".format(payload["modo"]), "",
        "## Cobertura e comparação", "",
        "- Registros atômicos: {}".format(coverage.get("atomicos", 0)),
        "- Linhas do oracle: {}".format(coverage.get("oracle", 0)),
        "- Método: {}".format(payload.get("comparacao", "")), "",
        "## Diagnósticos e riscos", "",
    ]
    risks = payload.get("riscos", [])
    lines.extend([f"- {risk}" for risk in risks] or ["- Nenhum risco bloqueante identificado."])
    lines.extend(["", "## Recomendação técnica", "", "- {}".format(payload.get("recomendacao", "Consultar a decisão registrada.")), "", "## Rastreabilidade", ""])
    for name, value in payload.get("hashes", {}).items():
        lines.append(f"- {name}: `{value}`")
    lines.extend(["", "## Arquivos gerados", ""])
    lines.extend(f"- `{name}`" for name in payload.get("artefatos", []))
    return "\n".join(lines) + "\n"


def _request_fingerprint(
    args: argparse.Namespace,
    window: AnalysisWindow,
    targets: list[ValidationTarget],
    scope_label: str,
    scope_key: str,
) -> str:
    files: dict[str, str] = {}
    common = (
        Path(__file__), Path(__file__).with_name("validation_contracts.py"),
        Path(__file__).with_name("validation_oracles.py"),
        Path(__file__).with_name("validation_extractors.py"),
        Path(__file__).with_name("validation_diagnostics.py"),
    )
    for path in (*common, *(target.production_entrypoint for target in targets)):
        files[str(path.relative_to(PROJECT_ROOT))] = _sha256(path)
    if args.modo == "integrado":
        for target in targets:
            directory = PROJECT_ROOT / "artefatos_local" / (
                "ocde/entregas" if target.family == "ocde" else "gestao"
            ) / window.mes_execucao / "escopos" / scope_key
            for contract in target.outputs:
                path = _latest(_a2_pattern(target, contract, args.produto), directory)
                if path:
                    files[str(path.relative_to(PROJECT_ROOT))] = _sha256(path)
    return _json_hash({
        "window": window.as_dict(), "targets": [target.code for target in targets],
        "mode": args.modo, "product": args.produto, "stage": args.etapa,
        "scope": scope_label, "files": files,
    })


def _resumable_manifest(output_dir: Path, fingerprint: str) -> dict[str, Any] | None:
    for path in sorted(output_dir.glob("manifesto_validacao_*.json"), reverse=True):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if value.get("fingerprint") == fingerprint and value.get("status_global") == "sucesso":
            value["manifesto"] = str(path)
            value["reutilizado"] = True
            return value
    return None


def _consolidate_existing(
    args: argparse.Namespace,
    window: AnalysisWindow,
    targets: list[ValidationTarget],
    output_dir: Path,
    scope_label: str,
    scope_key: str,
    units: set[str] | None,
) -> dict[str, Any]:
    """Forma um manifesto único com o resultado mais recente de cada alvo.

    A consolidação não recalcula nem altera A3--A5; ela apenas encadeia resultados
    já produzidos para a mesma data, produto, modo e escopo. Isso permite que
    famílias com extratores diferentes sejam executadas em lotes e aprovadas de
    modo transacional por um único manifesto.
    """
    wanted = {target.code for target in targets}
    latest: dict[str, tuple[Path, dict[str, Any]]] = {}
    for path in sorted(output_dir.glob("manifesto_validacao_*.json")):
        try:
            manifest = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        scope = manifest.get("escopo", {})
        if (
            manifest.get("data_execucao") != window.data_execucao.isoformat()
            or manifest.get("modo") != args.modo
            or manifest.get("produto") != args.produto
            or not isinstance(scope, dict)
            or scope.get("chave") != scope_key
        ):
            continue
        for result in manifest.get("resultados", []):
            code = result.get("alvo")
            if code in wanted:
                latest[code] = (path, result)
    missing = sorted(wanted - set(latest))
    if missing:
        raise FileNotFoundError(
            "Não há resultado compatível para consolidar: " + ", ".join(missing)
        )
    results = [latest[target.code][1] for target in targets]
    sources = sorted({latest[target.code][0].name for target in targets})
    failure = any(result.get("status") == "falha" for result in results)
    pending = any(result.get("status") == "pendente" for result in results)
    run_id = _run_id(window, targets)
    fingerprint = _json_hash({"fontes": [(name, _sha256(output_dir / name)) for name in sources]})
    manifest = {
        "tipo": "protocolo_validacao_A1_A5_consolidado",
        "run_id": run_id,
        **window.as_dict(),
        "familia": args.familia,
        "modo": args.modo,
        "produto": args.produto,
        "etapa": args.etapa,
        "escopo": {"rotulo": scope_label, "chave": scope_key, "unidades": sorted(units or [])},
        "fingerprint": fingerprint,
        "status_global": "falha" if failure else "pendente" if pending else "sucesso",
        "manifestos_fonte": sources,
        "resultados": results,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"manifesto_validacao_{run_id}.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest["manifesto"] = str(path)
    return manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--familia", choices=("ocde", "gestao", "todas"), default="todas")
    parser.add_argument("--alvo", default="todos")
    parser.add_argument("--data-execucao", required=True)
    parser.add_argument("--etapa", choices=("A1", "A2", "A3", "A4", "A5", "todas"), default="todas")
    parser.add_argument("--modo", choices=("fixture", "integrado"), default="fixture")
    parser.add_argument("--produto", choices=("restrito", "compartilhavel", "ambos"), default="restrito")
    parser.add_argument("--retomar", action="store_true")
    parser.add_argument("--revalidar", action="store_true")
    parser.add_argument("--salvar", action="store_true")
    parser.add_argument("--consolidar-existentes", action="store_true")
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--escopo", choices=("nacional",))
    scope.add_argument("--regional")
    scope.add_argument("--unidade")
    scope.add_argument("--mesogrupo")
    scope.add_argument("--tipo-unidade")
    scope.add_argument("--lista-unidades", type=Path)
    return parser


def run(argv: list[str] | None = None) -> dict[str, Any]:
    args = build_parser().parse_args(argv)
    problems = validate_registry()
    if problems:
        raise RuntimeError("Registro de validação inválido: " + "; ".join(problems))
    window = configure_execution_context(args.data_execucao)
    targets = selected_targets(args.familia, args.alvo)
    if not targets:
        raise ValueError("Nenhum alvo selecionado.")
    scope_label, units, scope_key = _scope_units(args)
    output_dir = _output_base(window, scope_key)
    if args.consolidar_existentes:
        return _consolidate_existing(
            args, window, targets, output_dir, scope_label, scope_key, units
        )
    fingerprint = _request_fingerprint(args, window, targets, scope_label, scope_key)
    if args.retomar and not args.revalidar:
        reusable = _resumable_manifest(output_dir, fingerprint)
        if reusable:
            return reusable
    run_id = _run_id(window, targets)
    atomic_cache: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    results = [
        _validate_target(
            target, args.modo, window, run_id, output_dir,
            stage=args.etapa, units=units, product=args.produto, atomic_cache=atomic_cache,
            scope_key=scope_key,
        )
        for target in targets
    ]
    failure = any(result["status"] == "falha" for result in results)
    pending = any(result["status"] == "pendente" for result in results)
    manifest = {
        "tipo": "protocolo_validacao_A1_A5", "run_id": run_id, **window.as_dict(),
        "familia": args.familia, "modo": args.modo, "produto": args.produto,
        "etapa": args.etapa, "escopo": {"rotulo": scope_label, "chave": scope_key, "unidades": sorted(units or [])}, "fingerprint": fingerprint,
        "status_global": "falha" if failure else "pendente" if pending else "sucesso",
        "resultados": results,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"manifesto_validacao_{run_id}.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest["manifesto"] = str(path)
    return manifest


def main(argv: list[str] | None = None) -> int:
    manifest = run(argv)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0 if manifest["status_global"] == "sucesso" else 1


if __name__ == "__main__":
    raise SystemExit(main())
