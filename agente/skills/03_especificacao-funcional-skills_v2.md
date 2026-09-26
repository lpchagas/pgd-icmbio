Especificação funcional do MVP do Assistente de PGD do ICMBio
=========================================================================

---

## 1. Escopo atualizado do MVP

O MVP passa a ser composto pelas seguintes dez skills:

| Código | Skill                                                    | Prioridade |
| ------ | -------------------------------------------------------- | ---------- |
| S01    | Configurador Institucional do PGD                        | P0         |
| S02    | Verificador Normativo e de Conformidade                  | P0         |
| S03    | Extrator de Competências e Responsabilidades em Entregas | P0         |
| S04    | Administrador do Catálogo de Entregas                    | P0         |
| S05    | Designer de Metas, Indicadores e Critérios de Aceite     | P1         |
| S06    | Auditor de Portfólio de Entregas                         | P1         |
| S07    | Planejador de Capacidade da Unidade                      | P1         |
| S08    | Matriz de Cobertura das Entregas pela Equipe             | P1         |
| S09    | Designer e Auditor de Encadeamento OKR-D                 | P1         |
| S10    | Analisador de Riscos, Dependências e Restrições          | P1         |

O fluxo funcional do MVP será:

> Documentos institucionais  
> → regras e vocabulário institucional  
> → competências da unidade  
> → entregas candidatas  
> → catálogo de referência  
> → metas e critérios de aceite  
> → auditoria do portfólio  
> → análise de capacidade  
> → distribuição da cobertura pela equipe  
> → encadeamento OKR-D  
> → análise de riscos e dependências.

* * *

## 2. Objetivo geral do MVP

Desenvolver e avaliar um agente especializado capaz de apoiar unidades do ICMBio na transformação de competências, responsabilidades e objetivos institucionais em planos de entregas:

* conceitualmente corretos;

* mensuráveis;

* institucionalmente alinhados;

* compatíveis com a capacidade da equipe;

* vinculados à estratégia;

* acompanhados de riscos, dependências e critérios de aceite;

* rastreáveis até as fontes utilizadas.

Os requisitos de arquitetura, métricas e limiares de desempenho descritos a seguir são propostas de projeto e avaliação acadêmica. Eles não devem ser interpretados como regras normativas do PGD ou do ICMBio.

* * *

## 3. Perfis de usuário

| Código | Perfil                       | Necessidade principal                                           |
| ------ | ---------------------------- | --------------------------------------------------------------- |
| P01    | Chefe de Unidade de Execução | Elaborar, revisar e pactuar o plano de entregas da unidade.     |
| P02    | Integrante da equipe         | Compreender as entregas e planejar sua contribuição.            |
| P03    | Unidade superior             | Avaliar a consistência, a capacidade e o alinhamento do plano.  |
| P04    | Unidade de gestão do PGD     | Orientar, monitorar conformidade e consolidar informações.      |
| P05    | Administrador institucional  | Configurar regras, fontes, estrutura e vocabulário do agente.   |
| P06    | Pesquisador ou avaliador     | Executar experimentos, comparar resultados e analisar métricas. |
| P07    | Especialista de domínio      | Validar respostas do agente e compor o padrão-ouro acadêmico.   |

* * *

## 4. Convenções para implementação

### 4.1 Formato das histórias de usuário

Cada história seguirá o padrão:

> Como [perfil], quero [funcionalidade], para [resultado esperado].

### 4.2 Formato dos critérios de aceitação

Os critérios utilizarão a estrutura:

> Dado [contexto], quando [ação], então [resultado verificável].

### 4.3 Tipos de teste

| Tipo            | Finalidade                                                      |
| --------------- | --------------------------------------------------------------- |
| Positivo        | Confirma o funcionamento com entrada válida.                    |
| Negativo        | Verifica rejeição ou tratamento de entrada inválida.            |
| Ambiguidade     | Verifica atuação quando os dados não permitem conclusão segura. |
| Limite          | Verifica valores extremos, campos vazios ou grandes volumes.    |
| Integração      | Verifica troca de dados entre skills.                           |
| Regressão       | Garante que alterações não modifiquem regras já validadas.      |
| Explicabilidade | Verifica se a saída apresenta justificativas e fontes.          |
| Segurança       | Verifica controle de acesso e tratamento de dados sensíveis.    |

* * *

## 5. Modelo mínimo de dados

### 5.1 Regra institucional

| Campo              | Tipo                                                | Obrigatório      |
| ------------------ | --------------------------------------------------- | ---------------- |
| rule_id            | Identificador                                       | Sim              |
| titulo             | Texto                                               | Sim              |
| descricao          | Texto                                               | Sim              |
| natureza           | Norma, regra institucional, recomendação ou exemplo | Sim              |
| fonte              | Documento e localização                             | Sim              |
| inicio_vigencia    | Data                                                | Quando aplicável |
| fim_vigencia       | Data                                                | Quando aplicável |
| status             | Vigente, revogada, conflitante ou pendente          | Sim              |
| confianca_extracao | Número ou categoria                                 | Sim              |
| validacao_humana   | Estado                                              | Sim              |

### 5.2 Entrega candidata

| Campo               | Tipo                                                     | Obrigatório                     |
| ------------------- | -------------------------------------------------------- | ------------------------------- |
| candidate_id        | Identificador                                            | Sim                             |
| texto_origem        | Texto                                                    | Sim                             |
| fonte_origem        | Documento e localização                                  | Sim                             |
| classificacao       | Entrega, objetivo, atividade, tarefa ou responsabilidade | Sim                             |
| titulo_sugerido     | Texto                                                    | Quando houver entrega candidata |
| justificativa       | Texto                                                    | Sim                             |
| confianca           | Alta, média ou baixa                                     | Sim                             |
| perguntas_pendentes | Lista                                                    | Quando houver ambiguidade       |

### 5.3 Entrega estruturada

| Campo                 | Tipo                           | Obrigatório        |
| --------------------- | ------------------------------ | ------------------ |
| delivery_id           | Identificador                  | Sim                |
| titulo                | Texto                          | Sim                |
| descricao             | Texto                          | Quando necessária  |
| forma_geracao         | Projeto ou processo            | Sim                |
| natureza_resultado    | Produto ou serviço             | Sim                |
| demandante            | Texto ou referência            | Sim                |
| destinatario          | Texto ou referência            | Sim                |
| meta                  | Objeto estruturado             | Sim                |
| prazo                 | Data ou período                | Sim                |
| progresso_esperado    | Percentual, marco ou descrição | Quando aplicável   |
| criterios_aceite      | Lista                          | Recomendado no MVP |
| evidencias_esperadas  | Lista                          | Recomendado no MVP |
| vinculos_estrategicos | Lista                          | Quando aplicável   |
| riscos                | Lista                          | Quando aplicável   |
| versao                | Número                         | Sim                |

