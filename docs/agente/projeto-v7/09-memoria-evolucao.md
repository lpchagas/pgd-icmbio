# 09 — Memória e evolução do projeto

## 1. Finalidade

Este capítulo preserva o raciocínio histórico sem depender dos arquivos de proposta v1–
v5. O histórico detalhado continua recuperável no Git. Esta memória não prevalece sobre a
proposta v6, os ADRs ou as normas.

## 2. Linha do tempo

| Versão/fase | Contribuição | Situação na v6 |
| --- | --- | --- |
| Ideia inicial/v1 | separação RAG e indicadores, ambiente Python e governança básica | absorvida; stack experimental superada |
| v2 | linguagem para analistas, RACI, riscos e Tutoriais T1–T6 | absorvida e atualizada no capítulo 07 |
| v3 | terceira capacidade, modelo comum, S01–S10, EAP e ciclo de vida | absorvida nos capítulos 01, 03 e 05 |
| v4 | MySQL, versionamento, imutabilidade e roadmap I0–I7 | absorvida no capítulo 02 e ADR-006 |
| v5 | S21–S24, execução/avaliação e migração `002` planejada | absorvida nos capítulos 03–05 e ADR-007 |
| v6 | catálogo S01–S24, local-first, desenvolvedor individual e 104 semanas | vigente |

## 3. Evolução do produto

### 3.1. De chatbot para três capacidades

O conceito inicial de consulta documental foi ampliado porque indicadores exigem fonte
de dados em tempo real e planejamento exige regras estruturadas. A arquitetura passou a
separar conhecimento, ferramentas de indicadores e skills.

### 3.2. De textos de prompt para regras executáveis

Quatro skills metodológicas originais demonstraram o fluxo estratégia→entregas→PE→PT.
A análise revelou lacunas em configuração, conformidade, capacidade, acompanhamento,
evidência e avaliação, originando o catálogo S01–S24.

### 3.3. De SQLite para MySQL

SQLite foi uma decisão inicial reversível. A necessidade de espelhar referências PETRVS,
preservar versões e preparar operação local levou ao MySQL 8, formalizado no ADR-006. O
banco atual tem 21 tabelas e 6 triggers.

### 3.4. Execução e avaliação

S21–S24 completaram o ciclo de PE/PT e introduziram o estado-alvo de 33 tabelas e 14
triggers. Esse alvo nunca deve ser confundido com o estado atual; a migração `002` ainda
não foi aplicada.

### 3.5. Realidade individual

A v6 remove a premissa implícita de equipe multidisciplinar disponível em tempo integral.
O desenvolvimento passa a usar 12 horas semanais, processamento local, custo incremental
zero e ondas de valor. A arquitetura institucional futura continua possível, mas separada.

## 4. Decisões preservadas

- Denodo somente leitura.
- Identidade persistente e códigos legíveis.
- Alteração por nova versão.
- Execução, regra, fonte e confiança rastreáveis.
- Decisões humanas separadas.
- Dado ausente como pergunta.
- Cálculos fora do LLM.
- MySQL local e serviço Windows.
- Piloto inicialmente restrito a CGOV/COCAGE.
- Conteúdo restrito fora de RAG/serviços externos.

## 5. Conteúdos superados

- SQLite como persistência vigente.
- dependência obrigatória de Langflow, Agno ou n8n;
- pressuposto de API paga incluída em assinatura de chat;
- Copilot Studio como canal imediato obrigatório;
- cronograma de equipe aplicado a uma pessoa;
- S11–S20 fora do horizonte;
- S21–S24 como bloco desconectado.

## 6. Tutoriais e capacitação

Os tutoriais originais foram revisados no [capítulo 07](07-operacao-capacitacao.md). O
glossário técnico permanece em [`docs/projeto/glossario-tecnico.md`](../../projeto/glossario-tecnico.md).

## 7. Recuperação histórica

Os arquivos de proposta anteriores foram removidos da árvore ativa após migração de
conteúdo. Para auditoria, podem ser consultados no histórico do Git. Recuperá-los não os
torna vigentes; qualquer regra atual deve apontar para v6, ADR ou fonte institucional.
