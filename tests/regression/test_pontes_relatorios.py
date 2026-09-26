"""Pontes ocde/relatorios -> relatorios (plano de reorganização, §9.3, L4a).

Cada verificação roda num processo Python novo, para que o estado de importação
de um teste não contamine outro. As CLIs são executadas de fato, uma vez, sobre
dados sintéticos gerados pelo replay numa cópia temporária da árvore versionada.
"""
from __future__ import annotations

import ast
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.regression
ROOT = Path(__file__).resolve().parents[2]
PONTES = sorted(p.stem for p in (ROOT / "ocde" / "relatorios").glob("*.py") if p.stem != "__init__")
CLIS = ("relatorio_cumulativo", "relatorio_v2")


def _python(codigo: str, cwd: Path = ROOT, env: dict | None = None) -> subprocess.CompletedProcess:
    ambiente = {**os.environ, "PYTHONPATH": str(ROOT), "PYTHONIOENCODING": "utf-8", **(env or {})}
    return subprocess.run([sys.executable, "-B", "-c", codigo], cwd=cwd, env=ambiente,
                          capture_output=True, text=True, encoding="utf-8")


def test_todas_as_pontes_correspondem_a_modulos_reais():
    reais = sorted(p.stem for p in (ROOT / "relatorios").glob("*.py") if p.stem != "__init__")
    assert PONTES == reais and len(PONTES) == 16


@pytest.mark.parametrize("nome", PONTES)
def test_ponte_nao_contem_logica(nome):
    arvore = ast.parse((ROOT / "ocde" / "relatorios" / f"{nome}.py").read_text(encoding="utf-8"))
    corpo = arvore.body
    assert isinstance(corpo[0], ast.Expr) and isinstance(corpo[0].value, ast.Constant)  # docstring
    permitidos = []
    for no in corpo[1:]:
        if isinstance(no, ast.Import):
            permitidos.append(all(a.name == "sys" for a in no.names))
        elif isinstance(no, ast.ImportFrom):
            permitidos.append(no.module == "relatorios" and [a.name for a in no.names] == [nome] and no.names[0].asname == "_modulo")
        elif isinstance(no, ast.Assign):
            permitidos.append(ast.unparse(no) == "sys.modules[__name__] = _modulo")
        elif isinstance(no, ast.If):
            permitidos.append(nome in CLIS and ast.unparse(no) ==
                              "if __name__ == '__main__':\n    raise SystemExit(_modulo.main())")
        else:
            permitidos.append(False)
    assert all(permitidos), ast.unparse(arvore)


def test_imports_antigos_e_novos_sao_o_mesmo_objeto_executado_uma_vez():
    codigo = (
        "import importlib\n"
        f"nomes = {PONTES!r}\n"
        "for n in nomes:\n"
        "    antigo = importlib.import_module('ocde.relatorios.' + n)\n"
        "    antigo._marca_teste = n\n"
        "    novo = importlib.import_module('relatorios.' + n)\n"
        "    assert antigo is novo and novo._marca_teste == n and novo.__name__ == 'relatorios.' + n, n\n"
        "from ocde.relatorios.relatorio_v2 import _eligible_shared, render_report\n"
        "from ocde.relatorios.analisar_execucao_pgd import _scope_sql\n"
        "from ocde.relatorios.privacidade import K_MIN, apply_complementary_suppression\n"
        "from ocde.relatorios import textos_execucao\n"
        "import relatorios.textos_execucao as t\n"
        "assert textos_execucao is t\n"
        "print('ok', len(nomes))\n"
    )
    resultado = _python(codigo)

    assert resultado.returncode == 0, resultado.stderr
    assert resultado.stdout.strip() == f"ok {len(PONTES)}"


def test_importar_um_modulo_pela_ponte_nao_carrega_os_demais():
    codigo = (
        "import sys\n"
        "import ocde.relatorios.privacidade\n"
        "print(sorted(m for m in sys.modules if m.startswith(('relatorios', 'ocde.relatorios'))))\n"
    )
    resultado = _python(codigo)

    assert resultado.returncode == 0, resultado.stderr
    assert resultado.stdout.strip() == "['ocde.relatorios', 'ocde.relatorios.privacidade', 'relatorios', 'relatorios.privacidade']"


