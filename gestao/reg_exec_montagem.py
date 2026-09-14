"""Montagem das linhas do produto REG_EXEC a partir dos resultados do Denodo.

Separado do entrypoint `REG_EXEC.1_run.py` porque o nome daquele arquivo tem
ponto e não é importável; aqui as funções são puras (dicionários entram,
listas de linhas saem) e podem ser testadas com fixtures sintéticas, sem
credencial nem JVM.
"""
from __future__ import annotations

import hashlib
from collections import defaultdict
from datetime import date
from typing import Mapping, Sequence

from lib.periodos import PeriodSpec, period_metadata
from ocde.relatorios.textos_execucao import TextSanitizer, priority_assessment

from gestao.reg_exec_regras import (
    anomalia_escala,
    ciclo_dentro_da_vigencia,
    desvio_pp,
    entrega_cumprida,
    horas_contratuais,
    parse_meta,
    prazo_status,
    rn04_situacao,
    semaforo_de_prioridade,
    servidor_refs,
    situacao_entrega,
    taxa_meta_integral,
    to_date,
    to_number,
)


COLUNAS_PESSOAIS = {"servidor_nome"}

ENTREGAS_COLUNAS = (
    "unidade_dona_sigla", "unidade_dona_nome", "unidade_executora_sigla",
    "plano_numero", "plano_status", "entrega_ref", "entrega_titulo",
    "entrega_meta_texto", "entrega_destinatario", "meta_pactuada", "meta_tipo",
    "taxa_meta_integral_perc", "anomalia_escala", "progresso_esperado",
    "progresso_realizado", "desvio_pp", "entrega_inicio", "entrega_fim",
    "prazo_status", "situacao", "pontuacao_prioridade", "prioridade",
    "gatilhos", "semaforo",
)

CICLOS_COLUNAS = (
    "unidade_sigla", "unidade_nome", "unidade_pai_sigla", "servidor_ref",
    "servidor_nome", "plano_numero", "plano_status", "ciclo_rotulo",
    "ciclo_inicio", "ciclo_fim", "consolidacao_status", "ciclo_conclusao",
    "ciclo_avaliacao", "score_avaliacao", "atividades_total",
    "atividades_concluidas", "horas_planejadas", "horas_despendidas",
    "rn04_situacao", "rn04_semaforo", "rn04_bloqueio", "acao_sugerida",
)

VINCULOS_COLUNAS = (
    "unidade_dona_sigla", "unidade_executora_sigla", "servidor_ref",
    "servidor_nome", "plano_entrega_numero", "entrega_ref",
    "plano_trabalho_numero", "plano_trabalho_status", "forca_trabalho_perc",
    "horas_contratuais_estimadas",
)

PAINEL_COLUNAS = (
    "unidade_sigla", "entregas_no_periodo", "entregas_com_meta",
    "entregas_cumpridas", "taxa_cumprimento_perc", "servidores_no_periodo",
    "ciclos_pt_esperados", "ciclos_pt_registrados", "ciclos_pt_avaliados",
    "ciclos_pt_pendentes", "rn04_apto_conclusao",
)


def entrega_ref(entrega_uuid: object) -> str:
    """Referência curta e estável para a entrega, sem exportar o UUID bruto.

    O caderno metodológico §2.4 admite identificador derivado, não o id do
    PETRVS: um UUID no CSV é barrado por ocde/relatorios/privacidade.py e
    reidentifica a linha fora do escopo. O digest é determinístico, então
    a mesma entrega mantém a referência entre quadrimestres.
    """

    bruto = str(entrega_uuid or "").strip()
    if not bruto:
        return ""
    return "E" + hashlib.sha256(bruto.encode("utf-8")).hexdigest()[:10]


def _texto(sanitizer: TextSanitizer | None, valor: object) -> str:
    if sanitizer is None:
        return str(valor or "").strip()
    return sanitizer.sanitize(valor).text


def _celula(valor: object) -> str:
    """Serializa um valor de célula. `str(x or "")` transformaria 0 e 0.0 em
    vazio — e uma pontuação de risco zero é um resultado, não uma ausência."""

    return "" if valor is None else str(valor)


def _fmt(valor: float | None, casas: int = 2) -> str:
    return "" if valor is None else f"{valor:.{casas}f}"


