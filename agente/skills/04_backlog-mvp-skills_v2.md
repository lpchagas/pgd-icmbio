# Backlog executável do MVP do Assistente de PGD do ICMBio

========================================================

---

## 1. Objetivo do projeto

Implementar e avaliar academicamente um MVP composto por dez skills:

| Código | Skill                                                    |
| ------ | -------------------------------------------------------- |
| S01    | Configurador Institucional do PGD                        |
| S02    | Verificador Normativo e de Conformidade                  |
| S03    | Extrator de Competências e Responsabilidades em Entregas |
| S04    | Administrador do Catálogo de Entregas                    |
| S05    | Designer de Metas, Indicadores e Critérios de Aceite     |
| S06    | Auditor de Portfólio de Entregas                         |
| S07    | Planejador de Capacidade da Unidade                      |
| S08    | Matriz de Cobertura das Entregas pela Equipe             |
| S09    | Designer e Auditor de Encadeamento OKR-D                 |
| S10    | Analisador de Riscos, Dependências e Restrições          |

O MVP deverá permitir o seguinte fluxo:

> Fontes institucionais → regras e estrutura → competências → entregas candidatas → catálogo → metas e critérios de aceite → auditoria do portfólio → capacidade → cobertura da equipe → encadeamento OKR-D → riscos e dependências.

---

## 2. Premissas de planejamento

### 2.1 Duração

* Sete sprints.

* Duas semanas por sprint.

* Duração total estimada: 14 semanas.

* Uma semana adicional pode ser reservada para preparação do ambiente ou aprovação ética da pesquisa, sem alterar a sequência funcional.

### 2.2 Capacidade de referência

A capacidade estimada é de aproximadamente **45 a 55 pontos por sprint**.

Essa estimativa considera uma equipe com dedicação parcial de especialistas institucionais e dedicação predominante da equipe técnica.

### 2.3 Escala de estimativas

| Pontos | Complexidade aproximada | Esforço ideal de referência |
| ------ | ----------------------- | --------------------------- |
| 1      | Ajuste muito pequeno    | Até 1 dia                   |
| 2      | Pequeno                 | 1 a 2 dias                  |
| 3      | Baixo                   | 2 a 3 dias                  |
| 5      | Médio                   | 3 a 5 dias                  |
| 8      | Alto                    | 5 a 8 dias                  |
| 13     | Muito alto              | 8 a 13 dias                 |

Os pontos incluem desenvolvimento, testes unitários e documentação técnica básica. Testes acadêmicos, validação de especialistas e integrações complexas aparecem como tarefas próprias.

---

## 3. Papéis e responsabilidades

| Sigla  | Papel                                  | Responsabilidades                                                                          |
| ------ | -------------------------------------- | ------------------------------------------------------------------------------------------ |
| PO     | Responsável pelo produto e pesquisa    | Priorizar backlog, aceitar entregas, coordenar pesquisa e resolver decisões de escopo.     |
| ED     | Especialista de domínio em PGD         | Validar regras, conceitos, exemplos, classificações e padrão-ouro.                         |
| ARQ    | Arquiteto ou líder técnico             | Definir arquitetura, contratos, segurança, integrações e padrões técnicos.                 |
| IA     | Engenheiro de IA                       | Prompts, recuperação de informação, classificação, avaliação de modelos e explicabilidade. |
| BE     | Desenvolvedor backend                  | APIs, regras, persistência, versionamento e processamento.                                 |
| FE     | Desenvolvedor frontend                 | Interfaces, formulários, matrizes, relatórios e experiência de uso.                        |
| QA     | Analista de qualidade                  | Estratégia de testes, automação, regressão e rastreabilidade de defeitos.                  |
| DEVSEC | DevOps e segurança                     | Ambientes, implantação, logs, controle de acesso e proteção de dados.                      |
| UX     | Pesquisador ou designer de experiência | Fluxos conversacionais, usabilidade, acessibilidade e testes com usuários.                 |
| DA     | Analista de dados e avaliação          | Métricas, amostras, análise estatística e painéis acadêmicos.                              |

Um profissional pode acumular mais de um papel em uma equipe menor, desde que sejam preservadas a validação de domínio e a revisão independente dos resultados acadêmicos.

---

## 4. Épicos do projeto

| Épico | Conteúdo                                        | Skills relacionadas | Sprint principal |
| ----- | ----------------------------------------------- | ------------------- | ---------------- |
| EP01  | Arquitetura, dados, segurança e rastreabilidade | Todas               | 1                |
| EP02  | Configuração institucional                      | S01                 | 1                |
| EP03  | Conformidade e extração de entregas             | S02 e S03           | 2                |
| EP04  | Catálogo, metas e aceite                        | S04 e S05           | 3                |
| EP05  | Auditoria do portfólio                          | S06                 | 4                |
| EP06  | Capacidade e cobertura da equipe                | S07 e S08           | 5                |
| EP07  | Encadeamento estratégico e riscos               | S09 e S10           | 6                |
| EP08  | Integração, avaliação acadêmica e piloto        | Todas               | 7                |

---

## 5. Caminho crítico

O caminho crítico recomendado é:

> EP01 → S01 → S02/S03 → S04/S05 → S06 → S07/S08 → S09/S10 → integração e avaliação.

Dependências essenciais:

1. S02 depende das regras e fontes configuradas em S01.

