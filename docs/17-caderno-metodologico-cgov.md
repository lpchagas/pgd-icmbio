# Caderno Metodológico para Deliberação da CGOV

## Indicadores gerenciais do PGD, execução dos Planos de Entregas e situação dos Planos de Trabalho

| Campo | Registro |
|---|---|
| Versão | 2.0 — deliberado pela CGOV em 13/09/2026 |
| Data de referência | 13/09/2026 |
| Unidade deliberativa | Coordenação de Governança — CGOV/ICMBio |
| Escopo da evidência integrada | Gerência Regional Nordeste — GR2 |
| Janela acumulada | 01/07/2025 a 31/08/2026 |
| Lente operacional de PT | fotografia datada, separada da janela acumulada |
| Execução de referência | validação integrada datada de 13/09/2026; identificador preservado no manifesto privado |
| Estado | 13 alvos em `HOMOLOGACAO_INICIAL_PENDENTE` |
| Natureza | proposta técnica independente, já submetida e deliberada |
| Deliberação | D01–D16 decididas; registro e efeitos em [`18-decisoes-homologacao-cgov-v2.md`](18-decisoes-homologacao-cgov-v2.md) |

## Resumo para decisão

> **Situação em 13/09/2026.** A CGOV deliberou sobre a matriz D01–D16 deste
> caderno. As decisões e o que cada uma produziu no código estão em
> [`18-decisoes-homologacao-cgov-v2.md`](18-decisoes-homologacao-cgov-v2.md).
> D07, D09, D10, D11, D12 e D14 alteraram fórmulas ou schema e elevaram a
> `formula_version` dos alvos afetados para 3.0.0, o que os devolve a
> `HOMOLOGACAO_INICIAL_PENDENTE`; D03, D04, D05, D06, D08 e D13 foram
> auditadas e confirmadas sem alteração de código. A Baseline V2 depende da
> reexecução integrada na GR2 (D15/D16) e do comparativo de séries do I07 e
> do I09, cujos valores mudaram e não são retrocompatíveis.

Este caderno consolida, em linguagem de negócio e com rastreabilidade técnica, as
definições metodológicas implementadas para os doze indicadores do projeto
OCDE/PGD e para a análise `PT_STATUS`. Seu propósito é permitir que a CGOV delibere
sobre **o que cada medida significa**, **como é calculada**, **qual unidade recebe
o resultado**, **quais limitações condicionam seu uso** e **quais mudanças obrigam
nova homologação**.

A validação automatizada da GR2 confrontou produção e oracles independentes em
Python. Não houve divergência numérica bloqueante. Foram observados alertas não
bloqueantes de duplicidade atômica em I01 (4 ocorrências) e I05/I06 (16 em cada),
tratados pelas regras de deduplicação. Isso comprova a reprodutibilidade da fórmula
observada, não a aprovação da escolha de negócio. Por isso, os 13 alvos continuam
pendentes de homologação inicial.

Há uma questão prévia de governança documental. O repositório identifica I01–I12
como indicadores do piloto OCDE/PGD. Um catálogo referencial interno consultado pela equipe usa os mesmos códigos para conceitos diferentes. A homonímia
não altera os cálculos, mas cria risco de comunicação. Recomenda-se confirmar a
fonte oficial e, até lá, usar `OCDE-PGD/ICMBio-IXX`.

Decisões centrais:

1. confirmar taxonomia e fonte documental dos códigos I01–I12;
2. aprovar a separação entre resultado do PE e atividade/capacidade do PT;
3. aprovar a janela acumulada fixa a partir de 01/07/2025;
4. decidir unidade de atribuição e denominador do I08;
5. reconhecer I07 como estimativa de capacidade em dias corridos;
6. aprovar a granularidade por evento de I09–I12 ou visão complementar por plano;
7. declarar semáforos como triagem, não norma ou decisão automática sobre pessoas;
8. aprovar a versão metodológica e fingerprints como baseline.

---

## 1. Objeto e escopo da deliberação

### 1.1 Objeto da homologação

| Camada | Pergunta | Efeito |
|---|---|---|
| Conceitual | Responde a uma pergunta gerencial relevante? | autoriza o uso e fixa limites |
| Semântica | Numerador, denominador, universo, período e unidade estão corretos? | fixa a fórmula de negócio |
| Técnica | A implementação reproduz a fórmula e é auditável? | aprova a baseline A1–A5 |
| Comunicacional | Nome, faixas e recomendações são adequados? | define apresentação e interpretação |

Aprovação técnica sem aprovação semântica apenas confirma que o software calcula
consistentemente uma fórmula ainda não homologada. Decisão conceitual sem atualizar
o contrato executável, por sua vez, não autoriza a produção.

### 1.2 Portfólio submetido

| Domínio | Alvos | Objeto principal | Unidade predominante |
|---|---|---|---|
| Modalidade | I01 | distribuição por modalidade | servidor × ciclo × unidade executora |
| Resultado do PE | I02–I04 | cumprimento de entregas e metas | entrega/PE × ciclo × unidade dona |
| Capacidade do PT | I05–I08 | distribuição, composição e horas planejadas | vínculo PT–entrega × ciclo |
| Avaliação | I09–I12 | avaliação de PT/PE e coerência | evento × unidade × ciclo |
| Operacional | PT_STATUS | estado de PT e consolidações | PT/consolidação × unidade executora |

### 1.3 Separação obrigatória entre PE e PT

O PE contém o compromisso organizacional de resultado. O PT organiza a
participação e a capacidade de trabalho. Consequentemente:

- I02–I04 medem resultado ou alcance de metas do PE;
- I05–I08 medem distribuição e capacidade planejada no PT;
- I09–I11 descrevem avaliação do PT;
- I12 compara avaliações agregadas de PT e PE;
- `PT_STATUS` mostra fluxo operacional, e não desempenho final;
- conclusão de atividade ou PT não pode substituir a meta própria da entrega do PE.

