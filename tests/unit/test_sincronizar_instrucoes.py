"""Sincronia do núcleo comum das instruções (tools/sincronizar_instrucoes.py; plano v3 §6)."""
from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
import threading
from pathlib import Path

import pytest

from tools import sincronizar_instrucoes as si

pytestmark = pytest.mark.unit

NUCLEO = (
    "<!-- nucleo-comum:inicio -->\n"
    "## Projeto\n\nRegra comum.\n\n```text\n# comentário em cerca não é título\n```\n"
    "<!-- nucleo-comum:fim -->\n"
)
NUCLEO_NOVO = NUCLEO.replace("Regra comum.", "Regra comum revisada.")
NUCLEO_OUTRO = NUCLEO.replace("Regra comum.", "Outra redação.")
BLOCOS = {
    "CLAUDE.md": "## Mecânica da ferramenta\n\n- Claude.\n",
    "AGENTS.md": "## Skills desta ferramenta\n\n- Codex.\n",
    "PROJECT.md": "## Comandos da ferramenta\n\n- Antigravity.\n",
}


def _arquivo(nome: str, nucleo: str = NUCLEO, bloco: str | None = None) -> str:
    return f"# Instruções — {nome}\n\n{nucleo}\n{BLOCOS[nome] if bloco is None else bloco}"


def _escrever(raiz: Path, nome: str, texto: str) -> None:
    caminho = raiz / nome
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_bytes(texto.encode("utf-8"))


def _repo(tmp_path: Path, nucleos: dict[str, str] | None = None, lock: str | None = NUCLEO) -> Path:
    nucleos = nucleos or {}
    for nome in si.ARQUIVOS:
        _escrever(tmp_path, nome, _arquivo(nome, nucleos.get(nome, NUCLEO)))
    if lock is not None:
        _escrever(tmp_path, si.LOCK_REL, si.conteudo_lock(si._sha(si.normalizar(lock))).decode("utf-8"))
    return tmp_path


def _diario_dir(raiz: Path) -> Path:
    return raiz / si.DIARIO_REL


def _nucleos(raiz: Path) -> set[str]:
    return {si.analisar(n, (raiz / n).read_bytes()).nucleo for n in si.ARQUIVOS}


def _estado(raiz: Path) -> int:
    return si.classificar(si.ler_estado(raiz)).estado


# ----------------------------------------------------------------- normalização e estrutura


def test_normalizar_bom_crlf_espacos_e_quebra_final():
    assert si.normalizar("﻿a  \r\nb\t\r\n\r\n\r\n") == "a\nb\n"
    assert si.normalizar("a\rb") == "a\nb\n"


def test_crlf_e_bom_nao_mudam_o_hash_do_nucleo(tmp_path):
    raiz = _repo(tmp_path)
    texto = "﻿" + _arquivo("AGENTS.md").replace("\n", "\r\n").replace("Regra comum.", "Regra comum.   ")
    _escrever(raiz, "AGENTS.md", texto)

    assert si.verificar(raiz)[0] == si.OK


def test_propagacao_grava_utf8_sem_bom_e_lf(tmp_path):
    raiz = _repo(tmp_path)
    _escrever(raiz, "CLAUDE.md", _arquivo("CLAUDE.md", NUCLEO_NOVO))
    _escrever(raiz, "AGENTS.md", "﻿" + _arquivo("AGENTS.md").replace("\n", "\r\n"))

    assert si.sincronizar(raiz)[0] == si.OK
    bruto = (raiz / "AGENTS.md").read_bytes()
    assert not bruto.startswith(b"\xef\xbb\xbf") and b"\r\n" not in bruto
    assert bruto.decode("utf-8").startswith("# Instruções — AGENTS.md\n")
    assert bruto.decode("utf-8").endswith(BLOCOS["AGENTS.md"])


