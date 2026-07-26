# Proposta de Projeto — `pgd-agente-icmbio`

**Versão:** 1.0 | **Data:** 26.07.2026
**Papel assumido nesta proposta:** Arquiteto de Soluções de IA e Gerente de Projetos, com foco
didático para desenvolvedor iniciante.

---

## 1. Raciocínio e premissas

### 1.1. Como decompus o pedido

O pedido tem duas dimensões que precisam de tratamento simultâneo, não sequencial:

1. **Aprendizado** — você está começando em programação e quer consolidar conceitos de IA de
   forma progressiva, sem pular etapas.
2. **Protótipo institucional** — em algum ponto **antes do fim do roadmap**, um gestor do ICMBio
   precisa conseguir ver algo funcionando dentro do Copilot Studio/Power Platform.

Por isso, esta proposta não trata o protótipo como "Fase 6" isolada. Ela define uma **trilha
paralela** (chamo de "Trilha B") com checkpoints de demonstração acoplados às Fases 1, 3 e 5 do
aprendizado — ver Seção 5.

### 1.2. Premissas assumidas

- O repositório GitHub privado `pgd-agente-icmbio` já existe (confirmado por você), mas a pasta
  local ainda não é um repositório git — a Fase 0 trata disso.
- Os dados consumidos (indicadores agregados I01–I12) não contêm dados pessoais identificáveis,
  então o tratamento de LGPD é simplificado — mas isso não elimina a necessidade de uma nota de
  governança institucional (Seção 7).
- O ICMBio já possui Azure/Microsoft 365 contratado — isso pesa a favor de Azure OpenAI/AI
  Foundry quando o projeto sair do ambiente pessoal de aprendizado.
- **Achado da exploração:** você já redigiu, na própria pasta do projeto, quatro documentos de
  metodologia de negócio — `skill-analise-entrega-v1.md`, `skill-okrd-v1.md`,
  `skill-plano-entregas-v1.md` e `skill-plano-trabalho-v1.md`. Assumi que estes **são os casos de
  uso-âncora** dos futuros agentes (junto com a consulta aos 12 indicadores OCDE), e não exemplos
  genéricos de "assistente de PGD". Toda a arquitetura desta proposta (Seção 4) foi desenhada em
  torno desse achado.

### 1.3. Perguntas em aberto (retomar quando chegar na fase correspondente)

- Você já tem acesso pago a alguma API (Anthropic, OpenAI, Gemini)? Isso decide o ponto de partida
  concreto da Fase 1.
- O Azure AI Foundry já está provisionado no tenant do ICMBio, ou isso dependeria de abrir chamado
  com o TI institucional? Isso afeta o tempo real da Fase 5.
- Os 4 documentos de metodologia devem ser tratados como conhecimento estático (RAG) ou você
  pretende evoluí-los com frequência (o que pesaria a favor de reindexação automática)?

---

## 2. Mini-glossário

| Termo | Definição simples |
| --- | --- |
| **LLM** (Large Language Model) | Modelo de linguagem treinado em grande volume de texto, capaz de gerar respostas coerentes a partir de um prompt (ex.: GPT, Claude, Gemini). |
| **Prompt / system prompt** | Instrução em texto enviada ao LLM. O "system prompt" define o papel/comportamento do agente antes da pergunta do usuário. |
| **RAG** (Retrieval-Augmented Generation) | Técnica em que, antes de perguntar ao LLM, o sistema busca trechos relevantes em uma base de documentos e os injeta no prompt — reduz "invenção" de respostas (alucinação). |
| **Embedding** | Representação numérica (vetor) de um texto, que captura seu significado — permite comparar textos por similaridade matemática. |
| **Banco vetorial** | Banco de dados especializado em armazenar e buscar embeddings por similaridade (ex.: ChromaDB, Pinecone). |
| **Agente vs. chatbot** | Um chatbot responde texto; um **agente** decide e executa ações (chamar uma função, consultar um banco, orquestrar múltiplos passos) para cumprir um objetivo. |
| **Tool calling / function calling** | Mecanismo pelo qual o LLM não só responde texto, mas pode "chamar" uma função de código (ex.: `consultar_indicador(...)`) e usar o resultado na resposta. |
| **Orquestração** | Camada de código que coordena múltiplos passos/agentes/ferramentas em um fluxo coerente (ex.: Agno, LlamaIndex, n8n). |
| **Webhook** | Endpoint HTTP que "escuta" e reage a um evento disparado por outro sistema. |
| **Custom Connector** (Power Platform) | Forma padronizada de o Power Platform/Copilot Studio chamar uma API externa como se fosse um conector nativo. |
| **Copilot Studio topic/action** | No Copilot Studio, um *topic* é um fluxo de conversa; uma *action* é uma chamada a um Custom Connector (ou outro serviço) dentro desse fluxo. |
| **JDBC** | Protocolo Java para conexão a bancos de dados — usado aqui para falar com o Denodo. |
| **Virtualização de dados (Denodo) vs. ETL** | ETL copia/transforma dados para um novo destino; virtualização de dados (Denodo) consulta a fonte original em tempo real, sem cópia intermediária. |

