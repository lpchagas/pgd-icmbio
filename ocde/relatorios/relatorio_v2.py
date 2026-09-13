"""Relatório Gerencial V2: PE, PT, riscos, textos sanitizados e apêndice OCDE."""
from __future__ import annotations

import argparse
import ast
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from lib.csv_utils import PROJECT_ROOT
from lib.denodo_config import connect, get_config
from lib.periodos import ANALYSIS_TIMEZONE, configure_execution_context
from ocde.relatorios.analisar_execucao_pgd import SQL_NAMES, extract_textual_evidence
from ocde.relatorios.dados_gerenciais import (
    cumulative_summary,
    load_all,
    people_counts_by_unit,
    scoped_data,
    temporal_summary,
)
from ocde.relatorios.escopo import load_unit_profiles, scope_from_values
from ocde.relatorios.pdf_export import export_pdf
from ocde.relatorios.privacidade import K_MIN, assert_safe_outputs
from ocde.relatorios.textos_execucao import TextSanitizer
from lib.monthly_runner import query_rows


INPUT_BASE = PROJECT_ROOT / "artefatos_local" / "ocde" / "entregas"
OUTPUT_BASE = PROJECT_ROOT / "artefatos_local" / "ocde" / "relatorios_v2"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-execucao", required=True)
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--escopo", choices=("nacional",))
    scope.add_argument("--regional")
    scope.add_argument("--unidade")
    scope.add_argument("--mesogrupo")
    scope.add_argument("--tipo-unidade")
    scope.add_argument("--lista-unidades", type=Path)
    parser.add_argument("--produto", choices=("restrito", "compartilhavel", "ambos"), default="ambos")
    parser.add_argument("--lente", choices=("acumulada", "operacional", "ambas"), default="ambas")
    parser.add_argument("--consultar-denodo", action="store_true", help="Opt-in para extrair textos e estado operacional.")
    parser.add_argument("--salvar", action="store_true")
    parser.add_argument("--pdf", action="store_true")
    return parser


def _escape(value: object, limit: int | None = None) -> str:
    text = str(value or "").replace("|", "\\|").replace("\n", " ").strip()
    return text if limit is None or len(text) <= limit else text[: limit - 1] + "…"


def _table(headers: list[str], rows: list[list[object]]) -> str:
    if not rows:
        return "Sem registros elegíveis para esta visão."
    result = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    result.extend("| " + " | ".join(_escape(value) for value in row) + " |" for row in rows)
    return "\n".join(result)


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    fields = list(rows[0])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="|", extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({
                key: ",".join(str(item) for item in value) if isinstance(value, (list, tuple)) else value
                for key, value in row.items()
            })


def _load_evidence(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="|"))
    for row in rows:
        row["pontuacao_prioridade"] = int(row.get("pontuacao_prioridade") or 0)
        raw = str(row.get("gatilhos") or "").strip()
        if raw.startswith("["):
            try:
                parsed = ast.literal_eval(raw)
                row["gatilhos"] = [str(item) for item in parsed] if isinstance(parsed, list) else []
            except (SyntaxError, ValueError):
                row["gatilhos"] = []
        else:
            row["gatilhos"] = [item.strip() for item in raw.split(",") if item.strip()]
    return rows


def _eligible_shared(
    evidence: list[dict[str, object]], people_by_unit: dict[str, int]
) -> list[dict[str, object]]:
    result = []
    for row in evidence:
        units = {
            str(row.get(key) or "").strip().upper()
            for key in ("unidade_dona_sigla", "unidade_executora_sigla")
            if str(row.get(key) or "").strip()
        }
        if units and all(people_by_unit.get(unit, 0) >= K_MIN for unit in units):
            result.append(row)
    return result