@pytest.mark.parametrize("texto, trecho", [
    (_arquivo("CLAUDE.md").replace("<!-- nucleo-comum:fim -->\n", ""), "marcadores"),
    (_arquivo("CLAUDE.md") + "\n<!-- nucleo-comum:inicio -->\n", "marcadores"),
    ("# T\n\n<!-- nucleo-comum:fim -->\nx\n<!-- nucleo-comum:inicio -->\n", "fim antes"),
    (_arquivo("CLAUDE.md").replace("<!-- nucleo-comum:inicio -->", "texto <!-- nucleo-comum:inicio -->"),
     "linha própria"),
    ("Texto solto\n" + _arquivo("CLAUDE.md"), "título do arquivo"),
    (_arquivo("CLAUDE.md", bloco="## Regras de negócio\n\n- x\n"), "título não permitido"),
    (_arquivo("CLAUDE.md", bloco="## Mecânica da ferramenta\n\n### Detalhe\n"), "título não permitido"),
    (_arquivo("CLAUDE.md", bloco="## Mecânica da ferramenta\n" + "- linha\n" * 40), "limite 40"),
])
def test_estado_8_estrutura(tmp_path, texto, trecho):
    raiz = _repo(tmp_path)
    _escrever(raiz, "CLAUDE.md", texto)

    codigo, mensagem = si.verificar(raiz)

    assert codigo == si.ERRO and "estado 8" in mensagem and trecho in mensagem
    assert si.sincronizar(raiz)[0] == si.ERRO
    assert not _diario_dir(raiz).exists()


def test_titulo_dentro_de_cerca_no_bloco_nao_conta(tmp_path):
    raiz = _repo(tmp_path)
    _escrever(raiz, "CLAUDE.md", _arquivo("CLAUDE.md", bloco="## Mecânica da ferramenta\n\n```text\n# x\n```\n"))

    assert si.verificar(raiz)[0] == si.OK


def test_bloco_com_40_linhas_e_aceito(tmp_path):
    raiz = _repo(tmp_path)
    _escrever(raiz, "CLAUDE.md", _arquivo("CLAUDE.md", bloco="## Mecânica da ferramenta\n" + "- l\n" * 39))

    assert si.verificar(raiz)[0] == si.OK


def test_arquivo_ausente_e_utf8_invalido(tmp_path):
    raiz = _repo(tmp_path)
    (raiz / "PROJECT.md").unlink()
    (raiz / "AGENTS.md").write_bytes(b"# T\n\xff\xfe")

    codigo, mensagem = si.verificar(raiz)

    assert codigo == si.ERRO and "PROJECT.md: ausente" in mensagem and "UTF-8" in mensagem


@pytest.mark.parametrize("conteudo", [
    "{\"versao\": 1}",
    "{\"nucleo\": \"abc\"}",
    "{\"nucleo\": \"" + "a" * 64 + "\"}",  # sem o prefixo sha256:
    "não é json",
])
def test_lock_invalido_e_erro(tmp_path, conteudo):
    raiz = _repo(tmp_path)
    _escrever(raiz, si.LOCK_REL, conteudo)

    assert si.verificar(raiz)[0] == si.ERRO


def test_lock_nao_dispara_detect_secrets(tmp_path):
    detect_secrets = pytest.importorskip("detect_secrets")
    from detect_secrets.settings import default_settings

    raiz = _repo(tmp_path)
    segredos = detect_secrets.SecretsCollection()
    with default_settings():
        segredos.scan_file(str(raiz / si.LOCK_REL))

    assert not segredos.json()


# ----------------------------------------------------------------- os 8 estados


def test_estado_1_ok_e_sincronizar_nao_escreve(tmp_path):
    raiz = _repo(tmp_path)
    antes = {n: (raiz / n).read_bytes() for n in si.ARQUIVOS}

    assert si.verificar(raiz) == (si.OK, "ok: núcleo idêntico nos três arquivos e igual ao lock (estado 1)")
    assert si.sincronizar(raiz) == (si.OK, "nada a fazer (estado 1)")
    assert {n: (raiz / n).read_bytes() for n in si.ARQUIVOS} == antes
    assert not _diario_dir(raiz).exists()


def test_estado_2_lock_desatualizado(tmp_path):
    raiz = _repo(tmp_path, lock=NUCLEO_OUTRO)

    codigo, mensagem = si.verificar(raiz)
    assert codigo == si.FALHA and "estado 2" in mensagem

    assert si.sincronizar(raiz)[0] == si.OK
    assert si.ler_lock((raiz / si.LOCK_REL).read_bytes()) == si._sha(si.normalizar(NUCLEO))
    assert si.verificar(raiz)[0] == si.OK


