# 01 — Visão do produto e governança

## 1. Finalidade

Este capítulo traduz o projeto para gestores, analistas e pessoas novas. A descrição
técnica está no [capítulo 02](02-arquitetura-tecnologia-dados.md).

## 2. Problema público

Planejar e acompanhar o PGD exige combinar competências regimentais, normas gerais,
orientações do ICMBio, capacidade disponível, metas, riscos, contribuições individuais e
evidências. Quando essas partes são tratadas separadamente, surgem entregas vagas, metas
sem critério, sobrecarga, vínculos estratégicos frágeis e avaliações pouco rastreáveis.

O agente organiza o raciocínio e os registros. Ele não substitui a chefia, o participante,
o analista, a autoridade normativa ou a decisão administrativa.

## 3. Proposta de valor

| Dor | Capacidade | Benefício esperado |
| --- | --- | --- |
| Normas e orientações dispersas | RAG com citação | resposta verificável |
| Indicadores sujeitos a erro manual | ferramenta Denodo | número reproduzível |
| Planos heterogêneos | S01–S24 | processo e contrato comuns |
| Decisões sem histórico | modelo versionado | auditoria e aprendizagem |
| Dado ausente preenchido por suposição | perguntas pendentes | transparência da lacuna |

## 4. Objetivos e indicadores

Os resultados RK01–RK10 são definidos na proposta principal. O acompanhamento usa:

| Indicador | Fórmula ou observação | Frequência |
| --- | --- | --- |
| Skills aprovadas | fichas que concluíram os sete passos / 24 | bimestral |
| Cobertura de testes | casos executados / casos previstos | por gate |
| Exatidão determinística | cálculos corretos / casos de cálculo | por versão |
| Citações válidas | respostas com fonte correta / respostas avaliadas | por bateria |
| Perguntas explícitas | lacunas registradas / lacunas identificadas | por piloto |
| Retrabalho | horas de correção / horas efetivas | bimestral |
| Vazamentos | ocorrências confirmadas | contínua; meta zero |
| Utilidade percebida | escala e comentários do piloto | por onda/piloto |

## 5. Escopo por estágio

| Capacidade | Protótipo individual | Piloto | Institucional |
| --- | --- | --- | --- |
| RAG público | Sim | Sim | Sim, após governança |
| RAG institucional comum | Local | Controlado | Ambiente aprovado |
| Dados pessoais | Evitar; usar sintéticos | Mínimo autorizado | Regras institucionais |
| Indicadores Denodo | Leitura | Leitura | Leitura com suporte |
| S01–S24 | Desenvolvimento por ondas | Recorte aprovado | Catálogo homologado |
| Interface Microsoft | Experimento | Opcional | Licenciamento próprio |
| SLA | Não | Limitado | A definir |

## 6. Estrutura analítica do projeto

| Bloco | Entregas |
| --- | --- |
| 1. Governo | proposta, ADRs, riscos, questões, atas e fontes |
| 2. Plataforma | ambiente, banco, API, motor de skills, RAG, indicadores e observabilidade |
| 3. Negócio | catálogo S01–S24, regras, exemplos, contratos e testes |
| 4. Qualidade | automação, segurança, homologação, regressão e métricas |
| 5. Adoção | capacitação, piloto, suporte, avaliação e decisão institucional |

## 7. Papéis

| Papel | No protótipo | Responsabilidade que não pode ser confundida |
| --- | --- | --- |
| Responsável pelo produto | Desenvolvedor individual | priorizar e explicar valor |
| Analista de negócio | Acumulado provisoriamente | propor regras e exemplos, sem autoaprovação institucional |
| Arquiteto/desenvolvedor | Desenvolvedor individual | código, dados, integrações e documentação |
| Testador | Desenvolvedor individual | registrar evidência; não omitir falha |
| Validador institucional | Analistas/autoridade futura | confirmar regra, vocabulário e uso real |
| Responsável por dados | A definir | autorizar tratamento e controles |
| TI institucional | Consultada/futura | identidade, rede, publicação e suporte |

## 8. RACI

Legenda: R = executa; A = aprova; C = consultado; I = informado.

| Atividade | Desenvolvedor | Analistas | Autoridade | TI | Participantes piloto |
| --- | :---: | :---: | :---: | :---: | :---: |
| Planejar backlog | R/A | C | I | I | I |
| Especificar skill | R | A futuro | I | I | C |
| Aprovar fonte/Q5 | R (prepara) | R | A | C | I |
| Implementar | R/A | C | I | C | I |
| Homologar regra | C | R | A quando necessário | I | C |
| Autorizar piloto | C | C | A | R/C | I |
| Operar protótipo | R/A | I | I | I | — |
| Operar solução institucional | C | C | A | R | R |

## 9. Ritos

| Rito | Frequência | Saída |
| --- | --- | --- |
| Planejamento do ciclo | quinzenal | objetivo, capacidade e limite de trabalho em andamento |
| Revisão da entrega | quinzenal | demonstração e defeitos |
| Revisão de capacidade | a cada 8 semanas | baseline atualizada |
| Revisão de risco | bimestral ou por evento | matriz atualizada |
| Gate da onda | fim da onda | decisão de avançar, corrigir ou aguardar |
| Revisão normativa | por mudança e trimestral | fontes, vigência e conflitos |

## 10. Fluxo de decisão

1. Registrar a questão com contexto e item bloqueado.
2. Identificar quem tem autoridade.
3. Preparar opções e evidências.
4. Manter o sistema em estado seguro enquanto não houver resposta.
5. Registrar a decisão em ADR, ata ou `decisoes_humanas`, conforme natureza.
6. Atualizar regra, teste e documentação afetados.

## 11. Mudança de catálogo

Uma inclusão, divisão, fusão ou retirada de skill exige análise de dependências, impacto em
contratos, cronograma, banco, testes e riscos. O ID não é reutilizado. Uma mudança
incompatível cria nova versão da ficha e do contrato.

## 12. Critérios para adoção institucional

- piloto autorizado e avaliado;
- ambiente e identidade aprovados;
- licenças adequadas ao uso institucional;
- política de dados e retenção definida;
- suporte, monitoramento e continuidade definidos;
- testes de segurança concluídos;
- responsável institucional designado;
- Q5 e regras críticas validadas;
- plano de reversão e incidentes disponível.

Sem esses itens, o produto permanece protótipo individual.
