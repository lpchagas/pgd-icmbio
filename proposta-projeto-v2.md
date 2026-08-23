# Proposta de Projeto — `pgd-agente-icmbio`

**Versão:** 2.0 (revista e ampliada) | **Data:** 26.07.2026
**Substitui:** `proposta-projeto-v1.md` (mantida como registro histórico)
**Papel assumido nesta proposta:** Consultor independente sênior em engenharia de software e
gestão de projetos.
**Público-alvo do documento:** equipe de projeto formada por **analistas de negócio**, sem
formação em programação. Todo termo técnico usado está no Glossário (Seção 4) e todo
procedimento prático tem tutorial passo a passo (Seção 9).

---

## Sumário executivo

O projeto `pgd-agente-icmbio` constrói, de forma incremental, um **agente de Inteligência
Artificial** capaz de (a) responder perguntas sobre a metodologia de elaboração de Planos de
Entregas e Planos de Trabalho do PGD/ICMBio e (b) consultar, em tempo real, os 12 indicadores
OCDE/PGD calculados no projeto irmão `pgd-ocde-icmbio`. O resultado final será acessível aos
gestores do ICMBio dentro do ambiente Microsoft 365 que já utilizam (Copilot Studio), sem
necessidade de novo sistema, login ou treinamento extenso.

A proposta organiza o trabalho em **6 fases (0 a 5)** com três **pontos de demonstração**
intermediários ("Checkpoints"), de modo que sempre exista algo funcionando para mostrar — o
projeto nunca fica meses "invisível". Cada fase tem objetivo, entregável, critério de aceite e
riscos mapeados. A Seção 9 traz **tutoriais completos**, escritos para quem nunca programou,
cobrindo desde a instalação do ambiente até o teste do agente.

**Três decisões estruturantes desta versão:**

1. **Começar pequeno e barato:** as primeiras fases usam uma chave de API comercial (custo de
   poucos dólares/mês) e ferramentas gratuitas, adiando a burocracia de provisionamento
   institucional para quando houver algo concreto a institucionalizar.
2. **Duas capacidades, uma arquitetura:** o agente combina "conhecimento" (os documentos de
   metodologia já escritos pela equipe) e "ação" (consulta ao banco de indicadores). Essa
   distinção guia todas as escolhas técnicas — ver Seção 5.
3. **Gestão de projeto explícita:** esta versão adiciona papéis e responsabilidades, matriz de
   riscos, critérios de aceite por fase e um plano de capacitação da equipe — ausentes na v1.

---

## O que mudou em relação à v1

| #   | Mudança                                                                                                                                           | Motivo                                                         |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| 1   | Documento reescrito para equipe de **analistas de negócio** (a v1 assumia um único aprendiz de programação)                                       | Adequação ao público real do projeto                           |
| 2   | Glossário ampliado de 13 para 40+ termos, organizado por tema                                                                                     | Autonomia de leitura da equipe                                 |
| 3   | Nova seção de **gestão de projeto**: papéis (RACI), matriz de riscos, critérios de aceite e estimativas de esforço                                | Boas práticas de gestão ausentes na v1                         |
| 4   | Novos **tutoriais completos** (Seção 9): instalação do ambiente, Git/GitHub, primeira chamada de API, consulta ao Denodo, Langflow e teste da API | A v1 listava comandos sem explicá-los                          |
| 5   | Nova seção de **boas práticas de engenharia traduzidas** para linguagem de negócio (Seção 8)                                                      | Nivelamento conceitual da equipe                               |
| 6   | Critérios de qualidade e "definição de pronto" por fase                                                                                           | Evitar fases "quase concluídas" indefinidamente                |
| 7   | Governança de dados ampliada com checklist de verificação pré-publicação                                                                          | Alinhamento com a disciplina já praticada no `pgd-ocde-icmbio` |

---

## 1. Contexto e justificativa

### 1.1. De onde partimos

O ICMBio participa do piloto OCDE/MGI de transformação do PGD (Programa de Gestão e
Desempenho) em instrumento de gestão de desempenho — Portaria ICMBio nº 5.592/2025. O projeto
`pgd-ocde-icmbio` já calcula 12 indicadores (I01–I12) diretamente da base do PETRVS, via
Denodo, e a CGOV já produziu quatro documentos de metodologia de negócio:

- **Análise de Entregas** (`skill-analise-entrega-v1.md`) — diagnostica se um texto representa
  uma entrega válida e propõe título revisado;
- **O que é OKR-D** (`skill-okrd-v1.md`) — explica a cadeia Objetivo → Resultado-chave →
  Entrega → Atividade;
- **Como elaborar um Plano de Entregas** (`skill-plano-entregas-v1.md`) — conduz a construção
  campo a campo;
- **Como elaborar um Plano de Trabalho** (`skill-plano-trabalho-v1.md`) — deriva o plano
  individual a partir do plano da unidade.

### 1.2. O problema que o agente resolve

