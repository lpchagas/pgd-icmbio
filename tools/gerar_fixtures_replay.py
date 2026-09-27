"""Gerador determinístico de fixtures do replay (tools/replay_producao.py).

Para os A1 com uma única SQL parametrizada por período (I03–I07, I09–I12), lê a
SQL do próprio A1 por ``ast`` (sem executá-lo), extrai as colunas do SELECT final
e os literais dos ``CASE ... END AS coluna`` e produz linhas sintéticas por
período, com semente fixa. A saída é congelada em
``tests/fixtures/replay/<alvo>/consultas.json`` e versionada: o replay compara
referência e candidato sobre esse arquivo, nunca sobre uma geração nova.

I01, I02, I08, G01 e G02 usam fixtures escritas à mão (consulta sem período,
duas consultas por período ou I/O próprio).

Uso:
  python -m tools.gerar_fixtures_replay --alvo I03            # grava
  python -m tools.gerar_fixtures_replay --alvo todos --verificar  # confere
"""
from __future__ import annotations

import argparse
import ast
import json
import random
import re
import sys
from datetime import date, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from lib.periodos import analysis_window, build_periods_pe, build_periods_pt  # noqa: E402
from tools.replay_producao import ALVOS, FIXTURES_DIR  # noqa: E402

DATA_EXECUCAO = "2026-09-13"
LINHAS_POR_PERIODO = 4
GERADOS = tuple(alvo for alvo, config in ALVOS.items() if config.get("fixture") == "gerada")

# Mesmas unidades das fixtures do I02: cobrem os três níveis do mesogrupo e o "Não mapeado".
UNIDADES = (
    ("CGSIN", "Coordenação-Geral Sintética"),
    ("NGI-SINT", "Núcleo Gestor Sintético"),
    ("UNID-NOME", "Unidade Mapeada Pelo Nome"),
    ("SEM-MAPA", "Unidade | sem mapa\nquebrada"),
)
_INTEIRO = re.compile(r"^(total|qtd|num|quantidade)_|_total$|^tamanho_")
_NOTA = re.compile(r"^nota_(minima|maxima)$")
_DECIMAL = re.compile(r"perc|pct|taxa|score|media|nota|diferenca|forca|carga|progresso|meta_|proporcao")
_DATA = re.compile(r"(^|_)(inicio|fim|data)(_|$)")
_IDENTIFICADOR = re.compile(r"(^id_|_id$)")


def sql_do_a1(script: Path) -> str:
    """Única constante SQL* de nível de módulo do A1; mais de uma exige fixture manual."""

    arvore = ast.parse(script.read_text(encoding="utf-8"))
    constantes = [
        no.value.value
        for no in arvore.body
        if isinstance(no, ast.Assign) and isinstance(no.value, ast.Constant) and isinstance(no.value.value, str)
        for alvo in no.targets
        if isinstance(alvo, ast.Name) and alvo.id.startswith("SQL")
    ]
    if len(constantes) != 1:
        raise ValueError(f"{script.name}: {len(constantes)} constantes SQL; use fixture manual")
    return constantes[0]


def _dividir_no_nivel_zero(texto: str) -> list[str]:
    partes, atual, profundidade, aspas = [], "", 0, False
    for caractere in texto:
        if caractere == "'":
            aspas = not aspas
        if not aspas:
            if caractere == "(":
                profundidade += 1
            elif caractere == ")":
                profundidade -= 1
            elif caractere == "," and profundidade == 0:
                partes.append(atual)
                atual = ""
                continue
        atual += caractere
    partes.append(atual)
    return partes


def colunas_do_select_final(sql: str) -> list[str]:
    sql = re.sub(r"--[^\n]*", "", sql)
    profundidade, marcas = 0, []
    for achado in re.finditer(r"\(|\)|\bSELECT\b|\bFROM\b", sql, re.IGNORECASE):
        token = achado.group(0).upper()
        if token == "(":
            profundidade += 1
        elif token == ")":
            profundidade -= 1
        elif profundidade == 0:
            marcas.append((token, achado.start(), achado.end()))
    select = [m for m in marcas if m[0] == "SELECT"][-1]
    fim = next(m for m in marcas if m[0] == "FROM" and m[1] > select[1])
    colunas = []
    for parte in _dividir_no_nivel_zero(sql[select[2]:fim[1]]):
        expressao = " ".join(parte.split())
        alias = re.search(r"\bAS\s+([A-Za-z_]\w*)\s*$", expressao, re.IGNORECASE)
        colunas.append(alias.group(1) if alias else expressao.split(".")[-1].strip())
    return colunas


