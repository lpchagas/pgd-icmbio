"""Seleção por escopo depois da unificação (plano de reorganização, §7.1, L5/L7).

Até o L4 havia dois caminhos de seleção: A (``relatorios.escopo``, extração OCDE,
relatórios e ciclo) e B (``OrganizationStructure.select`` repetido no
``gestao.runner`` e no ``lib.validation_runner``). O L5 unificou a resolução em
``relatorios.escopo.scope_from_values`` e resolveu cada divergência do L2:

- ESC-01 regional sem a hierarquia: erro (antes A caía no rótulo de mesogrupo);
- ESC-02 unidade inexistente: erro (antes A gerava produto vazio);
- ESC-03 sigla repetida: erro quando as homônimas ficam dos dois lados do recorte;
- ESC-04/05 chaves canônicas iguais nos três pontos (``tipo_unidade-…``,
  ``lista_unidades-<hash12>``), sem o caminho do arquivo;
- ESC-06 ``lib.escopos`` só normaliza (o ``ScopeSpec`` duplicado saiu).

No L7 (decisão CGOV D19, com trava de divergência e conciliação D20), a subordinação passou do
``id_mae`` da estrutura oficial para a hierarquia do **PETRVS** (``unidade_pai_id``):
na estrutura real, a maior parte das unidades da GR2 não tem sigla, e o produto
"GR2" certificado cobria só a própria regional.

Hierarquia 100% sintética em ``tests/fixtures/escopo/PETRVS_unidades.csv`` (aplicada
a todos os testes pelo ``conftest``); a estrutura sintética continua servindo aos
seletores por rótulo.
"""
from __future__ import annotations

import argparse
import ast
from dataclasses import replace
from pathlib import Path

import pytest

import gestao.runner as runner_gestao
import lib.validation_runner as runner_validacao
import relatorios.escopo as escopo
from lib.estrutura_organizacional import load_organization_structure
from lib.unidades_petrvs import HierarquiaPetrvs, UnidadePetrvs

pytestmark = pytest.mark.regression

RAIZ = Path(__file__).resolve().parents[2]
ESTRUTURA = RAIZ / "tests" / "fixtures" / "escopo" / "ICMBIO_estrutura.csv"


def _linhas(hierarquia: HierarquiaPetrvs) -> list[dict]:
    linhas = [{"unidade_sigla": u.sigla, "mesogrupo": "", "id": u.id} for u in hierarquia.unidades.values()]
    return linhas + [{"unidade_sigla": "cgov", "mesogrupo": "Sede", "id": "caixa-baixa"},
                     {"unidade_sigla": "N.I.", "mesogrupo": "Não mapeado", "id": "ni"}]


def _usar(monkeypatch, hierarquia: HierarquiaPetrvs) -> None:
    monkeypatch.setattr(escopo, "carregar_hierarquia", lambda *a: hierarquia)


def _com(hierarquia: HierarquiaPetrvs, *unidades: UnidadePetrvs, trocar: dict[str, str] | None = None) -> HierarquiaPetrvs:
    base = {i: (replace(u, unidade_pai_id=trocar[i]) if trocar and i in trocar else u) for i, u in hierarquia.unidades.items()}
    base.update({u.id: u for u in unidades})
    return HierarquiaPetrvs(base, "outra")


def caminho_a(linhas, **seletor) -> tuple[list[str], str]:
    """Linhas mantidas (sigla#id) e chave do escopo, como na extração OCDE."""

    spec = escopo.scope_from_values(**seletor)
    mantidas = escopo.filter_rows(linhas, spec, escopo.load_unit_profiles(ESTRUTURA))
    return sorted(f"{linha['unidade_sigla']}#{linha['id']}" for linha in mantidas), spec.key


def caminho_b(modulo=runner_gestao, **seletor) -> tuple[list[str], str]:
    """Siglas selecionadas e chave do escopo, como no gestao.runner/validation_runner."""

    argumentos = argparse.Namespace(escopo=None, regional=None, unidade=None, mesogrupo=None,
                                    tipo_unidade=None, lista_unidades=None)
    vars(argumentos).update(seletor)
    _rotulo, unidades, chave = modulo._scope_units(argumentos)
    return sorted(unidades), chave


