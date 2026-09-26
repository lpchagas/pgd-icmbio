"""Gate de liberação pelos comandos oficiais (plano §7.4, L5).

Os negativos passam pelas entradas oficiais, não só pela função: ``gestao.runner``,
``lib.ciclo_gerencial``, ``lib.indicator_extraction``, o executor de pilotos e a CLI
de registro de aceites. Os relatórios V2 e cumulativo (e suas pontes antigas) são
exercitados em ``test_pontes_relatorios.py``. Nenhum teste abre Denodo.
"""
from __future__ import annotations

import json
from dataclasses import replace

import pytest

import gestao.runner as runner_gestao
import lib.ciclo_gerencial as ciclo
import lib.indicator_extraction as extracao
from lib import liberacao
from tools import executar_pilotos, registrar_aceite_piloto

pytestmark = pytest.mark.regression

DATA = "2026-09-13"


@pytest.fixture(autouse=True)
def registro_isolado(tmp_path, monkeypatch):
    monkeypatch.setattr(liberacao, "ARQUIVO_ACEITES", tmp_path / "aceites.json")


def test_gestao_runner_recusa_compartilhavel_nacional():
    with pytest.raises(liberacao.LiberacaoRecusada, match="gestao.runner"):
        runner_gestao.run(["--data-execucao", DATA, "--escopo", "nacional", "--produto", "compartilhavel", "--dry-run"])


def test_ciclo_recusa_final_nacional_antes_de_qualquer_etapa(monkeypatch):
    monkeypatch.setattr(ciclo, "_preflight", lambda *a: pytest.fail("etapa executada apesar da recusa"))
    with pytest.raises(liberacao.LiberacaoRecusada, match="lib.ciclo_gerencial"):
        ciclo.run(["--data-execucao", DATA, "--escopo", "nacional", "--produto", "restrito"])


def test_ciclo_dry_run_registra_a_decisao_sem_executar():
    manifesto = ciclo.run(["--data-execucao", DATA, "--escopo", "nacional", "--dry-run"])
    assert manifesto["liberacao"]["autorizada"] is False and manifesto["status_global"] == "dry-run"


def test_ciclo_rascunho_restrito_fora_dos_pilotos_segue_uso_atual():
    manifesto = ciclo.run(["--data-execucao", DATA, "--escopo", "nacional", "--produto", "restrito",
                           "--rascunho", "--dry-run"])
    assert manifesto["liberacao"]["autorizada"] is True


def test_extracao_registra_liberacao_do_a2_intermediario():
    manifesto = extracao.run(["--data-execucao", DATA, "--so", "I02", "--dry-run"])
    assert manifesto["liberacao"]["autorizada"] is True
    assert manifesto["liberacao"]["produto"] == "intermediario"


def test_executor_recusa_modo_real_sem_cadastro_conferido(capsys):
    assert executar_pilotos.main(["--capacidade", "I02", "--data-execucao", DATA, "--modo", "real"]) == 1
    assert "não conferido" in capsys.readouterr().out


def test_executor_dry_run_separa_resultados_por_piloto_sem_agregado(monkeypatch):
    chamadas = []
    monkeypatch.setattr(executar_pilotos, "_executar", lambda linha: chamadas.append(linha) or {
        "returncode": 0, "status": "dry-run", "liberacao": None, "manifesto": "", "erro": ""})
    registro = executar_pilotos.run(["--capacidade", "G01", "--data-execucao", DATA])

    assert [r["piloto"] for r in registro["resultados_por_piloto"]] == ["CGOV", "COCAGE", "GR2"]
    assert registro["total_agregado"] is None
    assert [linha[-3:] for linha in chamadas] == [["--unidade", "CGOV", "--dry-run"], ["--unidade", "COCAGE", "--dry-run"],
                                                  ["--regional", "GR2", "--dry-run"]]
    assert all("status-pt" in linha for linha in chamadas)


def test_executor_ocde_declara_aquisicao_nacional(monkeypatch):
    monkeypatch.setattr(executar_pilotos, "_executar", lambda linha: {
        "returncode": 0, "status": "dry-run", "liberacao": None, "manifesto": "", "erro": ""})
    registro = executar_pilotos.run(["--capacidade", "I05", "--data-execucao", DATA, "--piloto", "cgov"])

    (resultado,) = registro["resultados_por_piloto"]
    assert resultado["escopo_aquisicao"].startswith("nacional") and resultado["escopo_entrega"] == "unidade-cgov"
    assert "--so" in resultado["comando"] and "I05" in resultado["comando"]


def test_registro_recusa_aceite_com_cadastro_nao_conferido(tmp_path, capsys):
    manifesto = tmp_path / "m.json"
    manifesto.write_text("{}", encoding="utf-8")
    codigo = registrar_aceite_piloto.main(["aceite", "--capacidade", "I02", "--piloto", "CGOV", "--manifesto", str(manifesto),
                                           "--evidencia", str(manifesto), "--papel-aprovador", "CGOV"])
    assert codigo == 1 and "não conferido" in capsys.readouterr().out
    assert not liberacao.ARQUIVO_ACEITES.exists()


def test_registro_recusa_candidato_com_alteracoes_locais(tmp_path, monkeypatch, capsys):
    cadastro = liberacao.carregar_cadastro()
    conferido = replace(cadastro, pilotos=tuple(replace(p, conferido=True, id_petrvs="1") for p in cadastro.pilotos))
    monkeypatch.setattr(liberacao, "carregar_cadastro", lambda *a: conferido)
    monkeypatch.setattr(liberacao, "identidade_candidato", lambda c, cad=None: {"alteracoes_locais": True})
    codigo = registrar_aceite_piloto.main(["aceite", "--capacidade", "I02", "--piloto", "CGOV", "--manifesto", "x",
                                           "--evidencia", "x", "--papel-aprovador", "CGOV"])
    assert codigo == 1 and "alterações locais" in capsys.readouterr().out


def test_registro_revoga_e_verifica(tmp_path, monkeypatch, capsys):
    liberacao.ARQUIVO_ACEITES.write_text(json.dumps({"versao": 1, "aceites": [{"id": "abc", "revogado": False}],
                                                     "deliberacoes": []}), encoding="utf-8")
    assert registrar_aceite_piloto.main(["revogar", "--id", "abc", "--motivo", "erro material", "--papel-aprovador", "CGOV"]) == 0
    dados = json.loads(liberacao.ARQUIVO_ACEITES.read_text(encoding="utf-8"))
    assert dados["aceites"][0]["revogado"] is True and dados["aceites"][0]["revogacao"]["motivo"] == "erro material"
    assert registrar_aceite_piloto.main(["revogar", "--id", "abc", "--motivo", "x", "--papel-aprovador", "CGOV"]) == 1

    monkeypatch.setattr(liberacao, "identidade_candidato", lambda c, cad=None: {"capacidade": c})
    capsys.readouterr()
    assert registrar_aceite_piloto.main(["verificar", "--capacidade", "I02"]) == 1
    assert json.loads(capsys.readouterr().out)["elegivel"] is False