2. S03 depende do modelo comum de classificação e entrega.

3. S04 depende das entregas candidatas validadas.

4. S05 depende da classificação da entrega e dos campos estruturados.

5. S06 depende das entregas completas e do catálogo.

6. S07 depende das metas e estimativas das entregas.

7. S08 depende dos dados de capacidade e das contribuições individuais.

8. S09 depende de entregas estruturadas e elementos estratégicos.

9. S10 depende das entregas, metas, prazos e capacidade.

10. A avaliação acadêmica depende de logs, versionamento e reprodutibilidade implantados desde o início.

---

## 6. Sprint 1 — Fundação e Configurador Institucional

### 6.1 Objetivo

Criar a arquitetura mínima do agente, o modelo comum de dados, os controles de segurança e a primeira versão funcional da S01.

### 6.2 Backlog da sprint

| ID     | Tarefa técnica                                                   | Responsável | Apoio       | Estimativa | Dependência     | Entregável                                                            |
| ------ | ---------------------------------------------------------------- | ----------- | ----------- | ---------- | --------------- | --------------------------------------------------------------------- |
| SP1-01 | Definir arquitetura lógica do MVP                                | ARQ         | PO, IA, BE  | 5          | Nenhuma         | Diagrama de componentes e decisões arquiteturais                      |
| SP1-02 | Definir modelo comum de dados                                    | ARQ         | BE, ED, DA  | 8          | SP1-01          | Esquemas de regra, fonte, unidade, entrega, OKR-D, capacidade e risco |
| SP1-03 | Implementar identificadores, versionamento e trilha de auditoria | BE          | ARQ, DEVSEC | 8          | SP1-02          | Serviços de versionamento e histórico                                 |
| SP1-04 | Implementar cadastro de fontes institucionais                    | BE          | FE, ED      | 5          | SP1-02          | API e tela de cadastro de fontes                                      |
| SP1-05 | Implementar classificação da natureza das regras                 | IA          | ED, BE      | 5          | SP1-04          | Classificação norma/regra/recomendação/exemplo                        |
| SP1-06 | Implementar cadastro de unidades, hierarquia e papéis            | BE          | FE, ED      | 5          | SP1-02          | Estrutura organizacional básica                                       |
| SP1-07 | Implementar controle de acesso inicial                           | DEVSEC      | ARQ, BE     | 5          | SP1-01          | Perfis e permissões                                                   |
| SP1-08 | Criar interface de administração da S01                          | FE          | UX, BE      | 5          | SP1-04, SP1-06  | Tela de configuração institucional                                    |
| SP1-09 | Criar testes unitários e de segurança da S01                     | QA          | DEVSEC, BE  | 3          | SP1-04 a SP1-08 | Suíte automatizada                                                    |
| SP1-10 | Elaborar guia de configuração institucional                      | ED          | PO, UX      | 2          | SP1-05          | Documento de uso e governança                                         |

**Estimativa total:** 51 pontos.

### 6.3 Riscos da sprint

| Risco                                                                 | Probabilidade | Impacto | Resposta                                                          |
| --------------------------------------------------------------------- | ------------- | ------- | ----------------------------------------------------------------- |
| Modelo de dados crescer excessivamente                                | Alta          | Alto    | Fixar modelo mínimo; registrar extensões no backlog posterior.    |
| Documentos institucionais apresentarem conflitos                      | Média         | Alto    | Implementar estado “conflitante” e exigir decisão humana.         |
| Regras metodológicas serem confundidas com normas                     | Alta          | Alto    | Tornar a natureza da regra campo obrigatório.                     |
| Hierarquia organizacional não estar disponível em formato estruturado | Média         | Médio   | Permitir cadastro manual e importação futura.                     |
| Dados sensíveis serem cadastrados sem controle                        | Média         | Alto    | Aplicar perfis e classificação de acesso desde a primeira sprint. |

### 6.4 Critérios de conclusão

A sprint será concluída quando:

1. O modelo comum de dados estiver documentado e versionado.

2. Uma fonte institucional puder ser cadastrada com metadados.

3. Uma regra puder ser vinculada a uma fonte e classificada por natureza.

4. Conflitos entre regras puderem ser registrados sem decisão automática.

5. Unidades e relações hierárquicas puderem ser cadastradas.

6. Relações hierárquicas circulares forem rejeitadas.

7. Perfis não autorizados não puderem alterar regras vigentes.

8. Toda alteração gerar registro de auditoria.

9. Os testes críticos da S01 estiverem aprovados.

10. A demonstração da sprint for aceita pelo PO e pelo ED.

---

## Sprint 2 — Conformidade e Extração de Entregas

### 7.1 Objetivo

Implementar a S02 e a S03, permitindo verificar conformidade e transformar competências ou atividades em entregas candidatas.

### 7.2 Backlog da sprint

