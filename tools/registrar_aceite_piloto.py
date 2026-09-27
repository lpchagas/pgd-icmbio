"""Registra aceites de piloto, deliberações de expansão e revogações (plano §7.4, L5).

O registro fica no acervo privado (``artefatos_local/validacao/pilotos/aceites.json``)
e só referencia o ato humano (caminho privado + hash); o JSON não é assinatura.
Recusa enquanto o cadastro do piloto não estiver conferido na fonte (L7), quando as
dependências da capacidade têm alterações locais não commitadas e quando o
manifesto não vem de execução nova, integrada e bem-sucedida no escopo do piloto.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from lib import liberacao
from lib.periodos import ANALYSIS_TIMEZONE


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    comandos = parser.add_subparsers(dest="comando", required=True)

    aceite = comandos.add_parser("aceite", help="Aceite de uma capacidade em uma unidade piloto.")
    aceite.add_argument("--capacidade", required=True)
    aceite.add_argument("--piloto", required=True, help="Sigla do cadastro: CGOV, COCAGE ou GR2.")
    aceite.add_argument("--manifesto", type=Path, required=True, help="Manifesto da execução nova do candidato.")
    aceite.add_argument("--evidencia", type=Path, required=True, help="Ato humano no acervo privado.")
    aceite.add_argument("--papel-aprovador", required=True, help="Papel institucional, não nome pessoal.")

    deliberacao = comandos.add_parser("deliberacao", help="Deliberação de expansão para uma capacidade.")
    deliberacao.add_argument("--capacidade", required=True)
    deliberacao.add_argument("--evidencia", type=Path, required=True)
    deliberacao.add_argument("--papel-aprovador", required=True)

    revogar = comandos.add_parser("revogar", help="Revoga um aceite ou deliberação pelo id.")
    revogar.add_argument("--id", required=True)
    revogar.add_argument("--motivo", required=True)
    revogar.add_argument("--papel-aprovador", required=True)

    verificar = comandos.add_parser("verificar", help="Mostra a elegibilidade atual da capacidade.")
    verificar.add_argument("--capacidade", required=True)

    for sub in (aceite, deliberacao, revogar):
        sub.add_argument("--dry-run", action="store_true")
    return parser


def _agora() -> str:
    return datetime.now(ZoneInfo(ANALYSIS_TIMEZONE)).isoformat(timespec="seconds")


def _id(registro: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(registro, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:12]


def _gravar(dados: dict[str, Any]) -> Path:
    destino = liberacao.ARQUIVO_ACEITES
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporario = destino.with_suffix(".json.tmp")
    temporario.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporario, destino)
    return destino


def _identidade_sem_alteracoes(capacidade: str, cadastro: liberacao.Cadastro) -> dict[str, Any]:
    identidade = liberacao.identidade_candidato(capacidade, cadastro)
    if identidade["alteracoes_locais"]:
        raise ValueError("As dependências da capacidade têm alterações locais: o candidato precisa estar commitado.")
    return identidade


def registrar_aceite(args: argparse.Namespace) -> dict[str, Any]:
    cadastro = liberacao.carregar_cadastro()
    piloto = next((p for p in cadastro.pilotos if p.sigla == args.piloto.strip().upper()), None)
    if piloto is None:
        raise ValueError(f"Piloto fora do cadastro: {args.piloto}")
    if not piloto.conferido:
        raise ValueError(f"Cadastro do piloto {piloto.sigla} não conferido na fonte (id_petrvs): aceite recusado até o L7.")
    problemas = [m for m in liberacao.problemas_cadastro(cadastro) if m.startswith(f"{piloto.sigla}:")]
    if problemas:
        raise ValueError("Cadastro divergente da hierarquia atual: " + "; ".join(problemas))
    identidade = _identidade_sem_alteracoes(args.capacidade, cadastro)
    escopo = liberacao.escopo_resolvido(piloto)
    problema = liberacao.problema_manifesto(args.manifesto, args.capacidade, escopo["chave"])
    if problema:
        raise ValueError(f"Manifesto recusado: {problema}")
    registro = {
        **{campo: identidade[campo] for campo in ("capacidade", "versao", "fingerprint", "commit", "politica", "cadastro_versao")},
        "piloto": piloto.sigla,
        "escopo_resolvido": escopo,
        "manifesto": liberacao.referencia_arquivo(args.manifesto),
        "evidencia": liberacao.referencia_arquivo(args.evidencia),
        "papel_aprovador": args.papel_aprovador,
        "registrado_em": _agora(),
        "revogado": False,
    }
    return {"id": _id(registro), **registro}


def registrar_deliberacao(args: argparse.Namespace) -> dict[str, Any]:
    cadastro = liberacao.carregar_cadastro()
    identidade = _identidade_sem_alteracoes(args.capacidade, cadastro)
    registro = {
        **{campo: identidade[campo] for campo in ("capacidade", "versao", "fingerprint", "commit", "politica", "cadastro_versao")},
        "evidencia": liberacao.referencia_arquivo(args.evidencia),
        "papel_aprovador": args.papel_aprovador,
        "registrado_em": _agora(),
        "revogado": False,
    }
    return {"id": _id(registro), **registro}


def run(argv: list[str] | None = None) -> dict[str, Any]:
    args = build_parser().parse_args(argv)
    dados = liberacao.ler_registro()
    if args.comando == "verificar":
        elegivel, motivos = liberacao.elegivel_para_liberacao(
            liberacao.identidade_candidato(args.capacidade), registro=dados)
        return {"capacidade": args.capacidade, "elegivel": elegivel, "motivos": motivos}
    if args.comando == "aceite":
        novo, colecao = registrar_aceite(args), "aceites"
    elif args.comando == "deliberacao":
        novo, colecao = registrar_deliberacao(args), "deliberacoes"
    else:
        alvo = next((item for nome in ("aceites", "deliberacoes") for item in dados[nome] if item.get("id") == args.id), None)
        if alvo is None:
            raise ValueError(f"Registro não encontrado: {args.id}")
        if alvo.get("revogado"):
            raise ValueError(f"Registro já revogado: {args.id}")
        alvo.update({"revogado": True, "revogacao": {"motivo": args.motivo, "papel_aprovador": args.papel_aprovador,
                                                     "registrado_em": _agora()}})
        novo, colecao = alvo, None
    if colecao:
        dados[colecao].append(novo)
    resultado = {"comando": args.comando, "registro": novo, "dry_run": args.dry_run}
    if not args.dry_run:
        resultado["arquivo"] = _gravar(dados).name
    return resultado


def main(argv: list[str] | None = None) -> int:
    try:
        resultado = run(argv)
    except ValueError as exc:
        print(f"Recusado: {exc}")
        return 1
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    return 0 if resultado.get("elegivel", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