Hoje, o conhecimento metodológico está em documentos que o gestor precisa localizar, ler e
interpretar; e os indicadores estão em planilhas que exigem intermediação de analista. O agente
elimina as duas fricções: o gestor pergunta em linguagem natural ("minha entrega está bem
formulada?", "qual a taxa de cumprimento da minha unidade neste quadrimestre?") e recebe
resposta fundamentada — citando o documento de metodologia ou o indicador consultado.

### 1.3. Por que construir em fases

Projetos de IA falham com frequência por dois motivos opostos: ambição excessiva no início
(construir "o sistema completo" antes de validar qualquer parte) ou experimentação sem fim
(protótipos que nunca viram produto). O roadmap em fases com checkpoints de demonstração
(Seção 7) ataca os dois riscos: cada fase entrega algo verificável, e os checkpoints obrigam o
projeto a "aparecer" para os gestores em três momentos, não apenas no final.

---

## 2. Objetivos, resultados esperados e escopo

### 2.1. Objetivo geral

Disponibilizar aos gestores do ICMBio um agente de IA, acessível via Copilot Studio (Microsoft
365), que oriente a elaboração de Planos de Entregas e Planos de Trabalho segundo a metodologia
OKR-D e consulte os indicadores OCDE/PGD em tempo real.

### 2.2. Resultados esperados (formato OKR-D, coerente com a metodologia do projeto)

| Resultado-chave                                                            | Como será medido                                                                                |
| -------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| RC1 — Agente responde perguntas metodológicas citando a fonte              | Teste com 20 perguntas reais; ≥ 80% das respostas corretas e com citação do documento de origem |
| RC2 — Agente consulta qualquer um dos 12 indicadores por unidade e período | Teste com os 12 indicadores; resultado idêntico ao CSV oficial do `pgd-ocde-icmbio`             |
| RC3 — Gestor acessa o agente dentro do M365, sem novo login                | Demonstração formal (Checkpoint B3) com ao menos 2 gestores usando o agente                     |
| RC4 — Equipe de analistas opera o ciclo básico sem apoio externo           | Cada analista executa os Tutoriais T1–T4 de forma autônoma                                      |

### 2.3. Escopo

**Dentro do escopo:** agente de consulta e apoio à redação; integração de leitura com o Denodo
(mesmas consultas já validadas no projeto irmão); publicação no Copilot Studio; capacitação da
equipe de analistas.

**Fora do escopo (nesta proposta):** escrita de dados no PETRVS (o agente **não altera**
planos nem avaliações); decisão automatizada de qualquer natureza; uso de dados pessoais
identificáveis; desenvolvimento de aplicativo móvel próprio; treinamento de modelo de IA
próprio (usaremos modelos comerciais prontos).

O que está fora do escopo não é proibido para sempre — é adiado deliberadamente para manter o
projeto entregável. Qualquer inclusão passa por reavaliação formal desta proposta (nova versão).

---

## 3. Premissas e questões em aberto

### 3.1. Premissas

- O repositório GitHub privado `pgd-agente-icmbio` já existe; a pasta local ainda não está
  conectada a ele (o Tutorial T2 resolve isso).
- Os dados consumidos são **indicadores agregados** (taxas, médias, contagens) — sem dado
  pessoal identificável, o que simplifica (mas não elimina) o tratamento de governança
  (Seção 10).
- O ICMBio possui Microsoft 365/Azure contratado, o que favorece o Copilot Studio como
  interface final e o Azure OpenAI como provedor de modelo na fase institucional.
- Os quatro documentos de metodologia são os **casos de uso-âncora** do agente, junto com a
  consulta aos 12 indicadores.
- A equipe é formada por analistas de negócio; o projeto prevê capacitação embutida
  (tutoriais + pareamento), não pressupõe conhecimento prévio de programação.

### 3.2. Questões em aberto (registrar a resposta quando a fase correspondente chegar)

| #   | Questão                                                                          | Decide o quê                          | Quando responder                |
| --- | -------------------------------------------------------------------------------- | ------------------------------------- | ------------------------------- |
| Q1  | Já existe chave de API paga (Anthropic/OpenAI)?                                  | Ponto de partida da Fase 1            | Antes da Fase 1                 |
| Q2  | O Azure AI Foundry está provisionado no tenant do ICMBio ou exige chamado ao TI? | Prazo real da Fase 5                  | Durante a Fase 3 (antecedência) |
| Q3  | Os documentos de metodologia serão evoluídos com frequência?                     | Necessidade de reindexação automática | Durante a Fase 3                |
| Q4  | Quem no TI institucional é o ponto focal para Custom Connector / Copilot Studio? | Caminho de homologação da Fase 5      | Durante a Fase 4                |

---

## 4. Glossário de termos técnicos

> [!NOTE]
> O glossário técnico (IA, RAG, infraestrutura, desenvolvimento) foi extraído para arquivo
> próprio em 23.08.2026, ao lado do glossário institucional de negócio, para ficar mais fácil
> de encontrar. Ver [`docs/gestao/glossario-tecnico.md`](docs/gestao/glossario-tecnico.md).

---

## 5. Arquitetura — como o agente funciona (visão de negócio)

### 5.1. As duas capacidades do agente

A análise dos arquivos existentes na pasta do projeto mostra que o agente precisa de **duas
capacidades de natureza diferente** — e essa distinção orienta todas as decisões técnicas:

**(A) Capacidade de conhecimento — "o bibliotecário".** Os quatro documentos de metodologia
são conhecimento textual estável. A técnica adequada é **RAG**: os próprios `.md` viram a
"biblioteca" indexada; quando o gestor pergunta, o agente localiza os trechos relevantes e
responde com base neles, citando a fonte. Nas fases iniciais (antes do RAG existir), os
documentos são usados diretamente como *system prompt* — simplificação didática, não solução
final.

**(B) Capacidade de ação — "o consultor de plantão".** Os 12 indicadores OCDE/PGD mudam a cada
extração e exigem consulta **em tempo real** ao Denodo. Isso não é conhecimento estático — é
uma **ação** que o agente executa quando percebe a intenção ("qual a taxa de cumprimento da
minha unidade neste quadrimestre?"). A técnica adequada é **tool calling**: uma função
`consultar_indicador(indicador, periodo, unidade)`, inspirada no padrão `run_query()` já
validado no `pgd-ocde-icmbio`, que o modelo aciona sob demanda.

### 5.2. Diagrama simplificado

```text
                 ┌─────────────────────────────────────────────┐
 Gestor ──────►  │           Copilot Studio (M365)             │  ◄── interface final (Fase 5)
                 └──────────────────┬──────────────────────────┘
                                    │ Custom Connector (API)
                 ┌──────────────────▼──────────────────────────┐
                 │        Agente (Agno + FastAPI)              │  ◄── cérebro (Fase 4)
                 │  "Decide: é pergunta de metodologia         │
                 │   ou consulta de indicador?"                │
                 └───────┬──────────────────────────┬──────────┘
             capacidade A│                          │capacidade B
                 ┌───────▼────────┐        ┌────────▼───────────┐
                 │ RAG            │        │ Tool calling       │
                 │ LlamaIndex +   │        │ consultar_         │
                 │ ChromaDB       │        │ indicador()        │
                 │ (4 skills +    │        │ (JDBC → Denodo →   │
                 │ fichas OCDE)   │        │ petrvs_icmbio)     │
                 └────────────────┘        └────────────────────┘
```

### 5.3. Onde as capacidades nascem e onde convergem

|                     | Conhecimento (A)                                                                           | Ação (B)                               |
| ------------------- | ------------------------------------------------------------------------------------------ | -------------------------------------- |
| Técnica             | RAG (embeddings + banco vetorial)                                                          | Tool calling (função Python + JDBC)    |
| Aparece pela 1ª vez | Fase 1 (como system prompt simplificado)                                                   | Fase 1 (como 1 função simples)         |
| Amadurece           | Fase 3 (LlamaIndex + ChromaDB)                                                             | Fase 4 (o agente decide quando chamar) |
| Convergem           | **Fase 4** — o agente Agno tem as duas capacidades e escolhe qual usar conforme a pergunta |                                        |

Por isso a Fase 4 é o verdadeiro "produto mínimo completo": antes dela, as duas metades são
construídas separadamente **por desenho**, não por atraso.

---

## 6. Stack tecnológica — decisões e justificativas

> Regra seguida: **nenhuma tecnologia entra "porque está na moda"** — cada escolha tem
> alternativa considerada e trade-off explícito. Decisões marcadas como *reversíveis* podem ser
> trocadas depois sem retrabalho relevante; as *estruturantes* merecem mais cautela.

| Camada                     | Recomendação                                   | Alternativa considerada           | Justificativa (em linguagem de negócio)                                                                                                                                    | Tipo         |
| -------------------------- | ---------------------------------------------- | --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| Modelo de IA (Fases 1–3)   | **API comercial direta** (Anthropic ou OpenAI) | Azure OpenAI desde o início       | Setup em minutos com uma chave; custo de aprendizado baixo (dólares, não milhares). Evita esperar provisionamento institucional para começar.                              | Reversível   |
| Modelo de IA (Fases 4–5)   | **Migrar para Azure OpenAI / AI Foundry**      | Manter API direta em produção     | Aproveita contrato e rede já homologados pelo ICMBio — menos fricção de segurança ao expor a gestores. Exige abrir processo com o TI **com antecedência** (Q2, Seção 3.2). | Estruturante |
| Modelos open-source locais | **Não usar** como caminho principal            | Rodar um Llama local              | Exigiria equipamento caro (GPU) e conhecimento avançado, para resolver um problema que as APIs comerciais já resolvem. Exploração pontual, no máximo.                      | Reversível   |
| Orquestração de RAG        | **LlamaIndex**                                 | LangChain                         | Abstração mais direta para o nosso caso ("indexar documentos → consultar"), com menos conceitos para a equipe aprender.                                                    | Reversível   |
| Banco vetorial             | **ChromaDB local**                             | Pinecone/Weaviate (nuvem)         | Gratuito, roda embutido, sem conta externa — suficiente para uma base pequena (4 skills + 12 fichas). Migrar para nuvem só se houver necessidade real de escala.           | Reversível   |
| Prototipagem visual de RAG | **Langflow**                                   | Flowise                           | Ambos montam fluxos RAG visualmente (arrastar caixas). Langflow integra melhor com LlamaIndex e Python. Ferramenta **didática e descartável** após a Fase 2.               | Reversível   |
| Framework do agente        | **Agno** (Python)                              | Montar tudo à mão com LlamaIndex  | Agno entrega pronto o padrão "agente com memória + ferramentas + RAG", reduzindo código a manter. Adotado só na Fase 4, quando os conceitos já foram aprendidos.           | Estruturante |
| Automação institucional    | Avaliar **n8n** na Fase 5                      | n8n desde o início                | n8n permite montar integrações visualmente, mas é mais uma peça para hospedar e manter. Só compensa quando o foco virar integração institucional.                          | Reversível   |
| Interface para gestores    | **Copilot Studio + Custom Connector**          | Interface web própria (Streamlit) | Copilot Studio usa o M365 que os gestores já têm — sem novo login, sem nova URL. Streamlit fica como *plano B* de demonstração se a homologação do conector atrasar.       | Estruturante |

**Ordem de decisão recomendada:** não travar o início esperando a definição Azure vs. API
direta. Começar com API direta (decisão reversível, de baixo risco) e revisitar esta tabela na
transição Fase 3 → Fase 4.

**Custo estimado da fase de aprendizado (Fases 1–3):** o consumo de API para testes da equipe
tende a ficar entre US$ 5 e US$ 30/mês. Definir um alerta de gasto no painel do provedor
(ambos permitem limite mensal) é parte do Tutorial T3.

---

## 7. Gestão do projeto

### 7.1. Papéis e responsabilidades (matriz RACI simplificada)

| Atividade                                      | Coordenador do projeto | Analistas de negócio | TI institucional | Gestores (usuários) |
| ---------------------------------------------- | ---------------------- | -------------------- | ---------------- | ------------------- |
| Aprovar esta proposta e suas revisões          | **A**                  | C                    | I                | I                   |
| Executar fases técnicas (0–4)                  | **R**                  | R (com tutoriais)    | I                | —                   |
| Manter documentos de metodologia (skills)      | A                      | **R**                | —                | C                   |
| Validar respostas do agente (testes de aceite) | A                      | **R**                | —                | C                   |
| Provisionar Azure / Custom Connector (Fase 5)  | A                      | C                    | **R**            | I                   |
| Participar das demonstrações (Checkpoints)     | R                      | R                    | I                | **C**               |

*R = Responsável (executa) | A = Aprovador (responde pelo resultado) | C = Consultado |
I = Informado.*

### 7.2. Matriz de riscos

| #   | Risco                                                            | Prob. | Impacto | Mitigação                                                                                                                 |
| --- | ---------------------------------------------------------------- | ----- | ------- | ------------------------------------------------------------------------------------------------------------------------- |
| R1  | Provisionamento Azure/Custom Connector atrasar e travar a Fase 5 | Alta  | Alto    | Iniciar o processo junto ao TI ainda na Fase 3 (Q2/Q4 da Seção 3.2); manter Streamlit como plano B de demonstração        |
| R2  | Agente "alucinar" números de indicadores em demonstração         | Média | Alto    | Indicadores **sempre** via tool calling (nunca "de memória" do modelo); testes de aceite comparando com CSV oficial (RC2) |
| R3  | Credencial (API key / Denodo) vazar em repositório               | Baixa | Alto    | `.gitignore` desde o dia zero; `.env` fora do Git; verificação pré-push (Seção 10.3)                                      |
| R4  | Equipe não conseguir operar as ferramentas (barreira técnica)    | Média | Médio   | Tutoriais da Seção 9 + sessões de pareamento; critério RC4 mede isso explicitamente                                       |
| R5  | Escopo crescer durante o projeto ("já que estamos fazendo…")     | Alta  | Médio   | Seção 2.3 (fora de escopo) + regra de que inclusão exige nova versão da proposta                                          |
| R6  | Dependência de pessoa única (conhecimento concentrado)           | Média | Alto    | Tudo documentado no repositório; cada tutorial executado por ≥ 2 pessoas                                                  |
| R7  | Custo de API sair do controle                                    | Baixa | Baixo   | Limite mensal configurado no provedor (Tutorial T3)                                                                       |

### 7.3. Roadmap com critérios de aceite

Estimativas de esforço em **semanas-calendário com dedicação parcial** (projeto conduzido em
paralelo às atividades regulares da equipe). São referências, não compromissos rígidos.

| Fase | Nome                     | Esforço  | Entregável                                                                                         | Critério de aceite ("pronto quando…")                                                       |
| ---- | ------------------------ | -------- | -------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| 0    | Ambiente                 | 1–2 sem  | Pasta estruturada, `.venv`, `.gitignore`, repo conectado ao GitHub                                 | Todos da equipe rodam `git pull` e ativam o `.venv` sem ajuda (Tutoriais T1–T2)             |
| 1    | Scripts + API            | 2–3 sem  | `consulta_skill.py` (skill como system prompt) e `consultar_indicador.py` (1 indicador via Denodo) | Pergunta metodológica respondida citando a skill; consulta ao I02 confere com o CSV oficial |
| B1   | Checkpoint demo local    | 1 sem    | 2 endpoints FastAPI (`POST /skill`, `GET /indicador/{id}`)                                         | Demonstração ponta a ponta via navegador/Postman para um colega                             |
| 2    | Prototipagem visual      | 1–2 sem  | Fluxo Langflow de ingestão (skills + fichas OCDE)                                                  | Pergunta de teste retorna os trechos certos dos documentos certos                           |
| 3    | RAG em código            | 2–3 sem  | `rag.py` (LlamaIndex + ChromaDB)                                                                   | Respostas citam o documento de origem; índice persiste entre execuções                      |
| B2   | Checkpoint demo RAG      | 1 sem    | Endpoint `/skill` passa a usar o RAG                                                               | Resposta fundamentada em múltiplos documentos, não só na skill fixa                         |
| 4    | Agente unificado         | 3–4 sem  | Agente Agno com RAG + tool calling, exposto via FastAPI                                            | O agente escolhe sozinho a capacidade certa em 10 perguntas mistas de teste                 |
| 5    | Integração institucional | 3–6 sem* | Custom Connector + topic no Copilot Studio                                                         | Gestor acessa pelo M365 e obtém resposta correta (RC3)                                      |
| B3   | Checkpoint demo formal   | 1 sem    | Demonstração a gestores                                                                            | ≥ 2 gestores usam o agente ao vivo; feedback registrado                                     |

\* O prazo da Fase 5 depende do TI institucional (risco R1) — por isso o processo começa antes.

### 7.4. Ritos de acompanhamento

- **Reunião quinzenal de 30 min:** status por fase (verde/amarelo/vermelho), riscos ativados,
  próximos passos. Registro em ata curta no repositório (`docs/atas/`).
- **Revisão de fase:** ao concluir cada fase, verificar o critério de aceite **antes** de abrir
  a seguinte. Fase sem critério atendido não é fase concluída.
- **Registro de decisões:** decisões estruturantes (Seção 6) registradas em
  `docs/decisoes.md` — uma linha por decisão: data, decisão, alternativa descartada, motivo.

---

## 8. Boas práticas de engenharia — traduzidas para a equipe

Estas práticas vêm da engenharia de software profissional. A tradução para o nosso contexto:

1. **Versionar tudo, exceto segredos e dados.** O Git guarda o histórico de cada arquivo de
   código e documento. Credenciais (`.env`) e bases locais **nunca** entram no repositório — o
   `.gitignore` é a barreira. Analogia: o repositório é o processo administrativo oficial; a
   senha do sistema não se anexa ao processo.
2. **Commits pequenos e frequentes, com mensagem clara.** "Adiciona consulta ao indicador I02"
   conta a história; "ajustes" não. Um commit por avanço lógico, não um por semana.
3. **Reprodutibilidade.** Qualquer colega deve conseguir clonar o repositório, seguir o README
   e chegar ao mesmo resultado. Se só funciona na máquina de uma pessoa, não está pronto.
4. **Separar configuração de código.** O código é público (repositório); a configuração
   sensível fica no `.env` local. Trocar a senha não pode exigir mexer no código.
5. **Testar comparando com a verdade conhecida.** O agente consulta os mesmos indicadores que o
   `pgd-ocde-icmbio` já calcula e valida — toda resposta numérica do agente pode (e deve) ser
   conferida contra o CSV oficial. É o nosso "gabarito".
6. **Documentar decisões, não só resultados.** Daqui a um ano, "por que Langflow e não
   Flowise?" terá resposta em `docs/decisoes.md` — evita rediscutir o já decidido.
7. **Incremental sempre.** Cada fase entrega algo que funciona. Nunca reescrever tudo de uma
   vez; nunca acumular seis meses de trabalho sem demonstração.
8. **Simplicidade primeiro.** Só adicionar uma peça (n8n, banco vetorial em nuvem, novo
   framework) quando a dor que ela resolve **já apareceu** — não por antecipação.

---

## 9. Tutoriais completos para a equipe

> **Como usar esta seção.** Os tutoriais são sequenciais (T1 → T6) e assumem **zero**
> experiência prévia. Cada comando vem acompanhado de "o que este comando faz". Execute-os no
> **Prompt de Comando ou PowerShell do Windows** (busque "PowerShell" no menu Iniciar), salvo
> indicação contrária. Se algo der errado, consulte o quadro "Se der errado" ao final de cada
> tutorial — e registre o problema em `docs/duvidas.md` para a próxima pessoa.

### T1 — Preparar o ambiente de trabalho (uma vez por máquina)

**Objetivo:** deixar o computador pronto para o projeto: Python, VS Code e a pasta configurada.

**Passo 1 — Instalar o Python.**
Baixe em <https://www.python.org/downloads/> (versão 3.11 ou superior). Na primeira tela do
instalador, **marque a caixa "Add Python to PATH"** antes de clicar em Install — sem isso, o
Windows não encontra o Python no terminal. Para conferir a instalação, abra o PowerShell e digite:

```powershell
python --version
```

*O que faz: pergunta ao Python instalado qual é sua versão. Resposta esperada: algo como
`Python 3.12.x`. Se aparecer erro "não reconhecido", o PATH não foi marcado — reinstale.*

**Passo 2 — Instalar o VS Code.**
Baixe em <https://code.visualstudio.com/> e instale com as opções padrão. Depois, abra o VS
Code, clique no ícone de blocos (Extensions, barra lateral esquerda) e instale as extensões:
**Python** (Microsoft), **Pylance**, **Jupyter** e **GitLens**.

**Passo 3 — Abrir a pasta do projeto.**
No VS Code: `File → Open Folder → C:\Projetos\pgd-agente-icmbio`. A partir daqui, use o
terminal integrado do VS Code (`Terminal → New Terminal`) — ele já abre dentro da pasta certa.

**Passo 4 — Criar o ambiente virtual.**

```powershell
python -m venv .venv
```

*O que faz: cria a "caixa isolada" `.venv` dentro da pasta do projeto, onde ficarão os pacotes
deste projeto sem interferir no resto do computador. Só se faz uma vez.*

```powershell
.venv\Scripts\activate
```

*O que faz: "entra" na caixa. O terminal passa a mostrar `(.venv)` no início da linha — sinal
de que qualquer pacote instalado ou script rodado usará o ambiente do projeto. **Este comando
se repete toda vez que você abrir um novo terminal para trabalhar.***

> Se o PowerShell recusar com erro de "execution policy", rode uma única vez:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` e tente de novo.

**Passo 5 — Instalar os pacotes do projeto.**

```powershell
pip install python-dotenv jpype1 pandas fastapi uvicorn anthropic
```

*O que faz: o `pip` baixa e instala as bibliotecas listadas: `python-dotenv` (lê o arquivo
`.env`), `jpype1` (ponte com o driver Java do Denodo), `pandas` (tabelas de dados), `fastapi` e
`uvicorn` (criação e execução de APIs), `anthropic` (conversa com o modelo Claude — troque por
`openai` se a equipe optar pela OpenAI).*

**Se der errado:** 90% dos problemas de T1 são (a) PATH não marcado no Passo 1 ou (b) esquecer
de ativar o `.venv`. Confira os dois antes de qualquer outra coisa.

---

### T2 — Git e GitHub: conectar a pasta ao repositório (uma vez) e o ciclo diário

**Objetivo:** colocar a pasta sob controle de versão e conectá-la ao repositório
`https://github.com/lpchagas/pgd-agente-icmbio` já criado.

**Parte A — configuração inicial (feita uma vez, pelo coordenador).**

Antes de tudo, crie o arquivo `.gitignore` na raiz da pasta (VS Code: `File → New File`, nome
exato `.gitignore`) com o conteúdo:

```gitignore
.venv/
__pycache__/
*.pyc
.env
data/vectorstore/
*.ipynb_checkpoints/
.pytest_cache/
```

*O que faz: lista o que o Git deve ignorar. A linha `.env` é a mais importante — é ela que
impede credenciais de irem para o GitHub.*

Em seguida, no terminal (com Git instalado — <https://git-scm.com/download/win>, opções padrão):

```powershell
git init
```

*O que faz: transforma a pasta em repositório Git — cria a estrutura interna de histórico.*

```powershell
git remote add origin https://github.com/lpchagas/pgd-agente-icmbio.git
```

*O que faz: informa ao Git local o endereço do repositório remoto no GitHub ("origin" é o
apelido convencional).*

```powershell
git add .
git commit -m "Estrutura inicial do projeto pgd-agente-icmbio"
```

*O que fazem: `git add .` coloca todos os arquivos (exceto os ignorados) na "bandeja de saída";
`git commit` cria o ponto de salvamento com a mensagem entre aspas.*

```powershell
git branch -M main
git push -u origin main
```

*O que fazem: nomeia a linha principal do histórico como `main` e envia tudo ao GitHub. Na
primeira vez, o Windows abrirá uma janela de login do GitHub — use a conta com acesso ao
repositório.*

**Antes do primeiro push, confira:** rode `git status` e verifique que `.env` **não** aparece
na lista. Se aparecer, o `.gitignore` está errado — corrija antes de continuar.

**Parte B — ciclo diário (todos da equipe).**

```powershell
git pull            # ao COMEÇAR o dia: traz o trabalho dos colegas
# ... trabalha nos arquivos ...
git add .           # ao CONCLUIR um avanço: prepara os arquivos alterados
git commit -m "Descreve o que foi feito em uma frase"
git push            # envia ao GitHub
```

**Se der errado:** o erro mais comum é o *conflito* (duas pessoas alteraram o mesmo trecho).
Não entre em pânico: o Git marca o trecho conflitante no arquivo com `<<<<<<<` e `>>>>>>>`;
escolha a versão correta, apague as marcas, salve e faça `git add .` + `git commit`. Na dúvida,
chame o coordenador — nada se perde no Git.

---

### T3 — Obter a chave de API e fazer a primeira conversa com o modelo

**Objetivo:** ter uma chave de API funcionando, com limite de gasto configurado, e rodar o
primeiro script que conversa com o modelo usando uma skill como system prompt.

**Passo 1 — Criar a conta e a chave.**
No console do provedor escolhido (Anthropic: <https://console.anthropic.com> | OpenAI:
<https://platform.openai.com>): criar conta → cadastrar cartão → gerar uma **API key**. A chave
aparece **uma única vez** — copie-a imediatamente.

**Passo 2 — Configurar limite de gasto.**
No mesmo console, localize *Billing/Limits* e defina um teto mensal (sugestão: US$ 30). Isso
elimina o risco R7 (custo fora de controle).

**Passo 3 — Guardar a chave no `.env` (nunca no código).**
Crie o arquivo `.env` na raiz do projeto (ele já está no `.gitignore`) com:

```env
ANTHROPIC_API_KEY=cole-a-chave-aqui
```

**Passo 4 — Rodar o primeiro script.**
Crie `src/agente/consulta_skill.py` com o conteúdo abaixo (o coordenador pode preparar este
arquivo; o objetivo do tutorial é que **cada analista consiga rodá-lo e entendê-lo**):

```python
"""Primeira conversa com o modelo: usa uma skill .md como system prompt."""
import os
from pathlib import Path
from dotenv import load_dotenv
import anthropic

load_dotenv()                     # lê o arquivo .env e carrega as variáveis
cliente = anthropic.Anthropic()   # usa a ANTHROPIC_API_KEY do .env automaticamente

# 1. Carrega a skill escolhida como "instrução de bastidor" (system prompt)
skill = Path("skills/skill-analise-entrega-v1.md").read_text(encoding="utf-8")

# 2. Pergunta do usuário (troque à vontade para testar)
pergunta = "A entrega 'Melhorar a gestão da unidade' está bem formulada?"

# 3. Envia ao modelo e imprime a resposta
resposta = cliente.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1000,
    system=skill,                              # a metodologia vira a "persona" do agente
    messages=[{"role": "user", "content": pergunta}],
)
print(resposta.content[0].text)
```

Para executar (com o `.venv` ativado):

```powershell
python src/agente/consulta_skill.py
```

*O que esperar: uma análise da entrega segundo os critérios do documento de metodologia — a
mesma lógica que um analista aplicaria, mas gerada pelo modelo orientado pela skill.*

**Se der errado:** erro `authentication` = chave errada ou `.env` no lugar errado (deve estar
na raiz, onde você roda o comando); erro `module not found` = `.venv` não ativado ou pacote não
instalado (volte ao T1, Passo 5).

---

### T4 — Consultar um indicador no Denodo

**Objetivo:** rodar uma consulta real ao banco `petrvs_icmbio` e ver o resultado na tela —
provando que a "capacidade B" (ação) funciona na sua máquina.

**Pré-requisitos:** driver JDBC do Denodo no caminho usado pelo projeto irmão; IP da máquina
liberado pelo Dataprev; credenciais Denodo no `.env` (solicitar ao coordenador — **nunca**
circular por e-mail/chat em texto aberto):

```env
DENODO_HOST=
DENODO_PORT=
DENODO_DATABASE=
DENODO_USER=
DENODO_PASSWORD=
DENODO_DRIVER_PATH=
```

**Passo único — rodar o script de consulta.**
O script `src/dados/consultar_indicador.py` (preparado na Fase 1, seguindo o padrão
`run_query()` do `pgd-ocde-icmbio`) recebe o indicador e o período:

```powershell
python src/dados/consultar_indicador.py --indicador I02 --periodo Q1-2026
```

*O que esperar: uma tabela com a taxa de cumprimento por unidade no período. **Validação
obrigatória:** compare 2–3 unidades com o CSV oficial do projeto irmão — os números devem ser
idênticos. Se divergirem, pare e registre: é exatamente o tipo de problema que os testes de
aceite existem para pegar.*

**Se der errado:** erro de conexão/timeout = IP não liberado pelo Dataprev (abrir solicitação);
erro `class not found` = caminho do driver JDBC errado no `.env`; resultado vazio = conferir se
o período pedido existe (regra de periodicidade: PE quadrimestral e PT mensal em 2026).

---

### T5 — Montar o fluxo RAG visual no Langflow (Fase 2)

**Objetivo:** ver com os próprios olhos, sem escrever código, como um documento vira "base de
conhecimento" consultável.

**Passo 1 — Instalar e abrir o Langflow.**

```powershell
pip install langflow
langflow run
```

*O que faz: instala e inicia o Langflow. Ele abre no navegador, em endereço local
(`http://localhost:7860`) — nada sai da sua máquina.*

**Passo 2 — Montar o fluxo de ingestão.** Na tela do Langflow, crie um fluxo novo e arraste,
conectando na ordem:

1. **File/Directory Loader** — aponte para a pasta `skills/` (os 4 documentos de metodologia);
2. **Text Splitter** — divide os documentos em pedaços (*chunking*); comece com tamanho 1000 e
   sobreposição 200, valores usuais;
3. **Embeddings** — selecione o provedor da sua chave de API (converte pedaços em vetores);
4. **Chroma (Vector Store)** — grava os vetores no banco local;
5. **Retriever + Chat** — permite fazer uma pergunta e ver **quais pedaços** o sistema
   recuperou antes de responder.

**Passo 3 — Testar com perguntas reais.** Use perguntas que os gestores fariam ("como formulo
o título de uma entrega?", "qual a diferença entre entrega e atividade?") e observe os trechos
recuperados. **Critério de aceite da Fase 2:** os trechos vêm do documento certo. Se vierem
trechos irrelevantes, ajuste o tamanho do chunk e repita — esse ajuste fino é aprendizado
central da fase, não perda de tempo.

**Se der errado:** Langflow não abre = porta ocupada (rode `langflow run --port 7861`);
embeddings falham = chave de API ausente nas configurações do componente.

---

### T6 — Testar a API local (Checkpoints B1 e B2)

**Objetivo:** verificar, como um "cliente" faria, que o backend responde — é o ensaio da
integração com o Copilot Studio.

**Passo 1 — Subir a API.**

```powershell
uvicorn src.api.main:app --reload
```

*O que faz: liga o "servidor" local da nossa API (endereço `http://127.0.0.1:8000`). A opção
`--reload` recarrega automaticamente quando o código muda. Deixe este terminal aberto enquanto
testa.*

**Passo 2 — Testar pelo navegador (jeito mais fácil).**
Acesse `http://127.0.0.1:8000/docs`. O FastAPI gera sozinho uma página interativa (Swagger)
listando os endpoints. Clique em `GET /indicador/{id}` → *Try it out* → preencha `I02` →
*Execute* — a resposta aparece na própria página. Faça o mesmo com `POST /skill`, preenchendo a
pergunta no corpo da requisição.

**Passo 3 — Registrar o teste.** Anote em `docs/testes.md`: data, endpoint, pergunta usada,
resposta obtida, correta? (sim/não). Esse registro simples é a base dos critérios RC1 e RC2.

**Se der errado:** `address already in use` = já existe um servidor rodando (feche o terminal
antigo); erro 500 na resposta = problema no código ou credencial — copie a mensagem do terminal
e registre em `docs/duvidas.md`.

---

## 10. Estrutura do repositório e governança de dados

### 10.1. Estrutura de pastas (Fase 0)

```text
pgd-agente-icmbio/
  src/
    agente/               Código do agente (Fases 1 e 4)
    dados/                Acesso ao Denodo (padrão run_query())
    api/                  FastAPI — Checkpoints B1–B3
  skills/                 Os 4 .md de metodologia (mover os existentes para cá)
  data/
    docs_indexados/       Fichas OCDE + skills preparadas para RAG (Fase 3)
    vectorstore/          Banco ChromaDB local (ignorado pelo Git)
  prototipos/             Exports do Langflow (Fase 2)
  docs/
    referencia-pgd-ocde-icmbio.md   Referência técnica do projeto irmão
    decisoes.md           Registro de decisões (Seção 7.4)
    testes.md             Registro de testes de aceite (Tutorial T6)
    duvidas.md            Problemas encontrados e soluções (para a próxima pessoa)
    atas/                 Atas das reuniões quinzenais
  tests/
  .env.example            Modelo do .env, SEM valores preenchidos (versionado)
  .env                    Credenciais reais (NUNCA versionado)
  .gitignore
  requirements.txt        Lista dos pacotes (gerar com: pip freeze > requirements.txt)
  README.md
  proposta-projeto-v1.md  Registro histórico
  proposta-projeto-v2.md  Este documento
```

Os quatro `skill-*.md` da raiz devem ser movidos para `skills/`; o
`prompt-planejamento-inicial-v1.md` vai para `docs/` como registro histórico.

### 10.2. Governança de dados e uso responsável de IA

Os dados consumidos são **indicadores agregados** (taxas, médias, contagens por
unidade/período) — sem dado pessoal identificável, o que simplifica a análise sob a LGPD.
Ainda assim:

- **Infraestrutura homologada na fase institucional.** Ao expor o agente a gestores (Fase 5),
  priorizar componentes já homologados pelo ICMBio (Azure/M365) — reduz fricção de segurança e
  acelera a homologação (ver decisão estruturante na Seção 6).
- **Transparência com os usuários.** A interface no Copilot Studio deve declarar que o agente é
  **apoio à consulta e à redação**, não ferramenta de decisão automatizada. Toda resposta
  numérica deve indicar indicador, período e data da consulta — se um gestor questionar um
  número, deve ser possível reconstituir de onde veio (mesma disciplina de rastreabilidade do
  `pgd-ocde-icmbio`).
- **O agente não escreve no PETRVS.** Acesso somente leitura, reforçado no escopo (Seção 2.3) e
  na credencial utilizada.
- **Política institucional de IA.** Antes de expor o protótipo além do uso da equipe, verificar
  se o ICMBio possui (ou está elaborando) política sobre uso de IA generativa — exigência cada
  vez mais comum em órgãos públicos antes de qualquer uso além de prova de conceito.

### 10.3. Verificação de segurança antes de cada push

Rotina mínima antes de `git push` (mesma disciplina do projeto irmão):

1. `git status` — o `.env` **não** pode aparecer na lista;
2. Busca rápida por credenciais nos arquivos alterados (senha, chave, CPF) — no VS Code,
   `Ctrl+Shift+F` e procurar por `API_KEY=` seguido de valor, `PASSWORD=` seguido de valor;
3. Nenhum CSV de dados ou banco vetorial no commit (o `.gitignore` cobre, mas confira).

---

## 11. Template de README.md

```markdown
# pgd-agente-icmbio

Agente de IA para consulta e apoio à elaboração de Planos de Entregas e Planos de Trabalho do
PGD/ICMBio (metodologia OKR-D), com consulta em tempo real aos 12 indicadores OCDE via Denodo.

## Arquitetura (resumo)

Skills (.md) --RAG (LlamaIndex/ChromaDB)--\
                                            >-- Agente (Agno) -- API (FastAPI) -- Custom Connector -- Copilot Studio
Denodo (petrvs_icmbio) --JDBC/tool calling-/

## Pré-requisitos

- Python 3.11+ | Driver JDBC do Denodo | Chave de API (Anthropic/OpenAI) ou Azure OpenAI
- (Fase 5) Acesso ao Power Platform / Copilot Studio do ICMBio

## Instalação

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   (preencher com suas credenciais — nunca versionar)

## Documentação

- Proposta e roadmap: `proposta-projeto-v2.md`
- Tutoriais para a equipe: `proposta-projeto-v2.md`, Seção 9
- Referência técnica dos indicadores: `docs/referencia-pgd-ocde-icmbio.md`
```

---

## 12. Checklist de execução

- [ ] **Fase 0** — estrutura de pastas, `.gitignore`, `.venv`, `.env.example`, repo conectado
  
      (Tutoriais T1–T2 executados por toda a equipe)
- [ ] **Fase 1** — `consulta_skill.py` e `consultar_indicador.py` funcionando (T3–T4);
  
      resultado do I02 validado contra o CSV oficial
- [ ] **Checkpoint B1** — FastAPI com 2 endpoints testados via `/docs` (T6)
- [ ] **Fase 2** — fluxo Langflow de ingestão validado com perguntas reais (T5)
- [ ] **Fase 3** — `rag.py` (LlamaIndex + ChromaDB) respondendo com citação de fonte
- [ ] **Checkpoint B2** — endpoint `/skill` usando RAG
- [ ] **Fase 4** — agente Agno unificando RAG + tool calling; 10 perguntas mistas de teste ok
- [ ] **Processo Azure/TI iniciado** (durante a Fase 3 — risco R1)
- [ ] **Fase 5** — Custom Connector + topic no Copilot Studio funcionando
- [ ] **Checkpoint B3** — demo formal com ≥ 2 gestores; feedback registrado
- [ ] Governança revisada (Seção 10.2) e verificação pré-push praticada (Seção 10.3)
- [ ] `docs/decisoes.md`, `docs/testes.md` e atas em dia

---

*Documento elaborado como revisão consultiva independente da proposta v1. Alterações de escopo
ou de stack devem gerar a versão 3 deste documento, com registro do motivo em
`docs/decisoes.md`.*


