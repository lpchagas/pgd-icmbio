# Contexto Estratégico dos Indicadores PGD (Projeto OCDE/ICMBio)

Este documento consolida o contexto institucional, os marcos do projeto, os achados analíticos e os próximos passos do trabalho de indicadores OCDE/PGD do ICMBio, servindo como base de referência para as consultas SQL deste repositório.

---

## 1. O Projeto Piloto OCDE

### Identidade do projeto

**"Fortalecendo a capacidade organizacional no Brasil: Implementando indicadores de desempenho em organizações federais"**

| Atributo | Detalhe |
| --- | --- |
| Realizadores | OCDE · MGI · ICMBio · UFRN |
| Período | Janeiro/2025 a Maio/2026 |
| Pilares avaliados | Gestão de Pessoas · Finanças · **PGD** |
| Foco do pilar PGD | 12 indicadores de desempenho propostos pela OCDE para o Programa de Gestão e Desempenho |

### Objetivo estratégico

Transformar o PGD de uma ferramenta de **controle de frequência** em um instrumento de **gestão de desempenho e tomada de decisão baseada em evidências**.

Este esforço está diretamente alinhado às competências da **Coordenação de Governança (CGOV)** (Portaria ICMBio n.º 5.592/2025), fornecendo dados quantitativos para:

- Monitoramento da Cadeia de Valor e Alinhamento Estratégico
- Dimensionamento da Força de Trabalho (DFT)
- Governança, Cultura de Controle e Gestão de Riscos

---

## 2. O ICMBio e o PGD

### Perfil institucional

O ICMBio (Instituto Chico Mendes de Conservação da Biodiversidade), criado em 2007, é uma autarquia federal vinculada ao Ministério do Meio Ambiente e Mudança do Clima (MMA). Sua missão: promover a conservação ambiental e a gestão das unidades de conservação no Brasil.

| Estrutura | Números (abril/2026) |
| --- | --- |
| Unidades de Conservação | 344 |
| Centros de Pesquisa | 14 |
| Gerências Regionais | 5 (Norte, Nordeste, Centro-Oeste, Sudeste e Sul) |
| Servidores efetivos | 2.058 |
| Agentes temporários ambientais | 3.594 |
| **Total de agentes públicos** | **5.652** |

### Trajetória de implementação do PGD

| Etapa | Detalhe |
| --- | --- |
| Início | Novembro/2024 |
| Fases | Normatização → Sensibilização → Orientação → Treinamento em serviço → Suporte contínuo |
| Sistema | PETRVS (via ColaboraGov/MGI) |
| Servidores em PGD | 1.989 |
| Unidades executoras | 600 |
| Suporte | Pontos focais na Sede e nas Gerências Regionais |
| Gestão compartilhada | CGGE (estratégico) e CGGP (normativo/operacional) |

### Governança do PGD

**Papel da Gestão Estratégica (CGGE):**

- Alinhamento dos Planos de Trabalho ao Planejamento Estratégico Institucional
- Foco na entrega de resultados e nos indicadores de desempenho

**Papel da Gestão de Pessoas (CGGP):**

- Suporte normativo e operacional, capacitação e acompanhamento funcional
- Gestão dos processos de teletrabalho e time volante

**Funcionamento:** reuniões semanais entre as equipes; planos de ação e relatórios semestrais.

---

## 3. Desafios Identificados

| Desafio | Descrição |
| --- | --- |
| Mudança de paradigma | Transição da cultura do "controle de frequência" para o foco na "entrega de valor pública" |
| Lacunas gerenciais | Necessidade de capacitar lideranças para gerir equipes por desempenho e feedback, não por presença física |
| Mensuração de atividades finalísticas | Dificuldade em parametrizar e quantificar ações complexas (ex.: fiscalização de UC, pesquisa de campo) |
| Curva de aprendizagem tecnológica | Adaptação ao PETRVS buscando integridade e qualidade dos dados inseridos |
| Risco do "registro pelo registro" | Mitigar o "depósito de atividades" — garantir que a avaliação foque na qualidade técnica e no impacto, não apenas no fluxo do sistema |
| Incompletude sistêmica | Entregas planejadas sem registro de execução pelas chefias → falsos déficits de desempenho |
| Falta de padronização | Ciclos de avaliação díspares (mensais vs. semestrais) dificultam comparação transversal entre unidades |
| Outliers na base | Distorções (ex.: unidades com +600% de atingimento de metas) indicam erros de input e ausência de travas de validação |

