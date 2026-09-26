"""Replay offline de produção: A1 de referência × A1 candidato (plano de reorganização, §9.2).

Executa o A1 real de cada árvore num subprocesso, com o mesmo comando do
runner oficial, e substitui só o I/O (ver ``tools/replay_sitecustomize``):
Denodo, ``query_rows`` e planilhas de estrutura servem fixtures sintéticas
congeladas. Não conecta a Denodo nem a MySQL e não lê .env nem artefatos_local/.

Comparação: bytes dos artefatos (nome normalizado só no carimbo de horário);
havendo diferença, detalha BOM, delimitador, cabeçalho e linhas. Também compara
a SQL enviada por período, a saída padrão e colunas pessoais novas.

O resultado é evidência técnica de migração, nunca aceite institucional.

Uso:
  python -m tools.replay_producao --alvo I02 --referencia git:reorg-ponto-zero \
      --candidato . --data-execucao 2026-09-13 [--saida-json caminho]

Origens: ``git:<ref>`` (extraída com git archive, sem tocar no checkout) ou um diretório.
Saída: 0 equivalente · 1 divergente · 2 erro (replay não conclusivo).
"""
from __future__ import annotations

import argparse
import csv
import fnmatch
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
SHIM_DIR = Path(__file__).resolve().parent / "replay_sitecustomize"
FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures" / "replay"

def _ocde(numero: str, periodos: str, fixture: str = "gerada") -> dict[str, object]:
    # Mesmo comando do runner oficial (lib.indicator_extraction).
    return {
        "script": f"ocde/indicadores/IND_OCDE_{numero}.1_run.py", "periodos": periodos, "fixture": fixture,
        "argumentos": ("--data-execucao", "{data}", "--month", "{mes}"),
    }


def _gestao(numero: str, produto: str, *escopo: str) -> dict[str, object]:
    # Mesmo comando do runner oficial (gestao.runner): produto, --out e escopo explícitos.
    return {
        "script": f"gestao/IND_GEST_{numero}/IND_GEST_{numero}.1_run.py", "fixture": "manual",
        "contrato": f"G{numero}", "fixtures": f"G{numero}", "variante": produto,
        "argumentos": ("--data-execucao", "{data}", "--produto", produto, "--out", "{saida}", *escopo),
    }


_UNIDADES_SINTETICAS = ("--unidade", "CGSIN", "--unidade", "NGI-SINT", "--unidade", "UNID-NOME", "--unidade", "SEM-MAPA")

# fixture "gerada": tools/gerar_fixtures_replay.py; "manual": escrita à mão.
# Alvos de gestão rodam por produto: o restrito com lista de unidades, o compartilhável com --todas.
ALVOS: dict[str, dict[str, object]] = {
    "I02": _ocde("02", "pe", fixture="manual"),
    "I03": _ocde("03", "pe"),
    "I04": _ocde("04", "pe"),
    "I05": _ocde("05", "pt"),
    "I06": _ocde("06", "pt"),
    "I07": _ocde("07", "pe"),
    "I09": _ocde("09", "pt"),
    "I10": _ocde("10", "pt"),
    "I11": _ocde("11", "pt"),
    "I12": _ocde("12", "pe"),
    "I01": _ocde("01", "pt", fixture="manual"),
    "I08": _ocde("08", "pe", fixture="manual"),
    "G01-restrito": _gestao("01", "restrito", *_UNIDADES_SINTETICAS),
    "G01-compartilhavel": _gestao("01", "compartilhavel", "--todas"),
    "G02-restrito": _gestao("02", "restrito", "--unidade", "CGSIN", "--unidade", "NGI-SINT"),
    "G02-compartilhavel": _gestao("02", "compartilhavel", "--todas"),
}
_CHAVE_PADRAO = ("periodo", "unidade_sigla")


def pasta_de_fixtures(alvo: str) -> Path:
    return FIXTURES_DIR / str(ALVOS[alvo].get("fixtures", alvo))


def chave_do_arquivo(alvo: str, nome: str) -> tuple[str, ...]:
    """Chaves de negócio do contrato A2 cujo padrão casa com o arquivo."""

    from lib.validation_contracts import TARGETS

    base = nome.rsplit("/", 1)[-1].replace("_<carimbo>", "_00000000_0000")
    for contrato in TARGETS[str(ALVOS[alvo].get("contrato", alvo))].outputs:
        if fnmatch.fnmatch(base, contrato.pattern):
            return tuple(contrato.business_keys)
    return _CHAVE_PADRAO

