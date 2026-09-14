"""Adaptadores de apresentação dos A2 certificados da família de gestão."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from gestao.registry import enabled_extractions


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="|"))


def load_management(directory: Path, product: str) -> tuple[dict[str, list[dict[str, str]]], list[dict[str, Any]], dict]:
    manifest_path = directory / f"manifesto_gestao_{product}.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Manifesto de gestão ausente no escopo: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status_global") != "sucesso":
        raise ValueError("O manifesto de gestão não está íntegro.")
    results = {item.get("codigo"): item for item in manifest.get("resultados", [])}
    data: dict[str, list[dict[str, str]]] = {}
    auxiliary: dict[str, list[dict[str, str]]] = {"G02_HISTORY": [], "G02_NOMINAL": []}
    sources: list[dict[str, Any]] = []
    for extraction in enabled_extractions():
        result = results.get(extraction.code)
        if not result or result.get("status") != "sucesso":
            raise ValueError(f"Indicador ativo {extraction.code} ausente ou sem sucesso no manifesto de gestão.")
        if result.get("adaptador_relatorio") != extraction.report_adapter:
            raise ValueError(f"Indicador ativo {extraction.code} sem adaptador de apresentação coerente.")
        rows: list[dict[str, str]] = []
        artifacts = []
        for item in result.get("arquivos", []):
            path = directory / item["arquivo"]
            if not path.is_file() or sha256(path) != item.get("sha256"):
                raise ValueError(f"Artefato de gestão ausente ou com hash divergente: {path.name}")
            artifacts.append({"arquivo": path.name, "sha256": item["sha256"], "linhas": item.get("linhas", 0)})
            if (extraction.code == "G01" and ".2_painel_" in path.name) or (extraction.code == "G02" and ".2_entregas_" in path.name):
                rows.extend(read_csv(path))
            elif extraction.code == "G02" and ".2_historico_" in path.name:
                auxiliary["G02_HISTORY"].extend(read_csv(path))
            elif extraction.code == "G02" and ".2_nominal_" in path.name:
                auxiliary["G02_NOMINAL"].extend(read_csv(path))
        data[extraction.code] = rows
        sources.append({
            "codigo": extraction.code, "versao": extraction.formula_version,
            "adaptador": extraction.report_adapter, "artefatos": artifacts,
            "cobertura": len(rows),
        })
    data.update(auxiliary)
    return data, sources, manifest


def render_management_chapter(data: dict[str, list[dict[str, str]]], product: str) -> str:
    g01 = data.get("G01", [])
    g02 = data.get("G02", [])
    statuses = Counter(row.get("status_negocio") or "Não informado" for row in g01)
    reconciliation = Counter(row.get("situacao_reconciliacao") or "Não informado" for row in g02)
    owners = [row for row in g02 if row.get("visao") == "dona"]
    executors = [row for row in g02 if row.get("visao") == "executora"]
    cross = sum(row.get("unidade_dona_sigla") not in {"", "N.I.", row.get("unidade_executora_sigla")} for row in executors)
    history = data.get("G02_HISTORY", [])
    nominal = data.get("G02_NOMINAL", [])
    servers = (
        len({row.get("id_servidor") for row in nominal if row.get("id_servidor")})
        if nominal
        else max((int(float(row.get("total_servidores") or 0)) for row in g02), default=0)
    )
    plans = len({row.get("plano_trabalho_id") for row in nominal if row.get("plano_trabalho_id")})
    no_history = sum(name in {"TRABALHO_PT_SEM_HISTORICO_PE", "SEM_HISTORICO_PE_E_SEM_VINCULO_PT"} for name in (row.get("situacao_reconciliacao") for row in g02))
    no_link = sum(row.get("situacao_reconciliacao") == "HISTORICO_PE_SEM_VINCULO_PT" for row in g02)
    orphan = sum(row.get("situacao_reconciliacao") == "PT_OU_VINCULO_SEM_ENTREGA_IDENTIFICAVEL" for row in g02)
    status_lines = "\n".join(f"- {name}: {count} plano(s)." for name, count in statuses.most_common()) or "- Sem filas divulgáveis."
    reconciliation_lines = "\n".join(f"- {name}: {count} registro(s)." for name, count in reconciliation.most_common()) or "- Sem detalhe divulgável; aplicam-se as regras de k-anonimato."
    privacy = "O anexo nominal é restrito e não integra este produto compartilhável." if product == "compartilhavel" else "O anexo nominal restrito permite ação gerencial, sem CPF, e-mail, telefone ou endereço."
    return f"""## Indicadores de Gestão

