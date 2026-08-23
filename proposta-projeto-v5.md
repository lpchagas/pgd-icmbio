# Proposta de Projeto — `pgd-agente-icmbio`

**Versão:** 5.0 | **Data:** 18.08.2026
**Substitui:** `proposta-projeto-v4.md` como documento de planejamento e gestão.
A v2 **permanece válida como Anexo de Capacitação** — seu Glossário (Seção 4) e seus
Tutoriais T1–T6 (Seção 9) continuam sendo o material de referência da equipe. As v3 e v4
passam a registro histórico.
**Anexos vinculantes:** `docs/tecnologia/AT-01_analise-petrvs-esquema-mysql_v1.md`
(anexo técnico do modelo de dados; ADR-006) e
`skills/05_plano-skills-execucao-avaliacao_v1.md` (anexo de especificação do bloco
S21–S24, incorporado por esta v5).
**Papel assumido nesta proposta:** consultor independente sênior em engenharia de software e
gestão de projetos.
**Público-alvo:** equipe de projeto formada por analistas de negócio da CGOV/ICMBio.

---

## Sumário executivo

A v4 foi uma revisão dirigida de stack: adotou o MySQL 8 local com esquema de 21 tabelas
(AT-01; decisões D1–D4, ADR-006), mantendo escopo, skills, resultados-chave e roadmap da
v3. Esta v5 é uma **revisão de escopo, feita pelo rito que a própria v4 exigia**: o risco
RP09 estabelecia que "inclusão de skills fora do MVP exige a versão 5 desta proposta" —
e é exatamente isso que este documento formaliza.

**O que muda e por quê.** O catálogo S01–S20 foi desenhado com foco na **elaboração** dos
planos do PGD. A fase de **execução e avaliação** aparecia apenas de forma genérica em três
skills de baixa prioridade (S13, S16, S17), nenhuma delas distinguindo os dois instrumentos
do PGD — Plano de Entregas da unidade × Plano de Trabalho do participante — que possuem
atores, prazos, critérios, escalas e consequências jurídicas distintos. O documento
`skills/05` (18.08.2026) analisou integralmente a base normativa (IN nº 24/2023 via
cadernos Enap, documentos CGGE/ICMBio, Guia SEGES, Regimento Interno, Acórdão TCU
2082/2022), extraiu **36 regras normativas (RN-01 a RN-36)** e especificou um bloco novo de
quatro skills executáveis:

| Código | Skill | Ator principal |
| --- | --- | --- |
| **S21** | Registro de Execução do Plano de Entregas da Unidade | Chefia da unidade de execução |
| **S22** | Avaliação do Plano de Entregas da Unidade | Chefia hierarquicamente superior |
| **S23** | Registro de Execução do Plano de Trabalho do Participante | Participante |
| **S24** | Avaliação do Plano de Trabalho do Participante | Chefia da unidade de execução |

**As cinco decisões desta v5 (a registrar como ADR-007):**

1. **O bloco S21–S24 entra no catálogo oficial do projeto** como **Fase 2 — Execução e
   Avaliação**, com plano próprio de 8 etapas (E0–E7, 18–24 semanas) e Checkpoint **B4**.
   O MVP (S01–S10, incrementos I0–I7) **não muda**: a Fase 2 só inicia após o I2 (E0
   depende de S01/S02 operacionais).
2. **S13, S16 e S17 são reposicionadas** (Seção 1.4): S13 reduzida a check-in informal;
   S16 subordinada a S22 como avaliadora de entrega individual; S17 promovida a P2 com
   versão mínima antecipada (etapa E2). S14 passa a ser acionada por S21/S23.
3. **O modelo comum ganha a migração `002`**: 12 tabelas novas (33 no total) e 8 triggers
   de imutabilidade adicionais (14 no total), criando as entidades ausentes — em especial
   `planos_trabalho`, maior lacuna estrutural do esquema `001`.
4. **As regras dos protótipos CGOV sem lastro normativo** (faixa `≥ 80 % = Adequado`;
   "sem intercorrências" para Alto Desempenho) **serão declaradas como regra institucional
   no S01, com fonte e vigência** — nunca aplicadas como se fossem norma (achados A-01 e
   A-02 do `05` §4.4).
5. **RP16 entra formalmente na matriz de riscos** (perda da rota de rede ao Denodo,
   identificada em 26.07.2026 e ainda aberta), junto com os riscos específicos do bloco
   RP17–RP24. RP16 é hoje o único item que bloqueia o aceite do I0.

Tudo o mais permanece: as três capacidades do agente, as regras de ouro, os papéis, o
ciclo de vida de skill, os RC1–RC6 (acrescidos de RC7–RC9 para a Fase 2), o roadmap I0–I7
e as decisões D1–D4/ADR-001..006.

---

## 1. Análise da pasta `skills/` — o que existe e o que muda

### 1.1. Inventário e papel de cada arquivo *(atualizado)*

| Arquivo | Natureza | Papel no projeto a partir da v5 |
| --- | --- | --- |
| `00_skill-analise-entrega-v1.md` | Metodologia (B01) | Fonte de regras do classificador/validador de entregas; base de conhecimento RAG |
| `00_skill-okrd-v1.md` | Metodologia (B02) | Fonte conceitual da cadeia OKR-D; base do S09 |
| `00_skill-plano-entregas-v1.md` | Metodologia (B03) | Orquestrador conceitual do plano de entregas; base de S03–S06 |
| `00_skill-plano-trabalho-v1.md` | Metodologia (B04) | Regras de alocação de esforço; base de S07–S08 |
| `01_analise-skills_v1.md` | Análise crítica | Diagnóstico de fragilidades; origem da arquitetura em 4 camadas e das 20 skills |
| `02_matriz-desenvolvimento-skills_v2.md` | Matriz de desenvolvimento | **Especificação mestra do catálogo original**: 20 skills (S01–S20), prioridades P0–P3, dependências, testes de aceitação, critérios globais de pronto |
| `03_especificacao-funcional-skills_v2.md` | Especificação funcional | **Detalhamento do MVP (S01–S10)**: perfis, histórias de usuário, modelo de dados, casos de teste, requisitos não funcionais, plano de avaliação |
| `04_backlog-mvp-skills_v2.md` | Backlog executável | **Plano de execução do MVP**: 7 sprints, épicos, estimativas, riscos, definição de pronto |
| `05_plano-skills-execucao-avaliacao_v1.md` *(novo)* | Especificação + plano (Fase 2) | **Anexo vinculante desta v5**: base normativa RN-01..RN-36, fichas funcionais S21–S24 (32 casos de teste), migração `002`, mapeamento PETRVS camadas 3–4, plano E0–E7, riscos RP17–RP24 |
| `docs/tecnologia/AT-01_*.md` | Análise técnica | **Anexo vinculante**: análise do PETRVS e esquema MySQL do modelo comum (DDL de referência) |

### 1.2. Conclusões da análise incorporadas (v3/v4, mantidas)

**(a)** As skills deixaram de ser documentos e viraram software com regras de negócio —
validadores compartilhados, esquema canônico, objetos com ID persistente; o RAG é uma das
camadas, não a estratégia inteira. **(b)** O MVP tem escopo fechado: 10 skills (S01–S10).
**(c)** O caminho crítico é sequencial e começa pelo S01 e pelo modelo comum de dados.
**(d)** A qualidade é mensurável — testes Dado/Quando/Então, INT-T01 a INT-T08, metas
quantitativas. **(e)** O backlog pressupõe equipe que não existe; a sequência funcional é
preservada e as estimativas recalibradas.

