"""Auditoria de segredos sem revelar os valores pesquisados.

O valor sensível é lido do arquivo .env apenas em memória. O relatório contém
somente caminhos e quantidades; nunca o segredo, seu hash ou trechos vizinhos.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_KEYS = ("DENODO_USER", "DENODO_PASSWORD")
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".venv", "node_modules", "artefatos_local", "cgov", "setup"}
TEXT_SUFFIXES = {
    "", ".md", ".txt", ".py", ".json", ".toml", ".yaml", ".yml", ".ini",
    ".cfg", ".env", ".sql", ".csv", ".ipynb", ".ps1", ".sh",
}


def _dotenv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"\'')
    return values


def _files(root: Path):
    """Percorre arquivos locais sem seguir junctions/symlinks privados."""

    for directory, names, filenames in os.walk(root, topdown=True, followlinks=False):
        names[:] = [name for name in names if name not in SKIP_DIRS and not (Path(directory) / name).is_symlink()]
        for filename in filenames:
            path = Path(directory) / filename
            if path.is_symlink() or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            try:
                if path.stat().st_size <= 20 * 1024 * 1024:
                    yield path
            except OSError:
                continue


def scan_exact_secrets(
    root: Path = ROOT,
    env_path: Path | None = None,
    keys: tuple[str, ...] = DEFAULT_KEYS,
) -> dict:
    env_file = env_path or root / ".env"
    values = _dotenv(env_file)
    secrets = {key: values.get(key, "") for key in keys if values.get(key)}
    occurrences: list[dict[str, object]] = []
    for path in _files(root):
        if path.resolve() == env_file.resolve():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        matched = [key for key, secret in secrets.items() if secret and secret in text]
        if matched:
            occurrences.append({
                "arquivo": str(path.relative_to(root)),
                "variaveis": matched,
                "quantidade": sum(text.count(secrets[key]) for key in matched),
            })
    return {
        "tipo": "auditoria_segredo_exato",
        "credenciais_carregadas": sorted(secrets),
        "armazenamento_autorizado": str(env_file.relative_to(root)) if env_file.is_relative_to(root) else ".env externo",
        "ocorrencias_fora_do_armazenamento": occurrences,
        "status": "falha" if occurrences else "sucesso",
    }


def remediate_exact_secrets(
    root: Path = ROOT,
    env_path: Path | None = None,
    keys: tuple[str, ...] = DEFAULT_KEYS,
) -> dict:
    """Substitui somente ocorrências exatas fora do .env, sem copiar o segredo."""

    env_file = env_path or root / ".env"
    values = _dotenv(env_file)
    secrets = [values[key] for key in keys if values.get(key)]
    before = scan_exact_secrets(root, env_file, keys)
    changed: list[str] = []
    for occurrence in before["ocorrencias_fora_do_armazenamento"]:
        path = root / str(occurrence["arquivo"])
        content = path.read_text(encoding="utf-8", errors="replace")
        sanitized = content
        for secret in secrets:
            sanitized = sanitized.replace(secret, "<REMOVIDO: usar .env local>")
        if sanitized != content:
            path.write_text(sanitized, encoding="utf-8")
            changed.append(str(occurrence["arquivo"]))
    after = scan_exact_secrets(root, env_file, keys)
    after["arquivos_sanitizados"] = changed
    return after


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--env", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--remediate", action="store_true", help="Substitui ocorrências exatas por placeholder.")
    args = parser.parse_args(argv)
    scanner = remediate_exact_secrets if args.remediate else scan_exact_secrets
    result = scanner(args.root.resolve(), args.env.resolve() if args.env else None)
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered)
    return 0 if result["status"] == "sucesso" else 1


if __name__ == "__main__":
    raise SystemExit(main())