| ID     | Tarefa técnica                                                               | Responsável | Apoio   | Estimativa | Dependência     | Entregável                              |
| ------ | ---------------------------------------------------------------------------- | ----------- | ------- | ---------- | --------------- | --------------------------------------- |
| SP2-01 | Implementar motor de regras da S02                                           | BE          | ARQ, ED | 8          | S01             | Serviço de verificação configurável     |
| SP2-02 | Implementar seleção temporal de regras                                       | BE          | QA      | 5          | SP2-01          | Aplicação de regras por vigência        |
| SP2-03 | Implementar relatório de conformidade                                        | FE          | BE, UX  | 5          | SP2-01          | Visão de erros, alertas e recomendações |
| SP2-04 | Implementar classificador objetivo/entrega/atividade/tarefa/responsabilidade | IA          | ED, DA  | 8          | Modelo de dados | Classificador com confiança             |
| SP2-05 | Implementar extração de produto ou serviço candidato                         | IA          | ED      | 5          | SP2-04          | Sugestão de entrega candidata           |
| SP2-06 | Implementar geração de perguntas para ambiguidade                            | IA          | UX, ED  | 5          | SP2-05          | Perguntas contextuais                   |
| SP2-07 | Implementar revisão em lote das candidatas                                   | FE          | BE, UX  | 5          | SP2-05          | Tela aprovar/rejeitar/agrupar           |
| SP2-08 | Criar conjunto inicial anotado para classificação                            | ED          | DA, PO  | 5          | Nenhuma         | Base de desenvolvimento                 |
| SP2-09 | Automatizar testes da S02 e S03                                              | QA          | IA, BE  | 5          | SP2-01 a SP2-07 | Suíte funcional e de regressão          |
| SP2-10 | Medir desempenho inicial dos classificadores                                 | DA          | IA, ED  | 3          | SP2-08, SP2-09  | Relatório de precisão e erros           |

**Estimativa total:** 54 pontos.

### 7.3 Riscos da sprint

| Risco                                                         | Probabilidade | Impacto | Resposta                                                                    |
| ------------------------------------------------------------- | ------------- | ------- | --------------------------------------------------------------------------- |
| Baixa precisão na distinção entre responsabilidade e entrega  | Alta          | Alto    | Usar exemplos contrastivos e obrigar confirmação humana em baixa confiança. |
| Sistema inventar produto ou serviço não sustentado pelo texto | Média         | Alto    | Exigir vínculo com trecho de origem e justificar inferências.               |
| Falsos positivos normativos                                   | Média         | Alto    | Exigir fonte para toda não conformidade.                                    |
| Conjunto de exemplos insuficiente                             | Alta          | Médio   | Adotar amostragem incremental e análise de erros a cada versão.             |
| Relatório discursivo dificultar correção                      | Média         | Médio   | Produzir saída estruturada por campo e gravidade.                           |

### 7.4 Critérios de conclusão

1. A S02 distinguir erro, alerta e recomendação.

2. Toda não conformidade apresentar regra e fonte.

3. Planos históricos utilizarem regras vigentes no período correspondente.

4. A S03 classificar textos nas cinco categorias definidas.

5. Toda candidata preservar o trecho de origem.

6. Entradas ambíguas gerarem perguntas em vez de preenchimento automático.

7. Candidatas aprovadas gerarem objeto estruturado.

8. A macro-F1 inicial da classificação ser calculada e documentada.

9. Casos de erro conhecidos serem incorporados à regressão.

10. PO e ED aprovarem a demonstração integrada S01–S03.

---

## Sprint 3 — Catálogo, Metas e Critérios de Aceite

### 8.1 Objetivo

Implementar o catálogo institucional de entregas e os mecanismos de definição de metas, indicadores e critérios de aceite.

### 8.2 Backlog da sprint

| ID     | Tarefa técnica                                         | Responsável | Apoio  | Estimativa | Dependência     | Entregável                      |
| ------ | ------------------------------------------------------ | ----------- | ------ | ---------- | --------------- | ------------------------------- |
| SP3-01 | Implementar repositório versionado do catálogo         | BE          | ARQ    | 5          | S03             | Serviço de catálogo             |
| SP3-02 | Implementar busca textual e semântica                  | IA          | BE, DA | 8          | SP3-01          | Busca por similaridade          |
| SP3-03 | Implementar detecção de duplicidades                   | IA          | ED, QA | 5          | SP3-02          | Alertas de similaridade         |
| SP3-04 | Implementar fluxo de publicação e aprovação            | BE          | FE, ED | 5          | SP3-01          | Rascunho, revisão e publicação  |
| SP3-05 | Implementar interface de pesquisa e adaptação          | FE          | UX     | 5          | SP3-02          | Tela de catálogo                |
| SP3-06 | Implementar designer de metas por tipo de entrega      | IA          | ED, BE | 8          | S03             | Sugestões para projeto/processo |
| SP3-07 | Implementar separação meta final/progresso esperado    | BE          | ED, QA | 5          | SP3-06          | Campos e validações distintas   |
| SP3-08 | Implementar critérios de aceite e evidências esperadas | BE          | FE, ED | 5          | SP3-06          | Editor de aceite                |
| SP3-09 | Implementar validação de mensurabilidade               | IA          | ED, QA | 5          | SP3-06          | Alertas para metas vagas        |
| SP3-10 | Criar testes de busca, metas e aceite                  | QA          | IA, BE | 5          | SP3-01 a SP3-09 | Suíte automatizada              |

**Estimativa total:** 56 pontos.

Caso a capacidade da equipe seja de 50 pontos, SP3-10 pode ser parcialmente antecipada durante o desenvolvimento e finalizada no início da Sprint 4.

### 8.3 Riscos da sprint