### 1.3. Conclusões novas incorporadas do `05` *(novo na v5)*

**(f)** A IN nº 24/2023 estabelece **quatro procedimentos diferentes** para execução e
avaliação, com quatro prazos, dois avaliadores e uma política de consequências que só
existe do lado do Plano de Trabalho (recurso, reavaliação, ações de desenvolvimento). Um
componente genérico de "avaliação" não implementa isso sem violar a regra de ouro 4.
**(g)** Falta a entidade `PlanoDeTrabalho` no modelo comum — `alocacoes` é matriz de
esforço, não um plano versionável com estado, prazo, TCR e critérios; sem ela, S23 não tem
o que registrar e S24 não tem o que avaliar. **(h)** As skills Cowork `cgov-registro-execucao`
e `cgov-avaliar-entrega`, em uso informal na CGOV, são o melhor conjunto de exemplos
anotados disponível — e ao mesmo tempo contêm regras sem lastro normativo (achados
A-01 a A-05 do `05` §4.4) que exigem tratamento explícito antes de migrar para o agente.
**(i)** A base normativa contém conflitos e lacunas reais (C-01 a C-03 do `05` §3.5) —
inclusive datas do ciclo 2026 internamente inconsistentes — que **não podem ser resolvidos
silenciosamente** (regra de ouro 5): viram registros em `regras_conflitos` e questões à
CGGE.

### 1.4. Reposicionamento de skills do catálogo original *(novo na v5)*

Para não duplicar regras (princípio herdado do `01` §1), o bloco S21–S24 absorve parte do
escopo previsto para S13 e S16:

| Skill | Situação a partir desta v5 |
| --- | --- |
| **S13** — Check-in de Execução | **Mantida, com escopo reduzido** a *check-in intermediário informal* (acompanhamento semanal, quadro de status), sem valor normativo. O registro formal migra para S21 (PE) e S23 (PT) |
| **S16** — Avaliador de Entregas | **Mantida, subordinada a S22.** Passa a ser o *avaliador de entrega individual*, chamado por S22 como sub-rotina: S22 avalia o **plano**, agregando as avaliações de entrega produzidas por S16 |
| **S17** — Organizador de Evidências | **Promovida a P2** e antecipada: sem repositório de evidências, RN-13(d) e RN-29(1) não são verificáveis. Uma versão mínima (tabela `evidencias` + vinculação) entra na etapa E2 |
| **S14** — Replanejamento | **Sem alteração de escopo**, mas passa a ser acionada por S21 (RN-05/RN-06) e S23 (RN-23) |

### 1.5. Pontos de atenção herdados (não resolver silenciosamente)

Os PA1–PA4 da v3/v4 permanecem com o mesmo tratamento. Acrescentam-se os do bloco novo:

| # | Ponto | Onde será tratado |
| --- | --- | --- |
| PA1 | Ambiguidade meta final × progresso esperado × marco intermediário | S05 — campos distintos (`meta` vs `meta_final`); **na Fase 2, RN-08**: progresso esperado (planejamento) jamais é sobrescrito pelo realizado (S21) |
| PA2 | Percentuais de referência de atividades indiretas são alertas, não proibições | S07/S08 — parâmetro configurável (I5) |
| PA3 | Estrutura "objeto + particípio" é preferência, não norma | S01/S02 — campo `natureza` obrigatório da regra (I2) |
| PA4 | Regras institucionais específicas do ICMBio não estão nas 4 skills | S01 — cadastro de fontes oficiais é pré-requisito do MVP (I2) |
| PA5 *(novo)* | Faixa percentual da CGOV (`≥ 80 % = Adequado`) e regra "sem intercorrências" não constam da IN 24/2023 (A-01/A-02) | E0 — declaradas como **regra institucional** com fonte "prática CGOV" e vigência; S22 rotula como convenção local (S22-T07); fatores externos nunca rebaixam conceito automaticamente (S22-T04) |
| PA6 *(novo)* | Progresso apurado por contagem de etapas confunde esforço com meta (A-03) | S21 — progresso realizado apurado **contra a meta pactuada**; contagem de etapas vira evidência auxiliar (S21-T02) |
| PA7 *(novo)* | Mesma escala de 5 conceitos com efeitos jurídicos diferentes no PE e no PT (C-02) | Modelo de dados separa as avaliações (`avaliacoes.objeto_tipo`); recurso só existe para PT; testes de regressão específicos (RP19) |
| PA8 *(novo)* | Datas dos quadrimestres 2026 internamente inconsistentes na página do ciclo (C-01) | E0 — motor de prazos recebe calendário por configuração; implementação bloqueada até confirmação da CGGE (Q9; RP20) |

---

## 2. Objetivos, resultados esperados e escopo

### 2.1. Objetivo geral *(ampliado)*

Disponibilizar aos gestores do ICMBio um agente de IA, acessível via Copilot Studio (M365),
que **(a)** oriente a elaboração de Planos de Entregas e Planos de Trabalho executando as
skills S01–S10 com regras rastreáveis, **(b)** responda perguntas metodológicas citando a
fonte, **(c)** consulte os 12 indicadores OCDE/PGD em tempo real via Denodo e — a partir da
Fase 2 — **(d)** apoie o registro de execução e a avaliação dos dois instrumentos do PGD
(S21–S24), aplicando os prazos, critérios e ritos da IN nº 24/2023 com cálculo
determinístico e decisão sempre humana.

### 2.2. Resultados-chave

RC1–RC6 mantidos da v3/v4 (medidos nos checkpoints B1–B3). Novos, vinculados ao
Checkpoint B4 da Fase 2:

| RC | Resultado-chave | Como será medido |
| --- | --- | --- |
| RC1 | Agente responde perguntas metodológicas citando a fonte | 20 perguntas reais; ≥ 80% corretas com citação |
| RC2 | Agente consulta os 12 indicadores por unidade e período | Resultado idêntico ao CSV oficial do `pgd-ocde-icmbio` |
| RC3 | As 10 skills do MVP executam seus testes de aceitação | Casos de teste do `03` aprovados; INT-T01 a INT-T08 aprovados |
| RC4 | Um caso completo percorre S01→S10 sem perda de identificadores | Teste ponta a ponta com rastreabilidade de fontes |
| RC5 | Gestor acessa o agente no M365, sem novo login | Demonstração formal (Checkpoint B3) com ≥ 2 gestores |
| RC6 | Equipe de analistas opera o ciclo de vida de skill sem apoio externo | Cada analista conduz os passos 1–4 do ciclo (Seção 8) de forma autônoma |
| RC7 *(novo)* | As 4 skills da Fase 2 executam seus testes de aceitação | 32 casos (S21-T01..07, S22-T01..08, S23-T01..07, S24-T01..10) aprovados; motor de prazos e de competência com 100% de exatidão |
| RC8 *(novo)* | Um ciclo completo percorre S21→S22→S23→S24, incluindo recurso e reavaliação, sem perda de identificadores | Teste ponta a ponta (INT-E01..E08); reavaliação preserva a avaliação original como versão |
| RC9 *(novo)* | Conceito sugerido pelo agente é confrontado com o conceito real do PETRVS | Conciliação da unidade-piloto (E6); acurácia medida e registrada — ou contingência sintética documentada, se RP16 persistir |

### 2.3. Escopo *(revisado)*

