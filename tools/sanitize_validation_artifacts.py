"""Sanitiza identificadores pessoais em artefatos A3–A5 já persistidos."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from ocde.relatorios.privacidade import redact_personal_identifiers, scan_file


def sanitize(directory: Path) -> dict:
    changed: list[str] = []
    remaining: dict[str, list[str]] = {}
    patterns = ("manifesto_validacao_*.json", "*.3_*", "*.4_*", "*.5_*")
    files = sorted({path for pattern in patterns for path in directory.glob(pattern) if path.is_file()})
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        sanitized = redact_personal_identifiers(text)
        if sanitized != text:
            path.write_text(sanitized, encoding="utf-8")
            changed.append(path.name)
        findings = scan_file(path)
        if findings:
            remaining[path.name] = findings
    return {
        "diretorio": str(directory),
        "arquivos_verificados": len(files),
        "arquivos_sanitizados": changed,
        "achados_restantes": remaining,
        "status": "falha" if remaining else "sucesso",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("diretorio", type=Path)
    args = parser.parse_args(argv)
    result = sanitize(args.diretorio)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "sucesso" else 1


if __name__ == "__main__":
    raise SystemExit(main())