---

## 3. Stack tecnológica — decisões e trade-offs

> Regra seguida aqui: **nenhuma tecnologia foi aceita "porque está na lista"** — cada uma foi
> avaliada com alternativa e trade-off. Onde a lista sugerida no prompt original não é a melhor
> opção, isso é sinalizado explicitamente.

| Camada | Recomendação | Alternativa considerada | Trade-off |
| --- | --- | --- | --- |
| **Modelo/API (Fases 1–3)** | API direta (Anthropic **ou** OpenAI — escolha a que você já usa/testa mais) | Azure OpenAI/AI Foundry desde o início | API direta tem setup em minutos (só uma chave), ideal para aprender conceitos sem burocracia de provisionamento institucional. Custo por uso é baixo em fase de aprendizado. |
| **Modelo/API (Fases 4–5, protótipo institucional)** | Migrar para **Azure OpenAI / AI Foundry** | Manter API direta também em produção | Aproveita contrato e rede já homologados pelo ICMBio (menos fricção de segurança/compliance ao expor para gestores), mas exige abrir processo de provisionamento com o TI — **planeje isso com antecedência**, não na véspera da demo. |
| **Modelos open-source (Hugging Face)** | Não usar como caminho principal agora | Rodar modelo local (ex.: Llama) | Curva de aprendizado e custo de infraestrutura (GPU) altos para o ganho, dado que APIs comerciais já resolvem bem o caso de uso. Vale como exploração pontual na Fase 3, não como dependência do roadmap. |
| **RAG — orquestração** | **LlamaIndex** | LangChain | LlamaIndex tem abstração mais direta para "indexar documentos → consultar" (o caso de uso das 4 skills + fichas OCDE), com menos conceitos genéricos para aprender de início. |
| **Banco vetorial (aprendizado)** | **ChromaDB local** | Pinecone/Weaviate desde já | ChromaDB roda embutido, sem conta externa nem custo — ideal enquanto a base de documentos é pequena (4 skills + 12 fichas). Migrar para Pinecone/Weaviate só quando houver necessidade real de escala/hospedagem gerenciada (provavelmente não antes da Fase 5). |
| **Prototipagem visual de RAG** | **Langflow** | Flowise | Ambos resolvem o mesmo problema (montar visualmente um fluxo RAG). Recomendo Langflow por ter integração mais madura com LlamaIndex (que já é a escolha de orquestração acima) e comunidade Python mais próxima do resto do stack. Se você já tiver familiaridade com Flowise (Node.js/JS), essa é uma alternativa igualmente válida — a decisão não é crítica, ambos são descartáveis após a Fase 2. |
| **Orquestração de código do agente definitivo** | **Agno** (Python) | Construir na mão com LlamaIndex puro | Agno já resolve o padrão "agente com memória + tools + RAG" com menos código boilerplate — apropriado quando você já entende os conceitos (chega na Fase 4) e quer produtividade, não mais aprendizado de fundamentos. |
| **Automação/integração institucional** | Avaliar **n8n** vs. manter em Python puro (FastAPI) | n8n desde a Fase 1 | n8n ajuda a visualizar integrações (Denodo, e-mail, Teams) sem código, mas adiciona uma peça de infraestrutura extra (hospedar o n8n) — só compensa na Fase 5, quando o foco muda de "aprender" para "integrar sistemas institucionais". Manter tudo em Python/FastAPI até lá reduz partes móveis. |
| **Interface para gestores** | **Copilot Studio + Power Platform Custom Connector** | Interface web própria (Streamlit/Gradio) | Copilot Studio aproveita o M365 que os gestores já usam (sem novo login/URL) — mas exige que o backend seja uma API HTTP estável desde cedo (ver Seção 4). Uma interface própria (Streamlit) é mais rápida de prototipar sozinho, e pode servir como *fallback* de demonstração caso o provisionamento do Custom Connector atrase. |

