Análise das skills e proposta de evolução para um assistente de PGD do ICMBio
=============================================================================

---

## 1. Síntese executiva.

As quatro skills formam uma base conceitual consistente para a fase de **planejamento** do PGD:

1. **Análise de Entregas:** verifica se um texto representa uma entrega e ajuda a estruturá-la.

2. **OKR-D:** conecta estratégia, resultados-chave, entregas e atividades.

3. **Plano de Entregas:** orienta a construção do portfólio de entregas da unidade.

4. **Plano de Trabalho:** distribui a capacidade individual entre entregas e outras categorias de trabalho.

Em conjunto, elas representam o seguinte fluxo:

> Estratégia → objetivos e resultados-chave → entregas da unidade → plano de entregas → contribuições individuais → plano de trabalho.

A cobertura é especialmente forte na definição conceitual das entregas, na separação entre entregas e atividades, no método 4Q1P e na distribuição percentual do esforço individual.  
Entretanto, o conjunto ainda não constitui um assistente completo para todo o ciclo do PGD. As skills concentram-se na elaboração inicial dos planos. Permanecem pouco desenvolvidas as etapas de:

* configuração institucional;

* análise de capacidade da unidade;

* pactuação e aprovação;

* monitoramento;

* tratamento de riscos e dependências;

* replanejamento;

* registro de evidências;

* avaliação das entregas;

* consolidação dos resultados;

* aprendizado para o ciclo seguinte.

A principal oportunidade é transformar as quatro skills atuais em um **ecossistema modular**, no qual regras conceituais comuns sejam executadas por validadores reutilizáveis e as novas skills cubram todo o ciclo de gestão.

* * *

## 2. Avaliação individual das quatro skills.

### 2.1 Skill “Análise de Entregas”

#### Pontos fortes

Essa é a skill com melhor capacidade de diagnóstico pontual. Ela verifica:

* se o texto é objetivo, entrega, tarefa ou atividade;

* qual produto ou serviço existirá ao final;

* se há clareza sobre a conclusão;

* se o título está redigido como resultado;

* se informações de meta, prazo, demandante e destinatário foram indevidamente colocadas no título;

* se a entrega é mensurável;

* se o nível de granularidade é adequado;

* se há necessidade de descrição ou progresso esperado.

A skill também fornece uma saída útil ao usuário: diagnóstico, proposta de título, justificativa e perguntas para completar o 4Q1P.

#### Fragilidades

A skill abrange muitas funções diferentes. Ela não apenas analisa o título, mas também:

* classifica a entrega;

* define meta;

* identifica demandante e destinatário;

* orienta prazo;

* produz descrição;

* avalia progresso esperado;

* avalia granularidade;

* prepara o desdobramento no plano de trabalho.

Isso cria sobreposição com a skill de elaboração do plano de entregas. A mesma regra pode acabar sendo mantida em dois lugares e evoluir de maneira diferente.

Também falta um formato de saída rigidamente estruturado. Em vez de apenas uma resposta discursiva, a skill poderia retornar algo semelhante a:

| Campo                           | Resultado                               |
| ------------------------------- | --------------------------------------- |
| Classificação do texto          | Entrega, objetivo, tarefa ou atividade  |
| Grau de confiança               | Alto, médio ou baixo                    |
| Problemas encontrados           | Lista categorizada                      |
| Título original                 | Texto recebido                          |
| Título recomendado              | Texto reformulado                       |
| Informações removidas do título | Meta, prazo, demandante etc.            |
| Campos ausentes                 | Elementos do 4Q1P ainda não informados  |
| Próxima ação                    | Completar, dividir, validar ou rejeitar |

#### Recomendação

Dividir funcionalmente essa skill em três componentes internos:

1. **Classificador de elementos do trabalho** — objetivo, entrega, atividade ou tarefa.

2. **Validador e reformulador de títulos**.

3. **Completador de campos do 4Q1P**.

Para o usuário, esses componentes podem continuar aparecendo como uma única experiência conversacional.

* * *

### 2.2 Skill “O que é OKR-D?”

#### Pontos fortes

A skill apresenta uma lógica clara:

> Objetivo → resultado-chave → entrega → atividade.

Ela diferencia adequadamente:

* objetivo como situação desejada;

