# Glossário técnico de termos de TI e IA

**Última revisão:** 23.08.2026
**Origem histórica:** glossário da segunda revisão, extraído em 23.08.2026 para ficar em arquivo próprio,
ao lado do glossário institucional, e ser mais fácil de encontrar.
**Vínculo v6:** [Portal documental](../projeto-v6/README.md)

> [!NOTE]
> **Distinto do glossário institucional** em
> [`glossario-institucional.md`](glossario-institucional.md), que cobre o vocabulário de
> negócio do Programa de Gestão e Desempenho (normas, guias, ciclo do PGD). Este glossário
> cobre os termos de **tecnologia** usados para construir o agente: Inteligência Artificial,
> técnicas de IA aplicadas ao projeto, infraestrutura/integração e desenvolvimento/versionamento.

### 4.1. Inteligência Artificial — conceitos básicos

| Termo                          | Definição em linguagem simples                                                                                                                                                                                                               |
| ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **IA generativa**              | Categoria de IA que produz conteúdo novo (texto, imagem, código) a partir de instruções em linguagem natural.                                                                                                                                |
| **LLM** (Large Language Model) | "Modelo de linguagem de grande porte" — o motor da IA generativa de texto. Foi treinado com enorme volume de textos e, por isso, consegue responder de forma coerente. Exemplos: GPT (OpenAI), Claude (Anthropic), Gemini (Google).          |
| **Modelo**                     | Nome curto para o LLM específico em uso (ex.: "o modelo Claude Sonnet"). Modelos diferem em custo, velocidade e qualidade.                                                                                                                   |
| **Prompt**                     | A instrução em texto enviada ao modelo. Pode ser uma pergunta simples ou uma instrução longa e estruturada.                                                                                                                                  |
| **System prompt**              | Instrução "de bastidor" que define o papel e as regras do agente antes de qualquer pergunta do usuário (ex.: "Você é um assistente de PGD do ICMBio; responda sempre citando a fonte"). O usuário não a vê, mas ela governa o comportamento. |
| **Token**                      | Unidade de cobrança e de medida dos modelos — aproximadamente ¾ de uma palavra. Os provedores cobram por milhão de tokens processados. Importa para estimar custo.                                                                           |
| **Alucinação**                 | Quando o modelo inventa uma informação com aparência de verdade. É o principal risco de qualidade em agentes de IA — e o motivo de usarmos RAG e citação de fontes (abaixo).                                                                 |
| **Janela de contexto**         | Quantidade máxima de texto que o modelo consegue "enxergar" de uma vez. Documentos maiores que a janela precisam ser divididos — daí o *chunking* (abaixo).                                                                                  |

### 4.2. Técnicas usadas neste projeto

| Termo                                    | Definição em linguagem simples                                                                                                                                                                                                                                                                                                                                                |
| ---------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Chatbot vs. agente**                   | Um chatbot só conversa. Um **agente** decide e executa ações: consultar um banco de dados, chamar uma função, encadear passos — e usa o resultado para responder. Este projeto constrói um agente.                                                                                                                                                                            |
| **RAG** (Retrieval-Augmented Generation) | "Geração aumentada por recuperação". Antes de responder, o sistema **busca** os trechos mais relevantes numa base de documentos confiáveis e os entrega ao modelo junto com a pergunta. O modelo responde com base neles — reduz alucinação e permite citar a fonte. Analogia: em vez de responder de memória, o atendente consulta o manual na sua frente e mostra a página. |
| **Embedding**                            | Tradução de um texto para uma lista de números (vetor) que representa seu **significado**. Textos de significado parecido ficam "próximos" matematicamente — é assim que o RAG encontra os trechos relevantes.                                                                                                                                                                |
| **Banco vetorial**                       | Banco de dados especializado em guardar embeddings e encontrar os mais próximos de uma pergunta. Usaremos o **ChromaDB** (gratuito, roda no próprio computador).                                                                                                                                                                                                              |
| **Chunking**                             | Divisão de um documento longo em pedaços menores ("chunks") antes de indexá-lo. Pedaços bem cortados = busca mais precisa.                                                                                                                                                                                                                                                    |
| **Indexação**                            | O processo completo de preparar documentos para busca: ler → dividir (chunking) → gerar embeddings → gravar no banco vetorial.                                                                                                                                                                                                                                                |
| **Tool calling** (ou *function calling*) | Mecanismo pelo qual o modelo, ao perceber que a pergunta exige uma ação, "aciona" uma função de código previamente cadastrada (ex.: `consultar_indicador(...)`) e usa o resultado na resposta. É o que transforma o chatbot em agente.                                                                                                                                        |
| **Orquestração**                         | A camada de código que coordena tudo: recebe a pergunta, decide entre RAG e tool calling, encadeia passos, monta a resposta. Ferramentas: **LlamaIndex** e **Agno** (ver Seção 6).                                                                                                                                                                                            |
| **Memória de conversa**                  | Capacidade do agente de lembrar o que foi dito antes na mesma conversa ("e no quadrimestre anterior?" só faz sentido se ele lembrar qual indicador estava em pauta).                                                                                                                                                                                                          |

