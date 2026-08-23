# Proposta de Projeto — `pgd-agente-icmbio`

**Versão:** 3.0 (revista e ampliada) | **Data:** 26.07.2026
**Substitui:** `proposta-projeto-v2.md` como documento de planejamento e gestão.
A v2 **permanece válida como Anexo de Capacitação** — seu Glossário (Seção 4) e seus
Tutoriais T1–T6 (Seção 9) continuam sendo o material de referência da equipe e não são
repetidos aqui.
**Papel assumido nesta proposta:** consultor independente sênior em engenharia de software e
gestão de projetos.
**Público-alvo:** equipe de projeto formada por analistas de negócio da CGOV/ICMBio.

---

## Sumário executivo

Entre a v2 (26.07.2026) e esta v3, a CGOV produziu na pasta `skills/` cinco artefatos que
mudam a natureza do projeto: a análise crítica das quatro skills originais
(`01_analise-skills_v1`), a matriz de 20 skills com prioridades e testes de aceitação
(`02_matriz-desenvolvimento-skills_v2`), a especificação funcional do MVP de 10 skills
(`03_especificacao-funcional-skills_v2`) e o backlog executável em 7 sprints
(`04_backlog-mvp-skills_v2`).

A v2 tratava as skills como **quatro documentos estáticos** a serem indexados via RAG. Os
novos artefatos redefinem as skills como um **ecossistema modular de regras negociais**:
validadores compartilhados, modelo de dados comum, contratos de entrada e saída,
rastreabilidade e testes de aceitação. Isso exige uma proposta que integre duas frentes que
até aqui evoluíam em documentos separados:

- **Trilha T (Tecnologia):** infraestrutura, RAG, tool calling, agente, API, Copilot Studio
  — o roadmap técnico da v2, preservado e reposicionado.
- **Trilha N (Negócio):** especificação, regras, casos de teste e validação das skills
  S01–S10 — o conteúdo dos artefatos 01–04, transformado em plano executável pela equipe real.

**As quatro decisões estruturantes desta versão:**

1. **Roadmap único de 8 incrementos (I0–I7)**, fundindo as fases tecnológicas da v2 com os
   7 sprints do backlog de skills. Cada incremento entrega capacidade técnica **e** conteúdo
   negocial que se validam mutuamente — nunca tecnologia sem conteúdo, nunca especificação
   sem meio de testá-la.
2. **Terceira capacidade do agente.** A v2 previa duas capacidades: conhecimento (RAG) e
   ação sobre dados (indicadores via Denodo). A v3 adiciona a capacidade central do produto:
   **skills executáveis** — regras negociais estruturadas com validadores, contratos e saídas
   padronizadas (Seção 3).
3. **Papéis do backlog adaptados à equipe real.** O backlog `04` pressupõe dez papéis
   profissionais (ARQ, IA, BE, FE, QA...). A Seção 5.2 mapeia esses papéis para a equipe
   efetivamente disponível e recalibra prazos: incrementos de 3–6 semanas com dedicação
   parcial, não sprints de 2 semanas com equipe dedicada.
4. **Ciclo de vida padronizado de skill (Seção 8).** Sete passos que separam claramente o
   trabalho do analista de negócio (especificar, anotar exemplos, validar) do trabalho
   técnico (implementar, integrar, medir) — é o mecanismo que permite desenvolver as duas
   frentes "de maneira sequencial e integrada".

---

## 1. Análise da pasta `skills/` — o que existe e o que muda

### 1.1. Inventário e papel de cada arquivo

| Arquivo | Natureza | Papel no projeto a partir da v3 |
| --- | --- | --- |
| `00_skill-analise-entrega-v1.md` | Metodologia (B01) | Fonte de regras do classificador/validador de entregas; base de conhecimento RAG |
| `00_skill-okrd-v1.md` | Metodologia (B02) | Fonte conceitual da cadeia OKR-D; base do S09 |
| `00_skill-plano-entregas-v1.md` | Metodologia (B03) | Orquestrador conceitual do plano de entregas; base de S03–S06 |
| `00_skill-plano-trabalho-v1.md` | Metodologia (B04) | Regras de alocação de esforço; base de S07–S08 |
| `01_analise-skills_v1.md` | Análise crítica | Diagnóstico de fragilidades; origem da arquitetura em 4 camadas e das 20 skills |
| `02_matriz-desenvolvimento-skills_v2.md` | Matriz de desenvolvimento | **Especificação mestra**: 20 skills (S01–S20), prioridades P0–P3, dependências, testes de aceitação, critérios globais de pronto |
| `03_especificacao-funcional-skills_v2.md` | Especificação funcional | **Detalhamento do MVP (S01–S10)**: perfis, histórias de usuário, modelo de dados, casos de teste, requisitos não funcionais, plano de avaliação |
| `04_backlog-mvp-skills_v2.md` | Backlog executável | **Plano de execução**: 7 sprints, épicos, estimativas, riscos, definição de pronto |

### 1.2. Conclusões da análise que esta v3 incorpora

**(a) As skills deixaram de ser documentos e viraram software com regras de negócio.** A
análise `01` demonstra que os quatro textos originais repetem regras entre si, não têm
modelo de dados comum, não distinguem norma de recomendação e não têm continuidade (a
entrega analisada numa skill não "viaja" para a seguinte). A solução — validadores
compartilhados, esquema canônico, objetos com ID persistente — é incompatível com a
abordagem "RAG puro" da v2. O RAG continua necessário (capacidade de conhecimento), mas
passa a ser **uma** das camadas, não a estratégia inteira.

**(b) O MVP tem escopo definido e fechado: 10 skills.** S01–S10 cobrem o fluxo
`fontes institucionais → regras → competências → entregas candidatas → catálogo → metas →
auditoria do portfólio → capacidade → cobertura da equipe → OKR-D → riscos`. Pactuação,
monitoramento, replanejamento, avaliação e inteligência gerencial (S11–S20) ficam fora do
MVP por decisão registrada no `04`, Seção 20.

