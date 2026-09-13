"""Contratos executáveis do protocolo automatizado A1--A5.

Este módulo descreve *o que* deve ser validado. As fórmulas independentes
vivem em :mod:`lib.validation_oracles` e os scripts A1 continuam sendo a
implementação de produção. Manter as duas implementações separadas é uma
condição de independência do protocolo.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .csv_utils import PROJECT_ROOT


APPROVAL_STATES = (
    "HOMOLOGACAO_INICIAL_PENDENTE",
    "CERTIFICADO_AUTOMATICAMENTE",
    "AGUARDANDO_DECISAO",
    "FALHA_TECNICA",
    "REPROVADO",
    "HOMOLOGADO",
)

COMMON_PERIOD_COLUMNS = (
    "ciclo_tipo",
    "periodo",
    "periodo_inicio",
    "periodo_fim",
    "periodo_fim_efetivo",
    "periodo_status",
    "duracao_dias",
)


@dataclass(frozen=True)
class Tolerances:
    counts: float = 0.0
    percentages: float = 0.05
    hours: float = 0.01
    scores: float = 0.01


@dataclass(frozen=True)
class DriftPolicy:
    null_warning_pp: float = 5.0
    null_blocking_pp: float = 15.0
    volume_warning_pct: float = 30.0
    volume_blocking_pct: float = 60.0
    psi_warning: float = 0.20
    psi_blocking: float = 0.30


@dataclass(frozen=True)
class OutputContract:
    pattern: str
    required_columns: tuple[str, ...]
    business_keys: tuple[str, ...]
    metrics: tuple[str, ...]
    view: str = "principal"
    allow_empty: bool = False


@dataclass(frozen=True)
class ValidationTarget:
    code: str
    family: str
    name: str
    production_entrypoint: Path
    oracle_name: str
    atomic_extractors: tuple[str, ...]
    outputs: tuple[OutputContract, ...]
    formula_version: str
    temporal_lenses: tuple[str, ...]
    supported_scopes: tuple[str, ...]
    invariants: tuple[str, ...]
    tolerances: Tolerances = field(default_factory=Tolerances)
    drift_policy: DriftPolicy = field(default_factory=DriftPolicy)
    privacy_class: str = "restrito"
    baseline: str = "HOMOLOGACAO_INICIAL_PENDENTE"
    enabled_in_monthly_cycle: bool = True

    def as_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["production_entrypoint"] = str(
            self.production_entrypoint.relative_to(PROJECT_ROOT)
        )
        return value

    def validate(self) -> list[str]:
        problems: list[str] = []
        if self.family not in {"ocde", "gestao"}:
            problems.append("família inválida")
        if self.baseline not in APPROVAL_STATES:
            problems.append("baseline inválida")
        if not self.production_entrypoint.is_file():
            problems.append(f"entrypoint ausente: {self.production_entrypoint}")
        if not self.outputs:
            problems.append("contrato de saída ausente")
        for output in self.outputs:
            missing_keys = set(output.business_keys) - set(output.required_columns)
            if missing_keys:
                problems.append(
                    f"{output.view}: chaves fora do schema: {sorted(missing_keys)}"
                )
            missing_metrics = set(output.metrics) - set(output.required_columns)
            if missing_metrics:
                problems.append(
                    f"{output.view}: métricas fora do schema: {sorted(missing_metrics)}"
                )
        return problems


def _periodic(*columns: str) -> tuple[str, ...]:
    return COMMON_PERIOD_COLUMNS + columns


SCOPE_ALL = (
    "nacional",
    "regional",
    "unidade",
    "mesogrupo",
    "tipo-unidade",
    "lista-unidades",
)


def _indicator(
    number: str,
    name: str,
    extractor: str | tuple[str, ...],
    columns: tuple[str, ...],
    keys: tuple[str, ...],
    metrics: tuple[str, ...],
    *,
    period: str = "pe",
    baseline: str = "HOMOLOGACAO_INICIAL_PENDENTE",
) -> ValidationTarget:
    extractors = (extractor,) if isinstance(extractor, str) else extractor
    return ValidationTarget(
        code=f"I{number}",
        family="ocde",
        name=name,
        production_entrypoint=PROJECT_ROOT / "ocde" / "indicadores" / f"IND_{number}.1_run.py",
        oracle_name=f"oracle_i{number}",
        atomic_extractors=extractors,
        outputs=(OutputContract(f"IND_{number}.2_*.csv", columns, keys, metrics),),
        formula_version="2.0.0",
        temporal_lenses=(period,),
        supported_scopes=SCOPE_ALL,
        invariants=(
            "ordem_invariante",
            "idempotencia",
            "fora_da_janela_sem_efeito",
            "soft_delete_sem_efeito",
            "chave_unica",
            "total_subtotais",
        ),
        baseline=baseline,
    )


TARGETS: dict[str, ValidationTarget] = {}

# I01 possui duas visões e, por isso, é declarado separadamente.
TARGETS["I01"] = ValidationTarget(
    code="I01",
    family="ocde",
    name="Proporção por regime de trabalho",
    production_entrypoint=PROJECT_ROOT / "ocde" / "indicadores" / "IND_01.1_run.py",
    oracle_name="oracle_i01",
    atomic_extractors=("pt_modalidade",),
    outputs=(
        OutputContract(
            "IND_01.2_v1_*.csv",
            _periodic("modalidade", "total_servidores", "proporcao_perc"),
            ("periodo", "modalidade"),
            ("total_servidores", "proporcao_perc"),
            view="institucional",
        ),
        OutputContract(
            "IND_01.2_v2_*.csv",
            _periodic(
                "unidade_sigla", "unidade_nome", "mesogrupo", "modalidade",
                "total_servidores", "proporcao_na_unidade_perc",
            ),
            ("periodo", "unidade_sigla", "modalidade"),
            ("total_servidores", "proporcao_na_unidade_perc"),
            view="unidade",
        ),
    ),
    formula_version="2.0.0",
    temporal_lenses=("pt",),
    supported_scopes=SCOPE_ALL,
    invariants=("deduplicacao_servidor_mes", "total_subtotais", "ordem_invariante"),
    baseline="HOMOLOGACAO_INICIAL_PENDENTE",
)

TARGETS.update({
    "I02": _indicator(
        "02", "Taxa de cumprimento das entregas", "pe_entregas",
        _periodic(
            "unidade_sigla", "unidade_nome", "mesogrupo", "total_cadastradas",
            "total_no_ciclo", "total_vence_no_periodo", "proporcao_vence_no_periodo_perc",
            "total_concluidas", "taxa_cumprimento_perc", "total_em_plano_avaliado",
            "concluidas_em_plano_avaliado", "grupo_performance", "alerta_avaliacao",
        ),
        ("periodo", "unidade_sigla"),
        ("total_no_ciclo", "total_concluidas", "taxa_cumprimento_perc"),
    ),
    "I03": _indicator(
        "03", "Taxa de cumprimento de metas por entrega", "pe_entregas",
        _periodic(
            "unidade_sigla", "unidade_nome", "mesogrupo", "id_entrega", "nome_entrega",
            "descricao_entrega", "progresso_esperado_bruto", "anomalia_escala",
            "meta_planejada", "meta_executada", "taxa_atingimento_perc", "status_entrega",
            "meta_json", "realizado_json", "taxa_meta_integral_perc", "status_meta_integral",
            "tipo_meta",
        ),
        ("periodo", "unidade_sigla", "id_entrega"),
        ("meta_planejada", "meta_executada", "taxa_atingimento_perc"),
    ),
    "I04": _indicator(
        "04", "Score médio de atingimento de metas", "pe_entregas",
        _periodic(
            "unidade_sigla", "unidade_nome", "mesogrupo", "total_cadastradas",
            "total_no_ciclo", "score_atingimento_perc", "total_em_plano_avaliado",
            "grupo_performance", "alerta_avaliacao",
        ),
        ("periodo", "unidade_sigla"),
        ("total_no_ciclo", "score_atingimento_perc"),
    ),
    "I05": _indicator(
        "05", "Distribuição de entregas por servidor", "pt_entregas_executor",
        _periodic(
            "unidade_sigla", "unidade_nome", "mesogrupo", "id_servidor", "nome_servidor",
            "qtd_entregas_por_servidor", "media_entregas_por_servidor_unidade",
            "posicao_relativa_media",
        ),
        ("periodo", "unidade_sigla", "id_servidor"),
        ("qtd_entregas_por_servidor", "media_entregas_por_servidor_unidade"),
        period="pt",
    ),
    "I06": _indicator(
        "06", "Grau de responsabilidade por entrega", "pt_entregas_executor",
        _periodic(
            "unidade_sigla", "unidade_nome", "mesogrupo", "tamanho_grupo_responsavel",
            "total_entregas_na_categoria", "total_entregas_unidade", "pct_categoria",
        ),
        ("periodo", "unidade_sigla", "tamanho_grupo_responsavel"),
        ("total_entregas_na_categoria", "total_entregas_unidade", "pct_categoria"),
        period="pt",
    ),
    "I07": _indicator(
        "07", "Horas planejadas por entrega", "pt_entregas_dono",
        _periodic(
            "unidade_sigla", "unidade_nome", "mesogrupo", "id_entrega", "nome_entrega",
            "id_plano_entrega", "inicio_vigencia_plano_entrega", "fim_vigencia_plano_entrega",
            "total_horas_planejadas_entrega", "num_servidores_alocados",
        ),
        ("periodo", "unidade_sigla", "id_entrega"),
        ("total_horas_planejadas_entrega", "num_servidores_alocados"),
    ),
    "I08": _indicator(
        "08", "Proporção de horas por entrega",
        ("pt_entregas_dono", "pt_capacidade_unidade"),
        _periodic(
            "unidade_sigla", "unidade_nome", "mesogrupo", "id_entrega", "nome_entrega",
            "horas_planejadas_entrega", "total_horas_disponiveis_unidade",
            "proporcao_horas_perc",
        ),
        ("periodo", "unidade_sigla", "id_entrega"),
        ("horas_planejadas_entrega", "total_horas_disponiveis_unidade", "proporcao_horas_perc"),
    ),
    "I09": _indicator(
        "09", "Média da avaliação do PT", "avaliacoes_pt",
        _periodic(
            "unidade_sigla", "unidade_nome", "mesogrupo", "total_avaliacoes_pt",
            "total_planos_com_avaliacao", "total_servidores_avaliados", "media_nota_pt",
            "nota_minima", "nota_maxima", "qtd_nota_1", "qtd_nota_2", "qtd_nota_3",
            "qtd_nota_4", "qtd_nota_5", "faixa_desempenho",
        ),
        ("periodo", "unidade_sigla"),
        ("total_avaliacoes_pt", "total_planos_com_avaliacao", "media_nota_pt"),
        period="pt",
    ),
    "I10": _indicator(
        "10", "Percentual de avaliações inadequadas", "avaliacoes_pt",
        _periodic(
            "unidade_sigla", "unidade_nome", "mesogrupo", "total_avaliacoes_pt",
            "total_servidores_avaliados", "qtd_inadequado", "perc_inadequado", "nivel_alerta",
        ),
        ("periodo", "unidade_sigla"),
        ("total_avaliacoes_pt", "qtd_inadequado", "perc_inadequado"),
        period="pt",
    ),
    "I11": _indicator(
        "11", "Percentual de avaliações excepcionais", "avaliacoes_pt",
        _periodic(
            "unidade_sigla", "unidade_nome", "mesogrupo", "total_avaliacoes_pt",
            "total_servidores_avaliados", "qtd_excepcional", "perc_excepcional",
            "nivel_reconhecimento",
        ),
        ("periodo", "unidade_sigla"),
        ("total_avaliacoes_pt", "qtd_excepcional", "perc_excepcional"),
        period="pt",
    ),
    "I12": _indicator(
        "12", "Coerência entre avaliação PT e PE", ("avaliacoes_pt", "avaliacoes_pe"),
        _periodic(
            "unidade_sigla", "unidade_nome", "mesogrupo", "total_avaliacoes_pt",
            "total_servidores_avaliados", "media_nota_pt", "total_avaliacoes_pe",
            "media_nota_pe", "diferenca_absoluta", "diferenca_direcional",
            "classificacao_coerencia", "direcao_divergencia",
        ),
        ("periodo", "unidade_sigla"),
        ("media_nota_pt", "media_nota_pe", "diferenca_absoluta", "diferenca_direcional"),
    ),
})

TARGETS["PT_STATUS"] = ValidationTarget(
    code="PT_STATUS",
    family="gestao",
    name="Situação operacional dos Planos de Trabalho",
    production_entrypoint=PROJECT_ROOT / "gestao" / "PT_STATUS.1_run.py",
    oracle_name="oracle_pt_status",
    atomic_extractors=("pt_status_planos", "pt_status_consolidacoes", "pt_status_transicoes"),
    outputs=(
        OutputContract(
            "PT_STATUS.2_painel_*.csv",
            ("unidade_sigla", "status_negocio", "qtd_planos"),
            ("unidade_sigla", "status_negocio"),
            ("qtd_planos",),
            view="painel",
        ),
    ),
    formula_version="2.0.0",
    temporal_lenses=("operacional",),
    supported_scopes=SCOPE_ALL,
    invariants=("precedencia_consolidacao", "fallback_data_status", "total_subtotais"),
    privacy_class="ambos",
)


def selected_targets(family: str = "todas", target: str = "todos") -> list[ValidationTarget]:
    normalized = target.strip().upper().replace("IND_", "I")
    if normalized not in {"TODOS", *TARGETS}:
        raise ValueError(f"Alvo de validação desconhecido: {target}")
    values = list(TARGETS.values()) if normalized == "TODOS" else [TARGETS[normalized]]
    if family != "todas":
        values = [item for item in values if item.family == family]
    return [item for item in values if item.enabled_in_monthly_cycle]


def validate_registry() -> list[str]:
    problems: list[str] = []
    for code, target in TARGETS.items():
        if code != target.code:
            problems.append(f"{code}: código divergente")
        problems.extend(f"{code}: {problem}" for problem in target.validate())
    return problems
