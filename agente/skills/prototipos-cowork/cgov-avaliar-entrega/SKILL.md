---
name: "cgov-avaliar-entrega"
description: "Use this skill whenever the Coordenador de Governança (CGOV/ICMBio) needs to evaluate a completed or closing entrega at the end of its cycle or deadline. Triggers include: /avaliar_plano_entrega, \"avaliar entrega\", \"parecer de avaliação\", \"avaliação de desempenho da entrega\", \"o prazo da entrega venceu\", \"emitir conceito\", \"nota da entrega\", \"encerrar entrega\", \"fechar ciclo da entrega\", \"avaliação final\", \"desempenho da entrega\", \"entrega dentro do prazo?\", \"gerar parecer\", \"nota conceitual\". Always use when the Coordenador needs a formal evaluation of an entrega — even when phrased informally like \"como ficou a CGOV_02?\" or \"encerra a entrega e dá uma nota\"."
---

# SKILL: Avaliar Entrega — CGOV/ICMBio

Você está no modo **Avaliar Entrega**. Suspenda a conversação genérica e execute
estritamente as fases abaixo. O objetivo é aplicar a escala de avaliação do PGD,
emitir um **Parecer de Avaliação Institucional** formal e gerar um relatório `.md`
com instruções para registro no PETRVS/SEI.

---

## FASE 1 — COLETA DOS DADOS PARA AVALIAÇÃO

Solicite (apenas o que não foi ainda informado):

1. **ID da Entrega:** Qual o `id_entrega` a ser avaliado? (padrão: `CGOV_XX`)
2. **Data de referência:** Confirme a data de avaliação (padrão: hoje).
3. **Intercorrências:** Houve algum fato superveniente que impediu ou dificultou a
   execução? (ex.: contingenciamento, mudança de prioridade institucional, vacância)

Se as Planilhas A e B estiverem disponíveis na sessão, extraia automaticamente:
- `prazo_limite` (col. J da Planilha A)
- `% Concluído` (col. Q da Planilha A) → usar como referência; prevalece o cálculo pela Planilha B
- `status_atual` (col. P da Planilha A)
- `Etapas` da Planilha B — **use a regra de cálculo abaixo**
- Servidores responsáveis (cols. U–Y da Planilha A)

**Regra de cálculo do % Concluído (Planilha B):**
```
etapas_denominador = total de etapas da entrega EXCLUINDO as com status "Cancelada"
etapas_numerador   = etapas com status "Concluida" (somente)
% Concluido = (etapas_numerador / etapas_denominador) x 100
```
- Etapas com status **"Cancelada"** sao excluidas do numerador **e** do denominador.
- Etapas **"Em andamento"** e **"Nao iniciada"** entram apenas no denominador, nunca no numerador.
- Se o valor calculado pela Planilha B divergir do valor da col. Q da Planilha A, prevalece o valor calculado; registre a divergencia no parecer.

Se as planilhas NÃO estiverem disponíveis, pergunte:
- Percentual de conclusão atual (%)
- O prazo foi cumprido? (sim/não)
- Houve conclusão antes do prazo? Se sim, quantos dias antes?

---

## FASE 2 — APLICAÇÃO DA ESCALA DE AVALIAÇÃO DO PGD

⚠️ **Convenção local, não norma.** Os limiares percentuais desta escala (100%,
80%) são uma **prática consolidada da CGOV**, sem lastro expresso na
IN MGI nº 24/2023, na Portaria ICMBio nº 5.592/2025 ou em qualquer outro
normativo que discipline especificamente a avaliação de entregas do PGD.
Use-os como referência de trabalho — é o único corte hoje em uso, e substituí-lo
sem alternativa normativa pioraria a consistência das avaliações — mas não os
apresente no parecer como se fossem regra normativa. Se o Coordenador indicar
um critério diferente, ou identificar a norma que os discipline, atualize esta
escala e registre a mudança.

Aplique **obrigatoriamente** um dos cinco conceitos abaixo. Use a lógica decisória
na ordem apresentada — pare na primeira condição verdadeira:

```
1. "Não Executado"
   → % Concluído = 0%
   → Justificativa: entrega sem nenhuma etapa iniciada ou concluída.

2. "Excepcional"
   → % Concluído ≥ 100% E data de conclusão < prazo_limite
   → Justificativa: meta integralmente atingida com antecipação do prazo.

3. "Alto Desempenho"
   → % Concluído ≥ 100% E data de conclusão ≤ prazo_limite
   → Justificativa: meta integralmente atingida dentro do prazo.

4. "Adequado" (faixa de corte — convenção local, ver nota acima)
   → % Concluído entre 80% e 99%
   → Justificativa: meta substancialmente atingida; resultado de qualidade aceitável.

5. "Inadequado"
   → % Concluído < 80% sem justificativa técnica
   OU prazo extrapolado sem intercorrência documentada
   → Justificativa: execução aquém do mínimo exigido sem mitigação adequada.
```

**Intercorrências — informação a ponderar, nunca automatismo do conceito.**
Registre toda intercorrência relatada (contingenciamento, mudança de
prioridade institucional, vacância etc.) na Seção II do parecer,
independentemente do conceito calculado acima. A ausência ou presença de
intercorrência **não** é condição para "Alto Desempenho" nem rebaixa
automaticamente qualquer conceito — a única exceção listada é a de
"Inadequado" por prazo extrapolado sem intercorrência documentada, que
permanece condição explícita da escala. Fora esse caso, trate a intercorrência
como fator a ser examinado à parte, na análise qualitativa (Parágrafo 3): ela
pode fundamentar, com justificativa explícita no parecer, por que um
enquadramento específico é apropriado apesar de um percalço pontual — mas essa
ponderação é sempre argumentada por escrito, nunca um efeito automático de uma
condição booleana "sem intercorrências".

**Cálculo de antecipação ou atraso:**
```
dias_diferença = data_avaliação − prazo_limite
  → Valor negativo: entrega concluída com antecipação (Δ dias antes do prazo)
  → Valor positivo: entrega em atraso (Δ dias após o prazo)
  → Valor zero: entrega no prazo exato
```

---

## FASE 3 — REDAÇÃO DO PARECER FORMAL

Gere um arquivo `.md` e salve em `H:\Meu Drive\CGOV_PGD\` com o nome:
`AAAA.MM.DD_parecer_avaliacao_[id_entrega].md`

Use exatamente o template abaixo:

```
---
# PARECER DE AVALIAÇÃO INSTITUCIONAL — CGOV/ICMBio
**Número do Parecer:** [AAAA-MM-DD/[id_entrega]]
**Data de Emissão:** [data de hoje]
**Unidade Avaliadora:** Coordenação de Governança — CGOV/ICMBio
**Skill:** cgov-avaliar-entrega
---

## I. IDENTIFICAÇÃO DA ENTREGA

| Campo | Valor |
|---|---|
| id_entrega | [CGOV_XX] |
| Nome da Entrega | [nome completo] |
| Processo | [Governança de Processos / Gestão de Riscos / Gestão da Integridade] |
| Objetivo Estratégico | [IV-b/e/h/j — texto completo] |
| Demandante | [valor] |
| Destinatário | [valor] |
| Servidores Responsáveis | [lista dos servidores com flag = 1] |
| Prazo Estabelecido | [DD/MM/AAAA] |
| Data de Avaliação | [DD/MM/AAAA] |

---

## II. EVIDÊNCIAS DE DESEMPENHO

| Indicador | Valor |
|---|---|
| Total de etapas previstas | [T] |
| Etapas canceladas (excluidas) | [C] |
| Etapas validas (denominador) | [N = T - C] |
| Etapas concluidas (numerador) | [X] |
| Etapas em andamento | [Y] |
| Etapas nao iniciadas | [Z] |
| % Concluido (calculado) | [P% = X/N x 100] |
| Prazo cumprido? | [Sim / Não / Antecipado em N dias] |
| Intercorrências registradas | [Sim — descrever / Não] |

---

## III. CONCEITO ATRIBUÍDO

> # 🏅 [CONCEITO: Excepcional / Alto Desempenho / Adequado / Inadequado / Não Executado]

---

## IV. JUSTIFICATIVA TÉCNICA

[Redigir 3 a 5 parágrafos formais, estruturados da seguinte forma:]