### 4.3. Infraestrutura e integração

| Termo                                       | Definição em linguagem simples                                                                                                                                                                    |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **API** (Application Programming Interface) | "Balcão de atendimento" entre sistemas: um sistema faz um pedido padronizado e o outro responde. Usar a "API da Anthropic" = enviar perguntas ao modelo Claude pela internet, mediante uma chave. |
| **Chave de API** (API key)                  | Senha longa que identifica quem está usando uma API e permite a cobrança. **É credencial sigilosa** — nunca vai para documento, e-mail ou repositório.                                            |
| **Endpoint**                                | Um "guichê" específico de uma API, identificado por um endereço (ex.: `POST /skill`). Cada endpoint faz uma coisa.                                                                                |
| **HTTP / REST**                             | O "idioma" padrão de comunicação entre sistemas na web. `GET` pede informação; `POST` envia informação.                                                                                           |
| **FastAPI**                                 | Ferramenta Python para criar APIs próprias. É como transformaremos nossos scripts em serviços que outros sistemas (Copilot Studio) conseguem chamar.                                              |
| **OpenAPI/Swagger**                         | Documento padronizado que descreve "o cardápio" de uma API (endpoints, parâmetros, respostas). O Power Platform lê esse documento para criar o Custom Connector.                                  |
| **JDBC**                                    | Protocolo de conexão a bancos de dados (via Java). É como o projeto irmão já conversa com o Denodo — reaproveitaremos o mesmo mecanismo.                                                          |
| **Denodo (virtualização de dados)**         | Plataforma que permite consultar a base do PETRVS **em tempo real, sem copiar os dados**. Diferente de ETL, que copia e transforma dados para outro lugar.                                        |
| **Custom Connector** (Power Platform)       | "Adaptador" que ensina o Power Platform/Copilot Studio a chamar a nossa API como se fosse um conector nativo da Microsoft.                                                                        |
| **Copilot Studio — topic e action**         | No Copilot Studio, um *topic* é um roteiro de conversa; uma *action* é o momento em que o roteiro chama a nossa API (via Custom Connector) para buscar uma resposta real.                         |
| **Webhook**                                 | Endereço que "fica escutando" e reage quando outro sistema dispara um evento. Pode aparecer na Fase 5 (integrações via n8n).                                                                      |
| **localhost**                               | Endereço do próprio computador. "Rodar em localhost" = o serviço funciona só na sua máquina, invisível para os demais — perfeito para desenvolvimento.                                            |

### 4.4. Desenvolvimento e versionamento

| Termo                                     | Definição em linguagem simples                                                                                                                                               |
| ----------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Python**                                | Linguagem de programação usada no projeto — a mesma do `pgd-ocde-icmbio`. Legível o bastante para analistas acompanharem o código.                                           |
| **Script**                                | Arquivo de código que executa uma tarefa do início ao fim quando rodado.                                                                                                     |
| **Biblioteca / pacote**                   | Código pronto, feito por terceiros, que instalamos e reutilizamos (ex.: `llama-index`). O `pip` é o instalador de pacotes do Python.                                         |
| **Ambiente virtual** (`.venv`)            | "Caixa isolada" onde ficam os pacotes de UM projeto, sem interferir em outros projetos ou no computador. Sempre ativado antes de trabalhar.                                  |
| **Variável de ambiente / arquivo `.env`** | Forma segura de guardar credenciais fora do código: o código lê "a variável DENODO_PASSWORD" sem que a senha esteja escrita nele. O arquivo `.env` fica só na máquina local. |
| **Git**                                   | Sistema de controle de versões: registra cada alteração dos arquivos, por quem e quando, e permite voltar atrás. Como um "histórico de versões" profissional.                |
| **GitHub**                                | Serviço online que hospeda repositórios Git — cópia de segurança e ponto de colaboração da equipe.                                                                           |
| **Repositório (repo)**                    | A pasta do projeto sob controle do Git, com todo o seu histórico.                                                                                                            |
| **Commit**                                | Um "ponto de salvamento" nomeado no histórico do Git (ex.: "Adiciona consulta ao indicador I02").                                                                            |
| **Push / pull**                           | Enviar commits locais para o GitHub (*push*) e trazer os commits dos colegas para sua máquina (*pull*).                                                                      |
| **`.gitignore`**                          | Lista de arquivos que o Git deve **ignorar** — é a barreira que impede credenciais (`.env`) e dados locais de irem para o GitHub.                                            |
| **README**                                | Arquivo de apresentação do repositório: o que é o projeto, como instalar, como rodar.                                                                                        |
| **VS Code**                               | Editor de código gratuito da Microsoft, usado como ambiente de trabalho do projeto.                                                                                          |
| **Terminal / linha de comando**           | Janela onde se digitam comandos de texto para o computador executar. Os tutoriais da Seção 9 explicam cada comando usado.                                                    |