def test_project_root_e_o_mesmo_de_qualquer_diretorio(tmp_path):
    codigo = (
        "import lib.caminhos, lib.csv_utils, lib.denodo_config, lib.docs_sql, relatorios.loader\n"
        "print(lib.caminhos.PROJECT_ROOT)\n"
        "print({str(x) for x in (lib.csv_utils.PROJECT_ROOT, lib.denodo_config.PROJECT_ROOT, lib.docs_sql.PROJECT_ROOT, relatorios.loader.ROOT)})\n"
        "print(relatorios.loader.ENTREGAS_BASE)\n"
    )
    resultado = _python(codigo, cwd=tmp_path)

    assert resultado.returncode == 0, resultado.stderr
    raiz, conjunto, entregas = resultado.stdout.strip().splitlines()
    assert Path(raiz) == ROOT and conjunto == repr({str(ROOT)})
    assert Path(entregas) == ROOT / "artefatos_local" / "ocde" / "entregas"


# --- CLIs antigas e novas, executadas de fato ---------------------------------------------

@pytest.fixture(scope="module")
def copia_com_dados_sinteticos(tmp_path_factory):
    """Cópia só dos arquivos versionados (nunca os ignorados/privados) + A2 sintéticos do replay."""

    listagem = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                              capture_output=True)
    if listagem.returncode != 0:
        pytest.skip("a cópia exige o repositório Git")
    copia = tmp_path_factory.mktemp("pontes") / "arvore"
    for nome in filter(None, listagem.stdout.decode("utf-8").split("\0")):
        origem = ROOT / nome
        if origem.is_file():
            (copia / nome).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(origem, copia / nome)
    from tools import replay_producao as rp

    mes = copia / "artefatos_local" / "ocde" / "entregas" / "2026-09"
    por_escopo = mes / "escopos" / "nacional-nacional"  # o V2 lê por escopo; o cumulativo, pelo mês
    por_escopo.mkdir(parents=True)
    trabalho = tmp_path_factory.mktemp("a2")
    for alvo in [a for a in rp.ALVOS if a.startswith("I")]:
        execucao = rp.executar(copia, alvo, "2026-09-13", rp.pasta_de_fixtures(alvo), trabalho / alvo)
        assert execucao["returncode"] == 0, (alvo, execucao["stderr"][-300:])
        for caminho in execucao["arquivos"].values():
            shutil.copy2(caminho, mes / caminho.name)
            shutil.copy2(caminho, por_escopo / caminho.name)
            (mes / "escopos" / "regional-gr2").mkdir(exist_ok=True)
            shutil.copy2(caminho, mes / "escopos" / "regional-gr2" / caminho.name)
    # Estrutura sintética: as unidades dos A2 sintéticos ficam sob a GR2, piloto do gate (L5).
    estrutura = copia / "artefatos_local" / "ocde" / "diagnosticos" / "ICMBIO_estrutura.csv"
    estrutura.parent.mkdir(parents=True, exist_ok=True)
    estrutura.write_text(
        '{"schema":"estrutura sintetica das pontes"}\n'
        "icmbio_id,id_mae,sigla,uorg_nome,uorg_nome-completo,mesogrupo,tipo,macroprocesso,microgrupo,status\n"
        "10,,GR2,GR2 sintetica,GR2 sintetica,GR2,Gerência Regional,,,Ativo\n"
        "11,10,CGSIN,Unidade sintetica,Unidade sintetica,UC na GR2,UC,,,Ativo\n"
        "12,10,NGI-SINT,NGI sintetico,NGI sintetico,UC na GR2,NGI,,,Ativo\n",
        encoding="utf-8",
    )
    return copia