**Dentro — Fase 1 (MVP, inalterada):** 10 skills (S01–S10); modularização de B01–B04; RAG
sobre metodologia + perfil institucional; consulta aos 12 indicadores; API FastAPI; agente
unificado; publicação no Copilot Studio; capacitação da equipe; avaliação piloto adaptada.

**Dentro — Fase 2 (nova, aprovada por esta v5):** bloco S21–S24 (execução e avaliação dos
dois instrumentos do PGD); carga das 36 regras normativas no S01; migração `002` do modelo
comum; versão mínima do S17 (evidências); motor determinístico de prazos e de competência;
rito de notificação, recurso, reavaliação e ações de desenvolvimento; conciliação com as
camadas 3–4 do PETRVS; piloto CGOV/COCAGE em ciclo real (Checkpoint B4).

**Fora (adiado deliberadamente):** as demais skills do catálogo — S11, S12, S14, S15, S18,
S19, S20 e as reposicionadas S13/S16 em seus novos escopos (implementadas apenas na medida
mínima exigida pela Fase 2, conforme Seção 1.4); **escrita de dados no PETRVS** (o MySQL
local é banco próprio do agente — o PETRVS permanece somente leitura via Denodo, ADR-002);
decisão automatizada de qualquer natureza — **em especial, o agente jamais emite conceito
de avaliação** (invariante I2, Seção 3.4); dados pessoais identificáveis; app móvel; modelo
de IA próprio; assinatura eletrônica. Novas inclusões exigem a versão 6 desta proposta.

**Observação sobre S11/S12 (pactuação):** o fluxo normativo completo pressupõe planos
pactuados. A Fase 2 não implementa a pactuação: no caminho curto (Seção 6.4), metas, CHD e
critérios são informados manualmente; o estado `pactuado` das entidades novas registra o
fato, não o rito.

### 2.4. Premissas e questões em aberto *(atualizado)*

Mantêm-se as premissas da v2 (Seção 3). Situação das questões:

| # | Questão em aberto | Decide o quê | Situação / quando responder |
| --- | --- | --- | --- |
| Q5 | Quais documentos oficiais do ICMBio alimentarão o S01? | Conteúdo do perfil institucional; viabilidade do S02 | **Aberta** — antes do Incremento I2 (pendência da Trilha N do I0) |
| Q6 | O projeto terá dimensão acadêmica formal? | Profundidade do plano de avaliação (Seção 9); na Fase 2, o desenho de RC9 | Antes do Incremento I6 |
| Q7 | Haverá reforço de equipe técnica? | Recalibragem dos prazos | Revisão a cada checkpoint |
| Q8 | Qual é a unidade-piloto? | Escopo do espelho `ref_usuarios` (D2) | **Respondida em 26.07.2026: CGOV e COCAGE** |
| Q9 *(nova)* | Datas exatas dos quadrimestres do PE em 2026 — a página do ciclo traz faixas internamente inconsistentes (C-01) | Motor de prazos de S21/S22 | CGGE; bloqueia E0/E1 (RP20). *(= Q1 do `05` §12)* |
| Q10 *(nova)* | A faixa `≥ 80 % = Adequado` da CGOV vira regra institucional do ICMBio, é revista ou descartada? (A-01) | Sugestão de conceito em S22/S24 | CGGE/CGOV; bloqueia E0 e E4. *(= Q2 do `05`)* |
| Q11 *(nova)* | Política interna de medidas corretivas para conceitos 4 e 5 no PE (RN-15) | Saídas de S22 | CGGE/Direção; bloqueia E4. *(= Q3 do `05`)* |
| Q12 *(nova)* | Exercícios do curso de Avaliação digitalizados sem camada de texto: existe versão pesquisável ou OCR? | Conjuntos anotados de E1 | Solicitante. *(= Q4 do `05`)* |
| Q13 *(nova)* | Chefias dispensadas de controle de frequência não têm PT: como S24 as trata e como isso afeta RN-04? | S23/S24 e regra de conclusão do PE | CGGE; bloqueia E3. *(= Q5 do `05`)* |
| Q14 *(nova)* | Contribuições a outras unidades e times volantes entram no registro de qual unidade? | S23 e matriz de S15 | CGGE; bloqueia E3. *(= Q6 do `05`)* |
| Q15 *(nova)* | O parecer de avaliação é instruído em processo SEI? Qual tipo de documento e fluxo? | Exportação de S22/S24 | CGGE/SEI; bloqueia E4. *(= Q7 do `05`)* |
| Q16 *(nova)* | O acesso ao Denodo será restabelecido a tempo de E6 (RP16)? A contingência sintética é aceitável para RC9? | E6 e validação acadêmica | TI/Dataprev. *(= Q8 do `05`)* |

---

## 3. Visão do produto — as três capacidades do agente

As três capacidades definidas na v3 permanecem: **(A) Conhecimento** — "o bibliotecário"
(RAG sobre B01–B04, fichas OCDE e perfil institucional); **(B) Ação sobre dados** — "o
consultor de plantão" (`consultar_indicador()` via Denodo); **(C) Skills executáveis** — "o
analista metodológico". A capacidade C, antes restrita a S01–S10, passa a compreender
também o bloco S21–S24 na Fase 2. O agente unificado (I6) decide qual acionar e pode
combiná-las.

### 3.1. Arquitetura em camadas (mantida; Camada 2 ampliada na Fase 2)

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
                │ LlamaIndex +  │  │ consultar_     │  │ S01–S10 (Fase 1) +  │
                │ ChromaDB      │  │ indicador()    │  │ S21–S24 (Fase 2) +  │
                │               │  │ (JDBC→Denodo)  │  │ validadores comuns  │
                └───────┬───────┘  └────────────────┘  └──────┬──────────────┘
                        │                                     │
                ┌───────▼─────────────────────────────────────▼──────┐
                │ CAMADA 1 — Conhecimento institucional              │
                │ B01–B04 | fichas OCDE | perfil institucional (S01) │
                │ catálogo de entregas (S04) | base normativa da     │
                │ execução/avaliação (RN-01..36, Fase 2)             │
                ├────────────────────────────────────────────────────┤
                │ CAMADA 4 — Governança e dados  ►  MySQL 8 local    │
                │ modelo comum (21 → 33 tabelas) | UUID + códigos |  │
                │ versões imutáveis (triggers 6 → 14) | execuções |  │
                │ decisões humanas | perguntas pendentes |           │
                │ espelhos ref_* (Denodo→local, camadas 1–4 PETRVS)  │
                └────────────────────────────────────────────────────┘