### 5.4 Plano de capacidade

| Campo                    | Tipo                |
| ------------------------ | ------------------- |
| unidade                  | Referência          |
| periodo                  | Intervalo           |
| participantes            | Lista               |
| capacidade_nominal       | Horas               |
| indisponibilidades       | Horas e motivos     |
| capacidade_util          | Horas               |
| atividades_indiretas     | Horas ou percentual |
| capacidade_para_entregas | Horas               |
| demanda_estimada         | Horas ou faixas     |
| deficit_ou_folga         | Horas ou percentual |

### 5.5 Vínculo OKR-D

| Campo                 | Tipo                           |
| --------------------- | ------------------------------ |
| objective_id          | Referência                     |
| key_result_id         | Referência                     |
| delivery_id           | Referência                     |
| contribution_type     | Direta, indireta ou contextual |
| contribution_strength | Alta, média ou baixa           |
| justificativa         | Texto                          |
| evidencia_logica      | Texto ou referência            |
| validacao_humana      | Estado                         |

### 5.6 Registro de risco

| Campo         | Tipo                                         |
| ------------- | -------------------------------------------- |
| risk_id       | Identificador                                |
| delivery_id   | Referência                                   |
| tipo          | Risco, impedimento, dependência ou restrição |
| causa         | Texto                                        |
| evento        | Texto                                        |
| impacto       | Texto                                        |
| probabilidade | Escala                                       |
| severidade    | Escala                                       |
| resposta      | Texto                                        |
| responsavel   | Referência                                   |
| prazo_revisao | Data                                         |
| status        | Estado                                       |

* * *

## 6. Skill S01 — Configurador Institucional do PGD

### 6.1 Objetivo funcional

Criar e manter uma configuração institucional versionada, capaz de orientar todas as demais skills.

### 6.2 Histórias de usuário

#### S01-US01 — Importar fontes institucionais

Como administrador institucional, quero cadastrar documentos, regras e estruturas do ICMBio para que o agente utilize fontes identificadas e controladas.

**Critérios de aceitação**

1. Dado um documento válido, quando ele for cadastrado, então o sistema deve registrar título, versão, data, origem e responsável pela inclusão.

2. Dado um documento sem identificação de versão, quando ele for cadastrado, então o sistema deve marcar a versão como pendente de validação.

3. Dado um documento duplicado, quando ele for enviado, então o sistema deve alertar sobre a possível duplicidade.

4. Dado um documento substituído, quando a nova versão for aprovada, então a versão anterior deve permanecer no histórico.

#### S01-US02 — Classificar regras institucionais

Como gestor do PGD, quero que as orientações sejam classificadas segundo sua natureza para evitar que recomendações sejam apresentadas como obrigações.

**Critérios de aceitação**

1. Toda regra deve ser classificada como norma, regra institucional, recomendação ou exemplo.

2. Toda regra deve possuir referência à fonte.

3. Regras conflitantes devem ser marcadas para decisão humana.

4. O sistema não deve resolver conflitos normativos sem autorização.

#### S01-US03 — Configurar estrutura e papéis

Como administrador institucional, quero registrar unidades, níveis hierárquicos e papéis de aprovação para que o agente reconheça responsabilidades organizacionais.

**Critérios de aceitação**

1. Uma unidade deve possuir identificador único.

2. Relações hierárquicas circulares devem ser rejeitadas.

3. Uma unidade só deve ser tratada como UE quando configurada ou validada para essa finalidade.

4. Papéis de aprovação devem ser associados a unidade, perfil ou instância.

### 6.3 Casos de teste detalhados

| ID      | Cenário                         | Pré-condição                       | Entrada                                  | Resultado esperado                                            |
| ------- | ------------------------------- | ---------------------------------- | ---------------------------------------- | ------------------------------------------------------------- |
| S01-T01 | Cadastro válido                 | Usuário autorizado                 | Documento com metadados completos        | Documento cadastrado, versionado e disponível para consulta.  |
| S01-T02 | Fonte sem versão                | Usuário autorizado                 | Documento sem número ou data de versão   | Cadastro permitido com alerta “versão não confirmada”.        |
| S01-T03 | Conflito de regras              | Duas fontes cadastradas            | Regras incompatíveis sobre o mesmo campo | Conflito registrado; nenhuma regra escolhida automaticamente. |
| S01-T04 | Recomendação tratada como norma | Regra cadastrada como recomendação | Solicitação de verificação               | Saída deve usar “recomendado”, não “obrigatório”.             |
| S01-T05 | Hierarquia circular             | Unidades A e B existentes          | A subordinada a B e B subordinada a A    | Operação rejeitada e inconsistência explicada.                |
| S01-T06 | Acesso indevido                 | Usuário sem permissão              | Alteração de regra vigente               | Alteração bloqueada e evento registrado em log.               |

### 6.4 Métricas acadêmicas específicas

* precisão da classificação da natureza das regras;

* percentual de regras com fonte corretamente associada;

* taxa de conflitos corretamente detectados;

* taxa de decisões indevidas tomadas sem validação humana;

* concordância entre especialistas sobre a classificação.

* * *

## 7. Skill S02 — Verificador Normativo e de Conformidade

### 7.1 Objetivo funcional

Comparar entregas e planos com as regras institucionais vigentes, distinguindo não conformidades de recomendações.

### 7.2 Histórias de usuário

#### S02-US01 — Verificar uma entrega

Como chefe de unidade, quero verificar uma entrega antes de incluí-la no plano para corrigir campos obrigatórios ausentes.

**Critérios de aceitação**

1. A verificação deve identificar campos ausentes.

2. Cada não conformidade deve apontar a fonte aplicável.

3. A saída deve distinguir erro, alerta e recomendação.

4. A correção sugerida não deve modificar silenciosamente a entrada.

#### S02-US02 — Verificar um plano completo

Como unidade superior, quero analisar a conformidade do plano para apoiar sua aprovação.

**Critérios de aceitação**

1. O relatório deve apresentar visão consolidada e detalhamento por entrega.

2. Regras vigentes no período do plano devem ser utilizadas.

3. Dados ausentes devem ser diferenciados de dados em desacordo.

4. O sistema deve informar quando não possui fonte suficiente para concluir.

#### S02-US03 — Reavaliar plano histórico

Como pesquisador, quero aplicar as regras vigentes na época do plano para evitar análise anacrônica.

**Critérios de aceitação**