* resultado-chave como medida de avanço;

* entrega como produto ou serviço concreto;

* atividade como ação realizada para gerar a entrega.

Também oferece testes de consistência importantes:

1. As atividades geram a entrega?

2. A entrega contribui para o resultado-chave?

3. O resultado-chave indica avanço em direção ao objetivo?

Essa cadeia ajuda a impedir que atividades sejam registradas como entregas e oferece uma ponte entre planejamento estratégico e execução operacional.

#### Fragilidades

A skill é predominantemente explicativa. Ela esclarece o método, mas ainda não conduz plenamente uma oficina de elaboração.

Faltam operações como:

* analisar um objetivo estratégico apresentado pelo usuário;

* avaliar a qualidade de um resultado-chave;

* propor diferentes entregas candidatas;

* detectar entregas sem vínculo estratégico;

* identificar resultados-chave que não possuem entregas suficientes;

* registrar relações muitos-para-muitos entre objetivos, resultados-chave e entregas;

* avaliar se uma entrega realmente possui influência plausível sobre o resultado-chave;

* distinguir contribuição direta, indireta ou apenas contextual.

Uma entrega pode contribuir para mais de um resultado-chave, e um resultado-chave pode depender de várias entregas. A skill atual apresenta a cadeia de modo principalmente linear.

#### Recomendação

Transformar a skill em duas experiências:

* **Introdução ao OKR-D**, mantendo sua finalidade educativa;

* **Designer e auditor de encadeamentos OKR-D**, para elaborar e testar relações concretas.

O auditor deve produzir uma matriz como:

| Entrega   | Resultado-chave relacionado | Tipo de contribuição | Intensidade esperada | Justificativa |
| --------- | --------------------------- | -------------------- | -------------------- | ------------- |
| Entrega A | KR 1                        | Direta               | Alta                 | Explicação    |
| Entrega B | KR 1 e KR 2                 | Indireta             | Média                | Explicação    |

* * *

### 2.3 Skill “Como elaborar um plano de entregas?”

#### Pontos fortes

Essa é a skill mais abrangente. Ela cobre:

* definição da Unidade de Execução;

* vigência;

* levantamento das entregas;

* formulação e validação dos títulos;

* classificação entre projeto e processo;

* classificação entre produto e serviço;

* método 4Q1P;

* descrição;

* meta;

* prazo;

* progresso esperado;

* vinculação institucional;

* revisão do portfólio;

* pactuação;

* desdobramento nos planos de trabalho.

A matriz que cruza projeto ou processo com produto ou serviço é especialmente útil para orientar metas, critérios de acompanhamento e formas de avaliação.

#### Fragilidades

A skill é extensa e monolítica. Um usuário que precise apenas definir uma meta ou revisar um portfólio precisa passar conceitualmente por uma metodologia muito maior.

Também existe um ponto de ambiguidade interna que merece correção. Em uma parte, a documentação orienta que o percentual de avanço não seja confundido com a meta final e seja registrado como progresso esperado. Em outra, a tabela de metas frequentes para projetos inclui “percentual de conclusão” como possibilidade de meta.

Para evitar registros inconsistentes, a futura arquitetura deveria estabelecer:

* **meta final:** resultado que caracteriza a entrega como concluída ou o desempenho final esperado;

* **progresso esperado:** avanço previsto dentro da vigência do plano;

* **marco intermediário:** resultado parcial verificável, que pode ser tratado como progresso ou como subentrega, mas não simultaneamente das duas formas.

Outras lacunas:

* ausência de critérios formais de aceite;

* ausência de fontes de evidência;

* ausência de riscos e dependências;

* ausência de responsáveis pela coordenação da entrega;

* ausência de análise quantitativa de capacidade;

* ausência de controle de versões;

* ausência de histórico das alterações;

* ausência de workflow de aprovação;

* ausência de tratamento estruturado para entregas canceladas, suspensas ou substituídas.

#### Recomendação

Converter essa skill em um **orquestrador**. Ela seria responsável por conduzir o usuário, mas acionaria componentes especializados para cada etapa:

> Identificar entrega → validar título → classificar → completar 4Q1P → definir meta → definir critérios de aceite → analisar capacidade → verificar portfólio → pactuar.

* * *

