"""Catálogo único das capacidades S01–S24 (tools/gerar_catalogo_capacidades.py; B1, DP-09)."""
from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path

import pytest
import yaml

from lib.calendario import dias_uteis
from tools import gerar_catalogo_capacidades as g

pytestmark = pytest.mark.unit

RAIZ = g.PROJECT_ROOT
CAP03 = "docs/agente/projeto-v7/03-catalogo-skills-s01-s24.md"


@pytest.fixture
def copia(tmp_path: Path) -> Path:
    """Cópia mínima da árvore: YAML, template, arquivos com blocos e fichas atuais."""
    for rel in (g.CATALOGO, g.TEMPLATE, Path("capacidades/CATALOGO.md"), Path(CAP03)):
        destino = tmp_path / rel
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(RAIZ / rel, destino)
    shutil.copytree(RAIZ / g.FICHAS, tmp_path / g.FICHAS)
    return tmp_path


def _editar_yaml(raiz: Path, velho: str, novo: str) -> None:
    caminho = raiz / g.CATALOGO
    texto = caminho.read_text(encoding="utf-8")
    assert velho in texto
    caminho.write_text(texto.replace(velho, novo, 1), encoding="utf-8")


def test_repositorio_em_sincronia():
    assert g.divergencias(RAIZ) == []


def test_gerar_e_deterministico(copia: Path):
    shutil.rmtree(copia / g.FICHAS)
    assert len(g.gerar(copia)) == 24 + 1  # fichas e índice; os arquivos com blocos já estão em sincronia
    assert g.gerar(copia) == []
    (copia / g.FICHAS / "COMO_TESTAR.md").write_text("manual\n", encoding="utf-8")
    assert g.main(["--raiz", str(copia), "verificar"]) == 0


def test_ficha_editada_a_mao_e_detectada(copia: Path, capsys):
    ficha = copia / g.FICHAS / "S07.md"
    ficha.write_text(ficha.read_text(encoding="utf-8") + "edição manual\n", encoding="utf-8")
    assert g.main(["--raiz", str(copia), "verificar"]) == 1
    assert "divergente: capacidades/fichas/S07.md" in capsys.readouterr().out


def test_bloco_editado_a_mao_e_detectado(copia: Path):
    caminho = copia / CAP03
    texto = caminho.read_text(encoding="utf-8")
    caminho.write_text(texto.replace("calcular CHD e demanda", "calcular só CHD", 1), encoding="utf-8")
    assert g.divergencias(copia) == [f"divergente: {CAP03}"]


def test_arquivo_sobrando_e_detectado(copia: Path):
    (copia / g.FICHAS / "SKILL_S25.md").write_text("x\n", encoding="utf-8")
    assert g.divergencias(copia) == ["sobrando: capacidades/fichas/SKILL_S25.md"]


@pytest.mark.parametrize(
    ("velho", "novo", "trecho_erro"),
    [
        ("consumidores: S08, S10, S11, S12, S21", "consumidores: S08, S99", "inexistente S99"),
        ("  onda: 2\n  gate: G2\n", "  onda: 2\n  gate: G3\n", "incoerente com a onda"),
        ("- id: S07-T06\n", "- id: S07-T07\n", "teste_ia.casos deve seguir"),
        ("situacao: proposta_nao_validada", "situacao: aprovada_pelo_modelo", "situacao desconhecida"),
        ("fontes_metodologicas:\n  - B04", "fontes_metodologicas:\n  - B09", "fonte metodológica desconhecida"),
    ],
)
def test_yaml_invalido_e_recusado(copia: Path, velho: str, novo: str, trecho_erro: str):
    _editar_yaml(copia, velho, novo)
    with pytest.raises(g.CatalogoInvalido) as exc:
        g.carregar(copia)
    assert any(trecho_erro in erro for erro in exc.value.args[0]), exc.value.args[0]
    assert g.main(["--raiz", str(copia), "verificar"]) == 2


@pytest.mark.parametrize("dado", ["fulano@exemplo.gov.br", "123.456.789-00", "(61) 99999-0000"])
def test_dado_pessoal_no_yaml_e_recusado(copia: Path, dado: str):
    _editar_yaml(copia, "finalidade: calcular CHD e demanda", f"finalidade: calcular CHD e demanda {dado}")
    with pytest.raises(g.CatalogoInvalido):
        g.carregar(copia)


def test_ficha_tem_as_duas_partes():
    texto = (RAIZ / g.FICHAS / "S07.md").read_text(encoding="utf-8")
    assert texto.startswith(g.CABECALHO)
    for n in range(1, 28):
        assert f"\n## {n}. " in texto
    for trecho in ("## Teste em outras ferramentas de IA", "### Prompt de sistema", "```text\nVocê é um assistente",
                   "#### S07-T01 — período normal", "#### S07-SEC", "#### S07-AUT", "#### S07-SIS", "### Rubrica",
                   "| S07-SIS | | | | | | |"):
        assert trecho in texto
    assert "{{" not in texto


def test_toda_skill_tem_caso_por_caso_previsto():
    dados = yaml.safe_load((RAIZ / g.CATALOGO).read_text(encoding="utf-8"))
    for skill in dados["skills"]:
        previstos = [c["id"] for c in skill["ficha"]["casos_previstos"]]
        assert [c["id"] for c in skill["teste_ia"]["casos"]] == previstos, skill["id"]


def test_casos_de_calendario_conferem_com_lib_calendario():
    """Os números esperados das fichas S07 e S23 dependem destes dias úteis."""
    assert dias_uteis(date(2026, 9, 1), date(2026, 9, 30)) == 21
    assert dias_uteis(date(2026, 9, 14), date(2026, 9, 25)) == 10
    assert dias_uteis(date(2026, 9, 16), date(2026, 9, 30)) == 11
    assert dias_uteis(date(2026, 10, 1), date(2026, 10, 31)) == 20
    s07 = (RAIZ / g.FICHAS / "S07.md").read_text(encoding="utf-8")
    s23 = (RAIZ / g.FICHAS / "S23.md").read_text(encoding="utf-8")
    assert "21 dias úteis; CHD de 168 h" in s07 and "C: 11 dias úteis × 6 h = 66 h" in s07
    assert "20 dias úteis; CHD = 8 × (20 − 2) = 144 h" in s23
