## Prompt para desenvolvimento do projeto **"pgd-agente-icmbio"**

---

## 1. PAPEL

Atue como Arquiteto de Soluções de IA e Gerente de Projetos, com estilo
didático voltado a um desenvolvedor iniciante. Além de projetar a solução,
seu papel é me ensinar os fundamentos em cada etapa.

## 2. CONTEXTO DO PROJETO

Estou iniciando o projeto `pgd-agente-icmbio`. Para esta finalidade criei 
a pasta "C:\Projetos\pgd-agente-icmbio". Objetivo final: desenvolver
agentes de IA especializados na consulta e análise de dados do PGD (Programa
de Gestão e Desempenho) do ICMBio, integrando fontes complexas —
especificamente bancos de dados Denodo e indicadores da OCDE.

Os dados utilizados são majoritariamente indicadores agregados, sem dados
pessoais identificáveis. Isso simplifica a análise de LGPD, mas ainda quero
uma nota breve de governança institucional (o ICMBio pode ter política
interna sobre uso de IA/dados, mesmo sem dado pessoal envolvido).

O ICMBio já possui infraestrutura de serviços fornecida pela Microsoft
(Azure/Microsoft 365). Avalie, ao lado das APIs diretas (OpenAI, Anthropic,
Google Gemini) e dos modelos locais via Hugging Face, a opção de usar
Azure OpenAI Service / Azure AI Foundry, considerando vantagens de já
existir contrato/procurement institucional.

## 3. DUPLA FINALIDADE DO PROJETO (ambas devem orientar o plano)

(i) Aprendizado pessoal estruturado e progressivo em desenvolvimento de
    agentes de IA de alta qualidade.
(ii) Produzir, em algum ponto adiantado do roadmap — não só ao final —,
     um protótipo demonstrável para gestores do ICMBio, integrado ao
     Copilot Studio e ao Microsoft Power Platform.

Por isso, o backend dos agentes deve ser modular e exposto como API/Webhook
DESDE O INÍCIO, compatível com o padrão de Custom Connector do Power
Platform, para que o Copilot Studio possa consumi-lo como uma Action.
Proponha no plano como conciliar a trilha de aprendizado profundo (RAG,
vetores, Agno) com uma trilha de protótipo demonstrável mais rápida —
podem ser trilhas paralelas ou pontos de checkpoint no mesmo roadmap.

## 4. MEU PERFIL E RESTRIÇÕES

- Iniciante em programação, buscando aprendizado profissional e estruturado.
  Plano progressivo: cada fase consolida conceitos antes de avançar em
  complexidade.
- Versionamento: repositório privado no GitHub; desenvolvimento local (VS Code).

## 5. STACK TECNOLÓGICO ALVO (uso estratégico e progressivo)

- Modelos/APIs: OpenAI, Anthropic, Google Gemini, Azure OpenAI/AI Foundry;
  open-source via Hugging Face.
- RAG/Dados: LlamaIndex para orquestração de leitura de documentos/dados.
- Bancos vetoriais: ChromaDB (local inicial) → Pinecone/Weaviate (escala).
- Prototipagem visual: Flowise ou Langflow para mapear o fluxo de RAG.
- Orquestração de código: Agno (Python) para os agentes definitivos.
- Automação/Integração institucional: n8n (fluxos internos/Denodo) e
  Copilot Studio + Power Platform (interface para gestores).

IMPORTANTE: para cada tecnologia, justifique a escolha e sinalize trade-offs
ou riscos (incluindo custo, curva de aprendizado e aderência à infraestrutura
Microsoft já existente). Não siga a stack cegamente — aponte quando houver
alternativa mais adequada.

## 6. TAREFA: gere um plano de projeto abrangente contendo

1. **Fase 0 — Ambiente:** estrutura de pastas (scaffolding), `.gitignore`
   para IA/Python, extensões recomendadas do VS Code, setup de ambiente
   virtual e gestão de segredos (.env).
2. **Roadmap (Fases 1 a 5 + trilha de protótipo):** para cada fase, informe:
   (a) objetivo de aprendizado, (b) conceitos-chave, (c) entregável
   verificável, (d) pré-requisitos. Indique explicitamente em que ponto o
   protótipo do Copilot Studio/Power Platform pode ser demonstrado aos
   gestores.
   - Fase 1: scripts em Python puro consumindo APIs.
   - Fase 2: prototipagem visual (Flowise/Langflow) da ingestão de docs do PGD.
   - Fase 3: RAG via código com LlamaIndex e ChromaDB.
   - Fase 4: arquitetura final do agente com Agno, exposta como API.
   - Fase 5: integração institucional — Denodo via n8n, e conexão da API
     como Custom Connector no Copilot Studio/Power Platform.
3. **Nota de governança de dados** (breve): já que os dados são agregados,
   resuma o que ainda merece atenção institucional (ex.: uso de infraestrutura
   já homologada, transparência com gestores, versionamento de indicadores).
4. **Template de README.md:** propósito, arquitetura, pré-requisitos e
   passos de instalação do `pgd-agente-icmbio`.

## 7. COMO VOCÊ DEVE TRABALHAR

- Antes de propor, explique seu raciocínio e quebre a tarefa em subtarefas.
- Explicite premissas assumidas e pergunte quando algo for ambíguo.
- Quando uma decisão for relevante, apresente alternativas com trade-offs e
  recomende uma, justificando.
- Defina termos técnicos ao introduzi-los (mini-glossário), pois sou iniciante.
- Apresente primeiro o PLANO completo e a lista de tarefas. Não crie nenhum
  arquivo ou pasta até eu confirmar o plano.

## 8. FONTE DE REFERÊNCIA (projeto original)

A pasta C:\Projetos\pgd-ocde-icmbio contém o projeto original de indicadores
do PGD/OCDE, já em produção. Ela foi adicionada como diretório de leitura
(--add-dir). Trate-a como REFERÊNCIA SOMENTE LEITURA: não crie, edite,
mova ou execute comandos git dentro dela em nenhuma hipótese.

Antes de propor a estrutura inicial do pgd-agente-icmbio, explore essa pasta
e extraia:

- Os indicadores existentes e suas definições (arquivos .py da "Opção C" e
  eventuais .md de documentação).
- O padrão de conexão e consulta ao Denodo usado em
  consultas_denodo.ipynb (bibliotecas, forma de autenticação, estrutura das
  queries) — isso deve inspirar o módulo de acesso a dados do novo projeto.
- Convenções de nomenclatura e organização de pastas já em uso.

Não copie arquivos do projeto antigo para o novo indiscriminadamente.
Sintetize o que for relevante em um documento próprio do novo projeto
(ex.: docs/referencia-pgd-ocde-icmbio.md), citando de qual arquivo cada
informação veio. Se encontrar credenciais, strings de conexão ou segredos
no projeto antigo, NÃO os copie para o novo repositório — aponte apenas que
existem e que devem ser reconfigurados via variável de ambiente (.env) no
pgd-agente-icmbio.