def _siglas(selecao_a: list[str]) -> list[str]:
    return sorted({item.split("#")[0].upper() for item in selecao_a})


# --- Coincidências preservadas ------------------------------------------------------------

@pytest.mark.parametrize("seletor, esperado, chave", [
    ({"regional": "GR2"}, ["CT-X", "GR2", "NGI-A", "UC-A1", "UC-A2", "UC-DUP"], "regional-gr2"),
    ({"unidade": "CGOV"}, ["CGOV"], "unidade-cgov"),
    ({"unidade": "COCAGE"}, ["COCAGE"], "unidade-cocage"),
])
def test_pilotos_h4_mesmas_unidades_e_mesma_chave_nos_tres_pontos(hierarquia_petrvs_sintetica, seletor, esperado, chave):
    selecao_a, chave_a = caminho_a(_linhas(hierarquia_petrvs_sintetica), **seletor)
    selecao_b, chave_b = caminho_b(**seletor)
    selecao_c, chave_c = caminho_b(runner_validacao, **seletor)

    assert _siglas(selecao_a) == selecao_b == selecao_c == esperado
    assert chave_a == chave_b == chave_c == chave


def test_regional_segue_a_hierarquia_do_petrvs_em_qualquer_profundidade(hierarquia_petrvs_sintetica):
    selecao_a, _ = caminho_a(_linhas(hierarquia_petrvs_sintetica), regional="GR2")
    selecao_b, _ = caminho_b(regional="GR2")

    for selecao in (_siglas(selecao_a), selecao_b):
        assert {"UC-A2", "CT-X"} <= set(selecao)   # profundidade 3; rótulo divergente na estrutura
        assert "UC-FORA" not in selecao             # rotulada GR2 na estrutura, filha da GR1 no PETRVS


def test_regional_registra_ids_do_petrvs_com_a_raiz_primeiro():
    spec = escopo.scope_from_values(regional="GR2")

    assert spec.ids[0] == "p-gr2"
    assert set(spec.ids) == {"p-gr2", "p-ngi", "p-uca1", "p-uca2", "p-ctx", "p-dup1", "p-dup2"}


def test_homonimas_todas_dentro_do_recorte_sao_aceitas(hierarquia_petrvs_sintetica):
    selecao_a, _ = caminho_a(_linhas(hierarquia_petrvs_sintetica), regional="GR2")
    assert {"UC-DUP#p-dup1", "UC-DUP#p-dup2"} <= set(selecao_a)


def test_unidade_nao_inclui_subordinadas(hierarquia_petrvs_sintetica):
    for sigla, subordinada in (("CGOV", "DIV-CGOV"), ("COCAGE", "SEC-COCAGE")):
        selecao_a, _ = caminho_a(_linhas(hierarquia_petrvs_sintetica), unidade=sigla)
        selecao_b, _ = caminho_b(unidade=sigla)
        assert subordinada not in _siglas(selecao_a) and subordinada not in selecao_b


def test_caminho_a_normaliza_caixa_da_sigla_nas_linhas(hierarquia_petrvs_sintetica):
    selecao_a, _ = caminho_a(_linhas(hierarquia_petrvs_sintetica), unidade="CGOV")

    assert selecao_a == ["CGOV#p-cgov", "cgov#caixa-baixa"]


def test_mudanca_de_hierarquia_altera_os_dois_caminhos_igualmente(monkeypatch, hierarquia_petrvs_sintetica):
    # UC-A1 (e UC-A2 abaixo dela) passa para a GR1
    _usar(monkeypatch, _com(hierarquia_petrvs_sintetica, trocar={"p-uca1": "p-gr1"}))

    selecao_a, _ = caminho_a(_linhas(hierarquia_petrvs_sintetica), regional="GR2")
    selecao_b, _ = caminho_b(regional="GR2")

    assert _siglas(selecao_a) == selecao_b == ["CT-X", "GR2", "NGI-A", "UC-DUP"]


# --- Divergências resolvidas no L5 e fonte da hierarquia no L7 --------------------------------

