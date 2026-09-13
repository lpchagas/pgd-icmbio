# 18 — Decisões de Homologação CGOV (v2.0) e sua implementação

| Campo | Valor |
| --- | --- |
| Deliberação | Coordenação de Governança (CGOV/ICMBio) |
| Data de referência | 13 de setembro de 2026 |
| Objeto | 12 indicadores OCDE/PGD (I01–I12) + análise de gestão `PT_STATUS` |
| Documento de entrada | `docs/17-caderno-metodologico-cgov.md` (matriz D01–D16) |
| Estado após implementação | 13 alvos em `HOMOLOGACAO_INICIAL_PENDENTE`, aguardando a Baseline V2 |

Este documento registra as decisões deliberadas pela CGOV sobre o caderno
metodológico e o que cada uma produziu no código. É o registro auditável a que
a cadeia de precedência do caderno (§1.4) se refere: **decisão CGOV > contratos
executáveis > scripts de produção > fichas > artefatos A3–A5**.

Onde uma decisão não alterou o cálculo, isso está dito explicitamente — uma
confirmação deliberada é tão vinculante quanto uma mudança.

---

## 1. Quadro-resumo

| Decisão | Alvo | Efeito no código | `formula_version` |
| --- | --- | --- | --- |
| D01 | todos os OCDE | Renomeação para o namespace `IND_OCDE_` | inalterada |
| D02 | OCDE, MGI, gestão | Janelas por domínio; MGI anual documentada | inalterada |
| D03 | Eixos 2 e 3 | Separação PE × PT — auditada, já conforme | inalterada |
| D04 | I02 | Carteira ativa — auditada, já conforme | 2.0.0 |
| D05 | I03 | Superexecução sem teto — auditada, já conforme | 2.0.0 |
| D06 | I04 | Média aritmética simples — confirmada | 2.0.0 |
| D07 | I05 | **Nova visão estatística agregada (v2)** | 3.0.0 |
| D08 | I06 | Categorias mantidas; legenda de risco ajustada | 2.0.0 |
| D09 | I07, I08 | **Rateio por dias úteis; coluna renomeada** | 3.0.0 |
| D10 | I08 | **Dupla perspectiva dona × executora** | 3.0.0 |
| D11 | I09 | **Média por Plano de Trabalho** | 3.0.0 |
| D12 | I10, I11 | **Coluna `volume_suficiente`** | 3.0.0 |
| D13 | I12 | Cálculo mantido; uso delimitado a triagem | 2.0.0 |
| D14 | `PT_STATUS` (hoje G01) | **Identificação nominal nos produtos internos** | 3.0.0 |
| D15–D16 | ciclo | Baseline V2 após reexecução na GR2 | — |
| D17 ⏳ | G01 (ex-`PT_STATUS`) | **Namespace `IND_GEST_` e correções de método** | 4.0.0 |

⏳ A D17 foi adotada pelo responsável técnico em 13.09.2026, depois da ata, e
está **pendente de ratificação pela CGOV**. Até lá, o G01 permanece em
`HOMOLOGACAO_INICIAL_PENDENTE`.

Os alvos que subiram para `3.0.0` retornam automaticamente a
`HOMOLOGACAO_INICIAL_PENDENTE`: `lib/validation_runner.py::_baseline_status`
compara a versão declarada com a registrada na baseline. **Nenhum hash foi
editado à mão.**

---

## 2. Decisões que mudaram o cálculo

### D09 — Dias úteis institucionais (I07, propagada ao I08)

Ratear capacidade por dias corridos superestima a força de trabalho disponível
em meses curtos ou com feriados prolongados. O rateio passa a usar dias úteis.

O Denodo/VQL não calcula dias úteis — não há CTE recursiva, `DATEDIFF()`,
`TIMESTAMPDIFF()` nem tabela de calendário. As consultas do I07 e do I08 passam
a devolver **linhas atômicas** por (entrega × plano de trabalho), e a agregação
migrou para Python, em `lib/calendario.py`.