def categorias(sql: str, coluna: str) -> list[str]:
    """Literais (texto ou número) de THEN/ELSE do CASE que define a coluna, em qualquer CTE."""

    valores: list[str] = []
    for bloco in re.finditer(rf"CASE\b((?:(?!\bCASE\b).)*?)\bEND\s+AS\s+{coluna}\b", sql, re.IGNORECASE | re.DOTALL):
        for texto, numero in re.findall(r"\b(?:THEN|ELSE)\s+(?:'([^']*)'|(-?\d+(?:\.\d+)?)\b)", bloco.group(1), re.IGNORECASE):
            literal = numero or texto
            if literal not in valores:
                valores.append(literal)
    return valores


def _valor(coluna: str, sql: str, rng: random.Random, inicio: date, fim: date, n: int) -> str:
    if _IDENTIFICADOR.search(coluna):
        return f"sint-{coluna}-{n}"
    literais = categorias(sql, coluna)
    if literais:
        return rng.choice(literais)
    if _DATA.search(coluna):
        return (inicio + timedelta(days=rng.randint(0, max((fim - inicio).days, 0)))).isoformat()
    if _NOTA.search(coluna):
        return str(rng.randint(1, 5))
    if _INTEIRO.search(coluna):
        return str(rng.randint(0, 25))
    if _DECIMAL.search(coluna):
        if rng.random() < 0.1:
            return ""  # NULL do JDBC chega como texto vazio (clean)
        if "nota" in coluna:
            return f"{rng.uniform(1, 5):.2f}"
        if "diferenca_direcional" in coluna:
            return f"{rng.uniform(-4, 4):.2f}"
        if "diferenca" in coluna:
            return f"{rng.uniform(0, 4):.2f}"
        if any(parte in coluna for parte in ("forca", "perc", "pct", "proporcao")):
            return f"{rng.uniform(0, 100):.2f}"
        return f"{rng.uniform(0, 150):.2f}"
    if coluna == "nome_servidor":
        return f"Servidor Sintético {n:02d}"
    if coluna.startswith(("nome_", "descricao_")):
        return rng.choice(("Entrega sintética nº {n}", "Relatório | anual {n}", "Ação\nem duas linhas {n}", "")).format(n=n)
    return rng.choice(("Sim", "Não", ""))


def _ajustar_i03(linha: dict, rng: random.Random, n: int) -> None:
    pares = (
        ('{"quantitativo": 10}', '{"quantitativo": 12}'),
        ('{"quantitativo": 8}', '{"quantitativo": 8}'),
        ('{"porcentagem": 100}', '{"porcentagem": 45}'),
        ('{"porcentagem": 0}', '{"porcentagem": 10}'),
        ('{"outro": 1}', '{"outro": 1}'),
        ("{invalido", '{"quantitativo": 1}'),
        ("", ""),
        ("null", '{"quantitativo": 3}'),
    )
    linha["meta_json"], linha["realizado_json"] = pares[n % len(pares)]


def _ajustar_i07(linhas: list[dict], rng: random.Random, inicio: date, fim: date) -> None:
    """Dois vínculos por entrega (a agregação soma horas) e datas coerentes com o período."""

    chave = ("unidade_sigla", "unidade_nome", "id_entrega", "nome_entrega", "id_plano_entrega",
             "inicio_vigencia_plano_entrega", "fim_vigencia_plano_entrega")
    for n, linha in enumerate(linhas):
        if n % 2:
            linha.update({c: linhas[n - 1][c] for c in chave})
        else:
            vigencia = sorted((linha["inicio_vigencia_plano_entrega"], linha["fim_vigencia_plano_entrega"]))
            linha["inicio_vigencia_plano_entrega"], linha["fim_vigencia_plano_entrega"] = vigencia
        plano_inicio = inicio - timedelta(days=rng.randint(0, 40))
        plano_fim = max(plano_inicio + timedelta(days=rng.randint(30, 150)), inicio)
        linha.update({
            "plano_trabalho_id": f"sint-pt-{n}",
            "carga_horaria": str(rng.choice((20, 30, 40))),
            "forma_contagem_carga_horaria": ("HORAS", "DIAS", "")[n % 3],
            "plano_inicio": plano_inicio.isoformat(),
            "plano_fim": plano_fim.isoformat(),
            "sobreposicao_inicio": max(plano_inicio, inicio).isoformat(),
            "sobreposicao_fim": min(plano_fim, fim).isoformat(),
            "forca_trabalho": f"{rng.choice((25, 50, 100)):.2f}",
        })
    if linhas:
        linhas[-1]["plano_inicio"] = ""  # ramo sem data: 0 hora


