Matriz de desenvolvimento das skills do Assistente de PGD do ICMBio
===================================================================

## 1. Convenções da matriz

-----------------------

### Prioridades

| Prioridade            | Significado                                                                                         |
| --------------------- | --------------------------------------------------------------------------------------------------- |
| **P0 — Fundação**     | Componente necessário para governança, padronização ou funcionamento seguro das demais skills.      |
| **P1 — MVP**          | Componente central para elaborar planos consistentes e demonstrar valor acadêmico e organizacional. |
| **P2 — Operação**     | Componente necessário para pactuar, executar, monitorar e alterar os planos.                        |
| **P3 — Inteligência** | Componente voltado à avaliação, consolidação, aprendizado e integração institucional.               |

### Componentes existentes que serão reutilizados

| Código  | Componente atual    | Função no futuro agente                                                                 |
| ------- | ------------------- | --------------------------------------------------------------------------------------- |
| **B01** | Análise de Entregas | Classificar textos, validar títulos e completar informações da entrega.                 |
| **B02** | OKR-D               | Relacionar objetivos, resultados-chave, entregas e atividades.                          |
| **B03** | Plano de Entregas   | Orquestrar a elaboração do portfólio da Unidade de Execução.                            |
| **B04** | Plano de Trabalho   | Distribuir a capacidade útil dos participantes entre contribuições e demais atividades. |

A arquitetura proposta pressupõe que esses componentes sejam modularizados. As regras de validação não devem ser duplicadas em várias skills.

* * *

## 2. Skills de prioridade P0 — Fundação institucional

### S01 — Configurador Institucional do PGD

| Campo                    | Especificação                                                                                                                                                                                                                   |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Prioridade**           | P0                                                                                                                                                                                                                              |
| **Objetivo**             | Parametrizar o agente com os conceitos, estruturas, regras e vocabulários adotados pelo ICMBio.                                                                                                                                 |
| **Dependências**         | Nenhuma. É a base das demais skills.                                                                                                                                                                                            |
| **Entradas**             | Normativos; estrutura organizacional; relação de unidades; competências; cadeia de valor; objetivos institucionais; macroprocessos; calendários; perfis; papéis de aprovação; campos adotados nos planos.                       |
| **Saídas**               | Perfil institucional versionado; glossário; relação de UEs; regras obrigatórias; campos opcionais; taxonomias; matriz de papéis; calendário de ciclos; lista de fontes utilizadas.                                              |
| **Regras principais**    | Distinguir obrigação normativa, regra institucional, recomendação metodológica e exemplo; registrar fonte e versão; não presumir regra específica do ICMBio sem documento correspondente; sinalizar conflitos entre documentos. |
| **Teste de aceitação 1** | **Dado** um conjunto de documentos institucionais, **quando** a configuração for executada, **então** o sistema deve gerar um perfil com fonte, data e versão de cada regra identificada.                                       |
| **Teste de aceitação 2** | **Dado** que dois documentos apresentem regras conflitantes, **quando** forem processados, **então** o sistema não deve escolher silenciosamente uma regra; deve apresentar o conflito para decisão humana.                     |
| **Teste de aceitação 3** | **Dado** um campo não previsto nos documentos fornecidos, **quando** ele for sugerido, **então** deve ser identificado como recomendação de projeto, e não como obrigação institucional.                                        |

* * *

### S02 — Verificador Normativo e de Conformidade

| Campo                    | Especificação                                                                                                                                                                                                                                             |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Prioridade**           | P0                                                                                                                                                                                                                                                        |
| **Objetivo**             | Verificar se entregas, planos e alterações atendem às regras aplicáveis.                                                                                                                                                                                  |
| **Dependências**         | S01; B01; B03; B04.                                                                                                                                                                                                                                       |
| **Entradas**             | Entrega, plano de entregas, plano de trabalho ou solicitação de alteração; perfil institucional; versão dos normativos.                                                                                                                                   |
| **Saídas**               | Relatório de conformidade; regras atendidas; não conformidades; gravidade; fonte; correção recomendada; itens que exigem decisão humana.                                                                                                                  |
| **Regras principais**    | Toda não conformidade deve citar a regra aplicável; recomendações não podem ser apresentadas como obrigações; a análise deve usar a versão normativa vigente no ciclo avaliado; ausência de informação deve ser diferenciada de violação.                 |
| **Teste de aceitação 1** | **Dado** um plano sem campo obrigatório, **quando** for verificado, **então** o relatório deve identificar o campo ausente, a fonte da obrigação e a ação corretiva.                                                                                      |
| **Teste de aceitação 2** | **Dado** um título que não siga a redação preferencial, mas identifique claramente a entrega, **quando** for analisado, **então** o sistema deve tratá-lo como recomendação de melhoria, não como infração normativa, salvo regra institucional expressa. |
| **Teste de aceitação 3** | **Dado** um normativo revogado, **quando** um plano histórico for analisado, **então** o sistema deve considerar a regra vigente no período do plano.                                                                                                     |

