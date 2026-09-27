# Cobertura dos requisitos dos documentos intermediários do agente

> **Para quem é:** quem precisa rastrear de onde vem uma regra de execução e avaliação do
> PGD (RN-01 a RN-36) ou recuperar conteúdo dos documentos de trabalho do agente que foram
> retirados da árvore na reorganização (L4f).

## 1. O que foi retirado e por quê

Nove documentos de trabalho, vindos do repositório do agente, ficaram numa pasta
intermediária (`agente/`) durante a reorganização. Seu conteúdo **vigente** foi consolidado
na [proposta v6](../agente/projeto-v6/00_proposta-projeto-v6.md), no
[catálogo S01–S24](../agente/projeto-v6/03-catalogo-skills-s01-s24.md) e nas
[fichas das capacidades](../../capacidades/especificacoes/README.md). Por isso, eles saíram
da árvore ativa.

**Nada se perdeu:** o histórico do agente foi preservado no repositório. Cada documento
continua recuperável, exatamente como estava, na versão `78e496b`:

```text
git show 78e496b:agente/skills/05_plano-skills-execucao-avaliacao_v1.md
```

Recuperar um documento não o torna vigente: em caso de divergência, prevalecem a proposta v6
e as fichas.

## 2. Regras RN-01 a RN-36 — destino