| Risco                                                 | Probabilidade | Impacto | Resposta                                                        |
| ----------------------------------------------------- | ------------- | ------- | --------------------------------------------------------------- |
| Busca semântica sugerir modelos inadequados           | Média         | Médio   | Exibir similaridade e contexto, sem aplicação automática.       |
| Catálogo padronizar excessivamente unidades distintas | Média         | Alto    | Permitir adaptação e registrar apenas referência de origem.     |
| Meta final ser confundida com percentual de progresso | Alta          | Alto    | Campos distintos e validações específicas.                      |
| Critérios de aceite permanecerem subjetivos           | Alta          | Médio   | Exigir condição observável e evidência esperada.                |
| Duplicidades legítimas serem fundidas                 | Média         | Médio   | Manter decisão humana e justificativa para registros separados. |

### 8.4 Critérios de conclusão

1. Entregas aprovadas poderem ser publicadas no catálogo.

2. Toda entrada possuir versão e histórico.

3. Busca por título e semântica retornar resultados relevantes.

4. Duplicidades serem sinalizadas antes da publicação.

5. Modelos poderem ser adaptados sem alterar o original.

6. Metas possuírem unidade de medida ou condição de conclusão.

7. Meta final e progresso esperado serem armazenados separadamente.

8. Critérios vagos gerarem solicitação de refinamento.

9. Toda meta possuir fonte de verificação ou alerta de ausência.

10. Testes de integração S03–S05 estarem aprovados.

---

## 9. Sprint 4 — Auditoria do Portfólio

### 9.1 Objetivo

Implementar a S06 para avaliar o plano como conjunto e identificar duplicidades, lacunas, problemas de granularidade e inconsistências.

### 9.2 Backlog da sprint

| ID     | Tarefa técnica                                      | Responsável | Apoio   | Estimativa | Dependência     | Entregável                      |
| ------ | --------------------------------------------------- | ----------- | ------- | ---------- | --------------- | ------------------------------- |
| SP4-01 | Implementar estrutura do plano de entregas          | BE          | ARQ, ED | 5          | S05             | Objeto de portfólio             |
| SP4-02 | Implementar detecção de duplicidades no plano       | IA          | ED, QA  | 5          | S04             | Comparador semântico            |
| SP4-03 | Implementar análise de sobreposição de escopo       | IA          | ED      | 8          | SP4-01          | Diagnóstico de escopo           |
| SP4-04 | Implementar comparação com competências da unidade  | IA          | BE, ED  | 8          | S01, S03        | Matriz competência × entrega    |
| SP4-05 | Implementar análise de granularidade                | IA          | ED      | 5          | S03             | Alertas de dividir/agrupar      |
| SP4-06 | Implementar análise de relevância gerencial         | IA          | ED, PO  | 5          | SP4-05          | Classificação e justificativa   |
| SP4-07 | Implementar relatório consolidado do portfólio      | FE          | BE, UX  | 5          | SP4-02 a SP4-06 | Painel de auditoria             |
| SP4-08 | Implementar tratamento de justificativas gerenciais | BE          | FE      | 3          | SP4-07          | Aceitar, corrigir ou justificar |
| SP4-09 | Criar conjunto de planos sintéticos para teste      | ED          | DA, QA  | 5          | Nenhuma         | Casos positivos e negativos     |
| SP4-10 | Executar avaliação de precisão da S06               | DA          | QA, ED  | 3          | SP4-09          | Relatório de desempenho         |

**Estimativa total:** 52 pontos.

### 9.3 Riscos da sprint

| Risco                                                   | Probabilidade | Impacto | Resposta                                                                   |
| ------------------------------------------------------- | ------------- | ------- | -------------------------------------------------------------------------- |
| Competências institucionais serem amplas demais         | Alta          | Médio   | Tratar ausência de vínculo como possível lacuna, não como erro automático. |
| Avaliação de granularidade ser excessivamente subjetiva | Alta          | Alto    | Explicitar critérios e manter decisão gerencial.                           |
| Similaridade lexical não representar sobreposição real  | Média         | Médio   | Combinar título, descrição, meta e destinatário.                           |
| Relatório gerar excesso de alertas                      | Média         | Alto    | Priorizar gravidade, confiança e impacto.                                  |
| Planos de teste não refletirem situações reais          | Média         | Médio   | Incluir casos anonimizados após validação institucional.                   |

9.4 Critérios de conclusão

---

1. A S06 analisar um plano completo.

2. Duplicidades e sobreposições serem apresentadas separadamente.

3. Lacunas de competência serem vinculadas à fonte institucional.

4. Atividades registradas como entregas serem sinalizadas.

5. Recomendações de divisão ou agrupamento apresentarem justificativa.

6. Usuário poder aceitar, corrigir ou justificar um alerta.

7. Alertas permanecerem rastreáveis até as entregas analisadas.

8. Relatório apresentar criticidade e confiança.

9. Desempenho ser medido contra conjunto anotado.

10. Integração S01–S06 estar demonstrável ponta a ponta.

---

## 10. Sprint 5 — Capacidade e Cobertura da Equipe

### 10.1 Objetivo

Implementar a S07 e S08 para analisar capacidade útil, demanda estimada, distribuição de esforço e cobertura das entregas.

### 10.2 Backlog da sprint

