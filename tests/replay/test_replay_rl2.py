"""Correções do parecer do L2 (RL2-01 e RL2-02) no replay de produção.

RL2-01: um módulo do projeto carregado de outra árvore (ponte, alias) torna o
replay ``erro``, mesmo com produtos e consultas iguais.
RL2-02: artefatos que só diferem no carimbo nunca são reduzidos a um; a
normalização da saída padrão não altera barras fora do caminho temporário.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tools import replay_producao as rp

DATA = "2026-09-13"
REFERENCIA = "git:HEAD"

pytestmark = pytest.mark.skipif(
    subprocess.run(["git", "-C", str(rp.PROJECT_ROOT), "rev-parse", "--verify", "HEAD"], capture_output=True).returncode != 0,
    reason="replay exige o repositório Git com HEAD",
)


def _copia(tmp_path: Path, nome: str) -> Path:
    raiz, _ = rp.materializar(REFERENCIA, tmp_path / nome)
    return raiz


def _substituir(arquivo: Path, antes: str, depois: str) -> None:
    texto = arquivo.read_text(encoding="utf-8")
    assert texto.count(antes) == 1, f"trecho não encontrado em {arquivo.name}"
    arquivo.write_text(texto.replace(antes, depois), encoding="utf-8")


# --- RL2-01 -----------------------------------------------------------------------------

def test_rl2_01_ponte_que_carrega_dependencia_de_outra_arvore_e_erro(tmp_path):
    candidato = _copia(tmp_path, "candidato")
    outra = _copia(tmp_path, "outra-arvore")
    ponte = candidato / "ocde" / "relatorios" / "privacidade.py"
    origem_externa = outra / "ocde" / "relatorios" / "privacidade.py"
    # Ponte que entrega a implementação de outra árvore com o mesmo nome de módulo:
    # produtos e consultas ficam iguais aos da referência.
    ponte.write_text(
        "import importlib.util, sys\n"
        f"_spec = importlib.util.spec_from_file_location(__name__, {str(origem_externa)!r})\n"
        "_modulo = importlib.util.module_from_spec(_spec)\n"
        "_spec.loader.exec_module(_modulo)\n"
        "sys.modules[__name__] = _modulo\n",
        encoding="utf-8",
    )

    relatorio = rp.replay("G01-compartilhavel", REFERENCIA, str(candidato), DATA)

    assert relatorio["status"] == "erro"
    assert "fora da árvore" in relatorio["erro"] and "ocde.relatorios.privacidade" in relatorio["erro"]


def test_rl2_01_alias_com_outro_nome_tambem_e_detectado(tmp_path):
    candidato = _copia(tmp_path, "candidato")
    outra = _copia(tmp_path, "outra-arvore")
    ponte = candidato / "ocde" / "relatorios" / "textos_execucao.py"
    origem_externa = outra / "ocde" / "relatorios" / "textos_execucao.py"
    ponte.write_text(
        "import importlib.util\n"
        f"_spec = importlib.util.spec_from_file_location('_implementacao_externa', {str(origem_externa)!r})\n"
        "_externo = importlib.util.module_from_spec(_spec)\n"
        "import sys\n"
        "sys.modules['_implementacao_externa'] = _externo\n"
        "_spec.loader.exec_module(_externo)\n"
        "TextSanitizer = _externo.TextSanitizer\n",
        encoding="utf-8",
    )

    relatorio = rp.replay("G02-restrito", REFERENCIA, str(candidato), DATA)

    assert relatorio["status"] == "erro"
    assert "_implementacao_externa" in relatorio["erro"]


def test_rl2_01_dependencia_dentro_da_arvore_candidata_segue_equivalente(tmp_path):
    candidato = _copia(tmp_path, "candidato")

    relatorio = rp.replay("G01-compartilhavel", REFERENCIA, str(candidato), DATA)

    assert relatorio["status"] == "equivalente", relatorio.get("erro")
    assert relatorio["candidato"]["origem"].startswith("diretorio:")


def test_rl2_01_identidade_do_candidato_diretorio_registra_head_e_alteracoes():
    _, identidade = rp.materializar(str(rp.PROJECT_ROOT), Path("."))

    head = subprocess.run(["git", "-C", str(rp.PROJECT_ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    assert identidade.startswith(f"diretorio:{head}")


# --- RL2-02 -----------------------------------------------------------------------------

def test_rl2_02_dois_artefatos_que_colidem_no_candidato_sao_recusados(tmp_path):
    candidato = _copia(tmp_path, "candidato")
    # Segunda emissão idêntica, diferindo só no carimbo: antes era reduzida a uma.
    _substituir(candidato / "ocde" / "indicadores" / "IND_OCDE_02.1_run.py",
                "    write_pipe_csv(output, all_cols or [], all_rows)\n",
                "    write_pipe_csv(output, all_cols or [], all_rows)\n"
                "    write_pipe_csv(out_dir / 'IND_OCDE_02.2_taxa_cumprimento_temporal_20000101_0000.csv',"
                " all_cols or [], all_rows)\n")

    relatorio = rp.replay("I02", REFERENCIA, str(candidato), DATA)

    assert relatorio["status"] == "erro"
    assert "colidem" in relatorio["erro"] and "IND_OCDE_02.2_taxa_cumprimento_temporal_<carimbo>.csv" in relatorio["erro"]


def test_rl2_02_coletor_separa_colisoes_e_mantem_emissao_unica(tmp_path):
    saida = tmp_path / "saida" / "2026-09"
    saida.mkdir(parents=True)
    (saida / "A_20260913_1000.csv").write_bytes(b"x")
    (saida / "A_20260913_1001.csv").write_bytes(b"y")
    (saida / "B_20260913_1000.csv").write_bytes(b"z")

    arquivos, colisoes = rp.coletar_arquivos(tmp_path / "saida")

    assert list(arquivos) == ["2026-09/B_<carimbo>.csv"]
    assert colisoes == [{"normalizado": "2026-09/A_<carimbo>.csv",
                         "fisicos": ["2026-09/A_20260913_1000.csv", "2026-09/A_20260913_1001.csv"]}]


def test_rl2_02_emissao_unica_por_lado_com_carimbos_diferentes_e_equivalente(tmp_path):
    referencia = tmp_path / "r" / "saida"
    candidato = tmp_path / "c" / "saida"
    for raiz, carimbo in ((referencia, "1000"), (candidato, "1001")):
        (raiz / "2026-09").mkdir(parents=True)
        (raiz / "2026-09" / f"X_20260913_{carimbo}.csv").write_bytes(b"coluna\nigual\n")

    arquivos_ref, colisoes_ref = rp.coletar_arquivos(referencia)
    arquivos_cand, colisoes_cand = rp.coletar_arquivos(candidato)

    assert colisoes_ref == colisoes_cand == []
    assert list(arquivos_ref) == list(arquivos_cand) == ["2026-09/X_<carimbo>.csv"]


def test_rl2_02_normalizacao_so_uniformiza_barras_no_caminho_temporario(tmp_path):
    saida = tmp_path / "saida"
    arquivo = saida / "2026-09" / "IND_OCDE_02.2_taxa_20260913_0959.csv"
    texto = f"Arquivo salvo: {arquivo}\nvalor A\\B\n"

    normalizado = rp.normalizar_saida(texto, saida)

    assert normalizado == "Arquivo salvo: <SAIDA>/2026-09/IND_OCDE_02.2_taxa_<carimbo>.csv\nvalor A\\B\n"
    assert rp.normalizar_saida("valor A\\B", saida) != rp.normalizar_saida("valor A/B", saida)