> **Analogia prática:** o PE é o destino contratado; o PT descreve como a equipe
> organizou a viagem. Horas de direção e número de motoristas ajudam a gerir o
> percurso, mas não provam que o destino foi alcançado.

### 1.4 Fontes de verdade e precedência

1. decisão formal da CGOV neste caderno ou ato associado — a deliberação
   vigente é a de 13/09/2026, registrada em
   [`18-decisoes-homologacao-cgov-v2.md`](18-decisoes-homologacao-cgov-v2.md);
2. contrato executável em `lib/validation_contracts.py`;
3. scripts de produção em `ocde/indicadores/` e `gestao/`;
4. fichas em `docs/ocde/` e documentação de gestão;
5. A3, A4 e A5 da execução de referência;
6. documentos históricos, apenas para contexto.

Após a homologação, divergência entre as camadas 1–4 bloqueia a recertificação.

### 1.5 Questão de taxonomia

O projeto associa os códigos aos conceitos deste caderno e os documenta como
componentes do *Performance Toolkit* do piloto OCDE/MGI/ICMBio. Um catálogo referencial interno, porém, usa I01–I12 para outro conjunto, com alinhamento estratégico,
macroprocessos, satisfação, despesas, atratividade e saúde. Há homonímia documental.

Proposta:

- manter o código técnico para preservar séries, scripts e artefatos;
- adotar `OCDE-PGD/ICMBio-IXX` em apresentações;
- anexar à decisão a fonte primária que vincula código e conceito;
- se a fonte primária confirmar catálogo diferente, migrar para `IG01–IG12`, com
  aliases legados e tabela de correspondência;
- não afirmar caráter “oficial OCDE” fora do piloto sem proveniência confirmada.

### 1.6 Evidência disponível

| Evidência | Situação em 13/09/2026 |
|---|---|
| Extração I01–I12 | ciclo nacional concluído; corte em 31/08/2026 |
| Validação integrada GR2 | 13 alvos executados por produção e oracle |
| Comparação A1 × A3 | sem divergência acima das tolerâncias |
| A4 e A5 | gerados para todos os alvos |
| Privacidade | sem nomes, CPF, e-mail ou telefone nos produtos de validação |
| Aprovação de negócio | pendente para os 13 alvos |

---

## 2. Fundamentação metodológica

### 2.1 Regra temporal comum

Toda edição acumulada usa `analysis_window()`:

```text
inicio = 01/07/2025
fim    = último dia do mês anterior à data de execução
```

Em setembro/2026: `01/07/2025–31/08/2026`. O mês corrente é excluído. A data de
execução é injetada no fuso `America/Sao_Paulo`; nenhum alvo usa `date.today()`.

PE são trimestrais em 2025 e quadrimestrais em 2026. PT são trimestrais em 2025 e
mensais em 2026. Ciclos posteriores ao corte são excluídos; sobrepostos são
truncados e marcados parciais. Avaliações entram pela data do evento. Correções
retroativas são aceitas quando o fato pertence à janela e ficam vinculadas à data
da extração.

### 2.2 Regra organizacional

A hierarquia é derivada de IDs e `id_mae`, com apoio do dicionário
PETRVS/Digiteca e `ICMBIO_estrutura.csv`. Sigla ou nome isolado não define
subordinação.

“Unidade dona do PE” e “unidade executora do PT” são dimensões distintas. A
primeira responde pelo compromisso; a segunda, pela capacidade. Medida que combine
as duas deve declarar a perspectiva e manter numerador e denominador coerentes.

### 2.3 Regras gerais de qualidade

- considerar registros ativos (`deleted_at IS NULL`), salvo exceção homologada;
- deduplicar pela chave de negócio, não pela linha física;
- excluir denominador zero e divulgar a perda de cobertura;
- manter nulos explícitos, sem imputação silenciosa;
- preservar superexecução quando a fórmula admite mais de 100%;
- não equiparar status formal a progresso numérico;
- distinguir ciclo completo, parcial e fora do corte;
- separar fato, inferência e recomendação;
- acompanhar semáforos de cobertura, volume e limitação.

### 2.4 Proteção de dados

A proteção LGPD concentra-se em dados pessoais. Nomes, CPF, endereços, telefones,
e-mails e identificadores pessoais não integram o relatório. IDs são usados em
memória para deduplicação e, quando indispensáveis à reprodução privada,
transformados em chave técnica/HMAC. Textos podem ser analisados após sanitização.

Unidades, entregas, metas, prazos, problemas e riscos podem ser nominados, pois são
objetos de gestão, desde que a combinação não revele pessoa natural. Produtos
compartilháveis aplicam `k ≥ 5` e supressão complementar a métricas de pessoas. O
produto restrito pode ter maior detalhe organizacional, mas continua sem PII.

### 2.5 Protocolo A1–A5

| Etapa | Conteúdo | Função |
|---|---|---|
| A1 | contrato, fórmula e produção | declara o cálculo |
| A2 | resultado, schema, hashes, janela e manifesto | prova o produzido |
| A3 | oracle Python independente | recalcula a partir de dados atômicos |
| A4 | diagnóstico de divergência, drift e privacidade | explica anomalias |
| A5 | dossiê derivado de A1–A4 | recomenda e registra decisão |

O A5 resume a definição executável e a evidência; não é sua única fonte. Este
caderno é a consolidação deliberativa. Depois de aprovado, contratos, scripts,
fichas e A5 devem refletir a decisão.

### 2.6 Fichas metodológicas

###### I01 — Proporção de servidores por regime de trabalho

