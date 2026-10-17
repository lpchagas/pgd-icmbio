# ADR-014 — LLM em execução: servidor MCP local e arranjo híbrido

**Data:** 17.10.2026 | **Estado:** aprovada (DP-08) | **Revisa:**
[ADR-004](ADR-004-modelo-linguagem.md) e o item 7 da
[ADR-008](ADR-008-desenvolvimento-individual-local-first.md)

## Contexto

A [ADR-004](ADR-004-modelo-linguagem.md) previa API comercial direta (Anthropic ou
OpenAI) nas fases de aprendizado e migração para Azure OpenAI na fase institucional. A
[ADR-008](ADR-008-desenvolvimento-individual-local-first.md) já tinha afastado a API paga
(custo incremental zero) e adotado FastAPI `/docs` como interface-base, mas não disse
como um modelo de linguagem conversa com as ferramentas do agente.

Desde então:

- o desenvolvimento passou a usar o Claude Code (principal) e o Antigravity (secundário),
  pela [ADR-013](ADR-013-retirada-codex.md);
- esses clientes falam o protocolo MCP (Model Context Protocol) e podem chamar
  ferramentas locais sem chave de API;
- as regras do projeto continuam: Denodo somente leitura, cálculo determinístico em
  Python, `99_restrito` fora de Git, RAG e serviço externo, e serviço externo só com dado
  público ou sintético.

Falta uma interface única para as ferramentas, que sirva a mais de um cliente e aplique a
classificação dos dados num ponto só.

## Decisão

1. **Servidor MCP local como interface-base.** As ferramentas determinísticas do agente
   (indicador, RAG, skills) ficam expostas por um servidor MCP que roda no computador
   autorizado (`agente/mcp/`, ciclo C03). A lógica fica em Python; o servidor só a expõe.
2. **Gate de classe de dado no servidor.** Toda resposta de ferramenta leva a classe do
   conteúdo. Cliente externo (Claude Code, Claude Desktop ou outro serviço fora do
   computador) recebe só:
   - dado público;
   - dado sintético;
   - agregado do produto compartilhável, com k≥5 e supressão complementar.

   O que não se enquadra é recusado no servidor, com erro controlado e log sem conteúdo.
   Conteúdo `99_restrito` não é servido por nenhuma ferramenta MCP.
3. **Modelo local para o institucional comum.** Redação ou resumo por LLM sobre conteúdo
   institucional comum usa um modelo local (Ollama), como cliente do mesmo servidor.
   Fallback, se o hardware não comportar (spike no C04): o institucional fica só nas
   ferramentas determinísticas, sem redação por LLM.
4. **FastAPI vira adaptador opcional.** Pode ser criado sobre as mesmas funções, para
   integração ou demonstração, mas não é pré-requisito do G0. Isso revisa o item 7 da
   ADR-008; os demais itens continuam valendo.
5. **Sem API paga e sem Azure OpenAI como etapa planejada.** Os clientes usam os planos
   individuais do desenvolvedor dentro dos limites do plano, sem tratá-los como backend.
   Adoção institucional (Azure, Copilot Studio ou outro) continua exigindo nova decisão,
   licença e segurança, como na ADR-008.

O princípio da ADR-004 continua: o modelo de linguagem é substituível. Contratos e
ferramentas não dependem de fornecedor.

## Alternativas consideradas

| Alternativa | Motivo do descarte |
| --- | --- |
| API comercial direta (ADR-004, fases 1–3) | Viola o custo incremental zero da ADR-008 e manda conteúdo para fora sem gate próprio |
| Azure OpenAI como destino planejado (ADR-004, fases 4–5) | Depende de provisionamento institucional (Q2) sem previsão; fica como opção de adoção futura |
| FastAPI como interface-base e MCP como adaptador | Os clientes de LLM falam MCP; o FastAPI exigiria um orquestrador próprio para chegar ao mesmo resultado |
| MCP e FastAPI como duas interfaces-base | Duplica a superfície de teste no G0 sem ganho funcional |
| Só modelo local, sem cliente externo | Perde a capacidade dos clientes atuais para dado público e sintético, que é a maior parte do desenvolvimento |
| Gate de classe no cliente (instruções) | Instrução não é controle; o servidor é o único ponto que vê todas as respostas |

## Consequências

- O G0 (Marco M1) inclui um teste negativo: nenhum dado não público chega ao cliente
  externo. O mesmo teste SEC se repete em cada gate seguinte.
- Os contratos Pydantic (C02) incluem a classe do dado na resposta.
- A ADR-004 fica revisada no planejamento de fornecedores, e o item 7 da ADR-008 passa a
  ler "servidor MCP local é a interface-base; FastAPI é adaptador opcional".
- O risco de hardware insuficiente para o modelo local é tratado no spike do C04.
- Para pôr um serviço externo dentro do gate com conteúdo institucional é preciso uma
  nova ADR, com base institucional (licença e classificação).

## Referências

- [ADR-004 — Modelo de linguagem substituível](ADR-004-modelo-linguagem.md)
- [ADR-008 — Desenvolvimento individual e local-first](ADR-008-desenvolvimento-individual-local-first.md)
- [ADR-009 — Arquitetura integrada](ADR-009-arquitetura-integrada.md)
- [ADR-013 — Retirada do Codex](ADR-013-retirada-codex.md)
- [AT-02 — Recursos e arquitetura local-first](../agente/recursos-local-first.md)
- [Registro de decisões do projeto](registro-decisoes-projeto.md)
