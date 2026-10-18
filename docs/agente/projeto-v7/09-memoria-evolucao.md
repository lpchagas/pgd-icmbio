# 09 — Memória e evolução do projeto

## 1. Finalidade

Este capítulo preserva o raciocínio histórico sem depender dos arquivos das propostas
v1–v6. O histórico detalhado continua recuperável no Git. Esta memória não prevalece sobre
a proposta v7, as ADRs ou as normas.

## 2. Linha do tempo

| Versão/fase | Data-base | Contribuição | Situação na v7 |
| --- | --- | --- | --- |
| Ideia inicial/v1 | — | separação RAG e indicadores, ambiente Python e governança básica | absorvida; stack experimental superada |
| v2 | — | linguagem para analistas, RACI, riscos e tutoriais T1–T6 | absorvida e atualizada no capítulo 07 |
| v3 | — | terceira capacidade, modelo comum, S01–S10, EAP e ciclo de vida | absorvida nos capítulos 01, 03 e 05 |
| v4 | — | MySQL, versionamento, imutabilidade e roadmap I0–I7 | absorvida no capítulo 02 e na ADR-006 |
| v5 | 18/08/2026 | S21–S24, execução/avaliação e migração `002` planejada | absorvida nos capítulos 03–05 e na ADR-007 |
| v6 | 23/08/2026 | catálogo S01–S24, local-first, desenvolvedor individual e 104 semanas | absorvida; mudanças na seção 8 |
| v7 | 17/10/2026 | monorepo, duas ferramentas de desenvolvimento, MCP híbrido, catálogo único e grade deslocada | vigente |

## 3. Evolução do produto

### 3.1. De chatbot para três capacidades

O conceito inicial de consulta documental foi ampliado porque indicadores exigem fonte
de dados real e planejamento exige regras estruturadas. A arquitetura passou a separar
conhecimento, ferramentas de indicadores e skills.

### 3.2. De textos de prompt para regras executáveis

Quatro skills metodológicas originais demonstraram o fluxo estratégia→entregas→PE→PT.
A análise revelou lacunas em configuração, conformidade, capacidade, acompanhamento,
evidência e avaliação, originando o catálogo S01–S24.

### 3.3. De SQLite para MySQL

SQLite foi uma decisão inicial reversível. A necessidade de espelhar referências PETRVS,
preservar versões e preparar operação local levou ao MySQL 8, formalizado na ADR-006. O
banco atual tem 21 tabelas e 6 triggers.

### 3.4. Execução e avaliação

S21–S24 completaram o ciclo de PE/PT e introduziram o estado-alvo de 33 tabelas e 14
triggers. Esse alvo nunca deve ser confundido com o estado atual; a migração `002` ainda
não foi aplicada.

### 3.5. Realidade individual

A v6 removeu a premissa implícita de equipe multidisciplinar disponível em tempo integral.
O desenvolvimento passou a usar 12 horas semanais, processamento local, custo incremental
zero e ondas de valor. A arquitetura institucional futura continua possível, mas separada.

### 3.6. Um repositório, dois projetos irmãos

Em setembro de 2026, o agente e o projeto analítico dos indicadores foram unidos no
monorepo `pgd-icmbio` (DP-01, ADR-009). O agente passou a contar com indicadores
homologados como insumo, e a fronteira ficou explícita: o núcleo analítico não importa o
agente.

### 3.7. Do FastAPI ao servidor MCP

A v6 previa uma API FastAPI como interface-base. Com clientes de LLM que falam MCP e o
custo zero mantido, a ADR-014 fez do servidor MCP local a interface-base, com o gate de
classe no servidor e um modelo local para o institucional comum. O FastAPI virou
adaptador opcional.

## 4. Decisões preservadas

- Denodo somente leitura.
- Identidade persistente e códigos legíveis.
- Alteração por nova versão.
- Execução, regra, fonte e confiança rastreáveis.
- Decisões humanas separadas.
- Dado ausente como pergunta.
- Cálculos fora do LLM.
- MySQL local, com backup diário.
- Piloto inicialmente restrito a CGOV/COCAGE.
- Conteúdo restrito fora de RAG e de serviços externos.
- Modelo de linguagem substituível.
- 104 semanas, cinco ondas e estabilização, com no máximo duas skills em andamento.

## 5. Conteúdos superados

- SQLite como persistência vigente;
- dependência obrigatória de Langflow, Agno ou n8n;
- pressuposto de API paga incluída em assinatura de chat;
- API comercial direta e Azure OpenAI como etapas planejadas (ADR-004, revisada);
- FastAPI como interface-base (item 7 da ADR-008, revisado);
- Copilot Studio como canal imediato obrigatório;
- cronograma de equipe aplicado a uma pessoa;
- S11–S20 fora do horizonte;
- S21–S24 como bloco desconectado;
- Windows como ambiente principal e serviço `MySQL84` como referência operacional;
- três ferramentas de desenvolvimento com três arquivos de instruções;
- fichas mantidas uma a uma, sem fonte única.

## 6. Tutoriais e capacitação