**(c) O caminho crítico das skills é sequencial e começa pelo S01.** Nenhuma skill funciona
sem o Configurador Institucional (regras com fonte, natureza e versão) e sem o modelo comum
de dados. Isso reordena o roadmap técnico: a "Fase 3 — RAG" da v2 deixa de indexar apenas os
4 `.md` e passa a indexar também o perfil institucional produzido pelo S01.

**(d) A qualidade é mensurável.** Os artefatos `02` e `03` trazem testes de aceitação no
formato Dado/Quando/Então, casos de teste por skill, testes de integração INT-T01 a INT-T08
e metas quantitativas. A v3 adota esse aparato como plano de qualidade do projeto
(Seção 9), simplificando o que é especificamente acadêmico.

**(e) O backlog pressupõe uma equipe que não existe.** Dez papéis e 45–55 pontos por sprint
de 2 semanas correspondem a uma equipe multidisciplinar dedicada. A sequência funcional do
backlog é excelente e será preservada; as estimativas e a alocação são recalibradas na
Seção 5.

### 1.3. Pontos de atenção herdados da análise (não resolver silenciosamente)

| # | Ponto | Onde será tratado |
| --- | --- | --- |
| PA1 | Ambiguidade meta final × progresso esperado × marco intermediário (01, §2.3) | S05 — campos distintos e validações específicas (I3) |
| PA2 | Percentuais de referência de atividades indiretas são alertas, não proibições (01, §2.4) | S07/S08 — parâmetros configuráveis no S01 (I5) |
| PA3 | Estrutura "objeto + particípio" é preferência, não norma (01, §3.3) | S01/S02 — classificação da natureza das regras (I2) |
| PA4 | Regras institucionais específicas do ICMBio não estão nas 4 skills (01, §8) | S01 — cadastro de fontes oficiais é pré-requisito do MVP (I2) |

---

## 2. Objetivos, resultados esperados e escopo

### 2.1. Objetivo geral

Disponibilizar aos gestores do ICMBio um agente de IA, acessível via Copilot Studio (M365),
que **(a)** oriente a elaboração de Planos de Entregas e Planos de Trabalho executando as
skills S01–S10 com regras rastreáveis, **(b)** responda perguntas metodológicas citando a
fonte e **(c)** consulte os 12 indicadores OCDE/PGD em tempo real via Denodo.

### 2.2. Resultados-chave (revistos)

| RC | Resultado-chave | Como será medido |
| --- | --- | --- |
| RC1 | Agente responde perguntas metodológicas citando a fonte | 20 perguntas reais; ≥ 80% corretas com citação |
| RC2 | Agente consulta os 12 indicadores por unidade e período | Resultado idêntico ao CSV oficial do `pgd-ocde-icmbio` |
| RC3 | As 10 skills do MVP executam seus testes de aceitação | Casos de teste do `03` aprovados; INT-T01 a INT-T08 aprovados |
| RC4 | Um caso completo percorre S01→S10 sem perda de identificadores | Teste ponta a ponta com rastreabilidade de fontes |
| RC5 | Gestor acessa o agente no M365, sem novo login | Demonstração formal (Checkpoint B3) com ≥ 2 gestores |
| RC6 | Equipe de analistas opera o ciclo de vida de skill sem apoio externo | Cada analista conduz os passos 1–4 do ciclo (Seção 8) de forma autônoma |

### 2.3. Escopo

**Dentro:** MVP de 10 skills (S01–S10); modularização de B01–B04; RAG sobre metodologia +
perfil institucional; consulta aos 12 indicadores; API FastAPI; agente unificado; publicação
no Copilot Studio; capacitação da equipe; avaliação piloto adaptada.

**Fora (adiado deliberadamente):** S11–S20 (pactuação, monitoramento, replanejamento,
avaliação, evidências, relatórios, aprendizado, integrações); escrita de dados no PETRVS;
decisão automatizada de qualquer natureza; dados pessoais identificáveis; app móvel; modelo
de IA próprio; assinatura eletrônica. Inclusões exigem a versão 4 desta proposta.

### 2.4. Premissas e questões em aberto

Mantêm-se as premissas e questões Q1–Q4 da v2 (Seção 3), acrescidas de:

| # | Questão nova | Decide o quê | Quando responder |
| --- | --- | --- | --- |
| Q5 | Quais documentos oficiais do ICMBio alimentarão o S01 (portarias, INs, regimento, cadeia de valor)? | Conteúdo do perfil institucional; viabilidade do S02 | Antes do Incremento I2 |
| Q6 | O projeto terá dimensão acadêmica formal (padrão-ouro com 2 especialistas, condições experimentais A/B/C)? | Profundidade do plano de avaliação (Seção 9.4) | Antes do Incremento I6 |
| Q7 | Haverá reforço de equipe técnica (bolsista UFRN, TI, consultoria) em algum incremento? | Recalibragem dos prazos da Seção 6 | Revisão a cada checkpoint |

---

## 3. Visão do produto — as três capacidades do agente

A v2 definia duas capacidades. A análise da pasta `skills/` impõe uma terceira, que passa a
ser o núcleo do produto:

**(A) Conhecimento — "o bibliotecário" (RAG).** Documentos de metodologia (B01–B04), fichas
dos indicadores OCDE e o perfil institucional gerado pelo S01, indexados em banco vetorial.
Responde "o que é", "como se faz", "qual a regra" — sempre citando a fonte.

**(B) Ação sobre dados — "o consultor de plantão" (tool calling → Denodo).** A função
`consultar_indicador(indicador, periodo, unidade)`, herdada do padrão `run_query()` do
`pgd-ocde-icmbio`. Responde "qual a taxa da minha unidade neste quadrimestre" com dado real,
nunca de memória.