def _unit_priorities(evidence: list[dict[str, object]]) -> list[dict[str, object]]:
    totals: dict[str, dict[str, object]] = defaultdict(
        lambda: {"registros": 0, "criticos": 0, "altos": 0, "pontos": 0, "gatilhos": Counter()}
    )
    for row in evidence:
        unit = str(row.get("unidade_dona_sigla") or row.get("unidade_executora_sigla") or "SEM_UNIDADE")
        item = totals[unit]
        item["registros"] = int(item["registros"]) + 1
        item["pontos"] = int(item["pontos"]) + int(row.get("pontuacao_prioridade") or 0)
        if row.get("prioridade") == "crítica":
            item["criticos"] = int(item["criticos"]) + 1
        if row.get("prioridade") == "alta":
            item["altos"] = int(item["altos"]) + 1
        item["gatilhos"].update(row.get("gatilhos") or [])  # type: ignore[union-attr]
    result = []
    for unit, item in totals.items():
        triggers = item.pop("gatilhos")
        result.append({
            "unidade": unit,
            **item,
            "gatilhos_principais": ", ".join(name for name, _ in triggers.most_common(3)),
        })
    return sorted(result, key=lambda row: (-int(row["criticos"]), -int(row["pontos"]), str(row["unidade"])))


def render_report(
    *, window, scope_label: str, product: str, cumulative: list[dict[str, str]],
    temporal: list[dict[str, str]], evidence: list[dict[str, object]], denodo_used: bool,
    evidence_origin: str = "indisponível",
) -> str:
    priorities = _unit_priorities(evidence)
    pe = [row for row in evidence if row.get("tipo_registro") == "PE"]
    pt = [row for row in evidence if row.get("tipo_registro") in {"PT", "ATIVIDADE"}]
    pe_priority = Counter(str(row.get("prioridade") or "") for row in pe)
    pt_priority = Counter(str(row.get("prioridade") or "") for row in pt)
    pt_status = Counter(str(row.get("status") or "Não informado") for row in pt)
    lens_counts = Counter(str(row.get("lente") or "") for row in evidence)
    cross_unit = sum(
        bool(row.get("unidade_dona_sigla"))
        and bool(row.get("unidade_executora_sigla"))
        and row.get("unidade_dona_sigla") != row.get("unidade_executora_sigla")
        for row in evidence
    )
    trigger_counts = Counter(trigger for row in evidence for trigger in (row.get("gatilhos") or []))
    recommendations = []
    mapping = {
        "prazo_vencido_sem_conclusao": "Pactuar plano de recuperação, responsável e nova data de controle.",
        "meta_pe_abaixo_do_pactuado": "Validar o resultado registrado no PE e tratar causas da diferença para a meta.",
        "status_operacional_requer_acao": "Destravar assinatura, ativação ou retomada do PT conforme o status.",
        "esforco_acima_do_planejado": "Revisar estimativa, capacidade e distribuição do esforço do PT.",
    }
    for trigger, count in trigger_counts.most_common():
        recommendations.append([trigger, count, mapping.get(trigger, "Analisar causa e pactuar tratamento.")])
    priority_table = _table(
        ["Unidade", "Registros", "Críticos", "Altos", "Pontos", "Gatilhos"],
        [[row["unidade"], row["registros"], row["criticos"], row["altos"], row["pontos"], row["gatilhos_principais"]]
         for row in priorities[:30]],
    )
    evidence_table = _table(
        ["Prioridade", "Tipo", "Dona", "Executora", "Plano", "Prazo", "Status", "Descrição sanitizada", "Gatilhos"],
        [[row.get("prioridade"), row.get("tipo_registro"), row.get("unidade_dona_sigla"),
          row.get("unidade_executora_sigla"), row.get("plano_numero"), row.get("data_fim"),
          row.get("status"), _escape(row.get("texto_principal"), 180), ", ".join(row.get("gatilhos") or [])]
         for row in evidence[:40]],
    )
    appendix = _table(
        ["Indicador", "Medida", "Resultado", "Observações", "Pessoas", "Divulgação"],
        [[row["indicador"], row["medida"], row["resultado"], row["observacoes_faixa"],
          row["servidores_distintos_faixa"], row["situacao_divulgacao"]] for row in cumulative],
    )
    trends = _table(
        ["Indicador", "Período", "Situação", "Resultado"],
        [[row["indicador"], row["periodo"], row["periodo_status"], row["resultado"]] for row in temporal],
    )
    pe_attention = _table(
        ["Prioridade", "Unidade dona", "Unidade executora", "Plano", "Prazo", "Progresso", "Entrega", "Gatilhos"],
        [[row.get("prioridade"), row.get("unidade_dona_sigla"), row.get("unidade_executora_sigla"),
          row.get("plano_numero"), row.get("data_fim"),
          f"{row.get('progresso_realizado', '')}/{row.get('progresso_esperado', '')}",
          _escape(row.get("texto_principal"), 220), ", ".join(row.get("gatilhos") or [])]
         for row in pe if row.get("prioridade") in {"crítica", "alta"}][:30],
    )
    pt_attention = _table(
        ["Prioridade", "Unidade executora", "Plano", "Prazo", "Status", "Atividade/vínculo", "Gatilhos"],
        [[row.get("prioridade"), row.get("unidade_executora_sigla"), row.get("plano_numero"),
          row.get("data_fim"), row.get("status"), _escape(row.get("texto_principal"), 220),
          ", ".join(row.get("gatilhos") or [])]
         for row in pt if row.get("prioridade") in {"crítica", "alta"}][:30],
    )
    status_table = _table(
        ["Status PT/atividade", "Registros"],
        [[status, count] for status, count in pt_status.most_common()],
    )
    return f"""# Relatório Gerencial V2 — Execução do PGD

- **Escopo:** {scope_label}
- **Produto:** {product}
- **Janela acumulada:** {window.inicio.strftime('%d/%m/%Y')} a {window.fim.strftime('%d/%m/%Y')}
- **Fotografia operacional:** {window.data_execucao.strftime('%d/%m/%Y')}
**Origem das evidências:** {evidence_origin}

## 1. Síntese decisória

Foram analisados {len(pe)} registros de resultado de PE e {len(pt)} registros de processo de PT/atividades. A lente acumulada contém {lens_counts.get('acumulada', 0)} evidências e a fotografia operacional contém {lens_counts.get('operacional', 0)}. Há {cross_unit} registros em que unidade dona e executora diferem. A priorização é uma triagem transparente baseada em prazo, diferença para a meta do PE, status que requer ação e esforço acima do planejado; ela não substitui avaliação gerencial.

## 2. Unidades que demandam atenção

{priority_table}

## 3. Resultados dos Planos de Entregas

O resultado do PE é apurado exclusivamente pelos campos próprios de meta e progresso. Atividades de PT não são usadas como prova de cumprimento da entrega. Entre os registros de PE, {pe_priority.get('crítica', 0)} foram classificados como críticos e {pe_priority.get('alta', 0)} como altos. Os gatilhos mostram a causa objetiva da triagem; a descrição sanitizada permite ao gerente identificar qual entrega deve ser conferida no PETRVS.

{pe_attention}

## 4. Execução dos Planos de Trabalho e atividades

Os registros de PT descrevem processo, capacidade, esforço e pendências. Unidade dona do PE e unidade executora do PT permanecem em colunas distintas. Foram encontrados {pt_priority.get('crítica', 0)} registros críticos e {pt_priority.get('alta', 0)} altos. A distribuição de status abaixo deve ser interpretada como fotografia de processo, nunca como medida substituta do resultado pactuado no PE.

{status_table}

### PT e atividades que requerem atenção

{pt_attention}

## 5. Evidências textuais sanitizadas

{evidence_table}

O anexo CSV contém a evidência completa elegível. Nomes de servidores, CPF, e-mails, telefones e endereços são suprimidos localmente; UUIDs não são persistidos.

## 6. Riscos, potenciais problemas e mitigação

{_table(['Gatilho', 'Ocorrências', 'Medida proposta'], recommendations)}

## 7. Evolução temporal

{trends}

## 8. Apêndice reconciliável I01–I12

{appendix}

## 9. Limitações e governança

- A lente acumulada termina no último dia do mês anterior; a fotografia operacional pode conter fatos posteriores e é identificada separadamente.
- Textos são evidências de execução, não conclusões automáticas. Inferências devem manter vínculo com o registro e o gatilho exibido.
- O produto restrito remove dados pessoais, mas preserva unidades, entregas, planos e textos sanitizados. O compartilhável aplica k≥{K_MIN} às unidades envolvidas.
- Correções retroativas são aceitas como estado observado na data da extração.
"""