**Finalidade e relevância.** Descrever como participantes do PGD se distribuem
entre modalidades, no Instituto e por unidade executora. Contextualiza resultados,
sem presumir causalidade entre modalidade e desempenho.

**Fonte/grão.** PT ativos, integração de servidores/modalidade e unidades. Servidor
distinto × ciclo PT × modalidade × unidade.

```text
proporcao_institucional = servidores_distintos_na_modalidade
                          / servidores_distintos_com_PT_ativo × 100
proporcao_unidade = servidores_distintos_na_modalidade_e_unidade
                    / servidores_distintos_na_unidade × 100
```

Quem teve modalidades diferentes no ciclo pode aparecer em mais de uma categoria;
isso mede exposição, não apenas vínculo mais recente. Código desconhecido vira
`N.I.`. Cobertura do campo e dupla contagem devem acompanhar o resultado.

> **Analogia:** quem usou ônibus e trem aparece nos dois meios de transporte; a
> soma pode exceder viajantes sem erro.

**Decisão.** Aprovar exposição por ciclo e decidir se haverá visão complementar da
modalidade mais recente.

###### I02 — Taxa de cumprimento das entregas por unidade

**Finalidade e relevância.** Medir a proporção de entregas elegíveis do PE cuja
execução atingiu a meta; é a visão binária de resultado por unidade dona.

**Fonte/grão.** PE, entregas de PE e unidades. Ciclo PE × unidade dona. Universo:
entregas ativas, PE ativo sobreposto, meta planejada maior que zero.

```text
entrega_cumprida = progresso_realizado >= progresso_esperado
taxa = entregas_cumpridas / entregas_elegiveis × 100
```

Vencimento no ciclo e status formal avaliado/concluído são coberturas
complementares. Faixas atuais: A ≥ 90%, B ≥ 70%, C ≥ 50%, D < 50%; são triagem.

> **Analogia:** sete de dez compromissos atingiram a meta: 70%, ainda que a
> avaliação administrativa da carteira não tenha encerrado.

**Decisão.** Confirmar sobreposição como denominador principal ou priorizar as
entregas vencíveis no ciclo.

###### I03 — Taxa de cumprimento da meta por entrega

**Finalidade e relevância.** Medir quanto da meta pactuada foi realizado e localizar
nominalmente entregas críticas.

**Fonte/grão.** Entrega ativa de PE × ciclo × unidade dona.

```text
taxa_atingimento = meta_executada / meta_planejada × 100
```

Meta em `(0,1]` é normalizada para 0–100. Meta nula/não positiva é excluída;
resultado negativo é inconsistente. Faixas: <0 inconsistente; >100 superexecutada;
100 concluída; 70–<100 parcialmente cumprida; >0–<70 em andamento; 0 não executada.
O produto preserva lente numérica do ciclo e, quando interpretável, meta integral
do JSON.

> **Analogia:** 120 itens para meta 100 = 120%; capar em 100 esconderia possível
> superexecução ou subestimação.

**Decisão.** Aprovar dupla lente e manutenção de valores acima de 100%.

###### I04 — Score médio de atingimento de metas por unidade

**Finalidade e relevância.** Resumir as taxas das entregas por unidade dona, sem
substituir a análise nominal da carteira.

**Fonte/grão.** Mesmo universo do I02; unidade × ciclo. Peso igual por entrega.

```text
score_entrega = abs(realizado) / abs(planejado) × 100
score_unidade = media_aritmetica(score_entrega)
```

Pode superar 100%. Faixas: A ≥ 90, B ≥ 70, C ≥ 50, D < 50. A média não pondera
criticidade, custo, esforço ou tamanho da meta.

> **Analogia:** é a média de notas dando peso igual a cada entrega, pequena ou
> estratégica; orienta a investigação, não encerra o juízo.

**Decisão.** Confirmar pesos iguais e superexecução; ponderação futura exige nova
versão e recálculo.

###### I05 — Distribuição de entregas por servidor

**Finalidade e relevância.** Descrever quantas entregas distintas estão vinculadas
a cada participante e a dispersão na unidade executora. Sinaliza concentração,
fragmentação e possíveis problemas de cadastro; é processo, não resultado do PE.

**Fonte/grão.** PT, vínculos PT–entrega, entrega e unidade executora. Pessoa técnica
× ciclo PT × unidade no processamento; publicação agregada e sem identidade.

```text
entregas_por_participante = contagem_distinta(entrega_id)
media_unidade = media(entregas_por_participante)
posicao = acima, igual ou abaixo da media_unidade
```

A média é sensível a extremos; vínculo não prova esforço; zero pode ser cadastro
incompleto ou situação legítima.

> **Analogia:** contar projetos na agenda mostra dispersão, não complexidade. Uma
> pessoa com um projeto crítico pode ter mais carga que outra com cinco simples.

**Decisão.** Aprovar uso agregado e acrescentar mediana, quartis e proporção de
zeros.

###### I06 — Grau de responsabilidade por entrega

**Finalidade e relevância.** Medir participantes distintos por entrega e a
proporção de entregas por tamanho de equipe. Evidencia ponto único de falha e
oportunidade de cooperação.

**Fonte/grão.** PT e vínculo PT–entrega; entrega × ciclo PT × unidade executora.

```text
responsaveis_entrega = contagem_distinta(participante)
categoria = 1, 2, 3 ou 4+ participantes
percentual = entregas_na_categoria / entregas_da_unidade × 100
```

O vínculo não prova responsabilidade decisória formal. Equipe de uma pessoa pode
ser legítima conforme especialização e contingência.

> **Analogia:** uma chave com uma só pessoa cria dependência, mas pode ser aceitável
> se houver contingência. O indicador abre a pergunta; não julga sozinho.

**Decisão.** Aprovar categorias e tratar “1 participante” como gatilho de risco,
não como não conformidade automática.