def _cli(copia: Path, modulo: str, *argumentos: str) -> subprocess.CompletedProcess:
    ambiente = {k: v for k, v in os.environ.items() if not k.startswith(("DENODO_", "MYSQL_", "PGD_"))}
    ambiente.update({"PYTHONIOENCODING": "utf-8", "PYTHONPATH": str(copia)})
    return subprocess.run([sys.executable, "-B", "-m", modulo, *argumentos], cwd=copia, env=ambiente,
                          capture_output=True, text=True, encoding="utf-8", timeout=300)


def test_cli_do_cumulativo_antiga_e_nova_geram_o_mesmo_relatorio(copia_com_dados_sinteticos):
    argumentos = ("--data-execucao", "2026-09-13", "--regional", "GR2")
    antiga = _cli(copia_com_dados_sinteticos, "ocde.relatorios.relatorio_cumulativo", *argumentos)
    nova = _cli(copia_com_dados_sinteticos, "relatorios.relatorio_cumulativo", *argumentos)

    assert antiga.returncode == nova.returncode == 0, antiga.stderr[-500:] + nova.stderr[-500:]
    estavel = lambda texto: [l for l in texto.splitlines() if "Extração observada em" not in l]  # noqa: E731
    assert estavel(antiga.stdout) == estavel(nova.stdout)
    assert antiga.stdout.count("# Relatório Gerencial Cumulativo do PGD") == 1  # main executado uma vez
    assert "RuntimeWarning" not in antiga.stderr


def test_cli_do_cumulativo_antiga_e_nova_recusam_nacional_sem_aceites(copia_com_dados_sinteticos):
    """Gate do L5 pelos comandos oficiais: a ponte antiga herda a recusa."""

    argumentos = ("--data-execucao", "2026-09-13", "--escopo", "nacional")
    antiga = _cli(copia_com_dados_sinteticos, "ocde.relatorios.relatorio_cumulativo", *argumentos)
    nova = _cli(copia_com_dados_sinteticos, "relatorios.relatorio_cumulativo", *argumentos)

    ultima = lambda r: r.stderr.strip().splitlines()[-1]  # noqa: E731
    assert antiga.returncode == nova.returncode == 1
    assert ultima(antiga) == ultima(nova) and ultima(nova).startswith("lib.liberacao.LiberacaoRecusada")
    assert "Relatório Gerencial Cumulativo" not in nova.stdout


def test_cli_do_v2_antiga_e_nova_chegam_ao_mesmo_ponto(copia_com_dados_sinteticos):
    """Sem manifesto e dados de gestão, as duas param no mesmo ponto real do main (não em --help)."""

    argumentos = ("--data-execucao", "2026-09-13", "--regional", "GR2", "--produto", "compartilhavel",
                  "--lente", "acumulada", "--rascunho")
    antiga = _cli(copia_com_dados_sinteticos, "ocde.relatorios.relatorio_v2", *argumentos)
    nova = _cli(copia_com_dados_sinteticos, "relatorios.relatorio_v2", *argumentos)

    ultima = lambda r: r.stderr.strip().splitlines()[-1]  # noqa: E731
    assert antiga.returncode == nova.returncode == 1
    assert ultima(antiga) == ultima(nova) and "Manifesto de gestão ausente" in ultima(antiga)
    assert "RuntimeWarning" not in antiga.stderr


@pytest.mark.parametrize("extra", [(), ("--rascunho",)])
def test_cli_do_v2_antiga_e_nova_recusam_compartilhavel_nacional_sem_aceites(copia_com_dados_sinteticos, extra):
    argumentos = ("--data-execucao", "2026-09-13", "--escopo", "nacional", "--produto", "compartilhavel",
                  "--lente", "acumulada", *extra)
    antiga = _cli(copia_com_dados_sinteticos, "ocde.relatorios.relatorio_v2", *argumentos)
    nova = _cli(copia_com_dados_sinteticos, "relatorios.relatorio_v2", *argumentos)

    ultima = lambda r: r.stderr.strip().splitlines()[-1]  # noqa: E731
    assert antiga.returncode == nova.returncode == 1
    assert ultima(antiga) == ultima(nova) and ultima(nova).startswith("lib.liberacao.LiberacaoRecusada")