**(C) Skills executáveis — "o analista metodológico" (regras + validadores).** As skills
S01–S10 como funções estruturadas: recebem um objeto (texto de entrega, plano, lista de
competências), aplicam validadores compartilhados e devolvem **saída estruturada** com
diagnóstico, classificação, grau de confiança, fonte da regra aplicada e perguntas
pendentes. É o que diferencia o agente de um chatbot com documentos anexados.

As três capacidades convergem no agente unificado (Incremento I6): diante de uma pergunta,
ele decide se busca conhecimento (A), consulta dados (B) ou executa uma skill (C) — e pode
combinar as três ("analise esta entrega **e** me diga como a unidade está no I02").

### 3.1. Arquitetura em camadas (da análise `01`, mapeada na stack da v2)

```text
                ┌────────────────────────────────────────────────────┐
 Gestor ─────►  │              Copilot Studio (M365)                 │ ◄─ interface (I7)
                └───────────────────────┬────────────────────────────┘
                                        │ Custom Connector
                ┌───────────────────────▼────────────────────────────┐
                │        CAMADA 3 — Agente (Agno + FastAPI)          │ ◄─ orquestração (I6)
                │  decide: conhecimento (A) | dados (B) | skill (C)  │
                └───────┬──────────────────┬──────────────────┬──────┘
                        │A                 │B                 │C
                ┌───────▼───────┐  ┌───────▼────────┐  ┌──────▼──────────────┐
                │ RAG           │  │ Tool calling   │  │ CAMADA 2 — Skills   │
                │ LlamaIndex +  │  │ consultar_     │  │ S01–S10 +           │
                │ ChromaDB      │  │ indicador()    │  │ validadores comuns  │
                │               │  │ (JDBC→Denodo)  │  │ (Python)            │
                └───────┬───────┘  └────────────────┘  └──────┬──────────────┘
                        │                                     │
                ┌───────▼─────────────────────────────────────▼──────┐
                │ CAMADA 1 — Conhecimento institucional              │
                │ B01–B04 | fichas OCDE | perfil institucional (S01) │
                │ catálogo de entregas (S04)                         │
                ├────────────────────────────────────────────────────┤
                │ CAMADA 4 — Governança e dados                      │
                │ modelo comum | IDs | versões | histórico | logs |  │
                │ confiança | decisões humanas | controle de acesso  │
                └────────────────────────────────────────────────────┘
```

### 3.2. Modelo comum de dados

O esquema mínimo está especificado no artefato `03`, Seção 5, e é **vinculante** para todo o
projeto: `RegraInstitucional`, `EntregaCandidata`, `EntregaEstruturada`,
`PlanoDeCapacidade`, `VinculoOKRD`, `RegistroDeRisco`. Regras de ouro (do `03`, §16.2):

1. Toda entrega possui identificador persistente; nenhuma skill recria um objeto que pode
   referenciar.
2. Alterações geram nova versão — a anterior nunca é sobrescrita.
3. Toda saída automática registra origem, regra aplicada e grau de confiança.
4. Decisões humanas são registradas separadamente das sugestões do agente.
5. Dados ausentes não são preenchidos silenciosamente — viram perguntas pendentes.

No MVP, a persistência será em **SQLite local** (arquivo único, sem servidor, consultável
via Python e DBeaver) com o esquema versionado em `src/dados/schema.sql`. Migração para
PostgreSQL/Azure só se a dor de escala aparecer (mesma lógica de simplicidade da v2, §8.8).

### 3.3. Decisões de stack — o que muda em relação à v2

A tabela de stack da v2 (Seção 6) permanece válida. Acrescentam-se:

| Camada | Recomendação | Justificativa | Tipo |
| --- | --- | --- | --- |
| Persistência do modelo comum | **SQLite local** | Zero infraestrutura; suficiente para 1 unidade-piloto; esquema portável | Reversível |
| Formato dos contratos de skill | **JSON (Pydantic)** | Validação automática de entrada/saída; vira documentação OpenAPI de graça no FastAPI | Estruturante |
| Especificação das skills | **Arquivos `SKILL_Sxx.md` versionados** (template na Seção 8.2) | Analistas editam Markdown, não código; o código lê as regras da especificação | Estruturante |
| Implementação dos validadores | **Python puro + chamadas ao LLM onde há classificação semântica** | Cálculos (capacidade, somas, versões) são determinísticos e testáveis; só classificação de texto usa o modelo | Estruturante |

Essa última decisão implementa uma distinção crítica dos artefatos `02`/`03`: **cálculos
determinísticos exigem exatidão de 100%** (capacidade, totalização de 100%, versionamento) e
por isso não passam pelo LLM; classificações semânticas (entrega × atividade, plausibilidade
de vínculo OKR-D) usam o LLM com grau de confiança explícito e validação humana quando a
confiança for baixa.

---

## 4. Estrutura analítica do projeto (EAP)