Todas as 36 regras de execução e avaliação estão na
[§11 do catálogo S01–S24](../agente/projeto-v6/03-catalogo-skills-s01-s24.md#11-regras-rn-01rn-36-de-execução-e-avaliação),
associadas à capacidade que as aplica. A coluna **Fonte** preserva a origem normativa
registrada no plano de execução e avaliação (siglas na §3).

| RN | Regra (texto vigente na v6) | Capacidade | Fonte | Bloco de origem |
| --- | --- | --- | --- | --- |
| RN-01 | A chefia da unidade registra a execução do PE | S21 | D1 §1.2 | Execução do Plano de Entregas (S21) |
| RN-02 | O registro descreve evolução das entregas e ocorrências de impacto | S21 | D1 §1.2 | Execução do Plano de Entregas (S21) |
| RN-03 | O registro ocorre durante a execução e se completa ao fim da vigência | S21 | D1 §1.2; D2 | Execução do Plano de Entregas (S21) |
| RN-04 | A conclusão do PE depende da verificação dos PTs do período | S21 | D2 | Execução do Plano de Entregas (S21) |
| RN-05 | Ajustes do PE são comunicados à chefia superior conforme regra aplicável | S21/S14 | D1 §1.2 | Execução do Plano de Entregas (S21) |
| RN-06 | Ajuste do PE pode exigir repactuação dos PTs vinculados | S21/S14 | D1 §1.2 | Execução do Plano de Entregas (S21) |
| RN-07 | Calendário do PE é configuração institucional validada | S21 | D2; D3 §9 | Execução do Plano de Entregas (S21) |
| RN-08 | Progresso esperado é planejamento; progresso realizado é execução | S21 | D4 §glossário; D5 | Execução do Plano de Entregas (S21) |
| RN-09 | Unidade hierarquicamente superior avalia o PE em cascata | S22 | D1 §2.2; D5 | Avaliação do Plano de Entregas (S22) |
| RN-10 | Unidade instituidora também executora pode ter dispensa normativa | S22 | D1 §2.2 | Avaliação do Plano de Entregas (S22) |
| RN-11 | Ato autorizativo pode prever outras dispensas previstas em norma | S22 | D1 §2.2 | Avaliação do Plano de Entregas (S22) |
| RN-12 | Avaliação do PE observa até 30 dias após o encerramento | S22 | D1 §2.2 | Avaliação do Plano de Entregas (S22) |
| RN-13 | Avaliar metas, prazos, justificativas e qualidade esperada | S22 | D1 §2.2 | Avaliação do Plano de Entregas (S22) |
| RN-14 | Escala 1 excepcional, 2 alto desempenho, 3 adequado, 4 inadequado, 5 não executado | S22/S24 | D1 §2.2 | Avaliação do Plano de Entregas (S22) |
| RN-15 | Norma geral não define automaticamente consequências 4/5 para PE | S22 | D1 §2.2 | Avaliação do Plano de Entregas (S22) |
| RN-16 | Resultado insatisfatório do PE analisa plano/gestão, não falha individual automática | S22 | D1 §2.2 | Avaliação do Plano de Entregas (S22) |
| RN-17 | Participante registra a execução do próprio PT | S23 | D1 §1.3 | Execução do Plano de Trabalho (S23) |
| RN-18 | Registro contém trabalhos realizados e intercorrências justificadas | S23 | D1 §1.3 | Execução do Plano de Trabalho (S23) |
| RN-19 | PT até 30 dias: registro em até 10 dias; maior: mensal até o décimo dia subsequente | S23 | D1 §1.3 | Execução do Plano de Trabalho (S23) |
| RN-20 | Periodicidade mensal do PT no ICMBio depende da fonte vigente | S23 | D2; D3 §10 | Execução do Plano de Trabalho (S23) |
| RN-21 | Férias, licenças e afastamentos planejados não são intercorrências | S07/S23 | D1 §1.3 | Execução do Plano de Trabalho (S23) |
| RN-22 | Intercorrências são fatos supervenientes com impacto, sem detalhe sensível | S23 | D1 §1.3, §2.3 | Execução do Plano de Trabalho (S23) |
| RN-23 | PT pode ser ajustado ou repactuado conforme competência e regra | S14/S23 | D1 §1.3 | Execução do Plano de Trabalho (S23) |
| RN-24 | CHD = jornada × dias trabalháveis, ajustada por ocorrências programadas | S07/S23 | D3 §8 | Execução do Plano de Trabalho (S23) |
| RN-25 | Usufruto/compensação registra categoria, horas e período de origem | S23 | D3 §18, §23 | Execução do Plano de Trabalho (S23) |
| RN-26 | PT corresponde à CHD; execução inferior não gera folga automática | S12/S23 | D3 §21 | Execução do Plano de Trabalho (S23) |
| RN-27 | Chefia avalia o PT como um todo, não cada atividade | S24 | D1 §2.3 | Avaliação do Plano de Trabalho (S24) |
| RN-28 | Avaliação do PT observa até 20 dias após o limite de registro | S24 | D1 §2.3; D2 | Avaliação do Plano de Trabalho (S24) |
| RN-29 | Considerar pactuação, critérios, fatores externos, TCR e ocorrências | S24 | D1 §2.3 | Avaliação do Plano de Trabalho (S24) |
| RN-30 | Participante é notificado do resultado | S24 | D1 §2.3 | Avaliação do Plano de Trabalho (S24) |
| RN-31 | Conceitos 1 e 5 exigem justificativa da chefia | S24 | D1 §2.3 | Avaliação do Plano de Trabalho (S24) |
| RN-32 | Conceitos 4/5 admitem recurso e manifestação em prazos de 10 dias | S24 | D1 §2.3 | Avaliação do Plano de Trabalho (S24) |
| RN-33 | Foco é contribuição às entregas, não comportamento | S24 | D1 §2.3 | Avaliação do Plano de Trabalho (S24) |
| RN-34 | Chefia promove acompanhamento e ações de desenvolvimento | S24 | D1 §2.3 | Avaliação do Plano de Trabalho (S24) |
| RN-35 | PGD não tem caráter punitivo automático | S24 | D3 §12 | Avaliação do Plano de Trabalho (S24) |
| RN-36 | Avaliação do PGD não substitui avaliação anual de desempenho | S24 | D3 §25 | Avaliação do Plano de Trabalho (S24) |

## 3. Fontes normativas citadas (D1–D9)

| Sigla | Documento | Natureza |
| --- | --- | --- |
| D1 | Caderno do curso "Execução e Avaliação dos Planos" (Enap, 2026) | Norma interpretada (reflete as IN 24/2023 e 52/2023) — fonte primária das regras |
| D2 | "Entendendo o Ciclo do PGD no ICMBio" (CGGE) | Regra institucional: periodicidade, quem registra o quê, conclusão do PE |
| D3 | "Perguntas e respostas PGD ICMBio" (CGGE) | Regra institucional e recomendação: CHD, usufruto e compensação de horas |
| D4 | Caderno do curso "Elaboração de Planos de Entrega e de Trabalho" (Enap) | Norma interpretada: meta, prazo, progresso esperado |
| D5 | Guia Prático PGD — Módulo 3: Plano de Entregas (SEGES/MGI) | Norma interpretada: estrutura do PE e cascata de avaliação |
| D6 | Caderno "Fundamentos do PGD" e instrumentos de controle (Enap) | Recomendação e exemplos |
| D7 | "Entenda como criar um Plano de Entregas" e "Guia para site de transparência do PGD" (ICMBio/MGI) | Recomendação: publicidade e transparência dos registros |
| D8 | Portaria ICMBio nº 5.592/2025 — Regimento Interno | Norma: competências e chefia hierarquicamente superior |
| D9 | Acórdão TCU 2082/2022 | Controle externo: rastreabilidade e evidência dos registros |

As referências oficiais do projeto estão no [catálogo de referências](../referencias-pgd/README.md)
e nas [fontes institucionais](fontes-institucionais.md). Uma regra que dependa de fonte ainda não
validada continua como questão aberta, nunca como fato.

## 4. Conteúdo sem destino na v6 (recuperável no histórico)

Estes trechos não foram reescritos na v6 e ficam como **histórico classificado**:
consultáveis na versão `78e496b`, sem valor normativo. Se uma capacidade for implementada,
o conteúdo deve ser revisto e levado à ficha correspondente.

| Documento (revisão no Git) | Trecho sem destino | Situação |
| --- | --- | --- |
| `78e496b:agente/skills/05_plano-skills-execucao-avaliacao_v1.md` | §2 base documental detalhada; §3.5 conflitos e lacunas normativas | Insumo para S02 e para as questões abertas da v6 |
| idem | §5 arquitetura do bloco S21–S24 e contrato de saída; §6 especificação funcional | Síntese vigente nas fichas S21–S24 e na [ADR-007](../decisoes/ADR-007-execucao-avaliacao-s21-s24.md) |
| idem | §7 modelo de dados da migração 002 (grupos 8 a 10, triggers) | Proposta não aplicada (a ADR-007 não aplica migração) |
| idem | §8 mapeamento com o PETRVS | Insumo para a implementação de S21–S24 |
| idem | §9 plano em etapas, §10 riscos, §11 critérios de aceite, §12 questões em aberto | Riscos vigentes em [riscos.md](riscos.md); cronograma vigente na v6 |
| idem | Anexo A (regra → skill → teste) e Anexo B (fluxo temporal de um ciclo) | Insumo para os testes de S21–S24 |
| `78e496b:agente/skills/01_analise-skills_v1.md` | Análise exploratória das quatro skills originais | Superado pela v6 |
| `78e496b:agente/skills/02_matriz-desenvolvimento-skills_v2.md` | Matriz de prioridades P0–P3 que originou S01–S20 | Divergências resolvidas pela v6 |
| `78e496b:agente/skills/03_especificacao-funcional-skills_v2.md` | Histórias de usuário e fluxos do MVP S01–S10; modelo mínimo de dados | Síntese do modelo em [esquema do banco do agente](../dados-petrvs/esquema-mysql-agente.md); fichas S01–S10 |
| `78e496b:agente/skills/04_backlog-mvp-skills_v2.md` | Backlog e sprints dimensionados para equipe | Não usar como cronograma: a v6 é de desenvolvimento individual ([ADR-008](../decisoes/ADR-008-desenvolvimento-individual-local-first.md)) |

## 5. Documentos de apoio retirados

| Documento | Destino do conteúdo |
| --- | --- |
| `78e496b:agente/docs/README.md` (portal do repositório do agente) | [Portal do agente](../agente/README.md) e [README do projeto](../../README.md) |
| `78e496b:agente/docs/tecnologia/referencia-pgd-ocde-icmbio.md` (resumo do projeto analítico para o agente) | Desnecessário no monorepo: fichas em [docs/ocde](../ocde/06-indicadores-ocde-denodo.md), regras de VQL nas instruções comuns (`CLAUDE.md`) e na [estrutura do banco](../dados-petrvs/estrutura-banco-dados.md) |
| `78e496b:agente/docs/gestao/historico-evolucao-projeto.md` (página de compatibilidade) | [Memória e evolução v1→v6](../agente/projeto-v6/09-memoria-evolucao.md) e [marcos do projeto](../projeto/visao-geral.md#8-marcos) |
| `78e496b:agente/docs/gestao/historico/prompt-planejamento-inicial-v1.md` (prompt que originou o projeto do agente) | Histórico; superado pela v6 |