O módulo cobre apenas **feriados nacionais de lei** — fixos (Leis 662/1949,
6.802/1980 e 10.607/2002) e móveis derivados da Páscoa por Meeus/Butcher. Ficam
de fora pontos facultativos, que variam por portaria anual, e feriados
estaduais e municipais, que exigiriam uma tabela por unidade organizacional que
a CGOV não deliberou. Anos fora da janela homologada (2025–2030) falham de
forma explícita, em vez de devolver um número errado em silêncio.

**Efeito verificável.** Um PT de 100 h vigente em todo janeiro/2026, com
sobreposição de 01 a 10/01: janeiro tem 21 dias úteis (22 dias de semana menos
1º de janeiro) e o intervalo tem 6 → 100 × 6/21 = **28,57 h**. Sob dias
corridos seriam 10/31 = 32,26 h — uma superestimativa de 13%.

A coluna `num_servidores_alocados` foi renomeada para
**`num_planos_trabalho_alocados`**: a contagem sempre foi de planos de
trabalho, e um servidor com dois PTs vinculados à mesma entrega era contado
duas vezes sob o nome antigo.

### D10 — Dupla perspectiva de capacidade (I08)

Quando servidores de áreas diferentes colaboram na mesma entrega, dividir horas
de uma unidade pela capacidade de outra produz um número sem significado. O
indicador passa a emitir duas visões, cada uma com numerador e denominador da
**mesma** unidade:

| Visão | Arquivo | Pergunta que responde |
| --- | --- | --- |
| Dona do PE | `IND_OCDE_08.2_v1_*` | Quanto as entregas que esta unidade planejou consomem do tamanho dela |
| Executora do PT | `IND_OCDE_08.2_v2_*` | Quanto da capacidade desta unidade está comprometido com cada entrega |

A v1 preserva os nomes de coluna históricos (`horas_planejadas_entrega`,
`total_horas_disponiveis_unidade`, `proporcao_horas_perc`) para não quebrar os
painéis da COCAGE. A v2 traz `horas_executora`, `capacidade_executora` e
`proporcao_executora_perc`.

O denominador vem de consulta própria (`SQL_I08_CAPACIDADE`), porque a
capacidade da unidade inclui PTs sem entrega vinculada, que não aparecem no
universo de vínculos.

### D11 — Média por Plano de Trabalho (I09)

A média da unidade era tirada sobre os eventos de avaliação, de modo que um
plano longo com muitas consolidações mensais pesava mais do que um plano curto.
A métrica primária passa a ser a **média das médias por plano** — cada plano
com peso 1.

`media_nota_pt` é agora a média das médias. A fórmula anterior continua
exportada em **`media_nota_pt_eventos`**, para que a COCAGE compare as duas
leituras durante a transição.

`nota_minima`, `nota_maxima` e `qtd_nota_1`…`qtd_nota_5` seguem sobre o
universo de eventos: são distribuições, não médias, e convertê-las esconderia a
dispersão real dentro da unidade.

### D07 — Distribuição estatística (I05)

A média sozinha esconde concentração: uma unidade em que um servidor carrega
vinte entregas e cinco não carregam nenhuma tem a mesma média de outra em que
todos carregam quatro. O indicador passa a emitir duas visões:

- `IND_OCDE_05.2_v1_*` — visão nominal por servidor, **produto restrito**;
- `IND_OCDE_05.2_v2_*` — visão estatística por unidade, **sem identificação**:
  `total_servidores`, `media_entregas_por_servidor`,
  `mediana_entregas_por_servidor`, `p25_entregas_por_servidor`,
  `p75_entregas_por_servidor` e `pct_servidores_sem_entrega`.

Os quantis usam interpolação linear (método padrão do pandas). Nenhum CPF é
exportado em qualquer das visões.

### D12 — Volumetria como limitador (I10, I11)

O cálculo permanece sobre a categoria bruta (`sequencia = 4` no I10,
`sequencia = 1` no I11), sem ponderação. Acrescenta-se a coluna
**`volume_suficiente`** — 1 quando a unidade tem ao menos 5 avaliações no
período, 0 abaixo disso. **Nenhuma linha é suprimida**: cabe ao BI da COCAGE
ocultar ou cinzentar as unidades de amostra pequena, em que um único caso
desloca o percentual dezenas de pontos.