### 2.4 Skill “Como elaborar um plano de trabalho?”

#### Pontos fortes

A skill estabelece corretamente que o plano de trabalho é uma distribuição da carga horária útil do participante, e não uma lista genérica de tarefas.

Ela diferencia:

* entregas da própria unidade;

* entregas de outras unidades;

* atividades de apoio, assessoramento e desenvolvimento;

* atividades de gestão de equipes e entregas.

Também esclarece que o percentual representa esforço planejado, e não percentual de conclusão da entrega. A validação da soma em 100% é um mecanismo objetivo e importante.

Outro ponto forte é o tratamento de entregas que atravessam vários meses: a entrega pode permanecer no plano, mas a descrição da contribuição individual deve mudar conforme o trabalho previsto para cada período.

#### Fragilidades

A skill funciona bem para um participante isolado, mas não agrega os planos individuais para responder perguntas gerenciais, como:

* todas as entregas possuem pessoas contribuindo?

* alguma entrega recebeu esforço insuficiente?

* existem pessoas sobrecarregadas?

* a distribuição dos participantes corresponde às prioridades?

* quanto esforço total da unidade está destinado a atividades indiretas?

* há concentração excessiva de conhecimento em uma única pessoa?

* as contribuições previstas cobrem todos os marcos do período?

* contribuições para outras unidades estão comprometendo entregas próprias?

A documentação também apresenta percentuais de referência para atividades indiretas. No futuro agente, esses valores precisam ser tratados como **parâmetros de análise ou alertas**, e não automaticamente como proibições. A própria skill reconhece situações em que assessores e chefias podem chegar a percentuais muito elevados nessas categorias.

#### Recomendação

Separar:

1. **Calculadora de capacidade útil**.

2. **Distribuidor individual de esforço**.

3. **Validador da soma de 100%**.

4. **Consolidador dos planos da equipe**.

5. **Analisador de cobertura das entregas**.

* * *

## 3. Problemas transversais da arquitetura atual.

### 3.1 Repetição de regras

As quatro skills repetem conceitos sobre:

* entrega versus atividade;

* título da entrega;

* método 4Q1P;

* meta;

* prazo;

* plano de entregas;

* plano de trabalho.

Essa repetição melhora a compreensão de cada documento isoladamente, mas cria risco técnico. Uma alteração conceitual precisaria ser reproduzida em vários arquivos.

#### Solução

Criar uma camada de regras compartilhadas:

* `classificar_elemento_trabalho`;

* `validar_titulo_entrega`;

* `validar_4q1p`;

* `classificar_projeto_processo`;

* `classificar_produto_servico`;

* `validar_meta`;

* `validar_progresso`;

* `validar_alocacao_esforco`.

As skills conversacionais passariam a reutilizar esses validadores.

* * *

### 3.2 Ausência de modelo de dados comum

As skills descrevem campos, mas não estabelecem um esquema canônico compartilhado.

#### Modelo recomendado para entrega

| Grupo         | Campos sugeridos                                          |
| ------------- | --------------------------------------------------------- |
| Identificação | ID, título, descrição                                     |
| Classificação | Projeto ou processo; produto ou serviço                   |
| 4Q1P          | Demandante, destinatário, meta, unidade de medida e prazo |
| Planejamento  | Vigência relacionada, progresso esperado e prioridade     |
| Estratégia    | Objetivo, resultado-chave, iniciativa ou macroprocesso    |
| Gestão        | Responsável pela coordenação, riscos e dependências       |
| Aceite        | Critérios de conclusão, aprovador e evidências            |
| Execução      | Situação, progresso realizado e impedimentos              |
| Governança    | Versão, data da alteração, justificativa e aprovadores    |

Nem todos esses campos precisam ser obrigatórios. O modelo deve distinguir:

* campos normativamente obrigatórios;

* campos institucionais;

* campos opcionais;

* campos calculados pelo sistema.

* * *

### 3.3 Regras e recomendações não estão classificadas

O agente precisa diferenciar:

* obrigação normativa;

* regra institucional do ICMBio;

* recomendação metodológica;

* exemplo;

* alerta gerencial;

* preferência de redação.

Por exemplo, a estrutura “Objeto direto + verbo no particípio” é apresentada como preferencial, e não como regra gramatical absoluta.

