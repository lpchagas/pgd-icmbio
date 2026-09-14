---
name: "cgov-registro-execucao"
description: "Use this skill whenever the Coordenador de Governança (CGOV/ICMBio) needs to record the execution progress of tasks (etapas) in the Plano de Entregas. Triggers include: /registro_execucao_entrega, \"registrar execução\", \"atualizar status da etapa\", \"marcar etapa como concluída\", \"etapa concluída\", \"etapa em andamento\", \"registrar andamento\", \"servidor concluiu\", \"atualizar progresso\", \"recalcular percentual\", \"atualizar plano de trabalho\", \"concluí uma etapa\", \"registrar entrega de etapa\". Always use when someone reports completion or progress on a specific task step — even in informal language like \"o servidor finalizou aquela atividade do CGOV_09\"."
---

# SKILL: Registrar Execução de Etapa — CGOV/ICMBio

Você está no modo **Registrar Execução**. Suspenda a conversação genérica e execute
estritamente as fases abaixo. O objetivo é atualizar o status de uma ou mais etapas
(Planilha B), recalcular o progresso da entrega macro correspondente (Planilha A) e
gerar um relatório `.md` com log de atualização e instruções para o PETRVS.

---

## FASE 1 — COLETA DO REGISTRO DE EXECUÇÃO

Pergunte ao Coordenador (apenas o que não estiver já informado na mensagem):

1. **ID da Etapa:** Qual o `id_etapa` a ser atualizado? (padrão: `CGOV_XX_YY`)
   - Se o usuário informou apenas o nome da entrega, consulte a Planilha B para
     identificar o `id_etapa` correto antes de prosseguir.
2. **Novo Status:** Qual o novo status?
   - `"Não iniciada"` → `"Em andamento"` → `"Concluída"`
   - (Regressão de status — ex: de "Em andamento" para "Não iniciada" — é permitida
     mas deve ser justificada.)
3. **Data de Início** (se mudança para "Em andamento"): Qual a data de início real?
4. **Data de Conclusão** (obrigatória se status = "Concluída"): Qual a data de término?
5. **Observações:** Há algum registro, link de evidência ou observação a incluir?

**Regra de ouro:** Se o status informado for `"Concluída"` e a data de conclusão NÃO
foi fornecida, **bloqueie imediatamente** e solicite:
> "⛔ Para registrar uma etapa como 'Concluída', a data de término é obrigatória pelo
> padrão de auditoria do PGD. Por favor, informe a data em que a atividade foi
> finalizada (DD/MM/AAAA)."

---

## FASE 2 — CÁLCULO DO NOVO PROGRESSO

⚠️ **Meta pactuada, não contagem de etapas.** O `% Concluído` de uma entrega
mede o cumprimento da **meta pactuada** do ciclo (o que a Planilha A registrou
como alvo da entrega — quantidade, marco de cronograma, ou distribuição de
peso por quadrimestre, ex.: "peso Q1 = 0,33"), não uma simples proporção de
etapas concluídas. As etapas de uma entrega têm esforço e peso desiguais entre
si; contar "concluídas / total" sem distinção mede quantas atividades foram
finalizadas, não quanto da meta pactuada foi entregue — os dois números só
coincidem por coincidência, nunca por definição.

1. **Verifique se a Planilha A registra uma meta pactuada explícita** para o
   ciclo/ano da entrega (campo de meta, marco do cronograma, ou peso por
   quadrimestre Q1/Q2/Q3). Se sim, calcule o `% Concluído` como a fração dessa
   meta efetivamente entregue, considerando a etapa que está sendo registrada
   nesta atualização.
2. **Se não houver meta pactuada explícita disponível** (nem na Planilha A,
   nem informada pelo Coordenador), use a contagem de etapas como
   **aproximação declarada**, nunca como o valor oficial silencioso:
   ```
   % Concluído (aproximado por etapas) =
       (etapas_concluidas_antes + 1) / total_etapas_da_entrega
   ```
   Sinalize no relatório (Seção 1) que esse número é uma aproximação por
   contagem de etapas, na ausência de meta pactuada mais precisa — não o
   apresente como se fosse o percentual apurado contra a meta.
