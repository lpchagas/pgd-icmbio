"""Gate de liberação dos pilotos (plano §7.4, L5): cadastro, elegibilidade e recusas."""
from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from lib import liberacao
from relatorios.escopo import ScopeSpec

pytestmark = pytest.mark.unit

IDENTIDADE = {"capacidade": "I02", "versao": "2.0.0", "fingerprint": "f" * 64, "commit": "c" * 40,
              "alteracoes_locais": False, "politica": "pilotos-v1", "cadastro_versao": 1}


def _escopo(piloto: liberacao.Piloto) -> dict:
    return {"sigla": piloto.sigla, "seletor": piloto.seletor, "chave": f"{piloto.seletor}-{piloto.sigla.lower()}",
            "ids": [piloto.sigla], "hierarquia_sha256": "e" * 64}


@pytest.fixture
def acervo(tmp_path, monkeypatch):
    """Raiz temporária com acervo privado; escopo e identidade fixos."""

    monkeypatch.setattr(liberacao, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(liberacao, "ARQUIVO_ACEITES", tmp_path / "artefatos_local" / "validacao" / "pilotos" / "aceites.json")
    monkeypatch.setattr(liberacao, "escopo_resolvido", _escopo)
    monkeypatch.setattr(liberacao, "identidade_candidato", lambda capacidade, cadastro=None: {**IDENTIDADE, "capacidade": capacidade})
    return tmp_path


def _arquivo(raiz: Path, nome: str, conteudo: str) -> dict:
    caminho = raiz / "artefatos_local" / "validacao" / "pilotos" / nome
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(conteudo, encoding="utf-8")
    return liberacao.referencia_arquivo(caminho)


def _manifesto(raiz: Path, piloto: liberacao.Piloto, **extra) -> dict:
    dados = {"tipo": "protocolo_validacao_A1_A5", "modo": "integrado", "status_global": "sucesso",
             "escopo": {"chave": _escopo(piloto)["chave"]}, "resultados": [{"alvo": "I02", "status": "certificado"}], **extra}
    return _arquivo(raiz, f"manifesto-{piloto.sigla}.json", json.dumps(dados))


def _registro(raiz: Path, cadastro: liberacao.Cadastro, **mudancas) -> dict:
    aceites = []
    for piloto in cadastro.pilotos:
        aceites.append({**IDENTIDADE, "piloto": piloto.sigla, "escopo_resolvido": _escopo(piloto),
                        "manifesto": _manifesto(raiz, piloto),
                        "evidencia": _arquivo(raiz, f"ato-{piloto.sigla}.md", f"ato humano {piloto.sigla}"),
                        "revogado": False, **mudancas})
    deliberacao = {**IDENTIDADE, "evidencia": _arquivo(raiz, "deliberacao.md", "deliberação"), "revogado": False}
    return {"versao": 1, "aceites": aceites, "deliberacoes": [deliberacao]}


# --- Cadastro -----------------------------------------------------------------------------

def test_cadastro_versionado_tem_os_tres_pilotos_da_h4_conferidos():
    cadastro = liberacao.carregar_cadastro()

    assert [(p.sigla, p.seletor, p.incluir_subordinadas) for p in cadastro.pilotos] == [
        ("CGOV", "unidade", False), ("COCAGE", "unidade", False), ("GR2", "regional", True)]
    assert cadastro.conferido and all(p.id_petrvs for p in cadastro.pilotos)


def test_conferencia_do_cadastro_contra_a_hierarquia():
    cadastro = liberacao.carregar_cadastro()
    # Na hierarquia sintética os ids são outros: a conferência aponta cada divergência.
    assert [m.split(":")[0] for m in liberacao.problemas_cadastro(cadastro)] == ["CGOV", "COCAGE", "GR2"]
    sinteticos = {"CGOV": "p-cgov", "COCAGE": "p-cocage", "GR2": "p-gr2"}
    conferido = replace(cadastro, pilotos=tuple(replace(p, id_petrvs=sinteticos[p.sigla]) for p in cadastro.pilotos))
    assert liberacao.problemas_cadastro(conferido) == []
    pendente = replace(cadastro, pilotos=(replace(cadastro.pilotos[0], conferido=False), *conferido.pilotos[1:]))
    assert liberacao.problemas_cadastro(pendente) == ["CGOV: id_petrvs não conferido na fonte"]


@pytest.mark.parametrize("mudanca", [
    {"incluir_subordinadas": True},             # unidade com subordinadas: recorte sem suporte
    {"id_petrvs": None},                        # conferido sem id_petrvs
    {"seletor": "mesogrupo"},
])
def test_cadastro_invalido_e_erro(tmp_path, mudanca):
    dados = json.loads(liberacao.CADASTRO.read_text(encoding="utf-8"))
    dados["unidades"][0].update(mudanca)
    caminho = tmp_path / "cadastro.json"
    caminho.write_text(json.dumps(dados), encoding="utf-8")
    with pytest.raises(ValueError):
        liberacao.carregar_cadastro(caminho)


def test_piloto_exige_o_mesmo_recorte_configurado():
    cadastro = liberacao.carregar_cadastro()

    assert liberacao.piloto_do_escopo(ScopeSpec("regional", "GR2"), cadastro).sigla == "GR2"
    assert liberacao.piloto_do_escopo(ScopeSpec("unidade", "CGOV"), cadastro).sigla == "CGOV"
    assert liberacao.piloto_do_escopo(ScopeSpec("regional", "CGOV"), cadastro) is None   # subordinadas de outro jeito
    assert liberacao.piloto_do_escopo(ScopeSpec("unidade", "GR2"), cadastro) is None


# --- Autorização --------------------------------------------------------------------------

@pytest.mark.parametrize("escopo", [ScopeSpec("regional", "GR2"), ScopeSpec("unidade", "COCAGE")])
def test_pilotos_sempre_autorizados(acervo, escopo):
    decisao = liberacao.execucao_autorizada("x", escopo, "compartilhavel", capacidades=["I02"], final=True)
    assert decisao.autorizada and decisao.motivo == "escopo piloto"


def test_fora_dos_pilotos_restrito_nao_final_segue_uso_atual(acervo):
    decisao = liberacao.execucao_autorizada("x", ScopeSpec("nacional", "NACIONAL"), "restrito", capacidades=["I02"])
    assert decisao.autorizada and "uso restrito" in decisao.motivo


@pytest.mark.parametrize("produto, final", [("compartilhavel", False), ("compartilhavel", True), ("restrito", True)])
def test_fora_dos_pilotos_final_ou_compartilhavel_sem_aceites_e_recusado(acervo, produto, final):
    with pytest.raises(liberacao.LiberacaoRecusada, match="sem aceites"):
        liberacao.exigir_execucao_autorizada("x", ScopeSpec("nacional", "NACIONAL"), produto,
                                             capacidades=["I02"], final=final)


def test_fora_dos_pilotos_sem_capacidade_declarada_e_recusado(acervo):
    cadastro = liberacao.carregar_cadastro()
    liberacao.ARQUIVO_ACEITES.parent.mkdir(parents=True, exist_ok=True)
    liberacao.ARQUIVO_ACEITES.write_text(json.dumps(_registro(acervo, cadastro)), encoding="utf-8")
    decisao = liberacao.execucao_autorizada("x", ScopeSpec("nacional", "NACIONAL"), "compartilhavel", final=True)
    assert not decisao.autorizada


def test_tres_aceites_da_mesma_identidade_e_deliberacao_liberam(acervo):
    cadastro = liberacao.carregar_cadastro()
    liberacao.ARQUIVO_ACEITES.parent.mkdir(parents=True, exist_ok=True)
    liberacao.ARQUIVO_ACEITES.write_text(json.dumps(_registro(acervo, cadastro)), encoding="utf-8")

    assert liberacao.elegivel_para_liberacao(IDENTIDADE, cadastro=cadastro) == (True, [])
    decisao = liberacao.execucao_autorizada("x", ScopeSpec("nacional", "NACIONAL"), "compartilhavel",
                                            capacidades=["I02"], final=True, cadastro=cadastro)
    assert decisao.autorizada


# --- Recusas (plano §7.4) -----------------------------------------------------------------

def _motivos(acervo, registro) -> list[str]:
    elegivel, motivos = liberacao.elegivel_para_liberacao(IDENTIDADE, cadastro=liberacao.carregar_cadastro(), registro=registro)
    assert not elegivel
    return motivos


def test_recusa_aceite_revogado(acervo):
    registro = _registro(acervo, liberacao.carregar_cadastro())
    registro["aceites"][0]["revogado"] = True
    assert _motivos(acervo, registro) == ["CGOV: aceite revogado"]


def test_recusa_evidencia_corrompida_ou_ausente(acervo):
    registro = _registro(acervo, liberacao.carregar_cadastro())
    (acervo / registro["aceites"][1]["evidencia"]["caminho"]).write_text("alterado", encoding="utf-8")
    (acervo / registro["aceites"][2]["evidencia"]["caminho"]).unlink()
    motivos = _motivos(acervo, registro)
    assert motivos[0].startswith("COCAGE: evidência corrompida") and motivos[1].startswith("GR2: evidência ausente")


@pytest.mark.parametrize("extra, motivo", [
    ({"modo": "fixture"}, "fixture"),
    ({"tipo": "protocolo_validacao_A1_A5_consolidado"}, "execução nova"),
    ({"status_global": "pendente"}, "sem sucesso"),
    ({"escopo": {"chave": "regional-cgov"}}, "outro escopo"),
])
def test_recusa_manifesto_invalido(acervo, extra, motivo):
    cadastro = liberacao.carregar_cadastro()
    registro = _registro(acervo, cadastro)
    registro["aceites"][0]["manifesto"] = _manifesto(acervo, cadastro.pilotos[0], **extra)
    assert motivo in _motivos(acervo, registro)[0]


def test_recusa_mesma_versao_com_fingerprint_diferente(acervo):
    registro = _registro(acervo, liberacao.carregar_cadastro(), fingerprint="0" * 64)
    assert all("mesma versão de fórmula com fingerprint diferente" in m for m in _motivos(acervo, registro)[:3])


def test_recusa_candidato_diferente(acervo):
    registro = _registro(acervo, liberacao.carregar_cadastro(), versao="3.0.0", fingerprint="0" * 64)
    assert "candidato diferente (versão)" in _motivos(acervo, registro)[0]


def test_recusa_escopo_resolvido_diferente_sem_heranca(acervo):
    registro = _registro(acervo, liberacao.carregar_cadastro())
    registro["aceites"][2]["escopo_resolvido"] = {**registro["aceites"][2]["escopo_resolvido"], "ids": ["GR2", "UC-NOVA"]}
    assert _motivos(acervo, registro) == ["GR2: escopo resolvido mudou (hierarquia ou subordinação)"]


def test_recusa_sem_deliberacao(acervo):
    registro = _registro(acervo, liberacao.carregar_cadastro())
    registro["deliberacoes"][0]["revogado"] = True
    assert _motivos(acervo, registro) == ["sem deliberação de expansão válida para esta identidade"]


def test_recusa_registro_corrompido(acervo):
    liberacao.ARQUIVO_ACEITES.parent.mkdir(parents=True, exist_ok=True)
    liberacao.ARQUIVO_ACEITES.write_text("{", encoding="utf-8")
    assert liberacao.elegivel_para_liberacao(IDENTIDADE, cadastro=liberacao.carregar_cadastro()) == (
        False, ["registro de aceites corrompido"])


def test_evidencia_publica_e_recusada(acervo):
    publico = acervo / "docs" / "ato.md"
    publico.parent.mkdir(parents=True)
    publico.write_text("ato", encoding="utf-8")
    with pytest.raises(ValueError, match="área privada"):
        liberacao.referencia_arquivo(publico)


# --- Fingerprint ---------------------------------------------------------------------------

def test_dependencias_transitivas_incluem_pacotes_e_imports_relativos(tmp_path, monkeypatch):
    monkeypatch.setattr(liberacao, "PROJECT_ROOT", tmp_path)
    arquivos = {
        "lib/__init__.py": "",
        "lib/a.py": "from lib import b\n",
        "lib/b.py": "import json\nfrom relatorios.c import X\n",
        "relatorios/__init__.py": "",
        "relatorios/c.py": "X = 1\n",
        "gestao/__init__.py": "",
        "gestao/registry.py": "",
        "gestao/runner.py": "from .registry import R\nimport lib.a\n",
    }
    for nome, conteudo in arquivos.items():
        (tmp_path / nome).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / nome).write_text(conteudo, encoding="utf-8")

    encontrados = {p.relative_to(tmp_path.resolve()).as_posix() for p in liberacao.dependencias(tmp_path / "gestao" / "runner.py")}
    assert encontrados == set(arquivos)


