# ADR-003 — Arquitetura do agente em capacidades A/B/C

**Data:** registrada nas revisões iniciais | **Estado:** aprovada; escolhas de orquestrador/interface revisadas pelo ADR-008
**Decisor:** Coordenador do projeto (Leandro)
**Documentos vigentes:** [Proposta v6](../agente/projeto-v6/00_proposta-projeto-v6.md) e
[arquitetura](../agente/projeto-v6/02-arquitetura-tecnologia-dados.md)

> **Nota de reconstrução:** este ADR formaliza decisões já tomadas e documentadas em v1–v3,
> sem conteúdo novo.

> [!NOTE]
> A separação A/B/C permanece vigente. Agno, Copilot Studio e Streamlit não são
> dependências do protótipo v6; FastAPI local é a base e a interface institucional será
> decidida futuramente, conforme ADR-008.

## Contexto

v1/v2 definiam duas capacidades do agente — conhecimento (RAG) e ação sobre dados (tool
calling → Denodo) — convergindo num agente único a construir na "Fase 4". A v3 identificou
que isso era insuficiente diante dos artefatos de skills (S01–S10), que exigem execução
estruturada com validadores compartilhados, e não apenas consulta.

## Decisão

1. **Framework de orquestração: Agno** (Python), adotado só depois que os conceitos de
   agente (memória + ferramentas + RAG) já tivessem sido aprendidos "na mão" nas fases
   iniciais — "entrega pronto o padrão... reduzindo código a manter" (v2 §6).
2. **Interface institucional: Copilot Studio + Power Platform Custom Connector** — "porque
   aproveita o M365 que os gestores já usam (sem novo login/URL)" —, com **Streamlit como
   plano B de demonstração** caso a homologação do Custom Connector atrase.
3. **Terceira capacidade (v3): arquitetura em três blocos** que convergem no agente
   unificado (Incremento I6):
   - **(A) RAG** — "o bibliotecário" (conhecimento institucional estático);
   - **(B) Tool calling/Denodo** — "o consultor de plantão" (indicadores e dados reais);
   - **(C) Skills executáveis S01–S10** — "o analista metodológico" (validadores +
     contratos estruturados), decidindo qual capacidade acionar ou combinando-as.

## Alternativas descartadas

| Alternativa | Motivo do descarte |
| --- | --- |
| Montar tudo à mão com LlamaIndex puro (sem framework de agente) | Exige mais código de manutenção; mantida apenas como caminho de aprendizado nas fases iniciais |
| Interface web própria (Streamlit/Gradio) como solução definitiva | Não aproveita o M365 já usado pelos gestores; rebaixada a plano B/fallback, não eliminada |
| Continuar apenas com RAG puro (sem terceira capacidade) | Insuficiente para as skills S01–S10, que exigem validadores compartilhados e continuidade de objetos, não apenas recuperação de texto |

## Consequências

- Classificada como decisão **Estruturante** (v2 §6) — não reversível sem retrabalho
  relevante.
- Risco associado **RP01** (matriz de riscos): "Provisionamento Azure/Custom Connector
  atrasar e travar o Incremento I7", mitigado por iniciar o processo com o TI
  antecipadamente (a partir do I6) e manter Streamlit como plano B.
- Reordena o roadmap técnico: a fusão das trilhas T (tecnologia) e N (negócio) num roadmap
  único de incrementos (I0–I7) é consequência direta de tratar as skills como terceira
  capacidade, não como conteúdo estático de RAG.