### D14 — Identificação nominal no `PT_STATUS`

O `PT_STATUS` é ferramenta tática da chefia, não um indicador. Dizer a um gestor
que ele tem "3 servidores aguardando assinatura" não permite agir; o nome
permite. A exposição está amparada na finalidade de execução das rotinas
ordinárias do serviço público e limitada aos produtos de uso interno:

| Produto | Detalhe nominal | Circulação |
| --- | --- | --- |
| `operacional` | sim | uso imediato da chefia |
| `restrito` | sim | interno da unidade |
| `compartilhavel` | **não** — painel agregado, supressão k≥5 | único que sai da unidade |

Coleta-se o mínimo necessário: `id_servidor` e `servidor_nome`. O
`servidor_email`, que a consulta selecionava sem uso definido, foi **retirado**;
CPF e matrícula nunca foram lidos. O gate de PII do A2 continua incidindo sobre
o produto `compartilhavel`, e o contrato de validação do `PT_STATUS` declara
apenas a visão `painel`.

### D01 — Namespace `IND_OCDE_`

Os catálogos OCDE e MGI passam a ser separados por prefixo de arquivo, para que
indicadores com propósitos, naturezas e recortes temporais distintos não
colidam nos painéis executivos:

| Família | Prefixo | Pasta |
| --- | --- | --- |
| Piloto OCDE/PGD | `IND_OCDE_XX` | `ocde/indicadores/` |
| Governamentais MGI | `IND_MGI_XX` | `mgi/indicadores/` |

O código lógico do alvo (`I01`…`I12`) **não** carrega o namespace — ele
identifica o indicador, não o arquivo. O prefixo tem fonte única em
`lib/validation_contracts.py`.

Os pontos de **leitura** (relatórios V2, drivers de gráficos e de conferência
de extração) aceitam as duas gerações de nome, para que as entregas de
2025-07 a 2026-08 já gravadas continuem carregando. A escrita emite apenas o
nome novo.

---

## 3. Decisões confirmadas sem alteração de código

Cada uma foi auditada contra a implementação vigente antes de ser registrada
como confirmada.

| Decisão | O que foi verificado |
| --- | --- |
| **D03** — separação PE × PT | Eixo 2 agrupa por `planos_entregas.unidade_id`; Eixo 3, por `planos_trabalhos.unidade_id`. O I07 e o I08 atribuem a entrega à unidade dona do PE, com fallback para a do PT. A D10 torna as duas perspectivas explícitas no I08. |
| **D04** — carteira ativa (I02) | O denominador da `taxa_cumprimento_perc` já era a sobreposição ao ciclo (`total_no_ciclo`); as entregas que vencem no período já constavam como métrica secundária (`total_vence_no_periodo`, `proporcao_vence_no_periodo_perc`). |
| **D05** — superexecução (I03) | Nenhum `min(taxa, 100)` na produção nem no oracle; o status `Superexecutada` já existia; `meta_json` e `realizado_json` já eram exportados e sanitizados por `clean()`, que troca quebras de linha por ` / ` sem romper o delimitador pipe. |
| **D06** — ponderação (I04) | Média aritmética simples confirmada; matriz de pesos formalmente fora do escopo. |
| **D08** — limiares (I06) | Categorias 1/2/3/4+ mantidas. Muda a **leitura**: "1 servidor" indica risco de descontinuidade, **não infração**. As legendas do BI devem dizer isso. |
| **D13** — coerência (I12) | `abs(media_PT − media_PE)` e `media_PT − media_PE` mantidos, com os volumes exportados. O indicador é **triagem**, não julgamento da unidade. |

### D02 — Janelas por domínio

| Domínio | Janela | Onde |
| --- | --- | --- |
| OCDE | cumulativa de 01/07/2025 ao último dia do mês anterior | `lib.periodos.analysis_window()` |
| MGI | anual, 1º de janeiro a 31 de dezembro do ano de referência | documentada em `mgi/README.md` (sem scripts ainda) |
| Gestão (`PT_STATUS`) | data de execução do dia, sem defasagem mensal | auditado: `window.data_execucao`, não `window.fim` |