```text
pgd-agente-icmbio (v3)
├── 1. GESTÃO DO PROJETO
│   ├── 1.1 Planejamento e revisões desta proposta
│   ├── 1.2 Ritos, atas e registro de decisões (ADRs)
│   ├── 1.3 Gestão de riscos e de escopo
│   └── 1.4 Checkpoints de demonstração (B1, B2, B3)
├── 2. TRILHA T — PLATAFORMA TECNOLÓGICA
│   ├── 2.1 Ambiente e repositório (Fase 0 da v2; Tutoriais T1–T2)
│   ├── 2.2 Núcleo conversacional: API do modelo + system prompt (T3)
│   ├── 2.3 Acesso a dados: consultar_indicador() via Denodo (T4)
│   ├── 2.4 RAG: Langflow (protótipo) → LlamaIndex + ChromaDB (T5)
│   ├── 2.5 Persistência: modelo comum de dados em SQLite
│   ├── 2.6 API própria: FastAPI + contratos das skills (T6)
│   ├── 2.7 Agente unificado: Agno (capacidades A+B+C)
│   └── 2.8 Integração M365: Custom Connector + Copilot Studio
├── 3. TRILHA N — SKILLS (REGRAS NEGOCIAIS)
│   ├── 3.1 Modularização de B01–B04 em validadores compartilhados
│   ├── 3.2 Bloco Fundação: S01 Configurador, S02 Verificador Normativo
│   ├── 3.3 Bloco Portfólio: S03 Extrator, S04 Catálogo, S05 Metas
│   ├── 3.4 Bloco Qualidade: S06 Auditor de Portfólio
│   ├── 3.5 Bloco Viabilidade: S07 Capacidade, S08 Cobertura
│   └── 3.6 Bloco Estratégia e Riscos: S09 OKR-D, S10 Riscos
├── 4. QUALIDADE E AVALIAÇÃO
│   ├── 4.1 Conjuntos anotados (exemplos reais rotulados)
│   ├── 4.2 Testes por skill (positivo/negativo/ambiguidade/integração)
│   ├── 4.3 Testes de integração INT-T01 a INT-T08
│   └── 4.4 Estudo-piloto com unidade real
└── 5. IMPLANTAÇÃO E CAPACITAÇÃO
    ├── 5.1 Capacitação da equipe (Tutoriais T1–T6 da v2)
    ├── 5.2 Homologação institucional (TI, segurança, política de IA)
    └── 5.3 Demonstrações a gestores e coleta de feedback
```

---

## 5. Gestão do projeto

### 5.1. Governança de artefatos — catálogo padronizado

Todo produto de trabalho do projeto pertence a uma série identificada. Isso permite
rastrear, cobrar e auditar o que existe:

| Série | Conteúdo | Local no repositório | Responsável primário |
| --- | --- | --- | --- |
| **GP-xx** | Gestão: proposta, atas, decisões (ADR), matriz de riscos | `docs/gestao/` | Coordenador |
| **AT-xx** | Tecnologia: arquitetura, esquema de dados, contratos de API, scripts | `src/`, `docs/tecnologia/` | Coordenador (papel técnico) |
| **AN-xx** | Negócio: especificações `SKILL_Sxx.md`, regras, exemplos anotados | `skills/specs/`, `skills/exemplos/` | Analistas de negócio |
| **QA-xx** | Qualidade: casos de teste, registros de execução, relatórios de métricas | `tests/`, `docs/testes/` | Analista designado por incremento |

Artefatos mínimos obrigatórios por incremento: 1 ata de abertura, 1 ata de encerramento com
critérios de aceite verificados, ADRs das decisões estruturantes tomadas, e os entregáveis
T e N listados na Seção 6.

### 5.2. Papéis — do backlog ideal à equipe real

O backlog `04` define dez papéis. A tabela abaixo os mapeia para a equipe disponível — o
mapeamento honesto é o que permite recalibrar prazos sem fantasia:

| Papel do backlog `04` | Quem exerce na prática | Observação |
| --- | --- | --- |
| PO — Produto e pesquisa | Coordenador do projeto (Leandro) | Prioriza backlog e aceita entregas |
| ARQ — Arquiteto/líder técnico | Coordenador do projeto | Decisões registradas em ADR para não ficarem só na cabeça de uma pessoa (risco R6 da v2) |
| IA — Engenheiro de IA | Coordenador, com apoio de ferramentas de IA assistida | Prompts, RAG, classificadores |
| BE — Backend | Coordenador + IA assistida | FastAPI, validadores, persistência |
| FE — Frontend | **Suprimido no MVP** | A interface é o Copilot Studio + páginas `/docs` do FastAPI; telas próprias ficam fora do escopo |
| QA — Qualidade | Analistas de negócio (rodízio por incremento) | Executam casos de teste do `03`; registram em `docs/testes/` |
| ED — Especialista de domínio | Analistas de negócio CGOV | Papel central: validam regras, anotam exemplos, compõem padrão de referência |
| DEVSEC — DevOps/segurança | Coordenador | Checklist pré-push (v2, §10.3); controle de acesso simplificado no MVP local |
| UX — Experiência | Analistas de negócio | Fluxos conversacionais e clareza das respostas |
| DA — Dados e avaliação | Coordenador + analista designado | Métricas da Seção 9 |

**Implicação assumida:** com FE suprimido e papéis acumulados, a capacidade real por
incremento é uma fração da capacidade de referência do `04` (45–55 pontos/sprint de 2
semanas). Adotam-se **incrementos de 3 a 6 semanas com dedicação parcial**, preservando a
sequência funcional do backlog e cortando o que era interface própria e aparato experimental
completo.

### 5.3. Matriz RACI consolidada

| Atividade | Coordenador | Analistas CGOV | TI institucional | Gestores |
| --- | --- | --- | --- | --- |
| Aprovar esta proposta e revisões | **A** | C | I | I |
| Especificar e validar skills (Trilha N, passos 1–4 do ciclo) | C | **R** | — | C |
| Implementar plataforma e validadores (Trilha T, passos 5–6) | **R** | C | I | — |
| Executar casos de teste e registrar resultados | A | **R** | — | — |
| Anotar exemplos e compor conjunto de referência | C | **R** | — | C |
| Provisionar Azure / Custom Connector (I7) | A | C | **R** | I |
| Participar dos checkpoints B1–B3 | R | R | I | **C** |

### 5.4. Ritos

- **Reunião quinzenal (30 min):** status por incremento (verde/amarelo/vermelho), riscos
  ativados, pendências de decisão. Ata curta em `docs/gestao/atas/`.
- **Revisão de incremento:** critérios de aceite verificados **antes** de abrir o seguinte;
  incremento sem critério atendido não é incremento concluído.
- **ADR (registro de decisão de arquitetura):** uma página por decisão estruturante em
  `docs/gestao/decisoes/ADR-nnn.md` — contexto, decisão, alternativas descartadas,
  consequências. As decisões das Seções 3.2 e 3.3 são os ADRs 001–005.