###### I07 — Horas planejadas por entrega

**Finalidade e relevância.** Estimar capacidade planejada alocada à entrega a partir
da carga do PT, duração sobreposta e força de trabalho do vínculo. Identifica
entregas intensivas e ajuda a confrontar esforço planejado, progresso e risco.

**Fonte/grão.** PT, vínculos, PE, entregas e unidades. Ciclo PE; atribuição atual à
unidade dona do PE, com fallback à unidade do PT.

```text
horas_base = carga_horaria_horas × dias_sobrepostos / dias_totais_do_PT
horas_vinculo = horas_base × forca_trabalho / 100
horas_entrega = soma(horas_vinculo)
```

Contagem por dia usa 8 horas. O rateio usa dias corridos inclusivos, sem descontar
feriados, férias ou afastamentos. É estimativa planejada, não hora trabalhada. O
campo `num_servidores_alocados` conta planos distintos e pode não equivaler a
pessoas distintas.

> **Analogia:** estima combustível reservado para a rota; não é a leitura final do
> hodômetro nem comprovação de consumo.

**Decisão.** Aprovar a aproximação, renomear para `num_planos_trabalho_alocados` ou
alterar a contagem, e decidir sobre calendário útil em versão futura.

###### I08 — Proporção das horas planejadas por entrega

**Finalidade e relevância.** Mostrar a parcela da capacidade planejada da unidade
comprometida com cada entrega, identificando concentração e inconsistências.

**Fonte/grão.** Fontes do I07 e capacidade de todos os PT ativos do ciclo.

```text
proporcao_horas = horas_planejadas_entrega
                  / horas_disponiveis_unidade × 100
```

O numerador segue entrega/PE; o denominador deriva da capacidade dos PT. Quando a
unidade dona difere da executora, a perspectiva pode ficar inconsistente. Valor
acima de 100% aciona diagnóstico de alocação ou denominador.

> **Analogia:** não se divide despesa de uma diretoria pelo orçamento de outra.
> Numerador e denominador precisam pertencer à mesma perspectiva.

**Decisão condicionante.** Escolher: (a) executora nos dois termos; (b) dona nos
dois; ou (c) duas visões separadas. Recomenda-se (c). Não homologar a visão híbrida
como definitiva.

###### I09 — Média da avaliação do Plano de Trabalho

**Finalidade e relevância.** Resumir avaliação dos PT por unidade e ciclo, sua
distribuição e cobertura.

**Fonte/grão.** Avaliações, notas, consolidações, PT e unidades. A implementação
agrega eventos de avaliação ocorridos no ciclo.

```text
score = 6 - sequencia_da_nota
media_unidade = media(score_dos_eventos_validos)
```

Mapeamento: sequência 1 Excepcional → 5; 2 Alto desempenho → 4; 3 Adequado → 3;
4 Inadequado → 2; 5 Não executado → 1. Faixas: ≥4,5 Excepcional; ≥3,5 Alto;
≥2,5 Adequado; ≥1,5 Inadequado; abaixo disso Não executado. Múltiplos eventos podem
dar mais peso a um PT; planos e pessoas distintos revelam cobertura.

> **Analogia:** é a média de todas as provas, não necessariamente a média final de
> cada aluno. Quem fez mais provas pesa mais.

**Decisão.** Aprovar evento como grão principal ou consolidar por PT/período.
Recomenda-se evento para processo e visão complementar por plano.

###### I10 — Percentual de avaliações inadequadas

**Finalidade e relevância.** Medir incidência da categoria “Inadequado” nos PT e
localizar unidades/ciclos que exigem acompanhamento.

**Fonte/grão.** Mesmo universo de eventos válidos do I09.

```text
inadequada = sequencia_da_nota == 4
percentual = eventos_inadequados / eventos_validos × 100
```

O I10 usa sequência bruta 4, sem inversão. Faixas: ≥30% atenção crítica; ≥15%
moderada; ≥5% observação; <5% baixa prevalência. São triagem, sem efeito disciplinar.

> **Analogia:** uma ocorrência em duas avaliações é 50%, mas tem evidência mais
> frágil que cinquenta em cem; o denominador deve acompanhar o percentual.

**Decisão.** Confirmar categoria, grão e faixas; exigir volume e ressalva para
amostras pequenas.

###### I11 — Percentual de avaliações excepcionais

**Finalidade e relevância.** Medir incidência de “Excepcional” e, junto de I09/I10,
detectar reconhecimento, concentração de notas ou baixa diferenciação.

**Fonte/grão.** Mesmo universo de eventos válidos do I09.

```text
excepcional = sequencia_da_nota == 1
percentual = eventos_excepcionais / eventos_validos × 100
```

O I11 usa sequência bruta 1. Faixas atuais: ≥40% reconhecimento elevado; ≥20%
desempenho diferenciado; ≥5% destaque pontual; <5% escala subutilizada. Percentual
alto não prova desempenho institucional e pode sinalizar generosidade avaliativa.

> **Analogia:** muitos conceitos máximos podem refletir excelência ou uma régua
> pouco discriminante; compare com PE e distribuição completa.

**Decisão.** Aprovar como diagnóstico, não ranking, e revisar o rótulo “escala
subutilizada” quando universo pequeno ou sem desempenho excepcional.

###### I12 — Coerência entre avaliações de PT e PE

**Finalidade e relevância.** Comparar avaliação individual agregada do PT com
avaliação organizacional do PE, sinalizando aparente desalinhamento.

**Fonte/grão.** Avaliações/notas de PT, consolidações e PE, agregadas por unidade.
Só entram unidades com os dois tipos de avaliação.

```text
media_PT = media(6 - sequencia_PT)
media_PE = media(6 - sequencia_PE)
diferenca_absoluta = abs(media_PT - media_PE)
diferenca_direcional = media_PT - media_PE
```

