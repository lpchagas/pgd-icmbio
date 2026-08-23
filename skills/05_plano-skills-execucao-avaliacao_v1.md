# Plano de desenvolvimento das skills de Execução e Avaliação dos Planos do PGD

**Documento:** `skills/05_plano-skills-execucao-avaliacao_v1.md`
**Versão:** v1 — 18.08.2026
**Objeto:** especificação e plano de desenvolvimento, em etapas, de quatro novas skills
executáveis do agente `pgd-agente-icmbio`, cobrindo a fase de **execução e avaliação** do
ciclo do PGD:

| Código  | Skill                                                    | Ator principal              |
| ------- | -------------------------------------------------------- | --------------------------- |
| **S21** | Registro de Execução do Plano de Entregas da Unidade     | Chefia da unidade de execução |
| **S22** | Avaliação do Plano de Entregas da Unidade                | Chefia hierarquicamente superior |
| **S23** | Registro de Execução do Plano de Trabalho do Participante | Participante                |
| **S24** | Avaliação do Plano de Trabalho do Participante           | Chefia da unidade de execução |

**Relação com os documentos de governo:** este documento é **subordinado** à
à arquitetura consolidada na proposta v6 e ao `AT-01`, e **complementar** aos documentos `02_matriz`,
`03_especificacao-funcional` e `04_backlog` (que definem S01–S20). Ele **não** altera o
escopo do MVP (S01–S10). Propõe um bloco novo — S21–S24 — a ser integrado ao catálogo na
proposta então vigente; a proposta v6 incorporou o conteúdo e reposiciona S13, S16 e S17.

---

## Sumário