- **Revisão da matriz de riscos:** a cada checkpoint (B1, B2, B3).

---

## 6. Roadmap integrado — 8 incrementos (I0–I7)

### 6.1. Princípio de integração

Cada incremento pareia uma entrega de **plataforma (T)** com uma entrega de **conteúdo
negocial (N)** que a exercita. A correspondência com os planos anteriores:

| Incremento | Fase da v2 | Sprint do backlog `04` | Checkpoint |
| --- | --- | --- | --- |
| I0 — Fundação | Fase 0 | Sprint 1 (parte: modelo de dados, versionamento) | — |
| I1 — Núcleo conversacional | Fase 1 + B1 | — (pré-requisito técnico) | **B1** |
| I2 — Conhecimento institucional | Fases 2–3 (RAG) | Sprint 1 (S01) + Sprint 2 (S02) | — |
| I3 — Formação do portfólio | Fase 3 (contínua) | Sprint 2 (S03) + Sprint 3 (S04, S05) | — |
| I4 — Qualidade do plano | Fase 4 (parcial) | Sprint 4 (S06) | **B2** |
| I5 — Viabilidade | Fase 4 (parcial) | Sprint 5 (S07, S08) | — |
| I6 — Estratégia, riscos e agente unificado | Fase 4 (conclusão) | Sprint 6 (S09, S10) | — |
| I7 — Integração institucional e piloto | Fase 5 + B3 | Sprint 7 | **B3** |

Estimativas em semanas-calendário com dedicação parcial; são referências, não compromissos.
Total estimado: **28 a 40 semanas** (7 a 10 meses).

### 6.2. Detalhamento dos incrementos

#### I0 — Fundação (2–3 semanas)

| Frente | Entregáveis |
| --- | --- |
| T | Estrutura de pastas (Seção 7), `.venv`, `.gitignore`, `.env.example`, repo conectado (Tutoriais T1–T2); `schema.sql` v1 do modelo comum (6 entidades do `03`, §5) em SQLite; serviço mínimo de IDs e versões |
| N | Revisão e aprovação formal do modelo comum de dados pelos analistas; glossário institucional inicial (termos do PGD/ICMBio); levantamento dos documentos oficiais para o S01 (responde Q5) |
| Gestão | ADRs 001–005; matriz de riscos ativada; primeiro ciclo de atas |

**Aceite:** toda a equipe roda `git pull` e ativa o `.venv` sem ajuda; modelo de dados
criado no SQLite e documentado; lista de fontes institucionais aprovada.

#### I1 — Núcleo conversacional e primeiro indicador (3–4 semanas) → Checkpoint B1

| Frente | Entregáveis |
| --- | --- |
| T | `consulta_skill.py` (B01 como system prompt — Tutorial T3); `consultar_indicador.py` (I02 via Denodo — Tutorial T4); FastAPI com 2 endpoints (`POST /skill`, `GET /indicador/{id}` — Tutorial T6) |
| N | Bateria de 20 perguntas metodológicas reais com respostas esperadas (primeiro conjunto anotado, base do RC1); validação do resultado do I02 contra o CSV oficial |

**Aceite (B1):** demonstração ponta a ponta via `/docs` para um colega; I02 idêntico ao CSV
oficial; as 20 perguntas registradas em `skills/exemplos/`.

#### I2 — Conhecimento institucional: RAG + S01 + S02 (4–6 semanas)

| Frente | Entregáveis |
| --- | --- |
| T | Protótipo Langflow de ingestão (Tutorial T5, didático); `rag.py` (LlamaIndex + ChromaDB) indexando B01–B04 + fichas OCDE + documentos institucionais; cadastro de fontes e regras no SQLite (motor do S01); motor de verificação do S02 lendo regras por vigência |
| N | **S01:** carga dos documentos oficiais; classificação de cada regra por natureza (norma / regra institucional / recomendação / exemplo) com fonte e versão — trabalho dos analistas com apoio do classificador; conflitos marcados para decisão humana. **S02:** casos de teste S02-T01 a T06 executados |

**Aceite:** endpoint `/skill` responde via RAG citando o documento de origem; perfil
institucional versionado com ≥ 1 fonte oficial carregada; S02 distingue erro, alerta e
recomendação nos casos de teste; conflito de regras não é resolvido silenciosamente
(S01-T03).

#### I3 — Formação do portfólio: S03 + S04 + S05 (4–6 semanas)

| Frente | Entregáveis |
| --- | --- |
| T | Classificador objetivo/entrega/atividade/tarefa/responsabilidade com grau de confiança; extração de entrega candidata com vínculo ao trecho de origem; catálogo versionado com busca semântica (reutiliza o ChromaDB); designer de metas com separação meta final × progresso esperado (PA1); endpoints das 3 skills no FastAPI |
| N | Conjunto anotado de classificação (≥ 50 exemplos reais rotulados pelos analistas — competências do regimento, itens de planos reais); casos S03-T01 a T06, S04-T01 a T06, S05-T01 a T06 executados; primeiras entregas reais da CGOV processadas pelo fluxo S03→S04→S05 |

**Aceite:** competência regimental real vira entrega candidata com rastreabilidade;
candidata aprovada entra no catálogo com ID e versão; meta vaga é rejeitada com perguntas de
refinamento (S05-T03); macro-F1 inicial do classificador medida e registrada.

#### I4 — Qualidade do plano: S06 (3–4 semanas) → Checkpoint B2

| Frente | Entregáveis |
| --- | --- |
| T | Auditor de portfólio: duplicidade lexical e semântica, comparação com competências (matriz competência × entrega), granularidade, relatório consolidado com criticidade e confiança; endpoint `/portfolio/auditar` |
| N | Plano de entregas real (ou sintético realista) da unidade-piloto montado via S03–S05; casos S06-T01 a T06 executados; alertas revisados um a um pelos analistas (aceitar/corrigir/justificar) |