Diferença ≤1: coerente; >1 e ≤2: divergência moderada; >2: elevada. Sinal positivo
indica média PT maior. As médias podem representar populações e volumes distintos;
o indicador não identifica causalidade nem incoerência individual.

> **Analogia:** comparar avaliação da tripulação com nota da viagem localiza
> discrepância, mas não prova qual avaliação está errada.

**Decisão.** Aprovar limiares e comparação agregada, sempre com volumes e direção.

###### PT_STATUS — Situação operacional dos Planos de Trabalho

**Finalidade e relevância.** Produzir fotografia acionável dos PT e consolidações:
rascunhos, assinaturas, execução, avaliação pendente e encerramento.

**Fonte/grão.** PT, consolidações, `status_justificativas` e unidades. O status do PT
é verdade de estado; a trilha fornece a data; sem trilha, usa-se `updated_at` com
origem declarada.

| Condição | Classificação gerencial |
|---|---|
| consolidação `CONCLUIDO` ainda não avaliada | Aguardando avaliação |
| PT `INCLUIDO` | Rascunho |
| PT `AGUARDANDO_ASSINATURA` | Aguardando assinatura |
| PT `ATIVO` | Em execução |
| PT/consolidação encerrado e avaliado | Concluído |
| PT `SUSPENSO`/`CANCELADO` | condição especial explícita |

“Aguardando avaliação” não existe em `planos_trabalhos.status`; deriva da
consolidação `CONCLUIDO`. A lente operacional pode conter fatos após o corte, mas
registra data/hora e não se mistura à série acumulada.

> **Analogia:** o PT é o processo; cada consolidação é uma etapa mensal. Um PT pode
> estar ativo e ter uma etapa aguardando avaliação.

**Decisão.** Aprovar precedência, lentes separadas e saída sem nomes; decidir os
status abertos padrão.

### 2.7 Interpretação cruzada

| Pergunta | Combinação | Cuidado |
|---|---|---|
| Entregas que exigem atenção | I03 + I02 + prazo/status PE | não substituir meta por atividade PT |
| Concentração de capacidade | I06 + I07 + I08 | validar dona/executora |
| Fragmentação de carga | I05 + I06 + textos sanitizados | quantidade não mede complexidade |
| Avaliação reflete resultado? | I09–I12 + I04 | comparar cobertura e populações |
| Fluxo está travado? | PT_STATUS + transições + prazos | fotografia não é tendência |
| Modalidade se associa a resultado? | I01 + I04/I09 | associação não é causalidade |

Textos sanitizados de entrega e execução podem explicar impedimentos, dependências
e riscos. A análise deve separar trecho observado, classificação automatizada e
interpretação, com rastreabilidade ao registro privado.

---

## 3. Alternativas metodológicas avaliadas

| Alvo | Opção A | Opção B | Recomendação |
|---|---|---|---|
| Taxonomia | manter I01–I12 | migrar para IG01–IG12 | qualificar agora; migrar só após fonte primária |
| I01 | todas as modalidades do ciclo | modalidade mais recente | A principal + B complementar |
| I02 | elegíveis sobrepostas | vencíveis no ciclo | A principal + B/cobertura |
| I03 | taxa numérica | meta integral JSON | publicar ambas |
| I04 | média sem teto | cap 100 ou peso estratégico | manter sem teto; peso em nova versão |
| I05 | média por pessoa | mediana/distribuição | manter série + estatísticas robustas |
| I06 | categorias 1/2/3/4+ | limiar único | categorias + alerta para 1 |
| I07 | dias corridos | dias úteis institucionais | A como estimativa; estudar B |
| I08 | perspectiva híbrida | dona e executora coerentes | duas visões coerentes |
| I09 | média por evento | consolidar por PT | A processo + B complementar |
| I10 | taxa/faixas fixas | incerteza e volume mínimo | taxa + volume/ressalva |
| I11 | percentual alto positivo | distribuição/leniência | segunda interpretação |
| I12 | diferença entre médias | pareamento de carteiras | A triagem; evoluir B |
| PT_STATUS | só abertos | abertos e fechados | abertos padrão; completo por filtro |

### 3.1 Teste de consistência decisória

A recomendação preserva a série, explicita limitações, separa resultado/capacidade,
permite aprofundamento versionado e mantém rastreabilidade. O único ponto que não
deve ser aceito por mera continuidade é I08: coerência de unidade entre numerador e
denominador é requisito lógico.

---

## 4. Avaliação de viabilidade

### 4.1 Escala

Notas de 1 a 5. Média: 4,5–5,0 = viabilidade alta; 3,5–4,4 = viável com
ressalvas; 2,5–3,4 = revisão necessária; abaixo de 2,5 = não recomendado. As notas
avaliam a medida, não o desempenho de qualquer unidade.

### 4.2 I01

| Critério | Nota (1–5) | Justificativa |
|---|---:|---|
| Clareza do indicador | 4 | dupla contagem exige explicação |
| Viabilidade da fórmula | 5 | contagem distinta reproduzível |
| Disponibilidade de dados | 4 | modalidade pode ser `N.I.` |
| Facilidade de coleta | 5 | automatizada |
| Aplicabilidade gerencial | 4 | contexto útil, sem causalidade |
| **Média** | **4,4** | **viável com ressalvas** |

### 4.3 I02

| Critério | Nota (1–5) | Justificativa |
|---|---:|---|
| Clareza do indicador | 5 | conclusão tem regra objetiva |
| Viabilidade da fórmula | 5 | numerador/denominador auditáveis |
| Disponibilidade de dados | 5 | campos centrais disponíveis |
| Facilidade de coleta | 5 | pipeline estabilizado |
| Aplicabilidade gerencial | 4 | exige prazo e status formal como contexto |
| **Média** | **4,8** | **viabilidade alta** |