def test_estado_3_lock_ausente_e_iguais_cria_lock(tmp_path):
    raiz = _repo(tmp_path, lock=None)

    codigo, mensagem = si.verificar(raiz)
    assert codigo == si.FALHA and "estado 3" in mensagem

    assert si.sincronizar(raiz)[0] == si.OK
    lock = json.loads((raiz / si.LOCK_REL).read_text(encoding="utf-8"))
    assert lock["arquivos"] == list(si.ARQUIVOS) and lock["versao"] == si.LOCK_VERSAO
    assert si.verificar(raiz)[0] == si.OK


def test_estado_4_lock_ausente_e_divergentes(tmp_path):
    raiz = _repo(tmp_path, {"AGENTS.md": NUCLEO_NOVO}, lock=None)

    codigo, mensagem = si.verificar(raiz)
    assert codigo == si.CONFLITO and "estado 4" in mensagem

    codigo, mensagem = si.sincronizar(raiz)
    assert codigo == si.CONFLITO and "Nada foi escrito" in mensagem
    assert not (raiz / si.LOCK_REL).exists()
    relatorios = list(_diario_dir(raiz).glob("conflito-*.md"))
    assert len(relatorios) == 1 and "Regra comum revisada." in relatorios[0].read_text(encoding="utf-8")


@pytest.mark.parametrize("origem", si.ARQUIVOS)
def test_estado_5_propaga_o_divergente_de_qualquer_arquivo(tmp_path, origem):
    raiz = _repo(tmp_path, {origem: NUCLEO_NOVO})
    blocos = {n: (raiz / n).read_text(encoding="utf-8").split("<!-- nucleo-comum:fim -->")[1] for n in si.ARQUIVOS}

    codigo, mensagem = si.verificar(raiz)
    assert codigo == si.FALHA and "estado 5" in mensagem and origem in mensagem

    codigo, mensagem = si.sincronizar(raiz)
    assert codigo == si.OK, mensagem
    assert _nucleos(raiz) == {si.normalizar(NUCLEO_NOVO)}
    assert {n: (raiz / n).read_text(encoding="utf-8").split("<!-- nucleo-comum:fim -->")[1]
            for n in si.ARQUIVOS} == blocos
    assert si.verificar(raiz)[0] == si.OK
    diario = si.ler_diario(_diario_dir(raiz))
    assert diario["concluida"] and diario["resultado"] == "aplicada" and diario["origem"] == origem
    assert not (_diario_dir(raiz) / si.EXCLUSAO_NOME).exists()


def test_estado_6_sem_diario_e_conflito(tmp_path):
    raiz = _repo(tmp_path, {"CLAUDE.md": NUCLEO_NOVO, "AGENTS.md": NUCLEO_NOVO})

    codigo, mensagem = si.verificar(raiz)
    assert codigo == si.FALHA and "estado 6" in mensagem

    codigo, mensagem = si.sincronizar(raiz)
    assert codigo == si.CONFLITO and "sem diário" in mensagem
    assert (raiz / "PROJECT.md").read_text(encoding="utf-8") == _arquivo("PROJECT.md")


@pytest.mark.parametrize("nucleos", [
    {"CLAUDE.md": NUCLEO_NOVO, "AGENTS.md": NUCLEO_OUTRO},
    {"CLAUDE.md": NUCLEO_NOVO, "AGENTS.md": NUCLEO_OUTRO, "PROJECT.md": NUCLEO_OUTRO + "\nMais.\n"},
])
def test_estado_7_conflito(tmp_path, nucleos):
    raiz = _repo(tmp_path, nucleos)
    antes = {n: (raiz / n).read_bytes() for n in si.ARQUIVOS}

    assert si.verificar(raiz)[0] == si.CONFLITO
    codigo, _ = si.sincronizar(raiz)

    assert codigo == si.CONFLITO
    assert {n: (raiz / n).read_bytes() for n in si.ARQUIVOS} == antes
    assert list(_diario_dir(raiz).glob("conflito-*.md"))


