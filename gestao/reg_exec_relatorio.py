"""Renderiza o Registro de Execução do Plano de Entregas (S21) em Markdown.

Segue o template da skill `cgov-registro-execucao` acrescido da seção de
verificação da RN-04 — a que decide se o Plano de Entregas do período pode
ser concluído. É um insumo técnico de apoio: não homologa avaliação nem
substitui o registro no PETRVS.
"""
from __future__ import annotations

from datetime import date
from typing import Mapping, Sequence

from lib.periodos import PeriodSpec

from gestao.reg_exec_regras import (
    SEMAFORO_ALERTA,
    SEMAFORO_ATENCAO,
    SEMAFORO_NAO_APLICA,
    SEMAFORO_OK,
    to_number,
)


# Rótulos Q são quadrimestres (3 por ano), não trimestres. A divergência com o
# texto herdado das planilhas da CGOV é registrada na seção de ressalvas.
_NOME_CICLO = {
    "quadrimestral": "quadrimestre",
    "trimestral": "trimestre",
    "mensal": "mês",
}


def _br(valor: object) -> str:
    """Data ISO para dd/mm/aaaa; qualquer outra coisa passa adiante."""

    texto = str(valor or "").strip()
    if len(texto) >= 10 and texto[4] == "-" and texto[7] == "-":
        return f"{texto[8:10]}/{texto[5:7]}/{texto[0:4]}"
    return texto or "—"


def _celula(valor: object) -> str:
    """Renderiza uma célula. Zero é um valor, não ausência — `or` os confunde."""

    if valor is None:
        return "—"
    texto = str(valor).strip()
    return texto if texto else "—"


def _tabela(cabecalho: Sequence[str], linhas: Sequence[Sequence[object]]) -> list[str]:
    if not linhas:
        return ["_Nenhum registro para o período._", ""]
    saida = ["| " + " | ".join(cabecalho) + " |",
             "|" + "|".join("---" for _ in cabecalho) + "|"]
    for linha in linhas:
        saida.append("| " + " | ".join(_celula(celula) for celula in linha) + " |")
    saida.append("")
    return saida


def _dicts(colunas: Sequence[str], linhas: Sequence[Sequence[str]]) -> list[dict[str, str]]:
    return [dict(zip(colunas, linha)) for linha in linhas]