* * *

### S03 — Extrator de Competências e Responsabilidades em Entregas

| Campo                    | Especificação                                                                                                                                                                                                                   |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Prioridade**           | P0                                                                                                                                                                                                                              |
| **Objetivo**             | Transformar competências regimentais, responsabilidades e processos em candidatas a entregas.                                                                                                                                   |
| **Dependências**         | S01; B01.                                                                                                                                                                                                                       |
| **Entradas**             | Regimento; descrição de competências; cadeia de valor; mapa de processos; lista de atividades; responsabilidades da unidade.                                                                                                    |
| **Saídas**               | Lista de entregas candidatas; trecho de origem; título sugerido; justificativa; classificação preliminar; dúvidas para validação da unidade.                                                                                    |
| **Regras principais**    | Não converter automaticamente todo verbo de competência em entrega; separar responsabilidade, atividade, objetivo e produto ou serviço; perguntar qual resultado existe ao final; manter rastreabilidade até o texto de origem. |
| **Teste de aceitação 1** | **Dado** o texto “acompanhar a execução dos contratos”, **quando** processado, **então** o sistema deve reconhecer que a frase descreve atividade ou responsabilidade e solicitar identificação do resultado gerado.            |
| **Teste de aceitação 2** | **Dado** um trecho que mencione a elaboração de relatório, **quando** houver evidência de produto final, **então** o sistema deve propor um título de entrega e vincular a proposta ao trecho original.                         |
| **Teste de aceitação 3** | **Dado** um texto ambíguo, **quando** não for possível identificar o produto ou serviço, **então** a saída deve ser “candidata não confirmada”, com pergunta para validação humana.                                             |

* * *

### S04 — Administrador do Catálogo de Entregas

| Campo                    | Especificação                                                                                                                                                                                                            |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Prioridade**           | P0                                                                                                                                                                                                                       |
| **Objetivo**             | Manter uma biblioteca institucional de entregas reutilizáveis, versionadas e pesquisáveis.                                                                                                                               |
| **Dependências**         | S01; S03; B01.                                                                                                                                                                                                           |
| **Entradas**             | Entregas aprovadas; descrições; classificações; exemplos de metas; critérios de aceite; unidade de origem; processo relacionado.                                                                                         |
| **Saídas**               | Catálogo pesquisável; versões; modelos de referência; registros de uso; sugestões de entregas semelhantes; alertas de duplicidade.                                                                                       |
| **Regras principais**    | Uma entrega do catálogo deve possuir identificador único; alterações devem gerar nova versão; modelos não substituem a validação contextual; unidades podem adaptar exemplos; entradas duplicadas devem ser sinalizadas. |
| **Teste de aceitação 1** | **Dado** um novo título semelhante a uma entrega já cadastrada, **quando** for submetido, **então** o sistema deve apresentar os registros semelhantes antes de criar uma nova entrada.                                  |
| **Teste de aceitação 2** | **Dado** que uma entrega seja atualizada, **quando** a nova versão for aprovada, **então** a versão anterior deve permanecer disponível no histórico.                                                                    |
| **Teste de aceitação 3** | **Dado** um modelo do catálogo, **quando** ele for reutilizado por outra unidade, **então** o sistema deve permitir adaptar meta, prazo, demandante, destinatário e descrição.                                           |

* * *

## 3. Skills de prioridade P1 — Planejamento e MVP

### S05 — Designer de Metas, Indicadores e Critérios de Aceite

| Campo                    | Especificação                                                                                                                                                                                                                                                       |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Prioridade**           | P1                                                                                                                                                                                                                                                                  |
| **Objetivo**             | Definir como a entrega será mensurada, acompanhada e considerada concluída.                                                                                                                                                                                         |
| **Dependências**         | B01; B03; S01; S04.                                                                                                                                                                                                                                                 |
| **Entradas**             | Título; descrição; classificação como projeto ou processo e produto ou serviço; vigência; histórico; capacidade; requisitos do demandante.                                                                                                                          |
| **Saídas**               | Meta final; unidade de medida; indicador; critério de qualidade; critério de aceite; fonte de evidência; responsável pelo aceite; progresso esperado, quando aplicável.                                                                                             |
| **Regras principais**    | Separar meta final de progresso esperado; para projetos, permitir meta binária ou resultado final verificável; para processos, favorecer volume ou desempenho; não usar esforço realizado como substituto do resultado; associar toda meta a evidência verificável. |
| **Teste de aceitação 1** | **Dado** um projeto que termina após a vigência, **quando** a meta for definida, **então** a meta final deve representar a conclusão da entrega e o avanço do ciclo deve ser registrado separadamente como progresso esperado.                                      |
| **Teste de aceitação 2** | **Dado** um processo recorrente, **quando** a meta for elaborada, **então** o sistema deve aceitar quantidade, percentual, prazo médio ou nível de serviço, desde que possuam unidade e fonte de verificação.                                                       |
| **Teste de aceitação 3** | **Dado** o indicador “realizar muitas análises”, **quando** validado, **então** o sistema deve rejeitá-lo como não mensurável e solicitar quantidade, percentual ou parâmetro de desempenho.                                                                        |