1. A data do plano deve determinar o conjunto de regras utilizado.

2. A saída deve registrar a versão normativa aplicada.

3. Regras posteriores não devem gerar não conformidade retroativa.

### 7.3 Casos de teste detalhados

| ID      | Cenário                            | Entrada                          | Resultado esperado                                              |
| ------- | ---------------------------------- | -------------------------------- | --------------------------------------------------------------- |
| S02-T01 | Campo obrigatório ausente          | Entrega sem destinatário         | Não conformidade com campo, fonte e correção sugerida.          |
| S02-T02 | Título fora do padrão preferencial | Título claro, mas sem particípio | Recomendação de redação, salvo regra institucional obrigatória. |
| S02-T03 | Falta de fonte                     | Regra não cadastrada             | Sistema informa impossibilidade de confirmação normativa.       |
| S02-T04 | Plano histórico                    | Plano de período anterior        | Aplicação das regras vigentes naquele período.                  |
| S02-T05 | Dados incompletos                  | Meta não informada               | Classificação “informação ausente”, não “meta inválida”.        |
| S02-T06 | Integração com S01                 | Regra revogada no configurador   | Regra não utilizada em plano posterior à revogação.             |

### 7.4 Métricas acadêmicas específicas

* precisão e revocação na identificação de não conformidades;

* taxa de falsos positivos normativos;

* percentual de apontamentos com fonte correta;

* qualidade da explicação avaliada por especialistas;

* tempo médio para revisão de um plano.

* * *

## 8. Skill S03 — Extrator de Competências e Responsabilidades em Entregas

### 8.1 Objetivo funcional

Identificar produtos e serviços candidatos a partir de competências, responsabilidades, processos e listas de atividades.

### 8.2 Histórias de usuário

#### S03-US01 — Extrair entregas candidatas

Como chefe de unidade, quero transformar as competências da unidade em entregas candidatas para iniciar o plano.

**Critérios de aceitação**

1. Cada candidata deve manter vínculo com o trecho de origem.

2. O sistema deve classificar o trecho como objetivo, entrega, atividade, tarefa ou responsabilidade.

3. Uma entrega candidata deve possuir produto ou serviço identificável.

4. Ambiguidades devem gerar perguntas de validação.

#### S03-US02 — Transformar atividades em resultados

Como integrante da equipe, quero informar uma lista de atividades e receber perguntas que ajudem a identificar os resultados gerados.

**Critérios de aceitação**

1. O sistema não deve converter automaticamente toda atividade em entrega.

2. Deve perguntar o que existirá ao final do trabalho.

3. Deve sugerir título somente quando houver produto ou serviço plausível.

4. A confiança da sugestão deve ser informada.

#### S03-US03 — Revisar candidatas em lote

Como gestor do PGD, quero revisar várias candidatas para aprovar, rejeitar, agrupar ou solicitar ajustes.

**Critérios de aceitação**

1. Cada candidata deve possuir estado próprio.

2. A rejeição deve permitir justificativa.

3. Candidatas semelhantes devem ser sinalizadas.

4. A aprovação deve gerar objeto compatível com S04 e S05.

### 8.3 Casos de teste detalhados

| ID      | Cenário                       | Entrada                                    | Resultado esperado                                                                |
| ------- | ----------------------------- | ------------------------------------------ | --------------------------------------------------------------------------------- |
| S03-T01 | Competência com produto claro | “Elaborar relatórios de monitoramento”     | Candidata “Relatórios de monitoramento elaborados”, com fonte.                    |
| S03-T02 | Atividade sem produto         | “Participar de reuniões”                   | Classificação como atividade e pergunta sobre o resultado.                        |
| S03-T03 | Objetivo genérico             | “Melhorar a conservação da biodiversidade” | Classificação como objetivo, sem conversão direta em entrega.                     |
| S03-T04 | Responsabilidade ampla        | “Coordenar as ações da unidade”            | Classificação como responsabilidade; solicitação de produtos ou serviços gerados. |
| S03-T05 | Texto ambíguo                 | “Apoiar as unidades”                       | Confiança baixa e perguntas sobre forma, destinatário e evidência.                |
| S03-T06 | Integração com S04            | Candidata aprovada                         | Registro enviado ao catálogo com identificador e origem.                          |

### 8.4 Métricas acadêmicas específicas

* macro-F1 da classificação objetivo/entrega/atividade/tarefa/responsabilidade;

* precisão das entregas candidatas;

* taxa de candidatas aceitas pelos especialistas;

* qualidade dos títulos em escala de clareza, verificabilidade e relevância;

* redução do tempo para levantamento inicial do portfólio.

* * *

## S04 — Administrador do Catálogo de Entregas

### 9.1 Objetivo funcional

Manter uma biblioteca institucional versionada de entregas, descrições, metas e exemplos de referência.

### 9.2 Histórias de usuário

#### S04-US01 — Pesquisar entregas de referência

Como chefe de unidade, quero pesquisar entregas semelhantes para aproveitar exemplos sem perder as particularidades da unidade.

**Critérios de aceitação**

1. A busca deve considerar título, descrição, processo, unidade e destinatário.

2. Os resultados devem informar grau de similaridade.

3. O usuário deve poder adaptar os campos.

4. O uso do modelo deve registrar a referência de origem.

#### S04-US02 — Cadastrar e versionar entrega

Como administrador do catálogo, quero publicar uma entrega validada para reutilização institucional.

**Critérios de aceitação**

1. A entrega deve possuir identificador único.

2. Alterações relevantes devem gerar nova versão.

3. A versão anterior deve permanecer consultável.

4. A publicação deve exigir validação humana.

#### S04-US03 — Detectar duplicidades

Como gestor do catálogo, quero identificar entradas semelhantes para reduzir redundância e inconsistência terminológica.

**Critérios de aceitação**

1. Possíveis duplicidades devem ser apresentadas antes da publicação.

2. O sistema deve explicar a semelhança detectada.

3. O usuário deve poder manter entradas distintas mediante justificativa.

4. A consolidação não deve apagar históricos.

### 9.3 Casos de teste detalhados

| ID      | Cenário                  | Entrada                            | Resultado esperado                                     |
| ------- | ------------------------ | ---------------------------------- | ------------------------------------------------------ |
| S04-T01 | Busca exata              | Título existente                   | Registro correto no primeiro grupo de resultados.      |
| S04-T02 | Busca semântica          | Título com sinônimos               | Entregas relacionadas apresentadas com similaridade.   |
| S04-T03 | Duplicidade provável     | Novo título muito semelhante       | Alerta antes da publicação.                            |
| S04-T04 | Versão nova              | Alteração de descrição e aceite    | Nova versão criada; anterior preservada.               |
| S04-T05 | Adaptação local          | Modelo utilizado por outra unidade | Campos 4Q1P editáveis; referência original preservada. |
| S04-T06 | Publicação sem aprovação | Usuário sem perfil autorizado      | Registro permanece como rascunho.                      |

