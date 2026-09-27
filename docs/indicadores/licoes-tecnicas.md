# Lições técnicas dos indicadores

> **Para quem é:** quem altera um A1, um oracle ou um relatório. Reúne erros já
> corrigidos, para não repeti-los, e achados de semântica que explicam escolhas de
> fórmula. As regras vigentes estão no protocolo de validação e nas fichas; este
> documento explica **por que** elas existem.

## 1. Erros corrigidos (não repetir)

| Erro | Indicadores | Causa | Correção |
| --- | --- | --- | --- |
| Escala de avaliação invertida | I09–I12 | `JSON_UNQUOTE(tan.nota)` devolvia nulo | Nota por `6 - tan.sequencia` (só nas médias, I09 e I12) |
| "Inadequado" errado | I10 | `sequencia = 2` (que é "Alto desempenho") | `sequencia = 4` |
| "Excepcional" errado | I11 | `sequencia = 5` (que é "Não executado") | `sequencia = 1` |
| Unidade errada | I07, I08 | `pt.unidade_id` no lugar da unidade do plano de entregas | `COALESCE(pe.unidade_id, ph.unidade_id)` |
| Linhas duplicadas por período | I07 | Faltava o filtro temporal do plano de entregas na CTE de linhas | Filtro por `pe.data_inicio`/`pe.data_fim` com `CROSS JOIN parametros` |
| Avisos deslocados | I05–I12 | Offsets posicionais fixos; a coluna `mesogrupo`, acrescentada depois, deslocava os avisos | Variáveis separadas: colunas e linhas para os avisos, e outras (com `mesogrupo`) para a escrita do CSV |
| Alias de alvo quebrado | todos | `replace("IND_", "I")` transformava `IND_OCDE_07` em `IOCDE_07` | `normalize_target` por expressão regular, tratando `IND_GEST_` antes |
| Plano duplicado | G01 | Junção da trilha de status por `created_at = MAX` com empates | CTE do responsável agregada, com interrupção se sobrar duplicata (D17) |
| Falha técnica falsa | G01 | O runner de validação pegava o A2 mais recente de qualquer produto | Busca pelo produto solicitado; células `SUPRIMIDO_K` fora da comparação |
| Avaliações de consolidações excluídas | I09–I12 | Faltava `deleted_at IS NULL` em `planos_trabalhos_consolidacoes` | Filtro em toda tabela do FROM/JOIN (correção de versão em I09–I12) |
| Falha de período engolida | I02–I12 | O A1 seguia gravando A2 parcial quando a consulta de um período falhava | Falha de qualquer período encerra o A1 sem gravar (D33) |
| Regional só com a sede | recortes regionais | A estrutura oficial não tem sigla nas unidades subordinadas; o recorte GR2 pegava só a regional | Recorte pela hierarquia do PETRVS, com trava de divergência (D19) |

## 2. Achados de semântica

- **I02 — dois sentidos de "concluída".**
  - O critério OCDE é `progresso_realizado >= progresso_esperado`.
  - O fluxo formal do PETRVS usa `pe.status = 'AVALIADO'`.
  - Os dois medem coisas diferentes, e o indicador segue o critério OCDE.
- **I12 — sinal da diferença.** O sinal de `diferenca_direcional` estava invertido e foi
  corrigido. Com o sinal certo, o padrão "avaliação do plano de entregas acima da do
  plano de trabalho" é real.
- **I09 — média por evento × média por plano.**
  - Muitos planos de trabalho têm várias avaliações (eventos).
  - A média por evento dá mais peso aos planos reavaliados, por isso a métrica primária
    é a média por plano (D11).
  - A média por evento continua disponível como coluna auxiliar.
- **Status do plano de trabalho em duas camadas.** "Aguardando avaliação" é uma
  consolidação em `CONCLUIDO`, não um status do plano. Detalhes em
  [estrutura do banco de dados](../dados-petrvs/estrutura-banco-dados.md).
- **Resultado × processo.** O resultado do plano de entregas nunca é substituído por
  atividade do plano de trabalho; o relatório preserva a unidade dona e a executora.

## 3. Cuidados recorrentes no VQL e no Python

- `* 100.0` antes da divisão, senão o JDBC faz divisão inteira; `NULLIF` contra
  divisão por zero (`progresso_esperado = 0` em I03 e I04).
- Dias úteis e hierarquias são calculados em Python: o VQL não tem CTE recursiva nem
  funções de diferença de datas.
- Nunca `date.today()` num cálculo de período: a janela vem de `--data-execucao`.
- Mudança de fórmula entra na produção **e** no oracle, cada um com o seu código, e
  incrementa `formula_version`.