| ID     | Tarefa técnica                                                      | Responsável | Apoio      | Estimativa | Dependência     | Entregável                 |
| ------ | ------------------------------------------------------------------- | ----------- | ---------- | ---------- | --------------- | -------------------------- |
| SP5-01 | Implementar cadastro de participantes e disponibilidade             | BE          | FE, DEVSEC | 5          | Modelo de dados | Base de capacidade         |
| SP5-02 | Implementar cálculo de carga horária útil                           | BE          | QA, ED     | 5          | SP5-01          | Motor de capacidade        |
| SP5-03 | Implementar estimativas por horas e faixas                          | BE          | FE, UX     | 5          | S05             | Editor de estimativas      |
| SP5-04 | Implementar cenários mínimo, provável e máximo                      | BE          | DA, FE     | 5          | SP5-03          | Simulador                  |
| SP5-05 | Implementar identificação de déficit, folga e lacuna de competência | BE          | IA, ED     | 8          | SP5-02 a SP5-04 | Diagnóstico de viabilidade |
| SP5-06 | Implementar matriz entrega × participante                           | FE          | BE, UX     | 5          | SP5-01          | Matriz de cobertura        |
| SP5-07 | Implementar validação de 100% dos planos individuais                | BE          | QA         | 3          | SP5-06          | Regra de totalização       |
| SP5-08 | Implementar alertas de entrega sem cobertura                        | BE          | IA         | 3          | SP5-06          | Alertas de cobertura       |
| SP5-09 | Implementar detecção de concentração e pessoa-chave                 | IA          | ED, DA     | 5          | SP5-06          | Risco de concentração      |
| SP5-10 | Criar testes matemáticos determinísticos                            | QA          | BE, DA     | 5          | SP5-02 a SP5-09 | Suíte de cálculo           |
| SP5-11 | Criar relatório integrado de capacidade e cobertura                 | FE          | UX, BE     | 5          | SP5-05 a SP5-09 | Painel gerencial           |

**Estimativa total:** 54 pontos.

### 10.3 Riscos da sprint

| Risco                                                        | Probabilidade | Impacto | Resposta                                                |
| ------------------------------------------------------------ | ------------- | ------- | ------------------------------------------------------- |
| Estimativas de esforço produzirem falsa precisão             | Alta          | Alto    | Permitir faixas e exibir incerteza.                     |
| Percentuais individuais serem confundidos com progresso      | Alta          | Alto    | Rótulos, ajuda contextual e testes de usabilidade.      |
| Dados pessoais de disponibilidade serem expostos             | Média         | Alto    | Controle por perfil e agregação em relatórios.          |
| Equipe possuir horas, mas não competência necessária         | Média         | Alto    | Separar déficit de capacidade de lacuna de competência. |
| Concentração ser sinalizada em entregas de baixa criticidade | Média         | Médio   | Considerar prioridade e substituição disponível.        |

### 10.4 Critérios de conclusão

1. Capacidade nominal e útil serem apresentadas separadamente.

2. Férias, licenças e afastamentos reduzirem a capacidade.

3. Estimativas aceitarem horas ou faixas.

4. Cenários mínimo, provável e máximo serem reproduzíveis.

5. Déficit de horas e lacuna de competência serem diferenciados.

6. Cada plano individual totalizar 100%.

7. Entregas sem cobertura serem identificadas.

8. Contribuições externas serem destacadas.

9. Concentração crítica gerar alerta contextualizado.

10. Todos os cálculos determinísticos possuírem exatidão de 100%.

---

## 11. Sprint 6 — Encadeamento OKR-D e Riscos

### 11.1 Objetivo

Implementar a S09 e a S10, conectando estratégia, entregas e execução e estruturando riscos, impedimentos, dependências e restrições.

### 11.2 Backlog da sprint

| ID     | Tarefa técnica                                                    | Responsável | Apoio    | Estimativa | Dependência     | Entregável                               |
| ------ | ----------------------------------------------------------------- | ----------- | -------- | ---------- | --------------- | ---------------------------------------- |
| SP6-01 | Implementar modelo de objetivos e resultados-chave                | BE          | ED, ARQ  | 5          | Modelo comum    | Estrutura OKR-D                          |
| SP6-02 | Implementar classificador objetivo/KR/entrega/atividade           | IA          | ED, DA   | 8          | S03             | Classificador estratégico                |
| SP6-03 | Implementar editor de vínculos muitos-para-muitos                 | FE          | BE, UX   | 5          | SP6-01          | Mapa de vínculos                         |
| SP6-04 | Implementar auditoria da plausibilidade dos vínculos              | IA          | ED       | 8          | SP6-02, SP6-03  | Avaliação direta/indireta/contextual     |
| SP6-05 | Implementar detecção de lacunas OKR-D                             | BE          | IA, FE   | 5          | SP6-03          | KRs sem entregas e entregas sem vínculo  |
| SP6-06 | Implementar visualização do encadeamento                          | FE          | UX, BE   | 5          | SP6-03          | Mapa objetivo → KR → entrega → atividade |
| SP6-07 | Implementar registro estruturado de riscos                        | BE          | FE, ED   | 5          | S05             | Cadastro de risco                        |
| SP6-08 | Implementar classificador risco/impedimento/dependência/restrição | IA          | ED, DA   | 8          | SP6-07          | Classificador com confiança              |
| SP6-09 | Implementar matriz de probabilidade e impacto                     | BE          | FE, ED   | 3          | SP6-07          | Avaliação configurável                   |
| SP6-10 | Implementar integração de riscos com capacidade e prazo           | BE          | S07, S05 | 5          | SP6-07, S07     | Impactos relacionados                    |
| SP6-11 | Implementar detecção de riscos duplicados                         | IA          | QA       | 3          | SP6-07          | Alerta de consolidação                   |
| SP6-12 | Criar testes de S09 e S10                                         | QA          | IA, ED   | 5          | SP6-01 a SP6-11 | Suíte automatizada                       |