### 9.4 Métricas acadêmicas específicas

* precisão das sugestões de similaridade;

* taxa de duplicidades identificadas;

* percentual de sugestões consideradas úteis;

* redução da variação terminológica;

* taxa de reutilização de modelos.

* * *

## 10. Skill S05 — Designer de Metas, Indicadores e Critérios de Aceite

### 10.1 Objetivo funcional

Transformar uma entrega validada em resultado mensurável e verificável.

### 10.2 Histórias de usuário

#### S05-US01 — Definir meta para entrega de projeto

Como chefe de unidade, quero definir a meta final de uma entrega de projeto sem confundi-la com o progresso do ciclo.

**Critérios de aceitação**

1. A meta final deve representar a conclusão da entrega.

2. O progresso esperado deve ser armazenado separadamente.

3. Marcos intermediários devem possuir condição verificável.

4. Percentuais subjetivos devem ser identificados como estimativas.

#### S05-US02 — Definir meta para processo contínuo

Como gestor, quero estabelecer volume e desempenho para entregas recorrentes.

**Critérios de aceitação**

1. A meta deve possuir unidade de medida.

2. Prazo, qualidade ou nível de serviço podem complementar o volume.

3. Deve existir fonte de dados.

4. A meta deve ser compatível com a vigência.

#### S05-US03 — Definir critérios de aceite

Como demandante, quero explicitar como a entrega será aceita para reduzir interpretações divergentes.

**Critérios de aceitação**

1. Cada critério deve ser verificável.

2. O responsável pelo aceite deve ser identificável.

3. As evidências esperadas devem ser registradas.

4. Critérios vagos devem gerar solicitação de detalhamento.

### 10.3 Casos de teste detalhados

| ID      | Cenário                           | Entrada                           | Resultado esperado                                                            |
| ------- | --------------------------------- | --------------------------------- | ----------------------------------------------------------------------------- |
| S05-T01 | Projeto concluído após a vigência | Sistema com prazo final posterior | Meta final e progresso esperado registrados separadamente.                    |
| S05-T02 | Processo recorrente               | Pareceres emitidos                | Sugestão de quantidade, prazo médio e conformidade.                           |
| S05-T03 | Meta vaga                         | “Atender bem às demandas”         | Rejeição como não mensurável e perguntas de refinamento.                      |
| S05-T04 | Meta baseada em esforço           | “Realizar 100 horas de análise”   | Alerta de que esforço não comprova a entrega.                                 |
| S05-T05 | Critério subjetivo                | “Relatório com boa qualidade”     | Solicitação de critérios observáveis de completude, precisão ou conformidade. |
| S05-T06 | Evidência inexistente             | Indicador sem fonte               | Meta marcada como não verificável até definição da fonte.                     |

### 10.4 Métricas acadêmicas específicas

* percentual de metas consideradas mensuráveis por especialistas;

* concordância sobre separação entre meta e progresso esperado;

* percentual de critérios de aceite verificáveis;

* completude dos campos;

* redução de metas vagas após interação com o agente.

* * *

## 11. Skill S06 — Auditor de Portfólio de Entregas

### 11.1 Objetivo funcional

Avaliar o plano como conjunto, identificando problemas de cobertura, consistência, relevância e granularidade.

### 11.2 Histórias de usuário

#### S06-US01 — Detectar duplicidades e sobreposições

Como chefe de unidade, quero identificar entregas redundantes para simplificar o plano.

**Critérios de aceitação**

1. A auditoria deve apresentar as entregas comparadas.

2. Deve explicar os elementos de sobreposição.

3. Não deve consolidar registros sem aprovação.

4. Deve permitir justificativa para manutenção separada.

#### S06-US02 — Verificar cobertura das competências

Como unidade superior, quero saber se o plano representa as principais responsabilidades da unidade.

**Critérios de aceitação**

1. A auditoria deve comparar o plano com fontes institucionais.

2. Competências sem entrega relacionada devem aparecer como possível lacuna.

3. A ausência pode ser justificada.

4. A análise deve diferenciar competência permanente e prioridade do ciclo.

#### S06-US03 — Analisar granularidade e relevância

Como gestor, quero localizar entregas amplas demais ou pequenas demais para melhorar o acompanhamento.

**Critérios de aceitação**

1. A análise deve apresentar justificativa para dividir ou agrupar.

2. Atividades instrumentais devem ser sinalizadas.

3. Entregas amplas devem ser avaliadas quanto a marcos e critérios de conclusão.

4. A decisão final deve permanecer gerencial.

### 11.3 Casos de teste detalhados

| ID      | Cenário                      | Entrada                              | Resultado esperado                                           |
| ------- | ---------------------------- | ------------------------------------ | ------------------------------------------------------------ |
| S06-T01 | Duplicidade lexical          | Dois títulos quase idênticos         | Possível duplicidade com justificativa.                      |
| S06-T02 | Duplicidade semântica        | Títulos diferentes e mesma descrição | Sobreposição detectada.                                      |
| S06-T03 | Atividade no portfólio       | “Realizar reuniões mensais”          | Classificação como provável atividade.                       |
| S06-T04 | Entrega excessivamente ampla | “Gestão ambiental realizada”         | Alerta de baixa verificabilidade e proposta de decomposição. |
| S06-T05 | Lacuna de competência        | Competência sem entrega vinculada    | Possível lacuna com referência à fonte.                      |
| S06-T06 | Justificativa válida         | Competência não priorizada no ciclo  | Lacuna mantida como justificada, não como erro.              |

### 11.4 Métricas acadêmicas específicas

* precisão e revocação da detecção de duplicidades;

* taxa de lacunas confirmadas por especialistas;

* concordância sobre granularidade;

* redução do número de inconsistências após revisão;

* utilidade percebida do relatório de auditoria.

* * *

## 12. Skill S07 — Planejador de Capacidade da Unidade

### 12.1 Objetivo funcional

Comparar a capacidade útil da equipe com o esforço necessário para o portfólio.

### 12.2 Histórias de usuário

#### S07-US01 — Calcular capacidade útil

Como chefe de unidade, quero descontar indisponibilidades previstas para conhecer a capacidade efetiva do período.

**Critérios de aceitação**

1. Férias, licenças e afastamentos devem reduzir a capacidade.

2. O cálculo deve ser reproduzível.