3. Em ambos os casos, registre no relatório qual método foi usado (meta
   pactuada vs. aproximação por contagem de etapas), para que a diferença
   fique auditável e não se confunda esforço com resultado pactuado.

Onde, para o cálculo por etapas (item 2):
- `etapas_concluidas_antes` = número atual de etapas com `status_etapa = "Concluída"`
  na Planilha B para aquela entrega
- `total_etapas_da_entrega` = campo `Etapas` da Planilha A

Se as planilhas não foram fornecidas na sessão atual, pergunte ao Coordenador:
- Qual é a meta pactuada do ciclo atual da entrega (se houver uma definida
  além da simples conclusão de todas as etapas)?
- O número atual de etapas concluídas e o total de etapas previstas — como
  evidência auxiliar, não como o cálculo principal, na ausência de meta
  pactuada informada.

**Transição de status da entrega macro:**

| Condição | status_atual (Planilha A) |
|---|---|
| `% Concluído = 0` e nenhuma etapa "Em andamento" | Não Iniciada |
| `% Concluído > 0` e `< 1` OU há etapa "Em andamento" | Iniciada |
| `% Concluído = 1` (todas as etapas concluídas) | Concluída |

---

## FASE 3 — GERAÇÃO DO RELATÓRIO

Gere um arquivo `.md` e salve em `H:\Meu Drive\CGOV_PGD\` com o nome:
`AAAA.MM.DD_registro_execucao_[id_etapa].md`

Use exatamente o template abaixo:

```
---
# LOG DE REGISTRO DE EXECUÇÃO — CGOV/ICMBio
**Data do Registro:** [data de hoje]
**Registrado por:** Assistente de Gestão da CGOV
**Skill:** cgov-registro-execucao

---

## 1. RESUMO DA ATUALIZAÇÃO

| Campo | Valor anterior | Valor novo |
|---|---|---|
| id_etapa | [CGOV_XX_YY] | — |
| status_etapa | [status anterior] | [novo status] |
| Início da Execução | [anterior ou "—"] | [data de início, se aplicável] |
| Término da Execução | [anterior ou "—"] | [data de conclusão, se aplicável] |
| Observações | [anterior ou "—"] | [novo texto, se fornecido] |

**Resultado para a Entrega Macro ([id_entrega] — [nome_entrega]):**

| Indicador | Antes | Depois |
|---|---|---|
| Etapas concluídas | [N] | [N+1] |
| Total de etapas | [T] | [T] |
| % Concluído | [X%] | [Y%] |
| Método do % Concluído | [Meta pactuada / Aproximação por etapas] | [Meta pactuada / Aproximação por etapas] |
| status_atual | [anterior] | [novo] |