---

## 4. Efeito sobre a série histórica

As mudanças de D07, D09, D10, D11 e D12 alteram valores. **Séries anteriores a
13.09.2026 não são comparáveis às novas sem reprocessamento.**

O comparativo abaixo foi medido em 13.09.2026, reexecutando os indicadores
contra a base real (janela 01/07/2025–31/08/2026) e confrontando linha a linha
com a última extração da fórmula anterior.

### I07 — efeito dos dias úteis

| Medida | Resultado |
| --- | --- |
| Linhas | 13.286 → 13.286 (nenhuma entrega entra ou sai) |
| Total de horas planejadas | 96.479 h → 96.507 h (**+0,03%**) |
| Variação média por entrega | +0,07% |
| Entregas com variação acima de 5% | 76 |

O agregado nacional praticamente não se move, mas entregas individuais sim, nos
dois sentidos — é exatamente a distorção que a D09 corrige. Casos extremos:
`CT-MANAUS` em Q2-2026 vai de 46,4 h para 78,4 h (+69%), enquanto entregas cuja
sobreposição com o período cai inteiramente em fins de semana ou feriados vão a
zero (por exemplo `RESEXPIRAJUBAE` em T3-2025, de 8,0 h para 0 h). Zero horas
para uma sobreposição sem nenhum dia útil é o resultado correto sob a D09, e
deve ser lido como sinal de PT com vigência mal posicionada, não como erro de
extração.

### I09 — efeito da média por plano

| Medida | Resultado |
| --- | --- |
| Linhas | 839 → 839 |
| Média nacional | 3,931 → 3,931 (estável) |
| Unidades sem alteração prática (< 0,005) | 721 de 839 (**85%**) |
| Maior deslocamento por unidade | ±0,34 |
| Unidades que mudam de faixa de desempenho | 10 |

A média nacional não se move porque o efeito é redistributivo: unidades com
planos longos e muitas consolidações perdem peso, e unidades com planos curtos
ganham. As dez mudanças de faixa são o que a CGOV precisa examinar — por
exemplo `NGIPALMAS` em T4-2025 sobe de 4,42 (Alto desempenho) para 4,67
(Excepcional), e `NGISUDOEBAIANO` cai de 4,67 (Excepcional) para 4,33 (Alto
desempenho).

A coluna `media_nota_pt_eventos` reproduz a fórmula anterior em **839 de 839**
unidades-período, o que confirma que a mudança é de método e não de universo.

### I08 — efeito da dupla perspectiva

A visão executora tem mais linhas que a visão dona em todos os períodos (por
exemplo 3.426 contra 3.156 em T3-2025): a diferença é exatamente a colaboração
entre unidades, que a fórmula anterior comprimia numa única linha com
denominador incompatível. As entregas com proporção acima de 100% — sinal de
`forca_trabalho` inválida no PETRVS — caíram de 19 para 6.

### G01 — efeito da D17

Painel nacional de planos, fotografia de 13.09.2026, mesmo universo padrão:

| Status de negócio | 3.0.0 | 4.0.0 | Causa |
| --- | ---: | ---: | --- |
| Em execução | 1.288 | 1.287 | F3: um plano contado duas vezes |
| Aguardando avaliação | 606 | **613** | F1: +7 planos concluídos com período pendente |
| Aguardando assinatura | 490 | 490 | — |
| Rascunho | 297 | 297 | — |
| Suspenso | 3 | 3 | — |
| **Total** | 2.684 linhas / 2.683 planos | **2.690 planos** | |

## 5. D17 — Família de gestão: namespace `IND_GEST_` e correções do G01

**Estado:** adotada pelo responsável técnico em 13.09.2026; pendente de
ratificação CGOV. `formula_version` do G01: 3.0.0 → **4.0.0**.

### Namespace