@pytest.mark.parametrize("modulo", [None, runner_gestao, runner_validacao])
def test_esc01_regional_sem_hierarquia_e_erro_nos_tres_pontos(monkeypatch, hierarquia_petrvs_sintetica, modulo):
    _usar(monkeypatch, HierarquiaPetrvs({}))
    with pytest.raises(escopo.EscopoInvalido, match="cadastro de unidades do PETRVS"):
        if modulo is None:
            caminho_a(_linhas(hierarquia_petrvs_sintetica), regional="GR2")
        else:
            caminho_b(modulo, regional="GR2")


def test_esc01_regional_sem_unidades_resolvidas_nao_cai_no_rotulo():
    linhas = [{"unidade_sigla": "GR2", "mesogrupo": "GR2"}]
    with pytest.raises(escopo.EscopoInvalido):
        escopo.filter_rows(linhas, escopo.ScopeSpec("regional", "GR2"))


@pytest.mark.parametrize("modulo", [None, runner_gestao, runner_validacao])
def test_esc02_unidade_inexistente_e_erro_nos_tres_pontos(hierarquia_petrvs_sintetica, modulo):
    with pytest.raises(escopo.EscopoInvalido, match="não localizada"):
        if modulo is None:
            caminho_a(_linhas(hierarquia_petrvs_sintetica), unidade="INEXISTENTE")
        else:
            caminho_b(modulo, unidade="INEXISTENTE")


@pytest.mark.parametrize("seletor, trecho", [
    ({"regional": "GR2"}, "homônimas fora do recorte: X-DUP"),
    ({"regional": "GR1"}, "homônimas fora do recorte: X-DUP"),
    ({"unidade": "X-DUP"}, "Sigla ambígua no PETRVS"),
    ({"unidade": "UC-DUP"}, "Sigla ambígua no PETRVS"),
])
def test_esc03_homonimas_divididas_pelo_recorte_sao_erro_nos_tres_pontos(monkeypatch, hierarquia_petrvs_sintetica, seletor, trecho):
    dividida = _com(hierarquia_petrvs_sintetica,
                    UnidadePetrvs("p-x1", "31", "X-DUP", "Homonima sob a GR2", "p-gr2"),
                    UnidadePetrvs("p-x2", "32", "X-DUP", "Homonima sob a GR1", "p-gr1"))
    _usar(monkeypatch, dividida)
    for modulo in (None, runner_gestao, runner_validacao):
        with pytest.raises(escopo.EscopoInvalido, match=trecho):
            if modulo is None:
                caminho_a(_linhas(dividida), **seletor)
            else:
                caminho_b(modulo, **seletor)


def test_esc04_chave_de_tipo_de_unidade_e_canonica(monkeypatch, hierarquia_petrvs_sintetica):
    estrutura = load_organization_structure(ESTRUTURA, ESTRUTURA.parent / "sem-dicionario.csv")
    monkeypatch.setattr(escopo, "load_organization_structure", lambda: estrutura)
    _, chave_a = caminho_a(_linhas(hierarquia_petrvs_sintetica), tipo_unidade="UC")
    _, chave_b = caminho_b(tipo_unidade="UC")
    _, chave_c = caminho_b(runner_validacao, tipo_unidade="UC")

    assert chave_a == chave_b == chave_c == "tipo_unidade-uc"


def test_esc05_chave_de_lista_depende_so_das_siglas(hierarquia_petrvs_sintetica, tmp_path):
    lista = tmp_path / "lista-pilotos.txt"
    lista.write_text("# pilotos\nCGOV\nCOCAGE\n", encoding="utf-8")
    outra = tmp_path / "outro-nome.csv"
    outra.write_text("sigla\ncocage\ncgov\n", encoding="utf-8")

    _, chave_a = caminho_a(_linhas(hierarquia_petrvs_sintetica), lista_unidades=lista)
    selecao_b, chave_b = caminho_b(lista_unidades=lista)
    _, chave_c = caminho_b(runner_validacao, lista_unidades=outra)

    assert chave_a == chave_b == chave_c
    assert chave_a.startswith("lista_unidades-") and len(chave_a) == len("lista_unidades-") + 12
    assert "pilotos" not in chave_a
    assert selecao_b == ["CGOV", "COCAGE"]


def test_esc05_lista_com_sigla_inexistente_e_erro(tmp_path):
    lista = tmp_path / "lista.txt"
    lista.write_text("CGOV\nNAO-EXISTE\n", encoding="utf-8")
    with pytest.raises(escopo.EscopoInvalido, match="não localizada"):
        caminho_b(lista_unidades=lista)