**Estimativa total:** 65 pontos.

A sprint excede a capacidade de referência. Recomenda-se uma das seguintes opções:

* ampliar temporariamente a equipe;

* antecipar SP6-01 e SP6-07 na Sprint 5;

* mover SP6-06 e SP6-11 para o início da Sprint 7;

* dividir a sprint em duas iterações menores.

Para preservar sete sprints, a recomendação é antecipar SP6-01 e SP6-07 na Sprint 5 e transferir SP6-11 para a Sprint 7. A carga líquida da Sprint 6 fica em aproximadamente 52 pontos.

### 11.3 Riscos da sprint

| Risco                                                      | Probabilidade | Impacto | Resposta                                                             |
| ---------------------------------------------------------- | ------------- | ------- | -------------------------------------------------------------------- |
| Agente afirmar causalidade entre entrega e resultado-chave | Alta          | Alto    | Utilizar linguagem de contribuição plausível e exigir justificativa. |
| Resultado-chave ser confundido com atividade               | Alta          | Alto    | Aplicar classificador e testes contrastivos.                         |
| Entregas obrigatórias serem tratadas como desalinhadas     | Média         | Médio   | Permitir justificativa operacional ou normativa.                     |
| Risco e impedimento apresentarem sobreposição              | Alta          | Médio   | Usar critério temporal: futuro incerto versus problema atual.        |
| Matriz de risco ser interpretada como decisão automática   | Média         | Alto    | Tornar escalas configuráveis e preservar decisão humana.             |
| Dependências sem responsável permanecerem invisíveis       | Média         | Alto    | Campo obrigatório ou alerta de incompletude.                         |

### 11.4 Critérios de conclusão

1. Objetivos, KRs, entregas e atividades possuírem entidades distintas.

2. Relações muitos-para-muitos serem preservadas.

3. Cada vínculo possuir justificativa e intensidade.

4. O sistema identificar KRs sem entregas.

5. Entregas sem vínculo estratégico permitirem justificativa operacional.

6. O agente não afirmar causalidade sem evidência.

7. Riscos possuírem causa, evento e impacto.

8. Impedimentos serem diferenciados de riscos futuros.

9. Dependências possuírem origem, responsável e data necessária.

10. Restrições serem diferenciadas de eventos incertos.

11. Riscos poderem ser relacionados a prazo, meta e capacidade.

12. Métricas iniciais de classificação S09 e S10 serem calculadas.

---

## 12. Sprint 7 — Integração, Piloto e Avaliação Acadêmica

### 12.1 Objetivo

Integrar as dez skills, executar testes ponta a ponta, preparar o conjunto de avaliação e realizar o estudo-piloto.

### 12.2 Backlog da sprint

| ID     | Tarefa técnica                                  | Responsável | Apoio      | Estimativa | Dependência     | Entregável                           |
| ------ | ----------------------------------------------- | ----------- | ---------- | ---------- | --------------- | ------------------------------------ |
| SP7-01 | Implementar orquestrador do fluxo S01–S10       | ARQ         | BE, IA     | 8          | Todas           | Fluxo integrado                      |
| SP7-02 | Implementar persistência de estado entre skills | BE          | ARQ        | 5          | SP7-01          | Continuidade dos objetos             |
| SP7-03 | Implementar painel de rastreabilidade           | FE          | BE, UX     | 5          | SP7-02          | Fontes, regras, confiança e decisões |
| SP7-04 | Executar testes de integração INT-T01 a INT-T08 | QA          | Todos      | 8          | SP7-01          | Relatório de integração              |
| SP7-05 | Executar testes de segurança e privacidade      | DEVSEC      | QA, PO     | 5          | Fluxo integrado | Relatório de segurança               |
| SP7-06 | Consolidar padrão-ouro                          | ED          | DA, PO     | 5          | Bases anotadas  | Conjunto validado                    |
| SP7-07 | Congelar conjunto de teste final                | DA          | ED, PO     | 3          | SP7-06          | Versão imutável                      |
| SP7-08 | Implementar captura de métricas experimentais   | DA          | BE, IA     | 5          | SP7-01          | Logs de tempo, erros e intervenções  |
| SP7-09 | Preparar instrumento de usabilidade e confiança | UX          | DA, PO     | 3          | Nenhuma         | Questionários e roteiro              |
| SP7-10 | Executar estudo-piloto                          | PO          | UX, DA, ED | 8          | SP7-04 a SP7-09 | Dados do piloto                      |
| SP7-11 | Corrigir defeitos críticos do piloto            | BE          | IA, FE, QA | 8          | SP7-10          | Versão candidata do MVP              |
| SP7-12 | Elaborar documentação de reprodução             | ARQ         | DA, DEVSEC | 5          | SP7-10          | Guia técnico e científico            |

