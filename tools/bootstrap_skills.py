"""Materializa o catálogo canônico privado de skills a partir de metadados comuns."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents" / "skills"
MANIFEST = ROOT / ".agents" / "skills-manifest.json"


CATALOG: dict[str, dict[str, str]] = {
    "ciclo-gerencial-mensal": {"class": "orquestracao", "status": "active", "purpose": "Executar o ciclo mensal completo e retomável, com A1–A5 como gates bloqueantes.", "entrypoint": "python -m lib.ciclo_gerencial", "permission": "read-write-private"},
    "relatorio-extracao": {"class": "orquestracao", "status": "active", "purpose": "Conciliar cobertura, arquivos, linhas, janelas e checksums das extrações.", "entrypoint": "manifestos de extração", "permission": "read-private"},
    "extrair-indicadores": {"class": "extracao", "status": "active", "purpose": "Executar A1/A2 de I01–I12, gerar manifesto rastreável e encaminhar ao runner A3–A5.", "entrypoint": "python -m lib.indicator_extraction", "permission": "denodo-read-private-write"},
    "extrair-gestao": {"class": "extracao", "status": "active", "purpose": "Executar análises de gestão somente quando contrato, oracle, fixture e privacidade estiverem registrados.", "entrypoint": "python -m gestao.runner", "permission": "denodo-read-private-write"},
    "verificar-ambiente": {"class": "ambiente", "status": "active", "purpose": "Verificar Python, JVM, driver, variáveis, dependências e caminhos sem revelar segredos.", "entrypoint": "lib.denodo_config e checks locais", "permission": "read-local"},
    "consultar-denodo": {"class": "ambiente", "status": "active", "purpose": "Executar smoke test, catálogo ou VQL estritamente somente leitura.", "entrypoint": "lib.denodo_config", "permission": "denodo-read"},
    "run-pgd-ocde-icmbio": {"class": "ambiente", "status": "alias", "purpose": "Encaminhar o comando legado para ambiente ou consulta Denodo.", "entrypoint": "verificar-ambiente ou consultar-denodo", "permission": "route-only", "successor": "verificar-ambiente"},
    "desenvolver-indicador": {"class": "indicadores", "status": "active", "purpose": "Orquestrar A1–A5 automatizados e pausar somente diante de decisão metodológica ou divergência não explicada.", "entrypoint": "p0-temporal a p5-gerar-a5", "permission": "read-write-private"},
    "p0-temporal": {"class": "indicadores", "status": "component", "purpose": "Validar a periodicidade observada contra as funções temporais oficiais.", "entrypoint": "lib.periodos", "permission": "read-denodo"},
    "p1-ler-docs": {"class": "indicadores", "status": "component", "purpose": "Ler a documentação aplicável antes de alterar um indicador.", "entrypoint": "docs/ocde", "permission": "read-local"},
    "p2-gerar-a1": {"class": "indicadores", "status": "component", "purpose": "Criar ou corrigir o script A1 no padrão Denodo do projeto.", "entrypoint": "ocde/indicadores", "permission": "write-code"},
    "p3-executar-a2": {"class": "indicadores", "status": "component", "purpose": "Executar o A1 e produzir o CSV A2 privado e auditável.", "entrypoint": "ocde/indicadores/IND_OCDE_XX.1_run.py", "permission": "denodo-read-private-write"},
    "p3b-auditar": {"class": "indicadores", "status": "gate", "purpose": "Auditar contrato, independência do oracle, schema, fixture, temporalidade e segurança antes do modo integrado.", "entrypoint": "testes e documentação do indicador", "permission": "read-private"},
    "p4-gerar-a4": {"class": "indicadores", "status": "component", "purpose": "Executar o motor automático de diagnósticos A4 e gerar detalhes apenas para checks acionados.", "entrypoint": "artefatos_local/ocde/diagnosticos", "permission": "read-write-private"},
    "p5-gerar-a5": {"class": "indicadores", "status": "component", "purpose": "Gerar automaticamente o dossiê A5 a partir dos manifestos A1–A4 e do baseline homologado.", "entrypoint": "artefatos_local/validacao", "permission": "read-write-private"},
    "relatorio-gerencial": {"class": "inteligencia-v2", "status": "active", "purpose": "Gerar a V2 por domínios decisórios nos produtos restrito e compartilhável.", "entrypoint": "python -m relatorios.relatorio_v2", "permission": "denodo-read-private-write"},
    "analisar-execucao-pgd": {"class": "inteligencia-v2", "status": "active", "purpose": "Analisar PE, PT, atividades, textos sanitizados, impedimentos e riscos sem misturar resultado e processo.", "entrypoint": "relatorios.analisar_execucao_pgd", "permission": "denodo-read-private-write"},
    "status-pt": {"class": "inteligencia-v2", "status": "active", "purpose": "Produzir fotografia operacional das duas camadas de status dos PT.", "entrypoint": "python gestao/IND_GEST_01/IND_GEST_01.1_run.py", "permission": "denodo-read-private-write"},
    "sumario-executivo": {"class": "inteligencia-v2", "status": "active", "purpose": "Sintetizar decisões, riscos, unidades e entregas prioritárias com evidências.", "entrypoint": "relatório V2 gerado", "permission": "read-private-write"},
    "graficos-gerenciais": {"class": "inteligencia-v2", "status": "active", "purpose": "Gerar visualizações dos domínios V2 e do apêndice OCDE.", "entrypoint": "CSVs e manifestos V2", "permission": "read-private-write"},
    "graficos-indicadores": {"class": "inteligencia-v2", "status": "alias", "purpose": "Preservar compatibilidade e encaminhar para gráficos gerenciais.", "entrypoint": "graficos-gerenciais", "permission": "route-only", "successor": "graficos-gerenciais"},
    "analisar-eixo1": {"class": "inteligencia-v2", "status": "compatibility", "purpose": "Mapear o eixo histórico 1 para capacidade, modalidades e distribuição.", "entrypoint": "analisar-execucao-pgd", "permission": "route-only", "successor": "analisar-execucao-pgd"},
    "analisar-eixo2": {"class": "inteligencia-v2", "status": "compatibility", "purpose": "Mapear o eixo histórico 2 para planejamento e resultados dos PE.", "entrypoint": "analisar-execucao-pgd", "permission": "route-only", "successor": "analisar-execucao-pgd"},
    "analisar-eixo3": {"class": "inteligencia-v2", "status": "compatibility", "purpose": "Mapear o eixo histórico 3 para execução dos PT e capacidade.", "entrypoint": "analisar-execucao-pgd", "permission": "route-only", "successor": "analisar-execucao-pgd"},
    "analisar-eixo4": {"class": "inteligencia-v2", "status": "compatibility", "purpose": "Mapear o eixo histórico 4 para avaliação e coerência PE × PT.", "entrypoint": "analisar-execucao-pgd", "permission": "route-only", "successor": "analisar-execucao-pgd"},
    "analisar-indicadores": {"class": "inteligencia-v2", "status": "deprecated", "purpose": "Manter o alias histórico de visualização durante a migração.", "entrypoint": "graficos-gerenciais", "permission": "route-only", "successor": "graficos-gerenciais"},
    "verificar-consistencia": {"class": "qualidade", "status": "gate", "purpose": "Executar testes unitários, diferenciais, metamórficos, drift, privacidade, retomada e rastreabilidade.", "entrypoint": "python -m lib.validation_runner --modo fixture; python -m pytest", "permission": "read-private"},
    "auditar-seguranca": {"class": "qualidade", "status": "gate", "purpose": "Detectar credenciais, PII, caminhos pessoais e artefatos indevidos.", "entrypoint": "python tools/security_audit.py e relatorios.privacidade", "permission": "read-private"},
    "validar-periodicidade": {"class": "qualidade", "status": "gate", "purpose": "Confirmar janela cumulativa, ciclos e separação das lentes temporais.", "entrypoint": "lib.periodos e testes temporais", "permission": "read-local"},
    "validar-skills": {"class": "qualidade", "status": "active", "purpose": "Validar pacotes, instalar links e certificar as três ferramentas.", "entrypoint": "python tools/skills_manager.py", "permission": "read-write-private"},
    "atualizar-docs": {"class": "governanca", "status": "active", "purpose": "Atualizar fichas, metodologia V2 e documentação das análises de gestão.", "entrypoint": "docs e CLAUDE.md", "permission": "write-docs"},
    "reconciliar-docs": {"class": "governanca", "status": "active", "purpose": "Comparar documentação, código, A5, manifestos e catálogo de skills.", "entrypoint": "docs, código e manifestos", "permission": "read-private"},
    "petrvs-reports": {"class": "inteligencia-v2", "status": "deprecated", "purpose": "Preservar referência histórica ao antigo gerador de relatórios PETRVS.", "entrypoint": "relatorio-gerencial", "permission": "route-only", "successor": "relatorio-gerencial"},
}


def description(name: str, spec: dict[str, str]) -> str:
    return f"{spec['purpose']} Use quando a solicitação corresponder exatamente a essa finalidade no projeto PGD/OCDE do ICMBio."


def skill_text(name: str, spec: dict[str, str]) -> str:
    successor = spec.get("successor", "")
    route = f"\nSkill sucessora: `{successor}`. Apenas encaminhe para ela.\n" if successor else ""
    return f"""---