Essa distinção deve aparecer nas respostas:

> “Obrigatório segundo a norma aplicável”  
> “Recomendado pela metodologia”  
> “Boa prática sugerida”  
> “Parâmetro configurado pelo ICMBio”

* * *

### 3.4 Falta de continuidade entre as skills

Hoje, a entrega analisada em uma skill não possui necessariamente um objeto estruturado que possa ser enviado automaticamente para a skill de plano de entregas e depois para a de plano de trabalho.

#### Solução

Cada skill deve produzir e receber objetos compatíveis.

Exemplo:

> Análise de Entrega gera `EntregaCandidata`  
> Plano de Entregas converte em `EntregaPactuada`  
> Plano de Trabalho referencia o `ID da EntregaPactuada`  
> Monitoramento atualiza a mesma entrega  
> Avaliação encerra o ciclo e preserva o histórico.

* * *

### 3.5 Cobertura incompleta do ciclo de gestão

As skills atuais concentram-se no planejamento. O futuro agente precisa cobrir:

> Preparar → planejar → pactuar → executar → monitorar → ajustar → avaliar → aprender.

* * *

## 4. Novas skills recomendadas.

### Prioridade 0 — Fundação institucional e qualidade dos dados

#### 4.1 Configurador Institucional do PGD no ICMBio

**Finalidade:** parametrizar o agente com a estrutura, terminologia e regras vigentes da organização.

**Entradas:**

* documentos normativos;

* estrutura organizacional;

* unidades que podem atuar como UEs;

* cadeia de valor;

* macroprocessos;

* objetivos institucionais;

* taxonomias;

* calendários;

* perfis e autoridades de aprovação.

**Saídas:**

* dicionário institucional;

* regras obrigatórias;

* campos utilizados pelo ICMBio;

* matriz de papéis;

* vocabulário autorizado;

* alertas sobre documentos conflitantes ou desatualizados.

Essa skill é essencial porque as quatro documentações analisadas não permitem determinar quais estruturas, sistemas, papéis e regras internas específicas do ICMBio deverão ser aplicados.

* * *

#### 4.2 Verificador Normativo e de Conformidade

**Finalidade:** analisar um plano ou entrega e informar se está em conformidade com os normativos aplicáveis.

**Funções:**

* distinguir obrigação normativa de recomendação metodológica;

* citar a fonte da regra;

* identificar campos obrigatórios ausentes;

* apontar violações;

* informar quando uma regra não pode ser confirmada;

* registrar a versão do normativo utilizada.

**Saída recomendada:**

| Regra | Situação | Gravidade | Fonte | Correção sugerida |
| ----- | -------- | --------- | ----- | ----------------- |

* * *

#### 4.3 Extrator de Competências e Responsabilidades em Entregas

**Finalidade:** transformar competências regimentais, responsabilidades e processos organizacionais em candidatas a entregas.

**Fluxo:**

1. Receber trecho de regimento, cadeia de valor ou descrição de processo.

2. Identificar verbos de responsabilidade.

3. Separar responsabilidades, atividades e resultados.

4. Propor produtos ou serviços gerados.

5. Formular títulos candidatos.

6. Solicitar validação da unidade.

Essa skill seria particularmente útil na implantação inicial do PGD, quando as unidades ainda possuem listas de atribuições, mas não um portfólio claro de entregas.

* * *

#### 4.4 Administrador do Catálogo de Entregas do ICMBio

**Finalidade:** manter uma biblioteca institucional de entregas padronizadas e reutilizáveis.

**Recursos:**

* busca por unidade, processo ou tema;

* sugestão de entregas semelhantes;

* identificação de duplicidades;

* versões aprovadas;

* exemplos de metas;

* descrições de referência;

* critérios de aceite;

* possibilidade de adaptação local.

O catálogo não deve obrigar todas as unidades a utilizarem títulos idênticos. Ele deve promover consistência sem eliminar particularidades legítimas.

* * *

### Prioridade 1 — Planejamento de qualidade

#### 4.5 Designer de Metas, Indicadores e Critérios de Aceite

**Finalidade:** complementar a atual definição da meta.

A skill deve ajudar a definir separadamente:

* meta final;

* unidade de medida;

* indicador;