def run(argv: list[str] | None = None) -> list[Path]:
    args = build_parser().parse_args(argv)
    window = configure_execution_context(args.data_execucao)
    scope = scope_from_values(
        escopo=args.escopo, regional=args.regional, unidade=args.unidade,
        mesogrupo=args.mesogrupo, tipo_unidade=args.tipo_unidade,
        lista_unidades=args.lista_unidades,
    )
    month_dir = INPUT_BASE / window.mes_execucao
    output_dir = OUTPUT_BASE / window.mes_execucao
    loaded = load_all(month_dir, window)
    profiles = load_unit_profiles()
    data = scoped_data(loaded, scope, profiles)
    people_by_unit = people_counts_by_unit(data.get("05", []))
    evidence: list[dict[str, object]] = []
    evidence_origin = "indisponível"
    if args.consultar_denodo:
        connection = connect(get_config(require_credentials=True))
        try:
            _, name_rows = query_rows(connection, SQL_NAMES)
            sanitizer = TextSanitizer(row[0] for row in name_rows if row)
            lenses = ("acumulada", "operacional") if args.lente == "ambas" else (args.lente,)
            for lens in lenses:
                evidence.extend(extract_textual_evidence(
                    connection, window, scope, profiles, lens=lens, sanitizer=sanitizer
                ))
        finally:
            connection.close()
        evidence_origin = "Denodo somente leitura nesta execução"
    else:
        previous = output_dir / f"evidencias_execucao_v2_{scope.kind}_restrito_{window.mes_execucao}.csv"
        evidence = _load_evidence(previous)
        if evidence:
            evidence_origin = f"artefato sanitizado reutilizado: {previous.name}"
    products = ("restrito", "compartilhavel") if args.produto == "ambos" else (args.produto,)
    outputs: list[Path] = []
    if args.salvar or args.pdf:
        output_dir.mkdir(parents=True, exist_ok=True)
    for product in products:
        enforce_k = product == "compartilhavel"
        product_evidence = _eligible_shared(evidence, people_by_unit) if enforce_k else evidence
        cumulative = cumulative_summary(data, enforce_k=enforce_k)
        temporal = temporal_summary(data, enforce_k=enforce_k)
        report = render_report(
            window=window, scope_label=scope.label, product=product,
            cumulative=cumulative, temporal=temporal, evidence=product_evidence,
            denodo_used=args.consultar_denodo, evidence_origin=evidence_origin,
        )
        if not (args.salvar or args.pdf):
            print(report)
            continue
        slug = f"{scope.kind}_{product}_{window.mes_execucao}"
        md = output_dir / f"relatorio_gerencial_v2_{slug}.md"
        csv_path = output_dir / f"evidencias_execucao_v2_{slug}.csv"
        manifest_path = output_dir / f"manifesto_relatorio_v2_{slug}.json"
        md.write_text(report, encoding="utf-8")
        _write_csv(csv_path, product_evidence)
        manifest = {
            "versao_relatorio": "2.0",
            **window.as_dict(),
            "data_hora_geracao": datetime.now(ZoneInfo(ANALYSIS_TIMEZONE)).isoformat(timespec="seconds"),
            "escopo": scope.as_dict(),
            "produto": product,
            "lentes": args.lente,
            "consulta_denodo": args.consultar_denodo,
            "origem_evidencias": evidence_origin,
            "registros_textuais": len(product_evidence),
            "campos_pessoais_persistidos": False,
            "unidade_dona_separada_da_executora": True,
            "resultado_pe_inferido_por_atividade_pt": False,
            "fontes_ocde": sorted(f"I{code}" for code in loaded),
        }
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        current = [md, manifest_path]
        if csv_path.exists():
            current.append(csv_path)
        if args.pdf:
            pdf = output_dir / f"relatorio_gerencial_v2_{slug}.pdf"
            export_pdf(report, pdf, f"Relatório Gerencial V2 · {window.mes_execucao}")
            current.append(pdf)
        assert_safe_outputs(current)
        outputs.extend(current)
    return outputs


def main(argv: list[str] | None = None) -> int:
    outputs = run(argv)
    for path in outputs:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