# Variáveis herdadas pelo subprocesso; credenciais e PGD_* do pai nunca passam.
_AMBIENTE_BASE = ("PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "HOME", "USERPROFILE", "LANG", "LC_ALL")
_CARIMBO = re.compile(r"_\d{8}_\d{4}(?:\d{2})?(?=\.csv\b)")  # HHMM (OCDE, G01) ou HHMMSS (G02)
_COLUNA_PESSOAL = re.compile(r"(^|_)(cpf|email|e_mail|telefone|matricula|nome_servidor|servidor_nome|usuario_nome)($|_)")
_BOM = b"\xef\xbb\xbf"
_EXEMPLOS = 10


class ReplayError(RuntimeError):
    """Replay não conclusivo: nunca é tratado como equivalência."""


def materializar(origem: str, destino: Path) -> tuple[Path, str]:
    """Devolve a raiz a executar e a identidade da origem."""

    if origem.startswith("git:"):
        ref = origem[4:]
        commit = subprocess.run(
            ["git", "-C", str(PROJECT_ROOT), "rev-parse", "--verify", f"{ref}^{{commit}}"],
            capture_output=True, text=True,
        )
        if commit.returncode != 0:
            raise ReplayError(f"ref inexistente: {ref}")
        sha = commit.stdout.strip()
        pacote = subprocess.run(
            ["git", "-C", str(PROJECT_ROOT), "archive", "--format=tar", sha],
            capture_output=True, check=True,
        ).stdout
        destino.mkdir(parents=True, exist_ok=True)
        with tarfile.open(fileobj=io.BytesIO(pacote)) as tar:
            tar.extractall(destino, filter="data")
        return destino, f"git:{sha}"
    raiz = Path(origem).resolve()
    if not (raiz / "lib" / "__init__.py").is_file():
        raise ReplayError(f"diretório sem o pacote lib: {origem}")
    return raiz, "diretorio"


def normalizar_nome(nome: str) -> str:
    return _CARIMBO.sub("_<carimbo>", nome)


def normalizar_saida(texto: str, saida: Path) -> str:
    """Remove da saída padrão só o diretório temporário e o carimbo de horário."""

    for caminho in {str(saida), str(saida).replace("\\", "/")}:
        texto = texto.replace(caminho, "<SAIDA>")
    return _CARIMBO.sub("_<carimbo>", texto.replace("\\", "/"))


def ambiente_subprocesso(
    raiz: Path, data_execucao: str, fixtures: Path, saida: Path, registro: Path, variante: str = "",
) -> dict[str, str]:
    """Ambiente do A1 sob replay: mínimo, com a substituição de I/O ativada."""

    env = {chave: os.environ[chave] for chave in _AMBIENTE_BASE if chave in os.environ}
    env.update({
        "PYTHONPATH": os.pathsep.join([str(SHIM_DIR), str(raiz)]),
        "PYTHONDONTWRITEBYTECODE": "1",
        "PGD_ANALYSIS_EXECUTION_DATE": data_execucao,
        "PGD_OUTPUT_MONTH": data_execucao[:7],
        "PGD_INDICATOR_OUTPUT_BASE": str(saida),
        "PGD_REPLAY_FIXTURES": str(fixtures),
        "PGD_REPLAY_RAIZ": str(raiz),
        "PGD_REPLAY_REGISTRO": str(registro),
        "PGD_REPLAY_VARIANTE": variante,
    })
    return env


def executar(raiz: Path, alvo: str, data_execucao: str, fixtures: Path, trabalho: Path) -> dict:
    """Roda o A1 da raiz com o I/O substituído e devolve o que produziu."""

    script = raiz / str(ALVOS[alvo]["script"])
    if not script.is_file():
        raise ReplayError(f"A1 ausente na origem: {ALVOS[alvo]['script']}")
    saida = trabalho / "saida"
    registro = trabalho / "registro.json"
    variante = str(ALVOS[alvo].get("variante", ""))
    env = ambiente_subprocesso(raiz, data_execucao, fixtures, saida, registro, variante)
    valores = {"data": data_execucao, "mes": data_execucao[:7], "saida": str(saida)}
    argumentos = [str(item).format(**valores) for item in ALVOS[alvo]["argumentos"]]
    processo = subprocess.run(
        [sys.executable, str(script), *argumentos],
        cwd=raiz, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300,
    )
    arquivos = {
        normalizar_nome(caminho.relative_to(saida).as_posix()): caminho
        for caminho in sorted(saida.rglob("*")) if caminho.is_file()
    } if saida.exists() else {}
    dados_registro = json.loads(registro.read_text(encoding="utf-8")) if registro.exists() else None
    return {
        "a1_sha256": hashlib.sha256(script.read_bytes()).hexdigest(),
        "returncode": processo.returncode,
        "stdout": normalizar_saida(processo.stdout, saida),
        "stderr": processo.stderr,
        "arquivos": arquivos,
        "registro": dados_registro,
        "variante": variante,
    }


def _validar_execucao(lado: str, execucao: dict, fixtures: Path) -> None:
    if execucao["returncode"] != 0:
        ultima = (execucao["stderr"].strip().splitlines() or [""])[-1]
        raise ReplayError(f"{lado}: A1 terminou com código {execucao['returncode']}: {ultima}")
    if re.search(r"^\s*ERRO:", execucao["stdout"], re.MULTILINE):
        raise ReplayError(f"{lado}: A1 relatou ERRO e seguiu (falha engolida)")
    registro = execucao["registro"]
    if not registro or not registro.get("ativo"):
        raise ReplayError(f"{lado}: substituição de I/O não foi ativada")
    nao_servidas = [c for c in registro["consultas"] if not c["servida"]]
    if nao_servidas:
        raise ReplayError(f"{lado}: {len(nao_servidas)} consulta(s) sem linhas congeladas")
    variante = execucao.get("variante", "")
    fixture = [
        c for c in json.loads((fixtures / "consultas.json").read_text(encoding="utf-8"))["consultas"]
        if not c.get("variantes") or variante in c["variantes"]
    ]
    identificar = lambda c: (c.get("inicio") or "", c.get("fim") or "", c.get("nome", ""))  # noqa: E731
    esperadas = sorted(map(identificar, fixture))
    servidas = sorted(map(identificar, registro["consultas"]))
    if servidas != esperadas:
        raise ReplayError(f"{lado}: consultas feitas diferem das fixtures (faltam, sobram ou se repetem)")
    if not execucao["arquivos"]:
        raise ReplayError(f"{lado}: nenhum artefato gerado")


def _ler_csv(dados: bytes) -> tuple[list[str], list[list[str]]]:
    texto = dados.decode("utf-8-sig", errors="replace")
    linhas = list(csv.reader(io.StringIO(texto, newline=""), delimiter="|"))
    return (linhas[0] if linhas else []), linhas[1:]


def _comparar_arquivo(nome: str, ref: bytes, cand: bytes, chave: tuple[str, ...]) -> list[dict]:
    if ref == cand:
        return []
    diferencas: list[dict] = []
    if ref.startswith(_BOM) != cand.startswith(_BOM):
        diferencas.append({"tipo": "bom", "arquivo": nome, "referencia": ref.startswith(_BOM), "candidato": cand.startswith(_BOM)})
    cab_ref, linhas_ref = _ler_csv(ref)
    cab_cand, linhas_cand = _ler_csv(cand)
    if cab_ref != cab_cand:
        diferencas.append({"tipo": "cabecalho", "arquivo": nome, "referencia": cab_ref, "candidato": cab_cand})
    if len(linhas_ref) != len(linhas_cand):
        diferencas.append({"tipo": "numero_linhas", "arquivo": nome, "referencia": len(linhas_ref), "candidato": len(linhas_cand)})
    if cab_ref == cab_cand:
        posicoes = [cab_ref.index(c) for c in chave if c in cab_ref]
        unica = all(len({tuple(l[p] for p in posicoes) for l in ls}) == len(ls) for ls in (linhas_ref, linhas_cand))
        if not (posicoes and unica):
            posicoes = []  # chave ausente ou repetida: compara por posição da linha
        indexar = lambda linhas: {tuple(l[p] for p in posicoes) if posicoes else (str(i),): l for i, l in enumerate(linhas)}  # noqa: E731
        por_chave_ref, por_chave_cand = indexar(linhas_ref), indexar(linhas_cand)
        divergentes = []
        for k in sorted(set(por_chave_ref) | set(por_chave_cand)):
            a, b = por_chave_ref.get(k), por_chave_cand.get(k)
            if a == b:
                continue
            colunas = [c for i, c in enumerate(cab_ref) if a is None or b is None or i >= len(a) or i >= len(b) or a[i] != b[i]]
            divergentes.append({"chave": list(k), "colunas": colunas if a and b else ["<linha ausente>"]})
        if divergentes:
            diferencas.append({"tipo": "linhas", "arquivo": nome, "total": len(divergentes), "exemplos": divergentes[:_EXEMPLOS]})
    if not diferencas:
        diferencas.append({"tipo": "bytes", "arquivo": nome, "detalhe": "conteúdo lógico igual; serialização diferente"})
    novas_pessoais = [c for c in cab_cand if _COLUNA_PESSOAL.search(c.lower()) and c not in cab_ref]
    if novas_pessoais:
        diferencas.append({"tipo": "privacidade", "arquivo": nome, "colunas": novas_pessoais})
    return diferencas


def comparar(alvo: str, referencia: dict, candidato: dict) -> tuple[list[dict], dict]:
    diferencas: list[dict] = []
    nomes_ref, nomes_cand = set(referencia["arquivos"]), set(candidato["arquivos"])
    if nomes_ref != nomes_cand:
        diferencas.append({"tipo": "arquivos", "so_referencia": sorted(nomes_ref - nomes_cand), "so_candidato": sorted(nomes_cand - nomes_ref)})
    for nome in sorted(nomes_ref & nomes_cand):
        diferencas += _comparar_arquivo(
            nome, referencia["arquivos"][nome].read_bytes(), candidato["arquivos"][nome].read_bytes(),
            chave_do_arquivo(alvo, nome),
        )
    sql_ref = [(c["inicio"], c["fim"], c["sql_sha256"]) for c in referencia["registro"]["consultas"]]
    sql_cand = [(c["inicio"], c["fim"], c["sql_sha256"]) for c in candidato["registro"]["consultas"]]
    if sql_ref != sql_cand:
        periodos = sorted({f"{a}..{b}" for a, b, _ in set(sql_ref) ^ set(sql_cand)})
        diferencas.append({"tipo": "consulta", "periodos": periodos})
    if referencia["stdout"] != candidato["stdout"]:
        diferencas.append({"tipo": "saida_padrao"})
    mod_ref, mod_cand = referencia["registro"]["modulos"], candidato["registro"]["modulos"]
    dependencias = {
        "so_referencia": sorted(set(mod_ref) - set(mod_cand)),
        "so_candidato": sorted(set(mod_cand) - set(mod_ref)),
        "hash_alterado": sorted(m for m in set(mod_ref) & set(mod_cand) if mod_ref[m] != mod_cand[m]),
        "a1_alterado": referencia["a1_sha256"] != candidato["a1_sha256"],
    }
    return diferencas, dependencias


def replay(alvo: str, referencia: str, candidato: str, data_execucao: str, fixtures: Path | None = None) -> dict:
    """Executa os dois lados e devolve o relatório (status equivalente/divergente/erro)."""

    if alvo not in ALVOS:
        raise ReplayError(f"alvo sem replay configurado: {alvo}")
    fixtures = (fixtures or pasta_de_fixtures(alvo)).resolve()
    relatorio: dict = {"alvo": alvo, "data_execucao": data_execucao, "fixtures": fixtures.name}
    with tempfile.TemporaryDirectory(prefix="pgd-replay-") as tmp:
        base = Path(tmp)
        try:
            execucoes = {}
            for lado, origem in (("referencia", referencia), ("candidato", candidato)):
                raiz, identidade = materializar(origem, base / lado / "arvore")
                execucao = executar(raiz, alvo, data_execucao, fixtures, base / lado)
                relatorio[lado] = {"origem": identidade}
                _validar_execucao(lado, execucao, fixtures)
                relatorio[lado].update({
                    "a1_sha256": execucao["a1_sha256"],
                    "consultas": len(execucao["registro"]["consultas"]),
                    "arquivos": sorted(execucao["arquivos"]),
                    "modulos": execucao["registro"]["modulos"],
                })
                execucoes[lado] = execucao
            diferencas, dependencias = comparar(alvo, execucoes["referencia"], execucoes["candidato"])
        except ReplayError as exc:
            relatorio.update({"status": "erro", "erro": str(exc)})
            return relatorio
    relatorio.update({
        "status": "divergente" if diferencas else "equivalente",
        "diferencas": diferencas,
        "dependencias": dependencias,
    })
    return relatorio


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Replay offline A1 de referência × candidato.")
    parser.add_argument("--alvo", required=True, choices=sorted(ALVOS))
    parser.add_argument("--referencia", required=True, help="git:<ref> ou diretório")
    parser.add_argument("--candidato", required=True, help="git:<ref> ou diretório")
    parser.add_argument("--data-execucao", required=True, help="AAAA-MM-DD, igual para os dois lados")
    parser.add_argument("--saida-json", type=Path, help="grava o relatório completo (fora do Git)")
    args = parser.parse_args(argv)
    relatorio = replay(args.alvo, args.referencia, args.candidato, args.data_execucao)
    if args.saida_json:
        args.saida_json.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{args.alvo}: {relatorio['status']}")
    if relatorio["status"] == "erro":
        print(f"  {relatorio['erro']}")
    for diferenca in relatorio.get("diferencas", []):
        print(f"  - {diferenca['tipo']}: {diferenca.get('arquivo', '')}".rstrip(": "))
    return {"equivalente": 0, "divergente": 1}.get(relatorio["status"], 2)


if __name__ == "__main__":
    sys.exit(main())