* * *

### S06 — Auditor de Portfólio de Entregas

| Campo                    | Especificação                                                                                                                                                                                                                            |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Prioridade**           | P1                                                                                                                                                                                                                                       |
| **Objetivo**             | Analisar a consistência do plano como conjunto de entregas.                                                                                                                                                                              |
| **Dependências**         | B01; B03; S02; S04; S05.                                                                                                                                                                                                                 |
| **Entradas**             | Plano de entregas completo; competências da unidade; prioridades; objetivos institucionais; catálogo; regras de validação.                                                                                                               |
| **Saídas**               | Diagnóstico do portfólio; duplicidades; sobreposições; lacunas; entregas amplas ou pequenas; problemas de meta e prazo; nota de consistência; recomendações de agrupamento ou divisão.                                                   |
| **Regras principais**    | Avaliar o conjunto, não apenas itens isolados; diferenciar problema crítico de oportunidade de melhoria; considerar responsabilidades da unidade; não excluir automaticamente entregas; apresentar justificativa para cada recomendação. |
| **Teste de aceitação 1** | **Dado** um plano com duas entregas semanticamente equivalentes, **quando** auditado, **então** o sistema deve sinalizar possível duplicidade e explicar os elementos coincidentes.                                                      |
| **Teste de aceitação 2** | **Dado** um plano que não represente uma competência relevante da unidade, **quando** comparado com a fonte institucional, **então** o sistema deve indicar possível lacuna de cobertura.                                                |
| **Teste de aceitação 3** | **Dado** um item que descreva apenas “participar de reuniões”, **quando** auditado, **então** deve ser classificado como provável atividade, com proposta de investigação do resultado gerado.                                           |

* * *

### S07 — Planejador de Capacidade da Unidade

| Campo                    | Especificação                                                                                                                                                                                                                                                                 |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Prioridade**           | P1                                                                                                                                                                                                                                                                            |
| **Objetivo**             | Verificar se a unidade dispõe de capacidade compatível com o portfólio planejado.                                                                                                                                                                                             |
| **Dependências**         | B03; B04; S05; S06.                                                                                                                                                                                                                                                           |
| **Entradas**             | Participantes; carga horária útil; férias e afastamentos; estimativas de esforço; prioridades; competências; atividades indiretas; entregas do período.                                                                                                                       |
| **Saídas**               | Capacidade total; capacidade disponível para entregas; demanda estimada; déficit ou folga; cenários; entregas sem cobertura suficiente; recomendações de ajuste.                                                                                                              |
| **Regras principais**    | Considerar carga horária útil, não apenas nominal; permitir estimativas por faixa; não apresentar estimativas como precisão absoluta; distinguir falta de capacidade, falta de competência e dependência externa; preservar percentuais de atividades indiretas justificadas. |
| **Teste de aceitação 1** | **Dado** que a demanda estimada supere a capacidade disponível, **quando** o plano for analisado, **então** o sistema deve apresentar o déficit e pelo menos um cenário de priorização ou ajuste.                                                                             |
| **Teste de aceitação 2** | **Dado** um participante em férias durante parte do ciclo, **quando** a capacidade for calculada, **então** o período de indisponibilidade deve ser descontado.                                                                                                               |
| **Teste de aceitação 3** | **Dado** que uma entrega exija competência inexistente na equipe, **quando** analisada, **então** o sistema deve apontar lacuna de competência, e não apenas insuficiência de horas.                                                                                          |

* * *

### S08 — Matriz de Cobertura das Entregas pela Equipe

| Campo                    | Especificação                                                                                                                                                                                                                                       |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Prioridade**           | P1                                                                                                                                                                                                                                                  |
| **Objetivo**             | Consolidar os planos individuais e demonstrar quem contribui para cada entrega.                                                                                                                                                                     |
| **Dependências**         | B03; B04; S07.                                                                                                                                                                                                                                      |
| **Entradas**             | Plano de entregas; planos de trabalho; participantes; percentuais; competências; responsáveis de referência.                                                                                                                                        |
| **Saídas**               | Matriz entrega × participante; esforço total associado; entregas sem contribuição; concentração de conhecimento; sobrealocações; lacunas de competência.                                                                                            |
| **Regras principais**    | Percentuais individuais não devem ser somados como se representassem percentual de conclusão; cada plano individual deve totalizar 100%; a matriz deve preservar a unidade proprietária da entrega; contribuições externas devem ser identificadas. |
| **Teste de aceitação 1** | **Dado** uma entrega sem participante vinculado, **quando** os planos forem consolidados, **então** ela deve aparecer como “sem cobertura”.                                                                                                         |
| **Teste de aceitação 2** | **Dado** um participante cujo plano totalize 110%, **quando** a matriz for gerada, **então** o sistema deve apontar sobrealocação.                                                                                                                  |
| **Teste de aceitação 3** | **Dado** que apenas uma pessoa detenha a competência crítica de uma entrega, **quando** a cobertura for analisada, **então** o sistema deve sinalizar risco de concentração.                                                                        |

