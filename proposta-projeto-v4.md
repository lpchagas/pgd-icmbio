# Proposta de Projeto — `pgd-agente-icmbio`

**Versão:** 4.0 | **Data:** 26.07.2026
**Substitui:** `proposta-projeto-v3.md` como documento de planejamento e gestão.
A v2 **permanece válida como Anexo de Capacitação** — seu Glossário (Seção 4) e seus
Tutoriais T1–T6 (Seção 9) continuam sendo o material de referência da equipe. A v3 passa a
registro histórico.
**Anexo técnico vinculante:** `docs/tecnologia/AT-01_analise-petrvs-esquema-mysql_v1.md`
(aprovado em 26.07.2026 com as decisões D1–D4 conforme recomendado; ADR-006).
**Papel assumido nesta proposta:** consultor independente sênior em engenharia de software e
gestão de projetos.
**Público-alvo:** equipe de projeto formada por analistas de negócio da CGOV/ICMBio.

---

## Sumário executivo

A v3 integrou as duas frentes do projeto — Trilha T (plataforma tecnológica) e Trilha N
(skills como regras negociais) — num roadmap único de 8 incrementos, e definiu o modelo
comum de dados como elemento vinculante de todo o MVP. Esta v4 é uma **revisão dirigida**:
mantém integralmente o escopo, as 10 skills S01–S10, os resultados-chave RC1–RC6, os papéis,
o ciclo de vida de skill e o roadmap I0–I7 da v3, e altera **uma única decisão estruturante**
com suas propagações: a persistência do modelo comum de dados.

**O que muda e por quê.** A análise AT-01 da estrutura real do PETRVS (MySQL 8 na origem,
123 views acessadas via Denodo) demonstrou que o sistema-fonte já pratica, em produção, as
convenções que as "regras de ouro" da Seção 3.2 exigem: identidade persistente por UUID
`CHAR(36)`, não-destruição por soft-delete universal, auditoria temporal e vínculos
estratégicos N:N. O SQLite prescrito na v3 obrigaria uma camada de tradução permanente entre
o modelo comum e os dados reais extraídos do Denodo. A v4 adota **MySQL 8 Community local**,
com esquema de **21 tabelas** modelado sobre as convenções do PETRVS — o que torna o modelo
comum **interoperável por construção**: uma entrega estruturada do agente referencia a
`unidade_id` real do ICMBio e pode ser comparada campo a campo com uma
`planos_entregas_entregas` real no piloto.

**As quatro decisões aprovadas (ADR-006):**

1. **D1 — MySQL 8 Community local** substitui o SQLite; esquema em `src/dados/schema.sql`
   (21 tabelas do AT-01 §5); imutabilidade de versões garantida por triggers no banco.
2. **D2 — Espelho mínimo de servidores:** `ref_usuarios` sincroniza apenas a unidade-piloto,
   sem CPF, e-mail ou situação funcional; relatórios usam pseudônimos.
3. **D3 — Identidade dupla:** UUID (técnica) + código legível citável (`ENT-2026-0001`,
   `R-014`) nas saídas das skills.
4. **D4 — Serviço Windows, sem Docker:** MySQL Community como serviço local, porta 3306,
   credenciais no `.env`, backup por `mysqldump` diário.

As quatro decisões estruturantes da v3 (roadmap único I0–I7, terceira capacidade do agente,
papéis adaptados à equipe real, ciclo de vida padronizado de skill) permanecem em vigor.

---

## 1. Análise da pasta `skills/` — o que existe e o que muda

*(Seção mantida da v3 sem alteração de conteúdo.)*

### 1.1. Inventário e papel de cada arquivo

| Arquivo | Natureza | Papel no projeto a partir da v3/v4 |
| --- | --- | --- |
| `00_skill-analise-entrega-v1.md` | Metodologia (B01) | Fonte de regras do classificador/validador de entregas; base de conhecimento RAG |
| `00_skill-okrd-v1.md` | Metodologia (B02) | Fonte conceitual da cadeia OKR-D; base do S09 |
| `00_skill-plano-entregas-v1.md` | Metodologia (B03) | Orquestrador conceitual do plano de entregas; base de S03–S06 |
| `00_skill-plano-trabalho-v1.md` | Metodologia (B04) | Regras de alocação de esforço; base de S07–S08 |
| `01_analise-skills_v1.md` | Análise crítica | Diagnóstico de fragilidades; origem da arquitetura em 4 camadas e das 20 skills |
| `02_matriz-desenvolvimento-skills_v2.md` | Matriz de desenvolvimento | **Especificação mestra**: 20 skills (S01–S20), prioridades P0–P3, dependências, testes de aceitação, critérios globais de pronto |
| `03_especificacao-funcional-skills_v2.md` | Especificação funcional | **Detalhamento do MVP (S01–S10)**: perfis, histórias de usuário, modelo de dados, casos de teste, requisitos não funcionais, plano de avaliação |
| `04_backlog-mvp-skills_v2.md` | Backlog executável | **Plano de execução**: 7 sprints, épicos, estimativas, riscos, definição de pronto |
| `docs/tecnologia/AT-01_*.md` | Análise técnica (novo na v4) | **Anexo vinculante**: análise do PETRVS e esquema MySQL do modelo comum (DDL de referência) |

