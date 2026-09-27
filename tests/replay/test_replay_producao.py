"""Replay offline de produção (tools/replay_producao.py), começando pelo I02.

Cada teste roda o A1 real em subprocesso, com I/O substituído por fixtures
sintéticas. Os controles negativos alteram uma dependência de produção sem
tocar no A1 e exigem que o replay acuse a divergência.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tools import replay_producao as rp

DATA = "2026-09-13"
REFERENCIA = "git:HEAD"

pytestmark = pytest.mark.skipif(
    subprocess.run(["git", "-C", str(rp.PROJECT_ROOT), "rev-parse", "--verify", "HEAD"], capture_output=True).returncode != 0,
    reason="replay exige o repositório Git com HEAD",
)


def _copia(tmp_path: Path) -> Path:
    raiz, _ = rp.materializar(REFERENCIA, tmp_path / "candidato")
    return raiz


def _alterar(arquivo: Path, antes: str, depois: str) -> None:
    texto = arquivo.read_text(encoding="utf-8")
    assert texto.count(antes) == 1, f"trecho a alterar não encontrado em {arquivo.name}"
    arquivo.write_text(texto.replace(antes, depois), encoding="utf-8")


def _tipos(relatorio: dict) -> set[str]:
    return {d["tipo"] for d in relatorio.get("diferencas", [])}


def test_normalizacao_remove_so_diretorio_temporario_e_carimbo(tmp_path):
    saida = tmp_path / "saida"
    arquivo = saida / "2026-09" / "IND_OCDE_02.2_taxa_20260913_0959.csv"
    texto = f"Arquivo salvo: {arquivo}\nConcluido.\n"

    assert rp.normalizar_saida(texto, saida) == "Arquivo salvo: <SAIDA>/2026-09/IND_OCDE_02.2_taxa_<carimbo>.csv\nConcluido.\n"
    assert rp.normalizar_nome("IND_OCDE_02.2_taxa_20260913_1000.csv") == "IND_OCDE_02.2_taxa_<carimbo>.csv"
    assert rp.normalizar_nome("IND_OCDE_02.2_v1_20260913.csv") == "IND_OCDE_02.2_v1_20260913.csv"


def test_i02_referencia_contra_ela_mesma_e_equivalente():
    relatorio = rp.replay("I02", REFERENCIA, REFERENCIA, DATA)

    assert relatorio["status"] == "equivalente", relatorio
    assert relatorio["referencia"]["consultas"] == 4
    assert relatorio["referencia"]["arquivos"] == ["2026-09/IND_OCDE_02.2_taxa_cumprimento_temporal_<carimbo>.csv"]
    assert {"lib/csv_utils.py", "lib/estrutura_organizacional.py", "lib/periodos.py"} <= set(relatorio["referencia"]["modulos"])
    assert relatorio["dependencias"] == {"so_referencia": [], "so_candidato": [], "hash_alterado": [], "a1_alterado": False}


def test_i02_arvore_de_trabalho_equivale_ao_head():
    relatorio = rp.replay("I02", REFERENCIA, str(rp.PROJECT_ROOT), DATA)

    assert relatorio["status"] == "equivalente", relatorio


def test_i02_artefato_preserva_bom_delimitador_e_mesogrupo(tmp_path):
    raiz = _copia(tmp_path)
    execucao = rp.executar(raiz, "I02", DATA, rp.FIXTURES_DIR / "I02", tmp_path / "trabalho")
    rp._validar_execucao("referencia", execucao, rp.FIXTURES_DIR / "I02")
    (arquivo,) = execucao["arquivos"].values()
    dados = arquivo.read_bytes()
    cabecalho, linhas = rp._ler_csv(dados)

    assert dados.startswith(b"\xef\xbb\xbf")
    assert b"|" in dados.splitlines()[0]
    assert cabecalho[cabecalho.index("unidade_nome") + 1] == "mesogrupo"
    mesogrupos = {linha[cabecalho.index("unidade_sigla")]: linha[cabecalho.index("mesogrupo")] for linha in linhas}
    assert mesogrupos == {
        "CGSIN": "Meso Sintético A",      # nível 1: dicionário -> icmbio_id
        "NGI-SINT": "Meso Sintético B",   # nível 2: sigla direta
        "UNID-NOME": "Meso Sintético C",  # nível 3: nome
        "SEM-MAPA": "Não mapeado",
    }
    assert "Unidade | sem mapa / quebrada" in {linha[cabecalho.index("unidade_nome")] for linha in linhas}


def test_controle_negativo_bom_removido_em_dependencia(tmp_path):
    raiz = _copia(tmp_path)
    _alterar(raiz / "lib" / "csv_utils.py", 'path.open("w", newline="", encoding="utf-8-sig")', 'path.open("w", newline="", encoding="utf-8")')

    relatorio = rp.replay("I02", REFERENCIA, str(raiz), DATA)

    assert relatorio["status"] == "divergente"
    assert "bom" in _tipos(relatorio)
    assert relatorio["dependencias"]["hash_alterado"] == ["lib/csv_utils.py"]
    assert relatorio["dependencias"]["a1_alterado"] is False


def test_controle_negativo_mesogrupo_alterado_em_dependencia(tmp_path):
    raiz = _copia(tmp_path)
    _alterar(raiz / "lib" / "estrutura_organizacional.py",
             "        # Nível 2 — sigla direta contra ICMBIO_estrutura.csv.\n        if sigla_norm and",
             "        # Nível 2 — sigla direta contra ICMBIO_estrutura.csv.\n        if False and sigla_norm and")

    relatorio = rp.replay("I02", REFERENCIA, str(raiz), DATA)

    assert relatorio["status"] == "divergente"
    (linhas,) = [d for d in relatorio["diferencas"] if d["tipo"] == "linhas"]
    assert {tuple(e["chave"]) for e in linhas["exemplos"]} == {("T3-2025", "NGI-SINT"), ("Q1-2026", "NGI-SINT")}
    assert all(e["colunas"] == ["mesogrupo"] for e in linhas["exemplos"])
    assert relatorio["dependencias"]["a1_alterado"] is False


def test_sql_alterada_no_a1_e_divergente_mesmo_com_linhas_iguais(tmp_path):
    raiz = _copia(tmp_path)
    _alterar(raiz / "ocde" / "indicadores" / "IND_OCDE_02.1_run.py",
             "WHEN r.taxa_cumprimento_perc >= 90 THEN", "WHEN r.taxa_cumprimento_perc >= 85 THEN")

    relatorio = rp.replay("I02", REFERENCIA, str(raiz), DATA)

    assert relatorio["status"] == "divergente"
    assert _tipos(relatorio) == {"consulta"}
    assert len(relatorio["diferencas"][0]["periodos"]) == 4


def test_periodo_sem_fixture_e_erro_e_nunca_equivalencia(tmp_path):
    fixtures = tmp_path / "fixtures"
    shutil.copytree(rp.FIXTURES_DIR / "I02", fixtures)
    documento = json.loads((fixtures / "consultas.json").read_text(encoding="utf-8"))
    documento["consultas"] = [c for c in documento["consultas"] if c["periodo"] != "T4-2025"]
    (fixtures / "consultas.json").write_text(json.dumps(documento, ensure_ascii=False), encoding="utf-8")

    relatorio = rp.replay("I02", REFERENCIA, REFERENCIA, DATA, fixtures=fixtures)

    assert relatorio["status"] == "erro"
    assert "ConsultaNaoCongelada" in relatorio["erro"]


def test_cli_retorna_codigo_por_status(tmp_path, capsys):
    saida = tmp_path / "relatorio.json"

    codigo = rp.main(["--alvo", "I02", "--referencia", REFERENCIA, "--candidato", REFERENCIA,
                      "--data-execucao", DATA, "--saida-json", str(saida)])

    assert codigo == 0
    assert json.loads(saida.read_text(encoding="utf-8"))["status"] == "equivalente"
    assert "I02: equivalente" in capsys.readouterr().out


def test_substituicao_bloqueia_env_acervo_privado_rede_e_subprocesso(tmp_path):
    raiz = _copia(tmp_path)
    (raiz / ".env").write_text("DENODO_PASSWORD=sentinela-replay\n", encoding="utf-8")  # pragma: allowlist secret
    (raiz / "artefatos_local").mkdir()
    (raiz / "artefatos_local" / "privado.txt").write_text("privado", encoding="utf-8")
    sonda = tmp_path / "sonda.py"
    sonda.write_text(
        "import socket, subprocess, sys\n"
        "import lib.denodo_config as dc\n"
        "tentativas = {\n"
        "    'env': lambda: open('.env').read(),\n"
        "    'acervo': lambda: open('artefatos_local/privado.txt').read(),\n"
        "    'rede': lambda: socket.create_connection(('127.0.0.1', 9), timeout=1),\n"
        "    'subprocesso': lambda: subprocess.run([sys.executable, '-c', 'pass']),\n"
        "    'jpype': lambda: __import__('jpype'),\n"
        "}\n"
        "for nome, acao in tentativas.items():\n"
        "    try:\n"
        "        acao(); print(nome, 'PERMITIDO')\n"
        "    except (PermissionError, ImportError):\n"
        "        print(nome, 'bloqueado')\n"
        "print('usuario', repr(dc.get_config().user))\n",
        encoding="utf-8",
    )
    env = rp.ambiente_subprocesso(raiz, DATA, rp.FIXTURES_DIR / "I02", tmp_path / "saida", tmp_path / "registro.json")

    processo = subprocess.run([sys.executable, str(sonda)], cwd=raiz, env=env, capture_output=True, text=True, encoding="utf-8")

    assert processo.returncode == 0, processo.stderr
    assert processo.stdout.split("\n")[:5] == ["env bloqueado", "acervo bloqueado", "rede bloqueado", "subprocesso bloqueado", "jpype bloqueado"]
    assert "usuario 'replay'" in processo.stdout
    assert "sentinela-replay" not in processo.stdout + processo.stderr


# --- Alvos com fixtures geradas (tools/gerar_fixtures_replay.py) -------------------------

from tools import gerar_fixtures_replay as gf  # noqa: E402


@pytest.mark.parametrize("alvo", gf.GERADOS)
def test_fixture_versionada_e_reproduzivel_pelo_gerador(alvo):
    versionada = (rp.FIXTURES_DIR / alvo / "consultas.json").read_text(encoding="utf-8")

    assert versionada == gf.serializar(gf.gerar(alvo))


@pytest.mark.parametrize("alvo", gf.GERADOS)
def test_replay_de_alvo_gerado_e_equivalente_e_nao_vazio(alvo):
    relatorio = rp.replay(alvo, REFERENCIA, REFERENCIA, DATA)

    assert relatorio["status"] == "equivalente", relatorio.get("erro")
    entradas = json.loads((rp.FIXTURES_DIR / alvo / "consultas.json").read_text(encoding="utf-8"))["consultas"]
    periodos = {(entrada["inicio"], entrada["fim"]) for entrada in entradas}
    # Uma consulta por período, mais as consultas com marcador (ex.: alerta D22 do I03),
    # que só as versões que as emitem consomem.
    assert len(periodos) <= relatorio["referencia"]["consultas"] <= len(entradas)
    assert relatorio["referencia"]["arquivos"]


def test_controle_negativo_calendario_de_dias_uteis_no_i07(tmp_path):
    raiz = _copia(tmp_path)
    calendario = raiz / "lib" / "calendario.py"
    texto = calendario.read_text(encoding="utf-8")
    assert "def dias_uteis(" in texto
    calendario.write_text(texto + "\n\n_original = dias_uteis\n\n\ndef dias_uteis(inicio, fim):\n    return _original(inicio, fim) + 1\n", encoding="utf-8")

    relatorio = rp.replay("I07", REFERENCIA, str(raiz), DATA)

    assert relatorio["status"] == "divergente"
    (linhas,) = [d for d in relatorio["diferencas"] if d["tipo"] == "linhas"]
    assert {c for e in linhas["exemplos"] for c in e["colunas"]} == {"total_horas_planejadas_entrega"}
    assert relatorio["dependencias"]["hash_alterado"] == ["lib/calendario.py"]


def test_chave_de_comparacao_vem_do_contrato_por_arquivo():
    assert rp.chave_do_arquivo("I05", "2026-09/IND_OCDE_05.2_v1_distribuicao_<carimbo>.csv") == ("periodo", "unidade_sigla", "id_servidor")
    assert rp.chave_do_arquivo("I05", "2026-09/IND_OCDE_05.2_v2_distribuicao_<carimbo>.csv") == ("periodo", "unidade_sigla")
    assert rp.chave_do_arquivo("I07", "2026-09/IND_OCDE_07.2_horas_<carimbo>.csv") == ("periodo", "unidade_sigla", "id_entrega")


@pytest.mark.parametrize("alvo", ["I02", "I08", "I01"])
def test_gerador_recusa_alvos_de_fixture_manual(alvo):
    with pytest.raises(ValueError):
        gf.gerar(alvo)


def test_extrator_le_colunas_e_categorias_da_sql():
    sql = "WITH x AS (SELECT CASE WHEN a > 1 THEN 'Alto' ELSE 'Baixo' END AS faixa, b FROM t)\n" \
          "SELECT x.faixa, SUM(b) AS total_b, CASE WHEN SUM(b) >= 5 THEN 1 ELSE 0 END AS volume_ok\nFROM x GROUP BY x.faixa"

    assert gf.colunas_do_select_final(sql) == ["faixa", "total_b", "volume_ok"]
    assert gf.categorias(sql, "faixa") == ["Alto", "Baixo"]
    assert gf.categorias(sql, "volume_ok") == ["1", "0"]


def test_erro_engolido_pelo_a1_torna_o_replay_nao_conclusivo(tmp_path):
    raiz = _copia(tmp_path)
    _alterar(raiz / "ocde" / "indicadores" / "IND_OCDE_04.1_run.py",
             "                columns, rows = query_rows(conn, sql)\n",
             "                columns, rows = query_rows(conn, sql)\n"
             "                if label == 'T4-2025':\n"
             "                    raise RuntimeError('falha simulada')\n")

    relatorio = rp.replay("I04", str(raiz), str(raiz), DATA)

    assert relatorio["status"] == "erro"
    assert "falha engolida" in relatorio["erro"]


# --- Alvos com fixture manual além do I02 ------------------------------------------------

@pytest.mark.parametrize("alvo, arquivos", [
    ("I01", ["2026-09/IND_OCDE_01.2_v1_proporcao_mensal_<carimbo>.csv",
             "2026-09/IND_OCDE_01.2_v2_proporcao_unidade_mensal_<carimbo>.csv"]),
    ("I08", ["2026-09/IND_OCDE_08.2_v1_proporcao_horas_dona_<carimbo>.csv",
             "2026-09/IND_OCDE_08.2_v2_proporcao_horas_executora_<carimbo>.csv"]),
])
def test_replay_de_alvo_manual_e_equivalente(alvo, arquivos):
    relatorio = rp.replay(alvo, REFERENCIA, REFERENCIA, DATA)

    assert relatorio["status"] == "equivalente", relatorio.get("erro")
    assert relatorio["referencia"]["arquivos"] == arquivos


def test_i08_serve_capacidade_e_vinculos_pelos_marcadores(tmp_path):
    raiz = _copia(tmp_path)
    execucao = rp.executar(raiz, "I08", DATA, rp.FIXTURES_DIR / "I08", tmp_path / "trabalho")

    rp._validar_execucao("referencia", execucao, rp.FIXTURES_DIR / "I08")
    assert [c["nome"] for c in execucao["registro"]["consultas"]] == ["capacidade", "vinculos"] * 4
    assert "AVISO: 1 entrega(s) com proporcao > 100%" in execucao["stdout"]


def _fixture_alterada(tmp_path, alvo, alterar) -> Path:
    destino = tmp_path / "fixtures" / alvo
    shutil.copytree(rp.FIXTURES_DIR / alvo, destino)
    documento = json.loads((destino / "consultas.json").read_text(encoding="utf-8"))
    alterar(documento["consultas"])
    (destino / "consultas.json").write_text(json.dumps(documento, ensure_ascii=False), encoding="utf-8")
    return destino


def test_marcadores_ambiguos_tornam_o_replay_nao_conclusivo(tmp_path):
    def sem_marcador(consultas):
        for item in consultas:
            item.pop("nao_contem", None)

    relatorio = rp.replay("I08", REFERENCIA, REFERENCIA, DATA, fixtures=_fixture_alterada(tmp_path, "I08", sem_marcador))

    assert relatorio["status"] == "erro"
    assert "ambíguas" in relatorio["erro"]


def test_fixture_que_sobra_torna_o_replay_nao_conclusivo(tmp_path):
    def duplicar(consultas):
        consultas.append(dict(consultas[0], nome="nunca-consultada", contem=["texto-que-nao-existe"]))

    relatorio = rp.replay("I01", REFERENCIA, REFERENCIA, DATA, fixtures=_fixture_alterada(tmp_path, "I01", duplicar))

    assert relatorio["status"] == "erro"
    assert "diferem das fixtures" in relatorio["erro"]


# --- Dublê JDBC e indicadores de gestão (G01, G02) ---------------------------------------

def test_controle_negativo_query_rows_real_esta_sob_replay(tmp_path):
    raiz = _copia(tmp_path)
    _alterar(raiz / "lib" / "monthly_runner.py",
             "rows.append([clean(rs.getObject(i + 1)) for i in range(count)])",
             "rows.append([clean(rs.getObject(i + 1)).upper() for i in range(count)])")

    relatorio = rp.replay("I02", REFERENCIA, str(raiz), DATA)

    assert relatorio["status"] == "divergente"
    assert relatorio["dependencias"]["hash_alterado"] == ["lib/monthly_runner.py"]


@pytest.mark.parametrize("alvo, arquivos", [
    ("G01-restrito", ["IND_GEST_01.2_detalhe_restrito_CGSIN_NGI-SINT_UNID-NOME_e_mais_1_<carimbo>.csv",
                      "IND_GEST_01.2_painel_restrito_CGSIN_NGI-SINT_UNID-NOME_e_mais_1_<carimbo>.csv"]),
    ("G01-compartilhavel", ["IND_GEST_01.2_painel_compartilhavel_TODAS_<carimbo>.csv"]),
    ("G02-restrito", ["IND_GEST_02.2_entregas_restrito_CGSIN_NGI-SINT_<carimbo>.csv",
                      "IND_GEST_02.2_historico_restrito_CGSIN_NGI-SINT_<carimbo>.csv",
                      "IND_GEST_02.2_nominal_restrito_CGSIN_NGI-SINT_<carimbo>.csv"]),
    ("G02-compartilhavel", ["IND_GEST_02.2_entregas_compartilhavel_TODAS_<carimbo>.csv"]),
])
def test_replay_de_gestao_e_equivalente_por_produto(alvo, arquivos):
    relatorio = rp.replay(alvo, REFERENCIA, REFERENCIA, DATA)

    assert relatorio["status"] == "equivalente", relatorio.get("erro")
    assert relatorio["referencia"]["arquivos"] == arquivos


@pytest.mark.parametrize("alvo", ["G01-compartilhavel", "G02-compartilhavel"])
def test_produto_compartilhavel_nao_traz_identificacao_pessoal(tmp_path, alvo):
    raiz = _copia(tmp_path)
    execucao = rp.executar(raiz, alvo, DATA, rp.pasta_de_fixtures(alvo), tmp_path / "trabalho")
    rp._validar_execucao("referencia", execucao, rp.pasta_de_fixtures(alvo))

    for caminho in execucao["arquivos"].values():
        texto = caminho.read_bytes().decode("utf-8-sig")
        cabecalho = texto.splitlines()[0].split("|")
        assert not {"servidor_nome", "id_servidor", "status_alterado_por"} & set(cabecalho)
        assert "Servidor Sintético" not in texto and "sint-srv-" not in texto


def test_controle_negativo_supressao_k_do_g01_em_modulo_que_muda_de_lugar(tmp_path):
    raiz = _copia(tmp_path)
    _alterar(raiz / "relatorios" / "privacidade.py", "K_MIN = 5", "K_MIN = 6")

    relatorio = rp.replay("G01-compartilhavel", REFERENCIA, str(raiz), DATA)

    assert relatorio["status"] == "divergente"
    assert relatorio["dependencias"]["hash_alterado"] == ["relatorios/privacidade.py"]
    assert relatorio["dependencias"]["a1_alterado"] is False


def test_controle_negativo_sanitizacao_do_g02_em_modulo_que_muda_de_lugar(tmp_path):
    raiz = _copia(tmp_path)
    _alterar(raiz / "relatorios" / "textos_execucao.py",
             r'_EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@', r'_EMAIL = re.compile(r"(?!)\b[A-Z0-9._%+-]+@')

    relatorio = rp.replay("G02-restrito", REFERENCIA, str(raiz), DATA)

    assert relatorio["status"] == "divergente"
    assert relatorio["dependencias"]["hash_alterado"] == ["relatorios/textos_execucao.py"]
    arquivos = {d.get("arquivo", "") for d in relatorio["diferencas"]}
    assert any("historico" in a for a in arquivos) and any("entregas" in a for a in arquivos)