* * *

### S09 — Designer e Auditor de Encadeamento OKR-D

| Campo                    | Especificação                                                                                                                                                                                                                                          |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Prioridade**           | P1                                                                                                                                                                                                                                                     |
| **Objetivo**             | Criar e validar relações entre objetivos, resultados-chave, entregas e atividades.                                                                                                                                                                     |
| **Dependências**         | B01; B02; S01; S05.                                                                                                                                                                                                                                    |
| **Entradas**             | Objetivos; resultados-chave; entregas; indicadores; atividades; planejamento institucional.                                                                                                                                                            |
| **Saídas**               | Mapa OKR-D; matriz de vínculos; justificativas; entregas sem alinhamento; resultados-chave sem suporte; inconsistências lógicas.                                                                                                                       |
| **Regras principais**    | Objetivo deve expressar situação desejada; resultado-chave deve medir avanço; entrega deve ser produto ou serviço; atividade deve explicar como a entrega será produzida; permitir relações muitos-para-muitos; não afirmar causalidade sem evidência. |
| **Teste de aceitação 1** | **Dado** um resultado-chave sem medida observável, **quando** analisado, **então** o sistema deve apontar que ele está formulado como intenção ou atividade.                                                                                           |
| **Teste de aceitação 2** | **Dado** uma entrega sem contribuição plausível para nenhum resultado-chave, **quando** o mapa for construído, **então** ela deve aparecer como “sem alinhamento demonstrado”.                                                                         |
| **Teste de aceitação 3** | **Dado** que uma entrega contribua para dois resultados-chave, **quando** registrada, **então** o sistema deve preservar os dois vínculos e suas justificativas.                                                                                       |

* * *

### S10 — Analisador de Riscos, Dependências e Restrições

| Campo                    | Especificação                                                                                                                                                                                                                                       |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Prioridade**           | P1                                                                                                                                                                                                                                                  |
| **Objetivo**             | Identificar fatores que possam afetar a execução das entregas.                                                                                                                                                                                      |
| **Dependências**         | B03; S05; S07.                                                                                                                                                                                                                                      |
| **Entradas**             | Entrega; prazo; meta; dependências; insumos; decisões pendentes; atores externos; histórico de problemas.                                                                                                                                           |
| **Saídas**               | Registro de riscos; impedimentos; dependências; probabilidade; impacto; resposta; responsável; data de revisão.                                                                                                                                     |
| **Regras principais**    | Diferenciar risco futuro de impedimento atual; todo risco deve possuir causa e impacto; dependência deve ter responsável ou unidade associada; respostas podem ser evitar, reduzir, transferir, aceitar ou acompanhar; decisões permanecem humanas. |
| **Teste de aceitação 1** | **Dado** que uma autorização necessária já esteja atrasada, **quando** registrada, **então** deve ser classificada como impedimento, não como risco futuro.                                                                                         |
| **Teste de aceitação 2** | **Dado** um risco sem impacto descrito, **quando** validado, **então** o sistema deve solicitar a consequência sobre meta, prazo, qualidade ou escopo.                                                                                              |
| **Teste de aceitação 3** | **Dado** uma dependência externa, **quando** registrada, **então** a saída deve identificar a unidade responsável e a data necessária.                                                                                                              |

* * *

## 4. Skills de prioridade P2 — Pactuação e execução

### S11 — Assistente de Pactuação do Plano de Entregas

| Campo                    | Especificação                                                                                                                                                                                         |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Prioridade**           | P2                                                                                                                                                                                                    |
| **Objetivo**             | Apoiar a negociação e a aprovação do plano entre a unidade e a chefia superior.                                                                                                                       |
| **Dependências**         | B03; S02; S06; S07; S10.                                                                                                                                                                              |
| **Entradas**             | Versão proposta; auditoria do portfólio; capacidade; riscos; comentários; contrapropostas; autoridades de aprovação.                                                                                  |
| **Saídas**               | Pauta; resumo executivo; divergências; decisões; condicionantes; versão pactuada; registro de aprovação; itens pendentes.                                                                             |
| **Regras principais**    | O agente não aprova o plano; toda alteração deve ser rastreável; divergências devem ser preservadas; condicionantes devem ter responsável e prazo; versão final deve ser explicitamente identificada. |
| **Teste de aceitação 1** | **Dado** que a chefia proponha redução de meta, **quando** a decisão for registrada, **então** o sistema deve manter a meta anterior no histórico e registrar justificativa e aprovador.              |
| **Teste de aceitação 2** | **Dado** um item ainda pendente, **quando** o plano for consolidado, **então** ele não deve ser apresentado como plenamente pactuado.                                                                 |
| **Teste de aceitação 3** | **Dado** um plano aprovado, **quando** a pactuação for concluída, **então** a saída deve incluir versão, data, participantes e decisões registradas.                                                  |