3. A capacidade nominal e a útil devem ser apresentadas separadamente.

4. Dados faltantes devem ser explicitados.

#### S07-US02 — Estimar demanda das entregas

Como equipe, quero estimar o esforço das entregas usando horas ou faixas de complexidade.

**Critérios de aceitação**

1. A estimativa deve informar seu método.

2. Intervalos devem ser aceitos quando não houver precisão.

3. A incerteza deve permanecer visível.

4. A estimativa deve ser revisável.

#### S07-US03 — Criar cenários de priorização

Como unidade superior, quero simular ajustes quando a demanda exceder a capacidade.

**Critérios de aceitação**

1. O déficit deve ser quantificado.

2. Cenários não podem alterar o plano automaticamente.

3. Cada cenário deve informar entregas afetadas.

4. Redução de escopo, prazo, meta ou prioridade devem ser apresentadas separadamente.

### 12.3 Casos de teste detalhados

| ID      | Cenário                     | Entrada                                 | Resultado esperado                                                       |
| ------- | --------------------------- | --------------------------------------- | ------------------------------------------------------------------------ |
| S07-T01 | Capacidade sem afastamentos | Equipe completa                         | Capacidade útil igual à nominal menos atividades indiretas configuradas. |
| S07-T02 | Férias parciais             | Participante ausente por parte do ciclo | Desconto proporcional correto.                                           |
| S07-T03 | Demanda superior            | Esforço maior que capacidade            | Déficit e cenários apresentados.                                         |
| S07-T04 | Estimativa em faixa         | Entrega de 80 a 120 horas               | Cenários mínimo, provável e máximo.                                      |
| S07-T05 | Competência ausente         | Horas disponíveis sem perfil técnico    | Lacuna de competência separada do déficit de horas.                      |
| S07-T06 | Soma inconsistente          | Dados individuais incompatíveis         | Erro de cálculo identificado antes da simulação.                         |

### 12.4 Métricas acadêmicas específicas

* exatidão dos cálculos;

* erro absoluto entre esforço estimado e realizado;

* utilidade dos cenários segundo gestores;

* redução de sobrealocação;

* percentual de déficits corretamente antecipados.

* * *

## 13. Skill S08 — Matriz de Cobertura das Entregas pela Equipe

### 13.1 Objetivo funcional

Consolidar contribuições individuais e verificar a cobertura das entregas da unidade.

### 13.2 Histórias de usuário

#### S08-US01 — Consolidar planos individuais

Como chefe de unidade, quero visualizar quais participantes contribuirão para cada entrega.

**Critérios de aceitação**

1. Cada contribuição deve referenciar uma entrega válida.

2. Cada plano individual deve totalizar 100%.

3. O percentual deve ser identificado como esforço.

4. Contribuições externas devem ser destacadas.

#### S08-US02 — Identificar entregas sem cobertura

Como gestor, quero localizar entregas sem pessoas ou competências suficientes.

**Critérios de aceitação**

1. Entregas sem participantes devem ser marcadas.

2. Competências necessárias devem ser comparadas com a equipe.

3. Cobertura parcial deve ser diferenciada de ausência total.

4. O alerta deve informar a causa.

#### S08-US03 — Detectar concentração e sobrealocação

Como chefe, quero identificar dependência excessiva de uma pessoa ou distribuição incompatível com as prioridades.

**Critérios de aceitação**

1. Participantes acima de 100% devem ser sinalizados.

2. Entregas dependentes de uma única pessoa devem gerar alerta.

3. A intensidade do risco deve considerar criticidade e substituição disponível.

4. O sistema não deve tratar a soma de percentuais individuais como percentual de conclusão.

### 13.3 Casos de teste detalhados

| ID      | Cenário                        | Entrada                                   | Resultado esperado                                           |
| ------- | ------------------------------ | ----------------------------------------- | ------------------------------------------------------------ |
| S08-T01 | Entrega coberta                | Dois participantes vinculados             | Matriz com participantes e respectivos esforços.             |
| S08-T02 | Entrega sem cobertura          | Nenhum plano relacionado                  | Alerta “sem cobertura”.                                      |
| S08-T03 | Plano individual acima de 100% | Soma de 110%                              | Sobrealocação identificada.                                  |
| S08-T04 | Concentração crítica           | Único especialista em entrega prioritária | Risco de concentração.                                       |
| S08-T05 | Contribuição externa           | Participante de outra UE                  | Unidade de origem e autorização exibidas.                    |
| S08-T06 | Erro conceitual                | Usuário interpreta 60% como progresso     | Sistema esclarece que o valor representa esforço individual. |

### 13.4 Métricas acadêmicas específicas

* precisão na identificação de entregas sem cobertura;

* taxa de sobrealocações detectadas;

* taxa de riscos de concentração confirmados;

* redução de inconsistências entre planos individuais e plano da unidade;

* clareza da matriz avaliada por usuários.

* * *

## 14. Skill S09 — Designer e Auditor de Encadeamento OKR-D

### 14.1 Objetivo funcional

Criar e validar relações entre objetivos, resultados-chave, entregas e atividades, preservando relações muitos-para-muitos.

### 14.2 Histórias de usuário

#### S09-US01 — Construir encadeamento a partir de objetivo e resultado-chave

Como chefe de unidade, quero identificar entregas que contribuam para um resultado-chave institucional.

**Critérios de aceitação**

1. O objetivo deve ser tratado como situação desejada.

2. O resultado-chave deve possuir medida de avanço.

3. As entregas propostas devem ser produtos ou serviços.

4. As atividades devem permanecer em camada separada.

5. Cada vínculo deve possuir justificativa.

#### S09-US02 — Auditar vínculos existentes

Como unidade superior, quero verificar se as entregas realmente contribuem para os resultados-chave informados.

**Critérios de aceitação**

1. A auditoria deve testar a plausibilidade do vínculo.

2. Contribuições diretas, indiretas e contextuais devem ser diferenciadas.

3. Entregas sem alinhamento demonstrado devem ser sinalizadas.

4. O sistema não deve afirmar causalidade comprovada apenas pela existência do vínculo.

#### S09-US03 — Identificar lacunas no encadeamento

Como gestor do planejamento, quero localizar resultados-chave sem entregas suficientes e entregas sem relação estratégica.

**Critérios de aceitação**

1. Resultados-chave sem entregas devem ser listados.

2. Entregas sem resultado-chave devem ser listadas.

3. A ausência de vínculo pode ser justificada para entregas obrigatórias ou operacionais.

4. Relações muitos-para-muitos devem ser preservadas.

#### S09-US04 — Validar a cadeia completa

