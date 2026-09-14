"""Registro explícito das análises de gestão homologadas para o ciclo mensal."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from lib.csv_utils import PROJECT_ROOT


@dataclass(frozen=True)
class ManagementExtraction:
    code: str
    name: str
    entrypoint: Path
    temporal_lenses: tuple[str, ...]
    supported_scopes: tuple[str, ...]
    output_schema: str
    privacy_class: str
    contains_narrative: bool
    enabled_in_monthly_cycle: bool
    oracle_entrypoint: Path
    atomic_extractors: tuple[str, ...]
    business_keys: tuple[str, ...]
    validation_schema: str
    formula_version: str
    invariants: tuple[str, ...]
    tolerances: dict[str, float]
    baseline: str

    def validate(self) -> list[str]:
        problems: list[str] = []
        if not self.entrypoint.is_file():
            problems.append(f"entrypoint ausente: {self.entrypoint}")
        if not set(self.temporal_lenses) <= {"acumulada", "operacional"}:
            problems.append("lente temporal inválida")
        if self.privacy_class not in {"restrito", "compartilhavel", "ambos"}:
            problems.append("classe de privacidade inválida")
        if not self.oracle_entrypoint.is_file():
            problems.append(f"oracle ausente: {self.oracle_entrypoint}")
        if not self.atomic_extractors:
            problems.append("extrator atômico ausente")
        if not self.business_keys:
            problems.append("chave de negócio ausente")
        if not self.invariants:
            problems.append("invariantes ausentes")
        if self.enabled_in_monthly_cycle and self.baseline not in {
            "HOMOLOGACAO_INICIAL_PENDENTE", "HOMOLOGADO"
        }:
            problems.append("baseline inválida")
        return problems


REGISTRY: dict[str, ManagementExtraction] = {
    "status-pt": ManagementExtraction(
        code="PT_STATUS",
        name="Situação operacional dos Planos de Trabalho",
        entrypoint=PROJECT_ROOT / "gestao" / "PT_STATUS.1_run.py",
        temporal_lenses=("operacional",),
        supported_scopes=(
            "nacional", "regional", "unidade", "mesogrupo", "tipo-unidade", "lista-unidades"
        ),
        output_schema="PT_STATUS.v2",
        privacy_class="ambos",
        contains_narrative=False,
        enabled_in_monthly_cycle=True,
        oracle_entrypoint=PROJECT_ROOT / "lib" / "validation_oracles.py",
        atomic_extractors=("pt_status_planos", "pt_status_consolidacoes", "pt_status_transicoes"),
        business_keys=("unidade_sigla", "status_negocio"),
        validation_schema="PT_STATUS.validation.v1",
        formula_version="2.0.0",
        invariants=("precedencia_consolidacao", "fallback_data_status", "total_subtotais"),
        tolerances={"counts": 0.0, "percentages": 0.05},
        baseline="HOMOLOGACAO_INICIAL_PENDENTE",
    ),
    "registro-execucao-pe": ManagementExtraction(
        code="REG_EXEC",
        name="Registro de execução do Plano de Entregas por período",
        entrypoint=PROJECT_ROOT / "gestao" / "REG_EXEC.1_run.py",
        # A lente continua sendo "acumulada": --periodo é uma dimensão
        # ortogonal à lente. Criar uma lente "periodo" exigiria alargar o
        # vocabulário aceito em validate() e em runner.py --lente, e faria
        # "--lente ambas" deixar de selecionar esta análise no ciclo mensal.
        temporal_lenses=("acumulada",),
        supported_scopes=(
            "nacional", "regional", "unidade", "mesogrupo", "tipo-unidade", "lista-unidades"
        ),
        output_schema="REG_EXEC.v1",
        privacy_class="ambos",
        contains_narrative=True,
        enabled_in_monthly_cycle=True,
        oracle_entrypoint=PROJECT_ROOT / "lib" / "validation_oracles.py",
        atomic_extractors=(
            "reg_exec_entregas", "reg_exec_consolidacoes", "reg_exec_vinculos",
        ),
        business_keys=("periodo", "unidade_sigla"),
        validation_schema="REG_EXEC.validation.v1",
        formula_version="1.0.0",
        invariants=(
            "recorte_dentro_da_janela_cumulativa",
            "meta_pe_nao_derivada_de_atividade",
            "separacao_dono_executora",
            "rn04_cobertura_dos_ciclos",
            "ciclo_fora_da_vigencia_nao_conta",
            "total_subtotais",
        ),
        tolerances={"counts": 0.0, "percentages": 0.05, "hours": 0.01, "scores": 0.01},
        baseline="HOMOLOGACAO_INICIAL_PENDENTE",
    ),
}


def enabled_extractions() -> list[ManagementExtraction]:
    return [item for item in REGISTRY.values() if item.enabled_in_monthly_cycle]


def validate_registry() -> list[str]:
    problems: list[str] = []
    for name, extraction in REGISTRY.items():
        if name != name.lower() or "_" in name:
            problems.append(f"nome não canônico: {name}")
        problems.extend(f"{name}: {problem}" for problem in extraction.validate())
    return problems