def montar_entregas(
    registros: Sequence[Mapping[str, object]],
    spec: PeriodSpec,
    *,
    sanitizer: TextSanitizer | None = None,
) -> tuple[list[str], list[list[str]]]:
    """Uma linha por entrega do PE vigente no período.

    A data de referência do semáforo é o FIM EFETIVO DO PERÍODO, não hoje: com
    a data corrente toda entrega de um quadrimestre encerrado dispararia o
    gatilho `prazo_vencido_sem_conclusao` e o semáforo perderia o sentido.
    """

    referencia = spec.fim_efetivo
    linhas: list[list[str]] = []
    for registro in registros:
        esperado = to_number(registro.get("progresso_esperado"), 0.0)
        realizado = to_number(registro.get("progresso_realizado"), 0.0)
        meta_valor, meta_tipo = parse_meta(registro.get("meta_json"))
        fim = to_date(registro.get("entrega_fim"))
        prazo = prazo_status(fim, referencia)
        prioridade = priority_assessment(
            {
                "tipo_registro": "PE",
                "status": registro.get("plano_status"),
                "data_fim": registro.get("entrega_fim"),
                "progresso_esperado": esperado,
                "progresso_realizado": realizado,
            },
            referencia,
        )
        valores = {
            "unidade_dona_sigla": registro.get("unidade_dona_sigla"),
            "unidade_dona_nome": registro.get("unidade_dona_nome"),
            "unidade_executora_sigla": registro.get("unidade_executora_sigla"),
            "plano_numero": registro.get("plano_numero"),
            "plano_status": registro.get("plano_status"),
            "entrega_ref": entrega_ref(registro.get("entrega_uuid")),
            "entrega_titulo": _texto(sanitizer, registro.get("entrega_titulo")),
            "entrega_meta_texto": _texto(sanitizer, registro.get("entrega_meta_texto")),
            "entrega_destinatario": _texto(sanitizer, registro.get("entrega_destinatario")),
            "meta_pactuada": _fmt(meta_valor),
            "meta_tipo": meta_tipo,
            "taxa_meta_integral_perc": _fmt(taxa_meta_integral(meta_valor, realizado)),
            "anomalia_escala": anomalia_escala(esperado, meta_valor, meta_tipo),
            "progresso_esperado": _fmt(esperado),
            "progresso_realizado": _fmt(realizado),
            "desvio_pp": _fmt(desvio_pp(esperado, realizado)),
            "entrega_inicio": registro.get("entrega_inicio"),
            "entrega_fim": registro.get("entrega_fim"),
            "prazo_status": prazo,
            "situacao": situacao_entrega(registro.get("plano_status"), esperado, realizado, prazo),
            "pontuacao_prioridade": prioridade["pontuacao_prioridade"],
            "prioridade": prioridade["prioridade"],
            "gatilhos": ";".join(prioridade["gatilhos"]),
            "semaforo": semaforo_de_prioridade(prioridade["prioridade"]),
        }
        linhas.append(spec.as_row() + [_celula(valores[c]) for c in ENTREGAS_COLUNAS])
    return list(period_metadata()) + list(ENTREGAS_COLUNAS), linhas


def _chave_servidor(registro: Mapping[str, object]) -> tuple[str, str]:
    return (
        str(registro.get("unidade_sigla") or "").strip().upper(),
        str(registro.get("servidor_nome") or "").strip(),
    )