**Estimativa total:** 68 pontos.

A Sprint 7 também excede a capacidade de referência. Para mantê-la em duas semanas:

* SP7-06, SP7-07 e SP7-09 devem começar durante as sprints anteriores;

* o piloto deve ter escopo reduzido;

* apenas defeitos críticos e altos devem ser corrigidos;

* ajustes de menor gravidade devem compor backlog pós-MVP.

Com essas antecipações, a carga operacional da Sprint 7 fica próxima de 50 pontos.

### 12.3 Riscos da sprint

| Risco                                                     | Probabilidade | Impacto | Resposta                                                      |
| --------------------------------------------------------- | ------------- | ------- | ------------------------------------------------------------- |
| Integrações revelarem incompatibilidades de dados         | Alta          | Alto    | Contratos definidos desde a Sprint 1 e testes progressivos.   |
| Conjunto de teste sofrer vazamento para o desenvolvimento | Média         | Alto    | Congelamento, acesso restrito e registro de uso.              |
| Piloto possuir poucos participantes                       | Média         | Médio   | Tratar resultados como exploratórios e registrar limitações.  |
| Logs não permitirem reprodução                            | Média         | Alto    | Validar reprodução antes do piloto.                           |
| Usuários aceitarem sugestões sem revisão                  | Média         | Alto    | Interface deve destacar confiança e necessidade de validação. |
| Correções do piloto ampliarem indevidamente o escopo      | Alta          | Médio   | Corrigir apenas severidades crítica e alta.                   |

### 12.4 Critérios de conclusão

---

1. Um caso completo percorrer S01–S10 sem perda de identificadores.

2. Fontes e regras permanecerem rastreáveis.

3. Alterações humanas e sugestões automáticas estarem separadas.

4. Testes INT-T01 a INT-T08 estarem aprovados.

5. Defeitos críticos estarem encerrados.

6. O conjunto de teste estar congelado.

7. O padrão-ouro estar validado por pelo menos dois especialistas.

8. Métricas de classificação, extração e auditoria estarem calculadas.

9. O estudo-piloto estar concluído.

10. Dados de pesquisa estarem anonimizados.

11. A execução poder ser reproduzida a partir dos logs.

12. Documentação técnica e acadêmica estar publicada internamente.

---

## 13. Backlog transversal

As tarefas abaixo atravessam várias sprints e não devem ser tratadas como trabalho apenas da Sprint 7.

| ID    | Tarefa transversal                      | Responsável | Frequência                  |
| ----- | --------------------------------------- | ----------- | --------------------------- |
| BT-01 | Atualizar matriz de riscos do projeto   | PO          | Semanal                     |
| BT-02 | Revisar decisões arquiteturais          | ARQ         | A cada sprint               |
| BT-03 | Atualizar conjunto de regressão         | QA          | A cada defeito relevante    |
| BT-04 | Realizar validação de domínio           | ED          | A cada incremento funcional |
| BT-05 | Medir desempenho dos classificadores    | DA          | A cada nova versão          |
| BT-06 | Revisar segurança e permissões          | DEVSEC      | A cada nova fonte de dados  |
| BT-07 | Testar fluxos com usuários              | UX          | A partir da Sprint 2        |
| BT-08 | Atualizar documentação de regras        | ED          | Sempre que houver alteração |
| BT-09 | Monitorar custos e desempenho do modelo | IA          | Semanal                     |
| BT-10 | Registrar limitações e hipóteses        | PO          | Contínuo                    |

---

## 14. Definição de pronto para histórias

Uma história de usuário estará pronta para desenvolvimento quando:

1. O objetivo de negócio estiver definido.

2. O perfil usuário estiver identificado.

3. As entradas e saídas estiverem documentadas.

4. As regras funcionais estiverem validadas pelo ED.

5. Os critérios de aceitação estiverem testáveis.

6. As dependências estiverem disponíveis.

7. Questões de segurança e privacidade estiverem avaliadas.

8. Os dados de teste estiverem disponíveis.

9. A estimativa estiver acordada pela equipe.

10. Não houver decisão normativa pendente que impeça a implementação.

---

## 15. Definição global de concluído

Uma tarefa ou história será considerada concluída quando:

1. O código estiver revisado.

2. Testes unitários estiverem aprovados.

3. Testes funcionais aplicáveis estiverem aprovados.

4. Os critérios de aceitação estiverem demonstrados.

5. A documentação técnica estiver atualizada.

6. Os contratos de entrada e saída estiverem publicados.

7. Logs e rastreabilidade estiverem implementados.

8. Erros não forem ocultados.

9. Dados ausentes não forem inventados.

10. A saída diferenciar regra, recomendação, inferência e dúvida.

11. A validação de domínio estiver registrada.

12. Não houver defeito crítico ou alto aberto.

13. A funcionalidade estiver disponível no ambiente de homologação.

14. A métrica acadêmica correspondente puder ser coletada.

---

## 16. Critérios de priorização de defeitos

| Severidade | Definição                                                                      | Tratamento                               |
| ---------- | ------------------------------------------------------------------------------ | ---------------------------------------- |
| Crítica    | Viola regra, expõe dado, perde histórico ou produz decisão automática indevida | Corrigir antes da continuidade do piloto |
| Alta       | Produz classificação ou cálculo incorreto em função central                    | Corrigir dentro da sprint                |
| Média      | Afeta usabilidade ou casos secundários                                         | Planejar na sprint seguinte              |
| Baixa      | Ajuste visual, textual ou melhoria não bloqueante                              | Backlog pós-MVP                          |

