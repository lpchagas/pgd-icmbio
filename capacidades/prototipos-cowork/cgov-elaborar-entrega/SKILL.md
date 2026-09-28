---
name: cgov-elaborar-entrega
description: >
  Use this skill whenever the Coordenador de Governança (CGOV/ICMBio) needs to create a
  new entrega for the Plano de Entregas. Triggers include: /elaborar_plano_entrega,
  "criar nova entrega", "elaborar entrega", "incluir entrega no plano", "nova entrega
  para o PGD", "entrega nova", "cadastrar entrega", "preciso criar uma entrega",
  "quero adicionar uma entrega". Always use this skill when a new macro-level delivery
  needs to be structured for PETRVS registration — even if the user just describes the
  work informally without using the exact trigger phrase.
---

# SKILL: Elaborar Nova Entrega — CGOV/ICMBio

Você está no modo **Elaborar Nova Entrega**. Suspenda a conversação genérica e execute
estritamente as fases abaixo. O objetivo é estruturar uma nova entrega no formato
compatível com a Planilha A do PETRVS e gerar um relatório `.md` pronto para cadastro.

---

## FASE 1 — COLETA DE INFORMAÇÕES (4Q1P)

Faça ao Coordenador as perguntas abaixo **uma de cada vez**, na ordem apresentada.
Só avance para a próxima quando tiver a resposta confirmada. Se o usuário já forneceu
alguma informação espontaneamente, não repita a pergunta — apenas confirme.

1. **O QUÊ:** Descreva brevemente o que será entregue (produto ou serviço?).
2. **QUANTO / COMO MEDIR:** Como saberemos que esta entrega foi concluída? Existe uma
   forma de calcular o progresso em etapas?
3. **QUANDO:** Qual é a data-limite para a conclusão desta entrega?
4. **QUEM PEDIU (Demandante):** Esta demanda veio da CGGE, da Presidência ou de outra
   instância?
5. **PARA QUEM (Destinatário):** O resultado beneficia o ICMBio como um todo, o Comitê
   Gestor, o MGI ou os servidores?
6. **PROCESSO:** Esta entrega se encaixa em qual macroprocesso?
   - Governança de Processos
   - Gestão de Riscos
   - Gestão da Integridade
7. **OBJETIVO ESTRATÉGICO:** Qual dos objetivos abaixo melhor descreve esta entrega?
   - `IV-b` — aprimorar a estrutura organizacional e a gestão por processos
   - `IV-e` — elaborar e aperfeiçoar instrumentos normativos
   - `IV-h` — fortalecer a governança e a coordenação interinstitucional
   - `IV-j` — incrementar e estruturar a força de trabalho
8. **RESPONSÁVEIS:** Quais servidores da equipe participarão?
   (Opções: os servidores da equipe, identificados como na planilha — Servidor 1 a Servidor 5)
9. **DISTRIBUIÇÃO QUADRIMESTRAL (Q1/Q2/Q3):** Como o esforço se distribui ao longo do ano?
   Informe os pesos percentuais para cada quadrimestre — eles devem somar 100%.
   Ex.: Q1=20%, Q2=50%, Q3=30%.
   ⚠️ Desde 2026 o Plano de Entregas do ICMBio é **quadrimestral**: são três
   períodos de quatro meses — Q1 = 01/01 a 30/04, Q2 = 01/05 a 31/08 e
   Q3 = 01/09 a 31/12. **Não existe Q4.** Os pesos somam 100% entre os três.

---

## FASE 2 — VALIDAÇÃO DE REGRAS DO PGD

Antes de gerar o output, aplique obrigatoriamente estas verificações:

**Regra 1 — Prazo máximo:** Se a data-limite fornecida ultrapassar 12 meses a partir
de hoje, alerte o Coordenador:
> "⚠️ O prazo informado excede 1 ano (limite máximo de uma entrega no PGD/IN MGI nº
> 24/2023). Recomendo fatiar este projeto em entregas menores com prazos intermediários.
> Deseja que eu ajude a dividir?"

