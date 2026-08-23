# ADR-005 — RAG com LlamaIndex + ChromaDB; Langflow como prototipagem descartável

**Data:** registrada em v1/v2, mantida sem alteração em v3 | **Estado:** aprovada, vigente
**Decisor:** Coordenador do projeto (Leandro)
**Documentos:** `proposta-projeto-v1.md` §3 e "Fase 3"; `proposta-projeto-v2.md` §6;
`proposta-projeto-v3.md` §3 e §1.2‑c (RAG ampliado para o perfil institucional do S01)

> **Nota de reconstrução:** este ADR formaliza uma decisão já registrada em v1/v2 e
> reafirmada em v3, sem conteúdo novo.

## Contexto

Os quatro documentos de metodologia (skills B01–B04) e as fichas dos indicadores OCDE são
conhecimento textual estático, cujo caminho natural é RAG (Retrieval-Augmented Generation)
para reduzir alucinação e permitir citação de fonte nas respostas do agente.

## Decisão

- **Orquestração de RAG: LlamaIndex** — "abstração mais direta para 'indexar documentos →
  consultar'... com menos conceitos genéricos para aprender de início".
- **Banco vetorial: ChromaDB local** — "roda embutido, sem conta externa nem custo — ideal
  enquanto a base de documentos é pequena (4 skills + 12 fichas)".
- **Prototipagem visual: Langflow**, ferramenta didática e descartável após a Fase 2 (uso
  documentado em `prototipos/`, não em produção).
- **v3:** o escopo do RAG é ampliado para indexar também o perfil institucional carregado
  pelo S01 (documentos oficiais), sem trocar a stack.

## Alternativas descartadas

| Alternativa | Motivo do descarte |
| --- | --- |
| LangChain (no lugar de LlamaIndex) | Mais conceitos genéricos para aprender de início |
| Pinecone/Weaviate — nuvem (no lugar de ChromaDB) | Descartada nas fases de aprendizado; migração cogitada só diante de necessidade real de escala/hospedagem gerenciada, "provavelmente não antes da Fase 5" |
| Flowise (no lugar de Langflow) | Integração menos madura com LlamaIndex/Python; decisão classificada como não crítica |

## Consequências

- Todas classificadas como **Reversíveis** na tabela de stack.
- A v3 confirma que a stack "permanece válida" — apenas amplia o escopo do que é indexado
  (perfil institucional do S01), sem trocar a tecnologia.
- Implementação prevista em `src/rag/rag.py` (Incremento I2).

## Nota operacional — auditoria do acervo em 23.08.2026

A stack permanece vigente, mas “documentos oficiais” não significa indexar toda a pasta.
O acervo passou a ter 55 conteúdos únicos, incluindo duplicatas físicas, normas alteradas,
manuais dependentes de versão, transcrições com nomes e evidências individuais. A allowlist,
as camadas de autoridade, o saneamento e as exclusões obrigatórias estão definidos em
[`../fontes-institucionais.md`](../fontes-institucionais.md). I03 bruto, P01–P08,
R01–R09 e C02 ficam fora do RAG; normas em PDF de imagem exigem OCR revisado.