* linha de base, quando aplicável;

* critério de qualidade;

* critério de aceite;

* fonte de evidência;

* responsável pelo aceite;

* progresso esperado.

**Validações importantes:**

* a meta mede entrega ou apenas esforço?

* o indicador está sob influência razoável da unidade?

* existe fonte de dados?

* o resultado pode ser verificado?

* há conflito entre meta final e progresso esperado?

* qualidade e quantidade estão equilibradas?

* * *

#### 4.6 Auditor de Portfólio de Entregas

**Finalidade:** analisar o plano de entregas como um conjunto, e não apenas cada entrega isoladamente.

**Verificações:**

* duplicidade;

* sobreposição;

* lacunas de cobertura;

* tarefas registradas como entregas;

* títulos excessivamente amplos;

* entregas pequenas demais;

* demandantes e destinatários ausentes;

* metas incompatíveis;

* prazos concentrados;

* excesso de entregas;

* entregas sem vínculo institucional;

* entregas sem critérios de aceite;

* equilíbrio entre processos contínuos e projetos.

**Saída:**

* nota de consistência do portfólio;

* problemas críticos;

* alertas;

* oportunidades de consolidação;

* entregas que devem ser divididas;

* entregas que devem ser agrupadas.

* * *

#### 4.7 Planejador de Capacidade da Unidade

**Finalidade:** verificar se o portfólio é compatível com a capacidade disponível.

Essa skill atuaria acima dos planos individuais.

**Entradas:**

* participantes;

* carga horária útil;

* indisponibilidades;

* esforço indireto esperado;

* estimativa de esforço das entregas;

* prioridades;

* competências necessárias.

**Saídas:**

* capacidade total;

* capacidade disponível para entregas;

* demanda estimada;

* déficit ou folga;

* entregas sem capacidade suficiente;

* cenários de priorização;

* recomendações de redução de escopo, prazo ou quantidade.

É importante não produzir uma falsa precisão. A skill pode trabalhar com faixas de esforço, como baixa, média e alta, além de horas estimadas.

* * *

#### 4.8 Matriz de Cobertura das Entregas pela Equipe

**Finalidade:** consolidar os planos de trabalho e verificar a cobertura do plano de entregas.

**Perguntas respondidas:**

* quem contribui para cada entrega?

* qual esforço total foi direcionado?

* existe coordenador ou referência?

* há competências críticas sem cobertura?

* alguma entrega depende de uma única pessoa?

* os planos individuais refletem as prioridades?

* existem participantes sobrealocados?

Essa skill complementa diretamente a skill atual de plano de trabalho.

* * *

#### 4.9 Designer de Encadeamento OKR-D

**Finalidade:** transformar a skill educativa de OKR-D em uma ferramenta de elaboração.

**Operações:**

* receber objetivo ou resultado-chave;

* avaliar sua redação;

* sugerir entregas candidatas;

* avaliar contribuição causal ou plausível;

* construir relações muitos-para-muitos;

* identificar entregas sem contribuição clara;

* detectar resultados-chave sem suporte operacional;

* produzir mapa visual ou matriz de alinhamento.

**Saída principal:**

> Objetivo → resultado-chave → entregas → indicadores → atividades principais.

* * *

#### 4.10 Analisador de Riscos, Dependências e Restrições

**Finalidade:** tornar o plano mais realista.

**Campos sugeridos:**

* dependências internas;

* dependências externas;

* insumos necessários;

* decisões pendentes;

* riscos;

* probabilidade;

* impacto;

* resposta planejada;

* responsável;

* data de revisão.

A skill deve diferenciar risco de impedimento:

* **risco:** evento futuro incerto;

* **impedimento:** problema já existente que afeta a execução.

* * *

### Prioridade 2 — Pactuação e execução

#### 4.11 Assistente de Pactuação do Plano de Entregas

**Finalidade:** apoiar a negociação entre unidade e chefia superior.

**Funções:**

* preparar pauta;

* sintetizar divergências;

* registrar propostas;

* comparar versões;

* documentar decisões;

* registrar ressalvas;

* identificar itens aprovados, rejeitados ou condicionados;

* produzir versão final pactuada.

A skill não deve tomar a decisão pela chefia. Deve organizar informações e preservar a trilha decisória.