def test_esc06_lib_escopos_so_normaliza():
    """``lib.escopos`` não tem mais ScopeSpec; o único é o de ``relatorios.escopo``."""

    import lib.escopos as modulo

    assert not hasattr(modulo, "ScopeSpec")
    importados: set[str] = set()
    # Só as pastas de código versionado; nunca percorre junctions privadas da raiz.
    codigo = [arquivo for pasta in ("lib", "ocde", "relatorios", "gestao", "mgi", "tools") for arquivo in (RAIZ / pasta).rglob("*.py")]
    assert codigo
    for arquivo in codigo:
        try:
            arvore = ast.parse(arquivo.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for no in ast.walk(arvore):
            if isinstance(no, ast.ImportFrom) and no.module == "lib.escopos":
                importados |= {alias.name for alias in no.names}

    assert importados <= {"slug", "normalize"}


# --- Trava de divergência (D19) e conciliação (D20) ------------------------------------------

def _estrutura_com_dicionario(**mapa):
    from lib.estrutura_organizacional import OrganizationStructure

    base = escopo.load_organization_structure()
    return OrganizationStructure(dict(base.units_by_id), mapa)


def test_d19_unidade_mapeada_em_outra_regional_trava_o_recorte(monkeypatch):
    # UC-A1 está sob a GR2 no PETRVS, mas o dicionário a liga à UC-FORA (id 15), da GR1.
    monkeypatch.setattr(escopo, "load_organization_structure", lambda *a, e=_estrutura_com_dicionario(**{"UC-A1": "15"}): e)
    monkeypatch.setattr(escopo, "carregar_conciliacoes", lambda *a: {})
    with pytest.raises(escopo.EscopoInvalido, match="trava de divergência.*UC-A1"):
        escopo.scope_from_values(regional="GR2")


def test_d19_unidade_da_regional_na_estrutura_mas_fora_no_petrvs_trava(monkeypatch):
    # UC-FORA existe no PETRVS sob a GR1; o dicionário a liga ao id 12 (UC-A1, na GR2).
    monkeypatch.setattr(escopo, "load_organization_structure", lambda *a, e=_estrutura_com_dicionario(**{"UC-FORA": "12"}): e)
    monkeypatch.setattr(escopo, "carregar_conciliacoes", lambda *a: {})
    with pytest.raises(escopo.EscopoInvalido, match="UC-FORA"):
        escopo.scope_from_values(regional="GR2")


def test_d20_conciliacao_registrada_libera_e_fica_no_escopo(monkeypatch):
    monkeypatch.setattr(escopo, "load_organization_structure", lambda *a, e=_estrutura_com_dicionario(**{"UC-A1": "15"}): e)
    monkeypatch.setattr(escopo, "carregar_conciliacoes", lambda *a: {"GR2": {"UC-A1"}})
    spec = escopo.scope_from_values(regional="GR2")
    assert spec.conciliadas == ("UC-A1",) and "UC-A1" in spec.units


def test_d19_sem_mapeamento_segue_o_petrvs_e_e_contado():
    spec = escopo.scope_from_values(regional="GR2")
    assert "UC-A2" in spec.units and "UC-A2" in spec.sem_mapeamento


def test_d19_sigla_do_dicionario_inexistente_no_petrvs_nao_trava(monkeypatch):
    monkeypatch.setattr(escopo, "load_organization_structure", lambda *a, e=_estrutura_com_dicionario(**{"SIGLA-VELHA": "12"}): e)
    assert escopo.scope_from_values(regional="GR2").ids[0] == "p-gr2"


def test_d19_regional_sem_estrutura_oficial_e_erro(monkeypatch):
    from lib.estrutura_organizacional import OrganizationStructure

    monkeypatch.setattr(escopo, "load_organization_structure", lambda *a: OrganizationStructure({}, {}))
    with pytest.raises(escopo.EscopoInvalido, match="exige a estrutura oficial"):
        escopo.scope_from_values(regional="GR2")


def test_d20_registro_versionado_concilia_as_tres_ucs_da_gr2():
    assert escopo.carregar_conciliacoes()["GR2"] == {"PARNAABROLHOS", "RESEXCASSURUBA", "PARNAMONPASCOAL"}