* * *

### S12 — Assistente de Pactuação do Plano de Trabalho

| Campo                    | Especificação                                                                                                                                                                                                                                      |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Prioridade**           | P2                                                                                                                                                                                                                                                 |
| **Objetivo**             | Apoiar a pactuação mensal entre participante e chefia.                                                                                                                                                                                             |
| **Dependências**         | B04; S07; S08; S11.                                                                                                                                                                                                                                |
| **Entradas**             | Plano de trabalho proposto; carga horária útil; prioridades; entregas pactuadas; atividades indiretas; contribuições externas.                                                                                                                     |
| **Saídas**               | Plano validado; divergências; ajustes de percentuais; contribuições acordadas; justificativas; aprovação.                                                                                                                                          |
| **Regras principais**    | A soma deve totalizar 100%; percentual representa esforço, não conclusão; atividades e tarefas pertencem à descrição da contribuição; contribuições para outras unidades devem possuir anuência; percentuais indiretos devem ser contextualizados. |
| **Teste de aceitação 1** | **Dado** um plano que totalize 90%, **quando** submetido à pactuação, **então** o sistema deve informar que 10% da capacidade permanece não alocada.                                                                                               |
| **Teste de aceitação 2** | **Dado** que o participante registre “participar de reuniões” como entrega, **quando** validado, **então** o sistema deve movê-lo para descrição de contribuição ou atividade indireta, conforme o caso.                                           |
| **Teste de aceitação 3** | **Dado** uma contribuição para outra UE sem anuência, **quando** o plano for pactuado, **então** ela deve permanecer pendente de autorização.                                                                                                      |

* * *

### S13 — Check-in de Execução e Monitoramento

| Campo                    | Especificação                                                                                                                                                                                                       |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Prioridade**           | P2                                                                                                                                                                                                                  |
| **Objetivo**             | Registrar o avanço das entregas durante o ciclo.                                                                                                                                                                    |
| **Dependências**         | S11; S12; S10; S17.                                                                                                                                                                                                 |
| **Entradas**             | Entrega pactuada; progresso anterior; evidências; avanços; impedimentos; riscos; decisões; previsão atualizada.                                                                                                     |
| **Saídas**               | Registro de check-in; situação; progresso realizado; evidências; desvios; próximos passos; decisões necessárias.                                                                                                    |
| **Regras principais**    | Não substituir meta por relato de esforço; progresso deve estar associado a evidência ou justificativa; distinguir atraso, bloqueio e mudança de escopo; não alterar o plano original sem acionar o replanejamento. |
| **Teste de aceitação 1** | **Dado** que o usuário relate apenas atividades realizadas, **quando** fizer o check-in, **então** o sistema deve perguntar qual avanço ocorreu na entrega.                                                         |
| **Teste de aceitação 2** | **Dado** um prazo em risco, **quando** o check-in for concluído, **então** a saída deve registrar o desvio e indicar necessidade de decisão ou replanejamento.                                                      |
| **Teste de aceitação 3** | **Dado** que nenhuma mudança formal seja aprovada, **quando** o monitoramento for salvo, **então** a meta e o prazo pactuados devem permanecer inalterados.                                                         |

* * *

### S14 — Gestor de Alterações e Replanejamento

| Campo                    | Especificação                                                                                                                                                                                                                                   |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Prioridade**           | P2                                                                                                                                                                                                                                              |
| **Objetivo**             | Controlar mudanças em entregas e planos durante a execução.                                                                                                                                                                                     |
| **Dependências**         | S11; S13; S02.                                                                                                                                                                                                                                  |
| **Entradas**             | Solicitação de mudança; versão atual; justificativa; impacto; autoridade; nova proposta; evidências.                                                                                                                                            |
| **Saídas**               | Análise de impacto; versão nova; histórico; decisão; itens afetados; comunicação de alteração.                                                                                                                                                  |
| **Regras principais**    | Nunca sobrescrever a versão pactuada; toda alteração deve possuir justificativa; mudanças relevantes exigem aprovação; cancelamento, suspensão e substituição são situações diferentes; impactos sobre planos de trabalho devem ser propagados. |
| **Teste de aceitação 1** | **Dado** uma mudança de prazo aprovada, **quando** registrada, **então** o sistema deve preservar o prazo original e criar nova versão.                                                                                                         |
| **Teste de aceitação 2** | **Dado** o cancelamento de uma entrega, **quando** processado, **então** as contribuições individuais relacionadas devem ser identificadas para redistribuição.                                                                                 |
| **Teste de aceitação 3** | **Dado** uma solicitação sem autoridade competente, **quando** submetida, **então** ela deve permanecer como proposta, sem modificar o plano vigente.                                                                                           |

