"""Caracterização da seleção por escopo antes da unificação (plano de reorganização, §7.1, L5).

Hoje há dois caminhos de seleção:

- A: ``ocde.relatorios.escopo`` (``scope_from_values`` + ``filter_rows``), usado pela
  extração OCDE, pelos relatórios V2/cumulativo e pelo ciclo gerencial;
- B: ``OrganizationStructure.select`` via ``gestao.runner._scope_units`` (o
  ``lib.validation_runner`` repete o mesmo código).

Os testes fixam onde A e B coincidem — inclusive nos três pilotos decididos na H4
(GR2 regional; CGOV e COCAGE sem subordinadas) — e registram as divergências atuais
como estão. A unificação do L5 deve manter as coincidências e resolver cada
divergência de forma deliberada, trocando o teste correspondente.

Estrutura 100% sintética em ``tests/fixtures/escopo/``.
"""
from __future__ import annotations

import argparse
import ast
from pathlib import Path

import pytest

import gestao.runner as runner_gestao
import lib.validation_runner as runner_validacao
import ocde.relatorios.escopo as escopo
from lib.escopos import slug
from lib.estrutura_organizacional import OrganizationStructure, load_organization_structure

pytestmark = pytest.mark.regression

RAIZ = Path(__file__).resolve().parents[2]
ESTRUTURA = RAIZ / "tests" / "fixtures" / "escopo" / "ICMBIO_estrutura.csv"


@pytest.fixture
def estrutura() -> OrganizationStructure:
    return load_organization_structure(ESTRUTURA, ESTRUTURA.parent / "sem-dicionario.csv")


def _linhas(estrutura: OrganizationStructure) -> list[dict]:
    linhas = [{"unidade_sigla": u.sigla, "mesogrupo": u.mesogrupo, "id": u.icmbio_id} for u in estrutura.units_by_id.values()]
    return linhas + [{"unidade_sigla": "cgov", "mesogrupo": "Sede", "id": "caixa-baixa"},
                     {"unidade_sigla": "N.I.", "mesogrupo": "Não mapeado", "id": "ni"}]


def caminho_a(monkeypatch, estrutura, linhas, **seletor) -> tuple[list[str], str]:
    """Linhas mantidas (sigla#id) e chave do escopo, como na extração OCDE."""

    monkeypatch.setattr(escopo, "load_organization_structure", lambda: estrutura)
    spec = escopo.scope_from_values(**seletor)
    mantidas = escopo.filter_rows(linhas, spec, escopo.load_unit_profiles(ESTRUTURA))
    return sorted(f"{linha['unidade_sigla']}#{linha['id']}" for linha in mantidas), spec.key


def caminho_b(monkeypatch, estrutura, modulo=runner_gestao, **seletor) -> tuple[list[str], str]:
    """Siglas selecionadas e chave do escopo, como no gestao.runner."""

    monkeypatch.setattr(modulo, "load_organization_structure", lambda: estrutura)
    argumentos = argparse.Namespace(escopo=None, regional=None, unidade=None, mesogrupo=None,
                                    tipo_unidade=None, lista_unidades=None)
    vars(argumentos).update(seletor)
    rotulo, unidades = modulo._scope_units(argumentos)
    chave = "-".join(slug(parte) for parte in rotulo.split(":", 1))
    return sorted(unidades), chave


def _siglas(selecao_a: list[str]) -> list[str]:
    return sorted({item.split("#")[0].upper() for item in selecao_a})


# --- Coincidências que a unificação precisa preservar ------------------------------------

@pytest.mark.parametrize("seletor, esperado, chave", [
    ({"regional": "GR2"}, ["CT-X", "GR2", "NGI-A", "UC-A1", "UC-A2", "UC-DUP"], "regional-gr2"),
    ({"unidade": "CGOV"}, ["CGOV"], "unidade-cgov"),
    ({"unidade": "COCAGE"}, ["COCAGE"], "unidade-cocage"),
])
def test_pilotos_h4_mesmas_unidades_e_mesma_chave_nos_dois_caminhos(monkeypatch, estrutura, seletor, esperado, chave):
    selecao_a, chave_a = caminho_a(monkeypatch, estrutura, _linhas(estrutura), **seletor)
    selecao_b, chave_b = caminho_b(monkeypatch, estrutura, **seletor)
    selecao_c, chave_c = caminho_b(monkeypatch, estrutura, runner_validacao, **seletor)

    assert _siglas(selecao_a) == selecao_b == [s.upper() for s in selecao_c] == esperado
    assert chave_a == chave_b == chave_c == chave