def test_idempotencia(tmp_path):
    raiz = _repo(tmp_path, {"PROJECT.md": NUCLEO_NOVO})

    assert si.sincronizar(raiz)[0] == si.OK
    depois = {n: (raiz / n).read_bytes() for n in [*si.ARQUIVOS, si.LOCK_REL]}
    assert si.sincronizar(raiz) == (si.OK, "nada a fazer (estado 1)")
    assert {n: (raiz / n).read_bytes() for n in [*si.ARQUIVOS, si.LOCK_REL]} == depois


# ----------------------------------------------------------------- queda, recuperação e CAS


def _quebrar_apos(monkeypatch, n_escritas: int, excecao: type[BaseException] = RuntimeError):
    """Simula queda: a (n+1)-ésima escrita de arquivo de instrução ou lock falha."""
    original = si.escrever_atomico
    contador = {"n": 0}

    def escrever(caminho, dados):
        if caminho.name in (*si.ARQUIVOS, Path(si.LOCK_REL).name):
            if contador["n"] >= n_escritas:
                raise excecao("queda simulada")
            contador["n"] += 1
        original(caminho, dados)

    monkeypatch.setattr(si, "escrever_atomico", escrever)


def test_queda_entre_escritas_deixa_estado_6_e_recuperar_retoma(tmp_path, monkeypatch):
    raiz = _repo(tmp_path, {"CLAUDE.md": NUCLEO_NOVO})
    _quebrar_apos(monkeypatch, 1)

    with pytest.raises(RuntimeError):
        si.sincronizar(raiz)
    monkeypatch.undo()

    assert _estado(raiz) == 6
    assert (_diario_dir(raiz) / si.EXCLUSAO_NOME).exists()  # lock mantido na queda
    # o processo "morto" é este; simula-se outro pid já encerrado
    exclusao = _diario_dir(raiz) / si.EXCLUSAO_NOME
    dados = json.loads(exclusao.read_text(encoding="utf-8"))
    dados["pid"] = _pid_encerrado()
    exclusao.write_text(json.dumps(dados), encoding="utf-8")
    assert si.sincronizar(raiz)[0] == si.OCUPADO

    codigo, mensagem = si.recuperar(raiz)

    assert codigo == si.OK, mensagem
    assert "lock abandonado removido" in mensagem and "retomada" in mensagem
    assert si.verificar(raiz)[0] == si.OK
    assert _nucleos(raiz) == {si.normalizar(NUCLEO_NOVO)}


def test_queda_antes_do_lock_e_retomada_pelo_sincronizar(tmp_path, monkeypatch):
    raiz = _repo(tmp_path, {"CLAUDE.md": NUCLEO_NOVO})
    _quebrar_apos(monkeypatch, 2)
    with pytest.raises(RuntimeError):
        si.sincronizar(raiz)
    monkeypatch.undo()
    assert _estado(raiz) == 2
    (_diario_dir(raiz) / si.EXCLUSAO_NOME).unlink()  # lock removido à mão depois de conferido

    codigo, mensagem = si.sincronizar(raiz)

    assert codigo == si.OK and "retomada" in mensagem
    assert si.verificar(raiz)[0] == si.OK


def test_recuperar_desfazer_volta_ao_estado_anterior(tmp_path, monkeypatch):
    raiz = _repo(tmp_path, {"AGENTS.md": NUCLEO_NOVO})
    antes = {n: (raiz / n).read_bytes() for n in [*si.ARQUIVOS, si.LOCK_REL]}
    _quebrar_apos(monkeypatch, 1)
    with pytest.raises(RuntimeError):
        si.sincronizar(raiz)
    monkeypatch.undo()
    (_diario_dir(raiz) / si.EXCLUSAO_NOME).unlink()

    codigo, mensagem = si.recuperar(raiz, desfazer=True)

    assert codigo == si.OK and "desfeita" in mensagem
    assert {n: (raiz / n).read_bytes() for n in [*si.ARQUIVOS, si.LOCK_REL]} == antes
    assert _estado(raiz) == 5


def test_desfazer_remove_lock_que_nao_existia(tmp_path, monkeypatch):
    raiz = _repo(tmp_path, lock=None)
    diario_dir = _diario_dir(raiz)
    assert si.sincronizar(raiz)[0] == si.OK
    diario = si.ler_diario(diario_dir)
    diario.update(concluida=False)
    si._gravar_diario(diario_dir, diario)

    assert si.recuperar(raiz, desfazer=True)[0] == si.OK
    assert not (raiz / si.LOCK_REL).exists()