### Ações adotadas para superar os desafios

1. **Pontos focais descentralizados:** incremento da comunicação e plantões internos entre os pontos focais nas GRs
2. **Programa de Desenvolvimento de Lideranças:** definição de competências e treinamento para diferentes níveis de gestão
3. **Melhoria dos Planos de Entregas:** criação de modelos baseados na Cadeia de Valor institucional
4. **Monitoramento dos dados:** acompanhamento sistemático do preenchimento do PETRVS com base nos relatórios do sistema

---

## 4. O Projeto Técnico — Engenharia Analítica

### O que foi construído

Conjunto de consultas SQL e documentação técnica que permite calcular os 12 indicadores OCDE/PGD do ICMBio diretamente sobre a base operacional do PETRVS — sem ETL, datamart intermediário ou containers.

Toda a inteligência analítica vive em arquivos SQL versionáveis e em um manual técnico estruturado por eixo e indicador.

### Escala do trabalho

| Dimensão | Valor |
| --- | --- |
| Indicadores documentados | 12 (um arquivo por indicador) |
| Eixos OCDE/PGD | 4 |
| Unidades organizacionais mapeadas | 379 |
| Entregas no ciclo 2025 | ~14.700 |
| Tabelas do PETRVS mapeadas | 130+ |

### A transição: dump estático → Denodo em tempo real

| Aspecto | Antes (dump estático) | Agora (Denodo/MGI) |
| --- | --- | --- |
| Origem do dado | Cópia bruta do banco por demanda ao MGI | Virtualização em tempo real (Dataprev) |
| Atualização | Defasagem de dias/semanas | Tempo real |
| Infraestrutura local | MySQL 8.0 instalado na máquina | Apenas DBeaver (gratuito) |
| Conexão | localhost:3306 | denodo-pgd.dataprev.gov.br:443 |
| Acompanhamento | Pontual — inviável em tempo real | Contínuo — mesmo durante o ciclo PGD |
| Queries SQL | Identidade — mesmas queries parametrizadas | **Sem alteração** — basta trocar o ponto de conexão |

A engenharia analítica criada sobre o dump é **integralmente reaproveitada** no Denodo: muda apenas o endereço da conexão no DBeaver.

---

## 5. Principais Achados — Eixo 2 (Execução, ciclo jan–dez/2025)

Os dados abaixo foram extraídos do banco PETRVS (dump de fevereiro/2026) e apresentados na Rede PGD em 13/05/2026. Representam o primeiro ciclo anual completo de análise quantitativa do PGD/ICMBio.

### I02 — Taxa de cumprimento por unidade

| Métrica | Valor |
| --- | --- |
| Taxa geral no órgão | **53,7%** |
| Unidades avaliadas | 379 |
| Entregas no ciclo | 10.902 |
| Concluídas (≥ meta) | 5.851 |
| Sem meta válida (descartadas) | 2,5% |

### I03 — Taxa de cumprimento por entrega

| Métrica | Valor |
| --- | --- |
| Taxa geral (concluídas + superexecutadas) | **54,3%** |
| Entregas analisadas | 10.420 |
| Concluídas exatamente na meta | 43,7% |
| Superexecutadas (acima da meta) | 10,6% |
| Sem progresso registrado | 30,7% |

### I04 — Score médio de atingimento