### 4.4 I03

| Critério | Nota (1–5) | Justificativa |
|---|---:|---|
| Clareza do indicador | 4 | duas representações de meta |
| Viabilidade da fórmula | 4 | normalização/JSON aumentam complexidade |
| Disponibilidade de dados | 5 | progresso disponível |
| Facilidade de coleta | 5 | automatizada e validada |
| Aplicabilidade gerencial | 5 | identifica entrega crítica |
| **Média** | **4,6** | **viabilidade alta** |

### 4.5 I04

| Critério | Nota (1–5) | Justificativa |
|---|---:|---|
| Clareza do indicador | 4 | média simples deve ser explícita |
| Viabilidade da fórmula | 5 | derivação direta |
| Disponibilidade de dados | 5 | mesmo universo de I02 |
| Facilidade de coleta | 5 | pipeline estabilizado |
| Aplicabilidade gerencial | 3 | pode ocultar composição/criticidade |
| **Média** | **4,4** | **viável com ressalvas** |

### 4.6 I05

| Critério | Nota (1–5) | Justificativa |
|---|---:|---|
| Clareza do indicador | 4 | quantidade não é esforço |
| Viabilidade da fórmula | 5 | contagem distinta simples |
| Disponibilidade de dados | 5 | vínculos disponíveis |
| Facilidade de coleta | 5 | automatizada |
| Aplicabilidade gerencial | 3 | requer distribuição e contexto |
| **Média** | **4,4** | **viável com ressalvas** |

### 4.7 I06

| Critério | Nota (1–5) | Justificativa |
|---|---:|---|
| Clareza do indicador | 5 | tamanho de equipe objetivo |
| Viabilidade da fórmula | 5 | deduplicação definida |
| Disponibilidade de dados | 5 | vínculos disponíveis |
| Facilidade de coleta | 5 | automatizada |
| Aplicabilidade gerencial | 4 | forte para risco, não para sanção |
| **Média** | **4,8** | **viabilidade alta** |

### 4.8 I07

| Critério | Nota (1–5) | Justificativa |
|---|---:|---|
| Clareza do indicador | 4 | deve ser denominado estimativa |
| Viabilidade da fórmula | 4 | rateio implementável |
| Disponibilidade de dados | 4 | limitações de carga/força |
| Facilidade de coleta | 5 | automatizada |
| Aplicabilidade gerencial | 3 | dias corridos; não mede hora realizada |
| **Média** | **4,0** | **viável com ressalvas** |

### 4.9 I08

| Critério | Nota (1–5) | Justificativa |
|---|---:|---|
| Clareza do indicador | 4 | participação da capacidade é clara |
| Viabilidade da fórmula | 3 | perspectiva organizacional pendente |
| Disponibilidade de dados | 4 | numerador e capacidade existem |
| Facilidade de coleta | 5 | automatizada |
| Aplicabilidade gerencial | 2 | pode enganar se unidades divergirem |
| **Média** | **3,6** | **ressalva semântica bloqueante** |

### 4.10 I09

| Critério | Nota (1–5) | Justificativa |
|---|---:|---|
| Clareza do indicador | 4 | escala definida; grão exige explicação |
| Viabilidade da fórmula | 5 | transformação determinística |
| Disponibilidade de dados | 5 | eventos/notas disponíveis |
| Facilidade de coleta | 5 | automatizada |
| Aplicabilidade gerencial | 3 | ponderação por evento exige contexto |
| **Média** | **4,4** | **viável com ressalvas** |

### 4.11 I10

| Critério | Nota (1–5) | Justificativa |
|---|---:|---|
| Clareza do indicador | 5 | categoria e denominador objetivos |
| Viabilidade da fórmula | 5 | teste direto da sequência 4 |
| Disponibilidade de dados | 5 | eventos disponíveis |
| Facilidade de coleta | 5 | automatizada |
| Aplicabilidade gerencial | 4 | bom alerta com volume explícito |
| **Média** | **4,8** | **viabilidade alta** |

### 4.12 I11

| Critério | Nota (1–5) | Justificativa |
|---|---:|---|
| Clareza do indicador | 5 | categoria e denominador objetivos |
| Viabilidade da fórmula | 5 | teste direto da sequência 1 |
| Disponibilidade de dados | 5 | eventos disponíveis |
| Facilidade de coleta | 5 | automatizada |
| Aplicabilidade gerencial | 3 | alto percentual é ambíguo |
| **Média** | **4,6** | **alta com revisão de rótulos** |

### 4.13 I12

| Critério | Nota (1–5) | Justificativa |
|---|---:|---|
| Clareza do indicador | 4 | direção/diferença compreensíveis |
| Viabilidade da fórmula | 4 | médias reproduzíveis |
| Disponibilidade de dados | 4 | requer PT e PE simultâneos |
| Facilidade de coleta | 5 | automatizada |
| Aplicabilidade gerencial | 3 | populações distintas limitam inferência |
| **Média** | **4,0** | **viável com ressalvas** |

### 4.14 PT_STATUS

| Critério | Nota (1–5) | Justificativa |
|---|---:|---|
| Clareza do indicador | 5 | estados acionáveis |
| Viabilidade da fórmula | 5 | precedência determinística |
| Disponibilidade de dados | 5 | PT, consolidações e trilha disponíveis |
| Facilidade de coleta | 5 | automatizada |
| Aplicabilidade gerencial | 5 | orienta atuação imediata |
| **Média** | **5,0** | **viabilidade alta** |

### 4.15 Síntese

I02, I03, I06, I10, I11 e `PT_STATUS` têm alta viabilidade. I01, I04, I05, I07,
I09 e I12 são viáveis com ressalvas obrigatórias. I08 requer decisão semântica antes
da homologação plena. Nenhum score autoriza ranking ou decisão automática sobre
unidades, chefias ou servidores.