**Parágrafo 1 — Contextualização:**
A entrega [id_entrega — nome_entrega], vinculada ao macroprocesso [Processo] e ao
objetivo estratégico [IV-X], teve como prazo-limite [DD/MM/AAAA] e foi submetida
à avaliação institucional em [data de avaliação].

**Parágrafo 2 — Análise Quantitativa:**
O cálculo de progresso, apurado com base no método de aferição pactuado — (nº de
etapas concluidas / nº de etapas validas) x 100, excluindo do denominador as etapas
com status "Cancelada" —, resultou em [P%] de execucao, correspondente a [X] etapas
concluidas de um total de [N] etapas validas (total previsto: [T], canceladas: [C]).
[Se antecipação/atraso: O prazo foi [cumprido com antecipação de N dias / cumprido
no prazo / extrapolado em N dias].]

**Parágrafo 3 — Análise Qualitativa:**
[Contextualizar o que foi entregue: produtos gerados, impacto institucional, alinhamento
com o Planejamento Estratégico. Mencionar se houve intercorrências.]

**Parágrafo 4 — Enquadramento na Escala do PGD:**
Com base nas evidências apuradas, esta entrega é enquadrada na categoria
**"[CONCEITO]"**, [razão pelo enquadramento nesta categoria — referencie os critérios
da escala]. [Se "Adequado" com justificativa: mencionar a intercorrência que justifica
o enquadramento acima de "Inadequado".]

**Parágrafo 5 — Recomendações (quando aplicável):**
[Somente se conceito for "Inadequado" ou "Não Executado": Descrever as providências
recomendadas para os próximos ciclos — ex.: revisão de cronograma, redistribuição de
responsabilidades, fatiamento em entregas menores.]

---

## V. INSTRUÇÕES PARA REGISTRO NO PETRVS/SEI

### 5.1 — Registro da Avaliação no PETRVS

**Pré-condição:**
Acesse o PETRVS com seu login institucional e navegue até:
**Gestão → Plano de Entregas → CGOV → [id_entrega: nome_entrega] → Avaliação**

**Passo 1 — Abrir o ciclo de avaliação**
- Clique em **"Iniciar Avaliação"** ou **"Registrar Avaliação Final"**
- Confirme que o período de avaliação está correto

**Passo 2 — Informar o resultado**
- Campo **"Percentual de Execução":** `[P%]`
- Campo **"Conceito":** selecione `[CONCEITO]`
- Campo **"Data de Conclusão":** `[data da última etapa concluída ou data de avaliação]`

**Passo 3 — Justificativa**
- No campo **"Justificativa / Memória de Cálculo"**, cole o texto do Item IV
  (Justificativa Técnica) acima
- Se o sistema tiver limite de caracteres, cole o resumo do Parágrafo 2 e 4

**Passo 4 — Intercorrências (se houver)**
- Registre no campo **"Intercorrências"** os fatos que impactaram a execução
- Anexe os documentos SEI de suporte, se existirem

**Passo 5 — Salvar e encaminhar**
- Clique em **"Salvar"** e depois em **"Encaminhar para Aprovação"**
- Verifique se o `status_atual` da entrega foi alterado para `"Concluída"` ou
  `"Avaliada"` conforme o fluxo do sistema

### 5.2 — Inclusão do Parecer no SEI (quando necessário)

Quando a avaliação exigir formalização em processo SEI:

**Passo 1:** Acesse o **SEI** → processo correspondente ao PGD da CGOV
**Passo 2:** Inclua um novo documento do tipo **"Nota Técnica"** ou **"Parecer"**
**Passo 3:** Cole o conteúdo das Seções I a IV deste relatório
**Passo 4:** Assine com certificado digital (gov.br)
**Passo 5:** Encaminhe para ciência da chefia imediata (CGGE)

### 5.3 — Atualização da Planilha A

Após o registro no PETRVS, atualize a Planilha A:

| Campo (col.) | Novo valor |
|---|---|
| status_atual (col. P) | `Concluída` |
| % Concluído (col. Q) | `[P como decimal, ex.: 0,85]` |

### Checklist de encerramento da entrega
- [ ] Conceito registrado no PETRVS
- [ ] Justificativa técnica inserida no sistema
- [ ] Intercorrências documentadas (se houver)
- [ ] Parecer assinado e juntado ao SEI (quando necessário)
- [ ] status_atual = "Concluída" na Planilha A
- [ ] % Concluído atualizado na Planilha A
- [ ] Servidores responsáveis notificados do encerramento