| Métrica | Valor |
| --- | --- |
| Média geral | **108,8%** |
| Mediana | 92,0% |
| Score máximo (DISAT) | 945% |
| Unidades com score zero | 36 |
| Grupo A — alto desempenho (≥ 90%) | 52,0% |
| Grupo D — baixo desempenho (< 50%) | 26,6% |

### Achados-chave para a gestão

**1. Polarização A vs. D:** 52% das unidades no Grupo A e 26,6% no Grupo D — a zona intermediária (B e C) é escassa (apenas 8,2% do total).

**2. Concentração de carteira no baixo desempenho:** o Grupo D detém 45,5% de todas as entregas, com taxa média de cumprimento de apenas 18,7%.

**3. Risco de não-registro:** 30,7% das entregas sem progresso registrado e 36 unidades com score zero — pode ser falha de execução ou falha de lançamento no sistema.

**4. Subplanejamento sistemático em outliers:** 34 unidades com score acima de 200% (máximo: 945%) — sinal de metas subestimadas no planejamento, não de alto desempenho real.

---

## 6. Marcos e Entregas do Projeto

### Entregas já consolidadas

| Entrega | Status |
| --- | --- |
| 12 documentos técnicos individuais (um por indicador) com SQL + interpretação | Concluído |
| Arquivo único `indicadores_ocde_pgd_icmbio_mysql_direto.sql` (todas as queries) | Concluído |
| Manual técnico estruturado por eixo: `docs/06.X-eixoX.md` + `docs/06.X.X-iXX.md` | Concluído |
| Mapa de 130+ tabelas do PETRVS + 6 tabelas críticas para os indicadores | Concluído (`docs/07-estrutura-banco-dados.md`) |
| Guia para gestores sem SQL | Concluído (`docs/indicadores/guia-rapido-gestores.md`) |
| Protocolo de validação manual (comparação SQL ↔ PETRVS online) | Concluído (`docs/indicadores/protocolo-validacao.md`) |
| I02 validado — critério OCDE vs. fluxo formal documentado | Evidência histórica mantida na área privada de validação |
| Conexão Denodo configurada no DBeaver (acesso em tempo real) | Concluído (maio/2026) |
| Documentação de conexão Denodo atualizada | Concluído (`docs/ambiente/acesso-denodo-dbeaver.md`) |

### Em curso (Fase 7 — Validação Manual)

| Atividade | Status |
| --- | --- |
| Validação de I03, I04 contra PETRVS online | Pendente |
| Validação de I09–I12 (avaliações) | Pendente |
| Sincronização das queries SQL com correções de auditoria | Contínuo |

---

## 7. Próximos Passos

### Técnicos (repositório)

1. **Adaptar conexões para Denodo** — verificar compatibilidade das queries com VQL do Denodo (especialmente CTEs recursivas de I07 e I08)
2. **Concluir validação manual** — I03, I04, I01 e I09–I12
3. **Publicar o repositório como referência aberta** na Rede PGD para outros órgãos da APF

### Estratégicos (ICMBio)

1. **Governança de dados:** inserir travas sistêmicas no PETRVS (ex.: impedir registro de meta atingida acima de 150% sem justificativa textual obrigatória)
2. **Processos:** criar um Comitê Gestor de Dados do PGD cruzando CGOV, CGGP e CGTI
3. **Tecnologia:** evoluir para painel gerencial automatizado sobre a camada Denodo (BI integrado)
4. **Capacitação:** incremento da equipe técnica e treinamento contínuo em análise de dados do PGD

### Para outros órgãos da APF

Este repositório foi construído como **referência reproduzível**. Qualquer órgão que utilize o PETRVS e tenha acesso ao Denodo pode aplicar os mesmos indicadores com mínima adaptação:

- As queries usam apenas tabelas padrão do PETRVS (não há customização ICMBio)
- O bloco `parametros` permite ajustar período e filtros sem editar o restante da query
- A documentação cobre desde o setup até a interpretação dos resultados para gestores

---

## 8. Os 4 Eixos e os 12 Indicadores

O *Performance Toolkit* da OCDE estabelece 12 indicadores chave, divididos em 4 eixos estruturantes.