```

### 3.2. Modelo comum de dados *(ampliado — migração 002)*

O esquema `001` (21 tabelas, cinco grupos, AT-01 §5) permanece como está, com as regras de
ouro integralmente em vigor:

1. Toda entrega possui identificador persistente; nenhuma skill recria um objeto que pode
   referenciar.
2. Alterações geram nova versão — a anterior nunca é sobrescrita.
3. Toda saída automática registra origem, regra aplicada e grau de confiança.
4. Decisões humanas são registradas separadamente das sugestões do agente.
5. Dados ausentes não são preenchidos silenciosamente — viram perguntas pendentes.

A Fase 2 aplica a migração **`002_execucao_avaliacao.sql`** (`05` §7): **12 tabelas novas**
e **8 triggers adicionais**, seguindo integralmente as convenções do AT-01 (PK `CHAR(36)`
UUID, soft-delete, `created/updated_at`, `ENUM` para status, `JSON` nativo, `DECIMAL(5,2)`
para métricas, nenhuma FK física para o PETRVS). Três grupos novos:

| Grupo | Tabelas | Implementa |
| --- | --- | --- |
| 8 — Plano de trabalho | `planos_trabalho` (+`_versoes` imutável) | A entidade ausente no esquema `001`: plano individual versionável com estado, CHD, contribuições, TCR; código `PT-2026-08-0001` |
| 9 — Registro de execução | `registros_execucao_entrega` (+`_versoes`), `registros_execucao_trabalho` (+`_versoes`), `ocorrencias`, `evidencias` | S21/S23; classificação intercorrência × evento planejado × ajuste de CH × fato externo; S17-mínimo |
| 10 — Avaliação | `avaliacoes` (+`_versoes` imutável), `recursos_avaliacao`, `acoes_desenvolvimento` | S22/S24; escala única de 5 conceitos com `objeto_tipo` separando PE e PT (C-02); rito de recurso e reavaliação como **nova versão** |

Toda escrita nessas tabelas passa por funções novas em `src/dados/versoes.py`
(`criar_plano_trabalho`, `registrar_execucao_entrega`, `registrar_ocorrencia`,
`criar_avaliacao`, `registrar_recurso` etc.) — **nenhum INSERT/UPDATE manual**. A
aderência do bloco às cinco regras de ouro está demonstrada tabela a tabela no `05` §7.4.

### 3.3. Decisões de stack — o que muda em relação à v4

As tabelas de stack da v2 (Seção 6) e da v4 (§3.3) permanecem válidas. Acréscimos:

| Camada | Recomendação | Justificativa | Tipo |
| --- | --- | --- | --- |
| Motor de prazos (Fase 2) | **Python puro, determinístico** (`src/skills_engine/prazos.py`); calendário do ciclo **por configuração, não por constante** | Prazos regulamentares (10/20/30 dias, dia 10, recurso) exigem exatidão de 100%; as datas do ciclo 2026 estão pendentes de confirmação (Q9/RP20) | Estruturante |
| Motor de competência (Fase 2) | **Determinístico sobre a árvore de `ref_unidades`** (`competencia.py`), com as dispensas RN-10/RN-11 | Competência de avaliação é questão jurídica, não semântica | Estruturante |
| Sugestão de conceito | **Híbrido**: regras determinísticas produzem faixa candidata; LLM redige fundamentação; **humano decide** (`decisoes_humanas`) | Invariante I2; RP18 | Estruturante |
| Contratos da Fase 2 | **Pydantic** em `src/skills_engine/contratos/execucao_avaliacao.py` (4 classes de saída, `05` §5.3) | Mesmo padrão do MVP; vira documentação OpenAPI | Estruturante |

### 3.4. Invariantes de arquitetura do bloco S21–S24 *(novo na v5)*

Quatro invariantes vinculantes, herdados do `05` §5.1:

- **I1 — Um ator por skill.** S21 = chefia da UE; S22 = chefia superior; S23 =
  participante; S24 = chefia da UE. O controle de perfil é pré-condição de execução, não
  validação a posteriori.
- **I2 — O agente nunca atribui conceito.** S22 e S24 produzem **conceito sugerido +
  confiança + fundamentação**. O conceito válido é sempre um registro em
  `decisoes_humanas` (regra de ouro 4). Avaliação sem decisão humana é, por construção,
  `estado = 'rascunho'`.
- **I3 — Determinístico ≠ LLM** (v4 §3.3). Prazos, CHD, progresso × meta, completude dos
  PTs (RN-04), elegibilidade a recurso e competência hierárquica: Python puro, 100% de
  exatidão. Classificação de relatos, aderência qualitativa a critérios e redação de
  fundamentação: LLM com confiança explícita e validação humana.
- **I4 — Dado ausente vira pergunta.** Sem critério de aceite pactuado, sem evidência ou
  sem registro do participante, a avaliação **não é emitida**: gera `perguntas_pendentes`
  (regra de ouro 5).

---

## 4. Estrutura analítica do projeto (EAP) *(ampliada)*

```text
pgd-agente-icmbio (v5)
├── 1. GESTÃO DO PROJETO
│   ├── 1.1 Planejamento e revisões desta proposta
│   ├── 1.2 Ritos, atas e registro de decisões (ADRs)
│   ├── 1.3 Gestão de riscos e de escopo
│   └── 1.4 Checkpoints de demonstração (B1, B2, B3, B4)
├── 2. TRILHA T — PLATAFORMA TECNOLÓGICA
│   ├── 2.1 Ambiente e repositório (Fase 0 da v2; Tutoriais T1–T2)
│   ├── 2.2 Núcleo conversacional: API do modelo + system prompt (T3)
│   ├── 2.3 Acesso a dados: consultar_indicador() via Denodo (T4)
│   ├── 2.4 RAG: Langflow (protótipo) → LlamaIndex + ChromaDB (T5)
│   ├── 2.5 Persistência: modelo comum em MySQL 8 (migrações 001 e 002,
│   │       versoes.py, sincronizar_ref.py, backup mysqldump)
│   ├── 2.6 API própria: FastAPI + contratos das skills (T6)
│   ├── 2.7 Agente unificado: Agno (capacidades A+B+C)
│   ├── 2.8 Integração M365: Custom Connector + Copilot Studio
│   └── 2.9 Motores determinísticos da Fase 2: prazos.py, competencia.py
├── 3. TRILHA N — SKILLS (REGRAS NEGOCIAIS)
│   ├── 3.1 Modularização de B01–B04 em validadores compartilhados
│   ├── 3.2 Bloco Fundação: S01 Configurador, S02 Verificador Normativo
│   ├── 3.3 Bloco Portfólio: S03 Extrator, S04 Catálogo, S05 Metas
│   ├── 3.4 Bloco Qualidade: S06 Auditor de Portfólio
│   ├── 3.5 Bloco Viabilidade: S07 Capacidade, S08 Cobertura
│   ├── 3.6 Bloco Estratégia e Riscos: S09 OKR-D, S10 Riscos
│   ├── 3.7 Bloco Execução (Fase 2): S21 Registro PE, S23 Registro PT
│   ├── 3.8 Bloco Avaliação (Fase 2): S22 Avaliação PE, S24 Avaliação PT
│   │       (+ S16 subordinada; S17-mínimo; rito de recurso)
│   └── 3.9 Base normativa da execução/avaliação: RN-01..36 no S01 (E0)
├── 4. QUALIDADE E AVALIAÇÃO
│   ├── 4.1 Conjuntos anotados (exemplos reais rotulados)
│   ├── 4.2 Testes por skill (positivo/negativo/ambiguidade/integração)
│   ├── 4.3 Testes de integração INT-T01..T08 (MVP) e INT-E01..E08 (Fase 2)
│   ├── 4.4 Estudo-piloto com unidade real (B3) e ciclo real (B4)
│   └── 4.5 Conciliação agente × PETRVS (camadas 3–4; RC9)
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

O `skills/05` integra a série AN como especificação vinculada da Fase 2 — no mesmo
estatuto dos artefatos `02`/`03`/`04` para o MVP. Alterações no esquema (migração `002`)
geram nova versão do AT-01 ou anexo AT próprio e migração registrada em `schema_migracoes`.

### 5.2. Papéis — do backlog ideal à equipe real (mantido; ator novo no piloto B4)