* * *

### S15 — Gestor de Contribuições Interunidades

| Campo                    | Especificação                                                                                                                                                                                                              |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Prioridade**           | P2                                                                                                                                                                                                                         |
| **Objetivo**             | Administrar contribuições de participantes para entregas pertencentes a outras unidades.                                                                                                                                   |
| **Dependências**         | S01; S08; S12; S14.                                                                                                                                                                                                        |
| **Entradas**             | Entrega proprietária; unidade responsável; unidade colaboradora; participantes; percentuais; anuências; prazo; responsabilidade pelo aceite.                                                                               |
| **Saídas**               | Acordo de contribuição; vínculos entre unidades; matriz de esforço; autorizações; alertas de dupla contagem; acompanhamento.                                                                                               |
| **Regras principais**    | A entrega pertence a uma unidade proprietária; contribuição externa não cria nova entrega; esforço não deve ser contado duas vezes; a chefia de origem deve autorizar; responsabilidade pelo aceite deve permanecer clara. |
| **Teste de aceitação 1** | **Dado** que duas unidades registrem a mesma entrega como própria, **quando** os dados forem consolidados, **então** o sistema deve solicitar definição da unidade proprietária.                                           |
| **Teste de aceitação 2** | **Dado** um participante colaborando externamente, **quando** o plano individual for validado, **então** o percentual deve aparecer uma única vez em sua alocação total.                                                   |
| **Teste de aceitação 3** | **Dado** que a contribuição externa termine, **quando** encerrada, **então** o registro deve preservar período, esforço, entregas relacionadas e anuências.                                                                |

* * *

## 5. Skills de prioridade P3 — Avaliação e inteligência gerencial

### S16 — Avaliador de Entregas

| Campo                    | Especificação                                                                                                                                                                                                                       |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Prioridade**           | P3                                                                                                                                                                                                                                  |
| **Objetivo**             | Apoiar a avaliação das entregas ao final do ciclo ou de sua conclusão.                                                                                                                                                              |
| **Dependências**         | S05; S13; S14; S17.                                                                                                                                                                                                                 |
| **Entradas**             | Meta; realizado; critérios de qualidade; prazo; evidências; aceite; alterações; riscos; fatores externos.                                                                                                                           |
| **Saídas**               | Resultado da avaliação; alcance da meta; qualidade; prazo; justificativas; fatores externos; aprendizado; pendências.                                                                                                               |
| **Regras principais**    | Avaliar entrega, não presença ou quantidade de atividades; considerar critérios previamente pactuados; distinguir não conclusão, conclusão parcial e conclusão com ressalvas; registrar fatores externos; preservar decisão humana. |
| **Teste de aceitação 1** | **Dado** uma entrega concluída em quantidade, mas sem qualidade mínima, **quando** avaliada, **então** o sistema não deve classificá-la automaticamente como integralmente alcançada.                                               |
| **Teste de aceitação 2** | **Dado** um atraso decorrente de dependência externa documentada, **quando** avaliado, **então** esse fator deve aparecer separadamente do resultado final.                                                                         |
| **Teste de aceitação 3** | **Dado** que não existam evidências suficientes, **quando** a avaliação for executada, **então** a saída deve indicar insuficiência de comprovação.                                                                                 |

* * *

### S17 — Organizador de Evidências

| Campo                    | Especificação                                                                                                                                                                                                                                                |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Prioridade**           | P3, mas necessário como versão simplificada em S13.                                                                                                                                                                                                          |
| **Objetivo**             | Vincular documentos, registros e demais comprovações às entregas.                                                                                                                                                                                            |
| **Dependências**         | S01; S05.                                                                                                                                                                                                                                                    |
| **Entradas**             | Arquivos; links; processos; registros de sistema; indicadores; atas; aprovações; manifestações dos destinatários.                                                                                                                                            |
| **Saídas**               | Repositório indexado; vínculo entrega-evidência; tipo; período; autoria; suficiência; sensibilidade; observações.                                                                                                                                            |
| **Regras principais**    | Evidência deve possuir origem e relação com a entrega; não expor conteúdo sensível indevidamente; distinguir evidência de execução e de resultado; permitir múltiplas evidências; não declarar suficiência quando o critério de aceite não estiver definido. |
| **Teste de aceitação 1** | **Dado** um documento sem relação identificável com a entrega, **quando** anexado, **então** o sistema deve solicitar justificativa do vínculo.                                                                                                              |
| **Teste de aceitação 2** | **Dado** um arquivo potencialmente sensível, **quando** processado, **então** deve ser marcado para controle de acesso antes da divulgação.                                                                                                                  |
| **Teste de aceitação 3** | **Dado** um critério de aceite que exige aprovação formal, **quando** houver apenas minuta, **então** a evidência deve ser classificada como parcial.                                                                                                        |

