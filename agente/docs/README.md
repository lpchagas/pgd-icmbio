# Documentação do projeto

**Última revisão:** 23.08.2026

O documento vigente é a [proposta v6](../../docs/agente/projeto-v6/00_proposta-projeto-v6.md). O
[portal v6](../../docs/agente/projeto-v6/README.md) organiza os capítulos vinculantes. Propostas anteriores
foram consolidadas e não são necessárias.

## Trilha para analistas de negócio

1. [Glossário institucional](../../docs/projeto/glossario-institucional.md).
2. [Proposta v6](../../docs/agente/projeto-v6/00_proposta-projeto-v6.md), seções 2–6.
3. [Catálogo S01–S24](../../docs/agente/projeto-v6/03-catalogo-skills-s01-s24.md).
4. [Índice das fontes PGD](../../docs/referencias-pgd/README.md).
5. [Fontes institucionais e Q5](../../docs/governanca-projeto/fontes-institucionais.md).
6. [Validação do modelo comum](../../docs/governanca-projeto/validacao-modelo-comum.md).
7. [Riscos](../../docs/governanca-projeto/riscos.md).

## Trilha técnica

1. [Arquitetura, tecnologia e dados](../../docs/agente/projeto-v6/02-arquitetura-tecnologia-dados.md).
2. [AT-01 — PETRVS/MySQL](../../docs/dados-petrvs/esquema-mysql-agente.md).
3. [AT-02 — recursos/local-first](../../docs/agente/recursos-local-first.md).
4. [Qualidade e testes](../../docs/agente/projeto-v6/05-qualidade-testes-aceite.md).
5. [Operação e capacitação](../../docs/agente/projeto-v6/07-operacao-capacitacao.md).

## Por necessidade

| Necessidade | Documento |
| --- | --- |
| Entender o produto | [Proposta v6](../../docs/agente/projeto-v6/00_proposta-projeto-v6.md) |
| Ver cronograma de 104 semanas | [Cronograma](../../docs/agente/projeto-v6/04-cronograma-capacidade-marcos.md) |
| Implementar uma skill | [Fichas S01–S24](../../capacidades/especificacoes/README.md) |
| Aprovar fontes/Q5 | [Fontes institucionais](../../docs/governanca-projeto/fontes-institucionais.md) |
| Consultar decisão | [ADRs](../../docs/decisoes/) |
| Acompanhar risco | [Matriz ativa](../../docs/governanca-projeto/riscos.md) |
| Entender a evolução | [Memória v1→v6](../../docs/agente/projeto-v6/09-memoria-evolucao.md) |
| Preparar ambiente | [Operação/capacitação](../../docs/agente/projeto-v6/07-operacao-capacitacao.md) |

## Decisões

- ADR-001 — SQLite histórico, substituído.
- ADR-002 — Denodo somente leitura.
- ADR-003 — arquitetura em capacidades.
- ADR-004 — modelo de linguagem substituível.
- ADR-005 — stack RAG.
- ADR-006 — MySQL 8 local.
- ADR-007 — execução e avaliação S21–S24.
- ADR-008 — desenvolvimento individual local-first e ondas S01–S24.

## Pendências humanas

Q5, validação do glossário/modelo comum e atas reais continuam pendentes. Documento
gerado não constitui aprovação.

## Regras de manutenção

- Atualize a fonte principal e crie links em vez de duplicar.
- Diferencie atual, alvo e pendente.
- Preserve IDs estáveis.
- Não publique credenciais, dados pessoais, transcrições ou evidências individuais.
- Revise links, números, datas, identificadores, riscos e `AGENTS.md` após mudança.
