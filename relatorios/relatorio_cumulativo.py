"""CLI do relatório gerencial cumulativo, por escopo e anonimizado."""
from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Iterable, Mapping
from zoneinfo import ZoneInfo

from lib.csv_utils import PROJECT_ROOT
from lib.denodo_config import connect, get_config
from lib.periodos import analysis_window, configure_execution_context
from relatorios.dados_gerenciais import (
    cumulative_summary,
    load_all,
    people_count,
    people_counts_by_unit,
    scoped_data,
    temporal_summary,
)
from lib.liberacao import exigir_execucao_autorizada
from lib.validation_contracts import TARGETS
from relatorios.escopo import ScopeSpec, load_unit_profiles, scope_from_values
from relatorios.expansao import load_state, register_execution, save_state
from relatorios.pdf_export import export_pdf
from relatorios.privacidade import K_MIN, assert_safe_outputs, count_band, eligible, forbidden_fields, quantity_band, review_longitudinal, scan_text
from relatorios.registros_execucao import extract_execution


TZ = ZoneInfo("America/Sao_Paulo")
INPUT_BASE = PROJECT_ROOT / "artefatos_local" / "ocde" / "entregas"
OUTPUT_BASE = PROJECT_ROOT / "artefatos_local" / "relatorios"
STATE_PATH = OUTPUT_BASE / "expansao_status.json"


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Gera relatório gerencial cumulativo e anonimizado do PGD.")
    result.add_argument("--data-execucao", required=True, help="AAAA-MM-DD; o mês corrente é excluído.")
    scope = result.add_mutually_exclusive_group(required=True)
    scope.add_argument("--escopo", choices=["nacional"])
    scope.add_argument("--regional")
    scope.add_argument("--unidade")
    scope.add_argument("--mesogrupo")
    scope.add_argument("--tipo-unidade")
    scope.add_argument("--lista-unidades", type=Path)
    result.add_argument("--reextrair", action="store_true", help="Executa novamente I01–I12 antes do relatório.")
    result.add_argument("--salvar", action="store_true", help="Grava Markdown, CSVs e manifesto na área privada.")
    result.add_argument("--pdf", action="store_true", help="Também gera e valida PDF; implica --salvar.")
    result.add_argument("--registrar-validacao-gerencial", action="store_true")
    result.add_argument("--registrar-validacao-lgpd", action="store_true")
    result.add_argument("--aprovar-nacional", action="store_true")
    result.add_argument("--reconciliar-nacional", action="store_true")
    return result


def _write_csv(path: Path, rows: list[dict[str, str]], window_text: str) -> None:
    if not rows:
        raise ValueError(f"Não há linhas para gravar em {path.name}.")
    fields = ["periodo_analise"] + list(rows[0])
    blocked = forbidden_fields(fields)
    if blocked:
        raise RuntimeError("Colunas proibidas no produto: " + ", ".join(blocked))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="|")
        writer.writeheader()
        for row in rows:
            writer.writerow({"periodo_analise": window_text, **row})


def _table(headers: list[str], rows: Iterable[Iterable[object]]) -> str:
    header = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(str(value) for value in row) + " |" for row in rows]
    return "\n".join([header, separator, *body])


def _safe_scope_label(scope: ScopeSpec, people: int) -> str:
    if scope.kind != "nacional" and not eligible(people):
        return "Escopo selecionado — identificação suprimida por k<5"
    return scope.label


def _source_extraction_time(paths: Iterable[Path]) -> str:
    latest = max(path.stat().st_mtime for path in paths)
    return datetime.fromtimestamp(latest, TZ).isoformat(timespec="seconds")


def _validate_temporal(window, temporal: list[dict[str, str]]) -> list[str]:
    problems: list[str] = []
    for row in temporal:
        start = row.get("periodo_inicio", "")
        end = row.get("periodo_fim_efetivo", "")
        if start and start < window.inicio.isoformat():
            problems.append(f"{row['indicador']} contém início anterior à janela")
        if end and end > window.fim.isoformat():
            problems.append(f"{row['indicador']} contém fim posterior à janela")
        if window.mes_execucao == "2026-09" and row.get("periodo") in {"Q3-2026", "M09-2026"}:
            problems.append(f"Período proibido na edição 2026-09: {row['periodo']}")
    return sorted(set(problems))


