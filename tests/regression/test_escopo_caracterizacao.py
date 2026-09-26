"""Seleção por escopo depois da unificação (plano de reorganização, §7.1, L5).

Até o L4 havia dois caminhos de seleção: A (``relatorios.escopo``, extração OCDE,
relatórios e ciclo) e B (``OrganizationStructure.select`` repetido no
``gestao.runner`` e no ``lib.validation_runner``). O L2 caracterizou onde eles
coincidiam e onde divergiam; o L5 unificou a resolução em
``relatorios.escopo.scope_from_values`` e trocou cada divergência de forma
deliberada:

- ESC-01 regional sem estrutura: erro (antes A caía no rótulo de mesogrupo);
- ESC-02 unidade inexistente: erro (antes A gerava produto vazio);
- ESC-03 sigla ambígua: erro, salvo ligação explícita no dicionário CGOV;
- ESC-04/05 chaves canônicas iguais nos três pontos (``tipo_unidade-…``,
  ``lista_unidades-<hash12>``), sem o caminho do arquivo;
- ESC-06 ``lib.escopos`` só normaliza (o ``ScopeSpec`` duplicado saiu).

Estrutura 100% sintética em ``tests/fixtures/escopo/``.
"""
from __future__ import annotations

import argparse
import ast
from pathlib import Path

import pytest

import gestao.runner as runner_gestao
import lib.validation_runner as runner_validacao
import relatorios.escopo as escopo
from lib.estrutura_organizacional import OrganizationStructure, load_organization_structure

pytestmark = pytest.mark.regression

RAIZ = Path(__file__).resolve().parents[2]
ESTRUTURA = RAIZ / "tests" / "fixtures" / "escopo" / "ICMBIO_estrutura.csv"


@pytest.fixture
def estrutura_ambigua() -> OrganizationStructure:
    """Estrutura completa: UC-DUP existe sob a GR2 (id 21) e sob a GR1 (id 22)."""

    return load_organization_structure(ESTRUTURA, ESTRUTURA.parent / "sem-dicionario.csv")


@pytest.fixture
def estrutura(estrutura_ambigua) -> OrganizationStructure:
    """A mesma estrutura sem a homônima da GR1, para as equivalências dos pilotos."""

    unidades = {i: u for i, u in estrutura_ambigua.units_by_id.items() if i != "22"}
    return OrganizationStructure(unidades, dict(estrutura_ambigua.petrvs_to_id))


def _linhas(estrutura: OrganizationStructure) -> list[dict]:
    linhas = [{"unidade_sigla": u.sigla, "mesogrupo": u.mesogrupo, "id": u.icmbio_id} for u in estrutura.units_by_id.values()]
    return linhas + [{"unidade_sigla": "cgov", "mesogrupo": "Sede", "id": "caixa-baixa"},
                     {"unidade_sigla": "N.I.", "mesogrupo": "Não mapeado", "id": "ni"}]


def _usar(monkeypatch, estrutura: OrganizationStructure) -> None:
    monkeypatch.setattr(escopo, "load_organization_structure", lambda: estrutura)


def caminho_a(monkeypatch, estrutura, linhas, **seletor) -> tuple[list[str], str]:
    """Linhas mantidas (sigla#id) e chave do escopo, como na extração OCDE."""

    _usar(monkeypatch, estrutura)
    spec = escopo.scope_from_values(**seletor)
    mantidas = escopo.filter_rows(linhas, spec, escopo.load_unit_profiles(ESTRUTURA))
    return sorted(f"{linha['unidade_sigla']}#{linha['id']}" for linha in mantidas), spec.key


def caminho_b(monkeypatch, estrutura, modulo=runner_gestao, **seletor) -> tuple[list[str], str]:
    """Siglas selecionadas e chave do escopo, como no gestao.runner/validation_runner."""

    _usar(monkeypatch, estrutura)
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
def test_pilotos_h4_mesmas_unidades_e_mesma_chave_nos_tres_pontos(monkeypatch, estrutura, seletor, esperado, chave):
    selecao_a, chave_a = caminho_a(monkeypatch, estrutura, _linhas(estrutura), **seletor)
    selecao_b, chave_b = caminho_b(monkeypatch, estrutura, **seletor)
    selecao_c, chave_c = caminho_b(monkeypatch, estrutura, runner_validacao, **seletor)

    assert _siglas(selecao_a) == selecao_b == selecao_c == esperado
    assert chave_a == chave_b == chave_c == chave


def test_regional_segue_id_mae_em_qualquer_profundidade_e_ignora_rotulo(monkeypatch, estrutura):
    selecao_a, _ = caminho_a(monkeypatch, estrutura, _linhas(estrutura), regional="GR2")
    selecao_b, _ = caminho_b(monkeypatch, estrutura, regional="GR2")

    for selecao in (_siglas(selecao_a), selecao_b):
        assert {"UC-A2", "CT-X"} <= set(selecao)   # profundidade 3; rótulo divergente
        assert "UC-FORA" not in selecao             # rotulada GR2, subordinada à GR1


def test_regional_registra_ids_resolvidos_com_a_raiz_primeiro(monkeypatch, estrutura):
    _usar(monkeypatch, estrutura)
    spec = escopo.scope_from_values(regional="GR2")

    assert spec.ids[0] == "10"
    assert set(spec.ids) == {"10", "11", "12", "13", "14", "21"}


def test_unidade_nao_inclui_subordinadas(monkeypatch, estrutura):
    for sigla, subordinada in (("CGOV", "DIV-CGOV"), ("COCAGE", "SEC-COCAGE")):
        selecao_a, _ = caminho_a(monkeypatch, estrutura, _linhas(estrutura), unidade=sigla)
        selecao_b, _ = caminho_b(monkeypatch, estrutura, unidade=sigla)
        assert subordinada not in _siglas(selecao_a) and subordinada not in selecao_b