**Aceite (B2):** demonstração do fluxo documento institucional → candidatas → catálogo →
metas → auditoria, com RAG respondendo dúvidas metodológicas no caminho; relatório de
auditoria considerado útil pelos analistas (registro formal).

#### I5 — Viabilidade: S07 + S08 (3–5 semanas)

| Frente | Entregáveis |
| --- | --- |
| T | Motor de capacidade (nominal × útil, descontos de indisponibilidade — cálculo determinístico, exatidão 100%); cenários mínimo/provável/máximo; matriz entrega × participante; validação de totalização em 100%; alertas de sobrealocação, entrega sem cobertura e concentração. Integração com capacidade B: o agente pode citar I05–I08 reais da unidade ao discutir capacidade |
| N | Dados de capacidade da unidade-piloto (participantes, cargas, indisponibilidades — com os cuidados de dados pessoais da Seção 11); percentuais de atividades indiretas parametrizados como alertas (PA2); casos S07-T01 a T06 e S08-T01 a T06 executados |

**Aceite:** todos os cálculos determinísticos com exatidão de 100% nos testes; déficit de
horas diferenciado de lacuna de competência (S07-T05); plano individual ≠ 100% detectado.

#### I6 — Estratégia, riscos e agente unificado: S09 + S10 + Agno (4–6 semanas)

| Frente | Entregáveis |
| --- | --- |
| T | Estrutura OKR-D com vínculos muitos-para-muitos; auditoria de plausibilidade (direta/indireta/contextual — nunca causalidade afirmada); registro estruturado de riscos com classificador risco/impedimento/dependência/restrição; **agente Agno unificando as capacidades A + B + C**, decidindo sozinho qual acionar |
| N | Objetivos e resultados-chave institucionais reais carregados; casos S09-T01 a T08 e S10-T01 a T08 executados; bateria de 10 perguntas mistas (metodologia + indicador + skill) para o teste de decisão do agente |

**Aceite:** o agente escolhe a capacidade certa nas 10 perguntas mistas; entrega obrigatória
sem KR aceita justificativa operacional (S09-T08); risco sem impacto gera pergunta, não
preenchimento automático. **Iniciar aqui o processo com o TI institucional (risco R1).**

#### I7 — Integração institucional e piloto (4–8 semanas, dependente do TI) → Checkpoint B3

| Frente | Entregáveis |
| --- | --- |
| T | Orquestrador do fluxo S01–S10 com persistência de estado; testes INT-T01 a INT-T08; Custom Connector + topic no Copilot Studio (plano B: Streamlit de demonstração); migração do modelo para Azure OpenAI se Q2 confirmada |
| N | Estudo-piloto com a unidade-piloto percorrendo o fluxo completo; questionário de utilidade e confiança; correção apenas de defeitos críticos e altos; relatório final de métricas (Seção 9) |

**Aceite (B3):** ≥ 2 gestores usam o agente ao vivo pelo M365; caso completo percorre
S01→S10 sem perda de identificadores (RC4); feedback registrado; backlog pós-MVP (S11–S20)
priorizado para a v4.

---

## 7. Estrutura do repositório (revista)

```text
pgd-agente-icmbio/
  src/
    agente/                Núcleo conversacional e agente Agno (I1, I6)
    dados/                 Denodo (run_query) + SQLite (schema.sql, versoes.py)
    rag/                   Indexação e consulta (LlamaIndex + ChromaDB) (I2)
    skills_engine/         Validadores compartilhados e motor das skills (I2–I6)
      validadores/         classificar_elemento, validar_titulo, validar_4q1p,
                           validar_meta, calcular_capacidade, validar_percentuais...
      s01_configurador.py ... s10_riscos.py
    api/                   FastAPI — endpoints e contratos Pydantic
  skills/
    00_skill-*.md          B01–B04 — metodologia original (fonte RAG; não editar sem versão)
    01..04_*.md            Artefatos de análise e especificação (fonte desta proposta)
    specs/                 SKILL_S01.md ... SKILL_S10.md (template Seção 8.2)
    exemplos/              Conjuntos anotados (classificação, perguntas, planos de teste)
  data/
    config-institucional/  Documentos oficiais carregados no S01 (verificar sensibilidade)
    vectorstore/           ChromaDB local (ignorado pelo Git)
    pgd_agente.db          SQLite do modelo comum (ignorado pelo Git)
  prototipos/              Exports do Langflow (I2, didático)
  docs/
    gestao/                atas/, decisoes/ (ADRs), riscos.md
    tecnologia/            arquitetura.md, contratos-api.md
    testes/                Registros de execução dos casos de teste (QA-xx)
    referencia-pgd-ocde-icmbio.md
  tests/                   Testes automatizados (unitários e integração)
  .env.example | .env | .gitignore | requirements.txt | README.md
  proposta-projeto-v1.md   Registro histórico
  proposta-projeto-v2.md   ANEXO DE CAPACITAÇÃO — glossário + tutoriais T1–T6
  proposta-projeto-v3.md   Este documento
```

`.gitignore` acrescenta: `data/pgd_agente.db`, `data/config-institucional/` (até que cada
documento seja classificado como publicável) e mantém tudo da v2.

---

## 8. Ciclo de vida de uma skill — o mecanismo de integração das trilhas

Toda skill S01–S10 percorre os mesmos sete passos. Os passos 1–4 são **trabalho de negócio**
(analistas); 5–6 são **trabalho técnico**; 7 é conjunto. É este ciclo que garante o
desenvolvimento "sequencial e integrado" pedido pelo projeto.

### 8.1. Os sete passos