### 1.2. Conclusões da análise incorporadas (v3, mantidas)

**(a)** As skills deixaram de ser documentos e viraram software com regras de negócio —
validadores compartilhados, esquema canônico, objetos com ID persistente; o RAG é uma das
camadas, não a estratégia inteira. **(b)** O MVP tem escopo fechado: 10 skills (S01–S10);
S11–S20 ficam fora por decisão registrada no `04`, Seção 20. **(c)** O caminho crítico é
sequencial e começa pelo S01 e pelo modelo comum de dados. **(d)** A qualidade é mensurável
— testes Dado/Quando/Então, INT-T01 a INT-T08, metas quantitativas. **(e)** O backlog
pressupõe equipe que não existe; a sequência funcional é preservada e as estimativas
recalibradas (Seção 5).

### 1.3. Pontos de atenção herdados (não resolver silenciosamente)

| # | Ponto | Onde será tratado |
| --- | --- | --- |
| PA1 | Ambiguidade meta final × progresso esperado × marco intermediário (01, §2.3) | S05 — campos distintos (`meta` vs `meta_final` no esquema AT-01 §5.4) e validações específicas (I3) |
| PA2 | Percentuais de referência de atividades indiretas são alertas, não proibições (01, §2.4) | S07/S08 — parâmetro `atividades_indiretas_perc` configurável (I5) |
| PA3 | Estrutura "objeto + particípio" é preferência, não norma (01, §3.3) | S01/S02 — campo `natureza` obrigatório da regra (I2) |
| PA4 | Regras institucionais específicas do ICMBio não estão nas 4 skills (01, §8) | S01 — cadastro de fontes oficiais é pré-requisito do MVP (I2) |

---

## 2. Objetivos, resultados esperados e escopo

### 2.1. Objetivo geral

Disponibilizar aos gestores do ICMBio um agente de IA, acessível via Copilot Studio (M365),
que **(a)** oriente a elaboração de Planos de Entregas e Planos de Trabalho executando as
skills S01–S10 com regras rastreáveis, **(b)** responda perguntas metodológicas citando a
fonte e **(c)** consulte os 12 indicadores OCDE/PGD em tempo real via Denodo.

### 2.2. Resultados-chave (mantidos da v3)

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
avaliação, evidências, relatórios, aprendizado, integrações); **escrita de dados no PETRVS**
(o MySQL local é banco próprio do agente — o PETRVS permanece somente leitura via Denodo);
decisão automatizada de qualquer natureza; dados pessoais identificáveis; app móvel; modelo
de IA próprio; assinatura eletrônica. Inclusões exigem a versão 5 desta proposta.

### 2.4. Premissas e questões em aberto

Mantêm-se as premissas e questões Q1–Q4 da v2 (Seção 3) e Q5–Q7 da v3 (Seção 2.4). As
questões D1–D4 levantadas pelo AT-01 foram **respondidas e encerradas** em 26.07.2026
(ADR-006).

| # | Questão em aberto | Decide o quê | Quando responder |
| --- | --- | --- | --- |
| Q5 | Quais documentos oficiais do ICMBio alimentarão o S01 (portarias, INs, regimento, cadeia de valor)? | Conteúdo do perfil institucional; viabilidade do S02 | Antes do Incremento I2 |
| Q6 | O projeto terá dimensão acadêmica formal (padrão-ouro com 2 especialistas, condições experimentais A/B/C)? | Profundidade do plano de avaliação (Seção 9.4) | Antes do Incremento I6 |
| Q7 | Haverá reforço de equipe técnica (bolsista UFRN, TI, consultoria) em algum incremento? | Recalibragem dos prazos da Seção 6 | Revisão a cada checkpoint |
| Q8 *(nova)* | Qual é a unidade-piloto? | Escopo do espelho `ref_usuarios` (D2) e dados de capacidade do I5 | **Respondida em 26.07.2026: CGOV e COCAGE** são as unidades-piloto |

---

## 3. Visão do produto — as três capacidades do agente

As três capacidades definidas na v3 permanecem: **(A) Conhecimento** — "o bibliotecário"
(RAG sobre B01–B04, fichas OCDE e perfil institucional); **(B) Ação sobre dados** — "o
consultor de plantão" (`consultar_indicador()` via Denodo); **(C) Skills executáveis** — "o
analista metodológico" (S01–S10 com validadores, contratos e saídas estruturadas). O agente
unificado (I6) decide qual acionar e pode combiná-las.

### 3.1. Arquitetura em camadas (mantida da v3; Camada 4 agora em MySQL)

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
                │ CAMADA 4 — Governança e dados  ►  MySQL 8 local    │
                │ modelo comum (21 tabelas) | IDs UUID + códigos |   │
                │ versões imutáveis (triggers) | execuções | logs |  │
                │ decisões humanas | perguntas pendentes |           │
                │ espelhos ref_* (Denodo→local)                      │
                └────────────────────────────────────────────────────┘