---

## 5. Recomendações e próximos passos

### 5.1 Recomendações

1. **Homologar por versão.** Registrar fórmula, schema, fontes, janela,
   granularidade, tolerâncias e hashes da baseline.
2. **Resolver a taxonomia antes da publicação externa.** Anexar fonte primária e
   usar namespace qualificado enquanto houver homonímia.
3. **Aprovar I02–I04 como núcleo de resultado do PE.** A análise deve chegar às
   entregas e evidências, não parar no score.
4. **Aprovar I05–I08 como processo/capacidade do PT.** Proibir apresentação como
   comprovação de alcance da meta do PE.
5. **Condicionar I08 à coerência de unidade.** Implementar e testar as perspectivas
   dona e executora antes da baseline definitiva.
6. **Aprovar I09–I12 com cobertura explícita.** Sempre divulgar eventos, planos e
   unidades junto de médias e percentuais.
7. **Revisar rótulos normativos.** Faixas A–D, atenção, reconhecimento e coerência
   são triagem, salvo norma formal.
8. **Preservar textos sanitizados.** Usá-los para impedimentos, riscos e mitigação,
   mantendo dados pessoais fora do relatório.
9. **Manter A5 automático.** Reabrir decisão humana apenas por mudança material,
   drift bloqueante ou divergência.
10. **Expandir após homologar a GR2.** Validar escopo nacional, unidade, mesogrupo,
    tipo e lista arbitrária com a mesma metodologia.

### 5.2 Matriz de deliberação

| ID | Tema | Proposta técnica | Decisão CGOV |
|---|---|---|---|
| D01 | Catálogo | confirmar fonte; namespace qualificado | ☐ aprovar ☐ ajustar ☐ rejeitar |
| D02 | Janela | 01/07/2025 ao mês anterior | ☐ aprovar ☐ ajustar ☐ rejeitar |
| D03 | Organização | dona e executora separadas | ☐ aprovar ☐ ajustar ☐ rejeitar |
| D04 | I02 | sobreposição principal; vencíveis complementar | ☐ aprovar ☐ ajustar ☐ rejeitar |
| D05 | I03 | ciclo e meta integral | ☐ aprovar ☐ ajustar ☐ rejeitar |
| D06 | I04 | média simples, igual e sem teto | ☐ aprovar ☐ ajustar ☐ rejeitar |
| D07 | I05 | agregado + mediana/quartis | ☐ aprovar ☐ ajustar ☐ rejeitar |
| D08 | I06 | 1/2/3/4+; “1” como risco | ☐ aprovar ☐ ajustar ☐ rejeitar |
| D09 | I07 | dias corridos; renomear contador | ☐ aprovar ☐ ajustar ☐ rejeitar |
| D10 | I08 | duas perspectivas coerentes | ☐ aprovar ☐ ajustar ☐ rejeitar |
| D11 | I09 | evento + visão por plano | ☐ aprovar ☐ ajustar ☐ rejeitar |
| D12 | I10/I11 | sequência bruta; faixas como triagem | ☐ aprovar ☐ ajustar ☐ rejeitar |
| D13 | I12 | diferença/direção com volumes | ☐ aprovar ☐ ajustar ☐ rejeitar |
| D14 | PT_STATUS | precedência e lente separada | ☐ aprovar ☐ ajustar ☐ rejeitar |
| D15 | Baseline | aprovar fingerprints após ajustes | ☐ aprovar ☐ ajustar ☐ rejeitar |
| D16 | Expansão | nacional e seletores após GR2 | ☐ aprovar ☐ ajustar ☐ rejeitar |

### 5.3 Minuta de deliberação

> A Coordenação de Governança do ICMBio, após examinar este Caderno e os artefatos
> A1–A5 da execução de referência, delibera:
>
> I — reconhecer a separação entre resultado dos PE, processo/capacidade dos PT e
> acompanhamento operacional;
>
> II — aprovar a janela iniciada em 01/07/2025 e encerrada no último dia do mês
> anterior à execução;
>
> III — decidir cada definição constante da matriz D01–D16;
>
> IV — determinar que faixas e semáforos sejam triagem, nunca decisão automática
> sobre unidades ou pessoas;
>
> V — autorizar recertificação automática mensal quando contratos, fontes,
> fórmulas, schemas, oracles, temporalidade e privacidade permanecerem inalterados e
> todos os testes forem aprovados;
>
> VI — exigir nova apreciação diante de mudança material, drift bloqueante ou
> divergência acima da tolerância;
>
> VII — autorizar expansão nacional e por seletores somente após incorporar as
> condicionantes da homologação GR2.

### 5.4 Registro da decisão

| Campo | Preenchimento pela CGOV |
|---|---|
| Resultado geral | ☐ homologado ☐ com condicionantes ☐ devolvido |
| Versão aprovada |  |
| Itens condicionados |  |
| Prazo |  |
| Unidade responsável |  |
| Data |  |
| Processo/ata |  |
| Observações |  |

### 5.5 Efeitos no ciclo

1. transcrever decisões para `ValidationTarget` e documentação;
2. incrementar versão dos alvos alterados;
3. invalidar caches/A5 afetados, preservando o histórico;
4. executar fixtures, propriedades, metamórficos e integração GR2;
5. gerar novos A3–A5 com fingerprints coerentes;
6. registrar `HOMOLOGADO` na baseline inicial;
7. permitir `CERTIFICADO_AUTOMATICAMENTE` nos ciclos estáveis;
8. bloquear relatório se alvo obrigatório falhar ou ficar pendente;
9. executar e validar expansão nacional e seletores.

## Anexo A — Tolerâncias e gates