| Passo | Atividade | Responsável | Artefato produzido |
| --- | --- | --- | --- |
| 1 | **Especificar** — preencher `SKILL_Sxx.md` a partir dos artefatos `02` e `03` | Analista (ED) | AN: `skills/specs/SKILL_Sxx.md` |
| 2 | **Definir regras** — listar cada regra com natureza (norma/institucional/recomendação) e fonte | Analista (ED) | AN: seção Regras da spec |
| 3 | **Anotar exemplos** — casos reais rotulados: válidos, inválidos, ambíguos | Analista (ED) | AN: `skills/exemplos/Sxx_*.md` ou planilha |
| 4 | **Escrever casos de teste** — Dado/Quando/Então (partir dos já existentes no `03`) | Analista (QA) | QA: casos em `docs/testes/` |
| 5 | **Implementar** — validadores + prompt + contrato Pydantic + endpoint | Coordenador (BE/IA) | AT: código em `src/skills_engine/` |
| 6 | **Integrar** — registrar a skill no agente; testes automatizados | Coordenador | AT: testes em `tests/` |
| 7 | **Validar aceite** — analistas executam os casos de teste; divergências viram correção ou ajuste de spec | Ambos | QA: registro de execução; ata de aceite |

Regra de fluxo: **nenhuma skill entra no passo 5 sem os passos 1–4 concluídos**, e nenhuma é
declarada pronta sem o passo 7 registrado. Os critérios globais de pronto do artefato `02`,
Seção 8 (entrada, saída, rastreabilidade, transparência, controle humano, versionamento,
interoperabilidade, proteção de dados, testes, experiência) valem integralmente.

### 8.2. Template de especificação — `skills/specs/SKILL_Sxx.md`

```markdown
# SKILL_Sxx — [Nome]
**Versão:** 1.0 | **Estado:** rascunho | em validação | aprovada
**Prioridade:** P0–P3 | **Incremento:** In | **Fonte:** 02_matriz (Sxx); 03_especificacao (§n)

## 1. Objetivo funcional
[1–3 frases: o que a skill faz e para quem]

## 2. Entradas (contrato)
| Campo | Tipo | Obrigatório | Origem (skill/usuário) |

## 3. Saídas (contrato)
| Campo | Tipo | Sempre presente? | Observação |
[Toda saída inclui: diagnostico, confianca (alta/média/baixa), fontes[], perguntas_pendentes[]]

## 4. Regras
| # | Regra | Natureza (norma/institucional/recomendação) | Fonte | Verificação |

## 5. Comportamento em ambiguidade
[O que a skill pergunta quando não pode concluir; o que NUNCA preenche sozinha]

## 6. Casos de teste
[Referência aos casos Sxx-T do artefato 03 + casos novos]

## 7. Dependências
[Skills e validadores requeridos — conferir 02_matriz, §6]

## 8. Histórico de alterações
| Data | Versão | Mudança | Autor |
```

### 8.3. Contrato técnico de saída (padrão para todas as skills)

```json
{
  "skill": "S03",
  "versao_skill": "1.0",
  "resultado": { "...": "estrutura específica da skill" },
  "confianca": "alta | media | baixa",
  "fontes": [ {"documento": "...", "trecho": "...", "natureza": "norma|institucional|recomendacao"} ],
  "regras_aplicadas": ["R-014", "R-022"],
  "perguntas_pendentes": ["Qual produto existirá ao final?"],
  "requer_validacao_humana": true,
  "executado_em": "2026-07-26T10:00:00",
  "modelo": "claude-sonnet-x",
  "rastreio_id": "uuid"
}
```

---

## 9. Plano de qualidade e avaliação

### 9.1. Tipos de teste (herdados do `03`, §4.3)

Positivo, negativo, ambiguidade, limite, integração, regressão, explicabilidade e segurança.
Cada skill precisa de ao menos os quatro primeiros; a suíte de regressão cresce a cada
defeito relevante (BT-03 do backlog).

### 9.2. Métricas essenciais do MVP (recorte pragmático das metas do `03`, §18.9)

| Indicador | Meta | Quando medir |
| --- | --- | --- |
| Exatidão dos cálculos determinísticos (S07, S08, versões) | 100% | I5 em diante |
| Macro-F1 da classificação de textos (S03) | ≥ 0,85 | I3, I7 |
| Saídas com fonte corretamente associada | ≥ 0,95 | I2 em diante |
| Precisão de não conformidades (S02) | ≥ 0,90 | I2, I7 |
| Indicadores idênticos ao CSV oficial (RC2) | 100% | I1, I7 |
| Perguntas metodológicas corretas com citação (RC1) | ≥ 80% | I2, I7 |
| Testes INT-T01 a INT-T08 | 8/8 aprovados | I7 |
| Satisfação dos usuários do piloto | ≥ 4 (escala 1–5) | I7 |

As demais metas acadêmicas do `03` (concordância entre especialistas, padrão-ouro duplo,
três condições experimentais) ficam **condicionadas à resposta de Q6**: se o projeto assumir
dimensão acadêmica formal, adota-se o plano completo do `03`, §18; caso contrário, aplica-se
o desenho simplificado abaixo.

### 9.3. Rubrica de qualidade de entregas

A rubrica de 10 dimensões × 0–4 pontos do `03`, §18.8 (máximo 40 pontos) é adotada como
instrumento padrão para avaliar entregas produzidas com e sem o agente.

### 9.4. Estudo-piloto (desenho simplificado — 2 condições)

1. Selecionar 1 unidade-piloto e 10–15 entregas/itens reais.
2. **Condição A (linha de base):** analistas avaliam os itens com a rubrica, sem o agente.
3. **Condição C (agente):** os mesmos itens processados pelo fluxo S01–S10; saídas avaliadas
   com a mesma rubrica.
4. Comparar pontuações, tempo e número de problemas detectados; registrar percepção de
   utilidade e confiança (questionário curto).
5. Limitações registradas honestamente (amostra pequena, avaliadores não cegos).

### 9.5. Registro de execução

Para cada execução de teste: versão da skill, versão do modelo, configuração institucional,
entrada, saída integral, resultado (aprovado/reprovado), avaliador e data — em
`docs/testes/`. É a base da reprodutibilidade exigida pelo `03`, §17.5.