1. [Síntese executiva](#1-síntese-executiva)
2. [Base documental analisada](#2-base-documental-analisada)
3. [Regras normativas extraídas (RN-01 a RN-36)](#3-regras-normativas-extraídas)
4. [Diagnóstico: o que já existe e o que falta](#4-diagnóstico-o-que-já-existe-e-o-que-falta)
5. [Arquitetura do bloco S21–S24](#5-arquitetura-do-bloco-s21s24)
6. [Especificação funcional das quatro skills](#6-especificação-funcional-das-quatro-skills)
7. [Modelo de dados — migração 002](#7-modelo-de-dados--migração-002)
8. [Mapeamento com o PETRVS](#8-mapeamento-com-o-petrvs)
9. [Plano de desenvolvimento em etapas (E0–E7)](#9-plano-de-desenvolvimento-em-etapas)
10. [Riscos específicos do bloco](#10-riscos-específicos-do-bloco)
11. [Critérios de aceite e definição de pronto](#11-critérios-de-aceite-e-definição-de-pronto)
12. [Questões em aberto](#12-questões-em-aberto)

---

## 1. Síntese executiva

O catálogo atual do projeto (S01–S20) foi desenhado com foco na **elaboração** dos planos.
A fase de **execução e avaliação** aparece apenas de forma genérica em três skills de baixa
prioridade — S13 (Check-in), S16 (Avaliador de Entregas) e S17 (Evidências) —, todas
concebidas antes de o modelo comum de dados existir e **nenhuma delas distingue os dois
instrumentos do PGD** (Plano de Entregas da unidade × Plano de Trabalho do participante),
que possuem atores, prazos, critérios, escalas e consequências jurídicas distintos.

A análise da pasta `referencias-pgd` mostra que essa distinção não é um detalhe: a IN nº
24/2023 estabelece **quatro procedimentos diferentes**, com **quatro prazos diferentes**,
**dois avaliadores diferentes** e uma **política de consequências que só existe do lado do
Plano de Trabalho** (recurso do participante, reavaliação, ações de desenvolvimento). Um
único componente genérico de "avaliação" não consegue implementar isso sem violar a regra
de ouro 4 do projeto (decisões humanas registradas separadamente).

Diagnóstico central em três pontos:

1. **Falta a entidade `PlanoDeTrabalho` no modelo comum.** O esquema atual (21 tabelas)
   representa capacidade (`planos_capacidade`, `participantes`, `alocacoes`) mas **não
   representa o plano de trabalho individual como objeto versionável** — que é justamente o
   objeto que S23 registra e S24 avalia. Esta é a maior lacuna estrutural do bloco.
2. **Faltam as entidades de execução e avaliação.** Não há tabela para registro de
   execução, intercorrência, ocorrência, evidência, avaliação, recurso ou ação de
   desenvolvimento. São necessárias **12 tabelas novas** (migração `002`).
3. **Os protótipos existentes contêm regras sem lastro normativo.** As skills Cowork
   `cgov-registro-execucao` e `cgov-avaliar-entrega`, hoje em uso informal na CGOV,
   embutem uma faixa percentual fixa (`≥ 80 % = Adequado`) e uma regra de "sem
   intercorrências" para Alto Desempenho que **não constam da IN nº 24/2023 nem dos
   cadernos da Enap**. São convenções locais legítimas, mas precisam ser **declaradas como
   regra institucional no S01, com fonte e vigência** — não como norma. Ver Seção 4.4.

O plano propõe **8 etapas (E0–E7)**, estimadas em **18 a 24 semanas**, executáveis em dois
regimes: o *caminho completo* (após o MVP S01–S10) e um *caminho curto* (E0–E3), que
entrega S21 e S23 sem depender de S05/S07/S08 e permite iniciar o piloto CGOV/COCAGE no
ciclo quadrimestral seguinte.

---

## 2. Base documental analisada

Foram lidos integralmente os documentos abaixo, da pasta
`C:\_cowork\cgge-fgbio-2026\referencias-pgd`. A coluna "peso" indica a força da fonte na
derivação de regras, no mesmo critério de `natureza` usado pelo S01
(norma > regra institucional > recomendação > exemplo).

| # | Documento | Origem | Peso | Contribuição para este plano |
| - | --------- | ------ | ---- | ---------------------------- |
| D1 | *Caderno do Curso — Execução e Avaliação dos Planos* (Enap, 2026, cont. Rodrigo Narcizo) | Enap/SEGES | **Norma interpretada** (reflete IN 24/2023 e 52/2023) | **Fonte primária deste documento.** Prazos, escala de 5 conceitos, os 5 critérios de avaliação do PT, recurso e reavaliação, notificação, justificativa obrigatória nas extremidades |
| D2 | *Entendendo o Ciclo do PGD no ICMBio* (SharePoint CGGE) | ICMBio/CGGE | Regra institucional | Periodicidade ICMBio (PE quadrimestral, PT mensal), quem registra o quê, condição para conclusão do PE, integração Petrvs |
| D3 | *Perguntas e respostas PGD ICMBio* (25 perguntas, SharePoint CGGE) | ICMBio/CGGE | Regra institucional + recomendação | CHD e seu cálculo, usufruto/compensação de horas, critérios de "inadequado", caráter não punitivo, distinção PGD × avaliação anual (GDAEM/AvaliaGov), atividades não vinculadas |
| D4 | *Caderno do Curso — Elaboração de Planos de Entrega e de Trabalho* (Enap) | Enap | Norma interpretada | Definições de meta, prazo, demandante, destinatário, **progresso esperado**, método 4Q1P — base de comparação planejado × realizado |
| D5 | *Guia Prático PGD — Módulo 3: Plano de Entregas* (2ª ed., SEGES) | SEGES/MGI | Norma interpretada | Estrutura do PE, papel da unidade instituidora, cascata de avaliação, campo "progresso esperado" como item opcional da unidade |
| D6 | *caderno-curso-fundamentos-PGD* + `Controle_de_Entregas.xlsx` + exercícios M1/M3 (Enap) | Enap | Recomendação/exemplo | Instrumentos de controle e vocabulário; a planilha é o modelo de onde vieram os protótipos `cgov-*` |
| D7 | *Entenda como criar um Plano de Entregas* / *Guia para site de transparência do PGD* | ICMBio/MGI | Recomendação | Publicidade e transparência dos registros — insumo para as regras de exposição de dados (Seção 10) |
| D8 | *Portaria ICMBio nº 5.592/2025 — Regimento Interno* | ICMBio | Norma | Competências das unidades — define quem é "chefia hierarquicamente superior" para efeito de S22 |
| D9 | *Acórdão TCU 2082/2022* (pasta ENAP) | TCU | Norma (controle externo) | Fundamenta a exigência de rastreabilidade e evidência dos registros |
| D10 | Exercícios do curso de Avaliação (`exercio-m1.pdf`, `exercio-m2.pdf`) | Enap | Exemplo | **Não processáveis:** PDFs sem camada de texto (digitalizados). Ver Q4 na Seção 12 |

Documentos internos do projeto usados como referência de conformidade: `proposta-projeto-v6.md`,
`AT-01`, `ADR-006`, `src/dados/schema.sql`, `skills/01`–`skills/04`, e as skills Cowork
sincronizadas `cgov-registro-execucao` e `cgov-avaliar-entrega`.

---

> [!IMPORTANT]
> Este arquivo é insumo histórico. A fonte vigente é o catálogo v6 e as fichas S21–S24.
> As questões Q1–Q8 deste documento pertencem ao namespace antigo; a consolidação vigente
> preserva Q5 para fontes institucionais e usa Q17–Q25 para execução, avaliação e adoção.

## 3. Regras normativas extraídas

As regras abaixo são a base de implementação dos validadores determinísticos. Cada uma
receberá um código `R-xxx` em `regras_institucionais` (S01), com `natureza`, `fonte`,
`inicio_vigencia` e `status`, exatamente como as demais regras do agente. Aqui recebem
códigos provisórios `RN-xx` para referência cruzada dentro deste documento.

### 3.1. Execução do Plano de Entregas (S21)

| Código | Regra | Fonte |
| ------ | ----- | ----- |
| RN-01 | O registro da execução do PE é atribuição **da chefia da unidade de execução** | D1 §1.2 |
| RN-02 | O conteúdo do registro é a **descrição da evolução das entregas** e as **ocorrências que possam impactar o alcance** | D1 §1.2 |
| RN-03 | O registro ocorre **ao longo da execução**; no ICMBio, deve estar completo **até o término da vigência do plano** | D1 §1.2; D2 |
| RN-04 | A **conclusão** do PE só pode ser feita depois de a chefia verificar que **todos os planos de trabalho dos servidores da unidade no período foram devidamente executados** | D2 |
| RN-05 | Ajustes no PE (prazo, meta, exclusão ou inclusão de entregas) **não ensejam nova pactuação** — exigem apenas **comunicação à chefia imediata superior**, que pode intervir | D1 §1.2 |
| RN-06 | Ajustes no PE **podem ensejar repactuação dos planos de trabalho vinculados** às entregas alteradas | D1 §1.2 |
| RN-07 | No ICMBio, o PE das unidades de execução é **quadrimestral** em 2026 | D2; D3 §9 |
| RN-08 | O **progresso esperado** é campo do planejamento; o registro de execução informa o **progresso realizado** — os dois nunca se confundem | D4 §glossário; D5 |

### 3.2. Avaliação do Plano de Entregas (S22)

| Código | Regra | Fonte |
| ------ | ----- | ----- |
| RN-09 | A avaliação do PE cabe à **unidade hierarquicamente superior** (a unidade instituidora avalia a UE imediatamente inferior, em cascata) | D1 §2.2; D5 |
| RN-10 | Quando a **unidade instituidora é também unidade de execução**, a IN 24/23 **dispensa** a avaliação por nível hierárquico superior | D1 §2.2 |
| RN-11 | O ato de autorização pode prever **dispensa do art. 18 §1º e do art. 22** para unidades de nível imediatamente inferior à unidade máxima | D1 §2.2 |
| RN-12 | Prazo: **até 30 dias após o encerramento do plano** | D1 §2.2 |
| RN-13 | Os quatro questionamentos obrigatórios: (a) as metas foram alcançadas? (b) os prazos foram cumpridos? (c) há justificativa para atraso ou descumprimento? (d) as entregas tiveram a qualidade esperada? | D1 §2.2 |
| RN-14 | Escala única de 5 conceitos: **1 excepcional · 2 alto desempenho · 3 adequado · 4 inadequado · 5 não executado** | D1 §2.2 |
| RN-15 | A IN 24/2023 **não estabelece consequências diretas** para os níveis 4 e 5 do PE — cada órgão define medidas corretivas por política interna | D1 §2.2 |
| RN-16 | Avaliação insatisfatória do PE deve ser lida como sinal de **planejamento mal elaborado e/ou falha de gestão da equipe**, não como falha individual dos participantes | D1 §2.2 |

### 3.3. Execução do Plano de Trabalho (S23)

| Código | Regra | Fonte |
| ------ | ----- | ----- |
| RN-17 | O registro da execução do PT é feito **pelo próprio participante** | D1 §1.3 |
| RN-18 | Dois conteúdos obrigatórios: **(A) descrição dos trabalhos realizados** e **(B) intercorrências, com justificativa** | D1 §1.3 |
| RN-19 | Prazos: **até 10 dias após o encerramento** se o PT tiver duração ≤ 30 dias; **mensalmente, até o 10º dia do mês subsequente**, se > 30 dias | D1 §1.3 |
| RN-20 | No ICMBio o PT é **mensal**, com registro **até o 10º dia do mês seguinte** | D2; D3 §10 |
| RN-21 | **Férias, licenças e afastamentos NÃO são intercorrências** — são eventos planejados e devem ser considerados no planejamento (CHD) | D1 §1.3 |
| RN-22 | São intercorrências: alteração de prioridade, atraso de terceiros, imprevistos, demandas de última hora, situações pessoais supervenientes | D1 §1.3, §2.3 |
| RN-23 | O PT pode ser **ajustado e repactuado a qualquer momento** | D1 §1.3 |
| RN-24 | **CHD = jornada × dias trabalháveis** (dias úteis − ocorrências programadas); usufruto **subtrai** e compensação **soma** horas | D3 §8 |
| RN-25 | Usufruto/compensação de horas se registra nas **ocorrências**, com motivo "Outras hipóteses (subtração de carga horária)" ou "(compensação)" e descrição do vínculo com o período de origem | D3 §18, §23 |
| RN-26 | O plano de trabalho deve corresponder à **totalidade da CHD**; execução em tempo inferior indica plano mal dimensionado, e **não gera folga compensatória** | D3 §21 |

### 3.4. Avaliação do Plano de Trabalho (S24)

| Código | Regra | Fonte |
| ------ | ----- | ----- |
| RN-27 | A avaliação cabe à **chefia da unidade de execução** e refere-se ao **plano como um todo** — a IN 24/2023 **não prevê avaliação de cada atividade separadamente** | D1 §2.3 |
| RN-28 | Prazo: **até 20 dias após a data limite do registro** feito pelo participante | D1 §2.3; D2 |
| RN-29 | Cinco critérios obrigatórios: (1) realização dos trabalhos conforme pactuado; (2) critérios de avaliação previamente definidos no TCR/plano; (3) **fatos externos à capacidade de ação do participante e de sua chefia**; (4) cumprimento do TCR; (5) ocorrências registradas pelo participante | D1 §2.3 |
| RN-30 | O participante **deve ser notificado** do resultado | D1 §2.3 |
| RN-31 | O uso dos conceitos das **extremidades da escala (1 e 5) exige justificativa** da chefia | D1 §2.3 |
| RN-32 | Conceitos **inferiores a "adequado"** (4 e 5) admitem **recurso em 10 dias** da notificação; a chefia tem **10 dias** para acatar (ajustando a avaliação) ou se manifestar pelo não acatamento | D1 §2.3 |
| RN-33 | O foco é a **contribuição para as entregas**, não a avaliação de comportamento individual | D1 §2.3 |
| RN-34 | Independentemente do resultado, a chefia deve **estimular o aprimoramento**: acompanhamento periódico e proposição de **ações de desenvolvimento** | D1 §2.3 |
| RN-35 | O PGD **não tem caráter punitivo**: justificativa coerente permite reprogramar a pendência no PT seguinte; a política de consequências só se aplica na **ausência de justificativa** | D3 §12 |
| RN-36 | A avaliação do PGD **não substitui** a avaliação de desempenho anual (GDAEM/AvaliaGov) — objetivos e métodos distintos | D3 §25 |

### 3.5. Conflitos e lacunas detectados na base normativa

Registrar em `regras_conflitos` (S01) — **não resolver silenciosamente** (regra de ouro 5):

- **C-01 — Datas do ciclo 2026 (D2).** A página do ciclo do PGD/ICMBio informa os
  quadrimestres como `01/01–31/04`, `01/05–30/07` e `01/08–31/12`. As três faixas são
  internamente inconsistentes (31/04 não existe; há lacuna entre 30/07 e 01/08; a terceira
  faixa tem 5 meses). O motor de prazos **não pode** ser implementado sobre esses valores
  sem confirmação da CGGE. → **Q1**, Seção 12.
- **C-02 — Escala do PE sem consequências × escala do PT com consequências.** RN-15 × RN-32.
  A mesma nomenclatura de 5 conceitos produz efeitos jurídicos diferentes conforme o objeto
  avaliado. O modelo de dados precisa **separar as duas avaliações** (Seção 7), sob pena de
  o agente sugerir recurso sobre avaliação de PE, onde ele não cabe.
- **C-03 — Vigência do PE × obrigatoriedade mensal da avaliação do PT.** D3 §10 afirma que
  a avaliação do PT é **obrigatoriamente mensal, sem flexibilização**, mesmo quando o PT
  tem vigência superior a um mês. A conclusão do PE (RN-04) depende de todos os PTs do
  período estarem executados — ou seja, no ICMBio um PE quadrimestral depende de **4 ciclos
  mensais completos** de registro + avaliação por participante.

---

## 4. Diagnóstico: o que já existe e o que falta

### 4.1. Cobertura do catálogo S01–S20

| Finalidade pedida | Skill existente mais próxima | Cobertura | Lacuna |
| ----------------- | ---------------------------- | --------- | ------ |
| (i) Registro de execução do **PE** | S13 — Check-in de Execução e Monitoramento (P2) | **Parcial** | S13 é *monitoramento contínuo genérico*: não distingue registro de PE de registro de PT; não trata da regra de conclusão (RN-04); não trata de prazo regulamentar; não trata do fluxo de comunicação de ajustes à chefia superior (RN-05) |
| (ii) Avaliação do **PE** | S16 — Avaliador de Entregas (P3) | **Parcial** | S16 avalia **entrega**, não **plano de entregas**. Não implementa os 4 questionamentos (RN-13), a escala de 5 conceitos (RN-14), a competência hierárquica e as dispensas (RN-09 a RN-11), nem o prazo de 30 dias (RN-12) |
| (iii) Registro de execução do **PT** | — (nenhuma) | **Ausente** | Não existe entidade `PlanoDeTrabalho` no modelo comum; não há tratamento de intercorrência, CHD realizada, usufruto/compensação |
| (iv) Avaliação do **PT** | — (nenhuma) | **Ausente** | Nenhuma skill trata dos 5 critérios (RN-29), notificação, justificativa obrigatória nas extremidades, recurso e reavaliação, ações de desenvolvimento |

Skills de apoio que o bloco reutiliza sem duplicar: **S02** (verificação normativa),
**S05** (critérios de aceite — insumo direto de S22/S24), **S07/S08** (capacidade e
alocação — base da CHD e da matriz de contribuição), **S10** (riscos — origem dos "fatos
externos" de RN-29), **S14** (replanejamento — acionado por RN-05/RN-06/RN-23),
**S17** (evidências), **S18** (relatório gerencial — consumidor natural das saídas).

### 4.2. Lacuna estrutural no modelo de dados

O `schema.sql` (21 tabelas, migração `001`) representa a **capacidade** da unidade
(`planos_capacidade`, `participantes`, `indisponibilidades`, `alocacoes`), mas **não
representa o plano de trabalho individual**. `alocacoes` é uma matriz esforço ×
participante × entrega, não um plano versionável com estado, prazo, TCR e critérios de
avaliação. Sem essa entidade, S23 não tem o que registrar e S24 não tem o que avaliar.
**Este é o pré-requisito nº 1 do bloco** e está resolvido na Seção 7.

Igualmente ausentes: registro de execução, ocorrência/intercorrência, evidência,
avaliação, recurso e ação de desenvolvimento — nenhuma delas tem equivalente nas 21
tabelas atuais.

### 4.3. Reposicionamento de S13, S16 e S17

Para não duplicar regras (princípio herdado de `01_analise-skills` §1) o bloco S21–S24
absorve parte do escopo previsto para S13 e S16:

| Skill | Situação histórica incorporada na v6 |
| ----- | ----------------------- |
| **S13** — Check-in de Execução | **Mantida, com escopo reduzido** a *check-in intermediário informal* (acompanhamento semanal, quadro de status), sem valor normativo. O registro formal migra para S21 (PE) e S23 (PT) |
| **S16** — Avaliador de Entregas | **Mantida, subordinada a S22.** Passa a ser o *avaliador de entrega individual*, chamado por S22 como sub-rotina: S22 avalia o **plano**, agregando as avaliações de entrega produzidas por S16 |
| **S17** — Organizador de Evidências | **Promovida a P2** e antecipada: sem repositório de evidências, RN-13(d) e RN-29(1) não são verificáveis. Uma versão mínima entra na etapa E2 |
| **S14** — Replanejamento | **Sem alteração**, mas passa a ser acionada por S21 (RN-05/RN-06) e S23 (RN-23) |

### 4.4. Confronto com as skills-protótipo em uso na CGOV

As skills Cowork `cgov-registro-execucao` e `cgov-avaliar-entrega` já operam sobre planilhas
(Planilhas A e B) e produzem pareceres. Elas são o **melhor conjunto de exemplos anotados
disponível** para os casos de teste — e, ao mesmo tempo, contêm regras que precisam de
tratamento explícito antes de migrar para o agente:

| Achado | Descrição | Encaminhamento |
| ------ | --------- | -------------- |
| **A-01** | `cgov-avaliar-entrega` define os conceitos por **faixas percentuais fixas** (`≥ 80 % = Adequado`, `< 80 % sem justificativa = Inadequado`). Essa faixa **não consta** da IN 24/2023 nem de D1/D4/D5 | Declarar como **regra institucional** no S01 (natureza `institucional`, fonte "prática CGOV", vigência), não como norma. S22 aplica a faixa **como sugestão**, sempre indicando que é convenção local |
| **A-02** | O mesmo protótipo exige "**sem intercorrências**" para Alto Desempenho | Conflita com RN-29(3): fatos externos devem ser **considerados separadamente**, e não rebaixar automaticamente o conceito. Corrigir na especificação de S22/S24 |
| **A-03** | `cgov-registro-execucao` calcula progresso como `etapas concluídas / total de etapas` | Confunde **esforço** com **meta** — vedado pela regra já registrada em S13 ("não substituir meta por relato de esforço"). Em S21, o progresso realizado é apurado **contra a meta pactuada** (`meta` JSON), e a contagem de etapas passa a ser evidência auxiliar, nunca a métrica |
| **A-04** | Ambos os protótipos gravam pareceres em pasta de nuvem pessoal (`H:\Meu Drive\...`) | Em S21–S24 a persistência é o banco `pgd_agente` + exportação; o parecer é **derivado**, não a fonte da verdade |
| **A-05** | `cgov-avaliar-entrega` avalia **entrega**; não há protótipo para avaliação de **plano de trabalho** | Confirma que (iii) e (iv) são construção nova, sem base prévia — maior esforço de especificação (E1) |

---

## 5. Arquitetura do bloco S21–S24

### 5.1. Princípio de separação

```
                    PLANO DE ENTREGAS (unidade, quadrimestral)
                    ┌──────────────────────────────────────────┐
   S03–S06  ──────► │  pactuado (S11)                          │
                    │        │                                 │
                    │        ▼                                 │
                    │   S21 registro de execução  ──► S14      │  ajustes → comunicação
                    │        │        (RN-01..08)              │  à chefia superior
                    │        ▼                                 │
                    │   S22 avaliação  (RN-09..16)             │  chefia SUPERIOR, 30 dias
                    └──────────────────────────────────────────┘
                                  ▲ agrega                ▲ depende (RN-04)
                                  │                       │
                    ┌─────────────┴───────────────────────┴────┐
                    │  PLANO DE TRABALHO (participante, mensal)│
   S07–S08  ──────► │  pactuado (S12)                          │
                    │        │                                 │
                    │        ▼                                 │
                    │   S23 registro de execução  (RN-17..26)  │  PARTICIPANTE, dia 10
                    │        │                                 │
                    │        ▼                                 │
                    │   S24 avaliação  (RN-27..36)             │  chefia da UE, 20 dias
                    │        │                                 │
                    │        ▼  recurso 10d → reavaliação 10d  │
                    └──────────────────────────────────────────┘
```

Quatro invariantes de arquitetura:

- **I1 — Um ator por skill.** S21 = chefia da UE; S22 = chefia superior; S23 = participante;
  S24 = chefia da UE. O controle de perfil é pré-condição de execução, não validação a
  posteriori.
- **I2 — O agente nunca atribui conceito.** S22 e S24 produzem **conceito sugerido +
  confiança + justificativa fundamentada nos critérios**. O conceito válido é sempre um
  registro em `decisoes_humanas` (regra de ouro 4). Uma avaliação sem decisão humana
  associada é, por construção, `estado = 'rascunho'`.
- **I3 — Determinístico ≠ LLM** (v4 §3.3). Ver tabela 5.2.
- **I4 — Dado ausente vira pergunta.** Sem critério de aceite pactuado (S05), sem evidência
  (S17) ou sem registro do participante (S23), a avaliação **não é emitida**: gera
  `perguntas_pendentes` (regra de ouro 5).

### 5.2. Divisão determinístico × modelo de linguagem

| Cálculo/decisão | Regime | Exatidão exigida |
| --------------- | ------ | ---------------- |
| Prazos regulamentares (10 / 20 / 30 dias, dia 10 do mês subsequente) e situação de tempestividade | **Determinístico** (Python puro, calendário de dias corridos/úteis) | 100 % |
| CHD planejada × CHD realizada; usufruto e compensação (RN-24, RN-25) | **Determinístico** | 100 % |
| Progresso realizado × meta pactuada; desvio; totalização de percentuais em 100 % | **Determinístico** | 100 % |
| Verificação de completude dos PTs antes da conclusão do PE (RN-04) | **Determinístico** (consulta ao banco) | 100 % |
| Elegibilidade a recurso e cômputo dos prazos de recurso/reavaliação (RN-32) | **Determinístico** | 100 % |
| Competência de avaliação e dispensas hierárquicas (RN-09 a RN-11) | **Determinístico** (árvore de `ref_unidades`) | 100 % |
| Classificação de um relato como intercorrência × evento planejado (RN-21/22) | **LLM com confiança**, validação humana obrigatória quando confiança < alta | — |
| Aderência qualitativa do realizado aos critérios de aceite (RN-13d, RN-29-2) | **LLM com confiança** + evidência obrigatória | — |
| Redação da narrativa de evolução e da justificativa do conceito | **LLM**, sempre revisável, nunca autoemitida | — |
| Sugestão de conceito na escala de 5 | **Híbrido**: regras determinísticas produzem faixa candidata; LLM redige fundamentação; **humano decide** | — |

### 5.3. Contrato de saída

Todas as quatro skills obedecem ao contrato v4 §8.3 e gravam em `execucoes_skill`
(`rastreio_id`, entrada, saída integral, `regras_aplicadas` com os códigos `R-xxx`
derivados de RN-01..RN-36, `fontes`, `confianca`, `requer_validacao_humana`). Contratos
Pydantic propostos em `src/skills_engine/contratos/execucao_avaliacao.py`:

```python
class RegistroExecucaoEntregaOut(SaidaSkill):      # S21
    entrega_id: UUID; periodo: Periodo
    progresso_realizado: Decimal                    # 0–100, apurado contra a meta
    progresso_esperado: Decimal | None              # do planejamento — nunca sobrescrito
    desvio: Decimal
    situacao: Literal['nao_iniciada','em_andamento','concluida',
                      'concluida_com_ressalva','suspensa','cancelada']
    narrativa_evolucao: str
    ocorrencias: list[Ocorrencia]
    evidencias: list[RefEvidencia]
    ajustes_sugeridos: list[SolicitacaoAjuste]      # → S14; nunca aplicados aqui
    bloqueios_para_conclusao: list[str]             # RN-04

class AvaliacaoPlanoEntregasOut(SaidaSkill):        # S22
    plano_entregas_id: UUID; avaliador_unidade_id: UUID
    competencia_verificada: CompetenciaAvaliacao    # RN-09..11, com dispensa aplicável
    prazo: ControlePrazo                            # RN-12
    questionamentos: QuatroQuestionamentos          # RN-13 a–d, cada um com evidência
    conceito_sugerido: ConceitoPGD                  # 1..5
    confianca: Literal['alta','media','baixa']
    fundamentacao: str
    fatores_externos: list[FatorExterno]            # separados do resultado
    medidas_corretivas_sugeridas: list[str]         # RN-15/16 — política interna
    decisao_humana_id: UUID | None                  # None ⇒ rascunho (I2)

class RegistroExecucaoTrabalhoOut(SaidaSkill):      # S23
    plano_trabalho_id: UUID; participante_rotulo: str   # pseudônimo (D2/RP06)
    periodo: Periodo
    chd_planejada_h: Decimal; chd_realizada_h: Decimal
    trabalhos_realizados: list[TrabalhoRealizado]   # por contribuição/entrega
    intercorrencias: list[Intercorrencia]           # classificadas RN-21/22
    eventos_planejados: list[EventoPlanejado]       # férias/licenças — NÃO intercorrência
    ajuste_carga_horaria: AjusteCH | None           # usufruto/compensação RN-25
    tempestividade: ControlePrazo                   # RN-19/20
    pendencias_para_proximo_ciclo: list[str]        # RN-35

class AvaliacaoPlanoTrabalhoOut(SaidaSkill):        # S24
    plano_trabalho_id: UUID; avaliador_id: UUID
    prazo: ControlePrazo                            # RN-28
    criterios: CincoCriterios                       # RN-29 (1..5), cada um fundamentado
    conceito_sugerido: ConceitoPGD
    justificativa_obrigatoria: bool                 # True se conceito ∈ {1,5} — RN-31
    fundamentacao: str
    elegivel_recurso: bool                          # True se conceito ∈ {4,5} — RN-32
    prazos_recurso: PrazosRecurso
    notificacao: Notificacao                        # RN-30
    acoes_desenvolvimento: list[AcaoDesenvolvimento]  # RN-34
    decisao_humana_id: UUID | None
```

---

## 6. Especificação funcional das quatro skills

Formato idêntico ao de `02_matriz-desenvolvimento-skills_v2.md` (fichas) e
`03_especificacao-funcional-skills_v2.md` (histórias + casos de teste).

### 6.1. S21 — Registro de Execução do Plano de Entregas da Unidade

| Campo | Especificação |
| ----- | ------------- |
| **Prioridade** | P2 |
| **Objetivo** | Apoiar a chefia da unidade de execução no registro tempestivo e rastreável da evolução das entregas do plano, na identificação de ocorrências e na verificação das condições de conclusão do plano |
| **Dependências** | S04, S05 (metas e critérios); S11 (plano pactuado); S13 (check-ins); S17-mínimo (evidências); S14 (para ajustes); `planos_entregas` + `registros_execucao_entrega` (migração 002) |
| **Entradas** | Plano de entregas pactuado e versão vigente; entregas com meta, prazo e progresso esperado; relatos de evolução; evidências; ocorrências; data de referência; situação dos PTs vinculados no período |
| **Saídas** | Registro de execução versionado por entrega; progresso realizado × esperado e desvio; narrativa de evolução; lista de ocorrências classificadas; evidências vinculadas; solicitações de ajuste encaminhadas a S14; **relatório de bloqueios para conclusão do plano**; controle de tempestividade |
| **Regras principais** | RN-01 a RN-08. O progresso realizado é apurado **contra a meta pactuada**, nunca por contagem de atividades (A-03); o progresso esperado do planejamento **jamais é sobrescrito** (regra de ouro 2); ajuste de meta/prazo/escopo **não é feito por esta skill** — gera solicitação a S14 e comunicação à chefia superior (RN-05); a conclusão do plano é **bloqueada** enquanto houver PT do período sem registro ou sem avaliação (RN-04); ocorrência sem impacto declarado gera pergunta pendente, não preenchimento automático |
| **Histórias** | **US01** Como chefe de UE, quero registrar a evolução de cada entrega no período, para que a execução fique documentada antes do encerramento da vigência. **US02** Como chefe de UE, quero saber quais planos de trabalho ainda impedem a conclusão do PE, para cobrar a equipe a tempo. **US03** Como chefe de UE, quero registrar uma ocorrência que impacta uma entrega, para que ela seja considerada na avaliação. **US04** Como chefe de UE, quero solicitar alteração de prazo de uma entrega, para que a mudança siga o rito de comunicação e versionamento |
| **T01** (positivo) | **Dado** entrega com meta `{"quantitativo": 10}` e 7 unidades realizadas, **quando** o registro for salvo, **então** o progresso realizado deve ser 70,00 e o desvio calculado contra o progresso esperado do período |
| **T02** (negativo) | **Dado** relato apenas de atividades realizadas ("participei de 5 reuniões"), **quando** submetido, **então** a skill deve perguntar qual avanço ocorreu **na entrega** e não registrar progresso |
| **T03** (limite / RN-04) | **Dado** um PE com 6 participantes e 1 PT do último mês sem registro, **quando** a conclusão for solicitada, **então** a skill deve bloquear a conclusão e listar nominalmente (por pseudônimo) o PT pendente |
| **T04** (regra de ouro 2) | **Dado** pedido de alteração do prazo de uma entrega, **quando** processado, **então** a skill não altera a versão vigente: cria solicitação para S14 e registra a exigência de comunicação à chefia superior (RN-05) |
| **T05** (ambiguidade) | **Dado** relato "houve atraso do fornecedor", **quando** classificado, **então** a skill deve distinguir **atraso**, **bloqueio** e **mudança de escopo** e, se não for possível, perguntar |
| **T06** (prazo) | **Dado** que a vigência do plano encerrou há 5 dias sem registro completo, **quando** a skill for acionada, **então** deve sinalizar intempestividade e indicar o prazo normativo violado (RN-03) |
| **T07** (explicabilidade) | **Dado** qualquer registro emitido, **quando** consultado, **então** a saída deve citar os códigos das regras aplicadas e as fontes (D1/D2) |

### 6.2. S22 — Avaliação do Plano de Entregas da Unidade

| Campo | Especificação |
| ----- | ------------- |
| **Prioridade** | P2 |
| **Objetivo** | Apoiar a chefia hierarquicamente superior na avaliação do plano de entregas de uma unidade subordinada, aplicando os quatro questionamentos e a escala de cinco conceitos, com fundamentação rastreável |
| **Dependências** | S21 (registros de execução); S05 (critérios de aceite); S16 (avaliação de entrega individual, como sub-rotina); S17 (evidências); S10 (riscos → fatores externos); árvore de `ref_unidades` (competência) |
| **Entradas** | Plano de entregas e sua versão final; registros de execução de todas as entregas; metas e prazos pactuados; evidências; ocorrências e fatores externos; identificação do avaliador e da unidade avaliada; ato de autorização vigente (dispensas) |
| **Saídas** | Verificação de competência (com dispensa aplicável, RN-09 a RN-11); controle do prazo de 30 dias; **quatro questionamentos respondidos com evidência** (RN-13); conceito **sugerido** na escala de 5 com grau de confiança; fundamentação; fatores externos apresentados separadamente; medidas corretivas sugeridas para conceitos 4 e 5; parecer exportável; pendências |
| **Regras principais** | RN-09 a RN-16. O agente **não emite** conceito: sugere e exige decisão humana (I2); qualidade e alcance de meta são apurados separadamente — meta atingida sem qualidade **não** produz "integralmente alcançada"; fatores externos aparecem em bloco próprio e **não rebaixam automaticamente** o conceito (corrige A-02); faixas percentuais locais são aplicadas apenas se existir regra institucional vigente e são rotuladas como convenção local (A-01); **não** propor recurso — o recurso é instituto do PT (C-02); ausência de evidência ⇒ insuficiência de comprovação declarada, não conceito baixo |
| **Histórias** | **US01** Como chefe superior, quero saber se sou a autoridade competente para avaliar este plano, para não avaliar fora de competência. **US02** Como chefe superior, quero responder aos quatro questionamentos com base nos registros, para fundamentar o conceito. **US03** Como chefe superior, quero que os fatores externos apareçam separados do desempenho, para avaliar com justiça. **US04** Como chefe superior, quero um parecer formal exportável, para registro no Petrvs/SEI |
| **T01** (competência) | **Dado** que a unidade avaliada é a própria unidade instituidora, **quando** a avaliação for solicitada, **então** a skill deve informar a dispensa da avaliação por nível superior (RN-10) e não emitir conceito |
| **T02** (RN-13) | **Dado** um plano com 8 entregas, 6 concluídas no prazo e 2 atrasadas com justificativa, **quando** avaliado, **então** os quatro questionamentos devem ser respondidos individualmente, cada um com a evidência que o sustenta |
| **T03** (qualidade × quantidade) | **Dado** entrega com meta quantitativa atingida mas critério de aceite não satisfeito, **quando** avaliada, **então** a skill **não** deve classificá-la como integralmente alcançada |
| **T04** (fator externo — corrige A-02) | **Dado** atraso decorrente de dependência externa documentada em `registros_risco`, **quando** avaliado, **então** o fator deve aparecer em bloco separado e a fundamentação deve explicitar que ele **não** foi usado para rebaixar o conceito |
| **T05** (decisão humana) | **Dado** conceito sugerido "adequado" sem decisão humana registrada, **quando** o parecer for consultado, **então** o estado deve ser `rascunho` e o parecer deve ostentar a marcação de não homologado |
| **T06** (prazo) | **Dado** encerramento do plano em 30/04 e avaliação iniciada em 05/06, **quando** a skill for acionada, **então** deve indicar violação do prazo de 30 dias (RN-12), sem impedir o registro |
| **T07** (convenção local) | **Dado** que exista regra institucional vigente com faixa `≥ 80 % = adequado`, **quando** aplicada, **então** a saída deve identificá-la como **convenção institucional do ICMBio**, com fonte, e não como exigência da IN 24/2023 |
| **T08** (insuficiência) | **Dado** ausência de evidências para 3 das 8 entregas, **quando** avaliado, **então** a saída deve declarar insuficiência de comprovação para essas entregas antes de qualquer conceito global |

### 6.3. S23 — Registro de Execução do Plano de Trabalho do Participante

| Campo | Especificação |
| ----- | ------------- |
| **Prioridade** | P2 |
| **Objetivo** | Apoiar o participante no registro mensal e tempestivo dos trabalhos realizados e das intercorrências, mantendo a consistência com a carga horária disponível pactuada |
| **Dependências** | `planos_trabalho` (migração 002); S07 (CHD); S08 (alocações/contribuições); S12 (plano pactuado); S17-mínimo (evidências); S14 (repactuação) |
| **Entradas** | Plano de trabalho vigente com contribuições, percentuais e critérios de avaliação; CHD planejada; relatos de trabalhos realizados; intercorrências; eventos planejados (férias, licenças, afastamentos); usufruto/compensação de horas; data de referência |
| **Saídas** | Registro de execução versionado; trabalhos realizados por contribuição; CHD realizada × planejada; **intercorrências classificadas e justificadas**; eventos planejados separados das intercorrências; ajuste de carga horária com motivo compatível com o Petrvs; controle de tempestividade (dia 10); pendências para o próximo ciclo; solicitações de repactuação encaminhadas a S14 |
| **Regras principais** | RN-17 a RN-26. **Férias, licenças e afastamentos nunca são classificados como intercorrência** (RN-21) — são realocados para eventos planejados e devem ter sido considerados na CHD; toda intercorrência exige justificativa (RN-18b); a avaliação é do plano como um todo, logo o registro **não** produz nota por atividade (RN-27); registro fora do prazo é aceito, mas marcado como intempestivo, com o prazo violado explicitado; **dados sensíveis de saúde não são armazenados** — a intercorrência de natureza pessoal é registrada por categoria e impacto em horas, com a justificativa detalhada mantida fora do banco (Seção 10, RP18); a skill não altera o plano pactuado — repactuação é rito de S14 (RN-23) |
| **Histórias** | **US01** Como participante, quero registrar o que realizei em cada contribuição, para que a chefia acompanhe a evolução. **US02** Como participante, quero registrar uma intercorrência com justificativa, para que ela seja considerada na avaliação. **US03** Como participante, quero registrar usufruto de horas de uma operação anterior, para que minha carga horária do mês fique correta. **US04** Como participante, quero saber quantos dias faltam para o prazo do dia 10, para não perder o prazo |
| **T01** (positivo) | **Dado** um PT mensal com 4 contribuições somando 100 %, **quando** o registro for concluído, **então** cada contribuição deve ter relato próprio e a CHD realizada deve ser apurada |
| **T02** (negativo / RN-21) | **Dado** que o participante registre "tirei 10 dias de férias" como intercorrência, **quando** classificado, **então** a skill deve reclassificar como **evento planejado** e verificar se foi descontado da CHD |
| **T03** (RN-24/25) | **Dado** usufruto de 16 h referentes a operação do mês anterior, **quando** registrado, **então** a CHD do período deve ser reduzida em 16 h e a ocorrência deve receber o motivo "Outras hipóteses (subtração de carga horária)" com descrição do vínculo temporal |
| **T04** (limite) | **Dado** CHD planejada de 160 h e soma dos trabalhos equivalente a 96 h sem intercorrência ou evento que justifique, **quando** o registro for fechado, **então** a skill deve apontar a inconsistência e perguntar (RN-26), sem preencher automaticamente |
| **T05** (prazo) | **Dado** registro do mês de agosto iniciado em 14 de setembro, **quando** submetido, **então** deve ser marcado intempestivo com referência a RN-19/RN-20 |
| **T06** (segurança / RP18) | **Dado** relato de intercorrência com informação de saúde, **quando** processado, **então** a skill deve registrar apenas categoria e impacto em horas, alertar o participante e **não** persistir o conteúdo clínico |
| **T07** (integração) | **Dado** um registro concluído, **quando** S21 for executada para o mesmo período, **então** o PT deve constar como executado no relatório de bloqueios de conclusão do PE (RN-04) |

### 6.4. S24 — Avaliação do Plano de Trabalho do Participante

| Campo | Especificação |
| ----- | ------------- |
| **Prioridade** | P2 |
| **Objetivo** | Apoiar a chefia da unidade de execução na avaliação mensal do plano de trabalho do participante, aplicando os cinco critérios da IN 24/2023 e conduzindo o rito de notificação, recurso, reavaliação e ações de desenvolvimento |
| **Dependências** | S23 (registro de execução); S12 (plano pactuado + critérios do TCR); S05 (critérios de aceite das entregas); S10 (fatos externos); S17 (evidências); S21 (contexto do PE) |
| **Entradas** | Plano de trabalho pactuado e vigente; registro de execução do período; critérios de avaliação definidos no plano/TCR; TCR e regras específicas da unidade; intercorrências registradas; fatos externos; histórico de avaliações do participante |
| **Saídas** | Controle do prazo de 20 dias (RN-28); **os cinco critérios apurados e fundamentados individualmente** (RN-29); conceito **sugerido** com confiança; sinalização de justificativa obrigatória (RN-31); minuta de notificação (RN-30); elegibilidade e prazos de recurso e reavaliação (RN-32); ações de desenvolvimento propostas (RN-34); pendências reprogramáveis para o ciclo seguinte (RN-35); parecer exportável |
| **Regras principais** | RN-27 a RN-36. A avaliação é **única e sobre o plano como um todo** — a skill não emite conceito por atividade nem por entrega (RN-27); o agente sugere, o humano decide (I2); os fatos externos à capacidade de ação do participante **e da chefia** são apurados em critério próprio e não rebaixam automaticamente o conceito; o foco é a contribuição para as entregas, **nunca comportamento pessoal** (RN-33) — critérios comportamentais só entram se previamente definidos no TCR; ausência de critérios previamente definidos ⇒ pergunta pendente e avaliação não emitida (I4); avaliação sem registro do participante (S23) **não é emitida**; conceito 1 ou 5 sem justificativa é bloqueado (RN-31); conceito 4 ou 5 dispara automaticamente o cálculo dos prazos de recurso; a saída deve declarar que a avaliação **não substitui** a avaliação anual (RN-36) |
| **Histórias** | **US01** Como chefe de UE, quero avaliar o plano de trabalho aplicando os cinco critérios, para produzir uma avaliação fundamentada. **US02** Como chefe de UE, quero ser impedido de atribuir conceito extremo sem justificar, para cumprir a norma. **US03** Como chefe de UE, quero gerar a notificação ao participante e conhecer os prazos de recurso, para conduzir o rito corretamente. **US04** Como chefe de UE, quero propor ações de desenvolvimento coerentes com a justificativa do conceito, para estimular o aprimoramento. **US05** Como participante, quero registrar recurso com minhas justificativas, para que a chefia reavalie |
| **T01** (positivo) | **Dado** PT integralmente executado conforme pactuado, com critérios atendidos e TCR cumprido, **quando** avaliado, **então** os cinco critérios devem ser apurados individualmente e o conceito sugerido deve ser "adequado" ou superior, com fundamentação por critério |
| **T02** (RN-31) | **Dado** conceito "excepcional" sem justificativa preenchida, **quando** a emissão for solicitada, **então** a skill deve bloquear e exigir a justificativa |
| **T03** (RN-32) | **Dado** conceito "inadequado" homologado e notificado em 12/09, **quando** o rito for consultado, **então** a skill deve informar o prazo de recurso até 22/09 e o prazo de manifestação da chefia até 10 dias após o recurso |
| **T04** (RN-27) | **Dado** um plano com 5 contribuições de desempenho heterogêneo, **quando** avaliado, **então** a skill deve produzir **uma única** avaliação do plano, usando as contribuições como fundamentação — nunca 5 conceitos |
| **T05** (I4) | **Dado** plano de trabalho sem critérios de avaliação previamente definidos, **quando** a avaliação for solicitada, **então** a skill deve gerar pergunta pendente e não emitir conceito (RN-29-2) |
| **T06** (RN-29-3) | **Dado** que a execução foi comprometida por indisponibilidade de sistema institucional documentada, **quando** avaliada, **então** o fato externo deve compor critério próprio e a fundamentação deve registrar seu efeito, sem rebaixamento automático |
| **T07** (RN-35) | **Dado** meta parcialmente executada com justificativa coerente, **quando** avaliada, **então** a saída deve oferecer a reprogramação da pendência para o PT seguinte e **não** acionar política de consequências |
| **T08** (RN-33 / segurança) | **Dado** que a chefia insira observação sobre característica pessoal do participante não prevista no TCR, **quando** processada, **então** a skill deve recusar sua incorporação à fundamentação e registrar o motivo |
| **T09** (RN-36 / regressão) | **Dado** qualquer parecer emitido, **quando** exportado, **então** deve conter a ressalva de que a avaliação do PGD não substitui a avaliação de desempenho anual |
| **T10** (integração) | **Dado** todas as avaliações de PT de um período homologadas, **quando** S21 for consultada, **então** o bloqueio de conclusão do PE relativo àquele período deve estar liberado |

---

## 7. Modelo de dados — migração 002

Migração `002_execucao_avaliacao.sql`, aplicada sobre o esquema `001`. **12 tabelas novas**
e **8 triggers de imutabilidade**, seguindo integralmente as convenções do `AT-01`
(PK `CHAR(36)` UUID gerado pela aplicação, soft-delete, `created_at`/`updated_at`, `ENUM`
para status, `JSON` nativo, `DECIMAL(5,2)` para métricas, nenhuma FK física para o PETRVS).

### 7.1. Grupo 8 — Plano de trabalho (entidade ausente no modelo comum)

| Tabela | Papel |
| ------ | ----- |
| `planos_trabalho` | Cabeçalho: `codigo` legível (`PT-2026-08-0001`), `participante_id` (→ `participantes`, pseudonimizado), `plano_capacidade_id`, `periodo_inicio/fim`, `versao_atual`, `estado` ENUM(`rascunho`,`pactuado`,`em_execucao`,`registrado`,`avaliado`,`em_recurso`,`encerrado`), `petrvs_plano_trabalho_id`, soft-delete |
| `planos_trabalho_versoes` | **Imutável.** `chd_planejada_h DECIMAL(7,2)`, `jornada_diaria_h`, `dias_trabalhaveis`, `ajuste_ch_h` (usufruto −/compensação +), `contribuicoes JSON` (entrega_id, percentual, descrição, critérios de avaliação), `atividades_nao_vinculadas JSON`, `tcr_regras JSON`, `motivo_versao`, `execucao_id` |

Restrição de integridade: soma de `contribuicoes[].percentual` + `atividades_nao_vinculadas[].percentual` = 100,00 — validada na aplicação (`versoes.py`) e por `CHECK` sobre coluna gerada.

### 7.2. Grupo 9 — Registro de execução (S21 e S23)

| Tabela | Papel |
| ------ | ----- |
| `registros_execucao_entrega` | Cabeçalho por (entrega, período): `entrega_id`, `plano_entregas_periodo`, `versao_atual`, `estado` ENUM(`aberto`,`registrado`,`concluido`,`bloqueado`) |
| `registros_execucao_entrega_versoes` | **Imutável.** `progresso_realizado DECIMAL(5,2)` `CHECK (0..100)`, `progresso_esperado_ref DECIMAL(5,2)` (cópia do planejado, para desvio), `situacao` ENUM, `narrativa_evolucao TEXT`, `meta_apurada JSON`, `motivo_versao`, `execucao_id` |
| `registros_execucao_trabalho` | Cabeçalho por (plano de trabalho, período): `plano_trabalho_id`, `versao_atual`, `estado`, `registrado_em`, `prazo_limite DATE`, `tempestivo TINYINT(1)` |
| `registros_execucao_trabalho_versoes` | **Imutável.** `chd_realizada_h DECIMAL(7,2)`, `trabalhos JSON` (por contribuição), `pendencias JSON`, `motivo_versao`, `execucao_id` |
| `ocorrencias` | Genérica e polimórfica: `objeto_tipo` ENUM(`entrega`,`plano_trabalho`), `objeto_id`, `classe` ENUM(`intercorrencia`,`evento_planejado`,`ajuste_carga_horaria`,`fato_externo`), `categoria` VARCHAR (taxonomia RN-22), `motivo_petrvs` VARCHAR (compatível com a lista do Petrvs), `impacto_horas DECIMAL(7,2)`, `impacto_descricao`, `justificativa TEXT`, `sensivel TINYINT(1)`, `confianca_classificacao` ENUM, `execucao_id` |
| `evidencias` | Versão mínima do S17: `objeto_tipo`, `objeto_id`, `tipo` ENUM(`documento`,`link`,`processo_sei`,`registro_sistema`,`indicador`,`ata`,`aprovacao`), `referencia`, `periodo`, `autoria`, `suficiencia` ENUM(`suficiente`,`parcial`,`insuficiente`), `sensivel TINYINT(1)` |

### 7.3. Grupo 10 — Avaliação (S22 e S24)

| Tabela | Papel |
| ------ | ----- |
| `avaliacoes` | Cabeçalho: `objeto_tipo` ENUM(`plano_entregas`,`plano_trabalho`), `objeto_id`, `periodo_inicio/fim`, `avaliador_id`/`avaliador_unidade_id`, `versao_atual`, `estado` ENUM(`rascunho`,`homologada`,`notificada`,`em_recurso`,`reavaliada`,`final`), `prazo_limite DATE`, `tempestiva TINYINT(1)`, `dispensa_aplicada` VARCHAR NULL (RN-10/11), `petrvs_avaliacao_id` |
| `avaliacoes_versoes` | **Imutável.** `conceito` ENUM(`excepcional`,`alto_desempenho`,`adequado`,`inadequado`,`nao_executado`), `origem_conceito` ENUM(`sugerido_agente`,`decisao_humana`), `confianca` ENUM, `criterios_apurados JSON` (4 questionamentos para PE / 5 critérios para PT), `fatores_externos JSON`, `fundamentacao TEXT`, `evidencias_ref JSON`, `decisao_humana_id` (→ `decisoes_humanas`), `motivo_versao`, `execucao_id` |
| `recursos_avaliacao` | `avaliacao_id`, `notificado_em DATE`, `prazo_recurso DATE` (+10 d), `interposto_em DATE NULL`, `justificativa_participante TEXT`, `prazo_manifestacao DATE` (+10 d), `decisao` ENUM(`acatado`,`acatado_parcialmente`,`nao_acatado`) NULL, `decidido_em DATE NULL`, `avaliacao_versao_resultante INT NULL` |
| `acoes_desenvolvimento` | `avaliacao_id`, `tipo` ENUM(`capacitacao`,`treinamento_em_servico`,`acompanhamento`,`redimensionamento_plano`,`outro`), `descricao`, `responsavel_rotulo`, `prazo DATE`, `status` ENUM |

### 7.4. Triggers e regras de ouro

Oito triggers novos, no mesmo padrão do `schema.sql` (statement único, `SIGNAL SQLSTATE
'45000'`), rejeitando `UPDATE` e `DELETE` em: `planos_trabalho_versoes`,
`registros_execucao_entrega_versoes`, `registros_execucao_trabalho_versoes` e
`avaliacoes_versoes`.

Aderência às cinco regras de ouro:

| Regra de ouro | Como este bloco a cumpre |
| ------------- | ------------------------ |
| 1 — ID persistente | Todos os cabeçalhos com UUID + código legível: `PT-2026-08-0001`, `REX-ENT-2026-0001-Q2`, `AVA-PT-2026-08-0001` |
| 2 — Nova versão, nunca sobrescrita | Quatro tabelas `*_versoes` imutáveis; reavaliação após recurso **cria versão nova** e preserva a original |
| 3 — Origem, regra e confiança | Toda linha de versão referencia `execucao_id` em `execucoes_skill`, com `regras_aplicadas` = códigos derivados de RN-01..RN-36 |
| 4 — Decisão humana separada | `avaliacoes_versoes.decisao_humana_id`; sem ele, `origem_conceito = 'sugerido_agente'` e `estado = 'rascunho'` |
| 5 — Dado ausente vira pergunta | Critério de aceite ausente, evidência ausente, registro do participante ausente e impacto de ocorrência ausente geram `perguntas_pendentes` |

Toda escrita nessas tabelas passa por funções novas em `src/dados/versoes.py`:
`criar_plano_trabalho`, `nova_versao_plano_trabalho`, `registrar_execucao_entrega`,
`registrar_execucao_trabalho`, `registrar_ocorrencia`, `criar_avaliacao`,
`nova_versao_avaliacao`, `registrar_recurso`. **Nenhum INSERT/UPDATE manual.**

---

## 8. Mapeamento com o PETRVS

O `AT-01` §2.1 identifica as camadas 3 (Execução) e 4 (Avaliação) do PETRVS, até hoje não
exploradas pelo projeto. O bloco S21–S24 é o primeiro a consumi-las.

| Objeto do agente | Tabela/view PETRVS | Campo de vínculo | Uso |
| ---------------- | ------------------ | ---------------- | --- |
| `registros_execucao_entrega_versoes.progresso_realizado` | `planos_entregas_entregas.progresso_realizado` `DECIMAL(5,2)` | `entregas.petrvs_entrega_id` | Conciliação agente × Petrvs; **atenção**: o AT-01 §2.4 documenta anomalias reais (escala 0–1 × 0–100 e 9 registros negativos) — a conciliação precisa normalizar antes de comparar |
| Estado do plano de entregas | `planos_entregas.status` (`INCLUIDO`,`ATIVO`,`CONCLUIDO`,`AVALIADO`) | `petrvs_plano_entregas_id` | Espelha o ciclo de S21 → S22 |
| `planos_trabalho` + `_versoes` | `planos_trabalhos` (14.168) + `planos_trabalhos_entregas` (69.208, `forca_trabalho DECIMAL(5,2)`) | `petrvs_plano_trabalho_id` | Origem da CHD (`carga_horaria` + `forma_contagem_carga_horaria`) e das contribuições |
| `registros_execucao_trabalho` | `planos_trabalhos_consolidacoes` (40.880) + `atividades` (141.724) | `petrvs_consolidacao_id` | Registro mensal de execução do PT |
| `ocorrencias` (eventos planejados) | `afastamentos` (7.456) | `petrvs_afastamento_id` | Base de RN-21 e do desconto de CHD |
| `avaliacoes` + `_versoes` | `avaliacoes` (26.931) + `tipos_avaliacoes_notas` (escala 1–5) | `petrvs_avaliacao_id` | Escala idêntica à de RN-14; permite comparar conceito sugerido × conceito real |

Três usos previstos, todos **somente leitura** (ADR-002):

1. **Espelhamento** — estender `sincronizar_ref.py` com as views de execução/avaliação da
   unidade-piloto, respeitando as restrições VQL já documentadas (prefixo
   `petrvs_icmbio_`, `CAST(... AS DATE)`, sem `DATEDIFF`, sem window function,
   `deleted_at IS NULL` em todo FROM/JOIN).
2. **Conciliação** — relatório de divergência entre o registrado no agente e o registrado
   no Petrvs, por entrega e por PT.
3. **Validação acadêmica (RC2)** — comparar o conceito sugerido por S22/S24 com o conceito
   real lançado em `avaliacoes` para o mesmo objeto: é a métrica de acurácia mais forte
   disponível para o bloco. Exige anonimização (ver Seção 10).

**Dependência crítica:** os três usos estão bloqueados enquanto o acesso ao Denodo não for
restabelecido (RP16, `docs/gestao/riscos.md`). O plano trata isso na Seção 9 com uma
estratégia de *dados sintéticos realistas* para não travar E1–E5.

---

## 9. Plano de desenvolvimento em etapas

### 9.1. Visão geral

| Etapa | Nome | Duração | Frente T (plataforma) | Frente N (negócio) | Entrega ao final |
| ----- | ---- | ------- | --------------------- | ------------------ | ---------------- |
| **E0** | Fundamento normativo | 2 sem | — | Carga das regras RN-01..RN-36 no S01; registro dos conflitos C-01..C-03 | Base normativa versionada e aprovada |
| **E1** | Especificação e contratos | 2–3 sem | Contratos Pydantic; motor de prazos | Fichas S21–S24 validadas pelos analistas; conjuntos anotados | Especificação homologada |
| **E2** | Modelo de dados e evidências | 2 sem | Migração 002 + triggers + `versoes.py`; S17-mínimo | Vocabulário de ocorrências e evidências | Banco pronto, teste de imutabilidade aprovado |
| **E3** | S21 e S23 — registro de execução | 3–4 sem | Implementação, endpoints, validadores | Casos S21-T01..T07 e S23-T01..T07 executados | **Registro de execução operacional** |
| **E4** | S22 e S24 — avaliação | 3–4 sem | Motor de conceito, competência, notificação | Casos S22-T01..T08 e S24-T01..T10 executados | **Avaliação operacional** |
| **E5** | Rito de recurso e desenvolvimento | 1–2 sem | `recursos_avaliacao`, `acoes_desenvolvimento`, reavaliação versionada | Fluxo revisado com a CGGE | Ciclo completo do PT |
| **E6** | Conciliação Petrvs | 2–3 sem | Espelhamento das camadas 3 e 4; relatório de divergência | Validação contra dados reais da unidade-piloto | Conciliação e métrica de acurácia |
| **E7** | Piloto e avaliação acadêmica | 3–4 sem | Orquestração S21→S24; correções críticas | Piloto CGOV/COCAGE em um ciclo real; questionário | **Checkpoint B4** |

**Total: 18 a 24 semanas** no caminho completo. **Caminho curto (E0–E3): 9 a 11 semanas.**

### 9.2. Detalhamento

#### E0 — Fundamento normativo (2 semanas)

**Objetivo:** transformar as 36 regras da Seção 3 em regras institucionais versionadas,
antes de qualquer linha de código — o passo 2 do ciclo de vida de skill (v4 §8).

- **T:** carga em `fontes_institucionais` (D1–D9) e `regras_institucionais(+_versoes)`, com
  `natureza`, `fonte`, `inicio_vigencia`; registro de C-01, C-02 e C-03 em
  `regras_conflitos`; regra institucional específica para a faixa percentual da CGOV (A-01),
  com fonte declarada e vigência.
- **N:** validação das 36 regras pelos analistas da CGGE; confirmação das datas do ciclo
  2026 (**Q1**); decisão sobre a faixa percentual (**Q2**); definição da política interna de
  medidas corretivas para conceitos 4 e 5 do PE (RN-15, **Q3**).
- **Aceite:** as 36 regras consultáveis via `/skill` com citação da fonte; nenhum conflito
  resolvido silenciosamente; ata de validação registrada em `docs/gestao/atas/`.
- **Pré-requisito:** S01 e S02 operacionais (incremento I2 do roadmap v4).

#### E1 — Especificação funcional e contratos (2–3 semanas)

- **T:** contratos Pydantic da Seção 5.3 em `src/skills_engine/contratos/`; **motor de
  prazos** (`src/skills_engine/prazos.py`) — determinístico, cobrindo os prazos de 10, 20 e
  30 dias, o dia 10 do mês subsequente, os prazos de recurso e a distinção dias corridos ×
  dias úteis; **motor de competência** (`competencia.py`) percorrendo `ref_unidades` com as
  dispensas RN-10/RN-11.
- **N:** revisão das fichas S21–S24 pelos analistas; **conjuntos anotados**: ≥ 40 relatos de
  execução de PE e ≥ 40 de PT, classificados manualmente (intercorrência × evento planejado
  × ajuste de CH); ≥ 20 pares (registro → conceito) extraídos dos pareceres já produzidos
  pelos protótipos `cgov-*`.
- **Aceite:** motor de prazos com 100 % de exatidão em bateria de 30 casos de calendário
  (incluindo virada de mês, feriados e meses de 31 dias); contratos com validação de
  fronteira testada; conjuntos anotados versionados em `skills/exemplos/`.

#### E2 — Modelo de dados e evidências mínimas (2 semanas)

- **T:** `src/dados/migracoes/002_execucao_avaliacao.sql` (12 tabelas + 8 triggers);
  extensão de `versoes.py` com as 8 funções novas; smoke test `--teste` cobrindo o novo
  bloco com rollback; backup validado com o esquema ampliado; S17-mínimo (tabela
  `evidencias` + vinculação).
- **N:** taxonomia de ocorrências (categorias de RN-22) alinhada com a lista de motivos do
  Petrvs; catálogo de tipos de evidência aceitos no ICMBio.
- **Aceite:** 33 tabelas no banco; `UPDATE` em cada uma das quatro novas `*_versoes`
  rejeitado com `ERROR 1644`; smoke test criando PT v1 → registro de execução → avaliação
  → recurso → avaliação v2, com histórico íntegro e rollback limpo.

#### E3 — S21 e S23: registro de execução (3–4 semanas)

- **T:** implementação das duas skills; validadores determinísticos (progresso × meta,
  CHD, totalização, bloqueios de conclusão RN-04); classificador de ocorrência com
  confiança; endpoints `POST /execucao/entrega` e `POST /execucao/trabalho`; integração com
  S14 para solicitações de ajuste.
- **N:** execução dos 14 casos de teste (S21-T01..T07, S23-T01..T07); processamento de um
  ciclo real (ou sintético realista) da CGOV; revisão um a um dos alertas com registro em
  `decisoes_humanas`.
- **Aceite:** progresso nunca apurado por contagem de atividades (T02/A-03); férias jamais
  classificadas como intercorrência (T02 de S23); conclusão de PE bloqueada com PT pendente
  (T03); nenhum dado sensível de saúde persistido (T06); macro-F1 do classificador de
  ocorrências medida e registrada.

#### E4 — S22 e S24: avaliação (3–4 semanas)

- **T:** motor de conceito (faixa determinística + fundamentação por LLM + exigência de
  decisão humana); verificação de competência e dispensas; geração de parecer exportável
  (`.md` e `.docx`) e da minuta de notificação; endpoints `POST /avaliacao/plano-entregas`
  e `POST /avaliacao/plano-trabalho`.
- **N:** execução dos 18 casos de teste (S22-T01..T08, S24-T01..T10); validação dos
  pareceres pelos analistas contra os pareceres reais produzidos na CGOV; ajuste do texto
  padrão do parecer.
- **Aceite:** nenhum conceito emitido sem `decisao_humana_id` (I2); conceito 1 ou 5 sem
  justificativa bloqueado (RN-31); fatores externos sempre em bloco separado (T04/A-02);
  parecer sempre com a ressalva de RN-36; ausência de critério pactuado impede a avaliação
  (T05 de S24).

#### E5 — Rito de recurso, reavaliação e desenvolvimento (1–2 semanas)

- **T:** fluxo `notificada → em_recurso → reavaliada → final`; cálculo dos dois prazos de 10
  dias; reavaliação como **nova versão** de `avaliacoes_versoes`, preservando a original;
  `acoes_desenvolvimento` com responsável e prazo.
- **N:** validação do rito com a CGGE e, se possível, com a PFE; modelo de notificação e de
  manifestação de não acatamento.
- **Aceite:** reavaliação preserva integralmente a avaliação original; recurso indisponível
  para conceitos 1–3 e para avaliações de PE (C-02); ação de desenvolvimento obrigatória
  quando o conceito final for 4 ou 5 e não houver justificativa acatada (RN-34/RN-35).

#### E6 — Conciliação com o PETRVS (2–3 semanas) — *dependente de RP16*

- **T:** extensão de `sincronizar_ref.py` para as camadas 3 e 4; normalização das anomalias
  de escala documentadas no AT-01 §2.4; relatório de divergência agente × Petrvs por
  entrega e por PT; comparação conceito sugerido × conceito real.
- **N:** validação dos números com a CGGE; análise dos casos divergentes.
- **Aceite:** conciliação executada para a unidade-piloto; divergências explicadas ou
  registradas como pendência; acurácia do conceito sugerido medida e registrada.
- **Contingência (RP16 persistente):** substituir por base sintética realista derivada dos
  pareceres da CGOV; E6 é a **única etapa** com dependência dura do Denodo — E0 a E5 e E7
  seguem sem ele.

#### E7 — Piloto e avaliação acadêmica (3–4 semanas) → **Checkpoint B4**

- **T:** orquestração do fluxo S21→S24 com persistência de estado; testes de integração
  INT-E01..E08; correção apenas de defeitos críticos e altos.
- **N:** piloto em um ciclo real das unidades CGOV e COCAGE — um quadrimestre de PE e ao
  menos um mês de PT por participante; questionário de utilidade e confiança; relatório de
  métricas.
- **Aceite (B4):** ao menos 2 chefias e 4 participantes usam as skills ao vivo; um caso
  completo percorre S21→S24 (incluindo um recurso simulado) sem perda de identificadores;
  todos os prazos regulamentares calculados corretamente no ciclo real; feedback registrado;
  proposta vigente atualizada com o bloco integrado ao catálogo.

### 9.3. Dependências e caminho crítico

```
E0 ──► E1 ──► E2 ──► E3 ──► E4 ──► E5 ──► E7
                       │              ▲
                       └──► E6 ───────┘   (E6 pode correr em paralelo a E4/E5)
```

| Etapa | Depende de (interno) | Depende de (projeto) |
| ----- | -------------------- | -------------------- |
| E0 | — | S01, S02 operacionais (I2) |
| E1 | E0 | — |
| E2 | E1 | migração 001 aplicada (I0 ✔) |
| E3 | E2 | S04/S05 (metas e critérios, I3); S07/S08 (capacidade, I5) para a CHD |
| E4 | E3 | S05 (critérios de aceite); S10 (riscos → fatores externos, I6); S17-mínimo (E2) |
| E5 | E4 | — |
| E6 | E2 | **Denodo liberado (RP16)** |
| E7 | E4, E5 | agente unificado (I6) para a experiência conversacional |

**Caminho curto (E0–E3, 9–11 semanas):** entrega S21 e S23 operacionais usando metas e
CHD informadas manualmente, sem depender da conclusão de S05/S07/S08. Recomendado se a
CGGE quiser resultados no ciclo quadrimestral em curso. Custo: retrabalho estimado de
15–20 % em E3 quando S05/S07/S08 ficarem prontas.

### 9.4. Esforço estimado

Escala de referência do `04_backlog` (sprints de 2 semanas):

| Etapa | Pontos T | Pontos N | Observação |
| ----- | -------- | -------- | ---------- |
| E0 | 5 | 13 | Predomínio de trabalho dos analistas |
| E1 | 13 | 13 | Motor de prazos é o item mais sensível |
| E2 | 13 | 5 | Migração e triggers |
| E3 | 21 | 13 | Duas skills + classificador |
| E4 | 21 | 13 | Duas skills + geração de parecer |
| E5 | 8 | 5 | Rito processual |
| E6 | 13 | 8 | Bloqueado por RP16 |
| E7 | 13 | 21 | Piloto real |
| **Total** | **107** | **91** | |

---

## 10. Riscos específicos do bloco

A registrar em `docs/gestao/riscos.md`, na sequência da matriz v4 §10 (o último risco
registrado é RP16):

| ID | Risco | P × I | Mitigação |
| -- | ----- | ----- | --------- |
| **RP17** | **Dado sensível de saúde em intercorrência.** D1 §2.3 cita expressamente "situações de saúde" como intercorrência a registrar. Persistir isso violaria o RP06 e a governança de dados da v4 §11 | Alta × Alto | `ocorrencias.sensivel = 1`; armazenar **apenas categoria e impacto em horas**; conteúdo clínico nunca persistido; S23-T06 como teste de segurança obrigatório; orientação explícita ao participante na interface |
| **RP18** | **Agente induzindo o conceito.** Sugestão de conceito com aparência de decisão pode enviesar a chefia e gerar contestação com efeito funcional | Média × Alto | Invariante I2; `origem_conceito` explícito; parecer não homologado ostenta marcação; justificativa sempre exigida da chefia, nunca autopreenchida sem revisão |
| **RP19** | **Assimetria PE × PT** (C-02): tratar as duas avaliações como um só objeto levaria a oferecer recurso onde ele não existe | Média × Alto | Separação estrutural desde o modelo de dados (`avaliacoes.objeto_tipo`); testes de regressão específicos |
| **RP20** | **Datas do ciclo 2026 inconsistentes** (C-01): o motor de prazos calcularia prazos errados | Alta × Alto | E0 bloqueia a implementação até confirmação da CGGE (**Q1**); enquanto isso, o motor recebe o calendário por configuração, não por constante |
| **RP21** | **Faixa percentual sem lastro normativo** (A-01) migrar para o agente como se fosse norma | Média × Médio | Registro como regra institucional com fonte e vigência; rotulagem obrigatória na saída (S22-T07) |
| **RP22** | **Uso indevido da avaliação do PGD como avaliação de desempenho anual** (RN-36) | Média × Médio | Ressalva obrigatória em todo parecer (S24-T09); menção na capacitação |
| **RP23** | **Volume do ciclo mensal.** No ICMBio, PT mensal × N participantes × 12 meses gera carga de registro e avaliação que pode inviabilizar o uso manual da skill | Média × Médio | Processamento em lote no S18; priorizar unidades-piloto; medir tempo médio por registro no E7 |
| **RP24** | **Exposição de dados individuais em relatórios** (transparência, D7) | Média × Alto | Pseudônimos em `participantes.rotulo` (D2); agregação por unidade; nenhum ranking individual (regra já prevista em S18) |

---

## 11. Critérios de aceite e definição de pronto

### 11.1. Definição de pronto por skill (herdada do `04_backlog` §14, ampliada)

Uma skill do bloco S21–S24 só é considerada pronta quando:

1. Ficha funcional aprovada pelos analistas (passo 1 do ciclo de vida, v4 §8).
2. Todas as regras aplicáveis (RN-xx) carregadas em `regras_institucionais` com fonte e
   vigência, e referenciadas por código na saída.
3. Conjunto anotado com ≥ 40 exemplos reais processados.
4. 100 % dos casos de teste da ficha executados e registrados em `docs/testes/`.
5. Cálculos determinísticos com exatidão de 100 % em bateria dedicada.
6. Contrato de saída v4 §8.3 gravado em `execucoes_skill` para toda execução.
7. Escrita exclusivamente via `src/dados/versoes.py`.
8. Teste de segurança de dados pessoais aprovado (RP17/RP24).
9. Nenhuma decisão de conceito emitida sem `decisao_humana_id` (S22/S24).
10. Documentação em `skills/specs/SKILL_Sxx.md`.

### 11.2. Aceite do bloco (Checkpoint B4)

- [ ] 36 regras normativas carregadas, versionadas e citáveis com fonte
- [ ] Conflitos C-01, C-02 e C-03 registrados e decididos por humano
- [ ] Migração 002 aplicada: 33 tabelas, 14 triggers, imutabilidade comprovada nas 4 novas `*_versoes`
- [ ] Motor de prazos com 100 % de exatidão nos 5 prazos normativos (10 / 20 / 30 dias, dia 10, recurso)
- [ ] Motor de competência aplicando corretamente as dispensas RN-10 e RN-11
- [ ] 32 casos de teste das quatro skills executados e registrados
- [ ] Ciclo completo S21→S22→S23→S24→recurso→reavaliação percorrido sem perda de identificadores
- [ ] Conciliação com o Petrvs executada (ou contingência sintética documentada, se RP16 persistir)
- [ ] Piloto real em CGOV e COCAGE com feedback registrado
- [ ] Nenhum dado sensível de saúde persistido no banco (auditoria com `rg` sobre dump anonimizado)
- [x] Proposta v6 integra S21–S24 e reposiciona S13/S16/S17

---

## 12. Questões em aberto

| # | Questão | Destinatário | Bloqueia |
| - | ------- | ------------ | -------- |
| **Q1** | Quais são exatamente as datas dos quadrimestres do PE em 2026? A página do ciclo informa `01/01–31/04`, `01/05–30/07` e `01/08–31/12`, faixas internamente inconsistentes (C-01) | CGGE | E0, E1 (motor de prazos) |
| **Q2** | A faixa percentual usada hoje pela CGOV (`≥ 80 % = Adequado`) deve ser adotada como regra institucional do ICMBio, revista ou descartada? (A-01) | CGGE / CGOV | E0, E4 |
| **Q3** | Qual a política interna de medidas corretivas para conceitos 4 e 5 no **Plano de Entregas**, já que a IN 24/2023 não a estabelece (RN-15)? | CGGE / Direção | E4 |
| **Q4** | Os exercícios `exercio-m1.pdf` e `exercio-m2.pdf` do curso de Avaliação estão digitalizados sem camada de texto. Existe versão pesquisável, ou devem ser processados por OCR para compor os conjuntos anotados? | Solicitante | E1 (conjuntos anotados) |
| **Q5** | Chefias dispensadas de controle de frequência (D3 §13) não têm PT. Como S24 trata a unidade em que a chefia não possui plano de trabalho — e como isso afeta a regra de conclusão do PE (RN-04)? | CGGE | E3 |
| **Q6** | Contribuições a outras unidades e times volantes (D3 §16 e §17) entram no registro de execução de qual unidade? Impacta S23 e a matriz de S15 | CGGE | E3 |
| **Q7** | O parecer de avaliação deve ser instruído em processo SEI? Se sim, qual o tipo de documento e o fluxo? | CGGE / SEI | E4 |
| **Q8** | O acesso ao Denodo será restabelecido a tempo de E6 (RP16)? Se não, a contingência sintética é aceitável para a validação acadêmica? | TI / Dataprev | E6 |

---

## Anexo A — Rastreabilidade regra → skill → teste

| Regra | S21 | S22 | S23 | S24 | Teste-âncora |
| ----- | :-: | :-: | :-: | :-: | ------------ |
| RN-01 a RN-03 (quem/o quê/quando do PE) | ● | | | | S21-T06 |
| RN-04 (conclusão condicionada aos PTs) | ● | | ○ | ○ | S21-T03, S23-T07, S24-T10 |
| RN-05, RN-06 (ajustes e repactuação) | ● | | | | S21-T04 |
| RN-08 (esperado × realizado) | ● | ○ | | | S21-T01 |
| RN-09 a RN-11 (competência e dispensas) | | ● | | | S22-T01 |
| RN-12 (30 dias) | | ● | | | S22-T06 |
| RN-13 (quatro questionamentos) | | ● | | | S22-T02, T03 |
| RN-14 (escala de 5) | | ● | | ● | S22-T05, S24-T01 |
| RN-15, RN-16 (sem consequência direta no PE) | | ● | | | S22-T07 |
| RN-17 a RN-20 (quem/o quê/quando do PT) | | | ● | | S23-T01, T05 |
| RN-21, RN-22 (intercorrência × evento planejado) | | | ● | ○ | S23-T02 |
| RN-24, RN-25, RN-26 (CHD e horas) | | | ● | | S23-T03, T04 |
| RN-27 (avaliação única do plano) | | | | ● | S24-T04 |
| RN-28 (20 dias) | | | | ● | S24-T03 |
| RN-29 (cinco critérios) | | | ○ | ● | S24-T01, T05, T06 |
| RN-30, RN-31 (notificação e justificativa) | | | | ● | S24-T02 |
| RN-32 (recurso e reavaliação) | | | | ● | S24-T03 |
| RN-33 (contribuição, não comportamento) | | | | ● | S24-T08 |
| RN-34, RN-35 (desenvolvimento, não punição) | | | | ● | S24-T07 |
| RN-36 (não substitui avaliação anual) | | | | ● | S24-T09 |

● responsabilidade principal · ○ participação/consumo

---

## Anexo B — Fluxo temporal de um ciclo ICMBio

Exemplo para o quadrimestre `mai–ago/2026` (sujeito a Q1), com PT mensal:

| Data | Evento | Skill | Regra |
| ---- | ------ | ----- | ----- |
| até 30/04 | Pactuação do PE do quadrimestre e do PT de maio | S11, S12 | — |
| ao longo de mai–ago | Registro contínuo da evolução das entregas | **S21** | RN-03 |
| até 10/06 | Participante registra a execução do PT de maio | **S23** | RN-19, RN-20 |
| até 30/06 | Chefia da UE avalia o PT de maio (20 d após 10/06) | **S24** | RN-28 |
| +10 d da notificação | Prazo de recurso do participante | **S24** | RN-32 |
| +10 d do recurso | Manifestação/reavaliação da chefia | **S24** | RN-32 |
| … | Repetição mensal para jun, jul e ago | S23, S24 | RN-20 |
| até 31/08 | Registro final do PE e verificação dos 4 ciclos de PT | **S21** | RN-03, RN-04 |
| até 30/09 | Chefia superior avalia o PE (30 d após o encerramento) | **S22** | RN-12 |

---

**Fim do documento.** Alterações a este plano seguem o protocolo de manutenção do
`CLAUDE.md`: atualizar a Seção 10 (Estado do projeto) e sincronizar a memória persistente.