def _comparison_rows(loaded, profiles, scope_summary) -> list[list[str]]:
    national_scope = scope_from_values(escopo="nacional")
    national = cumulative_summary(scoped_data(loaded, national_scope, profiles))
    national_by_code = {row["indicador"]: row for row in national}
    result = []
    for row in scope_summary:
        if row["indicador"] in {"I02", "I04", "I09", "I10", "I11"}:
            result.append([
                row["indicador"], row["resultado"],
                national_by_code.get(row["indicador"], {}).get("resultado", "N/D"),
            ])
    return result


def _render_report(
    *, window, scope_label: str, people: int, unit_count: int,
    cumulative: list[dict[str, str]], temporal: list[dict[str, str]],
    comparisons: list[list[str]], extraction_time: str, sources: int,
    excluded: int, phase: str, execution_rows: list[dict[str, str]],
) -> str:
    window_text = f"{window.inicio.strftime('%d/%m/%Y')}–{window.fim.strftime('%d/%m/%Y')}"
    published = sum(row["situacao_divulgacao"] == "publicado" for row in cumulative)
    suppressed = sum(row["situacao_divulgacao"] == "suprimido_k" for row in cumulative)
    unavailable = sum(row["situacao_divulgacao"] == "sem_dados" for row in cumulative)
    panel = _table(
        ["Indicador", "Medida", "Resultado", "Observações", "Pessoas", "Divulgação"],
        ([row["indicador"], row["medida"], row["resultado"], row["observacoes_faixa"],
          row["servidores_distintos_faixa"], row["situacao_divulgacao"]] for row in cumulative),
    )
    trends = _table(
        ["Indicador", "Ciclo", "Status", "Resultado", "Observações", "Pessoas"],
        ([row["indicador"], row["periodo"], row["periodo_status"], row["resultado"],
          row["observacoes_faixa"], row["servidores_distintos_faixa"]] for row in temporal),
    )
    comparison = _table(["Indicador", "Escopo", "Instituto"], comparisons) if comparisons else "Comparação não aplicável ao escopo nacional."
    execution = "Registros de execução ainda não reextraídos nesta edição. Use `--reextrair`."
    if execution_rows:
        execution = _table(
            ["Nível", "Unidade", "PE", "Entregas", "Cumprimento", "PT", "PT concluídos", "Atividades", "Atividades concluídas", "Consolidações", "Avaliadas", "Aguardando avaliação"],
            ([row["nivel_agregacao"], row["unidade_sigla"], row["planos_entregas_faixa"],
              row["entregas_faixa"], row["cumprimento_entregas"], row["planos_trabalho_faixa"],
              row["pt_concluidos_percentual"], row["atividades_faixa"], row["atividades_concluidas_percentual"],
              row["consolidacoes_faixa"], row["consolidacoes_avaliadas_percentual"],
              row["aguardando_avaliacao_faixa"]]
             for row in execution_rows),
        )
    return f"""# Relatório Gerencial Cumulativo do PGD

- **Escopo:** {scope_label}
- **Janela analítica:** {window_text}
- **Mês de execução:** {window.mes_execucao}
- **Extração observada em:** {extraction_time}
- **Classificação:** produto agregado e anonimizado; sem dados pessoais.

## 1. Escopo, janela e fonte

A edição usa exclusivamente fatos com referência entre **{window_text}**. O mês de execução não integra a análise. Correções retroativas dentro da janela são aceitas e rastreadas pelo momento da extração. Foram localizadas {sources}/12 fontes de indicadores.

## 2. Sumário executivo acumulado

O painel possui {published} indicadores divulgáveis, {suppressed} suprimidos por k e {unavailable} indisponíveis por cobertura/histórico. O universo de pessoas aparece somente como faixa: **{count_band(people)}**. Semáforos e alertas são triagem gerencial, não juízo normativo nem avaliação individual.

## 3. Cobertura organizacional e dos dados

- Unidades com registro no recorte: {quantity_band(unit_count)}.
- Pessoas distintas: {count_band(people)}.
- Linhas-fonte fora da janela descartadas antes da análise: {quantity_band(excluded)}.
- A cobertura não equivale a qualidade integral do preenchimento; lacunas do PETRVS permanecem limitações da fonte.

## 4. Painel I01–I12

{panel}

## 5. Execução acumulada dos PE e entregas

I02–I04 tratam o alcance das entregas e metas próprias dos Planos de Entregas. I07–I08 mostram esforço planejado associado. Estados parciais sem histórico temporal confiável não devem ser usados como reconstrução retroativa.

{execution}

## 6. Execução acumulada dos PT, atividades e consolidações

I01, I05–I06 e I09–I12 sintetizam modalidade, distribuição, responsabilidade e avaliações. A conclusão de uma atividade do PT é medida de processo e **não** comprova, isoladamente, o cumprimento da meta pactuada no PE.

## 7. Evolução por ciclo e mês

{trends}

## 8. Comparação com o Instituto

{comparison}

Comparações por tipo de unidade, mesogrupo ou lista usam os mesmos seletores, janela e limiar de divulgação; células abaixo do limiar permanecem suprimidas.

## 9. Insights cruzados PE × PT

- Interpretar I02/I04 em conjunto com I05–I08 para verificar se volume, responsabilidade e esforço planejado acompanham o alcance das metas.
- Interpretar I09–I12 como evidência avaliativa estruturada, sem convertê-la em avaliação individual.
- Divergências entre atividades concluídas e metas do PE devem ser investigadas como diferença entre processo e resultado.

## 10. Riscos operacionais e oportunidades

- Risco de estado retroativo: campos atuais sem trilha histórica não representam automaticamente a situação na data de corte.
- Risco de cobertura: ausência ou atraso de consolidação e avaliação altera denominadores.
- Oportunidade: usar tendências persistentes, com cobertura adequada, para priorizar apoio às unidades.

## 11. Recomendações gerenciais

- Validar unidades com alertas em mais de um ciclo antes de qualquer intervenção.
- Separar problemas de cadastro, distribuição de esforço, conclusão de atividades e alcance da meta do PE.
- Registrar decisões e correções de fonte para que a edição seguinte explique mudanças retroativas.

## 12. Metodologia temporal, anonimização e qualidade

A janela inicia fixamente em 01/07/2025 e termina no último dia do mês anterior à execução, no fuso America/Sao_Paulo. Identificadores são usados somente em memória para deduplicação; não são gravados. Métricas ligadas a pessoas exigem **k≥{K_MIN}**; contagens são apresentadas em faixas, percentuais com uma casa decimal e células de baixo volume são suprimidas. A combinação unidade × período × modalidade/status deve ser reavaliada a cada edição e longitudinalmente. Para I09–I12, a coluna Pessoas registra a faixa mínima comprovável em uma única unidade e ciclo; unidades e ciclos não são somados, prevenindo dupla contagem.

Referências: [Lei nº 13.709/2018](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709compilado.htm) e [estudo técnico da ANPD sobre anonimização](https://www.gov.br/anpd/pt-br/centrais-de-conteudo/documentos-tecnicos-orientativos/estudo_tecnico_sobre_anonimizacao_de_dados_na_lgpd_uma_visao_de_processo_baseado_em_risco_e_tecnicas_computacionais.pdf/@@display-file/file).

## 13. Expansão obrigatória

Fase registrada: **{phase}**. A aprovação técnica do piloto GR2 não encerra o projeto: ainda são obrigatórias a execução nacional aprovada, a reconciliação e a validação dos seletores de unidade, mesogrupo, tipo de unidade e lista arbitrária.

---
Janela analítica {window_text} · edição {window.mes_execucao} · conteúdo anonimizado
"""


