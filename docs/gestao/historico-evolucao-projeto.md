# Como o projeto chegou até aqui — histórico consolidado da proposta (v1 a v5)

**Última revisão:** 23.08.2026
**Situação:** documento de apoio (onboarding), **não normativo**
**Documento normativo vigente:** [`proposta-projeto-v5.md`](../../proposta-projeto-v5.md) — em
qualquer divergência de conteúdo, a v5 prevalece sobre este texto
**Estado real de execução:** [`AGENTS.md`](../../AGENTS.md) (raiz do repositório), Seção 10 —
este documento explica **como o plano evoluiu**, não **o que já foi feito**; essas são duas
perguntas diferentes e têm fontes diferentes

> [!NOTE]
> **Termos técnicos usados neste documento**
>
> - **RAG (Retrieval-Augmented Generation / Geração Aumentada por Recuperação):** técnica em
>   que a IA busca trechos de documentos relevantes antes de responder, em vez de confiar só
>   no que aprendeu previamente — assim a resposta pode citar a fonte exata.
>   📚 [O que é RAG — AWS](https://aws.amazon.com/what-is/retrieval-augmented-generation/)
> - **Tool calling / function calling:** mecanismo pelo qual a IA não só responde texto, mas
>   pode "chamar" uma função de código (ex.: consultar um indicador no banco) e usar o
>   resultado real na resposta, em vez de tentar adivinhar o número.
>   📚 [Tool use — documentação Anthropic](https://docs.claude.com/en/docs/build-with-claude/tool-use)
> - **API (Application Programming Interface):** um "balcão de atendimento" entre dois
>   programas — um sistema expõe funções que outro programa pode chamar, sem precisar saber
>   como elas foram implementadas por dentro.
> - **Versão (de um documento ou registro):** cada vez que um conteúdo já registrado muda, o
>   sistema (ou, neste caso, a numeração do documento) cria uma cópia nova em vez de apagar a
>   antiga — assim é sempre possível voltar e ver "como era antes".

---

## 1. Como ler este documento

Este texto existe porque o projeto `pgd-agente-icmbio` foi planejado em **cinco versões
sucessivas** de um documento de proposta — `proposta-projeto-v1.md` até `v5.md` — escritas
entre 26.07.2026 e 18.08.2026, somando quase 3.200 linhas. Cada versão "substituiu" a
anterior como plano de gestão, mas nenhuma delas apaga o que a anterior ensinou: partes
inteiras de v2 e v3 continuam válidas hoje, mesmo com v5 sendo a versão vigente.

Isso é ótimo para rastreabilidade (dá para provar por que cada decisão foi tomada), mas ruim
para quem chega agora e só quer entender o panorama: teria que ler os cinco arquivos, cruzar
referências e adivinhar o que é histórico puro e o que ainda vale.

**Este documento resolve isso** contando a evolução de forma linear, uma vez só, com tabelas
e explicações para quem não programa. Ele:

- **NÃO substitui a v5** como documento de planejamento — se este texto e a v5 divergirem em
  algum detalhe, a v5 está certa.
- **NÃO é o lugar para ver o que já foi feito** — isso muda toda semana e vive em
  [`AGENTS.md`](../../AGENTS.md) §10 (Estado do projeto), atualizado a cada sessão de trabalho.
- **É o lugar certo** para: entender por que o projeto tem 5 versões de proposta, o que mudou
  em cada uma e por quê, encontrar os tutoriais completos de configuração do ambiente (T1–T6,
  vindos da v2), e saber onde os documentos originais foram guardados.

### Trilha de leitura por perfil

| Se você é... | Leia primeiro |
| --- | --- |
| **Analista de negócio novo na equipe** | Seção 2 (linha do tempo) → Seção 3 (visão geral) → Seção 6 (skills) |
| **Gestor/coordenador** | Seção 2 (linha do tempo) → Seção 7 (gestão do projeto) → Seção 8 (riscos) |
| **Pessoa nova configurando o ambiente pela primeira vez** | Seção 11 (Tutoriais T1–T6) direto |
| **Quem quer entender uma decisão técnica específica** | Seção 4 (arquitetura) → [`docs/gestao/decisoes/`](decisoes/) para o ADR correspondente |

---

## 2. Linha do tempo v1 → v5

| Versão | Data | Papel na cadeia de decisão | Status hoje |
| --- | --- | --- | --- |
| **v1** | 26.07.2026 | Documento fundador. Escrito para um único desenvolvedor aprendiz, não para a equipe. | Histórico puro — não usar como referência |
| **v2** | 26.07.2026 | Reescrita para a equipe de analistas de negócio; adiciona gestão de projeto e tutoriais completos | **Parcialmente vigente**: Tutoriais T1–T6 continuam material de referência (reincorporados na Seção 11 deste documento); o Glossário foi extraído para [`glossario-tecnico.md`](glossario-tecnico.md) |
| **v3** | 26.07.2026 | Integra a análise da pasta `skills/` e introduz a 3ª capacidade do agente (skills executáveis) | Rotulado "histórico", mas sua estrutura de gestão (EAP, RACI, ciclo de vida de skill) foi mantida sem reescrita por v4 e v5 — é histórico **estrutural**, não descartável |
| **v4** | 26.07.2026 | Revisão dirigida: troca a persistência de SQLite para MySQL 8 local | Histórico, mas seu modelo de dados (21 tabelas) é o **estado técnico real do banco hoje** — a migração `002` da v5 (33 tabelas) ainda não foi aplicada |
| **v5** | 18.08.2026 | Adiciona a Fase 2 (execução e avaliação do PGD, skills S21–S24) sem alterar o MVP S01–S10 | **Vigente** — documento normativo atual |

### O que mudou em cada passagem

**v1 → v2** (mesma data, revisão imediata): reescrita para o público real do projeto —
analistas de negócio sem formação em programação, não um único desenvolvedor aprendiz.
Acrescentou: glossário ampliado (13 → 40+ termos), gestão de projeto explícita (papéis RACI,
matriz de riscos R1–R7, critérios de aceite), tutoriais completos passo a passo (Seção 9) e
boas práticas de engenharia traduzidas para linguagem de negócio (Seção 8).

**v2 → v3** (mesma data): a equipe da CGOV produziu, entre a v2 e a v3, quatro documentos na
pasta `skills/` (`01_analise-skills`, `02_matriz-desenvolvimento-skills`,
`03_especificacao-funcional-skills`, `04_backlog-mvp-skills`) que redefiniram as 4 skills de
metodologia — antes tratadas como simples texto a indexar via RAG — como um **ecossistema
modular de regras negociais**: validadores compartilhados, modelo de dados comum, contratos de
entrada/saída e testes de aceitação. A v3 formalizou isso com quatro decisões estruturantes:
roadmap único de 8 incrementos (I0–I7), a **3ª capacidade do agente** (skills executáveis,
além de conhecimento/RAG e ação/tool calling), papéis adaptados à equipe real (em vez dos 10
papéis profissionais do backlog original) e um ciclo de vida padronizado de 7 passos para cada
skill.

**v3 → v4** (mesma data): revisão dirigida por uma única causa — a análise técnica do esquema
do sistema PETRVS ([AT-01](../tecnologia/AT-01_analise-petrvs-esquema-mysql_v1.md)) mostrou que
o sistema-fonte já pratica em produção as mesmas convenções ("regras de ouro") que o projeto
exigia de si mesmo: identidade persistente por UUID, imutabilidade por versionamento, auditoria
temporal. Isso tornou o SQLite planejado na v3 uma camada de tradução desnecessária. A v4
adotou **MySQL 8 Community local** com um esquema de 21 tabelas modelado sobre as convenções do
PETRVS — decisão registrada em [ADR-006](decisoes/ADR-006-persistencia-mysql.md) (D1–D4). O
restante do plano da v3 (EAP, RACI, ciclo de vida de skill, roadmap I0–I7) foi mantido sem
alteração de mérito.

**v4 → v5** (18.08.2026, a única passagem com salto de data — 23 dias): a equipe produziu o
documento `skills/05_plano-skills-execucao-avaliacao_v1.md`, que analisou a base normativa do
PGD (IN nº 24/2023, cadernos ENAP, documentos internos CGGE/ICMBio, Acórdão TCU nº 2.082/2022),
extraiu 36 regras normativas (RN-01 a RN-36) e especificou um bloco novo de 4 skills — a fase
de **execução e avaliação** do PGD, que antes só aparecia de forma genérica em três skills de
baixa prioridade. A v5 formaliza cinco decisões (a registrar em um ADR-007 ainda não escrito):
o bloco S21–S24 entra no catálogo oficial como **Fase 2**, com roadmap próprio (E0–E7); três
skills do catálogo original são reposicionadas; o modelo de dados ganha uma migração `002`
planejada (33 tabelas, ainda não aplicada); as regras informais de avaliação da CGOV passam a
ser tratadas explicitamente como "regra institucional", não norma; e o risco de rede ao Denodo
(RP16) entra formalmente na matriz. **O MVP original (S01–S10, Incrementos I0–I7) não muda.**

---

## 3. Visão geral do projeto

O `pgd-agente-icmbio` constrói, de forma incremental, um agente de Inteligência Artificial
para apoiar gestores do ICMBio na elaboração e no acompanhamento de **Planos de Entregas** e
**Planos de Trabalho** do Programa de Gestão e Desempenho (PGD). O agente é acessado dentro do
Microsoft 365 que o ICMBio já usa (via Copilot Studio), sem exigir sistema novo ou treinamento
extenso dos gestores.

### As capacidades do agente (evolução)

| Capacidade | O que faz | Desde qual versão |
| --- | --- | --- |
| **A — Conhecimento metodológico (RAG)** | Responde perguntas sobre a metodologia do PGD, sempre citando a fonte | v1 |
| **B — Ação / consulta de indicadores** | Consulta em tempo real os 12 indicadores OCDE/PGD via Denodo (tool calling) | v1 |
| **C — Skills executáveis** | Regras negociais estruturadas (S01–S10), com validadores, contratos e saídas rastreáveis — o núcleo do produto | v3 |
| **D — Execução e avaliação** | Bloco S21–S24, apoiando o registro e a avaliação dos planos já em execução | v5 (Fase 2 — ainda não iniciada) |

### Escopo e regra de crescimento

Uma regra se manteve estável desde a v2 e é aplicada rigorosamente: **o escopo só cresce por
uma nova versão da proposta, nunca por acréscimo informal** ("já que estamos fazendo...").
Esse é, inclusive, o risco RP09 da matriz (Seção 8) — e a própria v5 é o exemplo de como essa
regra funciona na prática: a Fase 2 só entrou no projeto porque um documento de análise
completo (`skills/05`) justificou a mudança e uma nova versão formal a registrou.

---

## 4. Arquitetura técnica

> [!NOTE]
> **Mais termos técnicos usados nesta seção**
>
> - **JDBC (Java Database Connectivity):** protocolo padrão para um programa se conectar a um
>   banco de dados — usado aqui para o agente "conversar" com o Denodo.
> - **UUID (Universally Unique Identifier):** um código longo e praticamente impossível de se
>   repetir, usado como identidade permanente de um registro (ex.: uma entrega, um risco) —
>   diferente de um número sequencial (1, 2, 3...), que pode colidir entre sistemas diferentes.
> - **Trigger (gatilho):** uma regra guardada dentro do próprio banco de dados que dispara
>   automaticamente quando algo é alterado — usada aqui para **impedir** que um registro
>   histórico seja apagado ou sobrescrito, mesmo por acidente.
> - **ENUM:** um tipo de campo de banco de dados que só aceita um valor de uma lista fixa
>   predefinida (ex.: só "Norma", "Institucional", "Recomendação" ou "Exemplo") — evita erro
>   de digitação e valores inconsistentes.
> - **JSON (JavaScript Object Notation):** um formato de texto estruturado, parecido com uma
>   ficha com campos e valores, usado para guardar informação mais flexível dentro de um campo
>   de banco de dados.

### Evolução do modelo de dados

| Versão | Persistência | Estado |
| --- | --- | --- |
| v3 | SQLite (arquivo local único) | Substituída antes de ser implementada |
| v4 | **MySQL 8 Community local**, 21 tabelas, 6 triggers de imutabilidade | **Estado técnico real do banco hoje** |
| v5 (planejado) | Migração `002`: +12 tabelas (33 no total), +8 triggers (14 no total) | Ainda **não aplicada** — depende da Fase 2 iniciar |

### As cinco regras de ouro (vigentes desde v3, detalhadas em `AGENTS.md` §3)

1. Todo objeto tem identidade persistente (UUID + código legível, ex.: `ENT-2026-0001`).
2. Toda alteração gera uma **nova versão** — a anterior nunca é sobrescrita (garantido por
   trigger no banco, não só por convenção de código).
3. Toda saída automática do agente registra origem, regra aplicada e nível de confiança.
4. Decisões humanas são registradas separadamente das saídas do agente.
5. Dado ausente vira **pergunta pendente** — nunca é preenchido silenciosamente pelo agente.

---

## 5. Roadmap e execução

O plano de execução também evoluiu de nome e granularidade a cada versão:

| Versão | Unidade de planejamento |
| --- | --- |
| v1 | 6 Fases (0 a 5) + uma "Trilha B" paralela de demonstrações |
| v2 | As mesmas 6 fases, com critérios de aceite e riscos mapeados por fase |
| v3–v4 | **8 Incrementos (I0 a I7)** — substituem as fases; cada incremento entrega capacidade técnica **e** conteúdo negocial que se validam mutuamente |
| v5 | Incrementos I0–I7 mantidos (Fase 1) **+ 8 Etapas novas (E0 a E7)** para a Fase 2, com 18–24 semanas estimadas |

Os **checkpoints de demonstração** (B1, B2, B3 e, a partir da v5, B4) marcam os momentos em
que algo funcionando é mostrado à equipe — a intenção, presente desde a v1, é que o projeto
nunca fique meses "invisível" entre uma demonstração e outra.

> [!NOTE]
> **Onde ver o que já foi executado, e não apenas planejado**
> Este documento e a própria v5 descrevem o **plano**. O **estado real** — o que já foi
> concluído, o que está bloqueado e por quê — muda a cada sessão de trabalho e vive em
> [`AGENTS.md`](../../AGENTS.md) §10, atualizado com data. Por exemplo: a v5 (18.08.2026) ainda
> registrava o risco RP16 (rota de rede ao Denodo) como bloqueio aberto do Incremento I0; ele
> foi mitigado quatro dias depois (22.08.2026) — um fato que só existe em `AGENTS.md`, não no
> texto da v5.

---

## 6. Skills executáveis

### Ciclo de vida de uma skill (7 passos, definido na v3, mantido em v4/v5)

1. **Especificar** — o que a skill faz, entradas e saídas esperadas (trabalho do analista).
2. **Definir regras** — as regras negociais que a skill aplica, com fonte (trabalho do analista).
3. **Anotar exemplos** — casos reais anotados para servir de referência e teste (analista).
4. **Validar** — revisão humana da especificação antes de qualquer código (analista).
5. **Implementar** — codificar a skill seguindo o contrato definido (técnico).
6. **Integrar** — conectar a skill ao restante do sistema (técnico).
7. **Medir** — acompanhar métricas de qualidade e uso (técnico).

Os passos 1–4 são deliberadamente não técnicos: qualquer analista de negócio pode e deve
participar deles sem depender de quem programa — é o mecanismo que a v3 criou para permitir
que as duas frentes do projeto (negócio e tecnologia) avancem juntas.

### Catálogo de skills

| Bloco | Skills | Foco | Desde |
| --- | --- | --- | --- |
| Institucional | S01, S02 | Fontes normativas e regras institucionais | v3 (MVP) |
| Portfólio | S03–S06 | Elaboração e auditoria de entregas | v3 (MVP) |
| Viabilidade | S07, S08 | Capacidade de execução da equipe | v3 (MVP) |
| Estratégia/risco | S09, S10 | OKR-D e registro de riscos | v3 (MVP) |
| *(fora do MVP)* | S11–S20 | Reservado — inclusão exige nova versão da proposta (regra RP09) | — |
| Execução e avaliação | **S21–S24** | Registro e avaliação de Planos de Entregas/Trabalho já em execução | v5 (Fase 2, ainda não iniciada) |

S21–S24, por skill: **S21** registro de execução do Plano de Entregas (pela chefia da
unidade), **S22** avaliação do Plano de Entregas (pela chefia superior), **S23** registro de
execução do Plano de Trabalho (pelo participante), **S24** avaliação do Plano de Trabalho
(pela chefia da unidade). A v5 também reposiciona três skills do catálogo original: S13 é
reduzida a um check-in informal, S16 passa a subordinada a S22, e S17 é antecipada para a
etapa E2 da Fase 2.

---

## 7. Gestão do projeto

Estrutura mantida desde a v3, ainda em uso:

- **EAP (Estrutura Analítica do Projeto)** — decompõe o trabalho em entregáveis; ampliada na
  v5 para incluir a Fase 2.
- **Papéis e responsabilidades (RACI)** — adaptados, desde a v3, à equipe efetivamente
  disponível (não aos dez papéis profissionais idealizados no backlog original).
- **Catálogo de séries de artefatos** — cada documento do projeto tem um prefixo que indica
  sua natureza: `GP` (gestão de projeto), `AT` (análise técnica), `AN` (análise de negócio),
  `QA` (qualidade/teste).
- **Ritos** — reuniões, revisão de riscos e o processo de registrar decisões arquiteturais em
  ADRs (ver [`docs/gestao/decisoes/`](decisoes/)).

---

## 8. Matriz de riscos — evolução histórica

A matriz de riscos também foi renumerada ao longo das versões:

| Versão | Nomenclatura | O que aconteceu |
| --- | --- | --- |
| v2 | R1–R7 | Primeira matriz de riscos do projeto |
| v3–v4 | RP01–RP15 | R1–R7 foram fundidos com riscos identificados nos artefatos de backlog da pasta `skills/` e renumerados |
| v5 | + RP16–RP24 | RP16 (rota de rede ao Denodo) formalizado; RP17–RP24 adicionados para os riscos específicos da Fase 2 (S21–S24) |

O **registro ativo e atualizado** — com status corrente de cada risco — vive em
[`docs/gestao/riscos.md`](riscos.md), não neste documento. Alguns destaques de evolução, a
título de contexto histórico:

- **RP09** ("o escopo cresce informalmente") é o único risco que, segundo o próprio registro,
  já se **materializou uma vez, pelo rito previsto**: a v5 incorporou a Fase 2 seguindo
  exatamente o processo que RP09 exige (nova versão formal), sem alterar o MVP.
- **RP16** (rede ao Denodo) foi identificado em 26.07.2026, formalizado na matriz apenas na
  v5 (18.08.2026) e mitigado em 22.08.2026 — um ciclo de vida completo que ilustra por que o
  registro ativo (`riscos.md`) e a proposta (histórica por natureza) precisam ser lidos juntos,
  nunca um no lugar do outro.
- **RP17–RP24** são riscos da Fase 2, que só começa após o Incremento I2 — não afetam o
  aceite do I0 atual.

---

## 9. Governança de dados e LGPD

A preocupação com dados pessoais está presente desde a v1 (nota de governança) e foi ampliada
progressivamente:

- **v1–v2:** nota de governança e checklist de verificação antes de publicar qualquer código
  ou documento (`.gitignore` desde o primeiro commit).
- **v3–v4:** o espelho mínimo de servidores (`ref_usuarios`) é desenhado para sincronizar
  **apenas as unidades-piloto** (CGOV e COCAGE), sem CPF, e-mail ou situação funcional —
  decisão D2 do [ADR-006](decisoes/ADR-006-persistencia-mysql.md); relatórios usam
  pseudônimos, nunca nomes reais.
- **v5:** acrescenta um invariante de arquitetura explícito — **dados sensíveis de saúde
  nunca são persistidos**, mesmo quando mencionados em uma intercorrência a registrar (apenas
  categoria e impacto em horas, nunca conteúdo clínico) — e reforça, em mais um invariante,
  que **o agente nunca atribui conceito de avaliação de desempenho**: qualquer parecer
  automatizado precisa de homologação humana explícita.

---

## 10. Glossário técnico

O glossário de termos técnicos (RAG, embeddings, banco vetorial, tool calling, JDBC, e mais de
40 outros termos) foi originalmente a Seção 4 da v2. Em 23.08.2026 ele foi extraído para um
arquivo próprio — **[`docs/gestao/glossario-tecnico.md`](glossario-tecnico.md)** — para não
ficar preso dentro de um documento de proposta datado. Use aquele arquivo como referência de
vocabulário técnico; a Seção 4 da v2 original está hoje vazia (com uma nota apontando para o
novo local — ver Seção 14 abaixo). Para vocabulário de **negócio** do PGD (não técnico de TI),
veja [`docs/gestao/glossario-institucional.md`](glossario-institucional.md).

---

## 11. Tutoriais completos T1–T6

> [!NOTE]
> **Como usar esta seção.** Os tutoriais são sequenciais (T1 → T6) e assumem **zero**
> experiência prévia em programação. Cada comando vem acompanhado de "o que este comando faz".
> Execute-os no **Prompt de Comando ou PowerShell do Windows** (busque "PowerShell" no menu
> Iniciar), salvo indicação contrária. Estes tutoriais vêm da v2 (Seção 9, 26.07.2026); os
> caminhos de arquivo e comandos abaixo foram conferidos e atualizados em 23.08.2026 para
> refletir a estrutura atual do repositório — onde algo mudou desde a v2, há uma nota
> explícita.

### T1 — Preparar o ambiente de trabalho (uma vez por máquina)

**Objetivo:** deixar o computador pronto para o projeto: Python, VS Code e a pasta configurada.

**Passo 1 — Instalar o Python.**
Baixe em <https://www.python.org/downloads/>. Na primeira tela do instalador, **marque a
caixa "Add Python to PATH"** antes de clicar em Install — sem isso, o Windows não encontra o
Python no terminal. Para conferir a instalação, abra o PowerShell e digite:

```powershell
python --version
```

*O que faz: pergunta ao Python instalado qual é sua versão. Resposta esperada: algo como
`Python 3.14.x` (o ambiente atual do projeto usa Python 3.14 — ver `AGENTS.md` §4). Se
aparecer erro "não reconhecido", o PATH não foi marcado — reinstale.*

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
pip install -r requirements.txt
```

*O que faz: instala todas as bibliotecas já fixadas no arquivo `requirements.txt` do
repositório (`PyMySQL`, `python-dotenv`, `JPype1`, `anthropic`, `fastapi`, `uvicorn` — a v2
original listava os pacotes um a um; hoje eles ficam centralizados nesse arquivo, então basta
apontar para ele).*

**Se der errado:** a maioria dos problemas de T1 é (a) PATH não marcado no Passo 1 ou (b)
esquecer de ativar o `.venv`. Confira os dois antes de qualquer outra coisa.

---

### T2 — Git e GitHub: conectar a pasta ao repositório (uma vez) e o ciclo diário

**Objetivo:** colocar a pasta sob controle de versão e conectá-la ao repositório
`https://github.com/lpchagas/pgd-agente-icmbio` já criado.

**Parte A — configuração inicial (já feita; para referência histórica).**
O `.gitignore` do repositório já existe e é mais completo do que a versão mínima proposta na
v2 original — ele hoje também ignora `data/{vectorstore,backups,config-institucional}/`,
`testes_cgov/`, `*.dump.sql` e `docs/referencias-pgd/**` (exceto o índice), além de `.env` e
`.venv/`. **A regra continua a mesma da v2: `.env` nunca pode aparecer versionado**, pois é
onde ficam as credenciais.

**Parte B — ciclo diário (todos da equipe).**

```powershell
git pull            # ao COMEÇAR o dia: traz o trabalho dos colegas
# ... trabalha nos arquivos ...
git add .           # ao CONCLUIR um avanço: prepara os arquivos alterados
git commit -m "Descreve o que foi feito em uma frase"
git push            # envia ao GitHub
```

**Antes de qualquer push, confira:** rode `git status` e verifique que `.env` **não** aparece
na lista. Se aparecer, o `.gitignore` está errado — pare e corrija antes de continuar.

**Se der errado:** o erro mais comum é o *conflito* (duas pessoas alteraram o mesmo trecho).
Não entre em pânico: o Git marca o trecho conflitante no arquivo com `<<<<<<<` e `>>>>>>>`;
escolha a versão correta, apague as marcas, salve e faça `git add .` + `git commit`. Na dúvida,
chame o coordenador — nada se perde no Git.

---

### T3 — Obter a chave de API e fazer a primeira conversa com o modelo

**Objetivo:** ter uma chave de API funcionando, com limite de gasto configurado, e rodar um
primeiro script que conversa com o modelo usando uma skill como *system prompt* (a instrução
que define o comportamento do agente antes da pergunta do usuário).

**Passo 1 — Criar a conta e a chave.**
No console da Anthropic (<https://console.anthropic.com>): criar conta → cadastrar forma de
pagamento → gerar uma **API key**. A chave aparece **uma única vez** — copie-a imediatamente.

**Passo 2 — Configurar limite de gasto.**
No mesmo console, localize *Billing/Limits* e defina um teto mensal. Isso elimina o risco de
custo fora de controle (RP14 da matriz de riscos — ver Seção 8).

**Passo 3 — Guardar a chave no `.env` (nunca no código).**
Copie `.env.example` (já presente na raiz do repositório) para `.env` e preencha:

```env
ANTHROPIC_API_KEY=cole-a-chave-aqui
```

**Passo 4 — Rodar um primeiro script exploratório.**
Este é um exemplo simples para entender o mecanismo — **o script oficial equivalente ainda
será construído no Incremento I1** (`consulta_skill.py`, ver `AGENTS.md` §10, "Próximo
incremento"). Para experimentar hoje, um script como este ilustra a ideia:

```python
"""Primeira conversa com o modelo: usa uma skill .md como system prompt."""
import os
from pathlib import Path
from dotenv import load_dotenv
import anthropic

load_dotenv()                     # lê o arquivo .env e carrega as variáveis
cliente = anthropic.Anthropic()   # usa a ANTHROPIC_API_KEY do .env automaticamente

# 1. Carrega a skill escolhida como "instrução de bastidor" (system prompt)
#    Caminho atualizado: os 4 documentos de metodologia ganharam o prefixo "00_"
skill = Path("skills/00_skill-analise-entrega-v1.md").read_text(encoding="utf-8")

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
python caminho\para\o\script.py
```

*O que esperar: uma análise da entrega segundo os critérios do documento de metodologia — a
mesma lógica que um analista aplicaria, mas gerada pelo modelo orientado pela skill.*

**Se der errado:** erro `authentication` = chave errada ou `.env` no lugar errado (deve estar
na raiz, onde você roda o comando); erro `module not found` = `.venv` não ativado ou pacote não
instalado (volte ao T1, Passo 5).

---

### T4 — Consultar um indicador no Denodo

**Objetivo:** rodar uma consulta real ao banco `petrvs_icmbio` (via Denodo) e ver o resultado
na tela — provando que a "capacidade B" (ação/consulta) funciona na sua máquina.

**Pré-requisitos:** driver JDBC do Denodo no caminho usado pelo projeto irmão `pgd-ocde-
icmbio`; rede/VPN institucional ativa (ver risco RP16 na Seção 8 — já mitigado, mas depende
de a máquina estar na rede correta); credenciais Denodo no `.env` (solicitar ao coordenador —
**nunca** circular por e-mail/chat em texto aberto):

```env
DENODO_HOST=
DENODO_PORT=
DENODO_DATABASE=
DENODO_USER=
DENODO_PASSWORD=
DENODO_DRIVER_PATH=
```

O script equivalente que já roda em produção local é `src/dados/sincronizar_ref.py` — ele
sincroniza `ref_unidades` e `ref_usuarios` (não um indicador individual, que é capacidade
ainda planejada para o Incremento I1 via `consultar_indicador.py` — ver `AGENTS.md` §10).
Para rodá-lo:

```powershell
.venv\Scripts\python src\dados\sincronizar_ref.py
```

*O que esperar: confirmação de quantos registros foram sincronizados em `ref_unidades` e
`ref_usuarios`. **Validação obrigatória:** confira o resultado contra os CSVs oficiais do
projeto irmão `pgd-ocde-icmbio` sempre que houver dúvida sobre um número — é exatamente o
tipo de checagem que os testes de aceite existem para fazer.*

**Se der errado:** erro de conexão/timeout = sem rota de rede ao Denodo (verifique VPN/rede
institucional); erro `class not found` = caminho do driver JDBC errado no `.env`.

---

### T5 — Montar o fluxo RAG visual no Langflow

**Objetivo:** ver, sem escrever código, como um documento vira "base de conhecimento"
consultável — útil para entender o conceito antes de o RAG oficial (Incremento I2) existir.

**Passo 1 — Instalar e abrir o Langflow.**

```powershell
pip install langflow
langflow run
```

*O que faz: instala e inicia o Langflow. Ele abre no navegador, em endereço local
(`http://localhost:7860`) — nada sai da sua máquina.*

**Passo 2 — Montar o fluxo de ingestão.** Na tela do Langflow, crie um fluxo novo e arraste,
conectando na ordem:

1. **File/Directory Loader** — aponte para a pasta `skills/` (os documentos de metodologia);
2. **Text Splitter** — divide os documentos em pedaços (*chunks*); comece com tamanho 1000 e
   sobreposição 200, valores usuais;
3. **Embeddings** — selecione o provedor da sua chave de API (converte pedaços em vetores
   numéricos que capturam significado);
4. **Chroma (Vector Store)** — grava os vetores em um banco vetorial local;
5. **Retriever + Chat** — permite fazer uma pergunta e ver **quais pedaços** o sistema
   recuperou antes de responder.

**Passo 3 — Testar com perguntas reais.** Use perguntas que os gestores fariam ("como formulo
o título de uma entrega?", "qual a diferença entre entrega e atividade?") e observe os trechos
recuperados. Se vierem trechos irrelevantes, ajuste o tamanho do *chunk* e repita — esse ajuste
fino é parte normal do trabalho com RAG, não perda de tempo.

**Se der errado:** Langflow não abre = porta ocupada (rode `langflow run --port 7861`);
embeddings falham = chave de API ausente nas configurações do componente.

---

### T6 — Testar a API local

**Objetivo:** verificar, como um "cliente" faria, que o backend responde — é o ensaio da
integração futura com o Copilot Studio. Esta API (FastAPI com `POST /skill` e
`GET /indicador/{id}`) ainda será construída no Incremento I1 (ver `AGENTS.md` §10); o
tutorial abaixo descreve como testá-la assim que existir.

**Passo 1 — Subir a API.**

```powershell
uvicorn src.api.main:app --reload
```

*O que faz: liga o "servidor" local da API (endereço `http://127.0.0.1:8000`). A opção
`--reload` recarrega automaticamente quando o código muda. Deixe este terminal aberto enquanto
testa.*

**Passo 2 — Testar pelo navegador (jeito mais fácil).**
Acesse `http://127.0.0.1:8000/docs`. O FastAPI gera sozinho uma página interativa (Swagger)
listando os endpoints. Clique em `GET /indicador/{id}` → *Try it out* → preencha um código de
indicador → *Execute* — a resposta aparece na própria página. Faça o mesmo com `POST /skill`,
preenchendo a pergunta no corpo da requisição.

**Passo 3 — Registrar o teste.** Anote data, endpoint, pergunta usada, resposta obtida e se
estava correta — esse registro simples é a base dos critérios de aceite RC1 e RC2 do projeto
(pasta `docs/testes/`, ainda a ser criada quando os primeiros testes existirem).

**Se der errado:** `address already in use` = já existe um servidor rodando (feche o terminal
antigo); erro 500 na resposta = problema no código ou credencial — copie a mensagem do
terminal e registre com o coordenador.

---

## 12. Boas práticas de engenharia — traduzidas para a equipe

Estas práticas vêm da engenharia de software profissional (Seção 8 da v2). A tradução para o
contexto do projeto:

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
   conferida contra o CSV oficial. É o "gabarito" do projeto.
6. **Documentar decisões, não só resultados.** Um ADR (ex.: [ADR-006](decisoes/ADR-006-persistencia-mysql.md))
   registra "por que MySQL e não SQLite?" de forma permanente — evita rediscutir o já decidido.
7. **Incremental sempre.** Cada incremento entrega algo que funciona. Nunca reescrever tudo de
   uma vez; nunca acumular meses de trabalho sem demonstração.
8. **Simplicidade primeiro.** Só adicionar uma peça nova (ferramenta, framework, camada extra)
   quando a dor que ela resolve **já apareceu** — não por antecipação.

---

## 13. Perguntas em aberto — histórico

As perguntas em aberto (Q1 a Q16, ao longo das cinco versões) rastreiam decisões que
dependiam de informação ainda não disponível no momento da escrita. Status conhecido das
principais:

| Pergunta | Assunto | Status |
| --- | --- | --- |
| Q2 | Migrar o modelo de linguagem para Azure OpenAI? | Tratada no [ADR-004](decisoes/ADR-004-modelo-linguagem.md) |
| Q5 | Quais fontes institucionais entram no cadastro/RAG? | **Ainda pendente** — ver [`fontes-institucionais.md`](fontes-institucionais.md) |
| Q8 | Quais são as unidades-piloto do projeto? | Respondida: **CGOV e COCAGE** |
| Q9–Q16 (v5) | Questões da Fase 2 (calendário do ciclo 2026, rota de rede ao Denodo, etc.) | Parcialmente respondidas — Q16 (rede ao Denodo) decidida junto com a mitigação do RP16; demais dependem do início da Fase 2 |

Perguntas sem entrada nesta tabela seguem registradas apenas no corpo de cada versão original
(Seção 14 indica onde encontrar cada uma).

---

## 14. Onde encontrar cada versão original

Após esta consolidação, os arquivos de proposta v1 a v4 foram movidos para uma pasta de
arquivo morto — preservando o histórico do Git — para que a raiz do repositório destaque
apenas o documento vigente (v5). Nada foi apagado.

| Versão | Caminho atual | Único conteúdo que só existe lá (texto integral) |
| --- | --- | --- |
| v1 | [`docs/gestao/historico/proposta-projeto-v1.md`](historico/proposta-projeto-v1.md) | Nenhum — totalmente superado por v2 |
| v2 | [`docs/gestao/historico/proposta-projeto-v2.md`](historico/proposta-projeto-v2.md) | Redação original dos Tutoriais T1–T6 e das boas práticas (reincorporados nas Seções 11–12 deste documento, com caminhos atualizados) |
| v3 | [`docs/gestao/historico/proposta-projeto-v3.md`](historico/proposta-projeto-v3.md) | Texto completo da análise da pasta `skills/` que introduziu a 3ª capacidade do agente |
| v4 | [`docs/gestao/historico/proposta-projeto-v4.md`](historico/proposta-projeto-v4.md) | Justificativa técnica completa da troca SQLite → MySQL 8 |
| v5 | [`proposta-projeto-v5.md`](../../proposta-projeto-v5.md) (raiz do repositório — **não foi movida**) | Documento normativo vigente — texto integral da Fase 2 |

---

## 15. Fontes externas — saiba mais

- [O que é RAG (Retrieval-Augmented Generation) — AWS](https://aws.amazon.com/what-is/retrieval-augmented-generation/)
- [Tool use (function calling) — documentação Anthropic](https://docs.claude.com/en/docs/build-with-claude/tool-use)
- [O que é uma função hash (usada para conferir integridade de arquivo) — Cloudflare](https://www.cloudflare.com/learning/ssl/what-is-a-hash-function/)
- [Documentação oficial do Python](https://docs.python.org/3/)
- [Documentação oficial do Git](https://git-scm.com/doc)
- [FastAPI — documentação oficial](https://fastapi.tiangolo.com/)