---

## VI. OBSERVAÇÕES FINAIS

[Campo livre para registrar ressalvas, recomendações para o próximo ciclo ou qualquer
informação adicional relevante.]

---
*Parecer emitido pelo Assistente de Gestão da CGOV.*
*Para fins oficiais, este documento deve ser revisado e assinado pelo Coordenador de
Governança antes de ser juntado a processos SEI.*
*Base normativa: IN MGI nº 24/2023 | PORTARIA ICMBio nº 5.592/2025*
```

---

## NOTAS INTERNAS DA SKILL

- **Conceito com dados parciais:** Se o Coordenador pedir avaliação de uma entrega
  ainda não encerrada ("qual seria o conceito hoje?"), emita o parecer como
  **"Avaliação Parcial"** e indique claramente que o conceito poderá mudar até o
  prazo final. Não use "Não Executado" para entregas com % > 0 em andamento.
- **Entrega com ciclo recorrente (ex.: CGOV_41):** Algumas entregas têm natureza
  contínua e recorrente (ex.: monitoramento a cada quadrimestre). Para essas, avalie
  cada ciclo separadamente com a mesma escala.
- **Tom do Parecer:** O Parecer é um documento institucional formal. Use linguagem
  técnica, objetiva e impessoal. Prefira a voz passiva. Evite julgamentos sobre
  servidores individualmente — avalie a entrega, não a pessoa.
- **Escala e normativa:** ⚠️ Os nomes dos cinco conceitos (Excepcional / Alto
  Desempenho / Adequado / Inadequado / Não Executado) seguem o espírito geral do
  PGD, mas os limiares percentuais (100%, 80%) e a lógica de enquadramento da
  Fase 2 são **convenção de trabalho da CGOV**, sem lastro expresso na
  IN MGI nº 24/2023 nem em normativo específico do ICMBio para avaliação de
  entregas — não os cite como regra normativa em pareceres formais. Caso o
  PETRVS use nomenclatura diferente, oriente o Coordenador a fazer a
  correspondência.
- **Intercorrências não são automatismo (correção de 30/08/2026):** versões
  anteriores desta skill exigiam "sem intercorrências" para o conceito "Alto
  Desempenho". Essa condição foi removida — a norma não prevê esse automatismo.
  Trate intercorrências sempre como informação a examinar separadamente (ver
  Fase 2).
- **Fluxo de aprovacao de atos normativos:** Apos a adequacao do texto final da
  minuta de portaria pela CGOV, o processo e encaminhado ao **Gabinete do Presidente
  do ICMBio** para aprovacao, assinatura e posterior publicacao no **Diario Oficial
  da Uniao (DOU)**. Este fluxo deve ser mencionado nas justificativas de entregas que
  dependem de formalizacao por ato normativo, pois a tramitacao no Gabinete e a
  publicacao no DOU estao fora da governanca direta da CGOV e impactam os prazos.

---

## NOTA DE CORREÇÃO — nomenclatura do ciclo (14.09.2026)

Versões anteriores desta skill tratavam `Q1/Q2/Q3` como **trimestres** e previam
um **Q4 implícito**. Está errado para 2026 em diante: o Plano de Entregas das
unidades do ICMBio é **quadrimestral** — três períodos de quatro meses, sem Q4.

| Rótulo | Início | Fim |
|---|---|---|
| Q1 | 01/01 | 30/04 |
| Q2 | 01/05 | 31/08 |
| Q3 | 01/09 | 31/12 |

O peso de referência 0,33 por período sempre esteve certo (três ciclos por ano);
o rótulo "trimestre" é que era resíduo do ciclo trimestral de 2025, que de fato
usava T1–T4. A segmentação acima é a implementada e testada em
`lib/periodos.py` do projeto `pgd-ocde-icmbio`.

**Calendário decidido (C-01 / RP20 / Q17 — 14.09.2026).** As datas da tabela
acima são definitivas: **o Q2 termina sempre em 31/08**. A página do ciclo
publicada pela CGGE, com faixas internamente inconsistentes (`01/01–31/04`,
`01/05–30/07`, `01/08–31/12`), não é usada como referência.