| Objeto | Regra |
|---|---|
| Contagens/chaves | igualdade exata |
| Percentuais | diferença máxima 0,05 p.p. |
| Horas/scores | diferença absoluta máxima 0,01 |
| Categorias/status | igualdade exata |
| Mudança de schema | bloqueante |
| Chaves A1 × A3 | diferença bloqueante |
| Nulos | >5 p.p. alerta; >15 p.p. bloqueante |
| Volume comparável | >30% alerta; >60% bloqueante |
| PSI | >0,20 alerta; >0,30 bloqueante |
| PII em produto | bloqueante |
| Fato após corte acumulado | bloqueante |

Drift usa ciclos fechados comparáveis ou parcela incremental, nunca o total
cumulativo bruto.

## Anexo B — Testes obrigatórios

- invariância à ordem e idempotência;
- ausência de efeito de fatos fora da janela e registros apagados;
- deduplicação determinística;
- denominador zero, nulos e datas invertidas;
- ciclo parcial, virada de ano e ano bissexto;
- reconciliação de total/subtotais e divisão/recombinação de unidades;
- limites de percentuais e exceção de superexecução;
- coerência entre produtos restrito e compartilhável;
- ausência de nome, CPF, e-mail, telefone ou UUID pessoal;
- setembro/2026 = `01/07/2025–31/08/2026`, sem M09/Q3.

## Anexo C — Rastreabilidade

Diretório privado:

```text
artefatos_local/validacao/2026-09/
```

Manifesto integrado:

```text
manifesto_validacao_<run_id>.json
```

Para I01–I12:

```text
IND_OCDE_XX.3_validacao_independente_<run_id>.{json,md}
IND_OCDE_XX.4_diagnostico_<run_id>.{json,md}
IND_OCDE_XX.5_relatorio_validacao_<run_id>.md
```

Para gestão:

```text
PT_STATUS.3_validacao_independente_<run_id>.{json,md}
PT_STATUS.4_diagnostico_<run_id>.{json,md}
PT_STATUS.5_relatorio_validacao_<run_id>.md
```

Apoio: `docs/09-protocolo-validacao-indicadores.md`, fichas `docs/ocde/06.*`,
`docs/07.1-estrutura-banco-dados.md`, `docs/07.2-status_artefatos_pgd_icmbio.md`,
`docs/14-status-planos-trabalho-gestores.md` e `lib/validation_contracts.py`.

## Anexo D — Glossário

| Termo | Definição |
|---|---|
| PE | compromisso organizacional de resultado |
| Entrega | resultado pactuado com meta/progresso próprios |
| PT | organização da participação/capacidade individual |
| Consolidação | fechamento/avaliação periódica do PT |
| Unidade dona | responsável pelo PE/entrega |
| Unidade executora | unidade do PT/capacidade |
| Evento | registro individual de avaliação |
| Oracle | recálculo independente sobre dados atômicos |
| Baseline | fórmula, código, schema, oracle, tolerâncias e hashes homologados |
| Drift | mudança relevante de schema, cobertura, volume ou distribuição |
| Lente acumulada | 01/07/2025 ao último dia do mês anterior |
| Lente operacional | fotografia corrente com data/hora própria |

## Anexo E — Conflito de taxonomia a resolver

O catálogo referencial da skill institucional informa como fonte o arquivo
`Instrumento Avaliação PGD.xlsx | ICMBio 2025`. A tabela evidencia que apenas o
tema de alcance de entregas possui aproximação parcial; os demais códigos designam
objetos distintos. A comparação não conclui qual catálogo é o oficial do piloto:
essa conclusão depende da fonte primária e da decisão da CGOV.

| Código | Catálogo implementado neste projeto | Instrumento de Avaliação PGD 2025 |
|---|---|---|
| I01 | proporção por regime de trabalho | alinhamento das entregas ao planejamento estratégico |
| I02 | taxa de cumprimento de entregas por unidade | alinhamento das entregas aos macroprocessos |
| I03 | taxa de cumprimento da meta por entrega | percentual de entregas com metas alcançadas |
| I04 | score médio de atingimento de metas | satisfação de usuários de serviços públicos |
| I05 | distribuição de entregas por servidor | nível de uso do PGD na alocação da força de trabalho |
| I06 | grau de responsabilidade por entrega | abrangência do PGD na organização |
| I07 | horas planejadas por entrega | despesas administrativas per capita |
| I08 | proporção das horas por entrega | atratividade de vagas com PGD |
| I09 | média da avaliação do PT | chefias em ações de desenvolvimento de liderança PGD |
| I10 | percentual de avaliações inadequadas | percentual de Planos de Entregas avaliados |
| I11 | percentual de avaliações excepcionais | percentual de Planos de Trabalho avaliados |
| I12 | coerência entre avaliação PT e PE | afastamento para tratamento da própria saúde |

Encaminhamento mínimo para D01:

1. localizar e anexar a versão controlada do *Performance Toolkit* que originou o
   repositório;
2. confrontá-la com o `Instrumento Avaliação PGD.xlsx | ICMBio 2025`;
3. registrar se os portfólios são concorrentes, complementares ou de fases
   diferentes do piloto;
4. definir namespace, código, título e versão de cada portfólio;
5. atualizar scripts, relatórios, skills e A5 sem apagar aliases históricos.

## Conclusão técnica

Há base suficiente para deliberação dos treze alvos. A implementação é reproduzível
e o oracle não apontou divergência bloqueante na referência. A homologação deve,
porém, registrar as escolhas semânticas deste caderno. Recomenda-se homologação com
condicionantes, mantendo I08 pendente de ajuste organizacional e a taxonomia
pendente de confirmação documental. Resolvidos esses pontos, o ciclo poderá operar
com recertificação automática e intervenção humana apenas por mudança ou falha.