Mesmo modelo do D01. O `PT_STATUS` passa a ser o indicador **G01 — Situação dos
Planos de Trabalho**, em `gestao/IND_GEST_01/IND_GEST_01.1_run.py`, com
artefatos `IND_GEST_01.{2,3,4,5}_*`. A CLI continua aceitando `PT_STATUS` e
`IND_GEST_01` como alias de `G01`. A skill `status-pt` mantém o nome.
Convenção completa em `gestao/README.md`.

### Correções de método

Cada achado foi medido no Denodo, somente leitura, antes da correção, na
fotografia de 13.09.2026.

| # | Achado | Medição | Decisão |
| --- | --- | --- | --- |
| F1 | O filtro padrão excluía planos `CONCLUIDO` com período entregue e não avaliado, e o encerramento automático por data os tirava da fila da chefia | 7 planos em 6 unidades | **Corrigido** no A1 e no oracle: o universo padrão inclui esses planos |
| F2 | Risco de a trilha datar o plano com transições de consolidação | 0 de 143.548 linhas de trilha de PT referenciam consolidação, PE ou atividade | Sem mudança; risco registrado |
| F3 | O join do responsável por `created_at = MAX` duplicava o plano quando havia empate | 140 empates na trilha; 1 plano duplicado no painel padrão, 37 na base inteira | **Corrigido**: responsável agregado por (plano, código, data); A1 aborta se houver plano duplicado; invariante `uma_linha_por_plano` |
| F4 | O autor da transição não filtra `deleted_at` | — | **Exceção declarada** à regra de soft-delete: autoria histórica é fato de auditoria |
| F5 | O extrator do oracle usava LEFT JOIN com `N.I.`; o A1 exige unidade e servidor ativos | 0 planos abertos órfãos | **Alinhado** ao universo do A1 (preventivo) |
| F6 | A documentação dizia "Concluído = todas as consolidações AVALIADO"; o código não exige isso | 16 planos concluídos com período `INCLUIDO` | Vale o código; documentação corrigida |
| F7 | Com `--data-execucao` retroativa, `dias_no_status_atual` podia ficar negativo; carimbo de hora sem fuso | — | **Corrigido**: dias vazio quando a data é posterior à fotografia; carimbo em `America/Sao_Paulo` |
| F9 | Plano `SUSPENSO` com período pendente continua "Suspenso" | 0 planos | Regra confirmada |
| F10 | `--incluir-subordinadas` cortava em 3 níveis sem aviso | 5 unidades no 4º nível abaixo de DIPLAN | **Corrigido**: aviso explícito e parâmetro `--niveis` |
| F11 | O painel compartilhável suprimia só a célula k<5; uma célula oculta isolada é dedutível por qualquer total da unidade | — | **Corrigido**: supressão complementar por unidade (`ocde.relatorios.privacidade`) |

### Correção no runner de validação

Na família de gestão, o A2 era escolhido pelo arquivo mais recente, sem olhar
o produto. Validar `restrito` logo depois de gerar o `compartilhavel` comparava
o oracle com células suprimidas e resultava em `FALHA_TECNICA` falsa. O A2
passa a ser buscado pelo produto solicitado (`ambos` usa o restrito), e uma
célula `SUPRIMIDO_K` deixa de contar como divergência.

**Verificação:** `python -m lib.validation_runner --familia gestao --alvo G01
--modo integrado --regional GR2` resulta em `HOMOLOGACAO_INICIAL_PENDENTE`, sem
achado bloqueante, nos produtos `restrito` e `compartilhavel`.

## 6. Próximos passos (D15–D17)

1. Reexecutar o ciclo integrado na GR2 e conferir que os 13 alvos ficam em
   `HOMOLOGACAO_INICIAL_PENDENTE`, e não em `FALHA_TECNICA`.
2. Submeter à CGOV os A5 com os deltas da seção 4 e a ratificação da D17 (seção 5).
3. Registrar a aprovação com `python -m tools.approve_validation_baseline`,
   sem editar hashes manualmente.
4. Reexecutar: sem mudanças e sem divergências, o estado esperado passa a ser
   `CERTIFICADO_AUTOMATICAMENTE`.
5. Só então liberar a expansão nacional.
