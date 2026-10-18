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
o analista, a autoridade normativa nem a decisão administrativa.

## 3. Proposta de valor

| Dor | Capacidade | Benefício esperado |
| --- | --- | --- |
| Normas e orientações dispersas | RAG com citação | resposta verificável |
| Indicadores sujeitos a erro manual | ferramenta sobre os resultados certificados | número reproduzível, igual ao oficial |
| Planos heterogêneos | S01–S24 | processo e contrato comuns |
| Decisões sem histórico | modelo versionado | auditoria e aprendizagem |
| Dado ausente preenchido por suposição | perguntas pendentes | transparência da lacuna |
| Medo de expor dado institucional a ferramenta externa | gate de classe no servidor MCP | uso de IA sem vazamento |

## 4. Objetivos e indicadores

Os resultados RK01–RK10 são definidos na proposta principal. O acompanhamento usa:

| Indicador | Fórmula ou observação | Frequência |
| --- | --- | --- |
| Skills aprovadas | fichas que concluíram os sete passos / 24 | a cada quatro ciclos |
| Cobertura de testes | casos executados / casos previstos | por gate |
| Exatidão determinística | cálculos corretos / casos de cálculo | por versão |
| Citações válidas | respostas com fonte correta / respostas avaliadas | por bateria |
| Perguntas explícitas | lacunas registradas / lacunas identificadas | por piloto |
| Retrabalho | horas de correção / horas efetivas | a cada quatro ciclos |
| Recusas do gate de classe | respostas recusadas por classe / chamadas de cliente externo | por gate; cada recusa é revisada |
| Vazamentos | ocorrências confirmadas | contínua; meta zero |
| Utilidade percebida | escala e comentários do piloto | por onda/piloto |

## 5. Escopo por estágio

| Capacidade | Protótipo individual | Piloto | Institucional |
| --- | --- | --- | --- |
| RAG público | Sim | Sim | Sim, após governança |
| RAG institucional comum | Local, com modelo local | Controlado | Ambiente aprovado |
| Dados pessoais | Evitar; usar sintéticos | Mínimo autorizado | Regras institucionais |
| Indicadores | A2 certificados, por piloto | A2 certificados, por piloto | Conforme liberação deliberada |
| S01–S24 | Desenvolvimento por ondas | Recorte aprovado | Catálogo homologado |
| Cliente externo de LLM | Só público, sintético ou agregado k≥5 | Idem | Nova ADR, licença e classificação |
| Interface Microsoft | Experimento | Opcional | Licenciamento próprio |
| SLA | Não | Limitado | A definir |

## 6. Estrutura analítica do projeto

| Bloco | Entregas |
| --- | --- |
| 1. Governo | proposta, ADRs, registro de decisões, riscos, questões, atas e fontes |
| 2. Plataforma | ambiente WSL, banco, contratos, motor de skills, servidor MCP, RAG, indicadores e observabilidade |
| 3. Negócio | catálogo S01–S24, regras, exemplos, contratos e testes |
| 4. Qualidade | suíte automatizada, CI, segurança, homologação, regressão e métricas |
| 5. Adoção | capacitação, piloto, suporte, avaliação e decisão institucional |

## 7. Papéis

| Papel | No protótipo | Responsabilidade que não pode ser confundida |
| --- | --- | --- |
| Responsável pelo produto | Desenvolvedor individual | priorizar e explicar valor |
| Analista de negócio | Acumulado provisoriamente | propor regras e exemplos, sem autoaprovação institucional |
| Arquiteto/desenvolvedor | Desenvolvedor individual, com Claude Code e Antigravity | código, dados, integrações e documentação |
| Testador | Desenvolvedor individual | registrar evidência; não omitir falha |
| Validador institucional | Analistas/autoridade futura | confirmar regra, vocabulário e uso real |
| Responsável por dados | A definir | autorizar tratamento e controles |
| TI institucional | Consultada/futura | identidade, rede, publicação e suporte |

As ferramentas de desenvolvimento escrevem e revisam com o desenvolvedor, mas não
aprovam: o aceite humano continua com as pessoas acima.

## 8. RACI

Legenda: R = executa; A = aprova; C = consultado; I = informado.

| Atividade | Desenvolvedor | Analistas | Autoridade | TI | Participantes piloto |
| --- | :---: | :---: | :---: | :---: | :---: |
| Planejar backlog | R/A | C | I | I | I |
| Especificar skill | R | A futuro | I | I | C |
| Validar casos de teste das fichas | R (prepara) | A | I | — | C |
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
| Revisão de capacidade | a cada quatro ciclos | baseline atualizada |
| Revisão de risco | a cada quatro ciclos ou por evento | matriz atualizada |
| Ciclo gerencial dos indicadores | mensal (1–2 h reservadas) | resultados dos pilotos, sem fórmula nova |
| Gate da onda | fim da onda | decisão de avançar, corrigir ou aguardar |
| Revisão normativa | por mudança e trimestral | fontes, vigência e conflitos |

## 10. Fluxo de decisão

1. Registrar a questão com contexto e item bloqueado.
2. Identificar quem tem autoridade.
3. Preparar opções e evidências.
4. Manter o sistema em estado seguro enquanto não houver resposta.
5. Registrar a decisão conforme a natureza: ADR (arquitetura), registro de decisões do
   projeto (estrutura e processo), ata (regra institucional) ou `decisoes_humanas`
   (execução de skill).
6. Atualizar regra, teste e documentação afetados.

## 11. Mudança de catálogo

Uma inclusão, divisão, fusão ou retirada de skill exige análise de dependências, impacto em
contratos, cronograma, banco, testes e riscos. O ID não é reutilizado. A mudança entra em
`capacidades/catalogo.yaml`, com nova versão da ficha e linha no histórico; uma mudança
incompatível cria também nova versão do contrato.

## 12. Critérios para adoção institucional

- piloto autorizado e avaliado;
- ambiente e identidade aprovados;
- licenças adequadas ao uso institucional, inclusive do cliente de LLM;
- política de dados e retenção definida;
- suporte, monitoramento e continuidade definidos;
- testes de segurança concluídos, inclusive do gate de classe;
- responsável institucional designado;
- Q5 e regras críticas validadas;
- plano de reversão e incidentes disponível.

Sem esses itens, o produto permanece protótipo individual.