Como especialista, quero testar a sequência objetivo → resultado-chave → entrega → atividade.

**Critérios de aceitação**

1. O sistema deve aplicar os testes: atividades geram a entrega; entrega contribui para o resultado-chave; resultado-chave indica avanço no objetivo.

2. Respostas negativas devem apontar o elo problemático.

3. A saída deve sugerir correção sem substituir a decisão humana.

4. A análise deve registrar grau de confiança.

### 14.3 Casos de teste detalhados

| ID      | Cenário                           | Entrada                                                          | Resultado esperado                                                    |
| ------- | --------------------------------- | ---------------------------------------------------------------- | --------------------------------------------------------------------- |
| S09-T01 | Encadeamento válido               | Objetivo, KR mensurável, entrega concreta e atividades coerentes | Cadeia validada com justificativa.                                    |
| S09-T02 | KR formulado como atividade       | “Realizar cinco reuniões”                                        | Alerta de que o KR mede atividade, não mudança ou resultado.          |
| S09-T03 | Entrega formulada como objetivo   | “Melhorar a proteção ambiental”                                  | Classificação como objetivo e solicitação do produto ou serviço.      |
| S09-T04 | Atividade registrada como entrega | “Analisar dados”                                                 | Reclassificação provável como atividade.                              |
| S09-T05 | Vínculo fraco                     | Entrega sem influência plausível no KR                           | “Alinhamento não demonstrado” ou contribuição contextual.             |
| S09-T06 | Relação muitos-para-muitos        | Uma entrega vinculada a dois KRs                                 | Dois vínculos preservados com justificativas independentes.           |
| S09-T07 | KR sem entregas                   | Resultado-chave isolado                                          | Lacuna operacional sinalizada.                                        |
| S09-T08 | Entrega obrigatória sem KR        | Entrega normativa                                                | Vínculo estratégico ausente, mas justificativa operacional permitida. |

### 14.4 Métricas acadêmicas específicas

* precisão da classificação objetivo/KR/entrega/atividade;

* concordância entre especialistas sobre a plausibilidade dos vínculos;

* percentual de vínculos aceitos sem alteração;

* taxa de lacunas corretamente identificadas;

* qualidade das justificativas;

* redução de encadeamentos inconsistentes após uso da skill.

* * *

## 15. Skill S10 — Analisador de Riscos, Dependências e Restrições

### 15.1 Objetivo funcional

Identificar e estruturar fatores que possam afetar a entrega, sua meta, prazo, qualidade ou escopo.

### 15.2 Histórias de usuário

#### S10-US01 — Registrar riscos futuros

Como responsável pela entrega, quero registrar eventos incertos que possam comprometer o resultado.

**Critérios de aceitação**

1. O risco deve possuir causa, evento e impacto.

2. Probabilidade e severidade devem seguir escala configurada.

3. O risco deve possuir responsável e data de revisão.

4. O sistema deve solicitar resposta planejada.

#### S10-US02 — Diferenciar risco de impedimento

Como chefe de unidade, quero separar problemas já existentes de eventos futuros incertos.

**Critérios de aceitação**

1. Eventos já ocorridos devem ser classificados como impedimentos.

2. Eventos futuros incertos devem ser classificados como riscos.

3. A classificação deve apresentar justificativa.

4. O usuário deve poder corrigir a classificação.

#### S10-US03 — Mapear dependências

Como gestor, quero identificar insumos, decisões e entregas externas necessárias para cumprir o plano.

**Critérios de aceitação**

1. Cada dependência deve informar origem e responsável.

2. Deve existir data em que o insumo ou decisão será necessário.

3. Dependências críticas devem ser destacadas.

4. Dependências entre entregas do próprio plano devem gerar vínculo explícito.

#### S10-US04 — Analisar restrições

Como unidade superior, quero conhecer limites fixos que condicionam a execução.

**Critérios de aceitação**

1. Restrições devem ser separadas de riscos.

2. Restrições podem envolver orçamento, competência, prazo legal, tecnologia ou disponibilidade.

3. O impacto sobre a entrega deve ser descrito.

4. Cenários inviáveis devem ser sinalizados.

### 15.3 Casos de teste detalhados

| ID      | Cenário                     | Entrada                                      | Resultado esperado                                           |
| ------- | --------------------------- | -------------------------------------------- | ------------------------------------------------------------ |
| S10-T01 | Risco futuro válido         | Possível atraso de fornecedor                | Registro de risco com causa, evento, impacto e resposta.     |
| S10-T02 | Impedimento atual           | Autorização já atrasada                      | Classificação como impedimento.                              |
| S10-T03 | Dependência externa         | Dados necessários de outra unidade           | Unidade responsável e data necessária registradas.           |
| S10-T04 | Restrição fixa              | Prazo legal imutável                         | Classificação como restrição e impacto sobre o planejamento. |
| S10-T05 | Risco incompleto            | “Pode dar problema”                          | Solicitação de causa, evento e impacto.                      |
| S10-T06 | Dependência sem responsável | Insumo externo não atribuído                 | Registro incompleto e alerta gerencial.                      |
| S10-T07 | Risco duplicado             | Mesmo risco descrito com palavras diferentes | Possível duplicidade apresentada para consolidação.          |
| S10-T08 | Integração com S07          | Risco de falta de capacidade                 | Vínculo com cenário de capacidade e impacto calculado.       |

### 15.4 Métricas acadêmicas específicas

* precisão da classificação risco/impedimento/dependência/restrição;

* cobertura de riscos relevantes em comparação com especialistas;

* percentual de registros com causa, evento e impacto completos;

* taxa de duplicidades detectadas;

* utilidade dos alertas para revisão do plano;

* concordância entre especialistas sobre severidade.

* * *

## 16. Fluxos de integração do MVP

### 16.1 Fluxo principal de elaboração

1. S01 carrega o contexto institucional.

2. S03 extrai entregas candidatas.

3. S04 apresenta referências e detecta duplicidades.

4. S05 completa metas e critérios de aceite.

5. S02 verifica conformidade.

6. S06 audita o portfólio.

7. S07 analisa capacidade.

8. S08 verifica cobertura pela equipe.

9. S09 testa o alinhamento OKR-D.

10. S10 registra riscos e dependências.

11. S02 executa verificação final do conjunto.

### 16.2 Regras de integração

* Toda entrega deve possuir identificador persistente.

* Nenhuma skill deve recriar uma entrega quando puder referenciar seu identificador.

* Alterações devem gerar nova versão.

* Saídas automáticas devem registrar origem, regra aplicada e confiança.

* Decisões humanas devem ser registradas separadamente das sugestões do agente.

