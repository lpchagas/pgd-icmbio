"""Sincronia do núcleo comum das instruções (plano de reorganização, §6; L4d).

``CLAUDE.md``, ``AGENTS.md`` e ``PROJECT.md`` são pares sem hierarquia (DP-03,
ADR-010). Cada um tem:

- o título (linha 1, ``# …``) antes do núcleo;
- o **núcleo comum**, idêntico nos três, entre ``<!-- nucleo-comum:inicio -->`` e
  ``<!-- nucleo-comum:fim -->``;
- o **bloco da ferramenta**, depois do marcador final, com até 40 linhas e só com os
  títulos permitidos (``TITULOS_PERMITIDOS``).

O hash do núcleo é calculado sobre o texto normalizado (UTF-8 sem BOM, LF, sem espaço
no fim da linha, uma quebra final) e guardado em ``config/instrucoes.lock.json``.

Estados (base = hash do lock; A, B, C = núcleos normalizados):

== ===================================================== ============ ===========================
#  Situação                                              ``verificar`` ``sincronizar``
== ===================================================== ============ ===========================
1  A=B=C=base                                            ok           nada
2  A=B=C≠base                                            falha        atualiza o lock
3  lock ausente e A=B=C                                  falha        cria o lock
4  lock ausente e divergentes                            conflito     não escreve; relatório
5  um ≠ base, dois = base                                falha        propaga o divergente
6  dois iguais ≠ base, um = base                         falha        só com diário interrompido;
                                                                      sem diário, conflito
7  dois ou três ≠ base e diferentes entre si             conflito     não escreve; relatório
8  marcadores, título ou bloco fora da estrutura         erro         não escreve
== ===================================================== ============ ===========================

Garantias (plano v3, §6): a escrita é atômica **por arquivo** (``os.replace``); não há
transação sobre o conjunto. O diário (``artefatos_local/sincronia/operacao.json``)
registra a base, o hash lido e o esperado de cada arquivo e as escritas concluídas;
``recuperar`` retoma ou desfaz a partir dele. Antes de substituir cada arquivo, o hash
lido é conferido de novo (compare-and-swap). O lock de exclusão
(``.sincronia.lck``, criado com ``O_EXCL``) registra pid, host e operação e nunca é
apagado pela idade. Arquivo que seja symlink, ponto de reparse ou hardlink é recusado.

Uso:
  python -m tools.sincronizar_instrucoes verificar            # árvore de trabalho
  python -m tools.sincronizar_instrucoes verificar --staged   # índice do Git (hook)
  python -m tools.sincronizar_instrucoes sincronizar
  python -m tools.sincronizar_instrucoes recuperar [--desfazer]
  python -m tools.sincronizar_instrucoes importar --de <pasta>  # só lista seções

Saídas: 0 ok; 1 falha sincronizável (estados 2, 3, 5 e 6); 2 conflito (4, 7 e 6 sem
diário); 3 erro estrutural ou recusa de link (8); 4 operação em andamento (lock).
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import socket
import stat
import subprocess
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

ARQUIVOS = ("CLAUDE.md", "AGENTS.md", "PROJECT.md")
LOCK_REL = "config/instrucoes.lock.json"
DIARIO_REL = "artefatos_local/sincronia"
DIARIO_NOME = "operacao.json"
EXCLUSAO_NOME = ".sincronia.lck"
MARCADOR_INICIO = "<!-- nucleo-comum:inicio -->"
MARCADOR_FIM = "<!-- nucleo-comum:fim -->"
TITULOS_PERMITIDOS = ("Mecânica da ferramenta", "Skills desta ferramenta", "Comandos da ferramenta")
LIMITE_BLOCO = 40
LOCK_VERSAO = 1

OK, FALHA, CONFLITO, ERRO, OCUPADO = 0, 1, 2, 3, 4

_TITULO = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
_CERCA = re.compile(r"^\s{0,3}(`{3,}|~{3,})")


class SincroniaErro(Exception):
    """Recusa com código de saída (conflito, erro estrutural ou lock ocupado)."""

    def __init__(self, codigo: int, mensagem: str):
        super().__init__(mensagem)
        self.codigo = codigo


# --------------------------------------------------------------------------- texto


def normalizar(texto: str) -> str:
    """UTF-8 sem BOM, LF, sem espaço no fim da linha e uma quebra final."""
    texto = texto.lstrip("﻿").replace("\r\n", "\n").replace("\r", "\n")
    linhas = [linha.rstrip() for linha in texto.split("\n")]
    return "\n".join(linhas).strip("\n") + "\n"


def _sha(dados: bytes | str) -> str:
    if isinstance(dados, str):
        dados = dados.encode("utf-8")
    return hashlib.sha256(dados).hexdigest()


def _decodificar(bruto: bytes) -> str:
    return bruto.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")


@dataclass
class Instrucao:
    nome: str
    bruto: bytes
    pre: str = ""
    nucleo: str = ""
    pos: str = ""
    erros: list[str] = field(default_factory=list)

    @property
    def sha_bruto(self) -> str:
        return _sha(self.bruto)

    @property
    def sha_nucleo(self) -> str:
        return _sha(self.nucleo)


def _titulos_fora_de_cerca(linhas: list[str]) -> list[tuple[int, str]]:
    titulos, cerca = [], None
    for numero, linha in enumerate(linhas, 1):
        marca = _CERCA.match(linha)
        if marca:
            simbolo = marca.group(1)
            if cerca is None:
                cerca = simbolo
            elif simbolo[0] == cerca[0] and len(simbolo) >= len(cerca):
                cerca = None
            continue
        if cerca is None and _TITULO.match(linha):
            titulos.append((numero, linha))
    return titulos


def analisar(nome: str, bruto: bytes) -> Instrucao:
    """Separa título, núcleo e bloco da ferramenta e confere a estrutura (estado 8)."""
    inst = Instrucao(nome=nome, bruto=bruto)
    try:
        texto = _decodificar(bruto)
    except UnicodeDecodeError:
        inst.erros.append("não está em UTF-8")
        return inst
    linhas = texto.split("\n")
    inicio = [i for i, l in enumerate(linhas) if MARCADOR_INICIO in l]
    fim = [i for i, l in enumerate(linhas) if MARCADOR_FIM in l]
    if len(inicio) != 1 or len(fim) != 1:
        inst.erros.append(f"marcadores: {len(inicio)} de início e {len(fim)} de fim (esperado 1 e 1)")
        return inst
    i, f = inicio[0], fim[0]
    if linhas[i].strip() != MARCADOR_INICIO or linhas[f].strip() != MARCADOR_FIM:
        inst.erros.append("marcador fora de linha própria")
    if i >= f:
        inst.erros.append("marcador de fim antes do de início")
        return inst

    pre = [l for l in linhas[:i] if l.strip()]
    if len(pre) != 1 or not re.match(r"^#\s+\S", pre[0]):
        inst.erros.append("antes do núcleo só pode haver o título do arquivo (uma linha '# …')")

    pos = linhas[f + 1:]
    while pos and not pos[-1].strip():
        pos.pop()
    corpo = list(pos)
    while corpo and not corpo[0].strip():
        corpo.pop(0)
    if len(corpo) > LIMITE_BLOCO:
        inst.erros.append(f"bloco da ferramenta com {len(corpo)} linhas (limite {LIMITE_BLOCO})")
    for numero, linha in _titulos_fora_de_cerca(pos):
        nivel, titulo = _TITULO.match(linha).groups()
        if len(nivel) != 2 or titulo not in TITULOS_PERMITIDOS:
            inst.erros.append(f"título não permitido no bloco da ferramenta (linha {f + 1 + numero}): {linha.strip()}")

    inst.pre = "\n".join(linhas[:i]) + "\n" if i else ""
    inst.nucleo = normalizar("\n".join(linhas[i:f + 1]))
    inst.pos = "\n".join(linhas[f + 1:])
    return inst


def montar(inst: Instrucao, nucleo: str) -> bytes:
    """Arquivo com o núcleo dado: título e bloco preservados; UTF-8 sem BOM e LF."""
    pos = inst.pos.rstrip("\n")
    texto = inst.pre + nucleo + (pos + "\n" if pos.strip() else "")
    return texto.encode("utf-8")


# --------------------------------------------------------------------------- leitura


def _problema_de_link(caminho: Path) -> str | None:
    try:
        st = os.lstat(caminho)
    except FileNotFoundError:
        return None
    atributos = getattr(st, "st_file_attributes", 0)
    if stat.S_ISLNK(st.st_mode) or atributos & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400):
        return "é link (symlink ou ponto de reparse); precisa ser arquivo regular"
    if st.st_nlink > 1:
        return f"é hardlink (nlink={st.st_nlink}); precisa ser arquivo regular"
    return None


def _git(raiz: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(raiz), *args], capture_output=True)


def _ler(raiz: Path, rel: str, staged: bool) -> bytes | None:
    if staged:
        modo = _git(raiz, "ls-files", "-s", "--", rel).stdout.decode("utf-8").split()
        if modo and modo[0] == "120000":
            raise SincroniaErro(ERRO, f"{rel}: preparado como link no índice; precisa ser arquivo regular")
        saida = _git(raiz, "show", f":{rel}")
        return saida.stdout if saida.returncode == 0 else None
    caminho = raiz / rel
    problema = _problema_de_link(caminho)
    if problema:
        raise SincroniaErro(ERRO, f"{rel}: {problema}")
    return caminho.read_bytes() if caminho.is_file() else None


def ler_lock(bruto: bytes | None) -> str | None:
    if bruto is None:
        return None
    try:
        dados = json.loads(bruto.decode("utf-8"))
        valor = dados["nucleo"]
    except (ValueError, KeyError, TypeError) as exc:
        raise SincroniaErro(ERRO, f"{LOCK_REL} inválido ({type(exc).__name__})") from exc
    casamento = re.fullmatch(r"sha256:([0-9a-f]{64})", str(valor))
    if not casamento:
        raise SincroniaErro(ERRO, f"{LOCK_REL}: valor de 'nucleo' inválido")
    return casamento.group(1)


def conteudo_lock(sha_nucleo: str) -> bytes:
    # O prefixo "sha256:" evita o falso positivo de string hexadecimal de alta entropia
    # do detect-secrets, que bloquearia a auditoria de publicação.
    dados = {
        "versao": LOCK_VERSAO,
        "algoritmo": "sha256 do núcleo normalizado (UTF-8 sem BOM, LF, sem espaço no fim da linha, uma quebra final)",
        "arquivos": list(ARQUIVOS),
        "nucleo": f"sha256:{sha_nucleo}",
    }
    return (json.dumps(dados, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


@dataclass
class Leitura:
    instrucoes: dict[str, Instrucao]
    lock_bruto: bytes | None
    base: str | None


def ler_estado(raiz: Path, staged: bool = False) -> Leitura:
    instrucoes, erros = {}, []
    for nome in ARQUIVOS:
        bruto = _ler(raiz, nome, staged)
        if bruto is None:
            erros.append(f"{nome}: ausente" + (" no índice do Git" if staged else ""))
            continue
        inst = analisar(nome, bruto)
        erros.extend(f"{nome}: {erro}" for erro in inst.erros)
        instrucoes[nome] = inst
    lock_bruto = _ler(raiz, LOCK_REL, staged)
    base = ler_lock(lock_bruto)
    if erros:
        raise SincroniaErro(ERRO, "erro estrutural (estado 8):\n  - " + "\n  - ".join(erros))
    return Leitura(instrucoes, lock_bruto, base)


# --------------------------------------------------------------------------- estados


@dataclass
class Diagnostico:
    estado: int
    mensagem: str
    alvo: str | None = None          # hash do núcleo que deve prevalecer
    origens: tuple[str, ...] = ()    # arquivos que já têm o núcleo-alvo


def classificar(leitura: Leitura) -> Diagnostico:
    hashes = {nome: inst.sha_nucleo for nome, inst in leitura.instrucoes.items()}
    distintos = set(hashes.values())
    base = leitura.base
    if base is None:
        if len(distintos) == 1:
            alvo = distintos.pop()
            return Diagnostico(3, "lock ausente; os três núcleos são iguais", alvo, ARQUIVOS)
        return Diagnostico(4, "lock ausente e núcleos divergentes")
    diferentes = [nome for nome, h in hashes.items() if h != base]
    if not diferentes:
        return Diagnostico(1, "núcleos iguais ao lock", base, ARQUIVOS)
    if len(diferentes) == len(ARQUIVOS) and len(distintos) == 1:
        return Diagnostico(2, "lock desatualizado: os três núcleos são iguais entre si e diferentes do lock",
                           distintos.pop(), ARQUIVOS)
    if len(diferentes) == 1:
        nome = diferentes[0]
        return Diagnostico(5, f"{nome} alterado; os outros dois iguais ao lock", hashes[nome], (nome,))
    if len(diferentes) == 2 and hashes[diferentes[0]] == hashes[diferentes[1]]:
        return Diagnostico(6, f"{' e '.join(diferentes)} iguais entre si e diferentes do lock",
                           hashes[diferentes[0]], tuple(diferentes))
    return Diagnostico(7, "núcleos alterados de formas diferentes: " + ", ".join(diferentes))


# --------------------------------------------------------------------------- escrita


def escrever_atomico(caminho: Path, dados: bytes) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temporario = caminho.with_name(f".{caminho.name}.tmp-{uuid.uuid4().hex[:8]}")
    with open(temporario, "wb") as saida:
        saida.write(dados)
        saida.flush()
        os.fsync(saida.fileno())
    os.replace(temporario, caminho)


def _processo_vivo(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes

        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.OpenProcess.restype = wintypes.HANDLE
        processo = kernel.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not processo:
            return ctypes.get_last_error() == 5  # acesso negado: o processo existe
        try:
            codigo = wintypes.DWORD()
            if not kernel.GetExitCodeProcess(processo, ctypes.byref(codigo)):
                return True
            return codigo.value == 259  # STILL_ACTIVE
        finally:
            kernel.CloseHandle(processo)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


class Exclusao:
    """Lock de exclusão mútua (``O_EXCL``) com pid, host e operação; nunca é removido pela idade."""

    def __init__(self, diario_dir: Path, operacao: str):
        self.caminho = diario_dir / EXCLUSAO_NOME
        self.operacao = operacao

    def adquirir(self) -> None:
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        try:
            fd = os.open(self.caminho, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            raise SincroniaErro(OCUPADO, _mensagem_ocupado(self.caminho)) from None
        dados = {"pid": os.getpid(), "host": socket.gethostname(), "operacao": self.operacao,
                 "criado_em": datetime.now().isoformat(timespec="seconds")}
        with os.fdopen(fd, "w", encoding="utf-8") as saida:
            json.dump(dados, saida, ensure_ascii=False)

    def liberar(self) -> None:
        self.caminho.unlink(missing_ok=True)


def _ler_exclusao(caminho: Path) -> dict:
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _mensagem_ocupado(caminho: Path) -> str:
    dados = _ler_exclusao(caminho)
    return (f"lock de sincronia presente ({caminho}): pid {dados.get('pid')}, host {dados.get('host')}, "
            f"operação {dados.get('operacao')}. Se a operação foi interrompida, rode "
            "'python -m tools.sincronizar_instrucoes recuperar'")


def _novo_id() -> str:
    return f"{datetime.now().strftime('%Y%m%dT%H%M%S')}-{uuid.uuid4().hex[:8]}"


def _gravar_diario(diario_dir: Path, diario: dict) -> None:
    escrever_atomico(diario_dir / DIARIO_NOME,
                     (json.dumps(diario, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def ler_diario(diario_dir: Path) -> dict | None:
    caminho = diario_dir / DIARIO_NOME
    if not caminho.is_file():
        return None
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise SincroniaErro(ERRO, f"diário ilegível: {caminho}") from exc


def _preparar_operacao(diario_dir: Path, operacao: str, leitura: Leitura, diag: Diagnostico) -> dict:
    """Diário da operação + cópias do antes e do depois de cada arquivo (retomar ou desfazer)."""
    origem = leitura.instrucoes[diag.origens[0]]
    pasta = diario_dir / f"operacao-{operacao}"
    arquivos = {}
    for nome, inst in leitura.instrucoes.items():
        if inst.sha_nucleo == diag.alvo:
            continue
        novo = montar(inst, origem.nucleo)
        escrever_atomico(pasta / f"{nome}.antes", inst.bruto)
        escrever_atomico(pasta / f"{nome}.depois", novo)
        arquivos[nome] = {"sha_lido": inst.sha_bruto, "sha_esperado": _sha(novo), "escrito": False}
    novo_lock = conteudo_lock(diag.alvo)
    if leitura.lock_bruto is not None:
        escrever_atomico(pasta / "lock.antes", leitura.lock_bruto)
    escrever_atomico(pasta / "lock.depois", novo_lock)
    return {
        "id": operacao,
        "estado_inicial": diag.estado,
        "base": leitura.base,
        "nucleo_alvo": diag.alvo,
        "origem": diag.origens[0],
        "arquivos": arquivos,
        "lock": {"sha_lido": _sha(leitura.lock_bruto) if leitura.lock_bruto is not None else None,
                 "sha_esperado": _sha(novo_lock), "escrito": False},
        "concluida": False,
    }


def _sha_atual(caminho: Path) -> str | None:
    problema = _problema_de_link(caminho)
    if problema:
        raise SincroniaErro(ERRO, f"{caminho.name}: {problema}")
    return _sha(caminho.read_bytes()) if caminho.is_file() else None


def _itens(raiz: Path, diario: dict) -> list[tuple[str, Path, dict]]:
    itens = [(nome, raiz / nome, dados) for nome, dados in diario["arquivos"].items()]
    itens.append(("lock", raiz / LOCK_REL, diario["lock"]))
    return itens


def _algo_escrito(diario: dict) -> bool:
    return any(dados["escrito"] for dados in [*diario["arquivos"].values(), diario["lock"]])


def _executar(raiz: Path, diario_dir: Path, diario: dict, desfazer: bool = False) -> list[str]:
    """Aplica (ou desfaz) as escritas do diário, com compare-and-swap antes de cada uma.

    Cada item está no hash de partida (``de``) ou no de chegada (``para``). Antes da
    primeira escrita, todos são conferidos; qualquer outro hash é conflito e nada é
    escrito. A conferência se repete imediatamente antes de cada substituição.
    """
    de, para, sufixo = ("sha_esperado", "sha_lido", "antes") if desfazer else ("sha_lido", "sha_esperado", "depois")
    itens = _itens(raiz, diario)
    if desfazer:
        itens.reverse()
    for _, caminho, dados in itens:
        if _sha_atual(caminho) not in (dados[de], dados[para]):
            raise SincroniaErro(CONFLITO, f"{caminho.name} foi alterado fora da sincronia (compare-and-swap)")
    pasta = diario_dir / f"operacao-{diario['id']}"
    feitos = []
    for rotulo, caminho, dados in itens:
        atual = _sha_atual(caminho)
        if atual == dados[para]:
            dados["escrito"] = not desfazer
            continue
        if atual != dados[de]:
            raise SincroniaErro(CONFLITO, f"{caminho.name} mudou durante a operação (compare-and-swap)")
        if dados[para] is None:
            caminho.unlink()
        else:
            escrever_atomico(caminho, (pasta / f"{rotulo}.{sufixo}").read_bytes())
        dados["escrito"] = not desfazer
        _gravar_diario(diario_dir, diario)
        feitos.append(caminho.name)
    return feitos


def _relatorio_conflito(diario_dir: Path, leitura: Leitura, diag: Diagnostico) -> Path:
    caminho = diario_dir / f"conflito-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
    partes = [f"# Conflito de sincronia (estado {diag.estado})", "", diag.mensagem, "",
              f"Lock: `{leitura.base or 'ausente'}`", ""]
    nomes = list(leitura.instrucoes)
    partes += [f"- `{nome}`: `{leitura.instrucoes[nome].sha_nucleo}`" for nome in nomes]
    referencia = nomes[0]
    for nome in nomes[1:]:
        texto = "\n".join(difflib.unified_diff(
            leitura.instrucoes[referencia].nucleo.splitlines(), leitura.instrucoes[nome].nucleo.splitlines(),
            fromfile=referencia, tofile=nome, lineterm=""))
        if texto:
            partes += ["", f"## {referencia} × {nome}", "", "```diff", texto, "```"]
    escrever_atomico(caminho, ("\n".join(partes) + "\n").encode("utf-8"))
    return caminho


# --------------------------------------------------------------------------- modos


def verificar(raiz: Path = PROJECT_ROOT, staged: bool = False) -> tuple[int, str]:
    """Só lê (árvore de trabalho ou índice do Git); nunca escreve."""
    try:
        diag = classificar(ler_estado(raiz, staged))
    except SincroniaErro as exc:
        return exc.codigo, str(exc)
    if diag.estado == 1:
        return OK, "ok: núcleo idêntico nos três arquivos e igual ao lock (estado 1)"
    if diag.estado in (4, 7):
        return CONFLITO, f"conflito (estado {diag.estado}): {diag.mensagem}. Resolva à mão e rode 'sincronizar'"
    return FALHA, (f"estado {diag.estado}: {diag.mensagem}. Rode "
                   "'python -m tools.sincronizar_instrucoes sincronizar' e depois 'git add'")


def _conduzir(raiz: Path, diario_dir: Path, diario: dict, desfazer: bool, exclusao: Exclusao) -> tuple[int, str]:
    """Executa um diário sob o lock já adquirido; libera o lock se não houver escrita parcial."""
    try:
        feitos = _executar(raiz, diario_dir, diario, desfazer)
    except SincroniaErro as exc:
        exclusao.liberar()
        if not diario.get("retomada") and not _algo_escrito(diario):
            diario.update(concluida=True, resultado="recusada")
            _gravar_diario(diario_dir, diario)
            return exc.codigo, f"{exc}. Nada foi escrito"
        return exc.codigo, (f"{exc}. A operação {diario['id']} ficou pendente; confira os arquivos e rode "
                            "'recuperar' (retoma), 'recuperar --desfazer' ou 'recuperar --abandonar'")
    if desfazer:
        resultado = "desfeita"
    else:
        resultado = "retomada" if diario.get("retomada") else "aplicada"
    diario.update(concluida=True, resultado=resultado)
    _gravar_diario(diario_dir, diario)
    exclusao.liberar()
    return OK, f"operação {diario['id']} {diario['resultado']}: {', '.join(feitos) or 'nada a escrever'}"


def sincronizar(raiz: Path = PROJECT_ROOT, diario_dir: Path | None = None) -> tuple[int, str]:
    diario_dir = diario_dir or raiz / DIARIO_REL
    if (diario_dir / EXCLUSAO_NOME).exists():
        return OCUPADO, _mensagem_ocupado(diario_dir / EXCLUSAO_NOME)
    try:
        leitura = ler_estado(raiz)
        diag = classificar(leitura)
        pendente = ler_diario(diario_dir)
    except SincroniaErro as exc:
        return exc.codigo, str(exc)
    if pendente and not pendente.get("concluida"):
        # operação interrompida (inclusive o estado 6 que ela deixou): retomar pelo diário
        return _retomar(raiz, diario_dir, pendente, desfazer=False)
    if diag.estado == 1:
        return OK, "nada a fazer (estado 1)"
    if diag.estado in (4, 6, 7):
        relatorio = _relatorio_conflito(diario_dir, leitura, diag)
        motivo = " sem diário de operação interrompida" if diag.estado == 6 else ""
        return CONFLITO, (f"conflito (estado {diag.estado}{motivo}): {diag.mensagem}. "
                          f"Nada foi escrito. Diff em {relatorio}")
    operacao = _novo_id()
    exclusao = Exclusao(diario_dir, operacao)
    try:
        exclusao.adquirir()
    except SincroniaErro as exc:
        return exc.codigo, str(exc)
    # Exceção inesperada daqui em diante mantém o lock: 'recuperar' decide pelo diário.
    diario = _preparar_operacao(diario_dir, operacao, leitura, diag)
    _gravar_diario(diario_dir, diario)
    codigo, mensagem = _conduzir(raiz, diario_dir, diario, False, exclusao)
    return codigo, (f"estado {diag.estado}: {mensagem}" if codigo == OK else mensagem)


def _retomar(raiz: Path, diario_dir: Path, diario: dict, desfazer: bool) -> tuple[int, str]:
    exclusao = Exclusao(diario_dir, diario["id"])
    try:
        exclusao.adquirir()
    except SincroniaErro as exc:
        return exc.codigo, str(exc)
    diario["retomada"] = True
    return _conduzir(raiz, diario_dir, diario, desfazer, exclusao)


def recuperar(raiz: Path = PROJECT_ROOT, diario_dir: Path | None = None,
              desfazer: bool = False, abandonar: bool = False) -> tuple[int, str]:
    """Trata lock abandonado e operação interrompida, a partir do diário.

    O lock só é considerado abandonado se foi criado neste host e o processo não existe
    mais; a idade nunca conta. Operação pendente é retomada (padrão), desfeita
    (``--desfazer``) ou encerrada sem escrita (``--abandonar``, depois de conferência humana).
    """
    diario_dir = diario_dir or raiz / DIARIO_REL
    caminho = diario_dir / EXCLUSAO_NOME
    avisos = []
    if caminho.exists():
        dados = _ler_exclusao(caminho)
        host, pid = dados.get("host"), dados.get("pid")
        if host != socket.gethostname() or not isinstance(pid, int):
            return OCUPADO, (f"lock {caminho} criado em outro host ou ilegível ({host}, pid {pid}); "
                             "confira a operação lá e remova o arquivo à mão")
        if _processo_vivo(pid):
            return OCUPADO, f"o processo {pid} ainda está ativo; a operação {dados.get('operacao')} está em andamento"
        caminho.unlink()
        avisos.append(f"lock abandonado removido (pid {pid} encerrado)")
    try:
        diario = ler_diario(diario_dir)
    except SincroniaErro as exc:
        return exc.codigo, str(exc)
    if not diario or diario.get("concluida"):
        return OK, "; ".join(avisos + ["nada a recuperar"])
    if abandonar:
        diario.update(concluida=True, resultado="abandonada")
        _gravar_diario(diario_dir, diario)
        return OK, "; ".join(avisos + [f"operação {diario['id']} encerrada sem escrita; rode 'verificar'"])
    codigo, mensagem = _retomar(raiz, diario_dir, diario, desfazer)
    return codigo, "; ".join(avisos + [mensagem])


def _titulos_h2(texto: str) -> list[tuple[str, int]]:
    """Títulos ``##`` (fora de cerca) com o número de linhas de cada seção."""
    linhas = texto.split("\n")
    titulos = [(n, l) for n, l in _titulos_fora_de_cerca(linhas) if l.startswith("## ")]
    saida = []
    for indice, (numero, linha) in enumerate(titulos):
        fim = titulos[indice + 1][0] if indice + 1 < len(titulos) else len(linhas) + 1
        saida.append((_TITULO.match(linha).group(2), fim - numero))
    return saida