def test_recuperar_abandonar_encerra_sem_escrever(tmp_path, monkeypatch):
    raiz = _repo(tmp_path, {"AGENTS.md": NUCLEO_NOVO})
    _quebrar_apos(monkeypatch, 1)
    with pytest.raises(RuntimeError):
        si.sincronizar(raiz)
    monkeypatch.undo()
    (_diario_dir(raiz) / si.EXCLUSAO_NOME).unlink()
    antes = {n: (raiz / n).read_bytes() for n in si.ARQUIVOS}

    codigo, _ = si.recuperar(raiz, abandonar=True)

    assert codigo == si.OK
    assert {n: (raiz / n).read_bytes() for n in si.ARQUIVOS} == antes
    assert si.ler_diario(_diario_dir(raiz))["resultado"] == "abandonada"
    assert si.sincronizar(raiz)[0] == si.CONFLITO  # estado 6 sem diário pendente


def test_compare_and_swap_antes_da_primeira_escrita(tmp_path, monkeypatch):
    raiz = _repo(tmp_path, {"CLAUDE.md": NUCLEO_NOVO})
    original = si._preparar_operacao

    def preparar_e_editar(*args, **kwargs):
        diario = original(*args, **kwargs)
        _escrever(raiz, "PROJECT.md", _arquivo("PROJECT.md") + "\nedição concorrente\n")
        return diario

    monkeypatch.setattr(si, "_preparar_operacao", preparar_e_editar)
    antes_agents = (raiz / "AGENTS.md").read_bytes()

    codigo, mensagem = si.sincronizar(raiz)

    assert codigo == si.CONFLITO and "compare-and-swap" in mensagem and "Nada foi escrito" in mensagem
    assert (raiz / "AGENTS.md").read_bytes() == antes_agents
    assert "edição concorrente" in (raiz / "PROJECT.md").read_text(encoding="utf-8")
    assert si.ler_diario(_diario_dir(raiz))["resultado"] == "recusada"
    assert not (_diario_dir(raiz) / si.EXCLUSAO_NOME).exists()


def test_compare_and_swap_no_meio_deixa_operacao_pendente(tmp_path, monkeypatch):
    raiz = _repo(tmp_path, {"CLAUDE.md": NUCLEO_NOVO})
    original = si.escrever_atomico

    def escrever(caminho, dados):
        original(caminho, dados)
        if caminho.name == "AGENTS.md":  # editor que ignora o lock, logo após a 1ª escrita
            (raiz / "PROJECT.md").write_bytes(b"# editado\n")

    monkeypatch.setattr(si, "escrever_atomico", escrever)

    codigo, mensagem = si.sincronizar(raiz)

    assert codigo == si.CONFLITO and "pendente" in mensagem
    assert (raiz / "PROJECT.md").read_bytes() == b"# editado\n"
    assert not (_diario_dir(raiz) / si.EXCLUSAO_NOME).exists()
    monkeypatch.undo()
    assert si.recuperar(raiz)[0] == si.CONFLITO  # nem retoma nem sobrescreve a edição


# ----------------------------------------------------------------- lock de exclusão


def _pid_encerrado() -> int:
    processo = subprocess.Popen([sys.executable, "-c", "pass"])
    processo.wait()
    return processo.pid


def _criar_exclusao(raiz: Path, pid: int, host: str | None = None) -> Path:
    caminho = _diario_dir(raiz) / si.EXCLUSAO_NOME
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps({"pid": pid, "host": host or socket.gethostname(), "operacao": "x",
                                   "criado_em": "2000-01-01T00:00:00"}), encoding="utf-8")
    return caminho


def test_processo_vivo():
    assert si._processo_vivo(os.getpid())
    assert not si._processo_vivo(_pid_encerrado())
    assert not si._processo_vivo(0)


def test_lock_de_processo_ativo_bloqueia_mesmo_antigo(tmp_path):
    raiz = _repo(tmp_path, {"CLAUDE.md": NUCLEO_NOVO})
    caminho = _criar_exclusao(raiz, os.getpid())

    assert si.sincronizar(raiz)[0] == si.OCUPADO
    codigo, mensagem = si.recuperar(raiz)

    assert codigo == si.OCUPADO and "ainda está ativo" in mensagem
    assert caminho.exists()  # nunca apagado pela idade