def reextrair_indicadores(window) -> None:
    """``--reextrair``: roda os A1 OCDE do contrato na área de saída já apontada por
    ``PGD_INDICATOR_OUTPUT_BASE`` (temporária, em memória).

    Antes do L4e, chamava um driver de skill privado e inexistente no repositório.
    Falha de qualquer A1 interrompe o relatório (D33).
    """
    for target in TARGETS.values():
        if target.family != "ocde":
            continue
        command = [sys.executable, str(target.production_entrypoint),
                   "--data-execucao", window.data_execucao.isoformat(), "--month", window.mes_execucao]
        subprocess.run(command, cwd=PROJECT_ROOT, env=os.environ.copy(), check=True)


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    window = configure_execution_context(args.data_execucao)
    scope = scope_from_values(
        escopo=args.escopo, regional=args.regional, unidade=args.unidade,
        mesogrupo=args.mesogrupo, tipo_unidade=args.tipo_unidade,
        lista_unidades=args.lista_unidades,
    )
    # Produto agregado e anonimizado, portanto compartilhável: fora dos pilotos exige
    # elegibilidade (L5). A comparação nacional interna é referência, não escopo.
    exigir_execucao_autorizada(
        "relatorios.relatorio_cumulativo", scope, "compartilhavel",
        capacidades=("RELATORIO_CUMULATIVO", *(code for code in TARGETS if code.startswith("I"))), final=True,
    )
    temporary_source = None
    if args.reextrair:
        memory_root = Path(os.environ.get("PGD_VOLATILE_TMP", "/dev/shm"))
        if not memory_root.is_dir():
            raise RuntimeError("A reextração anonimizada exige uma área temporária em memória (/dev/shm ou PGD_VOLATILE_TMP).")
        temporary_source = tempfile.TemporaryDirectory(prefix="pgd-relatorio-", dir=memory_root)
        os.environ["PGD_INDICATOR_OUTPUT_BASE"] = temporary_source.name
        reextrair_indicadores(window)

    month_dir = (
        Path(temporary_source.name) / window.mes_execucao
        if temporary_source else INPUT_BASE / window.mes_execucao
    )
    if not month_dir.exists():
        raise FileNotFoundError(f"Pasta mensal não encontrada: {month_dir}")
    loaded = load_all(month_dir, window)
    profiles = load_unit_profiles()
    data = scoped_data(loaded, scope, profiles)
    people = people_count(data.get("05", []))
    units = {str(row.get("unidade_sigla") or "") for rows in data.values() for row in rows if row.get("unidade_sigla")}
    mapped_units = {
        str(row.get("unidade_sigla") or "")
        for rows in data.values() for row in rows
        if row.get("unidade_sigla") and str(row.get("mesogrupo") or "").strip().upper() not in {"", "NÃO MAPEADO", "NAO MAPEADO"}
    }
    unmapped_units = sorted(units - mapped_units)
    cumulative = cumulative_summary(data)
    temporal = temporal_summary(data)
    longitudinal_warnings = review_longitudinal(
        OUTPUT_BASE, window.mes_execucao, scope.kind, cumulative
    )
    execution_rows: list[dict[str, str]] = []
    if args.reextrair:
        config = get_config(require_credentials=True)
        connection = connect(config)
        try:
            execution_rows = extract_execution(
                connection, window, scope, profiles,
                people_counts_by_unit(data.get("05", [])), people,
            )
        finally:
            connection.close()
    validation_problems = _validate_temporal(window, temporal)
    comparisons = _comparison_rows(loaded, profiles, cumulative) if scope.kind != "nacional" else []
    extraction_time = _source_extraction_time(item.path for item in loaded.values())
    excluded = sum(item.excluded_outside_window for item in loaded.values())
    technical_ok = (
        len(loaded) == 12
        and not validation_problems
        and not unmapped_units
        and bool(execution_rows)
        and args.pdf
    )

    state = load_state(STATE_PATH)
    disclosed_scope_value = scope.value if eligible(people) or scope.kind == "nacional" else "SUPRIMIDO_K"
    state = register_execution(
        state, scope_kind=scope.kind, scope_value=disclosed_scope_value,
        month=window.mes_execucao, technical_ok=technical_ok,
        management_review=args.registrar_validacao_gerencial,
        privacy_review=args.registrar_validacao_lgpd,
        national_approved=args.aprovar_nacional,
        national_reconciled=args.reconciliar_nacional,
    )
    report = _render_report(
        window=window, scope_label=_safe_scope_label(scope, people), people=people,
        unit_count=len(units), cumulative=cumulative, temporal=temporal,
        comparisons=comparisons, extraction_time=extraction_time,
        sources=len(loaded), excluded=excluded, phase=state["fase"], execution_rows=execution_rows,
    )
    privacy_findings = scan_text(report)
    if privacy_findings:
        raise RuntimeError("Validação de privacidade do relatório falhou: " + "; ".join(privacy_findings))
    if not (args.salvar or args.pdf):
        print(report)
        if temporary_source:
            temporary_source.cleanup()
            os.environ.pop("PGD_INDICATOR_OUTPUT_BASE", None)
        return 0

    output_dir = OUTPUT_BASE / window.mes_execucao
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = scope.kind
    window_text = f"{window.inicio.isoformat()}_a_{window.fim.isoformat()}"
    md_path = output_dir / f"relatorio_gerencial_{slug}_{window.mes_execucao}.md"
    cumulative_path = output_dir / f"indicadores_acumulados_{slug}_{window.mes_execucao}.csv"
    temporal_path = output_dir / f"indicadores_temporais_{slug}_{window.mes_execucao}.csv"
    manifest_path = output_dir / f"manifesto_{slug}_{window.mes_execucao}.json"
    md_path.write_text(report, encoding="utf-8")
    _write_csv(cumulative_path, cumulative, window_text)
    _write_csv(temporal_path, temporal, window_text)
    execution_path = None
    if execution_rows:
        execution_path = output_dir / f"execucao_acumulada_{slug}_{window.mes_execucao}.csv"
        _write_csv(execution_path, execution_rows, window_text)
    manifest = {
        **window.as_dict(),
        "data_hora_extracao": extraction_time,
        "data_hora_geracao": datetime.now(TZ).isoformat(timespec="seconds"),
        "fuso_horario": "America/Sao_Paulo",
        "escopo": {
            **scope.as_dict(),
            "valor": disclosed_scope_value,
        },
        "fontes_indicadores": sorted(f"I{code}" for code in loaded),
        "fontes_execucao": ["PE", "entregas", "PT", "atividades", "consolidacoes", "transicoes_status"] if execution_rows else [],
        "arquivos_fonte": [item.path.name for item in loaded.values()],
        "anonimizacao": {
            "k_minimo": K_MIN,
            "identificadores_persistidos": False,
            "datas_individuais_persistidas": False,
            "contagens_em_faixas": True,
            "percentuais_casas_decimais": 1,
            "celulas_suprimidas": (
                sum(row["situacao_divulgacao"] != "publicado" for row in cumulative)
                + sum(row["situacao_divulgacao"] != "publicado" for row in temporal)
            ),
            "celulas_acumuladas_suprimidas": sum(
                row["situacao_divulgacao"] != "publicado" for row in cumulative
            ),
            "celulas_temporais_suprimidas": sum(
                row["situacao_divulgacao"] != "publicado" for row in temporal
            ),
            "revisao_longitudinal_executada": True,
            "alertas_longitudinais": longitudinal_warnings,
        },
        "validacao_temporal": {"aprovada": not validation_problems, "problemas": validation_problems},
        "validacao_organizacional": {
            "aprovada": not unmapped_units,
            "unidades_nao_reconciliadas_faixa": quantity_band(len(unmapped_units)),
        },
        "validacao_registros_execucao": bool(execution_rows),
        "validacao_tecnica": technical_ok,
        "fase_expansao": state["fase"],
        "projeto_concluido": state["projeto_concluido"],
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    outputs = [md_path, cumulative_path, temporal_path, manifest_path]
    if execution_path:
        outputs.append(execution_path)
    if args.pdf:
        pdf_path = output_dir / f"relatorio_gerencial_{slug}_{window.mes_execucao}.pdf"
        export_pdf(report, pdf_path, f"Relatório PGD · {window_text}")
        outputs.append(pdf_path)

    assert_safe_outputs(outputs)

    # Só persiste o avanço depois que todos os produtos foram materializados.
    save_state(STATE_PATH, state)
    if temporary_source:
        temporary_source.cleanup()
        os.environ.pop("PGD_INDICATOR_OUTPUT_BASE", None)
    print("Produtos gerados:")
    for path in outputs:
        print(f"- {path}")
    if validation_problems:
        raise RuntimeError("Validação temporal falhou: " + "; ".join(validation_problems))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