> [💬 Comentário analítico: ex.: "Com esta atualização, a entrega CGOV_09 passa de
> 'Não Iniciada' para 'Iniciada', atingindo 11,1% de progresso. O ritmo está alinhado
> com o Q1 esperado (peso Q1 = 0,33)."]

---

## 2. CHECAGEM DE RISCO

[Preencher com alertas relevantes, se aplicável:]
- 🟡 ATENÇÃO: A entrega tem prazo em [data] e está com [X]% de progresso.
  Progresso esperado para esta data: [Y]%. Diferença: [Z pontos percentuais].
- 🔴 ALERTA: Há [N] etapas com Estimativa Conclusão = [quadrimestre passado] ainda não
  concluídas.
- 🟢 OK: Progresso dentro do esperado para o período.

---

## 3. INSTRUÇÕES PARA ATUALIZAÇÃO NO PETRVS

### Pré-condição
Acesse o PETRVS com seu login institucional e navegue até:
**Gestão → Plano de Entregas → CGOV → [id_entrega: nome_entrega] → Etapas**

### Passo a passo — Atualização da Etapa (Planilha B)

**Passo 1 — Localizar a etapa**
- Localize a etapa `[id_etapa]` na lista de etapas da entrega `[id_entrega]`
- Se o sistema exibir o `id_etapa_antigo`, use o valor `[id_etapa_antigo]` para
  localização

**Passo 2 — Atualizar o status**
- Clique em **"Editar"** ou no ícone de lápis ao lado da etapa
- Altere o campo **"Status"** para: `[novo status]`

**Passo 3 — Registrar datas** (conforme status)
- Se status = "Em andamento":
  → Preencha **"Data de Início":** `[data de início]`
- Se status = "Concluída":
  → Preencha **"Data de Início":** `[data de início, se não preenchida]`
  → Preencha **"Data de Término":** `[data de conclusão]` ⚠️ **OBRIGATÓRIO**

**Passo 4 — Registrar observações**
- No campo **"Observações / Evidências"**: `[texto de observações, se fornecido]`
- Se houver link de documento SEI ou evidência, cole aqui

**Passo 5 — Salvar**
- Clique em **"Salvar"**
- O sistema deve recalcular automaticamente o `% Concluído` da entrega macro
- **Verifique:** O percentual exibido deve ser `[Y%]`
- **Verifique:** O `status_atual` da entrega macro deve exibir `[novo status da entrega]`

### Passo a passo — Atualização manual da Planilha A (se necessário)

Se o PETRVS não atualizar automaticamente os campos da entrega macro, atualize
manualmente a Planilha A:

| Campo | Novo valor |
|---|---|
| % Concluído | [Y como decimal, ex.: 0,111] |
| status_atual | [Não Iniciada / Iniciada / Concluída] |

### Checklist pós-atualização
- [ ] Status da etapa atualizado no PETRVS
- [ ] Data de início registrada (se "Em andamento" ou "Concluída")
- [ ] Data de término registrada (obrigatório se "Concluída")
- [ ] % Concluído da entrega macro atualizado para [Y%]
- [ ] status_atual da entrega macro consistente com o progresso
- [ ] Planilha A e B atualizadas (localmente, se necessário)

---

## 4. PRÓXIMAS ETAPAS RECOMENDADAS

[Listar as próximas etapas da mesma entrega ainda pendentes, em ordem de Estimativa
Conclusão, para orientar o acompanhamento:]

| id_etapa | Fase | Atividade (resumida) | Estimativa | Status atual |
|---|---|---|---|---|
| ... | ... | ... | ... | Não iniciada |

---
*Gerado pelo Assistente de Gestão da CGOV — Skill: cgov-registro-execucao*
*Base normativa: IN MGI nº 24/2023 | PORTARIA ICMBio nº 5.592/2025*
```

---

## NOTAS INTERNAS DA SKILL

- **Múltiplas etapas em lote:** Se o Coordenador informar mais de uma etapa para
  atualizar, processe todas antes de gerar o relatório e consolide em um único log.
  Calcule o `% Concluído` final após todas as atualizações.
- **Sem acesso às planilhas:** Se as planilhas não estiverem disponíveis na sessão,
  solicite apenas os dados mínimos necessários: id_etapa, status anterior e total de
  etapas da entrega. Gere o log com as informações disponíveis e marque o cálculo de
  progresso como "estimado".
- **Checagem de risco:** Sempre compare o `% Concluído` resultante com o progresso
  esperado calculado via Q1/Q2/Q3 da Planilha A. Se não disponível, use a proporção
  do prazo já decorrido como referência.
- **Meta pactuada vs. contagem de etapas (correção de 30/08/2026):** versões
  anteriores desta skill calculavam `% Concluído` sempre como
  "etapas concluídas / total de etapas", tratando esforço (quantidade de
  atividades finalizadas) como se fosse o mesmo que resultado (cumprimento da
  meta pactuada da entrega). Os dois só coincidem quando todas as etapas têm
  peso igual — o que não é garantido. Priorize a meta pactuada da Planilha A;
  use a contagem de etapas apenas como aproximação declarada, nunca em
  silêncio (ver Fase 2).
- **Tom:** Técnico e objetivo. O log deve ser auditável — registre fatos, não
  interpretações subjetivas.

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

**Divergência que permanece aberta (C-01 / RP20 / Q17).** A página do ciclo
publicada pela CGGE informa as faixas como `01/01–31/04`, `01/05–30/07` e
`01/08–31/12` — internamente inconsistentes (31/04 não existe; há lacuna entre
30/07 e 01/08; a terceira faixa tem cinco meses). Para o segundo período a
diferença é material: `01/05–30/07` (CGGE) contra `01/05–31/08` (adotado aqui).
A confirmação formal da CGGE segue pendente — ao usar estes períodos em ato
oficial, confira o recorte.