* Uma inconsistência identificada por uma skill deve permanecer visível até ser corrigida, aceita ou justificada.

* Dados ausentes não podem ser preenchidos silenciosamente.

* O histórico deve permitir reproduzir a análise.

### 16.3 Testes de integração ponta a ponta

| ID      | Cenário                                                | Resultado esperado                                                            |
| ------- | ------------------------------------------------------ | ----------------------------------------------------------------------------- |
| INT-T01 | Documento institucional até entrega estruturada        | Fonte preservada em todas as etapas.                                          |
| INT-T02 | Entrega duplicada identificada no catálogo e portfólio | S04 e S06 geram alertas consistentes.                                         |
| INT-T03 | Meta incompatível com capacidade                       | S05 define a meta; S07 identifica déficit; S06 registra impacto no portfólio. |
| INT-T04 | Entrega sem vínculo estratégico                        | S09 sinaliza ausência; justificativa operacional pode ser registrada.         |
| INT-T05 | Risco afeta prazo e capacidade                         | S10 vincula risco; S07 recalcula cenário; saída preserva o plano original.    |
| INT-T06 | Regra institucional alterada                           | S01 cria nova versão; S02 aplica a versão correta conforme o período.         |
| INT-T07 | Entrega sem cobertura                                  | S08 alerta; S07 confirma capacidade ou competência insuficiente.              |
| INT-T08 | Dados insuficientes                                    | Skills não inventam campos; perguntas pendentes permanecem registradas.       |

* * *

## 17. Requisitos não funcionais

### 17.1 Rastreabilidade

Toda recomendação deve registrar:

* dado de entrada utilizado;

* regra aplicada;

* fonte institucional, quando existente;

* transformação realizada;

* grau de confiança;

* necessidade ou não de validação humana.

### 17.2 Explicabilidade

O agente deve explicar:

* por que classificou determinado texto;

* por que sugeriu uma alteração;

* qual critério foi violado;

* qual campo está ausente;

* quais alternativas foram consideradas;

* quais informações ainda não permitem conclusão.

### 17.3 Segurança e proteção de dados

* Controle de acesso por perfil.

* Separação entre dados institucionais, dados de unidade e dados individuais.

* Registro de acessos e alterações.

* Não divulgação de dados pessoais em relatórios agregados sem necessidade.

* Identificação de documentos sensíveis.

* Possibilidade de anonimização para a pesquisa acadêmica.

### 17.4 Desempenho

Metas técnicas iniciais propostas:

| Operação                                | Meta inicial    |
| --------------------------------------- | --------------- |
| Análise de uma entrega                  | Até 10 segundos |
| Auditoria de plano com até 100 entregas | Até 60 segundos |
| Busca no catálogo                       | Até 5 segundos  |
| Recalcular capacidade de uma unidade    | Até 15 segundos |
| Gerar matriz de cobertura               | Até 20 segundos |

Esses valores devem ser ajustados após testes de infraestrutura e volume.

### 17.5 Reprodutibilidade

Para cada execução acadêmica, devem ser registrados:

* versão da skill;

* versão do modelo;

* configuração institucional;

* conjunto de fontes;

* parâmetros utilizados;

* prompt ou formulário de entrada;

* saída integral;

* tempo de processamento;

* intervenções humanas;

* resultado da avaliação.

* * *

## 18. Plano de avaliação

### 18.1 Perguntas de pesquisa sugeridas

- RQ1: o assistente especializado aumenta a qualidade das entregas quando comparado à elaboração sem assistência?

- RQ2: o assistente especializado reduz o tempo necessário para elaborar e revisar planos de entregas?

- RQ3: a utilização de regras institucionais rastreáveis reduz erros conceituais e normativos?

- RQ4: a análise integrada de capacidade, cobertura, OKR-D e riscos aumenta a consistência do portfólio?

- RQ5: especialistas e usuários percebem as explicações do agente como úteis, claras e confiáveis?

### 18.2 Hipóteses sugeridas

| Código | Hipótese                                                                                                          |
| ------ | ----------------------------------------------------------------------------------------------------------------- |
| H1     | Entregas elaboradas com o agente recebem pontuação média superior em clareza, mensurabilidade e verificabilidade. |
| H2     | O tempo médio de elaboração é menor com o agente.                                                                 |
| H3     | O número de atividades indevidamente registradas como entregas é menor com o agente.                              |
| H4     | Planos elaborados com o agente apresentam maior completude do 4Q1P.                                               |
| H5     | A integração de S07, S08, S09 e S10 aumenta a detecção de inviabilidades e lacunas antes da pactuação.            |
| H6     | Respostas com fonte e justificativa recebem maior avaliação de confiança.                                         |

### 18.3 Desenho experimental recomendado

| Condição                                  | Desenho recomendado                                                                                                      |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| **Condição A — Controle*                  | Participantes elaboram ou revisam entregas utilizando apenas os materiais de orientação disponíveis.                     |
| **Condição B — Assistente genérico**      | Participantes utilizam um modelo de linguagem sem configuração institucional ou skills especializadas.                   |
| **Condição C — Assistente especializado** | Participantes utilizam o MVP com as dez skills.<br/>Uma alternativa de menor custo é comparar apenas as condições A e C. |

### 18.4 Unidades de análise

------------------------

* plano de entregas;

* mapa OKR-D;

* plano de capacidade;

* matriz de cobertura;

* registro de risco;

* sessão de interação;

* percepção do usuário.

#### 18.5 Conjunto de dados

O conjunto de avaliação deve conter exemplos:

* corretos;

* incorretos;

* ambíguos;

* incompletos;

* duplicados;

* com problemas de granularidade;

* com metas vagas;

* com capacidade insuficiente;

* com alinhamento estratégico fraco;

* com riscos e impedimentos confundidos.

Recomenda-se separar:

* conjunto de desenvolvimento;

* conjunto de validação;

* conjunto de teste final;

* conjunto de casos reais anonimizados.

O conjunto de teste final não deve ser utilizado durante o desenvolvimento das regras.

#### 18.6 Padrão-ouro

O padrão-ouro deve ser produzido por pelo menos dois especialistas independentes.

Cada caso deve receber:

* classificação;

* título recomendado;

* campos 4Q1P;

* avaliação da meta;

* problemas do portfólio;

* avaliação de capacidade;

* vínculos OKR-D;

* classificação de riscos;

* justificativa.

Divergências devem ser resolvidas por consenso ou terceiro avaliador.

### 18.7 Métricas quantitativas

---------------------------

