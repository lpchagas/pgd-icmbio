# Referência técnica — projeto `pgd-ocde-icmbio`

**Última revisão de escopo:** 23.08.2026
**Classificação:** referência técnica de integração; não integra a decisão Q5 sobre fontes
institucionais do PGD

Este documento sintetiza, para uso no `pgd-agente-icmbio`, os padrões relevantes já validados no
projeto de indicadores `pgd-ocde-icmbio` (`C:\Projetos\pgd-icmbio`, tratado como referência
somente leitura). Cada informação abaixo cita o arquivo de origem. **Nenhuma credencial, senha,
host real ou string de conexão foi copiada** — apenas nomes de variáveis de ambiente e padrões de
código. As credenciais reais do projeto antigo residem exclusivamente no seu `CLAUDE.md` (arquivo
gitignored, não replicado aqui); o `pgd-agente-icmbio` deve configurar as suas próprias via `.env`
local, seguindo o mesmo padrão de nomes.

Para normas, guias e orientações de negócio, use o catálogo em
[`docs/referencias-pgd/README.md`](../../../docs/referencias-pgd/README.md). Para a decisão de cadastro e RAG,
use [`docs/governanca-projeto/fontes-institucionais.md`](../../../docs/governanca-projeto/fontes-institucionais.md).

---

## 1. Padrão de conexão ao Denodo (via Jupyter, sem credenciais)

**Fonte:** `consultas_denodo_template.ipynb` (raiz do `pgd-ocde-icmbio`) — a variante pública sem
credenciais do notebook de consulta.

O padrão usa `python-dotenv` para carregar configuração de um `.env` local, e `jpype` para abrir
uma conexão JDBC direta ao Denodo (sem driver Python nativo — o Denodo expõe um driver JDBC Java).

Variáveis de ambiente usadas (nomes, não valores):

| Variável | Papel |
| --- | --- |
| `JAVA_HOME` | Caminho do JRE usado para iniciar a JVM (ex.: JRE embutido do DBeaver) |
| `DENODO_DRIVER_PATH` | Caminho local do `.jar` do driver JDBC do Denodo |
| `DENODO_HOST` | Host do servidor Denodo |
| `DENODO_PORT` | Porta (443 no ambiente do ICMBio) |
| `DENODO_DATABASE` | Nome da base virtual (`petrvs_icmbio` no caso do ICMBio) |
| `DENODO_USER` / `DENODO_PASSWORD` | Credenciais de acesso |

Estrutura da função central (reproduzida em forma de padrão, não de cópia literal):

```python
def run_query(sql: str) -> pd.DataFrame:
    # abre conexão JDBC via jpype.JClass("java.sql.DriverManager")
    # executa a query, lê metadados de coluna, monta um DataFrame pandas
    # fecha statement e conexão em bloco finally
    ...
```

**Recomendação para o `pgd-agente-icmbio`:** o módulo `agente/dados/` deve replicar esse padrão
(`.env` + `jpype` + função central de query), mas encapsulado como uma **tool** que o agente pode
chamar (ex.: `consultar_indicador(indicador, periodo, unidade)`), em vez de uma célula de notebook
de uso manual.

---

## 2. Os 12 indicadores OCDE/PGD do ICMBio

**Fonte:** `CLAUDE.md` (seção 6) e `docs/ocde/06-indicadores-ocde-mysql.md` do `pgd-ocde-icmbio`.

| Ind | Descrição | Eixo |
| --- | --- | --- |
| I01 | Proporção por regime de trabalho (presencial/híbrido/remoto) | 1 — Trabalho Remoto |
| I02 | Taxa de cumprimento das entregas (por unidade) | 2 — Execução |
| I03 | Taxa de cumprimento por entrega | 2 — Execução |
| I04 | Score médio de atingimento de metas | 2 — Execução |
| I05 | Distribuição de entregas por servidor | 3 — Carga de Trabalho |
| I06 | Grau de responsabilidade por entrega | 3 — Carga de Trabalho |
| I07 | Horas por entrega — planejadas (absolutas) | 3 — Carga de Trabalho |
| I08 | Proporção de horas por entrega (%) | 3 — Carga de Trabalho |
| I09 | Média da avaliação do Plano de Trabalho por unidade | 4 — Desempenho e Avaliação |
| I10 | Percentual de avaliações inadequadas | 4 — Desempenho e Avaliação |
| I11 | Percentual de avaliações excepcionais | 4 — Desempenho e Avaliação |
| I12 | Coerência entre avaliação do Plano de Trabalho e do Plano de Entregas | 4 — Desempenho e Avaliação |

