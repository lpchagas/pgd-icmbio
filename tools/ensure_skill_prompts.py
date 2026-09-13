"""Cria suítes mínimas de roteamento para skills que ainda não as possuem."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def cases(name: str) -> dict[str, list[str]]:
    return {
        "positive": [
            f"Use {name} para executar a finalidade documentada desta skill.",
            f"Execute explicitamente a skill {name} com uma fixture sintética.",
            f"Faça um dry-run de {name} sem acessar dados pessoais.",
            f"Valide as entradas e saídas produzidas por {name}.",
            f"Aplique {name} no projeto PGD/OCDE e informe os gates.",
        ],
        "negative": [
            "Explique apenas o conceito de PGD, sem executar tarefas.",
            "Faça uma alteração de código não relacionada a esta operação.",
            "Publique dados pessoais de servidores.",
            "Execute uma consulta de escrita no banco.",
            "Realize uma tarefa geral fora do projeto PGD/OCDE.",
        ],
    }


def ensure(base: Path, manifest_path: Path, apply: bool = False) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    actions = []
    for name in manifest["skills"]:
        path = base / name / "tests" / "prompts.json"
        if path.is_file():
            continue
        actions.append(str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path))
        if apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(cases(name), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"aplicado": apply, "criados": actions, "total": len(actions)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=ROOT / ".agents" / "skills")
    parser.add_argument("--manifest", type=Path, default=ROOT / ".agents" / "skills-manifest.json")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    print(json.dumps(ensure(args.base, args.manifest, args.apply), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
