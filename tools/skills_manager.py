"""Auditoria, instalação idempotente e certificação das skills do projeto."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / ".agents" / "skills"
MANIFEST = ROOT / ".agents" / "skills-manifest.json"
CLAUDE = ROOT / ".claude" / "skills"
CODEX_LEGACY = ROOT / ".codex" / "skills"
CHECKPOINT = ROOT / ".agents" / "certification" / "functional-checkpoint.json"
NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER = re.compile(r"^---\s*\n(?P<body>.*?)\n---\s*\n", re.S)
CLIENT_COMMANDS = {
    "codex": ("codex.exe", "codex"),
    "claude-code": ("claude.exe", "claude"),
    "antigravity": ("agy.exe", "agy", "antigravity.exe", "antigravity"),
}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    value.update(path.read_bytes())
    return value.hexdigest()


def metadata(path: Path) -> dict[str, str]:
    match = FRONTMATTER.match(path.read_text(encoding="utf-8"))
    if not match:
        return {}
    result: dict[str, str] = {}
    for line in match.group("body").splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip().strip('"\'')
    return result


def load_manifest(path: Path = MANIFEST) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def inventory(base: Path) -> dict[str, str]:
    return {
        path.parent.name: digest(path)
        for path in sorted(base.glob("*/SKILL.md"))
        if path.is_file()
    }


def validate_package(name: str, config: dict, canonical: Path = CANONICAL) -> list[str]:
    problems: list[str] = []
    skill = canonical / name / "SKILL.md"
    if not NAME.fullmatch(name):
        problems.append("nome não segue kebab-case")
    if not skill.is_file():
        return ["SKILL.md ausente"]
    front = metadata(skill)
    if front.get("name") != name:
        problems.append("frontmatter.name diverge do diretório")
    if len(front.get("description", "")) < 30:
        problems.append("description pouco discriminante")
    tests = canonical / name / "tests" / "prompts.json"
    if config.get("status") != "removed":
        if not tests.is_file():
            problems.append("tests/prompts.json ausente")
        else:
            cases = json.loads(tests.read_text(encoding="utf-8"))
            if len(cases.get("positive", [])) < 5 or len(cases.get("negative", [])) < 5:
                problems.append("são exigidos cinco prompts positivos e cinco negativos")
    text = skill.read_text(encoding="utf-8", errors="replace")
    if re.search(r"(?i)(password|senha)\s*[:=]\s*[^<$\s][^\s]{5,}", text):
        problems.append("possível credencial incorporada")
    if re.search(r"(?i)C:\\Users\\[^\\]+", text):
        problems.append("caminho pessoal incorporado")
    for reference in re.findall(r"\[[^]]+\]\(([^)]+)\)", text):
        if "://" in reference or reference.startswith("#"):
            continue
        target = (skill.parent / reference).resolve()
        if not target.exists() and not (ROOT / reference).exists():
            problems.append(f"referência ausente: {reference}")
    return sorted(set(problems))


def validate_all(manifest: dict | None = None) -> dict:
    catalog = manifest or load_manifest()
    findings = {
        name: validate_package(name, config)
        for name, config in catalog["skills"].items()
    }
    findings = {name: values for name, values in findings.items() if values}
    canonical_names = set(inventory(CANONICAL))
    declared = set(catalog["skills"])
    return {
        "status": "falha" if findings or canonical_names != declared else "sucesso",
        "achados": findings,
        "nao_declaradas": sorted(canonical_names - declared),
        "ausentes": sorted(declared - canonical_names),
    }


def _redact_path(value: str | None) -> str | None:
    if not value:
        return value
    return re.sub(r"(?i)C:\\Users\\[^\\]+", "%USERPROFILE%", value)


def _windows_to_local(value: str) -> str:
    if os.name == "nt" or not re.match(r"^[A-Za-z]:\\", value):
        return value
    return "/mnt/" + value[0].lower() + value[2:].replace("\\", "/")


def _where_windows(command: str) -> str | None:
    where = shutil.which("where.exe") or "/mnt/c/Windows/System32/where.exe"
    if not Path(where).exists() and not shutil.which(where):
        return None
    completed = subprocess.run([where, command], capture_output=True, text=True)
    if completed.returncode:
        return None
    return next((line.strip() for line in completed.stdout.splitlines() if line.strip()), None)


def _resolve_client(client: str, platform: str) -> str | None:
    windows_available = os.name == "nt" or Path("/mnt/c/Windows").exists()
    if platform == "windows" or (platform == "auto" and windows_available):
        for command in CLIENT_COMMANDS[client]:
            found = _where_windows(command)
            if found:
                return _windows_to_local(found)
    for command in CLIENT_COMMANDS[client]:
        found = shutil.which(command)
        if found:
            return found
    return None


def _tool_version(client: str, platform: str = "auto") -> dict:
    executable = _resolve_client(client, platform)
    if not executable:
        return {"disponivel": False, "versao": None, "executavel": None}
    completed = subprocess.run([executable, "--version"], capture_output=True, text=True)
    displayed = executable
    if executable.startswith("/mnt/"):
        displayed = executable[5].upper() + ":\\" + executable[7:].replace("/", "\\")
    return {
        "disponivel": completed.returncode == 0,
        "versao": (completed.stdout or completed.stderr).strip(),
        "executavel": _redact_path(displayed),
    }


def install(apply: bool = False) -> dict:
    plan: list[dict] = []
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = ROOT / ".agents" / "skill-backups" / stamp
    for name in sorted(inventory(CANONICAL)):
        source, target = CANONICAL / name, CLAUDE / name
        if target.is_symlink() and target.resolve() == source.resolve():
            continue
        plan.append({"action": "symlink", "source": str(source), "target": str(target)})
        if not apply:
            continue
        CLAUDE.mkdir(parents=True, exist_ok=True)
        if target.exists() or target.is_symlink():
            backup.mkdir(parents=True, exist_ok=True)
            shutil.move(str(target), str(backup / f"claude-{name}"))
        target.symlink_to(source, target_is_directory=True)
    if CODEX_LEGACY.exists():
        plan.append({"action": "archive", "source": str(CODEX_LEGACY), "target": str(backup / "codex-skills")})
        if apply:
            backup.mkdir(parents=True, exist_ok=True)
            shutil.move(str(CODEX_LEGACY), str(backup / "codex-skills"))
    return {"aplicado": apply, "backup": str(backup) if apply else None, "acoes": plan}


def _prompt_inventory() -> dict[str, dict]:
    return {
        name: json.loads((CANONICAL / name / "tests" / "prompts.json").read_text(encoding="utf-8"))
        for name in inventory(CANONICAL)
        if (CANONICAL / name / "tests" / "prompts.json").is_file()
    }


def _safe_environment() -> dict[str, str]:
    blocked = re.compile(r"(?i)(denodo|password|passwd|senha|cpf)")
    return {key: value for key, value in os.environ.items() if not blocked.search(key)}


def _probe_prompt(request: str) -> str:
    return (
        "Teste não destrutivo de roteamento de skills. Não execute ferramentas, não leia .env e "
        "não altere arquivos. Analise a solicitação e responda somente JSON no formato "
        '{"selected_skill":"nome-ou-none"}. Solicitação: ' + request
    )


def _command(client: str, executable: str, prompt: str) -> list[str]:
    if client == "codex":
        return [executable, "exec", "--json", "--sandbox", "read-only", "--ephemeral", "-C", str(ROOT), prompt]
    if client == "claude-code":
        return [executable, "-p", "--output-format", "json", "--permission-mode", "plan", "--tools", "", "--no-session-persistence", prompt]
    return [executable, "-p", "--output-format", "json", "--mode", "plan", "--sandbox", "--print-timeout", "5m", prompt]


def _selection(output: str) -> str | None:
    matches = re.findall(r'\\?"selected_skill\\?"\s*:\s*\\?"([^"\\]+)', output)
    return matches[-1].strip().lower() if matches else None


def run_prompt_suite(
    platform: str,
    clients: tuple[str, ...],
    *,
    checkpoint: Path = CHECKPOINT,
    resume: bool = False,
) -> dict[str, Any]:
    suites = _prompt_inventory()
    completed: dict[str, dict] = {}
    if resume and checkpoint.is_file():
        completed = json.loads(checkpoint.read_text(encoding="utf-8")).get("casos", {})
    failures: list[dict[str, str]] = []
    total = sum(len(v.get("positive", [])) + len(v.get("negative", [])) for v in suites.values()) * len(clients)
    for client in clients:
        executable = _resolve_client(client, platform)
        if not executable:
            failures.append({"cliente": client, "caso": "discovery", "motivo": "executável ausente"})
            continue
        for skill, groups in suites.items():
            for kind in ("positive", "negative"):
                for index, request in enumerate(groups.get(kind, []), start=1):
                    case_id = f"{client}:{skill}:{kind}:{index}"
                    if case_id in completed and completed[case_id].get("status") == "sucesso":
                        continue
                    try:
                        process = subprocess.run(
                            _command(client, executable, _probe_prompt(str(request))),
                            cwd=ROOT, capture_output=True, text=True, timeout=360,
                            env=_safe_environment(), encoding="utf-8", errors="replace",
                        )
                        selected = _selection((process.stdout or "") + (process.stderr or ""))
                        expected = skill if kind == "positive" else "none"
                        passed = process.returncode == 0 and selected == expected
                        completed[case_id] = {
                            "status": "sucesso" if passed else "falha",
                            "selecionada": selected,
                            "esperada": expected,
                            "returncode": process.returncode,
                        }
                    except subprocess.TimeoutExpired:
                        completed[case_id] = {"status": "falha", "motivo": "timeout"}
                    if completed[case_id]["status"] != "sucesso":
                        failures.append({"cliente": client, "caso": case_id, "motivo": str(completed[case_id])})
                    checkpoint.parent.mkdir(parents=True, exist_ok=True)
                    checkpoint.write_text(json.dumps({"casos": completed}, ensure_ascii=False, indent=2), encoding="utf-8")
    passed = sum(item.get("status") == "sucesso" for item in completed.values())
    return {
        "executado": True, "casos_planejados": total, "casos_concluidos": len(completed),
        "casos_aprovados": passed, "falhas": failures,
        "status": "sucesso" if passed == total and not failures else "falha",
        "checkpoint": str(checkpoint.relative_to(ROOT)),
    }


def certify(
    platform: str = "auto",
    mode: str = "smoke",
    clients: tuple[str, ...] | None = None,
    execute_prompts: bool = False,
    resume: bool = False,
    allow_denodo_smoke: bool = False,
) -> dict:
    validation = validate_all()
    selected = clients or tuple(CLIENT_COMMANDS)
    tools = {name: _tool_version(name, platform) for name in selected}
    discovery = {
        "codex": inventory(CANONICAL),
        "antigravity": inventory(CANONICAL),
        "claude-code": inventory(CLAUDE),
    }
    expected = inventory(CANONICAL)
    equivalent = all(discovery[name] == expected for name in selected)
    clients_available = all(item["disponivel"] for item in tools.values())
    planned = sum(
        len(cases.get("positive", [])) + len(cases.get("negative", []))
        for cases in _prompt_inventory().values()
    ) * len(selected)
    if mode == "full" and execute_prompts:
        functional = run_prompt_suite(platform, selected, resume=resume)
    else:
        functional = {
            "solicitado": mode == "full", "executado": False,
            "casos_planejados": planned,
            "status": "pendente" if mode == "full" else "nao_aplicavel",
            "orientacao": "Use --execute-prompts após aprovar custo e duração.",
        }
    functional_ok = mode == "full" and functional["status"] == "sucesso"
    certified = validation["status"] == "sucesso" and equivalent and clients_available and functional_ok
    status = "certificado" if certified else "validado_estruturalmente" if (
        mode != "full" and validation["status"] == "sucesso" and equivalent and clients_available
    ) else "pendente"
    return {
        "status": status, "plataforma": platform, "modo": mode,
        "validacao_pacotes": validation, "clientes": tools,
        "descoberta_unica_equivalente": equivalent,
        "testes_funcionais": functional,
        "denodo_smoke": "autorizado" if allow_denodo_smoke else "nao_solicitado",
        "hashes": expected,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("inventory", "validate", "install", "certify"))
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--platform", choices=("auto", "windows", "wsl", "linux"), default="auto")
    parser.add_argument("--mode", choices=("structural", "smoke", "full"), default="smoke")
    parser.add_argument("--clients", default="codex,claude-code,antigravity")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--allow-denodo-smoke", action="store_true")
    parser.add_argument("--execute-prompts", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    if args.command == "inventory":
        result = {"agents": inventory(CANONICAL), "claude": inventory(CLAUDE), "codex_legacy": inventory(CODEX_LEGACY)}
    elif args.command == "validate":
        result = validate_all()
    elif args.command == "install":
        result = install(args.apply)
    else:
        requested = tuple(item.strip() for item in args.clients.split(",") if item.strip())
        unknown = sorted(set(requested) - set(CLIENT_COMMANDS))
        if unknown:
            parser.error(f"clientes desconhecidos: {unknown}")
        result = certify(
            args.platform, args.mode, requested, args.execute_prompts,
            args.resume, args.allow_denodo_smoke,
        )
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered)
    if args.command == "certify":
        return 0 if result.get("status") == "certificado" else 1
    return 1 if result.get("status") == "falha" else 0


if __name__ == "__main__":
    raise SystemExit(main())