**Regra 2 — Nome da entrega:** Formate o `nome_entrega` obrigatoriamente no padrão
`Substantivo(s) + Verbo no Particípio`. Exemplos corretos:
- ✅ "Cadeia de Valor do ICMBio revisada"
- ✅ "Trilha formativa em Gestão por Processos elaborada"
- ❌ "Elaborar Trilha Formativa" (verbo no infinitivo — não usar)

**Regra 3 — Soma dos pesos quadrimestrais:** Q1 + Q2 + Q3 deve ser ≤ 1,0 (ou ≤ 100%).
Como não há Q4, a soma dos três é o ano inteiro: se somar menos que 1, confirme
com o Coordenador se a diferença é intencional.
Se somar mais que 1, solicite correção ao Coordenador.

**Regra 4 — ID da entrega:** O próximo `id_entrega` deve seguir a sequência dos IDs
já existentes. Se a Planilha A foi fornecida, identifique o maior ID atual (ex.:
`CGOV_42`) e sugira o próximo (`CGOV_43`). Se não foi fornecida, use `CGOV_[PRÓXIMO]`
como placeholder.

---

## FASE 3 — GERAÇÃO DO RELATÓRIO

Após coletar e validar todas as informações, gere um arquivo `.md` e salve-o em
`H:\Meu Drive\CGOV_PGD\` com o nome:
`AAAA.MM.DD_nova_entrega_[SIGLA].md`

Use exatamente o template abaixo:

```
---
# RELATÓRIO: NOVA ENTREGA CGOV
**Data de Elaboração:** [data de hoje]
**Elaborado por:** Assistente de Gestão da CGOV
**Skill:** cgov-elaborar-entrega

---

## 1. DADOS DA ENTREGA (Planilha A — compatível com PETRVS)

| Campo | Valor |
|---|---|
| id_entrega | [CGOV_XX] |
| Unidade Executora | CGOV |
| Processo | [valor] |
| Perspectiva do Mapa Estratégico | IV - Processos gerenciais e de suporte. |
| Objetivo Estratégico | [IV-b/e/h/j — texto completo] |
| ciclo | [Planejamento / Execução] |
| Entregas (nome) | [Substantivo + Verbo no Particípio] |
| Descrição da entrega | [3 a 5 parágrafos: contexto, metodologia, produto esperado] |
| Etiquetas | [Produto / Serviço] |
| Prazo | [DD/MM/AAAA] |
| Q1 | [0,XX] |
| Q2 | [0,XX] |
| Q3 | [0,XX] |
| Meta | 1 |
| Descrição da meta | (nº etapas concluídas / nº etapas previstas) × 100 |
| status_atual | Não Iniciada |
| % Concluído | 0 |
| Etapas | [a preencher após desdobramento] |
| Demandante | [valor] |
| Destinatário | [valor] |
| Servidor 1 | [0/1] |
| Servidor 2 | [0/1] |
| Servidor 3 | [0/1] |
| Servidor 4 | [0/1] |
| Servidor 5 | [0/1] |

---

## 2. DESDOBRAMENTO EM ETAPAS SUGERIDO (Planilha B — compatível com PETRVS)

> Sugestão de etapas para o campo `tb_etapa_trabalho`. Ajuste conforme necessidade.

| id_etapa | Fase | Atividade | Estimativa Conclusão | status_etapa |
|---|---|---|---|---|
| [CGOV_XX_01] | Fase 1: [nome da fase] | [descrição da atividade] | [Q1/Q2/Q3] | Não iniciada |
| [CGOV_XX_02] | Fase 1: [nome da fase] | [descrição da atividade] | [Q1/Q2/Q3] | Não iniciada |
| ... | ... | ... | ... | Não iniciada |

**Total de etapas sugeridas:** [N]

---

## 3. INSTRUÇÕES PARA CADASTRO NO PETRVS

### Pré-condição
Acesse o PETRVS com seu login institucional (gov.br) e navegue até:
**Gestão → Plano de Entregas → [Sua Unidade: CGOV] → Nova Entrega**

### Passo a passo — Cadastro da Entrega Macro (Planilha A)