def montar_ciclos(
    consolidacoes: Sequence[Mapping[str, object]],
    planos_vigentes: Sequence[Mapping[str, object]],
    spec: PeriodSpec,
    meses: Sequence[PeriodSpec],
    *,
    refs: Mapping[str, str],
) -> tuple[list[str], list[list[str]]]:
    """Matriz servidor x ciclo mensal, com o veredito da RN-04 por célula.

    O universo é o dos PLANOS VIGENTES, não o das consolidações existentes —
    é justamente o ciclo que nunca foi aberto que a RN-04 precisa enxergar, e
    ele não aparece em nenhuma consulta de consolidações.
    """

    por_plano: dict[str, list[Mapping[str, object]]] = defaultdict(list)
    for consolidacao in consolidacoes:
        por_plano[str(consolidacao.get("plano_numero") or "")].append(consolidacao)

    linhas: list[list[str]] = []
    for plano in sorted(
        planos_vigentes,
        key=lambda p: (_chave_servidor(p), str(p.get("plano_numero") or "")),
    ):
        unidade, servidor = _chave_servidor(plano)
        plano_numero = str(plano.get("plano_numero") or "")
        plano_inicio = to_date(plano.get("plano_inicio"))
        plano_fim = to_date(plano.get("plano_fim"))
        for mes in meses:
            dentro = ciclo_dentro_da_vigencia(mes.inicio, mes.fim, plano_inicio, plano_fim)
            consolidacao = _consolidacao_do_mes(por_plano.get(plano_numero, ()), mes)
            avaliada = bool(
                consolidacao
                and (
                    str(consolidacao.get("consolidacao_status") or "").upper() == "AVALIADO"
                    or to_date(consolidacao.get("ciclo_avaliacao")) is not None
                )
            )
            situacao = rn04_situacao(
                (consolidacao or {}).get("consolidacao_status"), avaliada, dentro
            )
            valores = {
                "unidade_sigla": unidade,
                "unidade_nome": plano.get("unidade_nome"),
                "unidade_pai_sigla": plano.get("unidade_pai_sigla"),
                "servidor_ref": refs.get(servidor, ""),
                "servidor_nome": servidor,
                "plano_numero": plano_numero,
                "plano_status": plano.get("plano_status"),
                "ciclo_rotulo": mes.rotulo,
                "ciclo_inicio": mes.inicio.isoformat(),
                "ciclo_fim": mes.fim.isoformat(),
                "consolidacao_status": (consolidacao or {}).get("consolidacao_status") or "",
                "ciclo_conclusao": (consolidacao or {}).get("ciclo_conclusao") or "",
                "ciclo_avaliacao": (consolidacao or {}).get("ciclo_avaliacao") or "",
                "score_avaliacao": (consolidacao or {}).get("score_avaliacao") or "",
                "atividades_total": (consolidacao or {}).get("atividades_total") or "0",
                "atividades_concluidas": (consolidacao or {}).get("atividades_concluidas") or "0",
                "horas_planejadas": (consolidacao or {}).get("horas_planejadas") or "0",
                "horas_despendidas": (consolidacao or {}).get("horas_despendidas") or "0",
                "rn04_situacao": situacao.situacao,
                "rn04_semaforo": situacao.semaforo,
                "rn04_bloqueio": "SIM" if situacao.bloqueia else "NAO",
                "acao_sugerida": situacao.acao,
            }
            linhas.append(spec.as_row() + [_celula(valores[c]) for c in CICLOS_COLUNAS])
    return list(period_metadata()) + list(CICLOS_COLUNAS), linhas


def _consolidacao_do_mes(
    consolidacoes: Sequence[Mapping[str, object]], mes: PeriodSpec
) -> Mapping[str, object] | None:
    """Consolidação que cobre o mês — sobreposição, não igualdade de datas."""

    for consolidacao in consolidacoes:
        inicio = to_date(consolidacao.get("ciclo_inicio"))
        fim = to_date(consolidacao.get("ciclo_fim"))
        if inicio is None or fim is None:
            continue
        if inicio <= mes.fim and fim >= mes.inicio:
            return consolidacao
    return None


def dias_de_sobreposicao(
    plano_inicio: date | None,
    plano_fim: date | None,
    spec: PeriodSpec,
) -> tuple[float | None, float | None]:
    """Dias do plano dentro do período e duração total do plano, inclusivos.

    Calculado em Python de propósito: o Denodo VQL não tem DATEDIFF e a
    subtração de datas varia conforme o wrapper da fonte, então deixar essa
    conta no SQL trocaria um cálculo testável por um ponto cego.
    """

    if plano_inicio is None or plano_fim is None or plano_fim < plano_inicio:
        return (None, None)
    inicio = max(plano_inicio, spec.inicio)
    fim = min(plano_fim, spec.fim_efetivo)
    sobrepostos = (fim - inicio).days + 1 if fim >= inicio else 0
    do_plano = (plano_fim - plano_inicio).days + 1
    return (float(sobrepostos), float(do_plano))


def montar_vinculos(
    registros: Sequence[Mapping[str, object]],
    spec: PeriodSpec,
    *,
    refs: Mapping[str, str],
) -> tuple[list[str], list[list[str]]]:
    """Força de trabalho declarada de cada PT em cada entrega do PE."""

    linhas: list[list[str]] = []
    for registro in registros:
        servidor = str(registro.get("servidor_nome") or "").strip()
        sobrepostos, do_plano = dias_de_sobreposicao(
            to_date(registro.get("plano_inicio")),
            to_date(registro.get("plano_fim")),
            spec,
        )
        horas = horas_contratuais(
            to_number(registro.get("carga_horaria")),
            registro.get("forma_contagem_carga_horaria"),
            sobrepostos,
            do_plano,
            to_number(registro.get("forca_trabalho_perc"), 0.0),
        )
        valores = {
            "unidade_dona_sigla": registro.get("unidade_dona_sigla"),
            "unidade_executora_sigla": registro.get("unidade_executora_sigla"),
            "servidor_ref": refs.get(servidor, ""),
            "servidor_nome": servidor,
            "plano_entrega_numero": registro.get("plano_entrega_numero"),
            "entrega_ref": entrega_ref(registro.get("entrega_uuid")),
            "plano_trabalho_numero": registro.get("plano_trabalho_numero"),
            "plano_trabalho_status": registro.get("plano_trabalho_status"),
            "forca_trabalho_perc": _fmt(to_number(registro.get("forca_trabalho_perc"), 0.0)),
            "horas_contratuais_estimadas": _fmt(horas),
        }
        linhas.append(spec.as_row() + [_celula(valores[c]) for c in VINCULOS_COLUNAS])
    return list(period_metadata()) + list(VINCULOS_COLUNAS), linhas