def test_lock_de_outro_host_nao_e_removido(tmp_path):
    raiz = _repo(tmp_path)
    caminho = _criar_exclusao(raiz, _pid_encerrado(), host="outro-host-inexistente")

    assert si.recuperar(raiz)[0] == si.OCUPADO
    assert caminho.exists()


def test_lock_abandonado_sem_diario(tmp_path):
    raiz = _repo(tmp_path)
    caminho = _criar_exclusao(raiz, _pid_encerrado())

    codigo, mensagem = si.recuperar(raiz)

    assert codigo == si.OK and "nada a recuperar" in mensagem
    assert not caminho.exists()


def test_concorrencia_uma_so_operacao_adquire(tmp_path):
    diario_dir = tmp_path / "sincronia"
    resultados = []
    barreira = threading.Barrier(8)

    def tentar(i):
        barreira.wait()
        try:
            si.Exclusao(diario_dir, f"op{i}").adquirir()
            resultados.append("ok")
        except si.SincroniaErro as exc:
            resultados.append(exc.codigo)

    threads = [threading.Thread(target=tentar, args=(i,)) for i in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert resultados.count("ok") == 1 and resultados.count(si.OCUPADO) == 7


# ----------------------------------------------------------------- links


def test_hardlink_e_recusado(tmp_path):
    raiz = _repo(tmp_path)
    (raiz / "CLAUDE.md").rename(raiz / "fora.md")
    os.link(raiz / "fora.md", raiz / "CLAUDE.md")

    codigo, mensagem = si.verificar(raiz)

    assert codigo == si.ERRO and "hardlink" in mensagem
    assert si.sincronizar(raiz)[0] == si.ERRO


def test_symlink_e_recusado(tmp_path):
    raiz = _repo(tmp_path)
    (raiz / "AGENTS.md").rename(raiz / "fora.md")
    try:
        os.symlink(raiz / "fora.md", raiz / "AGENTS.md")
    except OSError:
        pytest.skip("symlink exige privilégio neste ambiente")

    codigo, mensagem = si.verificar(raiz)

    assert codigo == si.ERRO and "link" in mensagem


# ----------------------------------------------------------------- índice do Git (hook)


def _git(raiz: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(raiz), *args], check=True, capture_output=True)


def test_verificar_staged_le_o_indice_e_nao_a_arvore(tmp_path):
    raiz = _repo(tmp_path)
    _git(raiz, "init", "-q")
    _git(raiz, "add", *si.ARQUIVOS, si.LOCK_REL)
    assert si.verificar(raiz, staged=True)[0] == si.OK

    _escrever(raiz, "CLAUDE.md", _arquivo("CLAUDE.md", NUCLEO_NOVO))
    assert si.verificar(raiz, staged=True)[0] == si.OK  # alteração não preparada
    assert si.verificar(raiz)[0] == si.FALHA

    _git(raiz, "add", "CLAUDE.md")
    codigo, mensagem = si.verificar(raiz, staged=True)
    assert codigo == si.FALHA and "estado 5" in mensagem


def test_verificar_staged_arquivo_fora_do_indice(tmp_path):
    raiz = _repo(tmp_path)
    _git(raiz, "init", "-q")
    _git(raiz, "add", "CLAUDE.md", "AGENTS.md", si.LOCK_REL)

    codigo, mensagem = si.verificar(raiz, staged=True)

    assert codigo == si.ERRO and "PROJECT.md: ausente no índice" in mensagem


def test_verificar_staged_recusa_link_no_indice(tmp_path):
    raiz = _repo(tmp_path)
    _git(raiz, "init", "-q")
    _git(raiz, "add", *si.ARQUIVOS, si.LOCK_REL)
    blob = subprocess.run(["git", "-C", str(raiz), "hash-object", "-w", "--stdin"], input=b"fora.md",
                          capture_output=True, check=True).stdout.decode().strip()
    _git(raiz, "update-index", "--cacheinfo", f"120000,{blob},AGENTS.md")

    codigo, mensagem = si.verificar(raiz, staged=True)

    assert codigo == si.ERRO and "link no índice" in mensagem


