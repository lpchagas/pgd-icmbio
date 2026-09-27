"""Verificador de links e referências da documentação (tools/verificar_links.py)."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tools import verificar_links as vl

pytestmark = pytest.mark.unit


def _repo(tmp_path: Path, arquivos: dict[str, str]) -> list[Path]:
    for nome, texto in arquivos.items():
        caminho = tmp_path / nome
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_text(texto, encoding="utf-8")
    return sorted(tmp_path / nome for nome in arquivos if nome.endswith(".md"))


def _classes(referencias) -> dict[str, str]:
    return {r.alvo: r.classe for r in referencias}


def test_slug_github_preserva_acentos_e_remove_pontuacao():
    assert vl.slug_github("Seção 2 — Ações `lib/x.py` e [link](a.md)!") == "seção-2--ações-libxpy-e-link"
    assert vl.slug_github("snake_case e Maiúsculas") == "snake_case-e-maiúsculas"


def test_ancoras_com_titulos_repetidos_e_ignora_codigo():
    texto = "# Título\n## Título\n```\n# Não é título\n```\n<a id=\"manual\"></a>\n"

    assert vl.ancoras(texto) == {"título", "título-1", "manual"}


def test_links_e_ancoras(tmp_path):
    arquivos = _repo(tmp_path, {
        "docs/a.md": "# Visão geral\n## Ações\n[ok](b.md) [anc](b.md#decisões) [ruim](b.md#nada)\n"
                     "[local](#ações) [local-ruim](#inexistente) [quebrado](c.md) [web](https://exemplo.invalid)\n"
                     "[raiz](/lib/x.py) ![img](img/fig.png)\n",
        "docs/b.md": "# Decisões\n",
        "lib/x.py": "",
    })

    classes = _classes(vl.verificar(arquivos, raiz=tmp_path))

    assert classes == {
        "b.md": "ok", "b.md#decisões": "ok", "b.md#nada": "ancora_quebrada",
        "#ações": "ok", "#inexistente": "ancora_quebrada", "c.md": "link_quebrado",
        "https://exemplo.invalid": "externo", "/lib/x.py": "ok", "img/fig.png": "link_quebrado",
    }


def test_crases_placeholder_planejado_e_inexistente(tmp_path):
    arquivos = _repo(tmp_path, {
        "README.md": "Use `lib/x.py` e `docs/06.X-eixoX.md` e `IND_OCDE_XX.1_run.py`.\n"
                     "`lib/caminhos.py` (planejado no L4a)\n"
                     "`lib/sumiu.py` foi citado\n"
                     "`python -m tools.algo` não é caminho; `arquivo_solto.py` também não\n"
                     "```\n`lib/dentro_de_codigo.py`\n```\n",
        "lib/x.py": "",
    })

    classes = _classes(vl.verificar(arquivos, raiz=tmp_path))

    assert classes == {
        "lib/x.py": "ok", "docs/06.X-eixoX.md": "placeholder", "IND_OCDE_XX.1_run.py": "placeholder",
        "lib/caminhos.py": "planejado", "lib/sumiu.py": "crase_inexistente", "arquivo_solto.py": "nome_sem_caminho",
    }


def test_areas_privadas_exigem_rotulo_e_nunca_sao_lidas(tmp_path):
    arquivos = _repo(tmp_path, {
        "docs/p.md": "[a](../artefatos_local/x.md)\n"
                     "`agente/CLAUDE.md` fica fora do Git (privado)\n"
                     "`cgov/analises/run.py`\n"
                     "`docs/cgov/README.md` é pública\n",
        "docs/cgov/README.md": "# CGOV\n",
    })

    classes = _classes(vl.verificar(arquivos, raiz=tmp_path))

    assert classes == {
        "../artefatos_local/x.md": "privado_sem_rotulo", "agente/CLAUDE.md": "privado",
        "cgov/analises/run.py": "privado_sem_rotulo", "docs/cgov/README.md": "ok",
    }


def test_link_para_fora_da_raiz(tmp_path):
    raiz = tmp_path / "repo"
    arquivos = _repo(raiz, {"docs/a.md": "[fora](../../outro/x.md)\n"})

    assert _classes(vl.verificar(arquivos, raiz=raiz)) == {"../../outro/x.md": "fora_da_raiz"}


def test_excecao_por_arquivo_e_resumo(tmp_path):
    arquivos = _repo(tmp_path, {"a.md": "[x](falta.md)\n", "b.md": "[y](falta.md)\n"})

    referencias = vl.verificar(arquivos, raiz=tmp_path, excecoes={"a.md": "página histórica mantida como está"})
    resumo = vl.resumir(referencias)

    assert _classes([r for r in referencias if r.arquivo == "a.md"]) == {"falta.md": "excecao"}
    assert resumo["total_problemas"] == 1 and list(resumo["problemas"]) == ["b.md"]


def test_cli_nao_bloqueia_por_padrao_e_exige_justificativa(tmp_path, capsys):
    assert vl.main([]) == 0
    assert "arquivos .md" in capsys.readouterr().out

    excecoes = tmp_path / "excecoes.json"
    excecoes.write_text('{"README.md": " "}', encoding="utf-8")
    with pytest.raises(SystemExit):
        vl.main(["--excecoes", str(excecoes)])


def test_listagem_pelo_git_nao_inclui_area_privada():
    if subprocess.run(["git", "-C", str(vl.PROJECT_ROOT), "rev-parse"], capture_output=True).returncode:
        pytest.skip("listagem exige o repositório Git")

    arquivos = vl.listar_markdown()

    assert arquivos
    relativos = [arquivo.relative_to(vl.PROJECT_ROOT).parts for arquivo in arquivos]
    assert not [partes for partes in relativos if vl._privado(partes)]