**Recomendação de ordem de decisão:** não trave o início do projeto esperando decidir Azure vs.
API direta — comece com API direta na Fase 1 (decisão de baixo risco, reversível) e volte a essa
tabela na Fase 4/5.

---

## 4. Arquitetura de capacidades do agente

Da exploração dos arquivos já existentes na pasta do projeto, identifiquei que os agentes deste
projeto têm **duas naturezas de capacidade distintas** — e isso deve moldar a arquitetura desde a
Fase 1, não só na Fase 4:

### (A) Capacidade metodológica / redação
Os quatro documentos já escritos por você definem *funções de negócio* baseadas em texto:

- **Análise de Entregas** (`skill-analise-entrega-v1.md`) — diagnostica se um texto representa
  uma entrega válida e propõe título revisado.
- **O que é OKR-D** (`skill-okrd-v1.md`) — explica a metodologia Objetivo → Resultado-chave →
  Entrega → Atividade.
- **Como elaborar um plano de entregas** (`skill-plano-entregas-v1.md`) — conduz a construção
  campo a campo de um plano de entregas.
- **Como elaborar um plano de trabalho** (`skill-plano-trabalho-v1.md`) — deriva o plano de
  trabalho individual a partir do plano de entregas da unidade.

Essas quatro são, na prática, **conhecimento textual estruturado** — o caminho natural é RAG: os
próprios `.md` viram documentos-fonte indexados, e o agente recupera o trecho relevante antes de
responder. Na Fase 1 (antes de existir RAG), elas podem ser usadas diretamente como *system
prompt* — uma simplificação didática, não uma solução final.