---

## 10. Matriz de riscos consolidada

Funde os riscos da v2 (R1–R7) com os riscos de implementação do `04`, §17 (R01–R14):

| # | Risco | Prob. | Impacto | Mitigação | Dono |
| --- | --- | --- | --- | --- | --- |
| RP01 | Provisionamento Azure/Connector atrasar e travar I7 (v2-R1) | Alta | Alto | Processo com TI iniciado em I6; Streamlit como plano B | Coordenador |
| RP02 | Agente alucinar números ou regras (v2-R2; 04-R02) | Média | Alto | Indicadores só via tool calling; toda regra com fonte; confiança explícita; validação humana em baixa confiança | Coordenador |
| RP03 | Confusão entre norma e recomendação (04-R01; PA3) | Alta | Alto | Natureza da regra é campo obrigatório no S01; teste S01-T04 | Analistas |
| RP04 | Meta confundir esforço com resultado; meta × progresso (04-R04; PA1) | Alta | Alto | Campos distintos no S05 + validador específico; teste S05-T04 | Analistas |
| RP05 | Cálculos de capacidade com falsa precisão (04-R06) | Alta | Médio | Faixas e cenários; incerteza sempre visível | Coordenador |
| RP06 | Dados individuais de disponibilidade expostos (04-R07) | Média | Alto | Perfis, agregação em relatórios, checklist da Seção 11 | Coordenador |
| RP07 | OKR-D afirmar causalidade indevida (04-R08) | Alta | Alto | Linguagem de contribuição plausível; justificativa obrigatória | Analistas |
| RP08 | Excesso de alertas na auditoria tornar o agente irritante (04-R05) | Média | Alto | Gravidade + confiança + limiar configurável; revisão com usuários no I4 | Analistas |
| RP09 | Escopo crescer ("já que estamos fazendo…") (v2-R5; 04-R14) | Alta | Alto | S11–S20 e exclusões do `04` §20 fora do MVP; inclusão exige v4 | Coordenador |
| RP10 | Dependência de pessoa única (v2-R6) | Alta | Alto | ADRs, specs em Markdown editáveis por analistas, tutoriais, pareamento; ciclo de vida com papéis explícitos | Todos |
| RP11 | Equipe não absorver o papel de ED/QA (v2-R4) | Média | Alto | RC6 (resultado-chave) mede autonomia; passos 1–4 do ciclo são deliberadamente não técnicos | Coordenador |
| RP12 | Credencial vazar em repositório (v2-R3) | Baixa | Alto | `.gitignore` desde o dia zero; verificação pré-push (v2, §10.3) | Coordenador |
| RP13 | Integrações perderem histórico/IDs (04-R10) | Média | Alto | IDs persistentes e versionamento desde I0; teste RC4/INT-T01 | Coordenador |
| RP14 | Custo de API sair do controle (v2-R7) | Baixa | Baixo | Limite mensal no provedor (Tutorial T3) | Coordenador |

---

## 11. Governança de dados e uso responsável de IA

Herda integralmente a Seção 10.2–10.3 da v2 (transparência, somente leitura no PETRVS,
verificação pré-push, política institucional de IA) e acrescenta, por força das novas skills:

1. **Dados de pessoas entram no projeto pela primeira vez** (S07/S08: participantes, cargas,
   indisponibilidades). Tratamento: dados reais só na máquina local e no SQLite ignorado
   pelo Git; relatórios e exemplos versionados usam dados **anonimizados ou sintéticos**;
   motivo de indisponibilidade nunca é detalhado (basta "indisponível X horas").
2. **Documentos institucionais carregados no S01** ficam em `data/config-institucional/`
   (fora do Git) até serem classificados como publicáveis, um a um.
3. **O agente não decide.** Nenhuma skill aprova plano, avalia pessoa ou resolve conflito
   normativo — saídas são sugestões com fonte; decisões humanas são registradas à parte
   (princípio transversal dos artefatos `02` e `03`).
4. **Rastreabilidade como requisito, não como recurso.** Se um gestor questionar uma
   resposta, deve ser possível reconstituir: fontes, regras, versão da skill, versão do
   modelo e quem validou (Seção 9.5).

---

## 12. Checklist de execução da v3

- [ ] **I0** — repo estruturado; `schema.sql` no SQLite; ADRs 001–005; fontes institucionais levantadas (Q5)
- [ ] **I1 / B1** — 2 endpoints demonstrados; I02 = CSV oficial; 20 perguntas anotadas
- [ ] **I2** — RAG citando fontes; perfil institucional versionado (S01); S02 com casos T01–T06 aprovados
- [ ] **I3** — fluxo S03→S04→S05 com entregas reais; macro-F1 medida; conjunto anotado ≥ 50 exemplos
- [ ] **I4 / B2** — auditoria de portfólio demonstrada ponta a ponta; utilidade registrada
- [ ] **I5** — cálculos determinísticos 100%; matriz de cobertura funcionando; dados pessoais protegidos
- [ ] **I6** — agente Agno decide entre A/B/C em 10 perguntas mistas; **processo TI iniciado**
- [ ] **I7 / B3** — INT-T01 a INT-T08 aprovados; Copilot Studio ativo; piloto executado; ≥ 2 gestores ao vivo
- [ ] Métricas da Seção 9.2 medidas e registradas
- [ ] Backlog pós-MVP (S11–S20) priorizado → insumo da proposta v4

---

*Documento elaborado como revisão consultiva independente, integrando a proposta v2 aos
artefatos 01–04 da pasta `skills/`. Alterações de escopo ou de stack geram a versão 4, com
registro do motivo em `docs/gestao/decisoes/`. A v2 permanece como Anexo de Capacitação
(glossário e Tutoriais T1–T6); os artefatos `02_matriz`, `03_especificacao` e `04_backlog`
permanecem como especificações vinculadas desta proposta.*