name: {name}
description: {description(name, spec)}
---

# {name}

Finalidade: {spec['purpose']}

Quando usar: quando o pedido mencionar essa operação ou quando ela for uma
etapa explícita do workflow que a contém. Não usar para tarefas adjacentes nem
para ampliar permissões. {route}

Entrada obrigatória: parâmetros explícitos do usuário e, quando houver
temporalidade, `--data-execucao AAAA-MM-DD`. Nunca calcular períodos diretamente
com `date.today()`.

Entrypoint canônico: `{spec['entrypoint']}`. A skill não duplica SQL, fórmula ou
driver. Leia a documentação e o código desse entrypoint antes de agir.

Permissão: `{spec['permission']}`. Consultas Denodo são somente leitura. Não
publique CSVs, dados pessoais, credenciais ou artefatos da área privada.

Saída: resultado verificável, caminhos dos artefatos privados pertinentes e
status dos gates. Falhas não podem ser convertidas em sucesso parcial.

Qualidade: valide janela, schema, ausência de PII/segredos e comportamento com
fixture sintética. No ciclo mensal, setembro/2026 deve resultar em
01/07/2025–31/08/2026.
"""


def prompts(name: str, spec: dict[str, str]) -> dict[str, list[str]]:
    purpose = spec["purpose"].rstrip(".")
    return {
        "positive": [
            f"Use {name} para {purpose.lower()}.",
            f"Execute explicitamente a skill {name} com dados sintéticos.",
            f"Valide a saída produzida por {name}.",
            f"Faça um dry-run de {name} para setembro de 2026.",
            f"Aplique {name} no escopo GR2 sem expor dados pessoais.",
        ],
        "negative": [
            "Explique apenas o conceito de PGD, sem executar tarefas.",
            "Altere uma fórmula de indicador não relacionada.",
            "Publique dados pessoais de servidores.",
            "Execute uma consulta de escrita no banco.",
            "Faça uma tarefa geral fora do projeto PGD/OCDE.",
        ],
    }


def _gravar(caminho: Path, conteudo: str, forcar: bool, preservados: list[str]) -> None:
    """Grava só arquivo novo ou idêntico; o existente e diferente é preservado sem ``--forcar``.

    O manifesto e os SKILL.md privados evoluíram depois da materialização (L4d): regravar
    tudo a partir deste catálogo seria regressão.
    """
    if caminho.exists():
        if caminho.read_text(encoding="utf-8") == conteudo:
            return  # igual: não regrava (evita trocar só as quebras de linha)
        if not forcar:
            preservados.append(str(caminho.relative_to(ROOT)))
            return
    caminho.write_text(conteudo, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--forcar", action="store_true",
                        help="regrava também SKILL.md, prompts e manifesto existentes e diferentes")
    args = parser.parse_args(argv)
    preservados: list[str] = []
    SKILLS.mkdir(parents=True, exist_ok=True)
    legacy = SKILLS / "petrvs_reports"
    if legacy.exists() and not (SKILLS / "petrvs-reports").exists():
        shutil.move(str(legacy), str(SKILLS / "petrvs-reports"))
    for name, spec in CATALOG.items():
        directory = SKILLS / name
        directory.mkdir(parents=True, exist_ok=True)
        _gravar(directory / "SKILL.md", skill_text(name, spec), args.forcar, preservados)
        if spec["status"] in {"active", "gate"}:
            tests = directory / "tests"
            tests.mkdir(exist_ok=True)
            _gravar(tests / "prompts.json", json.dumps(prompts(name, spec), ensure_ascii=False, indent=2),
                    args.forcar, preservados)
    manifest = {
        "schema_version": 1,
        "canonical_root": ".agents/skills",
        "supported_tools": {
            "codex": {"channel": "pinned-and-latest-stable"},
            "claude-code": {"channel": "pinned-and-latest-stable"},
            "antigravity": {"channel": "pinned-and-latest-stable"},
        },
        "quality": {
            "positive_prompts": 5,
            "negative_prompts": 5,
            "synthetic_fixtures": True,
            "denodo_integration": "read-only-opt-in",
            "certification_required": True,
        },
        "migration": {
            "petrvs_reports": "petrvs-reports",
            "graficos-indicadores": "graficos-gerenciais",
            "analisar-indicadores": "graficos-gerenciais",
            "run-pgd-ocde-icmbio": "verificar-ambiente|consultar-denodo",
        },
        "skills": {name: {**spec, "version": "2.0.0", "tools": ["codex", "claude-code", "antigravity"]} for name, spec in CATALOG.items()},
    }
    _gravar(MANIFEST, json.dumps(manifest, ensure_ascii=False, indent=2), args.forcar, preservados)
    print(f"{len(CATALOG)} skills materializadas em {SKILLS}")
    if preservados:
        print(f"{len(preservados)} arquivos existentes e diferentes preservados (use --forcar para regravar):")
        for caminho in preservados:
            print(f"  {caminho}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