---

## 17. Matriz consolidada de riscos de implementação

| ID  | Risco                                            | Skills afetadas | Probabilidade | Impacto | Responsável | Resposta                             |
| --- | ------------------------------------------------ | --------------- | ------------- | ------- | ----------- | ------------------------------------ |
| R01 | Confusão entre norma e recomendação              | S01, S02        | Alta          | Alto    | ED          | Classificação obrigatória e fonte    |
| R02 | Alucinação de regras ou entregas                 | S02, S03        | Média         | Alto    | IA          | Rastreabilidade e baixa confiança    |
| R03 | Catálogo gerar padronização excessiva            | S04             | Média         | Médio   | PO          | Permitir adaptação local             |
| R04 | Meta confundir esforço e resultado               | S05             | Alta          | Alto    | ED          | Validador específico                 |
| R05 | Auditoria gerar excesso de alertas               | S06             | Média         | Alto    | IA          | Gravidade e limiar configurável      |
| R06 | Estimativas de capacidade serem imprecisas       | S07             | Alta          | Médio   | PO          | Faixas e cenários                    |
| R07 | Dados individuais serem expostos                 | S07, S08        | Média         | Alto    | DEVSEC      | Perfis e agregação                   |
| R08 | OKR-D afirmar causalidade indevida               | S09             | Alta          | Alto    | ED          | Linguagem de contribuição            |
| R09 | Risco e impedimento serem confundidos            | S10             | Alta          | Médio   | IA          | Critério temporal explícito          |
| R10 | Integrações perderem histórico                   | Todas           | Média         | Alto    | ARQ         | IDs persistentes e versionamento     |
| R11 | Conjunto de avaliação contaminar treinamento     | Todas           | Média         | Alto    | DA          | Separação e controle de acesso       |
| R12 | Participantes confiarem excessivamente no agente | Todas           | Média         | Alto    | UX          | Confiança, justificativa e validação |
| R13 | Volume de documentos comprometer desempenho      | S01, S02, S04   | Média         | Médio   | ARQ         | Indexação e testes de carga          |
| R14 | Escopo ultrapassar sete sprints                  | Todas           | Alta          | Alto    | PO          | Controle rígido do MVP               |

---

## 18. Marcos de controle

| Marco                                       | Final da sprint | Evidência                                |
| ------------------------------------------- | --------------- | ---------------------------------------- |
| M1 — Fundação pronta                        | 1               | Modelo de dados, S01 e segurança inicial |
| M2 — Extração validável                     | 2               | S02 e S03 operacionais                   |
| M3 — Entrega mensurável                     | 3               | S04 e S05 integradas                     |
| M4 — Plano auditável                        | 4               | S06 operacional                          |
| M5 — Plano viável                           | 5               | S07 e S08 integradas                     |
| M6 — Plano alinhado e consciente dos riscos | 6               | S09 e S10 operacionais                   |
| M7 — MVP avaliado                           | 7               | Fluxo integrado, piloto e métricas       |

---

## 19. Métricas acompanhadas por sprint

| Sprint | Métricas mínimas                                                   |
| ------ | ------------------------------------------------------------------ |
| 1      | Regras com fonte; conflitos detectados; alterações rastreadas      |
| 2      | Macro-F1 da classificação; precisão de não conformidades           |
| 3      | Precision@k da busca; metas mensuráveis; critérios verificáveis    |
| 4      | Precisão de duplicidades; recall de problemas críticos             |
| 5      | Exatidão dos cálculos; sobrealocações e lacunas detectadas         |
| 6      | Concordância OKR-D; F1 de risco/impedimento/dependência/restrição  |
| 7      | Qualidade geral, tempo, usabilidade, confiança e reprodutibilidade |

---

## 20. Escopo excluído do MVP

Para evitar expansão indevida, ficam fora do MVP:

* pactuação formal dos planos;

* assinatura eletrônica;

* monitoramento periódico de execução;

* replanejamento e controle de alterações durante o ciclo;

* avaliação final das entregas;

* gestão completa de evidências;

* relatórios gerenciais institucionais definitivos;

* integração produtiva com sistemas corporativos;

* aprendizado automatizado entre ciclos;

* decisões automáticas sobre aprovação, priorização ou avaliação de pessoas.

Esses itens podem ser simulados apenas quando necessários à avaliação das dez skills.

---

## 21. Resultado esperado ao final

Ao final das sete sprints, o MVP deverá ser capaz de:

1. Carregar e versionar fontes institucionais.

2. Diferenciar normas, regras, recomendações e exemplos.

3. Verificar conformidade com rastreabilidade.

4. Extrair entregas candidatas de competências e atividades.

5. Pesquisar e versionar entregas em catálogo.

6. Definir metas e critérios de aceite.

7. Auditar um portfólio.

8. Analisar capacidade da unidade.

9. Verificar cobertura das entregas pela equipe.

10. Criar e auditar encadeamentos OKR-D.

11. Estruturar riscos, impedimentos, dependências e restrições.

12. Registrar confiança, fontes e decisões humanas.

13. Produzir dados reprodutíveis para avaliação acadêmica.