def test_fingerprint_real_cobre_a_ponte_importada_pelo_a1_do_g01():
    impressao = liberacao.fingerprint_candidato("G01")
    assert {"relatorios/privacidade.py", "ocde/relatorios/privacidade.py"} <= set(impressao["dependencias"])
    assert len(impressao["fingerprint"]) == 64


def test_cadastro_conferido_permite_piloto_so_com_id(tmp_path):
    cadastro = liberacao.carregar_cadastro()
    piloto = replace(cadastro.pilotos[0], conferido=True, id_petrvs="123")
    liberacao._validar_piloto(piloto)


def test_referencia_aceita_acervo_privado_que_e_juncao(acervo, tmp_path_factory):
    """artefatos_local é junção para o OneDrive: a referência não pode seguir o link."""

    import os

    externo = tmp_path_factory.mktemp("onedrive") / "artefatos_local"
    (externo / "validacao").mkdir(parents=True)
    (externo / "validacao" / "ato.pdf").write_bytes(b"%PDF-1.4 ato")
    link = acervo / "artefatos_local"
    try:
        if os.name == "nt":
            import _winapi
            _winapi.CreateJunction(str(externo), str(link))
        else:
            os.symlink(externo, link, target_is_directory=True)
    except OSError:
        pytest.skip("sem permissão para criar junção/link")

    ref = liberacao.referencia_arquivo(link / "validacao" / "ato.pdf")
    assert ref["caminho"] == "artefatos_local/validacao/ato.pdf"


def test_referencia_com_ponto_ponto_para_area_publica_e_recusada(acervo):
    publico = acervo / "docs" / "ato.md"
    publico.parent.mkdir(parents=True)
    publico.write_text("ato", encoding="utf-8")
    (acervo / "artefatos_local").mkdir(exist_ok=True)
    with pytest.raises(ValueError, match="área privada"):
        liberacao.referencia_arquivo(acervo / "artefatos_local" / ".." / "docs" / "ato.md")
