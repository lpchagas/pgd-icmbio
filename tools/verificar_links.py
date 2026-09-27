"""Verificador de links e referências da documentação (plano de reorganização, §11).

Lista os ``.md`` com ``git ls-files --cached --others --exclude-standard`` — o
acervo privado, ignorado pelo Git, nunca é percorrido — e classifica cada
referência:

- ``link``: ``[texto](alvo)`` relativo; confere o arquivo e, se houver, a âncora;
- ``ancora``: ``#slug`` no padrão do GitHub (acentos preservados, títulos
  repetidos com sufixo ``-1``, ``-2``…), no próprio arquivo ou no ``.md`` de destino;
- ``crase``: caminho citado entre crases (``lib/x.py``, ``docs/y.md``);
- ``placeholder``: caminho genérico (``XX``, ``AAAA-MM``, ``<escopo>``, ``*``);
- ``planejado``: alvo ausente com rótulo "planejado"/"futuro" na mesma linha;
- ``privado``: alvo em área privada, pela política única do scanner
  (``tools.security_audit.is_private_path``: ``artefatos_local``, ``cgov``, ``setup``…);
  exige rótulo "privado" na mesma linha.

Links externos (``http:``, ``mailto:``…) são contados e não verificados.
Exceções são aceitas só por arquivo e com justificativa (``--excecoes`` JSON).

Uso:
  python -m tools.verificar_links                     # relatório, sempre sai 0
  python -m tools.verificar_links --saida-json rel.json
  python -m tools.verificar_links --bloqueante        # sai 1 se houver problema (a partir do L4e)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import stat
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import unquote

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.security_audit import DEFAULT_PERFIL, is_private_path  # noqa: E402

EXCECOES_PADRAO = PROJECT_ROOT / "config" / "verificar-links-excecoes.json"
PROBLEMAS = ("link_quebrado", "ancora_quebrada", "crase_inexistente", "privado_sem_rotulo", "fora_da_raiz",
             "fonte_privada", "fonte_por_link", "alvo_por_link")

_LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+(?:\s+\"[^\"]*\")?)\)")
_CRASE = re.compile(r"(?<!`)`([^`\n]+)`(?!`)")
_CAMINHO = re.compile(r"^[\w.\-/]*\.(md|py|json|csv|ipynb|ps1|sql|toml|txt|ya?ml|cfg|ini)$|^(docs|lib|ocde|gestao|mgi|tools|tests|config)/[\w.\-/]*$")
_PLACEHOLDER = re.compile(r"XX|xxx|\.[Xx][-.]|[a-z]X\b|AAAA|MMDD|YYYY|<[^>]*>|\{[^}]*\}|\*|\.\.\.|…")
_ESQUEMA = re.compile(r"^[a-z][a-z0-9+.-]*:", re.I)
_TITULO = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
_ANCORA_HTML = re.compile(r"<a\s+(?:id|name)=[\"']([^\"']+)[\"']", re.I)
_ROTULO_PLANEJADO = re.compile(r"planejad|futur|a criar|previst", re.I)
_ROTULO_PRIVADO = re.compile(r"privad|restrit|fora do git|não versionad|nao versionad", re.I)


@dataclass(frozen=True)
class Referencia:
    arquivo: str
    linha: int
    tipo: str
    alvo: str
    classe: str


def listar_markdown(raiz: Path = PROJECT_ROOT) -> list[Path]:
    saida = subprocess.run(
        ["git", "-C", str(raiz), "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", "*.md"],
        capture_output=True, check=True,
    ).stdout.decode("utf-8")
    return sorted(raiz / nome for nome in saida.split("\0") if nome and (raiz / nome).is_file())


def slug_github(titulo: str) -> str:
    texto = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", titulo)  # link no título: fica o texto
    texto = re.sub(r"<[^>]+>", "", texto)
    return re.sub(r"[^\w\- ]", "", texto.strip().lower()).replace(" ", "-")


def _linhas_fora_de_codigo(texto: str):
    cerca = None
    for numero, linha in enumerate(texto.splitlines(), start=1):
        marca = linha.lstrip()[:3]
        if marca in ("```", "~~~"):
            cerca = None if cerca == marca else (cerca or marca)
            continue
        if cerca is None:
            yield numero, linha


def ancoras(texto: str) -> set[str]:
    vistos: Counter[str] = Counter()
    resultado: set[str] = set()
    for _, linha in _linhas_fora_de_codigo(texto):
        resultado.update(_ANCORA_HTML.findall(linha))
        titulo = _TITULO.match(linha)
        if not titulo:
            continue
        base = slug_github(titulo.group(2))
        resultado.add(base if not vistos[base] else f"{base}-{vistos[base]}")
        vistos[base] += 1
    return resultado


def _privado(partes: tuple[str, ...], perfil: str = DEFAULT_PERFIL) -> bool:
    """Política única de caminhos privados: a do scanner (tools/security_audit.py)."""

    return bool(partes) and is_private_path("/".join(partes), perfil)


# Etiquetas de reparse que são link (junção, symlink, symlink do WSL). O atributo de
# reparse sozinho não serve: pastas de nuvem (OneDrive) também o têm.
_LINK_TAGS = {0xA0000003, 0xA000000C, 0xA000001D}


def _eh_link(caminho: Path) -> bool:
    try:
        info = os.lstat(caminho)
    except OSError:
        return False
    return stat.S_ISLNK(info.st_mode) or getattr(info, "st_reparse_tag", 0) in _LINK_TAGS


def _barreira(raiz: Path, partes: tuple[str, ...]) -> str | None:
    """RL2-03: classifica um caminho **antes** de lê-lo.

    Recusa sem abrir: componente privado pelo caminho lexical, qualquer componente que
    seja link (o conteúdo poderia vir da área privada) e destino físico fora da raiz ou
    privado.
    """
    if _privado(partes):
        return "privado"
    atual = raiz
    for parte in partes:
        atual = atual / parte
        if _eh_link(atual):
            return "por_link"
    try:
        fisico = raiz.joinpath(*partes).resolve()
        relativo = fisico.relative_to(raiz.resolve())
    except (OSError, ValueError):
        return "fora_da_raiz"
    return "privado" if _privado(relativo.parts) else None


def verificar(arquivos: list[Path], raiz: Path = PROJECT_ROOT, excecoes: dict[str, str] | None = None) -> list[Referencia]:
    excecoes = excecoes or {}
    cache: dict[Path, set[str]] = {}

    def ancoras_de(caminho: Path) -> set[str]:
        if caminho not in cache:
            cache[caminho] = ancoras(caminho.read_text(encoding="utf-8", errors="replace"))
        return cache[caminho]

    referencias: list[Referencia] = []
    for arquivo in arquivos:
        relativo = arquivo.relative_to(raiz).as_posix()

        def registrar(numero: int, tipo: str, alvo: str, classe: str) -> None:
            if classe in PROBLEMAS and relativo in excecoes:
                classe = "excecao"
            referencias.append(Referencia(relativo, numero, tipo, alvo, classe))

        barreira = _barreira(raiz, arquivo.relative_to(raiz).parts)
        if barreira:  # a fonte não é lida
            registrar(0, "fonte", relativo, {"privado": "fonte_privada", "por_link": "fonte_por_link"}.get(
                barreira, "fora_da_raiz"))
            continue
        texto = arquivo.read_text(encoding="utf-8", errors="replace")

        for numero, linha in _linhas_fora_de_codigo(texto):
            planejado = bool(_ROTULO_PLANEJADO.search(linha))
            rotulo_privado = bool(_ROTULO_PRIVADO.search(linha))
            sem_crases = _CRASE.sub("", linha)
            for bruto in _LINK.findall(sem_crases):
                alvo = unquote(bruto.split()[0].strip("<>"))
                if _ESQUEMA.match(alvo):
                    registrar(numero, "link", alvo, "externo")
                    continue
                caminho_txt, _, fragmento = alvo.partition("#")
                if not caminho_txt:
                    classe = "ok" if fragmento in ancoras_de(arquivo) else "ancora_quebrada"
                    registrar(numero, "ancora", alvo, classe)
                    continue
                bruto_destino = (raiz / caminho_txt.lstrip("/")) if caminho_txt.startswith("/") else (arquivo.parent / caminho_txt)
                # 1º caminho lexical (preserva o componente privado); 2º resolvido (não sai da raiz).
                lexico = Path(os.path.normpath(bruto_destino))
                try:
                    partes = lexico.relative_to(raiz).parts
                except ValueError:
                    registrar(numero, "link", alvo, "fora_da_raiz")
                    continue
                if _privado(partes):
                    registrar(numero, "link", alvo, "privado" if rotulo_privado else "privado_sem_rotulo")
                    continue
                destino = raiz.joinpath(*partes)
                barreira = _barreira(raiz, partes) if os.path.lexists(destino) else None
                if barreira == "privado":
                    registrar(numero, "link", alvo, "privado" if rotulo_privado else "privado_sem_rotulo")
                elif barreira == "por_link":  # o destino não é lido (nem para âncoras)
                    registrar(numero, "link", alvo, "alvo_por_link")
                elif barreira == "fora_da_raiz":
                    registrar(numero, "link", alvo, "fora_da_raiz")
                elif not destino.exists():
                    registrar(numero, "link", alvo, "planejado" if planejado else "link_quebrado")
                elif fragmento and destino.suffix == ".md":
                    classe = "ok" if fragmento in ancoras_de(destino) else "ancora_quebrada"
                    registrar(numero, "ancora", alvo, classe)
                else:
                    registrar(numero, "link", alvo, "ok")
            for citado in _CRASE.findall(linha):
                citado = citado.strip()
                if " " in citado or not _CAMINHO.match(citado):
                    continue
                if _PLACEHOLDER.search(citado):
                    registrar(numero, "crase", citado, "placeholder")
                    continue
                partes = tuple(p for p in Path(citado).parts if p not in (".",))
                if _privado(partes):
                    registrar(numero, "crase", citado, "privado" if rotulo_privado else "privado_sem_rotulo")
                    continue
                if (raiz / citado).exists() or (arquivo.parent / citado).exists():
                    registrar(numero, "crase", citado, "ok")
                elif "/" not in citado:
                    registrar(numero, "crase", citado, "nome_sem_caminho")
                else:
                    registrar(numero, "crase", citado, "planejado" if planejado else "crase_inexistente")
    return referencias


def resumir(referencias: list[Referencia]) -> dict:
    por_classe = Counter(r.classe for r in referencias)
    problemas: dict[str, list[dict]] = defaultdict(list)
    for r in referencias:
        if r.classe in PROBLEMAS:
            problemas[r.arquivo].append({"linha": r.linha, "tipo": r.tipo, "alvo": r.alvo, "classe": r.classe})
    return {
        "arquivos_com_problema": len(problemas),
        "por_classe": dict(sorted(por_classe.items())),
        "total_problemas": sum(por_classe[c] for c in PROBLEMAS),
        "problemas": dict(sorted(problemas.items())),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Relatório de links e referências dos .md versionados.")
    parser.add_argument("--excecoes", type=Path, default=None,
                        help='JSON {"arquivo.md": "justificativa"}. Padrão: config/verificar-links-excecoes.json, se existir.')
    parser.add_argument("--saida-json", type=Path)
    parser.add_argument("--bloqueante", action="store_true", help="sai 1 se houver problema (gate do CI a partir do L4e)")
    args = parser.parse_args(argv)
    arquivo_excecoes = args.excecoes or (EXCECOES_PADRAO if EXCECOES_PADRAO.is_file() else None)
    excecoes = json.loads(arquivo_excecoes.read_text(encoding="utf-8")) if arquivo_excecoes else {}
    if any(not str(j).strip() for j in excecoes.values()):
        parser.error("toda exceção precisa de justificativa")
    arquivos = listar_markdown()
    resumo = resumir(verificar(arquivos, excecoes=excecoes))
    resumo["arquivos_verificados"] = len(arquivos)
    if args.saida_json:
        args.saida_json.write_text(json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(arquivos)} arquivos .md; {resumo['total_problemas']} problema(s) em {resumo['arquivos_com_problema']} arquivo(s)")
    for classe, quantidade in resumo["por_classe"].items():
        print(f"  {classe:<20} {quantidade}")
    for arquivo, itens in resumo["problemas"].items():
        print(f"- {arquivo}")
        for item in itens:
            print(f"    L{item['linha']} {item['classe']}: {item['alvo']}")
    return 1 if args.bloqueante and resumo["total_problemas"] else 0


if __name__ == "__main__":
    sys.exit(main())