def test_caminho_a_normaliza_caixa_da_sigla_nas_linhas(monkeypatch, estrutura):
    selecao_a, _ = caminho_a(monkeypatch, estrutura, _linhas(estrutura), unidade="CGOV")

    assert selecao_a == ["CGOV#2", "cgov#caixa-baixa"]


def test_mudanca_de_estrutura_altera_os_dois_caminhos_igualmente(monkeypatch, estrutura):
    unidade = estrutura.units_by_id["12"]  # UC-A1 (e UC-A2 abaixo dela) passa para a GR1
    estrutura.units_by_id["12"] = type(unidade)(**{**unidade.__dict__, "parent_id": "20"})

    selecao_a, _ = caminho_a(monkeypatch, estrutura, _linhas(estrutura), regional="GR2")
    selecao_b, _ = caminho_b(monkeypatch, estrutura, regional="GR2")

    assert _siglas(selecao_a) == selecao_b == ["CT-X", "GR2", "NGI-A", "UC-DUP"]


# --- Divergências resolvidas no L5 (antes registradas pelo L2) ------------------------------

@pytest.mark.parametrize("modulo", [None, runner_gestao, runner_validacao])
def test_esc01_regional_sem_estrutura_e_erro_nos_tres_pontos(monkeypatch, estrutura, modulo):
    vazia = OrganizationStructure({}, {})
    with pytest.raises(escopo.EscopoInvalido, match="exige a estrutura"):
        if modulo is None:
            caminho_a(monkeypatch, vazia, _linhas(estrutura), regional="GR2")
        else:
            caminho_b(monkeypatch, vazia, modulo, regional="GR2")


def test_esc01_regional_sem_unidades_resolvidas_nao_cai_no_rotulo():
    linhas = [{"unidade_sigla": "GR2", "mesogrupo": "GR2"}]
    with pytest.raises(escopo.EscopoInvalido):
        escopo.filter_rows(linhas, escopo.ScopeSpec("regional", "GR2"))


@pytest.mark.parametrize("modulo", [None, runner_gestao, runner_validacao])
def test_esc02_unidade_inexistente_e_erro_nos_tres_pontos(monkeypatch, estrutura, modulo):
    with pytest.raises(escopo.EscopoInvalido, match="não localizada"):
        if modulo is None:
            caminho_a(monkeypatch, estrutura, _linhas(estrutura), unidade="INEXISTENTE")
        else:
            caminho_b(monkeypatch, estrutura, modulo, unidade="INEXISTENTE")


@pytest.mark.parametrize("seletor", [{"regional": "GR2"}, {"regional": "GR1"}, {"unidade": "UC-DUP"}])
def test_esc03_sigla_ambigua_e_erro_nos_tres_pontos(monkeypatch, estrutura_ambigua, seletor):
    for modulo in (None, runner_gestao, runner_validacao):
        with pytest.raises(escopo.EscopoInvalido, match="ambígua"):
            if modulo is None:
                caminho_a(monkeypatch, estrutura_ambigua, _linhas(estrutura_ambigua), **seletor)
            else:
                caminho_b(monkeypatch, estrutura_ambigua, modulo, **seletor)


def test_esc03_dicionario_cgov_desfaz_a_homonimia(monkeypatch, estrutura_ambigua):
    ligada = OrganizationStructure(dict(estrutura_ambigua.units_by_id), {"UC-DUP": "21"})
    _usar(monkeypatch, ligada)

    assert escopo.scope_from_values(unidade="UC-DUP").ids == ("21",)
    assert "UC-DUP" in escopo.scope_from_values(regional="GR2").units


def test_esc04_chave_de_tipo_de_unidade_e_canonica(monkeypatch, estrutura):
    _, chave_a = caminho_a(monkeypatch, estrutura, _linhas(estrutura), tipo_unidade="UC")
    _, chave_b = caminho_b(monkeypatch, estrutura, tipo_unidade="UC")
    _, chave_c = caminho_b(monkeypatch, estrutura, runner_validacao, tipo_unidade="UC")

    assert chave_a == chave_b == chave_c == "tipo_unidade-uc"


def test_esc05_chave_de_lista_depende_so_das_siglas(monkeypatch, estrutura, tmp_path):
    lista = tmp_path / "lista-pilotos.txt"
    lista.write_text("# pilotos\nCGOV\nCOCAGE\n", encoding="utf-8")
    outra = tmp_path / "outro-nome.csv"
    outra.write_text("sigla\ncocage\ncgov\n", encoding="utf-8")

    _, chave_a = caminho_a(monkeypatch, estrutura, _linhas(estrutura), lista_unidades=lista)
    selecao_b, chave_b = caminho_b(monkeypatch, estrutura, lista_unidades=lista)
    _, chave_c = caminho_b(monkeypatch, estrutura, runner_validacao, lista_unidades=outra)

    assert chave_a == chave_b == chave_c
    assert chave_a.startswith("lista_unidades-") and len(chave_a) == len("lista_unidades-") + 12
    assert "pilotos" not in chave_a
    assert selecao_b == ["CGOV", "COCAGE"]


def test_esc05_lista_com_sigla_inexistente_e_erro(monkeypatch, estrutura, tmp_path):
    lista = tmp_path / "lista.txt"
    lista.write_text("CGOV\nNAO-EXISTE\n", encoding="utf-8")
    with pytest.raises(escopo.EscopoInvalido, match="não localizada"):
        caminho_b(monkeypatch, estrutura, lista_unidades=lista)


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