A tabela de papéis da v3/v4 §5.2 permanece integralmente. A Fase 2 acrescenta, **apenas no
piloto (E7/B4)**, atores institucionais que não integram a equipe de projeto: chefias das
unidades-piloto (S21/S24), chefia hierarquicamente superior (S22) e participantes (S23).
Sua participação é objeto do aceite do B4 (≥ 2 chefias e 4 participantes ao vivo).

Implicação mantida: incrementos/etapas de **3 a 6 semanas com dedicação parcial**,
preservando a sequência funcional.

### 5.3. Matriz RACI consolidada *(uma linha nova)*

| Atividade | Coordenador | Analistas CGOV | TI institucional | Gestores |
| --- | --- | --- | --- | --- |
| Aprovar esta proposta e revisões | **A** | C | I | I |
| Especificar e validar skills (Trilha N, passos 1–4 do ciclo) | C | **R** | — | C |
| Implementar plataforma e validadores (Trilha T, passos 5–6) | **R** | C | I | — |
| Executar casos de teste e registrar resultados | A | **R** | — | — |
| Anotar exemplos e compor conjunto de referência | C | **R** | — | C |
| Validar base normativa RN-01..36 e responder Q9–Q15 *(nova)* | C | **R** (com CGGE) | — | I |
| Provisionar Azure / Custom Connector (I7) | A | C | **R** | I |
| Participar dos checkpoints B1–B4 | R | R | I | **C** |

A CGGE é a instância de consulta normativa da Fase 2 (confirmação de datas do ciclo,
faixa percentual, medidas corretivas, rito de recurso — Q9 a Q15).

### 5.4. Ritos (mantidos)

- **Reunião quinzenal (30 min):** status por incremento/etapa, riscos ativados, pendências.
- **Revisão de incremento:** critérios de aceite verificados **antes** de abrir o seguinte.
- **ADR:** uma página por decisão estruturante em `docs/gestao/decisoes/ADR-nnn.md`.
  ADRs 001–005 = decisões v1–v3; ADR-006 = persistência MySQL (v4); **ADR-007 =
  incorporação do bloco S21–S24 e reposicionamento S13/S16/S17 (esta v5)**.
- **Revisão da matriz de riscos:** a cada checkpoint (B1, B2, B3, B4). O registro ativo é
  `docs/gestao/riscos.md`; esta proposta permanece a fonte normativa.

---

## 6. Roadmap integrado — Fase 1 (I0–I7) + Fase 2 (E0–E7)

### 6.1. Princípio de integração (mantido) e encadeamento das fases

Cada incremento/etapa pareia uma entrega de **plataforma (T)** com uma entrega de
**conteúdo negocial (N)**. A Fase 1 (I0–I7, 28–40 semanas) permanece exatamente como na
v4 §6 — inclusive entregáveis e critérios de aceite de I1–I7, que não são repetidos aqui.
A Fase 2 (E0–E7, 18–24 semanas) **não espera o fim da Fase 1**: E0 pode iniciar assim que
S01/S02 estiverem operacionais (I2), e o caminho curto E0–E3 entrega S21/S23 sem depender
de S05/S07/S08 concluídas (Seção 6.4).

**Estado em 18.08.2026:** o projeto está no **I0 — Fundação**, com a Trilha T
substancialmente concluída (MySQL 8.4 instalado; migração `001` aplicada com teste de
imutabilidade aprovado; `versoes.py` operacional; backup diário agendado; ADRs 001–006 e
matriz de riscos materializados). O aceite do I0 está **bloqueado por um único item
técnico** — RP16, perda da rota de rede ao Denodo, que impede `sincronizar_ref.py` de
popular `ref_unidades`/`ref_usuarios` — e pelas pendências da Trilha N (Q5, glossário,
validação formal do modelo pelos analistas).

### 6.2. Fase 1 — incrementos I0–I7 (mantidos da v4)

| Incr. | Nome | Duração | Situação em 18.08.2026 |
| --- | --- | --- | --- |
| I0 | Fundação | 2–4 sem | **Em curso** — Trilha T concluída; aceite bloqueado por RP16 + Trilha N (Q5) |
| I1 | Núcleo conversacional e primeiro indicador → **B1** | 3–4 sem | A iniciar após fechar I0 |
| I2 | Conhecimento institucional: RAG + S01 + S02 | 4–6 sem | — (pré-requisito de E0) |
| I3 | Formação do portfólio: S03 + S04 + S05 | 4–6 sem | — |
| I4 | Qualidade do plano: S06 → **B2** | 3–4 sem | — |
| I5 | Viabilidade: S07 + S08 | 3–5 sem | — (bloqueado por RP16 se persistir: dados de capacidade dependem de D2) |
| I6 | Estratégia, riscos e agente unificado: S09 + S10 + Agno | 4–6 sem | — |
| I7 | Integração institucional e piloto → **B3** | 4–8 sem | — |

Entregáveis e aceites de cada incremento: v4 §6.2, que permanece vinculante para a Fase 1.

### 6.3. Fase 2 — etapas E0–E7 (novas; detalhamento vinculante no `05` §9)

| Etapa | Nome | Duração | Frente T (plataforma) | Frente N (negócio) | Entrega ao final |
| --- | --- | --- | --- | --- | --- |
| **E0** | Fundamento normativo | 2 sem | Carga de D1–D9 em `fontes_institucionais` e das RN-01..36 em `regras_institucionais(+_versoes)`; conflitos C-01..03 em `regras_conflitos`; regra institucional da faixa CGOV (A-01) | Validação das 36 regras pela CGGE; respostas a Q9, Q10, Q11 | Base normativa versionada e aprovada |
| **E1** | Especificação e contratos | 2–3 sem | Contratos Pydantic; **motor de prazos** (100% em bateria de 30 casos de calendário); **motor de competência** (RN-09..11) | Fichas S21–S24 revisadas; conjuntos anotados (≥ 40 relatos de PE, ≥ 40 de PT, ≥ 20 pares registro→conceito dos protótipos `cgov-*`) | Especificação homologada |
| **E2** | Modelo de dados e evidências | 2 sem | Migração `002` (12 tabelas + 8 triggers) + extensão de `versoes.py`; S17-mínimo | Taxonomia de ocorrências (RN-22) alinhada aos motivos do Petrvs; catálogo de tipos de evidência | **33 tabelas**; teste de imutabilidade aprovado nas 4 novas `*_versoes` |
| **E3** | S21 e S23 — registro de execução | 3–4 sem | Skills, validadores determinísticos (progresso × meta, CHD, bloqueios RN-04), classificador de ocorrência, endpoints | 14 casos de teste executados; ciclo real (ou sintético) da CGOV processado | **Registro de execução operacional** |
| **E4** | S22 e S24 — avaliação | 3–4 sem | Motor de conceito (faixa determinística + fundamentação LLM + decisão humana); competência e dispensas; parecer exportável (.md/.docx); minuta de notificação | 18 casos de teste executados; pareceres validados contra os reais da CGOV | **Avaliação operacional** |
| **E5** | Rito de recurso e desenvolvimento | 1–2 sem | Fluxo `notificada → em_recurso → reavaliada → final`; reavaliação como nova versão; `acoes_desenvolvimento` | Rito validado com a CGGE (e PFE, se possível); modelos de notificação | Ciclo completo do PT |
| **E6** | Conciliação Petrvs | 2–3 sem | Espelhamento das camadas 3–4 (normalizando as anomalias do AT-01 §2.4); relatório de divergência; conceito sugerido × real | Validação dos números com a CGGE | Conciliação e métrica de acurácia (RC9) — **dependente de RP16**; contingência sintética se persistir |
| **E7** | Piloto e avaliação | 3–4 sem | Orquestração S21→S24; INT-E01..E08; correções críticas | Piloto CGOV/COCAGE em ciclo real (1 quadrimestre de PE, ≥ 1 mês de PT por participante); questionário | **Checkpoint B4** |