Os tutoriais originais foram revisados no [capítulo 07](07-operacao-capacitacao.md). O
glossário técnico permanece em [`docs/projeto/glossario-tecnico.md`](../../projeto/glossario-tecnico.md).

## 7. Recuperação histórica

Os arquivos das propostas anteriores foram removidos da árvore ativa após migração de
conteúdo. A v6 foi renomeada para a v7 por `git mv` (pasta `projeto-v6/` → `projeto-v7/`),
o que preserva o histórico de cada capítulo: `git log --follow` mostra a v6 e as versões
anteriores. Recuperá-las não as torna vigentes; qualquer regra atual deve apontar para a
v7, uma ADR ou uma fonte institucional.

## 8. Da v6 para a v7

A v7 não muda o produto, o catálogo S01–S24, as regras de ouro nem o horizonte de 104
semanas. Ela atualiza o plano ao que aconteceu entre 23/08 e 17/10/2026.

### 8.1. Ferramentas de desenvolvimento

| v6 | v7 | Base |
| --- | --- | --- |
| Codex, Claude Code e Antigravity, com três arquivos de instruções (`AGENTS.md`, `CLAUDE.md`, `PROJECT.md`) | Claude Code (principal) e Antigravity (secundário), com dois pares sem hierarquia (`CLAUDE.md`, `PROJECT.md`); `AGENTS.md` recusado na raiz | ADR-013, DP-07 |
| Ferramentas citadas só como apoio ao desenvolvimento | As mesmas ferramentas são também clientes externos do servidor MCP, limitados por classe de dado | ADR-014 |

### 8.2. Arquitetura: arranjo híbrido com MCP local

| v6 | v7 | Base |
| --- | --- | --- |
| FastAPI `/docs` como interface-base; `POST /skill` e `GET /indicador/{id}` | Servidor MCP local como interface-base, com ferramentas `indicador`, `rag` e `skill`; FastAPI como adaptador opcional | ADR-014, que revisa o item 7 da ADR-008 |
| Classificação de dados aplicada por fluxo | Gate de classe no servidor: cliente externo só com público, sintético ou agregado compartilhável (k≥5); `classe_dado` em toda resposta | ADR-014 |
| Modelo local citado como base para o institucional, sem papel definido | Ollama como cliente local do mesmo servidor, com spike no C04 e fallback só determinístico | ADR-014 |
| Indicador por consulta VQL e cálculo Python no agente | Indicador lido do A2 certificado, com liberação por piloto e sem somar pilotos | protocolo A1–A5; `lib/liberacao.py` |
| Riscos RP01–RP33 | Acréscimo de RP34–RP36 (fornecedor no desenvolvimento, vazamento pelo cliente externo, hardware do modelo local) | registro de riscos |

### 8.3. Cronograma

| v6 | v7 |
| --- | --- |
| C01–C52 de 31/08/2026 a 27/08/2028 | C01–C52 de 02/11/2026 a 29/10/2028 (deslocamento de nove semanas) |
| Fundação: contratos, API, RAG e indicador de prova | Fundação: contratos e motor (B2), servidor MCP e indicador (B3), RAG mínimo, spike do Ollama e M1 (B4) |
| Reservas de fim de ano em C09 e C35 | Reservas de fim de ano em C05 e C31, dentro das mesmas ondas |
| Migração `002` no C39, sem data de aplicação | Revisão e aplicação no C39, início da Onda 5, sob o gate da migração |
| Revisão de capacidade bimestral | Revisão a cada quatro ciclos, com 1–2 h/mês reservadas ao ciclo dos indicadores |

O deslocamento vem da Fase A (outubro de 2026), que fechou a validação dos indicadores
nos pilotos e tomou as decisões das ADR-013 e ADR-014. A B1, prevista para o C01,
terminou antes dele; a grade não foi antecipada e o C01 começa a B2.

### 8.4. Estado atual

| Tema | v6 (23/08/2026) | v7 (17/10/2026) |
| --- | --- | --- |
| Repositório | `pgd-agente-icmbio`, separado | monorepo `pgd-icmbio`, agente em `agente/` (ADR-009) |
| Ambiente | Windows, serviço `MySQL84`, tarefa agendada | WSL principal, MySQL 8.4 da distribuição, timer do systemd; Windows suportado |
| Restauração | manual documentada | instância isolada e `banco_teste.py` |
| Indicadores | rota Denodo validada | 12 OCDE, G01 e G02 homologados nos três pilotos; expansão nacional deliberada |
| Catálogo | 24 fichas separadas, com tabelas repetidas | `capacidades/catalogo.yaml` gera fichas 0.2 e tabelas (DP-09) |
| Fonte metodológica | documentos `skills/01–05` como insumo | `docs/agente/metodologia/` canônica; protótipos Cowork como referência |
| Decisões | ADR-001–008 | ADR-001–014; DP-01–DP-09 |
| Testes | suíte a criar | suíte offline no CI; testes MySQL opt-in na instância isolada |
| Motor, MCP, RAG, S01–S24 | não implementados | não implementados (Fundação a partir de 02/11/2026) |