### G01 — Situação dos Planos de Trabalho

As filas abaixo são uma fotografia operacional e indicam ações de regularização; não constituem avaliação de desempenho individual.

{status_lines}

### G02 — Execução das Entregas

Foram apresentadas {len(owners)} observações pela unidade dona e {len(executors)} pela unidade executora. Não se calcula score sintético: as contagens abaixo são descritivas e reconciliáveis.

#### Histórico da execução das entregas

O histórico contém {len(history)} registro(s) de progresso elegível(is) e termina no último ciclo fechado. Foram identificadas {no_history} observação(ões) sem histórico formal de progresso; a fotografia atual do PT não foi projetada para meses anteriores.

#### Fotografia dos PT e cobertura dos servidores

O produto autorizado cobre {servers} servidor(es){f' em {plans} Plano(s) de Trabalho' if plans else ''}. PT, vínculos e atividades pertencem exclusivamente à fotografia operacional. Há {no_link} observação(ões) com histórico de PE sem vínculo atual de PT e {orphan} observação(ões) de PT ou vínculo sem entrega identificável.

#### Execução entre unidades

Há {cross} observações em que a unidade dona e a unidade executora diferem. Essa separação é preservada no CSV e no relatório detalhado para permitir coordenação entre as unidades sem duplicar a visão da dona.

{reconciliation_lines}

#### Lacunas, riscos e recomendações

PT e atividade são evidências de processo e não substituem o resultado formal registrado no Plano de Entregas. Recomenda-se atualizar os registros de progresso ausentes, reconciliar entregas sem vínculo, corrigir vínculos órfãos e pactuar o acompanhamento das execuções interunidades. {privacy}

O Relatório de Execução de Entregas complementar contém todas as linhas elegíveis para o nível de acesso do produto, sua reconciliação e a trilha histórica autorizada.
"""


def render_delivery_report(data: dict[str, list[dict[str, str]]], scope: str, product: str, draft: bool) -> str:
    rows = data.get("G02", [])
    title = "# RASCUNHO NÃO HOMOLOGADO — Relatório de Execução de Entregas" if draft else "# Relatório de Execução de Entregas"
    lines = [title, "", f"- Escopo: {scope}", f"- Produto: {product}", f"- Registros elegíveis: {len(rows)}", "", "## Entregas e reconciliação", ""]
    if not rows:
        lines.append("Detalhamento integralmente suprimido porque o escopo não atingiu k≥5, ou não possui registros elegíveis.")
    else:
        lines.extend(["| Visão | Período | Dona | Executora | Entrega | Meta | Progresso | PT | Servidores | Reconciliação |", "| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |"])
        for row in rows:
            values = [row.get(key, "") for key in ("visao", "periodo", "unidade_dona_sigla", "unidade_executora_sigla", "nome_entrega", "meta_planejada", "progresso_historico", "total_planos_trabalho", "total_servidores", "situacao_reconciliacao")]
            lines.append("| " + " | ".join(str(value).replace("|", "\\|").replace("\n", " ") for value in values) + " |")
    lines.extend(["", "## Nota metodológica", "", "A lente PE usa somente eventos de progresso até o fim do último ciclo fechado. A lente PT é uma fotografia na data de execução e não é projetada retroativamente. Não há score sintético.", ""])
    history = data.get("G02_HISTORY", [])
    lines.extend(["## Trilha histórica de execução", "", f"Registros históricos elegíveis: {len(history)}.", ""])
    if history:
        lines.extend(["| Período | Unidade dona | Entrega | Data | Meta | Realizado | Registro sanitizado |", "| --- | --- | --- | --- | ---: | ---: | --- |"])
        for row in history:
            values = [row.get(key, "") for key in ("periodo", "unidade_dona_sigla", "nome_entrega", "data_progresso", "meta", "realizado", "registro_execucao")]
            lines.append("| " + " | ".join(str(value).replace("|", "\\|").replace("\n", " ") for value in values) + " |")
    nominal = data.get("G02_NOMINAL", [])
    lines.extend(["", "## Anexo nominal", "", f"O anexo nominal restrito contém {len(nominal)} linha(s) e permanece no artefato CSV próprio. Ele não contém CPF, e-mail, telefone ou endereço." if product == "restrito" else "O produto compartilhável não contém anexo nominal.", ""])
    return "\n".join(lines)