def test_regional_segue_id_mae_em_qualquer_profundidade_e_ignora_rotulo(monkeypatch, estrutura):
    selecao_a, _ = caminho_a(monkeypatch, estrutura, _linhas(estrutura), regional="GR2")
    selecao_b, _ = caminho_b(monkeypatch, estrutura, regional="GR2")

    for selecao in (_siglas(selecao_a), selecao_b):
        assert {"UC-A2", "CT-X"} <= set(selecao)   # profundidade 3; rótulo divergente
        assert "UC-FORA" not in selecao             # rotulada GR2, subordinada à GR1


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


# --- Divergências e defeitos atuais (registrados, não corrigidos no L2) ------------------

def test_divergencia_regional_sem_estrutura_cai_no_rotulo_com_a_mesma_chave(monkeypatch, estrutura):
    """A usa outro critério em silêncio (rótulo de mesogrupo) e mantém a chave; B recusa.

    O plano (§7.1) exige erro. O L5 deve fazer o caminho A falhar sem a estrutura.
    """

    linhas = _linhas(estrutura)
    selecao_a, chave_a = caminho_a(monkeypatch, OrganizationStructure({}, {}), linhas, regional="GR2")

    assert chave_a == "regional-gr2"
    assert _siglas(selecao_a) == ["GR2", "NGI-A", "UC-A1", "UC-A2", "UC-DUP", "UC-FORA"]
    with pytest.raises(FileNotFoundError):
        caminho_b(monkeypatch, OrganizationStructure({}, {}), regional="GR2")


def test_divergencia_unidade_inexistente_vira_produto_vazio_no_caminho_a(monkeypatch, estrutura):
    """A devolve zero linhas sem erro; B recusa. O plano (§7.1) exige erro."""

    selecao_a, chave_a = caminho_a(monkeypatch, estrutura, _linhas(estrutura), unidade="INEXISTENTE")

    assert (selecao_a, chave_a) == ([], "unidade-inexistente")
    with pytest.raises(ValueError, match="não localizada"):
        caminho_b(monkeypatch, estrutura, unidade="INEXISTENTE")


def test_defeito_sigla_duplicada_vaza_unidade_de_outra_regional(monkeypatch, estrutura):
    """Nenhum caminho trata sigla ambígua como erro (exigido no §7.1).

    A mantém as duas UC-DUP (ids 21 e 22) no escopo da GR2; B lista a sigla, e o filtro
    posterior por sigla traz as duas também.
    """

    selecao_a, _ = caminho_a(monkeypatch, estrutura, _linhas(estrutura), regional="GR2")
    selecao_b, _ = caminho_b(monkeypatch, estrutura, regional="GR2")

    assert {"UC-DUP#21", "UC-DUP#22"} <= set(selecao_a)
    assert "UC-DUP" in selecao_b


def test_divergencia_chave_de_tipo_de_unidade(monkeypatch, estrutura):
    _, chave_a = caminho_a(monkeypatch, estrutura, _linhas(estrutura), tipo_unidade="UC")
    _, chave_b = caminho_b(monkeypatch, estrutura, tipo_unidade="UC")

    assert (chave_a, chave_b) == ("tipo_unidade-uc", "tipo-unidade-uc")


def test_divergencia_chave_de_lista_depende_do_caminho_do_arquivo_no_caminho_b(monkeypatch, estrutura, tmp_path):
    lista = tmp_path / "lista-pilotos.txt"
    lista.write_text("CGOV\nCOCAGE\n", encoding="utf-8")

    _, chave_a = caminho_a(monkeypatch, estrutura, _linhas(estrutura), lista_unidades=lista)
    selecao_b, chave_b = caminho_b(monkeypatch, estrutura, lista_unidades=lista)

    assert chave_a == "lista_unidades-lista_fornecida"
    assert chave_b.startswith("lista-unidades-") and "lista-pilotos" in chave_b
    assert selecao_b == ["CGOV", "COCAGE"]


def test_scopespec_de_lib_escopos_nao_tem_uso_em_producao():
    """Só ``slug`` é importado de lib.escopos; o ScopeSpec de lá é código sem consumidor."""

    importados: set[str] = set()
    # Só as pastas de código versionado; nunca percorre junctions privadas da raiz.
    codigo = [arquivo for pasta in ("lib", "ocde", "gestao", "mgi", "tools") for arquivo in (RAIZ / pasta).rglob("*.py")]
    assert codigo
    for arquivo in codigo:
        try:
            arvore = ast.parse(arquivo.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for no in ast.walk(arvore):
            if isinstance(no, ast.ImportFrom) and no.module == "lib.escopos":
                importados |= {alias.name for alias in no.names}

    assert importados == {"slug"}