```

### 3.2. Modelo comum de dados *(revisado — mudança central da v4)*

O esquema conceitual mínimo continua sendo o do artefato `03`, Seção 5 — 6 entidades
vinculantes: `RegraInstitucional`, `EntregaCandidata`, `EntregaEstruturada`,
`PlanoDeCapacidade`, `VinculoOKRD`, `RegistroDeRisco`. As regras de ouro (do `03`, §16.2)
permanecem integralmente:

1. Toda entrega possui identificador persistente; nenhuma skill recria um objeto que pode
   referenciar.
2. Alterações geram nova versão — a anterior nunca é sobrescrita.
3. Toda saída automática registra origem, regra aplicada e grau de confiança.
4. Decisões humanas são registradas separadamente das sugestões do agente.
5. Dados ausentes não são preenchidos silenciosamente — viram perguntas pendentes.

**A persistência será em MySQL 8 Community local** (serviço Windows, porta 3306, sem
Docker), com esquema de **21 tabelas** especificado no AT-01 §5 e versionado em
`src/dados/schema.sql`, organizado em cinco grupos:

| Grupo | Tabelas | Implementa |
| --- | --- | --- |
| Referência espelhada | `ref_unidades`, `ref_usuarios` | FKs lógicas para UUIDs reais do ICMBio (Denodo → local) |
| Configuração institucional | `fontes_institucionais`, `regras_institucionais` (+`_versoes`), `regras_conflitos` | S01/S02; entidade 5.1 |
| Portfólio | `entregas_candidatas`, `entregas` (+`_versoes`) | S03–S06; entidades 5.2 e 5.3 |
| Viabilidade | `planos_capacidade`, `participantes`, `indisponibilidades`, `alocacoes` | S07/S08; entidade 5.4 |
| Estratégia, riscos e governança | `okrd_objetivos`, `okrd_resultados_chave`, `vinculos_okrd`, `registros_risco`, `execucoes_skill`, `decisoes_humanas`, `perguntas_pendentes`, `schema_migracoes` | S09/S10; entidades 5.5–5.6; regras de ouro 3–5 |

O esquema **herda as convenções estruturais do PETRVS** (PK UUID `CHAR(36)`, soft-delete
`deleted_at`, auditoria `created/updated_at`, `ENUM` para status, `JSON` nativo,
`DECIMAL(5,2)` para métricas) e as **completa** onde o PETRVS não chega: entidades
versionáveis usam o padrão **cabeçalho + versões INSERT-only**, com triggers que rejeitam
`UPDATE`/`DELETE` no histórico (AT-01 §6.3) — a regra de ouro 2 é garantida pelo banco,
não apenas pela aplicação. Campos `petrvs_entrega_id`/`petrvs_catalogo_id` permitem
confrontar, no piloto, a entrega redigida pelo agente com a entrega real no PETRVS.

### 3.3. Decisões de stack — o que muda em relação à v3

A tabela de stack da v2 (Seção 6) permanece válida. A tabela da v3 §3.3 é revisada assim:

| Camada | Recomendação | Justificativa | Tipo |
| --- | --- | --- | --- |
| Persistência do modelo comum | **MySQL 8 Community local (serviço Windows, sem Docker)** — revisa ADR-001; registrado no ADR-006 | Paridade de dialeto e convenções com o PETRVS; interoperabilidade por construção com dados do Denodo; triggers de imutabilidade; DBeaver já dominado pela equipe | Estruturante |
| Identidade dos objetos | **UUID v4 + código legível** (`ENT-2026-0001`, `R-014`) | UUID nunca colide com IDs do PETRVS; código legível é citável nas saídas das skills (§8.3) | Estruturante |
| Formato dos contratos de skill | **JSON (Pydantic)** | Validação automática de entrada/saída; vira documentação OpenAPI no FastAPI | Estruturante |
| Especificação das skills | **Arquivos `SKILL_Sxx.md` versionados** (template na Seção 8.2) | Analistas editam Markdown, não código | Estruturante |
| Implementação dos validadores | **Python puro + chamadas ao LLM onde há classificação semântica** | Cálculos determinísticos exigem exatidão de 100% e não passam pelo LLM | Estruturante |

---

## 4. Estrutura analítica do projeto (EAP)

```text
pgd-agente-icmbio (v4)
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
│   ├── 2.5 Persistência: modelo comum em MySQL 8 (schema.sql,
│   │       versoes.py, sincronizar_ref.py, backup mysqldump)
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

### 5.1. Governança de artefatos — catálogo padronizado (mantido)

| Série | Conteúdo | Local no repositório | Responsável primário |
| --- | --- | --- | --- |
| **GP-xx** | Gestão: proposta, atas, decisões (ADR), matriz de riscos | `docs/gestao/` | Coordenador |
| **AT-xx** | Tecnologia: arquitetura, esquema de dados, contratos de API, scripts | `src/`, `docs/tecnologia/` | Coordenador (papel técnico) |
| **AN-xx** | Negócio: especificações `SKILL_Sxx.md`, regras, exemplos anotados | `skills/specs/`, `skills/exemplos/` | Analistas de negócio |
| **QA-xx** | Qualidade: casos de teste, registros de execução, relatórios de métricas | `tests/`, `docs/testes/` | Analista designado por incremento |