* * *

#### 4.12 Assistente de Pactuação do Plano de Trabalho

**Finalidade:** apoiar a conversa entre participante e chefia.

**Análises:**

* soma de 100%;

* aderência às prioridades;

* compatibilidade com capacidade útil;

* clareza das contribuições;

* excesso de detalhamento;

* contribuições externas;

* atividades indiretas;

* diferenças entre proposta do participante e proposta da chefia.

* * *

#### 4.13 Check-in de Execução e Monitoramento

**Finalidade:** registrar o acompanhamento periódico sem reconstruir o plano.

**Perguntas centrais:**

* o que avançou?

* qual evidência existe?

* o que está bloqueado?

* a meta e o prazo continuam viáveis?

* houve mudança de prioridade?

* qual decisão gerencial é necessária?

* qual será o próximo marco?

**Saídas:**

* situação da entrega;

* progresso realizado;

* evidências;

* riscos atualizados;

* impedimentos;

* decisões;

* próximos passos.

* * *

#### 4.14 Gestor de Alterações e Replanejamento

**Finalidade:** controlar mudanças sem apagar o plano originalmente pactuado.

**Tipos de alteração:**

* mudança de meta;

* mudança de prazo;

* alteração de escopo;

* substituição de entrega;

* cancelamento;

* suspensão;

* inclusão de nova entrega;

* mudança de demandante ou destinatário;

* redistribuição de esforço.

**Requisitos:**

* justificativa;

* impacto;

* autoridade de aprovação;

* data;

* versão anterior;

* versão nova;

* histórico preservado.

* * *

#### 4.15 Gestor de Contribuições Interunidades

**Finalidade:** tratar trabalho matricial, grupos de trabalho, forças-tarefas e outras contribuições externas.

**Funções:**

* identificar unidade proprietária da entrega;

* registrar unidade colaboradora;

* registrar participantes;

* obter anuências;

* evitar contagem duplicada;

* consolidar esforço;

* registrar responsabilidade pela aceitação;

* acompanhar dependências entre unidades.

* * *

### Prioridade 3 — Avaliação, evidências e inteligência gerencial

#### 4.16 Avaliador de Entregas

**Finalidade:** apoiar a avaliação ao final do ciclo.

A avaliação deve considerar separadamente:

* alcance da meta;

* prazo;

* qualidade;

* conformidade;

* aceite do destinatário;

* evidências;

* justificativas;

* fatores externos;

* aprendizado.

A skill deve evitar avaliar o participante apenas pelo resultado bruto da entrega, especialmente quando existirem dependências externas relevantes.

* * *

#### 4.17 Organizador de Evidências

**Finalidade:** vincular comprovações às entregas e contribuições.

**Tipos de evidência:**

* documento;

* processo;

* registro em sistema;

* relatório;

* ata;

* painel;

* protocolo;

* manifestação do destinatário;

* produto digital;

* indicador.

A skill deve verificar se a evidência:

* corresponde à entrega;

* é suficiente;

* está dentro do período;

* possui origem identificável;

* demonstra quantidade e qualidade;

* contém dados sensíveis que exijam tratamento específico.

* * *

#### 4.18 Gerador de Relatório Gerencial do PGD

**Finalidade:** consolidar dados para chefias e instâncias de governança.

**Possíveis visões:**

* entregas por situação;

* metas previstas e realizadas;

* prazos;

* capacidade;

* riscos;

* entregas estratégicas;

* unidades com necessidade de apoio;

* contribuições interunidades;

* atividades indiretas;

* alterações realizadas;

* resultados e aprendizados.

Os relatórios devem permitir diferentes níveis de agregação sem expor indevidamente informações individuais.

* * *

#### 4.19 Analisador de Aprendizado entre Ciclos

**Finalidade:** utilizar dados históricos para melhorar o próximo planejamento.

**Análises possíveis:**

* metas frequentemente superestimadas;

* entregas reiteradamente adiadas;

* riscos recorrentes;

* prazos incompatíveis;

* esforço real diferente do planejado;

* excesso de alterações;

* atividades indiretas crescentes;

* padrões de dependência;

* entregas com baixo valor percebido.

A skill deve formular hipóteses e recomendações, sem apresentar correlações como causalidade comprovada.