def montar_painel(
    entregas_cols: Sequence[str],
    entregas_linhas: Sequence[Sequence[str]],
    ciclos_cols: Sequence[str],
    ciclos_linhas: Sequence[Sequence[str]],
    spec: PeriodSpec,
) -> tuple[list[str], list[list[str]]]:
    """Agregado por unidade, com o veredito de aptidão à conclusão (RN-04)."""

    ent_idx = {nome: posicao for posicao, nome in enumerate(entregas_cols)}
    cic_idx = {nome: posicao for posicao, nome in enumerate(ciclos_cols)}

    por_unidade: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    servidores: dict[str, set[str]] = defaultdict(set)

    for linha in entregas_linhas:
        unidade = linha[ent_idx["unidade_dona_sigla"]]
        esperado = to_number(linha[ent_idx["progresso_esperado"]], 0.0)
        realizado = to_number(linha[ent_idx["progresso_realizado"]], 0.0)
        por_unidade[unidade]["entregas_no_periodo"] += 1
        if esperado and esperado > 0:
            por_unidade[unidade]["entregas_com_meta"] += 1
        if entrega_cumprida(esperado, realizado):
            por_unidade[unidade]["entregas_cumpridas"] += 1

    for linha in ciclos_linhas:
        unidade = linha[cic_idx["unidade_sigla"]]
        situacao = linha[cic_idx["rn04_situacao"]]
        if situacao == "fora_da_vigencia":
            continue
        servidores[unidade].add(linha[cic_idx["servidor_ref"]] or linha[cic_idx["plano_numero"]])
        por_unidade[unidade]["ciclos_pt_esperados"] += 1
        if situacao != "ciclo_nao_aberto":
            por_unidade[unidade]["ciclos_pt_registrados"] += 1
        if situacao == "avaliado":
            por_unidade[unidade]["ciclos_pt_avaliados"] += 1
        if linha[cic_idx["rn04_bloqueio"]] == "SIM":
            por_unidade[unidade]["ciclos_pt_pendentes"] += 1

    linhas: list[list[str]] = []
    for unidade in sorted(por_unidade):
        valores = por_unidade[unidade]
        com_meta = valores.get("entregas_com_meta", 0.0)
        cumpridas = valores.get("entregas_cumpridas", 0.0)
        taxa = round(100.0 * cumpridas / com_meta, 2) if com_meta else 0.0
        pendentes = int(valores.get("ciclos_pt_pendentes", 0))
        celulas = {
            "unidade_sigla": unidade,
            "entregas_no_periodo": int(valores.get("entregas_no_periodo", 0)),
            "entregas_com_meta": int(com_meta),
            "entregas_cumpridas": int(cumpridas),
            "taxa_cumprimento_perc": f"{taxa:.2f}",
            "servidores_no_periodo": len(servidores.get(unidade, ())),
            "ciclos_pt_esperados": int(valores.get("ciclos_pt_esperados", 0)),
            "ciclos_pt_registrados": int(valores.get("ciclos_pt_registrados", 0)),
            "ciclos_pt_avaliados": int(valores.get("ciclos_pt_avaliados", 0)),
            "ciclos_pt_pendentes": pendentes,
            "rn04_apto_conclusao": "SIM" if pendentes == 0 else "NAO",
        }
        linhas.append(spec.as_row() + [str(celulas[c]) for c in PAINEL_COLUNAS])
    return list(period_metadata()) + list(PAINEL_COLUNAS), linhas


def remover_colunas_pessoais(
    colunas: Sequence[str], linhas: Sequence[Sequence[str]]
) -> tuple[list[str], list[list[str]]]:
    """Descarta as colunas nominais nos produtos restrito e compartilhável."""

    manter = [posicao for posicao, nome in enumerate(colunas) if nome not in COLUNAS_PESSOAIS]
    return (
        [colunas[posicao] for posicao in manter],
        [[linha[posicao] for posicao in manter] for linha in linhas],
    )