O **AT-01** (análise PETRVS + esquema MySQL) inaugura a série AT e é o documento de
referência do modelo de dados; alterações no esquema geram nova versão do AT-01 e migração
registrada em `schema_migracoes`.

### 5.2. Papéis — do backlog ideal à equipe real (mantido da v3)

| Papel do backlog `04` | Quem exerce na prática | Observação |
| --- | --- | --- |
| PO — Produto e pesquisa | Coordenador do projeto (Leandro) | Prioriza backlog e aceita entregas |
| ARQ — Arquiteto/líder técnico | Coordenador do projeto | Decisões registradas em ADR (risco RP10) |
| IA — Engenheiro de IA | Coordenador, com apoio de ferramentas de IA assistida | Prompts, RAG, classificadores |
| BE — Backend | Coordenador + IA assistida | FastAPI, validadores, persistência MySQL |
| FE — Frontend | **Suprimido no MVP** | Interface = Copilot Studio + `/docs` do FastAPI |
| QA — Qualidade | Analistas de negócio (rodízio por incremento) | Executam casos de teste do `03` |
| ED — Especialista de domínio | Analistas de negócio CGOV | Validam regras, anotam exemplos |
| DEVSEC — DevOps/segurança | Coordenador | Checklist pré-push; backup MySQL; controle de acesso |
| UX — Experiência | Analistas de negócio | Fluxos conversacionais |
| DA — Dados e avaliação | Coordenador + analista designado | Métricas da Seção 9 |

Implicação mantida: incrementos de **3 a 6 semanas com dedicação parcial**, preservando a
sequência funcional do backlog.

### 5.3. Matriz RACI consolidada (mantida da v3)

| Atividade | Coordenador | Analistas CGOV | TI institucional | Gestores |
| --- | --- | --- | --- | --- |
| Aprovar esta proposta e revisões | **A** | C | I | I |
| Especificar e validar skills (Trilha N, passos 1–4 do ciclo) | C | **R** | — | C |
| Implementar plataforma e validadores (Trilha T, passos 5–6) | **R** | C | I | — |
| Executar casos de teste e registrar resultados | A | **R** | — | — |
| Anotar exemplos e compor conjunto de referência | C | **R** | — | C |
| Provisionar Azure / Custom Connector (I7) | A | C | **R** | I |
| Participar dos checkpoints B1–B3 | R | R | I | **C** |

### 5.4. Ritos (mantidos da v3)

- **Reunião quinzenal (30 min):** status por incremento, riscos ativados, pendências.
- **Revisão de incremento:** critérios de aceite verificados **antes** de abrir o seguinte.
- **ADR:** uma página por decisão estruturante em `docs/gestao/decisoes/ADR-nnn.md`.
  ADRs 001–005 = decisões da v3 §3.2/3.3; **ADR-006 = persistência MySQL (esta v4)**.
- **Revisão da matriz de riscos:** a cada checkpoint (B1, B2, B3).

---

## 6. Roadmap integrado — 8 incrementos (I0–I7)

### 6.1. Princípio de integração (mantido)

Cada incremento pareia uma entrega de **plataforma (T)** com uma entrega de **conteúdo
negocial (N)**. Correspondências com v2/backlog `04` e checkpoints B1–B3 mantidas da v3.
Total estimado: **28 a 40 semanas** (7 a 10 meses).

### 6.2. Detalhamento dos incrementos

#### I0 — Fundação (2–4 semanas) *(revisado)*

| Frente | Entregáveis |
| --- | --- |
| T | Estrutura de pastas (Seção 7), `.venv`, `.gitignore`, `.env.example`, repo conectado (Tutoriais T1–T2); **instalação do MySQL 8 Community como serviço Windows (D4)**; `src/dados/schema.sql` v1 aplicado — **21 tabelas do AT-01 §5** — com **triggers de imutabilidade ativos**; serviço de IDs e versões (`versoes.py`: UUID + códigos legíveis D3, `nova_versao()` transacional); rotina `sincronizar_ref.py` (Denodo → `ref_unidades` completa + `ref_usuarios` da unidade-piloto, D2); rotina de backup `mysqldump` diário |
| N | Revisão e aprovação formal do modelo comum pelos analistas (o AT-01 já foi aprovado pelo coordenador; os analistas validam nomenclatura e campos contra o vocabulário do PGD); glossário institucional inicial; levantamento dos documentos oficiais para o S01 (responde Q5); **definição da unidade-piloto (responde Q8)** |
| Gestão | ADRs 001–006 registrados; matriz de riscos ativada; primeiro ciclo de atas |

**Aceite:** banco `pgd_agente` criado com as 21 tabelas; tentativa de `UPDATE` em
`entregas_versoes` rejeitada pelo trigger (teste de imutabilidade); `sincronizar_ref.py`
executada com as unidades reais e os servidores da unidade-piloto; toda a equipe roda
`git pull` e ativa o `.venv` sem ajuda; lista de fontes institucionais aprovada; primeiro
`mysqldump` de backup gerado.

