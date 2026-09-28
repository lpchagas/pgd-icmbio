# Manual Técnico — Indicadores OCDE/PGD ICMBio (Denodo, tempo real)

Este documento é o índice do manual técnico dos 12 indicadores do *Performance Toolkit* OCDE/PGD, implementados para execução direta na base original PETRVS via Denodo (virtualização em tempo real), sem datamart intermediário.

Cada indicador tem seu próprio documento com finalidade, implementação
canônica, explicação dos blocos e orientação para interpretar os resultados.
Os scripts em `ocde/indicadores/` são a fonte executável; exemplos SQL nas
fichas não substituem o código vigente.

Para o contexto estratégico do projeto, fórmulas e status de cada indicador,
consulte [05-contexto-ocde-pgd.md](../projeto/contexto-ocde-pgd.md).

---

## Como usar

### Opção A — scripts Python (recomendado)

1. Configure o `.env` local conforme o README.
2. Execute `python ocde/indicadores/IND_OCDE_XX.1_run.py --data-execucao AAAA-MM-DD`.
3. O script calcula a janela oficial e salva o CSV pipe-delimited somente em
   `artefatos_local/ocde/entregas/AAAA-MM/`.

### Opção B — Jupyter Notebook no VS Code

1. Crie uma cópia local de `consultas_denodo_template.ipynb`.
2. Siga o guia: [10-jupyter-guia-iniciantes.md](../ambiente/jupyter.md).
3. Use a função `run_query(sql)` para executar qualquer consulta desta documentação
4. O resultado já aparece como tabela e pode ser exportado para CSV com uma linha de código

### Padrão do bloco `parametros`

Todas as consultas começam com este bloco de controle:

```sql
WITH parametros AS (
    SELECT
        CAST('2025-07-01' AS DATE) AS data_inicio,
        CAST('2026-08-31' AS DATE) AS data_fim,
        0 AS incluir_excluidos   -- 0 = só ativos; 1 = inclui excluídos
)
```

O exemplo representa uma execução em setembro/2026. Em produção, não edite
datas manualmente: informe `--data-execucao` e deixe `analysis_window()` calcular
o corte.

Os indicadores I07 e I08 têm um campo adicional:

```sql
        8 as horas_por_dia       -- jornada diária em horas (padrão: 8)
```

### Padrão de desagregação temporal (quando aplicável)

As consultas que apresentam resultado por período seguem duas cadências:

- **2025:** somente T3 e T4, pois a janela oficial começa em 01/07/2025;
- **2026 em diante — PE:** ciclos quadrimestrais Q1, Q2 e Q3;
- **2026 em diante — PT:** ciclos mensais M01 a M12.

O fim da análise é sempre o último dia do mês anterior à execução. Ciclos que
atravessam o corte são truncados em `periodo_fim_efetivo` e recebem
`periodo_status = parcial_no_corte`.

---

## Índice dos indicadores

### Eixo 1 — Trabalho Remoto

Contexto do eixo: [06.1-eixo1.md](06.1-eixo1.md)

| Indicador | Descrição | Nível | Documento |
| --- | --- | --- | --- |
| I01 | Proporção de servidores por regime de trabalho | Institucional e por unidade | [06.1.1-i01.md](06.1.1-i01.md) |

---

### Eixo 2 — Execução

Contexto do eixo: [06.2-eixo2.md](06.2-eixo2.md)

| Indicador | Descrição | Nível | Documento |
| --- | --- | --- | --- |
| I02 | Taxa de cumprimento das entregas | Por unidade | [06.2.1-i02.md](06.2.1-i02.md) |
| I03 | Taxa de cumprimento de metas por entrega | Por entrega | [06.2.2-i03.md](06.2.2-i03.md) |
| I04 | Índice de atingimento de metas | Por unidade (score médio) | [06.2.3-i04.md](06.2.3-i04.md) |

---

### Eixo 3 — Carga de Trabalho

Contexto do eixo: [06.3-eixo3.md](06.3-eixo3.md)

| Indicador | Descrição | Nível | Documento |
| --- | --- | --- | --- |
| I05 | Distribuição das entregas entre os servidores | Por servidor | [06.3.1-i05.md](06.3.1-i05.md) |
| I06 | Grau de responsabilidade pelas entregas | Por entrega | [06.3.2-i06.md](06.3.2-i06.md) |
| I07 | Horas por entrega — planejadas (absolutas) | Por entrega | [06.3.3-i07.md](06.3.3-i07.md) |
| I08 | Proporção de horas por entrega — planejadas (%) | Por entrega | [06.3.4-i08.md](06.3.4-i08.md) |

---

### Eixo 4 — Desempenho e Avaliação

Contexto do eixo: [06.4-eixo4.md](06.4-eixo4.md)

> **Pré-requisito:** execute as consultas de mapeamento do documento do Eixo 4 antes de rodar qualquer indicador deste eixo. Os campos de avaliação variam conforme a versão e configuração do PETRVS instalado.

| Indicador | Descrição | Nível | Documento |
| --- | --- | --- | --- |
| I09 | Média da avaliação do Plano de Trabalho por unidade | Por unidade | [06.4.1-i09.md](06.4.1-i09.md) |
| I10 | Percentual de avaliações com conceito Inadequado (`sequencia = 4`) | Por unidade | [06.4.2-i10.md](06.4.2-i10.md) |
| I11 | Percentual de avaliações com conceito Excepcional (`sequencia = 1`) | Por unidade | [06.4.3-i11.md](06.4.3-i11.md) |
| I12 | Coerência entre avaliação do PT e do PE | Por unidade | [06.4.4-i12.md](06.4.4-i12.md) |

---

## Requisitos técnicos

| Requisito | Afeta |
| --- | --- |
| Denodo VQL (conexao ativa no DBeaver) | Todos os indicadores |
| Datas com `CAST('AAAA-MM-DD' AS DATE)` | Todos os indicadores |
| Prefixo `petrvs_icmbio_` no JDBC/Notebook | Todas as consultas via Python |
| Sem CTE recursiva e sem `DATEDIFF`/`TIMESTAMPDIFF` | I07 e I08 |
| `deleted_at IS NULL`, salvo auditoria explícita | Todos os indicadores |

---

## Estrutura do manual técnico

Cada documento de eixo apresenta:

- Contexto estratégico do eixo e sua relevância para o ICMBio
- Tabelas do PETRVS utilizadas e relacionamentos
- Consultas de mapeamento/auditoria a executar antes dos indicadores
- Relação com os demais eixos
- Limitações conhecidas

Cada documento de indicador apresenta:

1. **Finalidade** — pergunta central respondida
2. **Consulta completa (script Python, sem credenciais)** — pronta para uso no Jupyter/VS Code
3. **Passos da consulta** — explicação de cada bloco/CTE em linguagem simples
4. **Consulta de diagnostico pre-execucao** — QT-01/02/03 e o motivo de cada uma
5. **Como interpretar o resultado** — tabela de colunas + exemplos com unidades reais do ICMBio