* * *

#### 4.20 Importador, Exportador e Integrador de Planos

**Finalidade:** reduzir retrabalho e permitir interoperabilidade.

**Possíveis operações:**

* importar planilhas;

* validar colunas;

* normalizar títulos;

* detectar registros duplicados;

* exportar plano de entregas;

* exportar plano de trabalho;

* gerar documentos para pactuação;

* produzir dados para painéis;

* conectar registros de entregas a sistemas institucionais.

* * *

## 5. Arquitetura recomendada para o agente.

### Camada 1 — Conhecimento institucional

Contém:

* normativos;

* estrutura;

* glossário;

* cadeia de valor;

* objetivos;

* regras de aprovação;

* exemplos institucionais;

* catálogo de entregas.

### Camada 2 — Serviços de validação

Componentes reutilizáveis:

* classificador de texto;

* validador de título;

* validador 4Q1P;

* validador de meta;

* classificador da entrega;

* calculadora de capacidade;

* validador de percentuais;

* detector de duplicidades;

* analisador de alinhamento;

* verificador normativo.

### Camada 3 — Skills conversacionais

Experiências apresentadas ao usuário:

* elaborar entrega;

* elaborar plano de entregas;

* elaborar plano de trabalho;

* elaborar OKR-D;

* pactuar;

* monitorar;

* replanejar;

* avaliar.

### Camada 4 — Governança e dados

Responsável por:

* IDs;

* versões;

* histórico;

* aprovações;

* permissões;

* evidências;

* logs;

* integração;

* proteção de dados.

* * *

## 6. Priorização para um produto acadêmico.

### MVP recomendado

#### Primeira versão:

Para uma primeira versão funcional, eu priorizaria:

1. **Configurador institucional**.

2. **Extrator de competências em entregas**.

3. **Análise estruturada de entregas**.

4. **Designer de metas e critérios de aceite**.

5. **Elaborador modular do plano de entregas**.

6. **Auditor de portfólio**.

7. **Planejador de capacidade**.

8. **Consolidador dos planos de trabalho**.

Esse conjunto demonstraria uma contribuição acadêmica relevante: transformar atribuições organizacionais em entregas estruturadas, validar o portfólio e verificar sua compatibilidade com a capacidade da equipe.

#### Segunda versão:

Adicionar:

* pactuação;

* monitoramento;

* riscos;

* replanejamento;

* contribuições interunidades;

* avaliação e evidências.

#### Terceira versão:

Adicionar:

* análise histórica;

* relatórios gerenciais;

* recomendações baseadas em padrões;

* integrações com sistemas;

* catálogo institucional inteligente.

* * *

## 7. Critério para decidir se algo deve ser uma nova skill.

Uma funcionalidade deve tornar-se uma skill independente quando:

* possui intenção de usuário própria;

* pode ser acionada sem executar todo o fluxo;

* recebe entradas claramente identificáveis;

* produz uma saída reutilizável;

* possui regras específicas;

* pode ser testada isoladamente;

* é reutilizada por mais de um fluxo.

Por esse critério, “validar título”, “calcular capacidade” e “auditar portfólio” são bons componentes independentes. Já “explicar o que é uma entrega” pode continuar como recurso educativo incorporado em outras skills.

* * *

## 8. Conclusão.

As quatro skills atuais formam uma base conceitual forte, mas concentram-se na preparação dos planos. A evolução mais relevante não é simplesmente adicionar mais textos explicativos. É construir um agente com:

* dados estruturados;

* validadores compartilhados;

* continuidade entre as etapas;

* regras institucionais parametrizadas;

* memória do ciclo;

* rastreabilidade;

* análise de capacidade;

* monitoramento;

* avaliação;

* aprendizado.

Para o contexto do ICMBio, a maior diferenciação do futuro agente poderá estar em sua capacidade de compreender documentos institucionais, transformar competências e processos em entregas, relacioná-las ao planejamento organizacional e acompanhar sua execução em unidades com diferentes realidades operacionais.

A aderência concreta ao ICMBio deverá ser validada posteriormente com documentos oficiais e internos sobre estrutura, competências, planejamento, processos, sistemas, papéis e regras específicas. Essas informações não estão contidas nas quatro skills analisadas.