### (B) Capacidade de consulta a indicadores (ação/dados ao vivo)
Os 12 indicadores OCDE/PGD (I01–I12) exigem consulta **em tempo real** ao banco Denodo — isso não
é "conhecimento estático", é uma **ação** que o agente precisa executar sob demanda (ex.: "qual a
taxa de cumprimento da minha unidade neste quadrimestre?"). O caminho natural aqui é
**tool/function calling**: uma função Python como `consultar_indicador(indicador, periodo,
unidade)` — inspirada diretamente no padrão `run_query()` do projeto `pgd-ocde-icmbio` (ver
`docs/referencia-pgd-ocde-icmbio.md`) — que o LLM aciona quando identifica essa intenção.

### Por que essa distinção importa para o roadmap

| | Conhecimento (A) | Ação (B) |
| --- | --- | --- |
| Técnica | RAG (embeddings + banco vetorial) | Tool calling (função Python + JDBC) |
| Fase em que aparece pela 1ª vez | Fase 1 (como system prompt simplificado) | Fase 1 (como 1 função simples) |
| Fase em que amadurece | Fase 3 (LlamaIndex + ChromaDB) | Fase 4 (Agno decide quando chamar) |
| Onde convergem | **Fase 4** — o agente Agno tem acesso às duas capacidades ao mesmo tempo, decidindo qual usar conforme a pergunta do gestor. |||

Esse é o motivo de a Fase 4 (Agno) ser o verdadeiro "produto mínimo completo" do projeto — antes
dela, você está construindo as duas metades separadamente por design, não por atraso.

---

## 5. Fase 0 — Ambiente

### 5.1. Estrutura de pastas (scaffolding)

```text
pgd-agente-icmbio/
  src/
    agente/              Código do agente (Fases 1, 4)
    dados/                Módulo de acesso ao Denodo (inspirado no run_query())
    api/                  FastAPI — Trilha B (checkpoints 1–3)
  skills/                 Os 4 .md de metodologia (mover os já existentes para cá)
  data/
    docs_indexados/       Fichas OCDE + skills preparadas para RAG (Fase 3)
    vectorstore/          Banco ChromaDB local (gitignored)
  prototipos/             Exports do Langflow (Fase 2)
  docs/
    referencia-pgd-ocde-icmbio.md   (este documento — já gerado)
  tests/
  .env.example
  .gitignore
  requirements.txt
  README.md
```

Os 4 arquivos `skill-*.md` e o `prompt-planejamento-inicial-v1.md` já presentes na pasta devem ser
movidos para `skills/` (os primeiros) — o prompt de planejamento pode ficar na raiz como registro
histórico, ou mover para `docs/`.

### 5.2. `.gitignore` (Python/IA)

```gitignore
.venv/
__pycache__/
*.pyc
.env
data/vectorstore/
*.ipynb_checkpoints/
.pytest_cache/
```

### 5.3. Extensões VS Code recomendadas

- Python (Microsoft)
- Pylance
- Jupyter
- GitLens
- (Opcional) GitHub Copilot — só se você já tiver licença institucional/pessoal

### 5.4. Ambiente virtual e segredos

```bash
python -m venv .venv
.venv\Scripts\activate
pip install python-dotenv jpype1 pandas fastapi uvicorn
```

`.env.example` (mesmo padrão de nomes de variável usado no `consultas_denodo_template.ipynb` do
projeto antigo — ver `docs/referencia-pgd-ocde-icmbio.md`):

```env
# Denodo — preencher com os valores fornecidos para este projeto (não reutilizar sem confirmar)
DENODO_HOST=
DENODO_PORT=
DENODO_DATABASE=
DENODO_USER=
DENODO_PASSWORD=
DENODO_DRIVER_PATH=
JAVA_HOME=

# LLM (Fase 1 em diante)
ANTHROPIC_API_KEY=
# ou OPENAI_API_KEY=
```

### 5.5. Conectar ao repositório remoto já existente

O repositório `https://github.com/lpchagas/pgd-agente-icmbio.git` já existe, mas a pasta local
ainda não é um repositório git. Passos (rode você mesmo, ou peça para eu rodar mediante sua
confirmação explícita no momento, já que envolve `push` a um repositório remoto):

```bash
git init
git remote add origin https://github.com/lpchagas/pgd-agente-icmbio.git
git add .
git commit -m "Estrutura inicial do projeto pgd-agente-icmbio"
git branch -M main
git push -u origin main
```

> Antes do primeiro commit, confira que `.env` **não** está sendo adicionado (o `.gitignore` da
> Seção 5.2 já cobre isso) e que nenhum dos `skill-*.md` contém dado sensível — eles são
> metodologia de negócio, não deveriam conter dado pessoal, mas vale conferir.

---

## 6. Roadmap — Fases 1 a 5 + Trilha de Protótipo (Trilha B)

### Fase 1 — Scripts Python puro consumindo API

- **Objetivo de aprendizado:** entender o ciclo básico prompt → API → resposta, sem framework.
- **Conceitos-chave:** chamada de API HTTP, system prompt vs. user prompt, variáveis de ambiente,
  tratamento de erro básico.
- **Entregável verificável:** script `src/agente/consulta_skill.py` que recebe o nome de uma das
  4 skills + uma pergunta do usuário, injeta o `.md` correspondente como system prompt, e retorna
  a resposta da API. Mais um script simples `src/dados/consultar_indicador.py` que roda 1 query de
  1 indicador (ex.: I02) via Denodo, reaproveitando o padrão `run_query()`.
- **Pré-requisitos:** Fase 0 concluída; chave de API válida; driver JDBC do Denodo acessível
  (mesmo do projeto antigo).

> **Trilha B — Checkpoint 1 (demo local):** ao final da Fase 1, envolva os dois scripts acima em
> 2 endpoints FastAPI (`POST /skill`, `GET /indicador/{id}`). Teste via `curl` ou Postman. Isso já
> é "demonstrável" no sentido de mostrar a um colega/gestor curioso que o backend responde — ainda
> não é o protótipo institucional, mas prova o conceito ponta a ponta.

### Fase 2 — Prototipagem visual (Langflow) do fluxo de ingestão

- **Objetivo de aprendizado:** visualizar, sem escrever muito código, como um pipeline de RAG é
  composto (carregar documento → dividir em pedaços → gerar embedding → indexar → buscar).
- **Conceitos-chave:** *chunking* (divisão de texto), embedding, fluxo de nós visuais.
- **Entregável verificável:** um fluxo salvo no Langflow que lê os 4 `.md` de skills e as fichas
  `docs/ocde/06.X.X-iXX.md` (referenciadas, não copiadas — ver `docs/referencia-pgd-ocde-icmbio.md`)
  e devolve os pedaços mais relevantes para uma pergunta de teste.
- **Pré-requisitos:** Fase 1 concluída (para já saber o que uma resposta "boa" parece).

### Fase 3 — RAG via código com LlamaIndex + ChromaDB

- **Objetivo de aprendizado:** reproduzir em código Python o que a Fase 2 mostrou visualmente,
  ganhando controle fino sobre o pipeline.
- **Conceitos-chave:** `Document`, `VectorStoreIndex`, `retriever`, top-k, persistência do banco
  vetorial local.
- **Entregável verificável:** módulo `src/agente/rag.py` que indexa `skills/` e
  `data/docs_indexados/` no ChromaDB local e responde perguntas citando de qual documento veio a
  informação.
- **Pré-requisitos:** Fase 2 concluída (conceitos já vistos visualmente).

> **Trilha B — Checkpoint 2 (demo com conhecimento real):** o endpoint `POST /skill` do
> Checkpoint 1 passa a usar o `rag.py` em vez do `.md` fixo como system prompt. A demo já mostra
> respostas fundamentadas em múltiplos documentos, não só na skill "hardcoded".

### Fase 4 — Arquitetura final do agente com Agno

- **Objetivo de aprendizado:** unificar as duas capacidades (RAG + tool calling) em um único
  agente que decide sozinho qual usar, e aprender a expor isso como API estável.
- **Conceitos-chave:** *tool calling*, agente com memória de conversa, orquestração multi-step.
- **Entregável verificável:** agente Agno em `src/agente/agente_pgd.py`, com (a) acesso ao índice
  RAG da Fase 3 e (b) a função `consultar_indicador()` como tool — exposto via FastAPI em
  `src/api/main.py`.
- **Pré-requisitos:** Fases 1–3 concluídas.

### Fase 5 — Integração institucional (Denodo/n8n + Copilot Studio)

- **Objetivo de aprendizado:** entender como conectar um backend próprio a uma plataforma
  institucional (autenticação, contrato de API, Custom Connector).
- **Conceitos-chave:** OpenAPI/Swagger (contrato da API), Custom Connector, Copilot Studio topic,
  autenticação de API (chave ou OAuth).
- **Entregável verificável:** a API da Fase 4 registrada como Custom Connector no Power Platform,
  consumida por um Topic simples no Copilot Studio (ex.: "Pergunte sobre um indicador OCDE").
  Avaliar nesse ponto se vale migrar a consulta ao Denodo para dentro de um fluxo n8n (só se isso
  simplificar manutenção institucional; não é obrigatório).
- **Pré-requisitos:** Fase 4 concluída; decisão tomada sobre Azure OpenAI/AI Foundry (Seção 3).

> **Trilha B — Checkpoint 3 (demo formal a gestores):** este é o marco de demonstração
> institucional citado no pedido original — mas os Checkpoints 1 e 2 já permitiram mostrar
> progresso incremental antes deste ponto, reduzindo o risco de "big bang" no fim do projeto.

---

## 7. Nota de governança de dados (institucional)

Os dados consumidos pelos agentes são **indicadores agregados** (taxas, médias, contagens por
unidade/período) — não há dado pessoal identificável envolvido, o que simplifica a análise sob a
LGPD. Ainda assim, valem os seguintes cuidados institucionais, mesmo sem dado pessoal:

- **Infraestrutura homologada:** ao sair do ambiente de aprendizado pessoal para um protótipo que
  gestores acessarão, priorize componentes já homologados pelo ICMBio (Azure/M365) — reduz
  fricção de segurança institucional (ver decisão de migração na Seção 3).
- **Transparência com gestores:** deixe explícito, na interface do Copilot Studio, que o agente é
  um **apoio à consulta e à redação**, não uma ferramenta de decisão automatizada — evita
  expectativa equivocada sobre o papel do agente.
- **Versionamento e rastreabilidade:** mantenha a mesma disciplina de rastreabilidade já usada no
  `pgd-ocde-icmbio` (indicador, período, fonte, data de extração) para qualquer resposta do agente
  baseada em dado de indicador — se um gestor questionar um número, deve ser possível reconstituir
  de onde ele veio.
- **Política interna de IA:** antes de expor o protótipo além do seu uso pessoal, verifique se o
  ICMBio possui (ou está elaborando) uma política institucional sobre uso de IA generativa — comum
  em órgãos públicos e frequentemente exigida antes de qualquer uso além de prova de conceito
  individual.

---

## 8. Template de README.md

```markdown
# pgd-agente-icmbio

Agentes de IA para consulta e análise de dados do PGD (Programa de Gestão e Desempenho) do
ICMBio, integrando indicadores OCDE (via Denodo) e metodologia de elaboração de planos de
entregas/trabalho (OKR-D).

## Arquitetura

Denodo (petrvs_icmbio) --JDBC--> módulo de dados --tool calling--\
                                                                   >-- Agente (Agno) -- API (FastAPI) -- Custom Connector -- Copilot Studio
Skills (.md) --RAG (LlamaIndex/ChromaDB)-------------------------/

## Pré-requisitos

- Python 3.11+
- Driver JDBC do Denodo (mesmo do projeto `pgd-ocde-icmbio`)
- Chave de API (Anthropic/OpenAI) ou acesso Azure OpenAI/AI Foundry
- (Fase 5) Acesso ao Power Platform / Copilot Studio do ICMBio

## Instalação

\`\`\`bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# preencher .env com suas credenciais
\`\`\`

## Como rodar cada fase

Ver roadmap completo em `proposta-projeto-v1.md`. Referência técnica do projeto de indicadores
original em `docs/referencia-pgd-ocde-icmbio.md`.
```

---

## 9. Checklist de execução

- [ ] **Fase 0** — pastas criadas, `.gitignore`, `.venv`, `.env.example`, repo conectado ao
      remoto existente (`git init` + `remote add` + primeiro push)
- [ ] **Fase 1** — script de skill via API + script de 1 indicador via Denodo
- [ ] **Checkpoint B1** — FastAPI mínimo expondo os dois scripts da Fase 1
- [ ] **Fase 2** — fluxo Langflow de ingestão (skills + fichas OCDE)
- [ ] **Fase 3** — RAG em código (LlamaIndex + ChromaDB) sobre skills + fichas
- [ ] **Checkpoint B2** — endpoint da Fase 1 passa a usar RAG
- [ ] **Fase 4** — agente Agno unificando RAG + tool calling, exposto como API
- [ ] **Fase 5** — Custom Connector + Topic no Copilot Studio; decisão Azure OpenAI tomada
- [ ] **Checkpoint B3** — demo formal a gestores do ICMBio
- [ ] Nota de governança revisada com eventual contato institucional (LGPD/TI) do ICMBio