#### I1 — Núcleo conversacional e primeiro indicador (3–4 semanas) → Checkpoint B1

| Frente | Entregáveis |
| --- | --- |
| T | `consulta_skill.py` (B01 como system prompt — Tutorial T3); `consultar_indicador.py` (I02 via Denodo — Tutorial T4); FastAPI com 2 endpoints (`POST /skill`, `GET /indicador/{id}` — Tutorial T6) |
| N | Bateria de 20 perguntas metodológicas reais com respostas esperadas (base do RC1); validação do resultado do I02 contra o CSV oficial |

**Aceite (B1):** demonstração ponta a ponta via `/docs`; I02 idêntico ao CSV oficial; as 20
perguntas registradas em `skills/exemplos/`.

#### I2 — Conhecimento institucional: RAG + S01 + S02 (4–6 semanas)

| Frente | Entregáveis |
| --- | --- |
| T | Protótipo Langflow de ingestão (Tutorial T5); `rag.py` (LlamaIndex + ChromaDB) indexando B01–B04 + fichas OCDE + documentos institucionais; cadastro de fontes e regras **nas tabelas `fontes_institucionais`/`regras_institucionais`** (motor do S01); motor de verificação do S02 lendo regras por vigência (`inicio/fim_vigencia`) |
| N | **S01:** carga dos documentos oficiais; classificação de cada regra por natureza com fonte e versão; conflitos registrados em `regras_conflitos` para decisão humana. **S02:** casos de teste S02-T01 a T06 executados |

**Aceite:** endpoint `/skill` responde via RAG citando o documento de origem; perfil
institucional versionado com ≥ 1 fonte oficial carregada; S02 distingue erro, alerta e
recomendação; conflito de regras não é resolvido silenciosamente (S01-T03).

#### I3 — Formação do portfólio: S03 + S04 + S05 (4–6 semanas)

| Frente | Entregáveis |
| --- | --- |
| T | Classificador objetivo/entrega/atividade/tarefa/responsabilidade com grau de confiança; extração de candidata com vínculo ao trecho de origem (`entregas_candidatas`); catálogo versionado com busca semântica (ChromaDB); designer de metas com separação meta final × progresso esperado (PA1: campos `meta` e `meta_final`); endpoints das 3 skills |
| N | Conjunto anotado de classificação (≥ 50 exemplos reais); casos S03/S04/S05-T01 a T06 executados; primeiras entregas reais da CGOV processadas pelo fluxo S03→S04→S05 |

**Aceite:** competência regimental real vira candidata com rastreabilidade; candidata
aprovada entra no catálogo com **código legível e versão**; meta vaga é rejeitada com
perguntas de refinamento (S05-T03); macro-F1 inicial medida e registrada.

#### I4 — Qualidade do plano: S06 (3–4 semanas) → Checkpoint B2

| Frente | Entregáveis |
| --- | --- |
| T | Auditor de portfólio: duplicidade lexical e semântica, matriz competência × entrega, granularidade, relatório com criticidade e confiança; endpoint `/portfolio/auditar` |
| N | Plano de entregas real (ou sintético realista) da unidade-piloto montado via S03–S05; casos S06-T01 a T06 executados; alertas revisados um a um (aceitar/corrigir/justificar → `decisoes_humanas`) |

**Aceite (B2):** demonstração do fluxo documento institucional → candidatas → catálogo →
metas → auditoria, com RAG respondendo dúvidas no caminho; relatório de auditoria
considerado útil pelos analistas (registro formal).

#### I5 — Viabilidade: S07 + S08 (3–5 semanas)

| Frente | Entregáveis |
| --- | --- |
| T | Motor de capacidade (nominal × útil, descontos — determinístico, exatidão 100%); cenários mínimo/provável/máximo; matriz `alocacoes` entrega × participante; validação de totalização em 100%; alertas de sobrealocação, entrega sem cobertura e concentração. Integração com capacidade B: o agente cita I05–I08 reais da unidade |
| N | Dados de capacidade da unidade-piloto (participantes com pseudônimos — D2 e Seção 11); percentuais de atividades indiretas parametrizados como alertas (PA2); casos S07/S08-T01 a T06 executados |

**Aceite:** cálculos determinísticos com exatidão de 100%; déficit de horas diferenciado de
lacuna de competência (S07-T05); plano individual ≠ 100% detectado.

#### I6 — Estratégia, riscos e agente unificado: S09 + S10 + Agno (4–6 semanas)

| Frente | Entregáveis |
| --- | --- |
| T | Estrutura OKR-D com vínculos N:N (`vinculos_okrd`); auditoria de plausibilidade (direta/indireta/contextual — nunca causalidade afirmada); registro estruturado de riscos com classificador risco/impedimento/dependência/restrição; **agente Agno unificando A + B + C** |
| N | Objetivos e KRs institucionais reais carregados (com `petrvs_id` quando importados do PETRVS); casos S09-T01 a T08 e S10-T01 a T08 executados; bateria de 10 perguntas mistas para o teste de decisão do agente |

