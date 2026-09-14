"""Regras determinísticas do registro de execução do Plano de Entregas.

Funções puras, sem I/O e sem Denodo: recebem valores já extraídos e devolvem
as derivações do produto REG_EXEC. Ficam separadas do entrypoint justamente
para que a regra da RN-04 — a que decide se um Plano de Entregas pode ou não
ser concluído — seja testável com fixtures sintéticas.

Base normativa:
  RN-04  a conclusão do PE depende de todos os PT dos servidores da unidade
         no período terem sido devidamente executados;
  RN-08  o progresso esperado é do planejamento e o registro informa o
         progresso realizado — os dois nunca se confundem.
Caderno metodológico §1.3: conclusão de atividade ou de PT não substitui a
meta própria da entrega do PE.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime


# Estados da consolidação mensal do PT no PETRVS (camada de avaliação).
CONSOLIDACAO_ABERTA = "INCLUIDO"
CONSOLIDACAO_ENVIADA = "CONCLUIDO"
CONSOLIDACAO_AVALIADA = "AVALIADO"

SEMAFORO_OK = "🟢"
SEMAFORO_ATENCAO = "🟡"
SEMAFORO_ALERTA = "🔴"
SEMAFORO_NAO_APLICA = "⬜"

# priority_assessment() devolve 4 níveis; o relatório exibe 3 cores.
_SEMAFORO_POR_PRIORIDADE = {
    "crítica": SEMAFORO_ALERTA,
    "alta": SEMAFORO_ALERTA,
    "moderada": SEMAFORO_ATENCAO,
    "rotina": SEMAFORO_OK,
}


def semaforo_de_prioridade(prioridade: str) -> str:
    return _SEMAFORO_POR_PRIORIDADE.get(str(prioridade).strip().lower(), SEMAFORO_OK)


def to_number(value: object, default: float | None = None) -> float | None:
    """Converte valor de CSV/JDBC em float, tolerando vazio e vírgula decimal."""

    if value is None:
        return default
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    text = str(value).strip()
    if not text:
        return default
    try:
        return float(text.replace(",", "."))
    except ValueError:
        return default


def to_date(value: object) -> date | None:
    """Converte valor de CSV/JDBC em date, tolerando datetime e string vazia."""

    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Meta pactuada da entrega
# ---------------------------------------------------------------------------

def parse_meta(meta_json: object) -> tuple[float | None, str]:
    """Lê o campo `meta` do PETRVS: {"quantitativo": N} ou {"porcentagem": P}.

    Nunca levanta exceção: JSON malformado ou ausente devolve (None, "N/D"),
    porque uma entrega sem meta legível precisa aparecer no registro como
    pendência — não sumir dele.
    """

    if meta_json is None:
        return (None, "N/D")
    if isinstance(meta_json, dict):
        payload: object = meta_json
    else:
        text = str(meta_json).strip()
        if not text:
            return (None, "N/D")
        try:
            payload = json.loads(text)
        except (ValueError, TypeError):
            valor = to_number(text)
            return (valor, "quantitativo") if valor is not None else (None, "N/D")
    if not isinstance(payload, dict):
        valor = to_number(payload)
        return (valor, "quantitativo") if valor is not None else (None, "N/D")
    for chave in ("quantitativo", "porcentagem"):
        if chave in payload:
            valor = to_number(payload[chave])
            if valor is not None:
                return (valor, chave)
    return (None, "N/D")


def taxa_meta_integral(meta: float | None, realizado: float | None) -> float | None:
    """(realizado / meta) x 100. Denominador zero ou ausente devolve None."""

    if meta is None or realizado is None or meta <= 0:
        return None
    return round(100.0 * realizado / meta, 2)


def desvio_pp(esperado: float | None, realizado: float | None) -> float | None:
    """Desvio em pontos percentuais, com sinal: realizado − esperado."""

    if esperado is None or realizado is None:
        return None
    return round(realizado - esperado, 2)


def entrega_cumprida(esperado: float | None, realizado: float | None) -> bool:
    """Mesmo critério de ocde/relatorios/registros_execucao.py.

    Uma entrega sem progresso esperado pactuado (0 ou nulo) nunca conta como
    cumprida — é o que impede que meta não pactuada vire cumprimento gratuito.
    """

    if esperado is None or realizado is None:
        return False
    return esperado > 0 and realizado >= esperado


def anomalia_escala(
    progresso_esperado: float | None,
    meta_valor: float | None,
    meta_tipo: str,
) -> str:
    """Sinaliza divergência de escala entre `progresso_esperado` e `meta`.

    O AT-01 §2.4 documenta que o PETRVS mistura escalas 0–1 e 0–100 e chega a
    ter valores negativos. Aqui a divergência é exportada, nunca resolvida em
    silêncio escolhendo um dos dois campos.
    """

    problemas: list[str] = []
    for rotulo, valor in (("progresso_esperado", progresso_esperado),):
        if valor is not None and valor < 0:
            problemas.append(f"{rotulo}_negativo")
    if meta_valor is not None and meta_valor < 0:
        problemas.append("meta_negativa")
    if meta_tipo == "porcentagem" and meta_valor is not None and meta_valor > 100:
        problemas.append("meta_percentual_acima_de_100")
    if (
        meta_tipo == "porcentagem"
        and meta_valor is not None
        and progresso_esperado is not None
        and 0 < meta_valor <= 1
        and progresso_esperado > 1
    ):
        problemas.append("escalas_divergentes_0a1_vs_0a100")
    return ";".join(problemas)


def prazo_status(entrega_fim: date | None, referencia: date) -> str:
    """Situação do prazo da entrega na data de referência da apuração."""

    if entrega_fim is None:
        return "sem_prazo_cadastrado"
    if entrega_fim < referencia:
        return "vencido"
    if entrega_fim == referencia:
        return "vence_na_referencia"
    return "vigente"


def situacao_entrega(
    plano_status: object,
    esperado: float | None,
    realizado: float | None,
    prazo: str,
) -> str:
    """Situação da entrega para o registro de execução."""

    status = str(plano_status or "").strip().upper()
    if status == "CANCELADO":
        return "cancelada"
    if status == "SUSPENSO":
        return "suspensa"
    valor = realizado or 0.0
    if entrega_cumprida(esperado, realizado):
        return "concluida" if prazo != "vencido" else "concluida_com_ressalva"
    if valor <= 0:
        return "nao_iniciada"
    return "em_andamento"


# ---------------------------------------------------------------------------
# Verificação RN-04 — ciclos mensais de PT
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SituacaoCiclo:
    """Resultado da avaliação de um ciclo mensal de PT de um servidor."""

    situacao: str
    semaforo: str
    bloqueia: bool
    conta_como_esperado: bool
    acao: str


def rn04_situacao(
    consolidacao_status: object,
    avaliada: bool,
    dentro_da_vigencia: bool,
) -> SituacaoCiclo:
    """Decide o estado de um ciclo mensal de PT perante a RN-04.

    Atenção ao caso `CONCLUIDO`: no PETRVS ele significa "o servidor enviou e
    está aguardando a avaliação da chefia" — ou seja, ainda bloqueia a
    conclusão do PE. Tratá-lo como resolvido é o erro silencioso mais fácil
    de cometer aqui.
    """

    if not dentro_da_vigencia:
        return SituacaoCiclo(
            situacao="fora_da_vigencia",
            semaforo=SEMAFORO_NAO_APLICA,
            bloqueia=False,
            conta_como_esperado=False,
            acao="Mês fora da vigência do plano de trabalho — nada a fazer.",
        )
    status = str(consolidacao_status or "").strip().upper()
    if avaliada or status == CONSOLIDACAO_AVALIADA:
        return SituacaoCiclo(
            situacao="avaliado",
            semaforo=SEMAFORO_OK,
            bloqueia=False,
            conta_como_esperado=True,
            acao="",
        )
    if status == CONSOLIDACAO_ENVIADA:
        return SituacaoCiclo(
            situacao="aguardando_avaliacao",
            semaforo=SEMAFORO_ATENCAO,
            bloqueia=True,
            conta_como_esperado=True,
            acao="Chefia deve avaliar a consolidação já enviada pelo servidor.",
        )
    if status == CONSOLIDACAO_ABERTA:
        return SituacaoCiclo(
            situacao="nao_enviado",
            semaforo=SEMAFORO_ALERTA,
            bloqueia=True,
            conta_como_esperado=True,
            acao="Servidor deve concluir e enviar o registro do período.",
        )
    if not status:
        return SituacaoCiclo(
            situacao="ciclo_nao_aberto",
            semaforo=SEMAFORO_ALERTA,
            bloqueia=True,
            conta_como_esperado=True,
            acao="Nenhuma consolidação para o mês — abrir o ciclo no PETRVS.",
        )
    return SituacaoCiclo(
        situacao=f"status_nao_previsto:{status.lower()}",
        semaforo=SEMAFORO_ATENCAO,
        bloqueia=True,
        conta_como_esperado=True,
        acao=f"Status {status} não previsto na RN-04 — verificar manualmente.",
    )


def ciclo_dentro_da_vigencia(
    ciclo_inicio: date,
    ciclo_fim: date,
    plano_inicio: date | None,
    plano_fim: date | None,
) -> bool:
    """O mês é exigível para este PT? Exige sobreposição com a vigência.

    Admissão, exoneração e cessão no meio do quadrimestre são a razão de ser
    desta função: cobrar de um servidor um ciclo anterior à vigência do seu
    plano produziria pendência inexistente e um veredito falso-negativo.
    """

    if plano_inicio is not None and plano_inicio > ciclo_fim:
        return False
    if plano_fim is not None and plano_fim < ciclo_inicio:
        return False
    return True


# ---------------------------------------------------------------------------
# Capacidade contratual declarada (PT -> entrega)
# ---------------------------------------------------------------------------

def horas_contratuais(
    carga_horaria: float | None,
    forma_contagem: object,
    dias_sobrepostos: float | None,
    dias_plano: float | None,
    forca_trabalho_perc: float | None,
) -> float | None:
    """Estimativa de capacidade planejada, proporcional à sobreposição.

    NÃO é esforço realizado — esse vem de `tempo_despendido` das atividades.
    O caderno metodológico §1.3 separa resultado (PE) de capacidade (PT); usar
    este número como execução seria exatamente a confusão que ele proíbe.
    """

    if carga_horaria is None or not dias_plano or dias_sobrepostos is None:
        return None
    if dias_plano <= 0:
        return None
    horas = carga_horaria * 8 if str(forma_contagem or "").strip().upper() == "DIAS" else carga_horaria
    proporcao_periodo = max(0.0, min(1.0, dias_sobrepostos / dias_plano))
    fracao_entrega = (forca_trabalho_perc or 0.0) / 100.0
    return round(horas * proporcao_periodo * fracao_entrega, 2)


def servidor_refs(nomes: list[str]) -> dict[str, str]:
    """Pseudônimos SERVIDOR_01..NN, estáveis dentro de uma mesma execução.

    Escopo de execução, não identidade persistente: se a composição da equipe
    mudar, os rótulos mudam. É deliberado — ocde/relatorios/privacidade.py já
    declara que a redação não persiste pseudônimos —, mas impede comparar
    edições diferentes pelo rótulo.
    """

    unicos = sorted({str(nome).strip() for nome in nomes if str(nome).strip()})
    return {nome: f"SERVIDOR_{posicao:02d}" for posicao, nome in enumerate(unicos, start=1)}