def render_markdown(
    *,
    spec: PeriodSpec,
    escopo: str,
    produto: str,
    emitido_em: date,
    entregas: tuple[Sequence[str], Sequence[Sequence[str]]],
    ciclos: tuple[Sequence[str], Sequence[Sequence[str]]],
    vinculos: tuple[Sequence[str], Sequence[Sequence[str]]],
    painel: tuple[Sequence[str], Sequence[Sequence[str]]],
    unidades_expandidas: Sequence[str] = (),
    procedencia: Mapping[str, str] | None = None,
) -> str:
    entregas_d = _dicts(*entregas)
    ciclos_d = _dicts(*ciclos)
    vinculos_d = _dicts(*vinculos)
    painel_d = _dicts(*painel)
    nominal = produto == "operacional"
    ciclo_nome = _NOME_CICLO.get(spec.ciclo_tipo, spec.ciclo_tipo)

    linhas: list[str] = []
    linhas += [
        "# REGISTRO DE EXECUÇÃO DO PLANO DE ENTREGAS — CGOV/ICMBio",
        "",
        f"**Período:** {spec.rotulo} ({ciclo_nome}) — "
        f"{_br(spec.inicio.isoformat())} a {_br(spec.fim.isoformat())} — "
        f"situação: {spec.status}",
        f"**Escopo:** {escopo}",
        f"**Data de referência da apuração:** {_br(spec.fim_efetivo.isoformat())} "
        "(fim efetivo do período)",
        f"**Data de emissão:** {_br(emitido_em.isoformat())}",
        f"**Produto:** {produto}" + (" (nominal — uso interno)" if nominal else " (sem dados nominais)"),
        "**Base normativa:** IN MGI nº 24/2023 · Portaria ICMBio nº 5.592/2025 · RN-04 · RN-08",
        "",
        "> Insumo técnico de apoio à chefia. Não homologa avaliação, não atribui "
        "conceito e não substitui o registro no PETRVS.",
        "",
    ]

    if spec.status != "encerrado":
        linhas += [
            f"> ⚠️ O período {spec.rotulo} ainda **não encerrou** na janela de análise "
            f"(fim programado {_br(spec.fim.isoformat())}, apurado até "
            f"{_br(spec.fim_efetivo.isoformat())}). Os números são parciais.",
            "",
        ]

    if unidades_expandidas:
        linhas += [
            "> ℹ️ A expansão hierárquica acrescentou unidades subordinadas ao escopo: "
            + ", ".join(unidades_expandidas)
            + ".",
            "",
        ]

    # --- 1
    linhas += ["## 1. Resumo da execução das entregas", ""]
    linhas += _tabela(
        ["Entrega", "Meta pactuada", "Progr. esperado", "Progr. realizado",
         "Desvio (p.p.)", "Prazo", "Situação"],
        [
            [
                registro.get("entrega_titulo") or registro.get("entrega_ref"),
                f"{registro.get('meta_pactuada') or '—'} ({registro.get('meta_tipo')})",
                registro.get("progresso_esperado"),
                registro.get("progresso_realizado"),
                registro.get("desvio_pp"),
                _br(registro.get("entrega_fim")),
                registro.get("situacao"),
            ]
            for registro in entregas_d
        ],
    )
    linhas += [
        "> **Método do percentual.** A apuração usa a **meta pactuada** registrada no "
        "PETRVS (`progresso_esperado` × `progresso_realizado`), nunca a contagem de "
        "etapas ou de atividades concluídas — RN-08 e caderno metodológico §1.3. "
        "Entregas sem meta pactuada aparecem com `meta_tipo = N/D` e **não** contam "
        "como cumpridas.",
        "",
    ]

    anomalias = [r for r in entregas_d if r.get("anomalia_escala")]
    if anomalias:
        linhas += ["### 1.1 Anomalias de escala detectadas", ""]
        linhas += _tabela(
            ["Entrega", "Anomalia"],
            [[r.get("entrega_titulo") or r.get("entrega_ref"), r.get("anomalia_escala")] for r in anomalias],
        )

    # --- 2
    linhas += ["## 2. Checagem de risco por entrega", ""]
    linhas += _tabela(
        ["Entrega", "Semáforo", "Pontuação", "Gatilhos"],
        [
            [
                registro.get("entrega_titulo") or registro.get("entrega_ref"),
                registro.get("semaforo"),
                registro.get("pontuacao_prioridade"),
                registro.get("gatilhos") or "—",
            ]
            for registro in sorted(
                entregas_d,
                key=lambda r: -to_number(r.get("pontuacao_prioridade"), 0.0),
            )
        ],
    )
    linhas += [
        f"{SEMAFORO_OK} rotina · {SEMAFORO_ATENCAO} moderada · {SEMAFORO_ALERTA} alta ou crítica",
        "",
        "> A pontuação é calculada na data de referência do período, não na data de "
        "emissão. Fosse a data de hoje, toda entrega de um período encerrado "
        "dispararia o gatilho de prazo vencido e o semáforo não distinguiria nada.",
        "",
    ]

    # --- 3
    meses = sorted({r["ciclo_rotulo"] for r in ciclos_d}, key=lambda r: (r[-4:], r[1:3]))
    linhas += ["## 3. Verificação RN-04 — ciclos mensais de plano de trabalho", ""]
    linhas += [
        "A conclusão do Plano de Entregas depende de **todos** os planos de trabalho "
        "dos servidores da unidade no período terem sido registrados e avaliados. "
        "Cada célula abaixo é um ciclo mensal.",
        "",
    ]
    por_servidor: dict[tuple[str, str], dict[str, dict[str, str]]] = {}
    for registro in ciclos_d:
        chave = (registro.get("servidor_ref", ""), registro.get("plano_numero", ""))
        por_servidor.setdefault(chave, {})[registro["ciclo_rotulo"]] = registro

    linhas_matriz: list[list[str]] = []
    for (ref, plano), celulas in sorted(por_servidor.items()):
        exemplo = next(iter(celulas.values()))
        identificacao = f"{ref} ({exemplo.get('servidor_nome')})" if nominal else ref
        pendencias = sum(1 for c in celulas.values() if c.get("rn04_bloqueio") == "SIM")
        linhas_matriz.append(
            [identificacao, plano]
            + [(celulas.get(mes) or {}).get("rn04_semaforo", SEMAFORO_NAO_APLICA) for mes in meses]
            + [str(pendencias)]
        )
    linhas += _tabela(["Servidor", "PT"] + meses + ["Pendências"], linhas_matriz)
    linhas += [
        f"{SEMAFORO_OK} avaliado · {SEMAFORO_ATENCAO} enviado, aguardando avaliação da chefia · "
        f"{SEMAFORO_ALERTA} não enviado ou ciclo não aberto · {SEMAFORO_NAO_APLICA} fora da vigência do PT",
        "",
    ]

    bloqueios = [r for r in ciclos_d if r.get("rn04_bloqueio") == "SIM"]
    apto = not bloqueios
    if apto:
        linhas += [
            f"**Veredito:** {SEMAFORO_OK} Não há ciclo mensal pendente. "
            "A RN-04 não oferece obstáculo à conclusão do Plano de Entregas.",
            "",
        ]
    else:
        servidores_afetados = len({r.get("servidor_ref") for r in bloqueios})
        linhas += [
            f"**Veredito:** {SEMAFORO_ALERTA} O Plano de Entregas **NÃO pode ser concluído** — "
            f"{len(bloqueios)} ciclo(s) pendente(s) em {servidores_afetados} servidor(es).",
            "",
            "### 3.1 Bloqueios para a conclusão",
            "",
        ]
        for posicao, registro in enumerate(
            sorted(bloqueios, key=lambda r: (r.get("servidor_ref", ""), r.get("ciclo_rotulo", ""))),
            start=1,
        ):
            quem = registro.get("servidor_ref")
            if nominal:
                quem = f"{quem} ({registro.get('servidor_nome')})"
            linhas.append(
                f"{posicao}. {quem} — {registro.get('ciclo_rotulo')} "
                f"(PT {registro.get('plano_numero')}): {registro.get('acao_sugerida')}"
            )
        linhas.append("")

    # --- 4
    linhas += ["## 4. Força de trabalho declarada por entrega", ""]
    agregado: dict[str, dict[str, float]] = {}
    titulos = {r.get("entrega_ref"): r.get("entrega_titulo") for r in entregas_d}
    for registro in vinculos_d:
        alvo = agregado.setdefault(registro.get("entrega_ref", ""), {"servidores": 0.0, "forca": 0.0, "horas": 0.0})
        alvo["servidores"] += 1
        alvo["forca"] += to_number(registro.get("forca_trabalho_perc"), 0.0)
        alvo["horas"] += to_number(registro.get("horas_contratuais_estimadas"), 0.0)
    linhas += _tabela(
        ["Entrega", "Servidores", "Σ força de trabalho (%)", "Horas contratuais estimadas"],
        [
            [titulos.get(ref) or ref, int(v["servidores"]), f"{v['forca']:.2f}", f"{v['horas']:.2f}"]
            for ref, v in sorted(agregado.items())
        ],
    )
    linhas += [
        "> Capacidade **planejada** em dias corridos, derivada da carga horária e do "
        "campo `forca_trabalho`. Não é esforço realizado — esse vem de "
        "`tempo_despendido`. Caderno metodológico §1.3 (I07).",
        "",
    ]

    # --- 5
    linhas += ["## 5. Painel consolidado por unidade", ""]
    linhas += _tabela(
        ["Unidade", "Entregas", "Com meta", "Cumpridas", "Taxa (%)", "Servidores",
         "Ciclos esperados", "Registrados", "Avaliados", "Pendentes", "Apto (RN-04)"],
        [
            [
                r.get("unidade_sigla"), r.get("entregas_no_periodo"), r.get("entregas_com_meta"),
                r.get("entregas_cumpridas"), r.get("taxa_cumprimento_perc"),
                r.get("servidores_no_periodo"), r.get("ciclos_pt_esperados"),
                r.get("ciclos_pt_registrados"), r.get("ciclos_pt_avaliados"),
                r.get("ciclos_pt_pendentes"), r.get("rn04_apto_conclusao"),
            ]
            for r in painel_d
        ],
    )

    # --- 6
    linhas += [
        "## 6. Instruções para atualização no PETRVS",
        "",
        "### 6.1 Entregas do Plano de Entregas",
        "",
        "1. Acesse **Gestão → Plano de Entregas → [unidade] → [entrega] → Registro de execução**.",
        "2. Para cada entrega da seção 1, informe o **progresso realizado** do período "
        "e a **narrativa da evolução**, com as ocorrências que impactaram o alcance (RN-02).",
        "3. Registre as intercorrências do período no campo próprio, ainda que não "
        "alterem o percentual — elas fundamentam a avaliação posterior pela chefia superior.",
        "4. Ajustes de prazo, meta ou escopo **não** ensejam nova pactuação (RN-05); "
        "exigem comunicação à chefia imediata superior e podem ensejar repactuação dos PT (RN-06).",
        "",
        "### 6.2 Ciclos de plano de trabalho pendentes",
        "",
    ]
    if apto:
        linhas += ["Nenhuma pendência — siga para o fechamento do Plano de Entregas.", ""]
    else:
        linhas += [
            "Resolva **antes** de concluir o Plano de Entregas, na ordem da seção 3.1:",
            "",
            f"- {SEMAFORO_ATENCAO} *aguardando avaliação*: a chefia avalia a consolidação já enviada.",
            f"- {SEMAFORO_ALERTA} *não enviado*: o servidor conclui e envia o registro do período.",
            f"- {SEMAFORO_ALERTA} *ciclo não aberto*: abra o período no PETRVS e peça o registro.",
            "",
        ]
    linhas += [
        "### 6.3 Lista de conferência",
        "",
        "- [ ] Progresso realizado informado em todas as entregas da seção 1",
        "- [ ] Narrativa da evolução registrada por entrega (RN-02)",
        "- [ ] Intercorrências do período registradas",
        "- [ ] Todos os ciclos mensais de PT avaliados (RN-04)",
        "- [ ] Ajustes de prazo/meta comunicados à chefia superior (RN-05)",
        "- [ ] Plano de Entregas concluído no PETRVS",
        "",
    ]

    # --- 7
    linhas += [
        "## 7. Ressalvas metodológicas",
        "",
        f"1. **{spec.rotulo} é um {ciclo_nome}, de {_br(spec.inicio.isoformat())} a "
        f"{_br(spec.fim.isoformat())}.** Os rótulos Q1/Q2/Q3 designam três períodos de "
        "quatro meses por ano — não existe Q4. O texto herdado das planilhas da CGOV "
        "os chamava de trimestres e previa um Q4 implícito; a nomenclatura correta é a "
        "adotada aqui (RN-07).",
        "2. **Calendário institucional pendente de confirmação (C-01/RP20/Q17).** A "
        "página do ciclo da CGGE publica faixas internamente inconsistentes — entre "
        "elas `01/05–30/07` para o segundo período, contra `01/05–31/08` adotado aqui. "
        "Este relatório usa a segmentação implementada e testada em `lib/periodos.py`; "
        "a confirmação da CGGE segue pendente.",
        "3. **Separação PE × PT.** O resultado é medido pela meta da entrega; os planos "
        "de trabalho entram como verificação de execução (RN-04) e como capacidade "
        "planejada (seção 4), nunca como substitutos da meta.",
        "",
    ]

    if procedencia:
        linhas += ["## 8. Procedência", ""]
        linhas += _tabela(
            ["Item", "Valor"], [[chave, valor] for chave, valor in sorted(procedencia.items())]
        )

    linhas += [
        "---",
        "",
        "*Gerado por `gestao/REG_EXEC.1_run.py` — Registro de Execução do Plano de "
        "Entregas (S21). Revisar e assinar antes de qualquer uso oficial.*",
    ]
    return "\n".join(linhas) + "\n"