| Dimensão           | Métricas                                            |
| ------------------ | --------------------------------------------------- |
| Classificação      | Precisão, revocação, F1 e matriz de confusão        |
| Extração de campos | Acurácia por campo e completude                     |
| Similaridade       | Precision@k e Recall@k                              |
| Auditoria          | Taxa de problemas corretamente detectados           |
| Capacidade         | Exatidão matemática e erro de estimativa            |
| OKR-D              | Concordância sobre vínculos e lacunas               |
| Riscos             | F1 por classe e cobertura dos riscos relevantes     |
| Tempo              | Tempo médio e mediano por tarefa                    |
| Interação          | Número de turnos e correções necessárias            |
| Qualidade          | Pontuação por especialistas                         |
| Usabilidade        | Escala SUS ou instrumento equivalente               |
| Confiança          | Escala Likert e taxa de aceitação das recomendações |

### 18.8 Rubrica de qualidade das entregas

Cada dimensão pode ser pontuada de 0 a 4.

| Dimensão            | 0                           | 2                                  | 4                                             |
| ------------------- | --------------------------- | ---------------------------------- | --------------------------------------------- |
| Natureza de entrega | Não representa entrega      | Parcialmente identificável         | Produto ou serviço claramente identificável   |
| Clareza do título   | Incompreensível             | Compreensível com esforço          | Claro, simples e direto                       |
| Verificabilidade    | Sem condição de conclusão   | Conclusão parcialmente verificável | Conclusão objetivamente verificável           |
| Mensurabilidade     | Sem meta                    | Meta incompleta                    | Meta mensurável e coerente                    |
| 4Q1P                | Maioria ausente             | Parcialmente preenchido            | Completo e consistente                        |
| Relevância          | Tarefa instrumental         | Resultado de relevância limitada   | Resultado gerencialmente relevante            |
| Alinhamento         | Sem relação demonstrada     | Relação indireta                   | Contribuição claramente justificada           |
| Viabilidade         | Incompatível com capacidade | Incerteza relevante                | Compatível com capacidade e restrições        |
| Riscos              | Não analisados              | Análise parcial                    | Riscos e dependências estruturados            |
| Aceite              | Inexistente                 | Critério subjetivo                 | Critérios verificáveis e evidências definidas |

Pontuação máxima sugerida: 40 pontos.

### 18.9 Metas iniciais para o MVP

Os limiares abaixo são metas de pesquisa e devem ser recalibrados após o estudo-piloto.

| Indicador                                         | Meta inicial                   |
| ------------------------------------------------- | ------------------------------ |
| Macro-F1 da classificação de textos               | ≥ 0,85                         |
| Acurácia de extração dos campos 4Q1P              | ≥ 0,90                         |
| Precisão de não conformidades                     | ≥ 0,90                         |
| Recall de problemas críticos do portfólio         | ≥ 0,80                         |
| Exatidão dos cálculos de capacidade               | 100% nos casos determinísticos |
| Concordância dos vínculos OKR-D com especialistas | ≥ 0,75                         |
| F1 de risco/impedimento/dependência/restrição     | ≥ 0,80                         |
| Saídas com fonte corretamente associada           | ≥ 0,95                         |
| Redução do tempo de elaboração                    | ≥ 20%                          |
| Melhoria da rubrica de qualidade                  | ≥ 20%                          |
| Satisfação média dos usuários                     | ≥ 4 em escala de 1 a 5         |

### 18.10 Avaliação qualitativa

As entrevistas ou grupos focais devem investigar:

* confiança nas respostas;

* clareza das explicações;

* utilidade das perguntas;

* Fadequação ao contexto do ICMBio;

* percepção de controle humano;

* dificuldades de uso;

* situações em que o agente atrapalhou;

* sugestões de novos campos ou skills;

* riscos de dependência excessiva;

* percepção sobre rastreabilidade e transparência.

* * *

## 19. Critérios de pronto do MVP

O MVP estará pronto para estudo-piloto quando:

1. As dez skills estiverem implementadas com contratos de entrada e saída.

2. Todos os testes positivos e negativos críticos estiverem aprovados.

3. Os testes de integração INT-T01 a INT-T08 estiverem aprovados.

4. As regras institucionais puderem ser versionadas.

5. Toda recomendação relevante possuir justificativa.

6. Dados ausentes não forem preenchidos silenciosamente.

7. Alterações e decisões humanas forem registradas.

8. O conjunto de teste acadêmico estiver congelado.

9. A rubrica de avaliação estiver validada por especialistas.

10. Os registros de pesquisa puderem ser anonimizados.

11. Um plano completo puder percorrer o fluxo S01–S10.

12. Os resultados puderem ser reproduzidos a partir dos logs da execução.

* * *

## 20. Backlog recomendado de implementação

### Sprint 1 — Fundação

* modelo comum de dados;

* controle de versões;

* cadastro de fontes;

* S01;

* estrutura de logs;

* controle de acesso inicial.

### Sprint 2 — Regras e extração

* classificadores de texto;

* S02;

* S03;

* testes com objetivos, entregas e atividades;

* painel de validação humana.

### Sprint 3 — Catálogo e metas

* S04;

* busca semântica;

* versionamento das entregas;

* S05;

* critérios de aceite;

* fontes de evidência.

### Sprint 4 — Auditoria do portfólio

* S06;

* detecção de duplicidade;

* análise de granularidade;

* comparação com competências;

* relatório consolidado.

### Sprint 5 — Capacidade e cobertura

* S07;

* cálculo de carga horária útil;

* cenários;

* S08;

* matriz entrega × participante;

* alertas de sobrealocação e concentração.

### Sprint 6 — Estratégia e riscos

* S09;

* mapa OKR-D;

* auditoria dos vínculos;

* S10;

* classificação de riscos e impedimentos;

* integração com capacidade e portfólio.

### Sprint 7 — Integração e estudo-piloto

* fluxo ponta a ponta;

* testes de integração;

* congelamento do conjunto de teste;

* instrumento de avaliação;

* estudo-piloto;

* ajustes dos limiares.

* * *

## 21. Entregáveis associados

O desenvolvimento pode produzir os seguintes artefatos de pesquisa:

1. modelo conceitual do agente especializado;

2. ontologia ou esquema de dados do PGD;

3. catálogo de regras e validadores;

4. conjunto de casos anotados;

5. rubrica de qualidade de entregas;

6. protocolo experimental;

7. relatório de desempenho das dez skills;

8. estudo de usabilidade;

9. análise de erros;

10. recomendações para implantação institucional responsável.

O principal resultado acadêmico não será apenas a implementação do agente, mas a demonstração de como suas regras, fontes, decisões e limitações podem ser avaliadas de maneira rastreável e reproduzível.
