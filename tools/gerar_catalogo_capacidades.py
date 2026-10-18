"""Catálogo único das capacidades S01–S24 (plano v2, etapa B1; DP-09).

``capacidades/catalogo.yaml`` é a **única fonte editável** do catálogo. A partir dele e de
``capacidades/TEMPLATE_SKILL.md``, este gerador produz:

- ``capacidades/fichas/Sxx.md``: uma ficha por capacidade, com as características (seções
  1–27) e o bloco de teste em outras ferramentas de IA (prompt de sistema, casos sintéticos,
  rubrica);
- ``capacidades/fichas/README.md``: índice por onda;
- os trechos entre ``<!-- catalogo-capacidades:<bloco>:inicio -->`` e
  ``<!-- catalogo-capacidades:<bloco>:fim -->`` em ``capacidades/CATALOGO.md`` e no capítulo
  03 da proposta do agente (``docs/agente/projeto-v*/03-catalogo-skills-s01-s24.md``).

``capacidades/fichas/COMO_TESTAR.md`` é escrito à mão e só é tolerado na pasta gerada.

Antes de gerar, o YAML é validado: IDs S01–S24 únicos e em ordem, onda × gate coerentes,
dependências apontando para IDs existentes, casos de teste alinhados aos casos previstos,
fontes metodológicas conhecidas e nenhum padrão de CPF, e-mail ou telefone no arquivo.

Uso:
  python -m tools.gerar_catalogo_capacidades verificar   # 0 em sincronia; 1 divergente; 2 YAML inválido
  python -m tools.gerar_catalogo_capacidades gerar       # reescreve os arquivos gerados
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CATALOGO = Path("capacidades/catalogo.yaml")
TEMPLATE = Path("capacidades/TEMPLATE_SKILL.md")
FICHAS = Path("capacidades/fichas")
MANUAIS_EM_FICHAS = frozenset({"COMO_TESTAR.md"})
ARQUIVOS_COM_BLOCOS = ("capacidades/CATALOGO.md", "docs/agente/projeto-v*/03-catalogo-skills-s01-s24.md")

CABECALHO = ("<!-- Gerado por tools/gerar_catalogo_capacidades.py a partir de capacidades/catalogo.yaml"
             " e capacidades/TEMPLATE_SKILL.md. Não editar: altere o YAML e rode \"gerar\". -->")

# estado no YAML → (rótulo do CATALOGO.md, rótulo do cabeçalho da ficha); escala do cap. 03 §9
ESTADOS = {
    "planejada": ("planejado", "planejada"),
    "em_especificacao": ("em especificação", "em especificação"),
    "especificada": ("especificado", "especificada documentalmente; não implementada"),
    "em_implementacao": ("em implementação", "em implementação"),
    "implementada": ("implementado", "implementada; não aprovada"),
    "em_validacao": ("em validação", "em validação"),
    "aprovada": ("aprovado", "aprovada"),
}
SITUACOES_TESTE = {
    "proposta_nao_validada": "proposta, ainda não validada pela CGOV",
    "validada": "validada",
}
TRANSVERSAIS = ("SEC", "AUT", "SIS")  # casos comuns a todas as fichas, escritos no template
CAMPOS_FICHA = ("produto", "usuarios", "momento", "pre_condicoes", "entradas", "regras", "calculos", "llm",
                "consultadas", "gravadas", "dependencias", "fluxo", "alternativos", "privacidade",
                "casos_previstos", "aceite", "limites")

_MARCADOR = re.compile(r"<!-- catalogo-capacidades:(\w+):inicio -->\n(.*?)<!-- catalogo-capacidades:\1:fim -->",
                       re.S)
_CHAVE = re.compile(r"\{\{([a-z_.]+)\}\}")
_ID_SKILL = re.compile(r"S(\d\d)(?:–S(\d\d))?")
_PII = {
    "cpf": re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b|\b\d{11}\b"),
    "e-mail": re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
    "telefone": re.compile(r"\(?\b\d{2}\)?\s?9?\d{4}-\d{4}\b"),
}


class CatalogoInvalido(Exception):
    """O YAML não segue o schema; a lista de erros vem em ``args[0]``."""


# --------------------------------------------------------------------------- validação

def carregar(raiz: Path) -> dict:
    texto = (raiz / CATALOGO).read_text(encoding="utf-8")
    erros = [f"padrão de {nome} no catálogo: {m.group(0)!r}" for nome, rx in _PII.items() for m in rx.finditer(texto)]
    dados = yaml.safe_load(texto)
    erros += validar(dados)
    if erros:
        raise CatalogoInvalido(erros)
    return dados


def _ids_citados(texto: str) -> set[str]:
    ids = set()
    for m in _ID_SKILL.finditer(texto):
        inicio = int(m.group(1))
        fim = int(m.group(2)) if m.group(2) else inicio
        ids.update(f"S{n:02d}" for n in range(inicio, fim + 1))
    return ids


def validar(dados: dict) -> list[str]:
    erros: list[str] = []
    if not isinstance(dados, dict) or dados.get("versao_schema") != 1:
        return ["versao_schema ausente ou diferente de 1"]
    fontes = dados.get("fontes_metodologicas") or {}
    skills = dados.get("skills") or []
    ids = [s.get("id") for s in skills]
    if ids != [f"S{n:02d}" for n in range(1, len(ids) + 1)] or len(ids) != 24:
        erros.append(f"IDs devem ser S01–S24, únicos e em ordem: {ids}")
    conhecidos = set(ids)
    for s in skills:
        sid = s.get("id", "?")
        for chave in ("nome", "versao_ficha", "estado", "onda", "gate", "planejamento", "catalogo", "tecnica",
                      "dependencias", "fontes_metodologicas", "ficha", "teste_ia", "historico"):
            if chave not in s:
                erros.append(f"{sid}: campo obrigatório ausente: {chave}")
        if erros and any(e.startswith(f"{sid}: campo obrigatório") for e in erros):
            continue
        if s["estado"] not in ESTADOS:
            erros.append(f"{sid}: estado desconhecido: {s['estado']}")
        if s["gate"] != f"G{s['onda']}":
            erros.append(f"{sid}: gate {s['gate']} incoerente com a onda {s['onda']}")
        if s["historico"][-1]["versao"] != s["versao_ficha"]:
            erros.append(f"{sid}: a última linha do histórico deve ser a versão {s['versao_ficha']}")
        faltando = [c for c in CAMPOS_FICHA if c not in s["ficha"]]
        if faltando:
            erros.append(f"{sid}: campos da ficha ausentes: {faltando}")
            continue
        for campo in ("pre_requisitos", "consumidores"):
            for citado in sorted(_ids_citados(s["dependencias"][campo]) - conhecidos):
                erros.append(f"{sid}: dependência {campo} cita capacidade inexistente {citado}")
        for codigo in s["fontes_metodologicas"]:
            if codigo not in fontes:
                erros.append(f"{sid}: fonte metodológica desconhecida: {codigo}")
        previstos = [c["id"] for c in s["ficha"]["casos_previstos"]]
        if any(not re.fullmatch(rf"{sid}-T\d\d", c) for c in previstos) or len(set(previstos)) != len(previstos):
            erros.append(f"{sid}: casos previstos fora do padrão {sid}-Tnn ou repetidos: {previstos}")
        teste = s["teste_ia"]
        if teste.get("situacao") not in SITUACOES_TESTE:
            erros.append(f"{sid}: teste_ia.situacao desconhecida: {teste.get('situacao')}")
        if [c.get("id") for c in teste.get("casos", [])] != previstos:
            erros.append(f"{sid}: teste_ia.casos deve seguir os casos previstos {previstos}")
        for caso in teste.get("casos", []):
            for campo in ("entrada", "esperado", "falha_se"):
                if not str(caso.get(campo) or "").strip():
                    erros.append(f"{sid}: caso {caso.get('id')} sem {campo}")
    return erros


# --------------------------------------------------------------------------- renderização

def _rel(raiz: Path, de: Path, para: str) -> str:
    return Path(os.path.relpath(raiz / para, raiz / de)).as_posix()


def _preencher(template: str, contexto: dict[str, str]) -> str:
    def trocar(m: re.Match) -> str:
        if m.group(1) not in contexto:
            raise KeyError(f"marcador sem valor no template: {m.group(0)}")
        return contexto[m.group(1)]
    return _CHAVE.sub(trocar, template)


def _casos_previstos(sid: str, casos: list[dict]) -> str:
    partes = [f"{c['id'] if i == 0 else c['id'].removeprefix(sid + '-')} {c['titulo']}" for i, c in enumerate(casos)]
    return "; ".join(partes)


def _casos_ia(skill: dict) -> str:
    titulos = {c["id"]: c["titulo"] for c in skill["ficha"]["casos_previstos"]}
    blocos = []
    for caso in skill["teste_ia"]["casos"]:
        blocos.append(
            f"#### {caso['id']} — {titulos[caso['id']]}\n\n"
            f"**Mensagem do usuário:**\n\n```text\n{caso['entrada'].strip()}\n```\n\n"
            f"**Comportamento esperado:** {caso['esperado'].strip()}\n\n"
            f"**Falha se:** {caso['falha_se'].strip()}"
        )
    return "\n\n".join(blocos)


def _fontes(raiz: Path, dados: dict, skill: dict) -> str:
    codigos = skill["fontes_metodologicas"]
    if not codigos:
        return "Nenhum material metodológico específico; o prompt de sistema é suficiente."
    linhas = ["Arquivos públicos que podem ser anexados como conhecimento da ferramenta (opcional; o",
              "prompt funciona sem eles):", ""]
    for codigo in codigos:
        fonte = dados["fontes_metodologicas"][codigo]
        papel = "base metodológica canônica" if fonte["papel"] == "canonica" else "referência operacional, não canônica"
        linhas.append(f"- [{fonte['titulo']}]({_rel(raiz, FICHAS, fonte['caminho'])}) — {papel}.")
    return "\n".join(linhas)


def renderizar_ficha(raiz: Path, dados: dict, skill: dict, template: str) -> str:
    sid = skill["id"]
    contexto = {
        "id": sid,
        "nome": skill["nome"],
        "nome_minusculo": skill["nome"].lower(),
        "versao_ficha": skill["versao_ficha"],
        "estado_ficha": ESTADOS[skill["estado"]][1],
        "estado_catalogo": ESTADOS[skill["estado"]][0],
        "onda": str(skill["onda"]),
        "gate": skill["gate"],
        "casos_previstos": _casos_previstos(sid, skill["ficha"]["casos_previstos"]),
        "historico": "\n".join(f"| {h['versao']} | {h['data']} | {h['alteracao']} |" for h in skill["historico"]),
        "fontes_metodologicas": _fontes(raiz, dados, skill),
        "casos_ia": _casos_ia(skill),
        "registro": "\n".join(f"| {c} | | | | | | |" for c in
                              [c["id"] for c in skill["teste_ia"]["casos"]] + [f"{sid}-{t}" for t in TRANSVERSAIS]),
        "teste_ia.situacao": SITUACOES_TESTE[skill["teste_ia"]["situacao"]],
        "teste_ia.instrucoes": skill["teste_ia"]["instrucoes"].strip(),
    }
    for grupo in ("ficha", "catalogo", "dependencias"):
        for chave, valor in skill[grupo].items():
            if isinstance(valor, str):
                contexto[f"{grupo}.{chave}"] = valor
    return CABECALHO + "\n\n" + _preencher(template, contexto).rstrip("\n") + "\n"


def _link_ficha(raiz: Path, de: Path, sid: str) -> str:
    return _rel(raiz, de, (FICHAS / f"{sid}.md").as_posix())


def tabela(raiz: Path, dados: dict, bloco: str, de: Path) -> str:
    skills = dados["skills"]
    lnk = lambda s: f"[{s['id']}]({_link_ficha(raiz, de, s['id'])})"  # noqa: E731
    if bloco == "estado":
        cab = ["| ID | Capacidade | Estado | Onda | Gate | Versão da ficha |", "| --- | --- | --- | ---: | --- | --- |"]
        linhas = [f"| {s['id']} | [{s['nome']}]({_link_ficha(raiz, de, s['id'])}) | {ESTADOS[s['estado']][0]} "
                  f"| {s['onda']} | {s['gate']} | {s['versao_ficha']} |" for s in skills]
    elif bloco == "funcional":
        cab = ["| ID | Nome | Finalidade | Usuário principal | Entrada | Saída | Decisão humana |",
               "| --- | --- | --- | --- | --- | --- | --- |"]
        linhas = [f"| {lnk(s)} | {s['nome']} | {c['finalidade']} | {c['usuario_principal']} | {c['entrada']} "
                  f"| {c['saida']} | {c['decisao_humana']} |" for s in skills for c in [s["catalogo"]]]
    elif bloco == "tecnica":
        cab = ["| ID | Determinístico | Uso semântico permitido | Persistência principal | Integrações |",
               "| --- | --- | --- | --- | --- |"]
        linhas = [f"| {lnk(s)} | {t['deterministico']} | {t['semantico']} | {t['persistencia']} | {t['integracoes']} |"
                  for s in skills for t in [s["tecnica"]]]
    elif bloco == "dependencias":
        cab = ["| ID | Pré-requisitos funcionais | Consumidores principais | Gate |", "| --- | --- | --- | --- |"]
        linhas = [f"| {lnk(s)} | {d['pre_requisitos']} | {d['consumidores']} | {d['gate']} |"
                  for s in skills for d in [s["dependencias"]]]
    elif bloco == "planejamento":
        cab = ["| ID | Onda | Prioridade | Esforço relativo | Estado inicial | Marco |",
               "| --- | ---: | --- | --- | --- | --- |"]
        linhas = [f"| {lnk(s)} | {s['onda']} | {p['prioridade']} | {p['esforco']} | {p['estado_inicial']} | {p['marco']} |"
                  for s in sorted(skills, key=lambda s: (s["onda"], s["id"])) for p in [s["planejamento"]]]
    else:
        raise CatalogoInvalido([f"bloco desconhecido: {bloco} (em {de})"])
    return "\n".join(cab + linhas)


def indice(dados: dict) -> str:
    ondas: dict[int, list[dict]] = {}
    for s in dados["skills"]:
        ondas.setdefault(s["onda"], []).append(s)
    linhas = [
        CABECALHO, "",
        "# Fichas das capacidades S01–S24", "",
        "Cada ficha tem duas partes: as **características** da capacidade (seções 1–27, a",
        "especificação operacional) e o **teste em outras ferramentas de IA** (prompt de sistema",
        "copiável, casos sintéticos, rubrica). A fonte é [`catalogo.yaml`](../catalogo.yaml); o",
        "modelo, [`TEMPLATE_SKILL.md`](../TEMPLATE_SKILL.md). Roteiro de teste:",
        "[COMO_TESTAR.md](COMO_TESTAR.md).", "",
        "O estado `especificado` significa que a ficha existe, não que o código ou a validação",
        "institucional estejam concluídos.", "",
        "| Onda | Capacidades | Gate |", "| --- | --- | --- |",
    ]
    for onda in sorted(ondas):
        itens = ", ".join(f"[{s['id']}]({s['id']}.md) {s['nome']}" for s in ondas[onda])
        linhas.append(f"| {onda} | {itens} | {ondas[onda][0]['gate']} |")
    return "\n".join(linhas) + "\n"


# --------------------------------------------------------------------------- saídas

def _arquivos_com_blocos(raiz: Path) -> list[Path]:
    encontrados = []
    for padrao in ARQUIVOS_COM_BLOCOS:
        encontrados += sorted(p.relative_to(raiz) for p in raiz.glob(padrao))
    return encontrados


def gerar_saidas(raiz: Path) -> dict[Path, str]:
    """Conteúdo esperado de cada arquivo gerado, por caminho relativo à raiz."""
    dados = carregar(raiz)
    template = (raiz / TEMPLATE).read_text(encoding="utf-8")
    saidas = {FICHAS / f"{s['id']}.md": renderizar_ficha(raiz, dados, s, template) for s in dados["skills"]}
    saidas[FICHAS / "README.md"] = indice(dados)
    for rel in _arquivos_com_blocos(raiz):
        atual = (raiz / rel).read_text(encoding="utf-8")
        if not _MARCADOR.search(atual):
            raise CatalogoInvalido([f"{rel}: nenhum bloco catalogo-capacidades"])
        saidas[rel] = _MARCADOR.sub(
            lambda m: (f"<!-- catalogo-capacidades:{m.group(1)}:inicio -->\n{tabela(raiz, dados, m.group(1), rel.parent)}\n"
                       f"<!-- catalogo-capacidades:{m.group(1)}:fim -->"), atual)
    return saidas


def divergencias(raiz: Path) -> list[str]:
    saidas = gerar_saidas(raiz)
    problemas = []
    for rel, esperado in sorted(saidas.items()):
        caminho = raiz / rel
        if not caminho.exists():
            problemas.append(f"ausente: {rel.as_posix()}")
        elif caminho.read_text(encoding="utf-8") != esperado:
            problemas.append(f"divergente: {rel.as_posix()}")
    pasta = raiz / FICHAS
    if pasta.is_dir():
        for arquivo in sorted(pasta.iterdir()):
            rel = arquivo.relative_to(raiz)
            if rel not in saidas and arquivo.name not in MANUAIS_EM_FICHAS:
                problemas.append(f"sobrando: {rel.as_posix()}")
    return problemas


def gerar(raiz: Path) -> list[Path]:
    escritos = []
    for rel, conteudo in sorted(gerar_saidas(raiz).items()):
        caminho = raiz / rel
        if caminho.exists() and caminho.read_text(encoding="utf-8") == conteudo:
            continue
        caminho.parent.mkdir(parents=True, exist_ok=True)
        with open(caminho, "w", encoding="utf-8", newline="\n") as f:
            f.write(conteudo)
        escritos.append(rel)
    return escritos


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Catálogo único das capacidades S01–S24")
    parser.add_argument("--raiz", type=Path, default=PROJECT_ROOT, help=argparse.SUPPRESS)
    modos = parser.add_subparsers(dest="modo", required=True)
    modos.add_parser("verificar", help="confere os arquivos gerados contra o YAML (não escreve)")
    modos.add_parser("gerar", help="reescreve fichas, índice e blocos a partir do YAML")
    args = parser.parse_args(argv)
    try:
        if args.modo == "gerar":
            escritos = gerar(args.raiz)
            print(f"{len(escritos)} arquivo(s) atualizado(s)")
            for rel in escritos:
                print(f"  {rel.as_posix()}")
            return 0
        problemas = divergencias(args.raiz)
    except CatalogoInvalido as exc:
        print("catálogo inválido:", file=sys.stderr)
        for erro in exc.args[0]:
            print(f"  {erro}", file=sys.stderr)
        return 2
    if problemas:
        print("arquivos gerados fora de sincronia (rode: python -m tools.gerar_catalogo_capacidades gerar):")
        for p in problemas:
            print(f"  {p}")
        return 1
    print("catálogo em sincronia")
    return 0


if __name__ == "__main__":
    sys.exit(main())