def _normalizar_titulo(titulo: str) -> str:
    return re.sub(r"^\d+(\.\d+)*\.?\s*", "", titulo).strip().lower()


def importar(raiz: Path, de: Path) -> dict:
    """Só lista as seções dos arquivos de ``de`` que não estão no núcleo; não escreve nada.

    Mostra títulos e número de linhas, nunca o conteúdo das seções.
    """
    nucleo_titulos: set[str] = set()
    for nome in ARQUIVOS:
        caminho = raiz / nome
        if caminho.is_file():
            inst = analisar(nome, caminho.read_bytes())
            if not inst.erros:
                nucleo_titulos = {_normalizar_titulo(t) for t, _ in _titulos_h2(inst.nucleo)}
                break
    resultado = {"nucleo_encontrado": bool(nucleo_titulos), "origem": str(de), "fora_do_nucleo": {}}
    for nome in ARQUIVOS:
        caminho = de / nome
        if not caminho.is_file():
            continue
        texto = _decodificar(caminho.read_bytes())
        resultado["fora_do_nucleo"][nome] = [
            {"titulo": titulo, "linhas": linhas}
            for titulo, linhas in _titulos_h2(texto) if _normalizar_titulo(titulo) not in nucleo_titulos
        ]
    return resultado


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sincronia do núcleo comum de CLAUDE.md, AGENTS.md e PROJECT.md")
    parser.add_argument("--raiz", type=Path, default=PROJECT_ROOT, help=argparse.SUPPRESS)
    parser.add_argument("--diario-dir", type=Path, default=None, help=argparse.SUPPRESS)
    modos = parser.add_subparsers(dest="modo", required=True)
    p_verificar = modos.add_parser("verificar", help="confere os três núcleos e o lock (não escreve)")
    p_verificar.add_argument("--staged", action="store_true", help="lê o índice do Git (hook pre-commit)")
    modos.add_parser("sincronizar", help="propaga o núcleo alterado e atualiza o lock")
    p_recuperar = modos.add_parser("recuperar", help="lock abandonado ou operação interrompida")
    grupo = p_recuperar.add_mutually_exclusive_group()
    grupo.add_argument("--desfazer", action="store_true", help="volta os arquivos ao estado anterior à operação")
    grupo.add_argument("--abandonar", action="store_true", help="encerra a operação sem escrever")
    p_importar = modos.add_parser("importar", help="lista seções de instruções antigas fora do núcleo")
    p_importar.add_argument("--de", type=Path, required=True, help="pasta com as instruções antigas")
    args = parser.parse_args(argv)

    raiz = args.raiz.resolve()
    if args.modo == "importar":
        print(json.dumps(importar(raiz, args.de), ensure_ascii=False, indent=2))
        return OK
    if args.modo == "verificar":
        codigo, mensagem = verificar(raiz, args.staged)
    elif args.modo == "sincronizar":
        codigo, mensagem = sincronizar(raiz, args.diario_dir)
    else:
        codigo, mensagem = recuperar(raiz, args.diario_dir, args.desfazer, args.abandonar)
    print(mensagem, file=sys.stdout if codigo == OK else sys.stderr)
    return codigo


if __name__ == "__main__":
    raise SystemExit(main())