### Eixo 1 — Trabalho Remoto

Mede como a força de trabalho está distribuída entre os regimes de atuação (presencial, híbrido, teletrabalho). É o contexto que enquadra todos os outros indicadores — o regime de trabalho afeta diretamente como os planos são estruturados e executados.

| Indicador | Descrição resumida | Tabela base | Status |
| --- | --- | --- | --- |
| I01 | Proporção de servidores por regime de trabalho | `planos_trabalhos` + `tipos_modalidades` | Disponível (validar campo `nome`) |

### Eixo 2 — Execução

Mede o cumprimento das metas pactuadas nos Planos de Entregas. Responde se o que foi planejado foi efetivamente entregue, tanto em nível binário (cumpriu ou não) quanto em nível escalar (qual percentual da meta foi atingido).

| Indicador | Descrição resumida | Tabela base | Status |
| --- | --- | --- | --- |
| I02 | Taxa de cumprimento das entregas (por unidade) | `planos_entregas_entregas` | Disponível · validado (mai/2026) |
| I03 | Taxa de cumprimento de metas por entrega | `planos_entregas_entregas` | Disponível · validação pendente |
| I04 | Índice de atingimento de metas — score médio por unidade | `planos_entregas_entregas` | Disponível · validação pendente |

### Eixo 3 — Carga de Trabalho

Mede como o esforço está distribuído entre servidores e entregas. Identifica concentração de trabalho, gargalos de dependência e proporção de horas alocadas por entrega.

| Indicador | Descrição resumida | Tabela base | Status |
| --- | --- | --- | --- |
| I05 | Distribuição das entregas entre os servidores | `planos_trabalhos_entregas` | Disponível |
| I06 | Grau de responsabilidade pelas entregas | `planos_trabalhos_entregas` | Disponível |
| I07 | Estimativa de horas planejadas por entrega | `planos_trabalhos_entregas` | Disponível no Denodo |
| I08 | Proporção da capacidade planejada por entrega | `planos_trabalhos_entregas` | Disponível, com ressalva de unidade |

### Eixo 4 — Desempenho e Avaliação

Mede a qualidade percebida do desempenho via as avaliações registradas no PETRVS. Complementa o Eixo 2: enquanto I02–I04 medem *o que foi entregue*, os indicadores deste eixo medem *como o trabalho foi avaliado*. O I12 verifica se as avaliações individuais (PT) são coerentes com as avaliações coletivas (PE) da mesma unidade.

| Indicador | Descrição resumida | Tabela base | Status |
| --- | --- | --- | --- |
| I09 | Média da avaliação do Plano de Trabalho por unidade | `avaliacoes` + `tipos_avaliacoes_notas` | Disponível (validar campos) |
| I10 | Percentual do conceito “Inadequado” (`sequencia = 4`) | `avaliacoes` + `tipos_avaliacoes_notas` | Disponível |
| I11 | Percentual do conceito “Excepcional” (`sequencia = 1`) | `avaliacoes` + `tipos_avaliacoes_notas` | Disponível |
| I12 | Coerência entre avaliação do PT e do PE por unidade | `avaliacoes` + `planos_entregas` | Disponível (validar campos) |

---

## 9. Fórmulas dos 12 Indicadores

### I01 — Proporção de servidores por regime de trabalho

```text
I (por regime) = (A / B) * 100
A = Servidores distintos com planos ativos no regime R durante o período
B = Total de servidores distintos com planos ativos no período (todos os regimes)

Regimes típicos: Presencial / Híbrido / Teletrabalho (nomes conforme tipos_modalidades)
```

Variante adicional: proporção por regime dentro de cada unidade (usa `PARTITION BY unidade_sigla`).

---

### I02 — Taxa de cumprimento das entregas