Cada indicador tem uma ficha técnica dedicada em `docs/ocde/06.X.X-iXX.md` no projeto antigo, com
a query SQL canônica, tabelas-base e decisões metodológicas. Essas fichas são a fonte natural para
indexação RAG na Fase 3 do `pgd-agente-icmbio` (junto com os 4 `.md` de skills).

---

## 3. Convenções de nomenclatura e organização

**Fonte:** `CLAUDE.md` (seções 4, 5 e 10) do `pgd-ocde-icmbio`.

- Prefixo obrigatório de tabela/view: `petrvs_icmbio_<nome>` (ex.:
  `petrvs_icmbio_planos_entregas_entregas`).
- Soft-delete: toda tabela em `FROM`/`JOIN` deve filtrar `deleted_at IS NULL`.
- Exportação de dados: delimitador `|` (pipe), encoding `utf-8-sig`, função `clean()` para
  normalizar quebras de linha em campos de texto.
- Padrão de script de extração: `IND_XX.1_run.py` — script Python com JVM/JDBC, função
  `build_periods_pe()`/`build_periods_pt()` para gerar os períodos de análise, e exportação CSV
  padronizada.
- Campos críticos recorrentes: `progresso_esperado`/`progresso_realizado` (meta planejada vs.
  executada), `forca_trabalho` (dedicação do servidor em %), `(6 - sequencia)` para score de
  avaliação (nunca usar `nota` ou `JSON_UNQUOTE` diretamente — bug histórico já corrigido no
  projeto antigo).

**Relevância para o `pgd-agente-icmbio`:** se a tool `consultar_indicador()` (Seção 1) algum dia
gerar SQL dinamicamente a partir da pergunta do usuário, essas convenções (prefixo de tabela,
soft-delete, escala de avaliação) precisam ser respeitadas — o risco de indicador incorreto por
não aplicar `deleted_at IS NULL` ou usar a escala errada já se materializou no projeto antigo (ver
"Bugs históricos corrigidos" no `CLAUDE.md` dele).

---

## 4. Restrições de sintaxe do Denodo VQL

**Fonte:** `CLAUDE.md` (seção 5) do `pgd-ocde-icmbio`.

Relevante caso o agente do `pgd-agente-icmbio` venha a gerar ou validar SQL dinamicamente:

- `DATE()` não existe no Denodo VQL — usar `CAST('...' AS DATE)`.
- Não há CTEs recursivas nem `SET SESSION cte_max_recursion_depth`.
- `DIFF()`, `DATEDIFF()`, `TIMESTAMPDIFF()` não existem — diferença de datas é feita por
  subtração direta (`CAST(d1 AS DATE) - CAST(d2 AS DATE)`).
- Divisão inteira: sempre multiplicar por `100.0` (float) antes de dividir, para evitar
  truncamento no JDBC do Denodo.

---

## 5. O que NÃO foi trazido para este documento

- Nenhuma credencial (usuário, senha, host completo) do ambiente Denodo do ICMBio.
- Nenhum dado operacional ou CSV do projeto antigo.
- Nenhum código-fonte copiado literalmente — apenas padrões descritos em prosa/pseudocódigo.

Para reconfigurar o acesso ao Denodo no `pgd-agente-icmbio`, preencha o `.env` local (ver
`.env.example` e o capítulo v6 de operação) com as credenciais fornecidas pelo Dataprev
para este projeto — não reutilize as do `pgd-ocde-icmbio` sem confirmar com quem administra o
acesso se isso é permitido.