**Total: 18 a 24 semanas.** Esforço estimado (escala do `04_backlog`): 107 pontos T + 91
pontos N (`05` §9.4).

**Dependências entre fases:** E0 ← S01/S02 (I2) · E2 ← migração 001 (I0 ✔) · E3 ←
S04/S05 (I3) e S07/S08 (I5) para a CHD *(dispensável no caminho curto)* · E4 ← S05, S10
(I6), S17-mínimo (E2) · E6 ← Denodo liberado (RP16) · E7 ← agente unificado (I6) para a
experiência conversacional. E6 pode correr em paralelo a E4/E5.

**Aceite do Checkpoint B4** (`05` §11.2): 36 regras carregadas e citáveis; conflitos
C-01..03 decididos por humano; 33 tabelas e 14 triggers com imutabilidade comprovada;
motor de prazos 100% nos 5 prazos normativos; 32 casos de teste registrados; ciclo
completo S21→S22→S23→S24→recurso→reavaliação sem perda de identificadores; conciliação
Petrvs executada (ou contingência documentada); piloto real com ≥ 2 chefias e 4
participantes; nenhum dado sensível de saúde persistido (auditoria sobre dump
anonimizado).

### 6.4. Caminho curto (E0–E3) — opção de valor antecipado

Se a CGOV quiser resultados no ciclo quadrimestral em curso, o bloco pode ser executado no
regime curto: **E0–E3 em 9–11 semanas**, entregando S21 e S23 operacionais com metas e CHD
informadas manualmente, sem depender da conclusão de S05/S07/S08. Custo assumido:
retrabalho estimado de 15–20% em E3 quando essas skills ficarem prontas. A decisão entre
caminho completo e caminho curto será registrada em ata na abertura da Fase 2.

---

## 7. Estrutura do repositório (revista)

```text
pgd-agente-icmbio/
  src/
    agente/                Núcleo conversacional e agente Agno (I1, I6)
    dados/                 Denodo (run_query) + MySQL:
                           schema.sql (21 tabelas, migração 001),
                           migracoes/002_execucao_avaliacao.sql (12 tabelas, Fase 2),
                           versoes.py (IDs/versões — única via de escrita),
                           sincronizar_ref.py (espelhos ref_*, camadas 1–4),
                           backup.ps1 (mysqldump diário)
    rag/                   Indexação e consulta (LlamaIndex + ChromaDB) (I2)
    skills_engine/         Validadores compartilhados e motor das skills
      validadores/         classificar_elemento, validar_titulo, validar_4q1p,
                           validar_meta, calcular_capacidade, validar_percentuais...
      contratos/           Contratos Pydantic (MVP + execucao_avaliacao.py — Fase 2)
      prazos.py            Motor determinístico de prazos regulamentares (E1)
      competencia.py       Motor de competência e dispensas RN-09..11 (E1)
      s01_configurador.py ... s10_riscos.py
      s21_registro_pe.py ... s24_avaliacao_pt.py   (Fase 2, E3–E4)
    api/                   FastAPI — endpoints e contratos Pydantic
  skills/
    00_skill-*.md          B01–B04 — metodologia original (fonte RAG; não editar sem versão)
    01..04_*.md            Artefatos de análise e especificação (MVP)
    05_plano-skills-execucao-avaliacao_v1.md   Anexo vinculante da Fase 2 (esta v5)
    specs/                 SKILL_S01.md ... SKILL_S10.md, SKILL_S21..S24.md
    exemplos/              Conjuntos anotados (classificação, perguntas, relatos, pareceres)
  data/
    config-institucional/  Documentos oficiais carregados no S01 (verificar sensibilidade)
    vectorstore/           ChromaDB local (ignorado pelo Git)
    backups/               Dumps mysqldump do banco pgd_agente (ignorado pelo Git)
  prototipos/              Exports do Langflow (I2, didático)
  docs/
    gestao/                atas/, decisoes/ (ADR-001..007), riscos.md (registro ativo)
    tecnologia/            AT-01, arquitetura.md, contratos-api.md
    testes/                Registros de execução dos casos de teste (QA-xx)
    referencia-pgd-ocde-icmbio.md
  tests/                   Testes automatizados (unitários e integração)
  .env.example | .env | .gitignore | requirements.txt | README.md
  proposta-projeto-v1.md   Registro histórico
  proposta-projeto-v2.md   ANEXO DE CAPACITAÇÃO — glossário + tutoriais T1–T6
  proposta-projeto-v3.md   Registro histórico
  proposta-projeto-v4.md   Registro histórico (substituída por esta v5)
  proposta-projeto-v5.md   Este documento
```

Infraestrutura mantida da v4: banco `pgd_agente` no serviço MySQL local (Windows, porta
3306, sem Docker); credenciais no `.env` (gitignored); backup `mysqldump` diário
(tarefa agendada) com retenção; `.gitignore` cobrindo `data/backups/`, `*.dump.sql` e
`data/config-institucional/`.

---

## 8. Ciclo de vida de uma skill (mantido; aplicado também à Fase 2)

Os sete passos, a regra de fluxo (nenhuma skill entra no passo 5 sem os passos 1–4;
nenhuma é declarada pronta sem o passo 7 registrado), o template `SKILL_Sxx.md` e os
critérios globais de pronto permanecem integralmente válidos — **e a Fase 2 já nasce
obedecendo-os**: a etapa E0 é exatamente o passo 2 (regras com natureza e fonte) executado
antes de qualquer linha de código, e as fichas do `05` §6 cumprem o passo 1.

| Passo | Atividade | Responsável | Artefato |
| --- | --- | --- | --- |
| 1 | Especificar (`SKILL_Sxx.md`) | Analista (ED) | AN: `skills/specs/` |
| 2 | Definir regras com natureza e fonte | Analista (ED) | AN: seção Regras da spec; Fase 2: RN-01..36 → `regras_institucionais` |
| 3 | Anotar exemplos reais rotulados | Analista (ED) | AN: `skills/exemplos/` |
| 4 | Escrever casos de teste Dado/Quando/Então | Analista (QA) | QA: `docs/testes/` |
| 5 | Implementar (validadores + prompt + contrato + endpoint) | Coordenador (BE/IA) | AT: `src/skills_engine/` |
| 6 | Integrar e automatizar testes | Coordenador | AT: `tests/` |
| 7 | Validar aceite | Ambos | QA: registro; ata de aceite |

**Definição de pronto ampliada para S21–S24** (`05` §11.1): além dos critérios globais,
cada skill do bloco exige regras RN-xx carregadas e citadas por código na saída, conjunto
anotado ≥ 40 exemplos, cálculos determinísticos 100%, escrita exclusivamente via
`versoes.py`, teste de segurança de dados pessoais aprovado (RP17/RP24) e — para S22/S24 —
nenhum conceito emitido sem `decisao_humana_id`.

### 8.3. Contrato técnico de saída (mantido; quatro contratos novos)