**Passo 1 — Identificação**
- Preencha o campo **"Nome da Entrega"** com: `[nome_entrega gerado acima]`
- Selecione **Macroprocesso/Processo:** `[valor do campo Processo]`
- Selecione **Tipo:** `[Produto / Serviço]`

**Passo 2 — Alinhamento Estratégico**
- Selecione **Perspectiva:** `IV - Processos gerenciais e de suporte.`
- Selecione **Objetivo Estratégico:** `[IV-b/e/h/j]`

**Passo 3 — Descrição e Prazo**
- Cole no campo **"Descrição da Entrega"** o texto gerado na Seção 1 acima
- Informe a **Data-Limite:** `[Prazo]`
- Informe o **Demandante:** `[valor]`
- Informe o **Destinatário:** `[valor]`

**Passo 4 — Distribuição Quadrimestral**
- Campo **Q1:** `[valor]`
- Campo **Q2:** `[valor]`
- Campo **Q3:** `[valor]`
- ⚠️ Não há campo Q4: os três quadrimestres cobrem o ano inteiro. Se o PETRVS
  exibir um quarto campo, confirme com a CGGE antes de preencher.

**Passo 5 — Responsáveis**
Adicione os servidores responsáveis vinculando os planos de trabalho:
[lista dos servidores com flag = 1]

**Passo 6 — Salvar e publicar**
- Clique em **"Salvar Rascunho"** para revisão interna
- Após aprovação, clique em **"Publicar"** para tornar a entrega visível aos servidores
- Anote o **id_entrega** gerado pelo sistema e atualize a Planilha A

### Passo a passo — Cadastro das Etapas (Planilha B)

Para cada linha da Seção 2 acima, dentro da entrega recém-criada:
1. Acesse **"Desdobrar em Etapas"** ou **"Plano de Trabalho"**
2. Clique em **"+ Nova Etapa"**
3. Preencha:
   - **Fase:** `[fase_etapa]`
   - **Atividade:** `[atividade_etapa]`
   - **Estimativa de Conclusão:** `[Q1/Q2/Q3]`
   - **Status:** `Não iniciada`
4. Repita para todas as [N] etapas
5. Ao final, confirme que o campo **"Etapas"** na entrega macro exibe `[N]`

### Checklist de qualidade pós-cadastro
- [ ] Nome da entrega no padrão "Substantivo + Verbo no Particípio"
- [ ] Q1 + Q2 + Q3 ≤ 1,0 (ou o equivalente percentual no sistema)
- [ ] Prazo ≤ 12 meses a partir de hoje
- [ ] Pelo menos 1 servidor responsável vinculado
- [ ] Número de etapas cadastradas = valor do campo "Etapas" na Planilha A
- [ ] Status inicial = "Não Iniciada" / % Concluído = 0

---

## 4. OBSERVAÇÕES E RESSALVAS

[Incluir aqui qualquer alerta gerado na Fase 2, como prazo excedente ou ajuste de pesos quadrimestrais]

---
*Gerado pelo Assistente de Gestão da CGOV — Skill: cgov-elaborar-entrega*
*Base normativa: IN MGI nº 24/2023 | PORTARIA ICMBio nº 5.592/2025*
```

---

## NOTAS INTERNAS DA SKILL

- **Ciclo padrão:** Novas entregas iniciam no ciclo `"Planejamento"`. Se o Coordenador
  indicar que a entrega já está em andamento, use `"Execução"`.
- **Descrição da entrega:** Escreva 3 a 5 parágrafos no padrão das descrições existentes
  na Planilha A: (1) contextualização, (2) metodologia/processo, (3) produto esperado e
  impacto. Use linguagem gerencial e institucional.
- **Etapas sugeridas:** Organize sempre em Fases (mínimo 3, máximo 5). Cada fase deve
  ter de 2 a 5 atividades. A última fase deve sempre envolver comunicação/disseminação
  do resultado. Use como referência o padrão das etapas existentes na Planilha B.
- **Tom:** Profissional, técnico, compatível com o serviço público federal.

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
