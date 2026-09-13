"""Registro explícito das análises de gestão homologadas para o ciclo mensal."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from lib.csv_utils import PROJECT_ROOT
from lib.validation_contracts import TARGETS, target_artifact_prefix


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

    @property
    def artifact_prefix(self) -> str:
        """Prefixo dos arquivos gerados: G01 -> IND_GEST_01."""
        return target_artifact_prefix(self.code, "gestao")

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
    # A chave "status-pt" é o nome canônico da skill e do --analise; o código
    # lógico é G01 e os arquivos usam o namespace IND_GEST_01 (D17).
    "status-pt": ManagementExtraction(
        code="G01",
        name="Situação dos Planos de Trabalho",
        entrypoint=TARGETS["G01"].production_entrypoint,
        temporal_lenses=("operacional",),
        supported_scopes=(
            "nacional", "regional", "unidade", "mesogrupo", "tipo-unidade", "lista-unidades"
        ),
        output_schema="IND_GEST_01.v2",
        privacy_class="ambos",
        contains_narrative=False,
        enabled_in_monthly_cycle=True,
        oracle_entrypoint=PROJECT_ROOT / "lib" / "validation_oracles.py",
        atomic_extractors=("pt_status_planos", "pt_status_consolidacoes", "pt_status_transicoes"),
        business_keys=("unidade_sigla", "status_negocio"),
        validation_schema="IND_GEST_01.validation.v1",
        # Derivada do contrato de validação para que as duas declarações não
        # divirjam a cada mudança de fórmula (D14 elevou o G01 a 3.0.0; D17, a 4.0.0).
        formula_version=TARGETS["G01"].formula_version,
        invariants=TARGETS["G01"].invariants,
        tolerances={"counts": 0.0, "percentages": 0.05},
        baseline="HOMOLOGACAO_INICIAL_PENDENTE",
    )
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