O contrato JSON da v3 §8.3, persistido em `execucoes_skill` desde a v4, permanece. A Fase 2
acrescenta quatro contratos Pydantic específicos (`05` §5.3): `RegistroExecucaoEntregaOut`
(S21), `AvaliacaoPlanoEntregasOut` (S22), `RegistroExecucaoTrabalhoOut` (S23) e
`AvaliacaoPlanoTrabalhoOut` (S24) — todos derivados de `SaidaSkill`, com
`regras_aplicadas` citando os códigos `R-xxx` derivados de RN-01..RN-36, controle de
tempestividade, fatores externos em bloco separado e `decisao_humana_id` explícito
(`None` ⇒ rascunho).

---

## 9. Plano de qualidade e avaliação *(ampliado)*

Tipos de teste, rubrica e estudo-piloto do MVP permanecem como na v3 §9 / v4 §9.
Métricas-chave consolidadas:

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
| **Motor de prazos regulamentares (Fase 2)** *(nova)* | 100% em bateria de 30 casos de calendário | E1, E7 |
| **CHD, progresso × meta, bloqueios RN-04, elegibilidade a recurso** *(nova)* | 100% (determinístico) | E3–E5, E7 |
| **Macro-F1 do classificador de ocorrências (intercorrência × evento planejado)** *(nova)* | Medida e registrada (baseline no E3) | E3, E7 |
| **Casos de teste S21–S24** *(nova)* | 32/32 executados e registrados | E3–E5 |
| **Testes INT-E01 a INT-E08** *(nova)* | 8/8 aprovados | E7 |
| **Acurácia do conceito sugerido × conceito real do PETRVS (RC9)** *(nova)* | Medida e registrada (E6); meta quantitativa a fixar com Q6 | E6, E7 |
| **Satisfação de chefias e participantes do piloto B4** *(nova)* | ≥ 4 (escala 1–5) | E7 |

O registro de execução em `execucoes_skill` (versão da skill, modelo, entrada, saída
integral, tempo) segue sendo a base da reprodutibilidade. A validação mais forte da Fase 2
é a conciliação com as camadas 3–4 do PETRVS (RC9) — comparar o conceito sugerido por
S22/S24 com o conceito real lançado em `avaliacoes` para o mesmo objeto, com anonimização.
Metas acadêmicas completas seguem condicionadas a Q6.

---

## 10. Matriz de riscos consolidada *(revisada)*

RP01–RP15 permanecem como na v4 §10; o acompanhamento ativo (com coluna Status) está em
`docs/gestao/riscos.md`. Destaques de status em 18.08.2026: RP03/RP04/RP06/RP07 mitigados
pelo esquema; RP12/RP13/RP15 mitigados e verificados; demais abertos.

**Riscos incorporados ou novos nesta v5:**

| # | Risco | Prob. | Impacto | Mitigação | Dono |
| --- | --- | --- | --- | --- | --- |
| RP16 *(formalizado)* | Máquina de desenvolvimento sem rota de rede para o Denodo (confirmado em 26.07.2026) — bloqueia `sincronizar_ref.py`, o aceite do I0, o I5 e a etapa E6 | Alta (confirmada) | Alto | Executar a sincronização de máquina com VPN/rede institucional; documentar o procedimento de rede; acionar TI/Dataprev (Q16); contingência sintética para E6 | Coordenador |
| RP17 | Dado sensível de saúde em intercorrência (a IN cita "situações de saúde" como intercorrência a registrar) | Alta | Alto | `ocorrencias.sensivel = 1`; armazenar **apenas categoria e impacto em horas**; conteúdo clínico nunca persistido; S23-T06 como teste de segurança obrigatório; orientação explícita ao participante | Coordenador |
| RP18 | Agente induzindo o conceito — sugestão com aparência de decisão enviesa a chefia e gera contestação com efeito funcional | Média | Alto | Invariante I2; `origem_conceito` explícito; parecer não homologado ostenta marcação; justificativa sempre da chefia, nunca autopreenchida sem revisão | Coordenador |
| RP19 | Assimetria PE × PT (C-02): tratar as duas avaliações como um só objeto ofereceria recurso onde ele não existe | Média | Alto | Separação estrutural desde o modelo de dados (`avaliacoes.objeto_tipo`); testes de regressão específicos | Coordenador |
| RP20 | Datas do ciclo 2026 inconsistentes (C-01) fariam o motor de prazos calcular errado | Alta | Alto | E0 bloqueia a implementação até confirmação da CGGE (Q9); o motor recebe o calendário por configuração, não por constante | Analistas |
| RP21 | Faixa percentual sem lastro normativo (A-01) migrar para o agente como se fosse norma | Média | Médio | Registro como regra institucional com fonte e vigência; rotulagem obrigatória na saída (S22-T07) | Analistas |
| RP22 | Uso indevido da avaliação do PGD como avaliação de desempenho anual (RN-36) | Média | Médio | Ressalva obrigatória em todo parecer (S24-T09); menção na capacitação | Analistas |
| RP23 | Volume do ciclo mensal (PT mensal × N participantes × 12 meses) inviabilizar o uso manual | Média | Médio | Processamento em lote no S18 (pós-MVP); priorizar unidades-piloto; medir tempo médio por registro no E7 | Coordenador |
| RP24 | Exposição de dados individuais em relatórios de transparência | Média | Alto | Pseudônimos (`participantes.rotulo`); agregação por unidade; nenhum ranking individual | Coordenador |

---

## 11. Governança de dados e uso responsável de IA *(ampliada)*

Herda integralmente a Seção 11 da v4 (dados de pessoas; espelho `ref_usuarios` mínimo —
D2; documentos institucionais fora do Git até classificação; o agente não decide;
rastreabilidade como requisito; backups protegidos), com as seguintes adições da Fase 2:

1. **Saúde nunca é persistida (RP17).** Intercorrência de natureza pessoal é registrada
   por **categoria e impacto em horas**; a justificativa detalhada e qualquer conteúdo
   clínico ficam fora do banco. S23-T06 é teste de segurança obrigatório, e a auditoria do
   B4 inclui varredura de dump anonimizado.
2. **O agente jamais avalia pessoas.** S22/S24 sugerem conceito com fundamentação e
   confiança; o conceito válido é sempre decisão humana registrada (`decisoes_humanas` +
   `origem_conceito`). Parecer sem homologação circula com marcação de rascunho (RP18).
3. **A avaliação do PGD não substitui a avaliação de desempenho anual** (GDAEM/AvaliaGov)
   — ressalva obrigatória em todo parecer exportado (RN-36; RP22).
4. **Foco na contribuição, não no comportamento** (RN-33): observações sobre
   características pessoais não previstas no TCR são recusadas pela skill, com registro do
   motivo (S24-T08).
5. **Caráter não punitivo** (RN-35): pendência com justificativa coerente é reprogramada,
   não penalizada; a política de consequências só se aplica na ausência de justificativa.
6. **Transparência sem exposição individual** (RP24): relatórios e bloqueios de conclusão
   (RN-04) usam pseudônimos; agregação por unidade; nenhum ranking individual.
7. **PETRVS permanece somente leitura** (ADR-002) também nas camadas 3–4: espelhamento,
   conciliação e validação acadêmica jamais escrevem no sistema-fonte.

---

## 12. Checklist de execução da v5

**Fase 1 — MVP (estado em 18.08.2026):**