```text
I = (A / B) * 100
A = Entregas concluídas (progresso_realizado >= progresso_esperado)
B = Total de entregas planejadas no período com meta válida (progresso_esperado > 0)

Nível de agregação: por unidade

Classificação opcional por grupo de performance:
  A (>= 90%)  -> Alto desempenho
  B (70-89%)  -> Bom desempenho
  C (50-69%)  -> Desempenho intermediário
  D (< 50%)   -> Baixo desempenho
```

---

### I03 — Taxa de cumprimento de metas por entrega

```text
I = (A / B) * 100  (calculado por entrega individual)
A = progresso_realizado
B = progresso_esperado

Classificação automática:
  A > B  -> Superexecutada
  A = B  -> No alvo
  A < B  -> Subexecutada

Nível de agregação: por entrega (uma linha por entrega)
```

---

### I04 — Índice de atingimento de metas

```text
I = (SUM(Ai / Bi) / C) * 100
Ai = progresso_realizado de cada entrega i
Bi = progresso_esperado de cada entrega i
C  = total de entregas válidas da unidade

Equivalente a: AVG(proporção_atingimento) * 100 por unidade
Nível de agregação: por unidade (score médio)
```

---

### I05 — Distribuição das entregas entre os servidores

```text
Média da unidade = Total de atribuições distintas / Total de servidores com plano ativo

Por servidor:
  posição = 'Acima da média' se qtd_entregas_servidor > média_unidade
  posição = 'Abaixo da média' se qtd_entregas_servidor < média_unidade
  posição = 'Na média' se igual

Nível de agregação: por servidor dentro de cada unidade
```

---

### I06 — Grau de responsabilidade pelas entregas

```text
Por entrega:
  qtd_responsaveis = COUNT(DISTINCT usuario_id) dos planos vinculados à entrega

Agrupamento em faixas:
  '1 servidor'    -> entrega individual
  '2 servidores'  -> dupla
  '3 servidores'  -> trio
  '4+ servidores' -> grupo amplo

Nível de agregação: contagem de entregas por faixa, por unidade
```

---

### I07 — Horas por entrega — planejadas (absoluto)

```text
Horas_entrega = SUM(horas_proporcionais_plano_i * forca_trabalho_i / 100)

Onde para cada PT vinculado à entrega:
  horas_proporcionais_plano_i = carga_horaria do PT × dias de sobreposição / dias do PT
  forca_trabalho_i = percentual declarado em planos_trabalhos_entregas.forca_trabalho

A estimativa usa dias corridos porque o PETRVS não fornece calendário laboral
institucional suficiente para reconstrução retroativa.

Nível de agregação: por entrega (soma das contribuições dos PTs)
```

---

### I08 — Proporção de horas por entrega — planejadas (%)

```text
I = (A / B) * 100
A = Horas alocadas à entrega (resultado do I07)
B = Total de horas disponíveis de todos os servidores da unidade no período
    (soma de horas_planejadas por plano, SEM aplicar forca_trabalho — capacidade bruta)

Nota: a soma das proporções de todas as entregas de uma unidade NÃO precisa ser 100%.
O restante representa horas disponíveis não atribuídas explicitamente a nenhuma entrega.

Nível de agregação: por entrega + proporção em relação à capacidade da unidade
```

---

### I09 — Média da avaliação do Plano de Trabalho

```text
score = 6 - tipos_avaliacoes_notas.sequencia
I09 = AVG(score) por unidade

Sequência bruta: 1 = Excepcional, 2 = Alto desempenho, 3 = Adequado,
4 = Inadequado, 5 = Não executado.
Score convertido: 5 = melhor resultado e 1 = pior resultado.
```

### I10 — Percentual de avaliações inadequadas

```text
I10 = avaliações de PT com sequencia = 4 / total de avaliações de PT × 100
```

### I11 — Percentual de avaliações excepcionais

```text
I11 = avaliações de PT com sequencia = 1 / total de avaliações de PT × 100
```

I10 e I11 testam a sequência bruta; somente I09 e I12 aplicam `6 - sequencia`.

---

### I12 — Coerência entre avaliação do PT e do PE