* * *

### S18 — Gerador de Relatório Gerencial do PGD

| Campo                    | Especificação                                                                                                                                                                                                    |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Prioridade**           | P3                                                                                                                                                                                                               |
| **Objetivo**             | Consolidar informações dos planos para acompanhamento gerencial.                                                                                                                                                 |
| **Dependências**         | S06; S07; S08; S10; S13; S16.                                                                                                                                                                                    |
| **Entradas**             | Planos; check-ins; avaliações; capacidade; riscos; alterações; vínculos estratégicos; filtros de unidade e período.                                                                                              |
| **Saídas**               | Relatórios; painéis; indicadores; síntese executiva; lista de decisões necessárias; exportações.                                                                                                                 |
| **Regras principais**    | Manter rastreabilidade até os dados de origem; não misturar planejado, realizado e avaliado; permitir agregação sem exposição individual desnecessária; indicar dados incompletos; evitar rankings sem contexto. |
| **Teste de aceitação 1** | **Dado** um filtro por unidade e período, **quando** o relatório for gerado, **então** todos os indicadores devem respeitar os filtros aplicados.                                                                |
| **Teste de aceitação 2** | **Dado** que parte das unidades não tenha atualizado o monitoramento, **quando** houver consolidação, **então** o relatório deve indicar a incompletude dos dados.                                               |
| **Teste de aceitação 3** | **Dado** um indicador agregado, **quando** o usuário solicitar sua origem, **então** o sistema deve permitir rastrear os registros que o compõem.                                                                |

* * *

### S19 — Analisador de Aprendizado entre Ciclos

| Campo                    | Especificação                                                                                                                                                                                                                         |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Prioridade**           | P3                                                                                                                                                                                                                                    |
| **Objetivo**             | Identificar padrões históricos que ajudem a melhorar ciclos futuros.                                                                                                                                                                  |
| **Dependências**         | S14; S16; S18; histórico mínimo de dois ciclos.                                                                                                                                                                                       |
| **Entradas**             | Planos históricos; metas; resultados; alterações; capacidade; riscos; atrasos; avaliações; justificativas.                                                                                                                            |
| **Saídas**               | Padrões; hipóteses; tendências; recomendações; entregas recorrentes com problemas; parâmetros para o próximo ciclo.                                                                                                                   |
| **Regras principais**    | Correlação não deve ser apresentada como causalidade; resultados devem informar período e tamanho da amostra; preservar contexto institucional; permitir revisão humana; não utilizar dados individuais para inferências inadequadas. |
| **Teste de aceitação 1** | **Dado** um único ciclo, **quando** a análise histórica for solicitada, **então** o sistema deve informar que não há base suficiente para tendência.                                                                                  |
| **Teste de aceitação 2** | **Dado** que determinada entrega tenha sido adiada em vários ciclos, **quando** o padrão for detectado, **então** o sistema deve apresentar as evidências e hipóteses, sem afirmar automaticamente a causa.                           |
| **Teste de aceitação 3** | **Dado** um padrão baseado em poucos registros, **quando** exibido, **então** a saída deve indicar baixa confiança.                                                                                                                   |

* * *

### S20 — Importador, Exportador e Integrador de Planos

| Campo                    | Especificação                                                                                                                                                                                                    |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Prioridade**           | P3, com importação simples recomendada no MVP.                                                                                                                                                                   |
| **Objetivo**             | Permitir entrada, saída e intercâmbio de dados com planilhas, documentos e sistemas.                                                                                                                             |
| **Dependências**         | S01; modelo de dados comum; S02; S04.                                                                                                                                                                            |
| **Entradas**             | Planilhas; arquivos CSV; formulários; APIs; modelos institucionais; seleções de exportação.                                                                                                                      |
| **Saídas**               | Registros normalizados; relatório de erros; arquivos exportados; dados para painéis; logs de integração.                                                                                                         |
| **Regras principais**    | Validar estrutura antes de importar; não descartar linhas com erro silenciosamente; manter identificadores; detectar duplicidade; registrar origem; proteger dados; permitir pré-visualização antes da gravação. |
| **Teste de aceitação 1** | **Dado** um arquivo com colunas ausentes, **quando** importado, **então** o sistema deve apresentar os campos faltantes e não concluir a gravação sem correção.                                                  |
| **Teste de aceitação 2** | **Dado** um arquivo com linhas válidas e inválidas, **quando** processado, **então** o sistema deve informar claramente quais registros podem ser importados e quais precisam de correção.                       |
| **Teste de aceitação 3** | **Dado** um registro com identificador já existente, **quando** importado, **então** o sistema deve solicitar escolha entre atualizar, ignorar ou criar nova versão.                                             |

* * *

## 6. Dependências resumidas

