"""Aquisição nacional única entregue por piloto (H8-a, plano §7.2, L7).

O A1 é simulado: grava no staging um A2 "nacional" sintético com unidades de vários
pilotos e de fora deles. O teste confere que o A1 roda uma vez, que cada piloto
recebe só as suas linhas e que nada nacional é persistido.
"""
from __future__ import annotations

import csv
import subprocess
from pathlib import Path

import pytest

import lib.indicator_extraction as extracao

pytestmark = pytest.mark.regression

DATA = "2026-09-26"
LINHAS = ["CGOV", "DIV-CGOV", "COCAGE", "GR2", "UC-A2", "UC-DUP", "GR1", "UC-FORA"]


@pytest.fixture
def saida(tmp_path, monkeypatch):
    base = tmp_path / "entregas"
    monkeypatch.setenv("PGD_INDICATOR_OUTPUT_BASE", str(base))
    chamadas = []

    def a1_simulado(command, **kwargs):
        chamadas.append(command)
        staging = Path(kwargs["env"]["PGD_INDICATOR_OUTPUT_BASE"]) / command[command.index("--month") + 1]
        staging.mkdir(parents=True, exist_ok=True)
        with (staging / "IND_OCDE_02.2_taxa_cumprimento_temporal_20260926_1200.csv").open("w", encoding="utf-8-sig", newline="") as s:
            escritor = csv.writer(s, delimiter="|")
            escritor.writerow(["unidade_sigla", "unidade_nome", "taxa_cumprimento_perc"])
            escritor.writerows([sigla, sigla, "50.0"] for sigla in LINHAS)
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(extracao.subprocess, "run", a1_simulado)
    return base, chamadas


def _siglas(caminho: Path) -> list[str]:
    with caminho.open(encoding="utf-8-sig", newline="") as s:
        return sorted(linha["unidade_sigla"] for linha in csv.DictReader(s, delimiter="|"))


def test_um_a1_e_tres_entregas_filtradas_sem_persistir_o_nacional(saida):
    base, chamadas = saida
    resultado = extracao.run(["--data-execucao", DATA, "--pilotos", "--so", "I02", "--salvar-manifesto"])

    assert len(chamadas) == 1
    assert resultado["aquisicao"]["modo"] == "nacional_unica_por_pilotos"
    por_chave = {m["escopo"]["chave"]: m for m in resultado["manifestos_por_piloto"]}
    assert set(por_chave) == {"unidade-cgov", "unidade-cocage", "regional-gr2"}
    assert {m["run_id"] for m in por_chave.values()} == {resultado["run_id"]}

    escopos = base / "2026-09" / "escopos"
    assert sorted(p.name for p in escopos.iterdir()) == ["regional-gr2", "unidade-cgov", "unidade-cocage"]
    arquivo = "IND_OCDE_02.2_taxa_cumprimento_temporal_20260926_1200.csv"
    assert _siglas(escopos / "unidade-cgov" / arquivo) == ["CGOV"]
    assert _siglas(escopos / "unidade-cocage" / arquivo) == ["COCAGE"]
    assert _siglas(escopos / "regional-gr2" / arquivo) == ["GR2", "UC-A2", "UC-DUP"]
    assert not list((base / "2026-09").glob("IND_OCDE_*.csv"))  # nada nacional fora dos escopos
    for chave in por_chave:
        assert (escopos / chave / "manifesto_extracao_indicadores_parcial_{}.json".format(resultado["run_id"])).is_file()


def test_escopo_unico_mantem_o_formato_anterior(saida):
    _, chamadas = saida
    resultado = extracao.run(["--data-execucao", DATA, "--unidade", "CGOV", "--so", "I02"])

    assert len(chamadas) == 1
    assert resultado["tipo"] == "extracao_indicadores_ocde" and resultado["escopo"]["chave"] == "unidade-cgov"
    assert resultado["aquisicao"]["modo"] == "nacional"