```text
Diferença_unidade = |média_nota_PT - média_nota_PE| por unidade

Onde:
  média_nota_PT = AVG(nota) das avaliações de Planos de Trabalho da unidade
  média_nota_PE = AVG(nota) das avaliações de Planos de Entrega da unidade

Classificação da coerência:
  |diferença| <= 1.0  -> 'Coerente'
  |diferença| <= 2.0  -> 'Divergência moderada'
  |diferença|  > 2.0  -> 'Alta divergência'

Interpretação: se a unidade avalia bem os PT individuais mas mal o PE coletivo (ou vice-versa),
há uma incoerência que merece investigação — pode indicar avaliação por cordialidade,
subestimação coletiva ou desalinhamento entre líder e equipe.

Nível de agregação: por unidade (uma linha por unidade com PT e PE avaliados)
```

---

## 10. Regras Gerais de Uso das Consultas

### Bloco de parâmetros padrão

Todas as consultas usam um bloco `parametros` no início:

```sql
WITH parametros AS (
    SELECT
        CAST('2025-07-01' AS DATE) AS data_inicio,
        CAST('2026-08-31' AS DATE) AS data_fim,
        0 AS incluir_excluidos
)
```

O exemplo representa uma execução em setembro/2026. Nos scripts, informe
`--data-execucao`; `analysis_window()` calcula as datas e o mês corrente não entra.
- `incluir_excluidos = 0`: apenas registros ativos (`deleted_at is null`).
- `incluir_excluidos = 1`: inclui registros excluídos logicamente (útil para auditoria).

### Exclusão lógica no PETRVS

O PETRVS não apaga registros fisicamente. Registros excluídos recebem uma data em `deleted_at`. O campo `incluir_excluidos` controla se esses registros entram nos indicadores.

### Nomenclatura das entregas

O campo principal do nome da entrega é `descricao`. Se estiver vazio, usa-se `descricao_entrega` como fallback. Nenhuma entrega deve aparecer com nome em branco nos resultados.

### Nota sobre I01 e I09–I12

Esses cinco indicadores dependem de tabelas (`tipos_modalidades`, `tipos_avaliacoes_notas`) cujo conteúdo exato varia conforme a versão e configuração do PETRVS. Antes de executar, rode as consultas de mapeamento documentadas em [06-indicadores-ocde-denodo.md](../ocde/06-indicadores-ocde-denodo.md) para confirmar os nomes de campo e os valores de referência.

---

## 11. Tabelas do PETRVS Utilizadas

| Tabela | Indicadores | Campos críticos |
| --- | --- | --- |
| `planos_entregas_entregas` | I02, I03, I04, I07, I08 | `progresso_esperado`, `progresso_realizado`, `data_fim`, `unidade_id` |
| `planos_trabalhos` | I01, I05, I06, I07, I08 | `usuario_id`, `unidade_id`, `tipo_modalidade_id`, `data_inicio`, `data_fim` |
| `planos_trabalhos_entregas` | I05, I06, I07, I08 | `plano_trabalho_id`, `plano_entrega_entrega_id`, `forca_trabalho` |
| `planos_entregas` | I07, I08, I12 | `unidade_id`, `data_inicio`, `data_fim` |
| `unidades` | Todos | `id`, `sigla`, `nome` |
| `usuarios` | I05, I06, I09 | `id`, `nome` |
| `tipos_modalidades` | I01 | `id`, `nome` |
| `avaliacoes` | I09, I10, I11, I12 | `plano_trabalho_consolidacao_id`, `plano_entrega_id`, `tipo_avaliacao_id`, `tipo_avaliacao_nota_id` |
| `planos_trabalhos_consolidacoes` | I09, I10, I11, I12 | `id`, `plano_trabalho_id` |
| `tipos_avaliacoes` | I09, I10, I11, I12 | `id`, `nome` |
| `tipos_avaliacoes_notas` | I09, I10, I11, I12 | `id`, `nota` (validar nome do campo) |