**Aceite:** o agente escolhe a capacidade certa nas 10 perguntas mistas; entrega
obrigatória sem KR aceita justificativa operacional (S09-T08); risco sem impacto gera
pergunta, não preenchimento automático. **Iniciar aqui o processo com o TI institucional
(risco RP01).**

#### I7 — Integração institucional e piloto (4–8 semanas, dependente do TI) → Checkpoint B3

| Frente | Entregáveis |
| --- | --- |
| T | Orquestrador do fluxo S01–S10 com persistência de estado; testes INT-T01 a INT-T08; Custom Connector + topic no Copilot Studio (plano B: Streamlit); migração do modelo para Azure OpenAI se Q2 confirmada; **comparação agente × PETRVS** via `petrvs_entrega_id` para as entregas do piloto |
| N | Estudo-piloto com a unidade-piloto percorrendo o fluxo completo; questionário de utilidade e confiança; correção apenas de defeitos críticos e altos; relatório final de métricas (Seção 9) |

**Aceite (B3):** ≥ 2 gestores usam o agente ao vivo pelo M365; caso completo percorre
S01→S10 sem perda de identificadores (RC4); feedback registrado; backlog pós-MVP (S11–S20)
priorizado para a v5.

---

## 7. Estrutura do repositório (revista)

```text
pgd-agente-icmbio/
  src/
    agente/                Núcleo conversacional e agente Agno (I1, I6)
    dados/                 Denodo (run_query) + MySQL:
                           schema.sql (21 tabelas), versoes.py (IDs/versões),
                           sincronizar_ref.py (espelhos ref_*), backup.ps1 (mysqldump)
    rag/                   Indexação e consulta (LlamaIndex + ChromaDB) (I2)
    skills_engine/         Validadores compartilhados e motor das skills (I2–I6)
      validadores/         classificar_elemento, validar_titulo, validar_4q1p,
                           validar_meta, calcular_capacidade, validar_percentuais...
      s01_configurador.py ... s10_riscos.py
    api/                   FastAPI — endpoints e contratos Pydantic
  skills/
    00_skill-*.md          B01–B04 — metodologia original (fonte RAG; não editar sem versão)
    01..04_*.md            Artefatos de análise e especificação
    specs/                 SKILL_S01.md ... SKILL_S10.md (template Seção 8.2)
    exemplos/              Conjuntos anotados (classificação, perguntas, planos de teste)
  data/
    config-institucional/  Documentos oficiais carregados no S01 (verificar sensibilidade)
    vectorstore/           ChromaDB local (ignorado pelo Git)
    backups/               Dumps mysqldump do banco pgd_agente (ignorado pelo Git)
  prototipos/              Exports do Langflow (I2, didático)
  docs/
    gestao/                atas/, decisoes/ (ADR-001..006), riscos.md
    tecnologia/            AT-01_analise-petrvs-esquema-mysql_v1.md,
                           arquitetura.md, contratos-api.md
    testes/                Registros de execução dos casos de teste (QA-xx)
    referencia-pgd-ocde-icmbio.md
  tests/                   Testes automatizados (unitários e integração)
  .env.example | .env | .gitignore | requirements.txt | README.md
  proposta-projeto-v1.md   Registro histórico
  proposta-projeto-v2.md   ANEXO DE CAPACITAÇÃO — glossário + tutoriais T1–T6
  proposta-projeto-v3.md   Registro histórico (substituída por esta v4)
  proposta-projeto-v4.md   Este documento
```

**Mudanças de infraestrutura:** o banco `pgd_agente` vive no serviço MySQL local — não há
mais arquivo `data/pgd_agente.db`. O `.env` guarda as credenciais do MySQL local (host,
porta, usuário, senha) além das chaves já previstas. `.gitignore` acrescenta:
`data/backups/`, `*.dump.sql`, `data/config-institucional/` (até classificação documento a
documento) e mantém tudo da v2.

---

## 8. Ciclo de vida de uma skill (mantido da v3)

Os sete passos, a regra de fluxo (nenhuma skill entra no passo 5 sem os passos 1–4; nenhuma
é declarada pronta sem o passo 7 registrado), o template `SKILL_Sxx.md` (v3 §8.2) e os
critérios globais de pronto do artefato `02` §8 permanecem integralmente válidos.

| Passo | Atividade | Responsável | Artefato |
| --- | --- | --- | --- |
| 1 | Especificar (`SKILL_Sxx.md`) | Analista (ED) | AN: `skills/specs/` |
| 2 | Definir regras com natureza e fonte | Analista (ED) | AN: seção Regras da spec |
| 3 | Anotar exemplos reais rotulados | Analista (ED) | AN: `skills/exemplos/` |
| 4 | Escrever casos de teste Dado/Quando/Então | Analista (QA) | QA: `docs/testes/` |
| 5 | Implementar (validadores + prompt + contrato + endpoint) | Coordenador (BE/IA) | AT: `src/skills_engine/` |
| 6 | Integrar e automatizar testes | Coordenador | AT: `tests/` |
| 7 | Validar aceite | Ambos | QA: registro; ata de aceite |

