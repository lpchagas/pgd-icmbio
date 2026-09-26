"""Executa uma capacidade nas três unidades piloto, com resultado separado por piloto.

Plano de reorganização §7.3 (L5). Resolve ``config/unidades-piloto.json`` e chama o
adaptador do runner oficial com as flags que ele aceita de fato:

- I01–I12: ``lib.indicator_extraction --so IXX`` + seletor do piloto;
- G01/G02: ``gestao.runner --analise <registro>`` + seletor do piloto.

**Sem total agregado dos três:** somar taxas exigiria recompor numeradores e
denominadores, e pessoas e planos podem aparecer em mais de um recorte.

Cada resultado informa o escopo de aquisição (o que o runner consulta) e o de
entrega (o produto por piloto); o filtro posterior nunca é chamado de "consulta
restrita". O modo ``real`` é recusado enquanto o cadastro não estiver conferido na
fonte (início do L7), e a aquisição única reaproveitada nas três execuções (H8-a)
é implementada no L7.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from lib import liberacao
from lib.auditoria import minimal_subprocess_env, redact_log
from lib.caminhos import PROJECT_ROOT
from lib.periodos import ANALYSIS_TIMEZONE, configure_execution_context
from lib.validation_contracts import TARGETS, normalize_target

SAIDA = PROJECT_ROOT / "artefatos_local" / "validacao" / "pilotos" / "execucoes"


def _chave_gestao(codigo: str) -> str:
    from gestao.registry import REGISTRY

    for chave, extracao in REGISTRY.items():
        if extracao.code == codigo:
            return chave
    raise ValueError(f"Capacidade de gestão sem registro: {codigo}")


def comando(capacidade: str, piloto: liberacao.Piloto, data_execucao: str, produto: str, real: bool) -> tuple[list[str], str]:
    """Linha de comando do runner oficial e o escopo de aquisição declarado."""

    alvo = TARGETS[capacidade]
    if alvo.family == "ocde":
        linha = [sys.executable, "-m", "lib.indicator_extraction", "--data-execucao", data_execucao,
                 "--so", capacidade, *piloto.seletor_cli()]
        linha += ["--salvar-manifesto"] if real else ["--dry-run"]
        return linha, "nacional (o A1 OCDE consulta o universo nacional; o recorte do piloto é filtro posterior)"
    linha = [sys.executable, "-m", "gestao.runner", "--analise", _chave_gestao(capacidade),
             "--data-execucao", data_execucao, "--produto", produto, *piloto.seletor_cli()]
    if not real:
        linha.append("--dry-run")
    return linha, "definido pelo A1 de gestão, que recebe as siglas do escopo resolvido"


def _executar(linha: list[str]) -> dict[str, Any]:
    concluido = subprocess.run(linha, cwd=PROJECT_ROOT, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", env=minimal_subprocess_env())
    try:
        manifesto = json.loads(concluido.stdout)
    except json.JSONDecodeError:
        manifesto = {}
    return {
        "returncode": concluido.returncode,
        "status": manifesto.get("status_global", "erro" if concluido.returncode else "sem_manifesto"),
        "liberacao": manifesto.get("liberacao"),
        "manifesto": Path(manifesto["manifesto"]).name if manifesto.get("manifesto") else "",
        "erro": redact_log(concluido.stderr[-1000:]) if concluido.returncode else "",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--capacidade", required=True, help="I01–I12, G01 ou G02.")
    parser.add_argument("--data-execucao", required=True, help="AAAA-MM-DD")
    parser.add_argument("--produto", choices=("restrito", "compartilhavel"), default="restrito")
    parser.add_argument("--modo", choices=("dry-run", "real"), default="dry-run")
    parser.add_argument("--piloto", action="append", help="Restringe a pilotos do cadastro (repetível).")
    parser.add_argument("--salvar", action="store_true", help="Grava o registro no acervo privado.")
    return parser


def run(argv: list[str] | None = None) -> dict[str, Any]:
    args = build_parser().parse_args(argv)
    capacidade = normalize_target(args.capacidade)
    if capacidade not in TARGETS:
        raise ValueError(f"Capacidade sem runner de piloto: {args.capacidade}")
    window = configure_execution_context(args.data_execucao)  # regra temporal do projeto
    cadastro = liberacao.carregar_cadastro()
    pedidos = {sigla.strip().upper() for sigla in args.piloto or []}
    pilotos = [p for p in cadastro.pilotos if not pedidos or p.sigla in pedidos]
    if pedidos - {p.sigla for p in pilotos}:
        raise ValueError("Piloto fora do cadastro: " + ", ".join(sorted(pedidos - {p.sigla for p in pilotos})))
    real = args.modo == "real"
    if real and not all(p.conferido for p in pilotos):
        raise ValueError("Execução real recusada: id_petrvs dos pilotos ainda não conferido na fonte (L7).")

    resultados = []
    for piloto in pilotos:
        linha, aquisicao = comando(capacidade, piloto, window.data_execucao.isoformat(), args.produto, real)
        resultados.append({
            "piloto": piloto.sigla,
            "escopo_aquisicao": aquisicao,
            "escopo_entrega": f"{piloto.seletor}-{piloto.sigla.lower()}",
            "comando": [parte for parte in linha[1:]],
            **_executar(linha),
        })
    registro = {
        "tipo": "execucao_pilotos",
        "capacidade": capacidade,
        **window.as_dict(),
        "modo": args.modo,
        "produto": args.produto,
        "politica": cadastro.politica,
        "cadastro_versao": cadastro.versao,
        "gerado_em": datetime.now(ZoneInfo(ANALYSIS_TIMEZONE)).isoformat(timespec="seconds"),
        "resultados_por_piloto": resultados,
        "total_agregado": None,
        "status_global": "falha" if any(r["returncode"] for r in resultados) else args.modo if not real else "sucesso",
    }
    if args.salvar:
        SAIDA.mkdir(parents=True, exist_ok=True)
        destino = SAIDA / f"{window.data_execucao.isoformat()}_{capacidade}_{args.modo}_{args.produto}.json"
        destino.write_text(json.dumps(registro, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        registro["arquivo"] = destino.name
    return registro


def main(argv: list[str] | None = None) -> int:
    try:
        registro = run(argv)
    except ValueError as exc:
        print(f"Recusado: {exc}")
        return 1
    print(json.dumps(registro, ensure_ascii=False, indent=2))
    return 1 if registro["status_global"] == "falha" else 0


if __name__ == "__main__":
    raise SystemExit(main())