| Skill | Dependências mínimas              |
| ----- | --------------------------------- |
| S01   | Nenhuma                           |
| S02   | S01 + validadores B01/B03/B04     |
| S03   | S01 + B01                         |
| S04   | S01 + S03 + B01                   |
| S05   | B01 + B03 + S01                   |
| S06   | S02 + S04 + S05                   |
| S07   | B03 + B04 + S05                   |
| S08   | B03 + B04 + S07                   |
| S09   | B01 + B02 + S01                   |
| S10   | B03 + S05 + S07                   |
| S11   | S02 + S06 + S07 + S10             |
| S12   | B04 + S07 + S08 + S11             |
| S13   | S11 + S12 + S10                   |
| S14   | S02 + S11 + S13                   |
| S15   | S08 + S12 + S14                   |
| S16   | S05 + S13 + S14 + S17             |
| S17   | S01 + S05                         |
| S18   | S06 + S07 + S08 + S10 + S13 + S16 |
| S19   | S14 + S16 + S18 + histórico       |
| S20   | S01 + S02 + modelo de dados comum |

* * *

## 7. Sequência recomendada de desenvolvimento

### Incremento 1 — Núcleo conceitual

1. Modularizar B01, B02, B03 e B04.

2. Criar modelo comum de dados.

3. Desenvolver S01 e S02.

4. Definir esquema de versionamento e fontes.

**Resultado esperado:** regras institucionais e validadores compartilhados.

### Incremento 2 — Formação do portfólio

1. Desenvolver S03.

2. Desenvolver S04.

3. Desenvolver S05.

4. Integrar com B01 e B03.

**Resultado esperado:** competências transformadas em entregas completas e mensuráveis.

### Incremento 3 — Qualidade e viabilidade do plano

1. Desenvolver S06.

2. Desenvolver S07.

3. Desenvolver S08.

4. Desenvolver S09 e S10.

**Resultado esperado:** plano coerente, alinhado e compatível com a capacidade.

### Incremento 4 — Pactuação

1. Desenvolver S11.

2. Desenvolver S12.

3. Implementar controle de versões e aprovações.

**Resultado esperado:** planos pactuados com registro das decisões.

### Incremento 5 — Execução

1. Desenvolver S13.

2. Desenvolver S14.

3. Desenvolver S15.

4. Implementar versão inicial de S17.

**Resultado esperado:** acompanhamento e replanejamento rastreáveis.

### Incremento 6 — Avaliação e inteligência

1. Concluir S17.

2. Desenvolver S16.

3. Desenvolver S18.

4. Desenvolver S19.

5. Desenvolver S20.

**Resultado esperado:** avaliação, consolidação, aprendizado e interoperabilidade.

* * *

## 8. Critérios globais de pronto

Uma skill somente deve ser considerada concluída quando atender aos seguintes critérios:

| Dimensão                   | Critério                                                                             |
| -------------------------- | ------------------------------------------------------------------------------------ |
| **Entrada**                | Possui esquema de entrada documentado e valida campos obrigatórios.                  |
| **Saída**                  | Produz resposta estruturada, reutilizável por outras skills.                         |
| **Rastreabilidade**        | Informa quais dados, regras e fontes sustentam a saída.                              |
| **Transparência**          | Diferencia fato, regra, recomendação, inferência e dúvida.                           |
| **Controle humano**        | Não toma decisões reservadas a chefias, participantes ou instâncias de aprovação.    |
| **Versionamento**          | Preserva versões anteriores quando houver alteração de plano ou regra.               |
| **Interoperabilidade**     | Utiliza identificadores e campos compatíveis com o modelo comum de dados.            |
| **Proteção de dados**      | Respeita permissões e evita exposição indevida de informações pessoais ou sensíveis. |
| **Testes**                 | Possui testes positivos, negativos, de ambiguidade e de integração.                  |
| **Experiência do usuário** | Explica problemas e apresenta ação corretiva, em vez de apenas rejeitar entradas.    |

* * *

## 9. Escopo recomendado para o MVP do projeto

O MVP pode ser composto por:

* S01 — Configurador Institucional;

* S02 — Verificador Normativo;

* S03 — Extrator de Competências;

* S04 — Catálogo de Entregas;

* S05 — Designer de Metas;

* S06 — Auditor de Portfólio;

* S07 — Planejador de Capacidade;

* S08 — Matriz de Cobertura;

* S09 — Designer e Auditor de Encadeamento OKR-D;

* S10 — Analisador de Riscos, Dependências e Restrições; e

* versão operacional de B01, B03 e B04.

Esse recorte permite demonstrar um fluxo completo:

> Documento institucional → competências → entregas candidatas → validação → 4Q1P → metas e aceite → portfólio → capacidade → distribuição entre participantes.

Ele também delimita um problema suficientemente claro: avaliar se um agente especializado consegue aumentar a qualidade, a consistência e a viabilidade dos planos de entregas e planos de trabalho.
