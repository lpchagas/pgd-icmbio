"""Replay offline de produção (tools/replay_producao.py), começando pelo I02.

Cada teste roda o A1 real em subprocesso, com I/O substituído por fixtures
sintéticas. Os controles negativos alteram uma dependência de produção sem
tocar no A1 e exigem que o replay acuse a divergência.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tools import replay_producao as rp

DATA = "2026-09-13"
REFERENCIA = "git:HEAD"

pytestmark = pytest.mark.skipif(
    subprocess.run(["git", "-C", str(rp.PROJECT_ROOT), "rev-parse", "--verify", "HEAD"], capture_output=True).returncode != 0,
    reason="replay exige o repositório Git com HEAD",
)


def _copia(tmp_path: Path) -> Path:
    raiz, _ = rp.materializar(REFERENCIA, tmp_path / "candidato")
    return raiz


def _alterar(arquivo: Path, antes: str, depois: str) -> None:
    texto = arquivo.read_text(encoding="utf-8")
    assert texto.count(antes) == 1, f"trecho a alterar não encontrado em {arquivo.name}"
    arquivo.write_text(texto.replace(antes, depois), encoding="utf-8")


def _tipos(relatorio: dict) -> set[str]:
    return {d["tipo"] for d in relatorio.get("diferencas", [])}


def test_normalizacao_remove_so_diretorio_temporario_e_carimbo(tmp_path):
    saida = tmp_path / "saida"
    arquivo = saida / "2026-09" / "IND_OCDE_02.2_taxa_20260913_0959.csv"
    texto = f"Arquivo salvo: {arquivo}\nConcluido.\n"

    assert rp.normalizar_saida(texto, saida) == "Arquivo salvo: <SAIDA>/2026-09/IND_OCDE_02.2_taxa_<carimbo>.csv\nConcluido.\n"
    assert rp.normalizar_nome("IND_OCDE_02.2_taxa_20260913_1000.csv") == "IND_OCDE_02.2_taxa_<carimbo>.csv"
    assert rp.normalizar_nome("IND_OCDE_02.2_v1_20260913.csv") == "IND_OCDE_02.2_v1_20260913.csv"


def test_i02_referencia_contra_ela_mesma_e_equivalente():
    relatorio = rp.replay("I02", REFERENCIA, REFERENCIA, DATA)

    assert relatorio["status"] == "equivalente", relatorio
    assert relatorio["referencia"]["consultas"] == 4
    assert relatorio["referencia"]["arquivos"] == ["2026-09/IND_OCDE_02.2_taxa_cumprimento_temporal_<carimbo>.csv"]
    assert {"lib/csv_utils.py", "lib/estrutura_organizacional.py", "lib/periodos.py"} <= set(relatorio["referencia"]["modulos"])
    assert relatorio["dependencias"] == {"so_referencia": [], "so_candidato": [], "hash_alterado": [], "a1_alterado": False}


def test_i02_arvore_de_trabalho_equivale_ao_head():
    relatorio = rp.replay("I02", REFERENCIA, str(rp.PROJECT_ROOT), DATA)

    assert relatorio["status"] == "equivalente", relatorio


def test_i02_artefato_preserva_bom_delimitador_e_mesogrupo(tmp_path):
    raiz = _copia(tmp_path)
    execucao = rp.executar(raiz, "I02", DATA, rp.FIXTURES_DIR / "I02", tmp_path / "trabalho")
    rp._validar_execucao("referencia", execucao, rp.FIXTURES_DIR / "I02")
    (arquivo,) = execucao["arquivos"].values()
    dados = arquivo.read_bytes()
    cabecalho, linhas = rp._ler_csv(dados)

    assert dados.startswith(b"\xef\xbb\xbf")
    assert b"|" in dados.splitlines()[0]
    assert cabecalho[cabecalho.index("unidade_nome") + 1] == "mesogrupo"
    mesogrupos = {linha[cabecalho.index("unidade_sigla")]: linha[cabecalho.index("mesogrupo")] for linha in linhas}
    assert mesogrupos == {
        "CGSIN": "Meso Sintético A",      # nível 1: dicionário -> icmbio_id
        "NGI-SINT": "Meso Sintético B",   # nível 2: sigla direta
        "UNID-NOME": "Meso Sintético C",  # nível 3: nome
        "SEM-MAPA": "Não mapeado",
    }
    assert "Unidade | sem mapa / quebrada" in {linha[cabecalho.index("unidade_nome")] for linha in linhas}


def test_controle_negativo_bom_removido_em_dependencia(tmp_path):
    raiz = _copia(tmp_path)
    _alterar(raiz / "lib" / "csv_utils.py", 'path.open("w", newline="", encoding="utf-8-sig")', 'path.open("w", newline="", encoding="utf-8")')

    relatorio = rp.replay("I02", REFERENCIA, str(raiz), DATA)

    assert relatorio["status"] == "divergente"
    assert "bom" in _tipos(relatorio)
    assert relatorio["dependencias"]["hash_alterado"] == ["lib/csv_utils.py"]
    assert relatorio["dependencias"]["a1_alterado"] is False


def test_controle_negativo_mesogrupo_alterado_em_dependencia(tmp_path):
    raiz = _copia(tmp_path)
    _alterar(raiz / "lib" / "estrutura_organizacional.py",
             "        # Nível 2 — sigla direta contra ICMBIO_estrutura.csv.\n        if sigla_norm and",
             "        # Nível 2 — sigla direta contra ICMBIO_estrutura.csv.\n        if False and sigla_norm and")

    relatorio = rp.replay("I02", REFERENCIA, str(raiz), DATA)

    assert relatorio["status"] == "divergente"
    (linhas,) = [d for d in relatorio["diferencas"] if d["tipo"] == "linhas"]
    assert {tuple(e["chave"]) for e in linhas["exemplos"]} == {("T3-2025", "NGI-SINT"), ("Q1-2026", "NGI-SINT")}
    assert all(e["colunas"] == ["mesogrupo"] for e in linhas["exemplos"])
    assert relatorio["dependencias"]["a1_alterado"] is False


def test_sql_alterada_no_a1_e_divergente_mesmo_com_linhas_iguais(tmp_path):
    raiz = _copia(tmp_path)
    _alterar(raiz / "ocde" / "indicadores" / "IND_OCDE_02.1_run.py",
             "WHEN r.taxa_cumprimento_perc >= 90 THEN", "WHEN r.taxa_cumprimento_perc >= 85 THEN")

    relatorio = rp.replay("I02", REFERENCIA, str(raiz), DATA)

    assert relatorio["status"] == "divergente"
    assert _tipos(relatorio) == {"consulta"}
    assert len(relatorio["diferencas"][0]["periodos"]) == 4


def test_periodo_sem_fixture_e_erro_e_nunca_equivalencia(tmp_path):
    fixtures = tmp_path / "fixtures"
    shutil.copytree(rp.FIXTURES_DIR / "I02", fixtures)
    documento = json.loads((fixtures / "consultas.json").read_text(encoding="utf-8"))
    documento["consultas"] = [c for c in documento["consultas"] if c["periodo"] != "T4-2025"]
    (fixtures / "consultas.json").write_text(json.dumps(documento, ensure_ascii=False), encoding="utf-8")

    relatorio = rp.replay("I02", REFERENCIA, REFERENCIA, DATA, fixtures=fixtures)

    assert relatorio["status"] == "erro"
    assert "ConsultaNaoCongelada" in relatorio["erro"]


def test_cli_retorna_codigo_por_status(tmp_path, capsys):
    saida = tmp_path / "relatorio.json"

    codigo = rp.main(["--alvo", "I02", "--referencia", REFERENCIA, "--candidato", REFERENCIA,
                      "--data-execucao", DATA, "--saida-json", str(saida)])

    assert codigo == 0
    assert json.loads(saida.read_text(encoding="utf-8"))["status"] == "equivalente"
    assert "I02: equivalente" in capsys.readouterr().out


def test_substituicao_bloqueia_env_acervo_privado_rede_e_subprocesso(tmp_path):
    raiz = _copia(tmp_path)
    (raiz / ".env").write_text("DENODO_PASSWORD=sentinela-replay\n", encoding="utf-8")  # pragma: allowlist secret
    (raiz / "artefatos_local").mkdir()
    (raiz / "artefatos_local" / "privado.txt").write_text("privado", encoding="utf-8")
    sonda = tmp_path / "sonda.py"
    sonda.write_text(
        "import socket, subprocess, sys\n"
        "import lib.denodo_config as dc\n"
        "tentativas = {\n"
        "    'env': lambda: open('.env').read(),\n"
        "    'acervo': lambda: open('artefatos_local/privado.txt').read(),\n"
        "    'rede': lambda: socket.create_connection(('127.0.0.1', 9), timeout=1),\n"
        "    'subprocesso': lambda: subprocess.run([sys.executable, '-c', 'pass']),\n"
        "    'jpype': lambda: __import__('jpype'),\n"
        "}\n"
        "for nome, acao in tentativas.items():\n"
        "    try:\n"
        "        acao(); print(nome, 'PERMITIDO')\n"
        "    except (PermissionError, ImportError):\n"
        "        print(nome, 'bloqueado')\n"
        "print('usuario', repr(dc.get_config().user))\n",
        encoding="utf-8",
    )
    env = rp.ambiente_subprocesso(raiz, DATA, rp.FIXTURES_DIR / "I02", tmp_path / "saida", tmp_path / "registro.json")

    processo = subprocess.run([sys.executable, str(sonda)], cwd=raiz, env=env, capture_output=True, text=True, encoding="utf-8")

    assert processo.returncode == 0, processo.stderr
    assert processo.stdout.split("\n")[:5] == ["env bloqueado", "acervo bloqueado", "rede bloqueado", "subprocesso bloqueado", "jpype bloqueado"]
    assert "usuario 'replay'" in processo.stdout
    assert "sentinela-replay" not in processo.stdout + processo.stderr