- [x] **I0 (Trilha T)** — repo estruturado; MySQL 8.4 como serviço; migração `001`
  aplicada (21 tabelas); teste de imutabilidade aprovado; `versoes.py` operacional;
  backup diário agendado; ADRs 001–006; matriz de riscos ativa em `docs/gestao/riscos.md`
- [ ] **I0 (fechamento)** — `ref_unidades`/`ref_usuarios` sincronizadas (**bloqueado:
  RP16**); fontes institucionais aprovadas (Q5); glossário institucional; equipe roda
  `git pull` + `.venv` sem ajuda; ata de aprovação do modelo pelos analistas
- [ ] **I1 / B1** — 2 endpoints demonstrados; I02 = CSV oficial; 20 perguntas anotadas
- [ ] **I2** — RAG citando fontes; perfil institucional versionado (S01); S02 aprovado
  *(destrava E0 da Fase 2)*
- [ ] **I3** — fluxo S03→S04→S05 com entregas reais; macro-F1 medida; conjunto anotado ≥ 50
- [ ] **I4 / B2** — auditoria de portfólio demonstrada ponta a ponta; utilidade registrada
- [ ] **I5** — cálculos determinísticos 100%; matriz de cobertura; pseudônimos
- [ ] **I6** — agente Agno decide entre A/B/C em 10 perguntas mistas; processo TI iniciado
- [ ] **I7 / B3** — INT-T01..T08 aprovados; Copilot Studio ativo; piloto executado;
  ≥ 2 gestores ao vivo; comparação agente × PETRVS registrada

**Fase 2 — Execução e Avaliação (aprovada nesta v5):**

- [ ] **Abertura** — ADR-007 registrado; decisão caminho completo × caminho curto em ata;
  respostas a Q9–Q11 solicitadas à CGGE
- [ ] **E0** — 36 regras (RN-01..36) carregadas com fonte e vigência; C-01..03 em
  `regras_conflitos`; faixa CGOV declarada como regra institucional; ata de validação
- [ ] **E1** — motor de prazos 100% (30 casos); motor de competência; contratos Pydantic;
  conjuntos anotados versionados
- [ ] **E2** — migração `002` aplicada: 33 tabelas, 14 triggers; imutabilidade comprovada
  nas 4 novas `*_versoes`; S17-mínimo; smoke test PT v1 → execução → avaliação → recurso →
  v2 com rollback limpo
- [ ] **E3** — S21/S23 operacionais; 14 casos aprovados; férias jamais viram
  intercorrência; conclusão de PE bloqueada com PT pendente; nenhum dado de saúde
  persistido; macro-F1 de ocorrências registrada
- [ ] **E4** — S22/S24 operacionais; 18 casos aprovados; nenhum conceito sem
  `decisao_humana_id`; conceito 1/5 sem justificativa bloqueado; ressalva RN-36 em todo
  parecer
- [ ] **E5** — rito de recurso completo; reavaliação preserva a original; recurso
  indisponível para PE e conceitos 1–3
- [ ] **E6** — conciliação Petrvs executada (ou contingência sintética documentada);
  acurácia do conceito registrada (RC9)
- [ ] **E7 / B4** — INT-E01..E08 aprovados; piloto CGOV/COCAGE em ciclo real; ≥ 2 chefias
  e 4 participantes ao vivo; ciclo completo com recurso simulado sem perda de
  identificadores; feedback registrado
- [ ] Métricas da Seção 9 medidas e registradas; backlog remanescente (S11, S12, S14, S15,
  S18–S20) priorizado → insumo da proposta v6

---

## 13. Registro de mudanças v4 → v5

| Seção | Mudança | Origem |
| --- | --- | --- |
| Cabeçalho e Sumário | v5 substitui v4; `skills/05` vira anexo de especificação vinculante; cinco decisões (ADR-007) | `05` (18.08.2026); rito do RP09 |
| §1.1 | Inventário atualizado com o `05` | `05` |
| §1.3–1.4 | Conclusões (f)–(i); reposicionamento de S13/S16/S17; S14 acionada por S21/S23 | `05` §1, §4.3, §4.4 |
| §1.5 | PA5–PA8 (achados A-01/A-02/A-03 e conflito C-01/C-02) | `05` §3.5, §4.4 |
| §2.1 | Objetivo geral ganha a capacidade (d) — execução e avaliação | `05` |
| §2.2 | RC7–RC9 vinculados ao Checkpoint B4 | `05` §11 |
| §2.3 | Fase 2 dentro do escopo; "fora" atualizado (S11–S20 remanescentes; v6); nota sobre S11/S12 | `05`; RP09 |
| §2.4 | Q9–Q16 (mapeando Q1–Q8 do `05` §12); Q8 mantida como respondida | `05` §12 |
| §3.1 | Camadas 1, 2 e 4 anotadas com a Fase 2 (33 tabelas, 14 triggers) | `05` §5, §7 |
| §3.2 | Migração `002`: grupos 8–10 (12 tabelas); funções novas em `versoes.py` | `05` §7 |
| §3.3 | Linhas novas de stack: motores de prazos e competência, conceito híbrido, contratos da Fase 2 | `05` §5.2, §9 (E1) |
| §3.4 | Invariantes I1–I4 do bloco | `05` §5.1 |
| §4 (EAP) | 2.9, 3.7–3.9, 4.5; B4 em 1.4 e 4.4 | `05` |
| §5.1, §5.3, §5.4 | `05` na série AN; linha RACI da base normativa (CGGE); ADR-007 | `05` |
| §6 | Roadmap em duas fases; estado do I0 em 18.08.2026; tabela E0–E7; dependências entre fases; aceite do B4; caminho curto | `05` §9; CLAUDE.md/riscos.md (estado) |
| §7 | `migracoes/002`, `contratos/`, `prazos.py`, `competencia.py`, specs S21–S24; v4 → registro histórico | `05` |
| §8 | Definição de pronto ampliada; quatro contratos de saída novos | `05` §5.3, §11.1 |
| §9 | Sete métricas novas da Fase 2 | `05` §9, §11 |
| §10 | RP16 formalizado na matriz; RP17–RP24 novos | riscos.md (26.07.2026); `05` §10 |
| §11 | Itens 1–7 da Fase 2 (saúde, conceito, RN-36, RN-33, RN-35, transparência, somente leitura nas camadas 3–4) | `05` §10; ADR-002 |
| §12 | Checklist em duas fases, com estado real do I0 | CLAUDE.md; riscos.md |
| Demais seções (2.1 nas capacidades a–c, 3 nas capacidades, 5.2, 6.2 nos aceites de I1–I7, 8.1–8.2, 9 no MVP) | Mantidas da v4 sem alteração de mérito | — |

---

*Documento elaborado como revisão ampliada da v4, motivada pela conclusão do
`skills/05_plano-skills-execucao-avaliacao_v1.md` (18.08.2026) — análise normativa e
especificação do bloco S21–S24 —, seguindo o rito de controle de escopo estabelecido pelo
risco RP09 ("inclusão exige v5"). A incorporação do bloco e o reposicionamento de
S13/S16/S17 serão registrados no ADR-007. A v2 permanece como Anexo de Capacitação
(glossário e Tutoriais T1–T6); os artefatos `02_matriz`, `03_especificacao` e `04_backlog`
permanecem como especificações vinculadas do MVP; o `AT-01` é o anexo técnico vinculante do
modelo de dados; o `05` é o anexo de especificação vinculante da Fase 2. Alterações de
escopo ou de stack geram a versão 6, com registro do motivo em `docs/gestao/decisoes/`.*