### 8.3. Contrato técnico de saída (atualizado: rastreio persiste no banco)

O contrato JSON da v3 §8.3 permanece; a novidade da v4 é que ele **deixa de ser apenas
formato de resposta e passa a ser persistido**: cada execução grava uma linha em
`execucoes_skill` (com `id` = `rastreio_id`, entrada e saída integrais em JSON), e os campos
`regras_aplicadas` citam os **códigos legíveis** (`R-014`) das regras versionadas.

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

## 9. Plano de qualidade e avaliação (mantido da v3)

Tipos de teste (positivo, negativo, ambiguidade, limite, integração, regressão,
explicabilidade, segurança), métricas essenciais do MVP, rubrica de 10 dimensões × 0–4 e
estudo-piloto simplificado em 2 condições permanecem como na v3 §9. Métricas-chave:

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

O registro de execução (v3 §9.5) passa a ter suporte direto do banco: `execucoes_skill`
guarda versão da skill, modelo, entrada, saída integral e tempo — base da reprodutibilidade
exigida pelo `03` §17.5. Metas acadêmicas completas seguem condicionadas a Q6.

---

## 10. Matriz de riscos consolidada *(revisada)*

| # | Risco | Prob. | Impacto | Mitigação | Dono |
| --- | --- | --- | --- | --- | --- |
| RP01 | Provisionamento Azure/Connector atrasar e travar I7 | Alta | Alto | Processo com TI iniciado em I6; Streamlit como plano B | Coordenador |
| RP02 | Agente alucinar números ou regras | Média | Alto | Indicadores só via tool calling; toda regra com fonte; confiança explícita; validação humana em baixa confiança | Coordenador |
| RP03 | Confusão entre norma e recomendação (PA3) | Alta | Alto | Natureza da regra é campo obrigatório (`ENUM` no banco); teste S01-T04 | Analistas |
| RP04 | Meta confundir esforço com resultado; meta × progresso (PA1) | Alta | Alto | Campos distintos `meta`/`meta_final` no esquema + validador; teste S05-T04 | Analistas |
| RP05 | Cálculos de capacidade com falsa precisão | Alta | Médio | Faixas e cenários; incerteza sempre visível | Coordenador |
| RP06 | Dados individuais de disponibilidade expostos | Média | Alto | Espelho mínimo D2 (sem CPF/e-mail); pseudônimos; agregação; checklist da Seção 11 | Coordenador |
| RP07 | OKR-D afirmar causalidade indevida | Alta | Alto | Justificativa obrigatória (`NOT NULL` no banco); linguagem de contribuição plausível | Analistas |
| RP08 | Excesso de alertas tornar o agente irritante | Média | Alto | Gravidade + confiança + limiar configurável; revisão com usuários no I4 | Analistas |
| RP09 | Escopo crescer ("já que estamos fazendo…") | Alta | Alto | S11–S20 fora do MVP; inclusão exige v5 | Coordenador |
| RP10 | Dependência de pessoa única | Alta | Alto | ADRs, specs em Markdown, tutoriais, pareamento; ciclo de vida com papéis explícitos | Todos |
| RP11 | Equipe não absorver o papel de ED/QA | Média | Alto | RC6 mede autonomia; passos 1–4 do ciclo são não técnicos | Coordenador |
| RP12 | Credencial vazar em repositório | Baixa | Alto | `.gitignore` desde o dia zero (inclui `.env` com credenciais MySQL); verificação pré-push | Coordenador |
| RP13 | Integrações perderem histórico/IDs | Média | Alto | **Mitigação reforçada na v4:** triggers de imutabilidade no banco (AT-01 §6.3) — nem script com bug sobrescreve histórico; teste RC4/INT-T01 | Coordenador |
| RP14 | Custo de API sair do controle | Baixa | Baixo | Limite mensal no provedor (Tutorial T3) | Coordenador |
| RP15 *(novo)* | Indisponibilidade ou corrupção do serviço MySQL local travar o trabalho | Baixa | Médio | `mysqldump` diário para pasta com backup (padrão `backup_privado.ps1`); script de reinstalação + `schema.sql` versionado permitem reconstruir o ambiente em horas | Coordenador |

---

## 11. Governança de dados e uso responsável de IA *(revisada)*

Herda integralmente a Seção 10.2–10.3 da v2 (transparência, **somente leitura no PETRVS**,
verificação pré-push, política institucional de IA) e a Seção 11 da v3, com as seguintes
atualizações:

1. **Dados de pessoas** (S07/S08): dados reais só na máquina local e no **MySQL local fora
   do Git**; relatórios e exemplos versionados usam dados anonimizados ou sintéticos; motivo
   de indisponibilidade nunca é detalhado (basta "indisponível X horas").
2. **Espelho `ref_usuarios` mínimo (D2):** sincroniza apenas os servidores da
   unidade-piloto, com campos id, nome, matrícula, participa_pgd e unidade — **sem CPF,
   e-mail ou situação funcional**. Relatórios usam pseudônimos (`participantes.rotulo`).