# ----------------------------------------------------------------- hook de pre-commit


HOOK = si.PROJECT_ROOT / ".githooks" / "pre-commit"


def _sh() -> str | None:
    """O ``sh`` que o Git usa para rodar hooks (no Windows, o do Git para Windows)."""
    encontrado = shutil.which("sh")
    if encontrado:
        return encontrado
    execucao = subprocess.run(["git", "--exec-path"], capture_output=True, text=True).stdout.strip()
    candidato = Path(execucao).parents[2] / "bin" / "sh.exe" if execucao else None
    return str(candidato) if candidato and candidato.is_file() else None


def _rodar_hook(raiz: Path) -> int:
    sh = _sh()
    if sh is None:
        pytest.skip("sh indisponível neste ambiente")
    ambiente = {**os.environ, "PGD_PYTHON": sys.executable, "PYTHONPATH": str(si.PROJECT_ROOT)}
    return subprocess.run([sh, str(HOOK)], cwd=raiz, env=ambiente, capture_output=True).returncode


def test_hook_pula_branch_sem_nucleo_versionado(tmp_path):
    raiz = tmp_path
    _git(raiz, "init", "-q")
    _escrever(raiz, "README.md", "# x\n")
    _git(raiz, "add", "README.md")

    assert _rodar_hook(raiz) == 0


def test_hook_so_verifica_o_indice_e_nao_escreve(tmp_path):
    raiz = _repo(tmp_path)
    _git(raiz, "init", "-q")
    _git(raiz, "add", *si.ARQUIVOS, si.LOCK_REL)
    assert _rodar_hook(raiz) == 0

    _escrever(raiz, "CLAUDE.md", _arquivo("CLAUDE.md", NUCLEO_NOVO))
    _git(raiz, "add", "CLAUDE.md")
    antes = {n: (raiz / n).read_bytes() for n in [*si.ARQUIVOS, si.LOCK_REL]}

    assert _rodar_hook(raiz) == si.FALHA
    assert {n: (raiz / n).read_bytes() for n in [*si.ARQUIVOS, si.LOCK_REL]} == antes


def test_hook_nao_pula_quando_o_lock_sai_do_indice(tmp_path):
    raiz = _repo(tmp_path)
    _git(raiz, "init", "-q")
    _git(raiz, "add", *si.ARQUIVOS, si.LOCK_REL)
    subprocess.run(["git", "-C", str(raiz), "-c", "user.name=teste", "-c", "user.email=teste@exemplo.invalid",
                    "commit", "-q", "-m", "base"], check=True, capture_output=True)
    _git(raiz, "rm", "-q", "--cached", *si.ARQUIVOS, si.LOCK_REL)

    assert _rodar_hook(raiz) == si.ERRO  # arquivos ausentes no índice


# ----------------------------------------------------------------- importar e CLI


def test_importar_so_lista_titulos_fora_do_nucleo(tmp_path):
    raiz = _repo(tmp_path)
    antigos = tmp_path / "antigos"
    _escrever(antigos, "CLAUDE.md", "# Antigo\n\n## 1. Projeto\n\ntexto\n\n## 5. Fonte de dados\n\nsegredo=não\n")
    antes = {n: (raiz / n).read_bytes() for n in si.ARQUIVOS}

    resultado = si.importar(raiz, antigos)

    assert resultado["nucleo_encontrado"]
    assert resultado["fora_do_nucleo"] == {"CLAUDE.md": [{"titulo": "5. Fonte de dados", "linhas": 4}]}
    assert "segredo" not in json.dumps(resultado)
    assert {n: (raiz / n).read_bytes() for n in si.ARQUIVOS} == antes


def test_cli_verificar_codigos_de_saida(tmp_path):
    raiz = _repo(tmp_path, {"CLAUDE.md": NUCLEO_NOVO})

    def rodar(*args):
        return subprocess.run([sys.executable, "-m", "tools.sincronizar_instrucoes", "--raiz", str(raiz), *args],
                              cwd=si.PROJECT_ROOT, capture_output=True).returncode

    assert rodar("verificar") == si.FALHA
    assert rodar("sincronizar") == si.OK
    assert rodar("verificar") == si.OK
