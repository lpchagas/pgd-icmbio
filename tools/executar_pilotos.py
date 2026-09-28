"""Executa uma capacidade nas três unidades piloto, com resultado separado por piloto.

Plano de reorganização §7.3 (L5, L7). Resolve ``config/unidades-piloto.json`` e chama
o runner oficial com as flags que ele aceita de fato:

- I01–I12 (ou ``ocde`` para os doze): ``lib.indicator_extraction --pilotos``. É
  **uma única aquisição nacional** (H8-a), em staging temporário descartado, entregue
  filtrada para cada piloto — sem diferença temporal entre os três recortes;
- G01/G02: ``gestao.runner --analise <registro>`` por piloto (o A1 de gestão consulta
  só as siglas do escopo resolvido).

Com ``--validar`` (modo real), roda a validação integrada A1–A5 por piloto: os
manifestos que o registro de aceite exige.

**Sem total agregado dos três:** somar taxas exigiria recompor numeradores e
denominadores, e pessoas e planos podem aparecer em mais de um recorte.

Cada resultado informa o escopo de aquisição e o de entrega; o filtro posterior
nunca é chamado de "consulta restrita". O modo ``real`` é recusado quando o cadastro
não está conferido ou diverge da hierarquia atual do PETRVS.
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
AQUISICAO_OCDE = "nacional única (H8-a): os A1 OCDE consultam o universo nacional uma vez; o recorte de cada piloto é filtro posterior"
AQUISICAO_GESTAO = "definida pelo A1 de gestão, que consulta só as siglas do escopo resolvido do piloto"


def _chave_gestao(codigo: str) -> str:
    from gestao.registry import REGISTRY

    for chave, extracao in REGISTRY.items():
        if extracao.code == codigo:
            return chave
    raise ValueError(f"Capacidade de gestão sem registro: {codigo}")


def _capacidade(texto: str) -> tuple[str, str]:
    """(código, família); ``ocde`` seleciona os doze indicadores numa só aquisição."""

    if texto.strip().lower() == "ocde":
        return "OCDE", "ocde"
    codigo = normalize_target(texto)
    if codigo not in TARGETS:
        raise ValueError(f"Capacidade sem runner de piloto: {texto}")
    return codigo, TARGETS[codigo].family


def comando_ocde(capacidade: str, data_execucao: str, real: bool) -> list[str]:
    linha = [sys.executable, "-m", "lib.indicator_extraction", "--data-execucao", data_execucao, "--pilotos"]
    if capacidade != "OCDE":
        linha += ["--so", capacidade]
    return linha + (["--salvar-manifesto"] if real else ["--dry-run"])


def comando_gestao(capacidade: str, piloto: liberacao.Piloto, data_execucao: str, produto: str, real: bool) -> list[str]:
    linha = [sys.executable, "-m", "gestao.runner", "--analise", _chave_gestao(capacidade),
             "--data-execucao", data_execucao, "--produto", produto, *piloto.seletor_cli()]
    return linha if real else linha + ["--dry-run"]


def comando_validacao(capacidade: str, familia: str, piloto: liberacao.Piloto, data_execucao: str, produto: str) -> list[str]:
    return [sys.executable, "-m", "lib.validation_runner", "--familia", familia,
            "--alvo", "todos" if capacidade == "OCDE" else capacidade, "--modo", "integrado",
            "--data-execucao", data_execucao, "--produto", produto, *piloto.seletor_cli()]


def _rodar(linha: list[str]) -> tuple[int, dict[str, Any], str]:
    concluido = subprocess.run(linha, cwd=PROJECT_ROOT, capture_output=True, text=True,
                               encoding="utf-8", errors="replace",
                               env={**minimal_subprocess_env(), "PYTHONIOENCODING": "utf-8"})
    return concluido.returncode, ler_json_da_saida(concluido.stdout), redact_log(concluido.stderr[-1000:]) if concluido.returncode else ""


def ler_json_da_saida(texto: str) -> dict[str, Any]:
    """JSON final do runner; ignora linhas anteriores (ex.: 'JVM iniciada.' do adaptador Denodo)."""

    inicio = 0 if texto.startswith("{") else texto.find("\n{") + 1
    if inicio == 0 and not texto.startswith("{"):
        return {}
    try:
        return json.loads(texto[inicio:])
    except json.JSONDecodeError:
        return {}


def _resumo(codigo: int, manifesto: dict[str, Any], erro: str) -> dict[str, Any]:
    return {
        "returncode": codigo,
        "status": manifesto.get("status_global", "erro" if codigo else "sem_manifesto"),
        "liberacao": manifesto.get("liberacao"),
        "manifesto": Path(manifesto["manifesto"]).name if manifesto.get("manifesto") else "",
        "erro": erro,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--capacidade", required=True, help="I01–I12, ocde (os doze), G01 ou G02.")
    parser.add_argument("--data-execucao", required=True, help="AAAA-MM-DD")
    parser.add_argument("--produto", choices=("restrito", "compartilhavel"), default="restrito")
    parser.add_argument("--modo", choices=("dry-run", "real"), default="dry-run")
    parser.add_argument("--piloto", action="append", help="Restringe a pilotos do cadastro (só gestão; repetível).")
    parser.add_argument("--validar", action="store_true", help="Modo real: validação integrada A1–A5 por piloto.")
    parser.add_argument("--salvar", action="store_true", help="Grava o registro no acervo privado.")
    return parser


def run(argv: list[str] | None = None) -> dict[str, Any]:
    args = build_parser().parse_args(argv)
    capacidade, familia = _capacidade(args.capacidade)
    window = configure_execution_context(args.data_execucao)  # regra temporal do projeto
    data = window.data_execucao.isoformat()
    cadastro = liberacao.carregar_cadastro()
    pedidos = {sigla.strip().upper() for sigla in args.piloto or []}
    if pedidos and familia == "ocde":
        raise ValueError("A aquisição única entrega os três pilotos juntos: --piloto não se aplica às capacidades OCDE.")
    pilotos = [p for p in cadastro.pilotos if not pedidos or p.sigla in pedidos]
    if pedidos - {p.sigla for p in pilotos}:
        raise ValueError("Piloto fora do cadastro: " + ", ".join(sorted(pedidos - {p.sigla for p in pilotos})))
    real = args.modo == "real"
    if args.validar and not real:
        raise ValueError("--validar só se aplica ao modo real.")
    if real and not all(p.conferido for p in pilotos):
        raise ValueError("Execução real recusada: id_petrvs dos pilotos ainda não conferido na fonte (L7).")
    problemas = [m for m in liberacao.problemas_cadastro(cadastro) if m.split(":", 1)[0] in {p.sigla for p in pilotos}]
    if real and problemas:
        raise ValueError("Execução real recusada: " + "; ".join(problemas))

    resultados = []
    execucao_unica: dict[str, Any] | None = None
    if familia == "ocde":
        linha = comando_ocde(capacidade, data, real)
        codigo, saida, erro = _rodar(linha)
        por_chave = {m.get("escopo", {}).get("chave"): m for m in saida.get("manifestos_por_piloto", [])}
        execucao_unica = {"comando": linha[1:], "returncode": codigo, "run_id": saida.get("run_id", ""), "erro": erro}
        for piloto in pilotos:
            chave = f"{piloto.seletor}-{piloto.sigla.lower()}"
            manifesto = por_chave.get(chave, {})
            resultados.append({"piloto": piloto.sigla, "escopo_aquisicao": AQUISICAO_OCDE, "escopo_entrega": chave,
                               **_resumo(codigo if manifesto else codigo or 1, manifesto, erro)})
    else:
        for piloto in pilotos:
            linha = comando_gestao(capacidade, piloto, data, args.produto, real)
            resultados.append({"piloto": piloto.sigla, "escopo_aquisicao": AQUISICAO_GESTAO,
                               "escopo_entrega": f"{piloto.seletor}-{piloto.sigla.lower()}",
                               "comando": linha[1:], **_resumo(*_rodar(linha))})
    if args.validar:
        for resultado, piloto in zip(resultados, pilotos):
            if resultado["returncode"]:
                resultado["validacao"] = {"status": "nao_executada", "motivo": "extração do piloto falhou"}
                continue
            codigo, saida, erro = _rodar(comando_validacao(capacidade, familia, piloto, data, args.produto))
            resultado["validacao"] = {**_resumo(codigo, saida, erro),
                                      "alvos": {r.get("alvo"): r.get("status") for r in saida.get("resultados", [])}}

    validacoes = [r["validacao"].get("status") for r in resultados if "validacao" in r]
    # "pendente" = A1 e oracle coerentes, mas o escopo ainda não tem baseline homologada
    # (HOMOLOGACAO_INICIAL_PENDENTE): é o aceite humano do piloto, não falha técnica.
    falhou = any(r["returncode"] for r in resultados) or any(s not in ("sucesso", "pendente") for s in validacoes)
    registro = {
        "tipo": "execucao_pilotos",
        "capacidade": capacidade,
        **window.as_dict(),
        "modo": args.modo,
        "produto": args.produto,
        "politica": cadastro.politica,
        "cadastro_versao": cadastro.versao,
        "gerado_em": datetime.now(ZoneInfo(ANALYSIS_TIMEZONE)).isoformat(timespec="seconds"),
        "aquisicao_unica": execucao_unica,
        "resultados_por_piloto": resultados,
        "total_agregado": None,
        "status_global": (
            "falha" if falhou else args.modo if not real
            else "aguardando_homologacao" if "pendente" in validacoes else "sucesso"
        ),
    }
    if args.salvar:
        SAIDA.mkdir(parents=True, exist_ok=True)
        destino = SAIDA / f"{data}_{capacidade}_{args.modo}_{args.produto}.json"
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