def gerar(alvo: str, data_execucao: str = DATA_EXECUCAO) -> dict:
    if alvo not in GERADOS:
        raise ValueError(f"{alvo} não usa fixture gerada")
    config = ALVOS[alvo]
    sql = sql_do_a1(PROJECT_ROOT / str(config["script"]))
    colunas = colunas_do_select_final(sql)
    if "unidade_sigla" not in colunas:
        raise ValueError(f"{alvo}: SELECT final sem unidade_sigla")
    corte = analysis_window(data_execucao).fim
    periodos = build_periods_pt(corte) if config["periodos"] == "pt" else build_periods_pe(corte)
    rng = random.Random(f"{alvo}-{data_execucao}")
    consultas = []
    for indice, (rotulo, _tipo, inicio, _fim_previsto, fim, _status) in enumerate(periodos):
        quantidade = 0 if indice == len(periodos) - 1 else LINHAS_POR_PERIODO
        linhas = []
        for n in range(quantidade):
            sigla, nome = UNIDADES[(indice + n) % len(UNIDADES)]
            linha = {c: _valor(c, sql, rng, inicio, fim, n) for c in colunas}
            linha.update({"unidade_sigla": sigla, "unidade_nome": nome})
            if alvo == "I03":
                _ajustar_i03(linha, rng, indice + n)
            linhas.append(linha)
        if alvo == "I07":
            _ajustar_i07(linhas, rng, inicio, fim)
        principal = {
            "periodo": rotulo,
            "inicio": inicio.isoformat(),
            "fim": fim.isoformat(),
            "colunas": colunas,
            "linhas": [[linha[c] for c in colunas] for linha in linhas],
        }
        if alvo == "I03":
            # D22 (3.0.0): consulta de contagem do alerta no mesmo período; o marcador
            # separa as duas consultas (a referência anterior só emite a principal).
            principal["nao_contem"] = ["AS qtd"]
        consultas.append(principal)
        if alvo == "I03":
            consultas.append({
                "periodo": rotulo, "nome": "alerta_d22", "opcional": True,
                "inicio": inicio.isoformat(), "fim": fim.isoformat(),
                "contem": ["AS qtd"], "colunas": ["qtd"],
                "linhas": [["0" if quantidade == 0 else "2"]],
            })
    return {
        "descricao": (f"Linhas congeladas sintéticas do {alvo} para o replay offline (data de execução "
                      f"{data_execucao}). Geradas por tools/gerar_fixtures_replay.py. Sem dados reais."),
        "consultas": consultas,
    }


def serializar(documento: dict) -> str:
    return json.dumps(documento, ensure_ascii=False, indent=2) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gera ou confere fixtures sintéticas do replay.")
    parser.add_argument("--alvo", required=True, choices=[*GERADOS, "todos"])
    parser.add_argument("--verificar", action="store_true", help="não grava; falha se a fixture versionada diverge")
    args = parser.parse_args(argv)
    divergentes = []
    for alvo in GERADOS if args.alvo == "todos" else (args.alvo,):
        destino = FIXTURES_DIR / alvo / "consultas.json"
        texto = serializar(gerar(alvo))
        if args.verificar:
            if not destino.exists() or destino.read_text(encoding="utf-8") != texto:
                divergentes.append(alvo)
            continue
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(texto, encoding="utf-8", newline="\n")
        print(f"{alvo}: {destino.relative_to(PROJECT_ROOT).as_posix()}")
    if divergentes:
        print(f"fixture divergente da geração: {', '.join(divergentes)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