3. **Documentos institucionais do S01** ficam em `data/config-institucional/` (fora do Git)
   até serem classificados como publicáveis, um a um.
4. **O agente não decide.** Nenhuma skill aprova plano, avalia pessoa ou resolve conflito
   normativo — saídas são sugestões com fonte; decisões humanas ficam em `decisoes_humanas`,
   separadas das sugestões.
5. **Rastreabilidade como requisito:** se um gestor questionar uma resposta, reconstitui-se
   fontes, regras (por código e versão), versão da skill, versão do modelo e quem validou —
   diretamente das tabelas `execucoes_skill` e `decisoes_humanas`.
6. **Backups protegidos:** os dumps em `data/backups/` contêm os mesmos dados sensíveis do
   banco — mesma política de proteção (fora do Git, backup criptografado quando sair da
   máquina).

---

## 12. Checklist de execução da v4

- [ ] **I0** — repo estruturado; MySQL 8 instalado como serviço; `schema.sql` (21 tabelas)
  aplicado; **teste de imutabilidade aprovado** (UPDATE em `*_versoes` rejeitado);
  `ref_unidades` + `ref_usuarios` (piloto) sincronizadas; primeiro `mysqldump` gerado;
  ADRs 001–006; fontes institucionais levantadas (Q5); unidade-piloto definida (Q8)
- [ ] **I1 / B1** — 2 endpoints demonstrados; I02 = CSV oficial; 20 perguntas anotadas
- [ ] **I2** — RAG citando fontes; perfil institucional versionado (S01); S02 com casos
  T01–T06 aprovados
- [ ] **I3** — fluxo S03→S04→S05 com entregas reais; macro-F1 medida; conjunto anotado ≥ 50
  exemplos
- [ ] **I4 / B2** — auditoria de portfólio demonstrada ponta a ponta; utilidade registrada
- [ ] **I5** — cálculos determinísticos 100%; matriz de cobertura funcionando; dados
  pessoais protegidos (pseudônimos)
- [ ] **I6** — agente Agno decide entre A/B/C em 10 perguntas mistas; **processo TI iniciado**
- [ ] **I7 / B3** — INT-T01 a INT-T08 aprovados; Copilot Studio ativo; piloto executado;
  ≥ 2 gestores ao vivo; comparação agente × PETRVS registrada
- [ ] Métricas da Seção 9 medidas e registradas
- [ ] Backlog pós-MVP (S11–S20) priorizado → insumo da proposta v5

---

## 13. Registro de mudanças v3 → v4

| Seção | Mudança | Origem |
| --- | --- | --- |
| Cabeçalho e Sumário | v4 substitui v3; AT-01 vira anexo técnico vinculante; decisões D1–D4 registradas | Aprovação de 26.07.2026 |
| §2.4 | Q8 (unidade-piloto) adicionada; D1–D4 encerradas | AT-01 §8; D2 |
| §3.2 | SQLite → **MySQL 8 local**; esquema de 21 tabelas (AT-01 §5); triggers de imutabilidade; campos de comparação com o PETRVS | D1, D4; ADR-006 |
| §3.3 | Linha de persistência revisada (Reversível → Estruturante); linha nova de identidade dupla | D1, D3 |
| §4 (EAP 2.5) | Persistência em MySQL (schema.sql, versoes.py, sincronizar_ref.py, backup) | D1, D4 |
| §6.2 (I0) | Entregáveis e aceite reescritos: instalação MySQL, 21 tabelas, teste de imutabilidade, sincronização `ref_*`, backup; duração 2–4 semanas | AT-01 §8 |
| §7 | `data/pgd_agente.db` removido; `data/backups/`; `docs/tecnologia/AT-01`; `.env` com credenciais MySQL; v3 → registro histórico | D1, D4 |
| §8.3 | Contrato de saída persiste em `execucoes_skill`; `regras_aplicadas` usa códigos legíveis | D3 |
| §10 | RP13 com mitigação reforçada (triggers); **RP15 novo** (indisponibilidade do MySQL local) | AT-01 §8 |
| §11 | Itens 2 (espelho mínimo D2) e 6 (backups protegidos) adicionados | D2, D4 |
| §12 | Itens de I0 atualizados; referências a v5 | — |
| Demais seções (1, 2.1–2.3, 3.1, 5, 6.1, I1–I7 exceto notas, 8.1–8.2, 9) | Mantidas da v3 sem alteração de mérito | — |

---

*Documento elaborado como revisão dirigida da v3, motivada pela aprovação do AT-01
(análise da estrutura de dados do PETRVS e esquema MySQL do modelo comum) com as decisões
D1–D4, registradas no ADR-006. Alterações de escopo ou de stack geram a versão 5, com
registro do motivo em `docs/gestao/decisoes/`. A v2 permanece como Anexo de Capacitação
(glossário e Tutoriais T1–T6); os artefatos `02_matriz`, `03_especificacao` e `04_backlog`
permanecem como especificações vinculadas; o `AT-01` é o anexo técnico vinculante do modelo
de dados.*
