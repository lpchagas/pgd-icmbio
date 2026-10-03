# ocde/ — Extração e Análise dos Indicadores OCDE/ICMBio

Esta pasta reúne os scripts Python que automatizam a extração mensal dos 12 indicadores
do PGD do ICMBio a partir do banco PETRVS, via conexão em tempo real com o Denodo
(plataforma de virtualização de dados do Dataprev/MGI).

Os scripts são **públicos e sanitizados**: não contêm CPF, senhas, caminhos pessoais
nem dados extraídos do PETRVS. As credenciais ficam em um arquivo `.env` local,
que nunca é versionado.

Os módulos compartilhados ficam em `lib/` (raiz do repositório), reutilizáveis por
todas as iniciativas (OCDE, MGI etc.).

---

## O que estes scripts fazem — visão para gestores

Em linguagem de negócio, os scripts realizam três tarefas:

1. **Buscam os dados diretamente no PETRVS** (via Denodo, sem intermediários)
   e organizam os resultados em tabelas CSV prontas para uso no Power BI ou Excel.

2. **Calculam os indicadores automaticamente** para todos os períodos históricos
   (trimestres de 2025, quadrimestres e meses de 2026), poupando o trabalho manual
   de exportar e cruzar planilhas.

3. **Geram relatórios gerenciais em Markdown** com semáforos (🟢 🟡 🔴), rankings
   de unidades, tendências e recomendações interpretativas por eixo.

O resultado final são arquivos CSV salvos em `artefatos_local/ocde/entregas/AAAA-MM/`,
prontos para envio à COCAGE ou importação no Power BI.

---

## Estrutura de pastas

```text
ocde/
  indicadores/          Um script por indicador (IND_OCDE_01 a IND_OCDE_12)
  relatorios/           Módulos para análise e geração de relatórios gerenciais
  diagnosticos/         Template de diagnóstico para investigações pontuais

lib/                    Módulos compartilhados (raiz do repositório)
  denodo_config.py      Leitura do .env e conexão JDBC
  periodos.py           build_periods_pe() e build_periods_pt()
  csv_utils.py          clean(), delimitador pipe, pastas de saída automáticas
  auditoria.py          Verificação automática do CSV gerado
  monthly_runner.py     Motor de execução dos scripts
  docs_sql.py           Extração da SQL canônica dos docs
```

---

## Scripts de indicadores (`indicadores/`)

Cada arquivo `IND_OCDE_XX.1_run.py` extrai um indicador específico e gera um CSV mensal.
São executados uma vez por mês, seguindo o calendário em `docs/indicadores/extracao-mensal.md`.

| Script | Indicador | O que mede | Periodicidade 2026 |
| --- | --- | --- | --- |
| `IND_OCDE_01.1_run.py` | I01 — Regime de Trabalho | Proporção de servidores presencial / híbrido / remoto por unidade | Mensal |
| `IND_OCDE_02.1_run.py` | I02 — Cumprimento de Entregas | % de entregas concluídas em relação às planejadas por unidade | Quadrimestral |
| `IND_OCDE_03.1_run.py` | I03 — Atingimento por Entrega | % de atingimento da meta para cada entrega individualmente | Quadrimestral |
| `IND_OCDE_04.1_run.py` | I04 — Score de Atingimento | Score médio de cumprimento de metas por unidade | Quadrimestral |
| `IND_OCDE_05.1_run.py` | I05 — Distribuição de Entregas | Quantas entregas cada servidor acumula em média por unidade | Mensal |
| `IND_OCDE_06.1_run.py` | I06 — Concentração de Responsabilidade | % de entregas que dependem de um único servidor (risco operacional) | Mensal |
| `IND_OCDE_07.1_run.py` | I07 — Horas por Entrega | Total de horas planejadas para cada entrega | Quadrimestral |
| `IND_OCDE_08.1_run.py` | I08 — Proporção de Horas | % da capacidade horária da unidade consumida por cada entrega | Quadrimestral |
| `IND_OCDE_09.1_run.py` | I09 — Média das Avaliações PT | Nota média do Plano de Trabalho por unidade (escala 1–5) | Mensal |
| `IND_OCDE_10.1_run.py` | I10 — Avaliações Inadequadas | % de servidores com avaliação abaixo do esperado por unidade | Mensal |
| `IND_OCDE_11.1_run.py` | I11 — Avaliações Excepcionais | % de servidores com avaliação excepcional por unidade | Mensal |
| `IND_OCDE_12.1_run.py` | I12 — Coerência PT × PE | % de unidades onde a avaliação individual e a do plano de entrega são coerentes | Quadrimestral |

**Por que dois tipos de periodicidade?**
A partir de 2026, o ICMBio adotou ciclos distintos para os dois instrumentos do PGD:
os Planos de Trabalho (PT) são mensais; os Planos de Entrega (PE) são quadrimestrais.
Os scripts respeitam automaticamente essa bifurcação — sem necessidade de ajuste manual.

---

## Módulos compartilhados (`lib/`)

Estes módulos são a "infraestrutura invisível" usada por todos os scripts de indicadores.
Não precisam ser executados diretamente.

### `denodo_config.py` — Conexão com o banco PETRVS

Lê as credenciais do arquivo `.env` local e estabelece a conexão com o Denodo.
Garante que nenhuma senha seja gravada no código-fonte.
Se as credenciais não estiverem configuradas, o script para imediatamente com uma
mensagem de erro clara antes de tentar qualquer conexão.

### `periodos.py` — Calendário inteligente de períodos

Gera automaticamente a lista de períodos contidos na janela oficial cumulativa, de
01/07/2025 até o último dia do mês anterior à data de execução. A data pode ser
injetada com `--data-execucao AAAA-MM-DD`, garantindo reprodutibilidade. Cada
período inclui `periodo_fim_efetivo` e o status `encerrado` ou
`parcial_no_corte`; períodos iniciados após o corte são excluídos.

Duas funções principais:

- `build_periods_pe()` — para indicadores baseados em Plano de Entrega (I02, I03, I04, I07, I08, I12)
- `build_periods_pt()` — para indicadores baseados em Plano de Trabalho (I01, I05, I06, I09, I10, I11)

### `csv_utils.py` — Exportação segura de CSV

Cuida dos detalhes que corrompem planilhas:

- **Troca quebras de linha internas** (que servidores inserem em descrições de entregas)
  por ` / `, mantendo o texto legível em célula única no Excel.
- **Usa pipe (`|`) como separador** em vez de vírgula ou ponto-e-vírgula, que aparecem
  com frequência nos textos administrativos do PETRVS e corrompem a estrutura do arquivo.
- **Salva com BOM UTF-8** para que o Excel abra os acentos corretamente sem conversão manual.
- **Cria automaticamente** as pastas `artefatos_local/ocde/entregas/AAAA-MM/` e
  `artefatos_local/ocde/diagnosticos/AAAA-MM/` se ainda não existirem.

### `auditoria.py` — Verificação automática do CSV gerado

Após salvar cada CSV, verifica se a estrutura está íntegra:
conta as linhas, confere se todas têm o mesmo número de colunas e emite alertas
no console caso alguma linha esteja mal-formada. É a última linha de defesa antes
de o arquivo ser enviado à COCAGE.

### `monthly_runner.py` — Motor de execução dos scripts

Contém a lógica comum a todos os scripts de indicadores: conexão com Denodo,
execução por período, adição das colunas de metadado de período, salvamento do CSV
e chamada à auditoria. Os scripts `IND_OCDE_XX.1_run.py` delegam toda essa mecânica
ao `monthly_runner`, mantendo-se enxutos e focados apenas na SQL do indicador.

### `docs_sql.py` — Extração da SQL canônica dos documentos

Lê a SQL de referência de cada indicador diretamente dos arquivos `docs/ocde/06.X.X-iXX.md`
e a adapta automaticamente para funcionar via conexão JDBC com o Denodo:

- Adiciona o prefixo obrigatório `petrvs_icmbio_` nos nomes de tabela.
- Substitui funções MySQL incompatíveis pelo equivalente Denodo VQL
  (`DATE()` → `CAST(... AS DATE)`, remoção de `JSON_UNQUOTE()`).

Isso garante que os scripts reflitam sempre a mesma lógica documentada nas fichas
dos indicadores, sem duplicação de código.

---

## Módulos de relatórios (`relatorios/`)

Estes módulos transformam os CSVs gerados pelos scripts de indicadores em relatórios
gerenciais interpretativos (semáforos, rankings, tendências, recomendações).
São usados pelas skills `/relatorio-gerencial`, `/sumario-executivo` e similares.

### `loader.py` — Carregamento dos CSVs

Localiza os CSVs mais recentes em `artefatos_local/ocde/entregas/AAAA-MM/`,
carrega cada indicador como uma tabela estruturada e converte as colunas numéricas
para o tipo correto. Permite filtrar por unidade (ex: "CGOV", "GR3") ou trabalhar
com a visão nacional completa.

### `metricas.py` — Estatísticas por período

Para cada indicador e período, calcula: média, mediana, percentis P25 e P75,
mínimo, máximo e variação percentual em relação ao período anterior.
Esses valores alimentam as tabelas de tendência dos relatórios gerenciais.

### `classificador.py` — Semáforos por indicador

Aplica os limiares definidos pela CGOV/ICMBio para classificar cada indicador como
🟢 Verde, 🟡 Amarelo ou 🔴 Vermelho, tanto por unidade quanto para a média nacional.

Limiares configurados:

| Indicador | Verde | Amarelo | Lógica |
| --- | --- | --- | --- |
| I02 — Cumprimento | ≥ 80% | ≥ 60% | Maior = melhor |
| I04 — Score de atingimento | ≥ 80% | ≥ 60% | Maior = melhor |
| I06 — Concentração | ≤ 30% | ≤ 50% | Menor = melhor |
| I09 — Média avaliações | ≥ 3,5 | ≥ 2,5 | Maior = melhor |
| I10 — Inadequados | ≤ 5% | ≤ 10% | Menor = melhor |
| I11 — Excepcionais | ≥ 15% | ≥ 5% | Maior = melhor |
| I12 — Coerência PT×PE | ≥ 90% | ≥ 70% | Maior = melhor |

### `insights_engine.py` — Geração de insights interpretativos

Produz automaticamente frases interpretativas em português para cada eixo e para
cruzamentos entre indicadores. Exemplos do que é gerado:

- "Em Q1-2026, a modalidade dominante é **Teletrabalho Parcial** (62,3% dos servidores)."
- "⚠️ 14 unidades com taxa de cumprimento abaixo de 60% — atenção prioritária."
- "🔴 Risco combinado (I02 × I06): baixa execução nacional E alta concentração
  de responsabilidades em 7 unidades. Prioridade máxima."

Também gera recomendações contextualizadas ao semáforo atual de cada eixo.

### `report_builder.py` — Montagem do documento final

Combina todos os blocos (cabeçalho, painel de semáforos, tabelas de métricas,
rankings, insights, recomendações e rodapé) em um único documento Markdown
pronto para leitura pelos gestores ou exportação para PDF.

---

## Template de diagnóstico (`diagnosticos/`)

O arquivo `IND_OCDE_XX.4_diagnostico_template.py` é um modelo de script para investigações
pontuais, usado quando a equipe CGOV retorna observações após a validação manual no
PETRVS (artefato A4 do protocolo de validação).

Cada diagnóstico gera CSVs intermediários salvos em `artefatos_local/ocde/diagnosticos/`,
separados dos CSVs de entrega, para uso interno sem risco de envio acidental à COCAGE.

---

## Como executar

### Pré-requisito: configurar o arquivo `.env`

Antes da primeira execução, copie `.env.example` para `.env` na raiz do projeto
e preencha as quatro variáveis:

```text
DENODO_USER=seu_cpf_aqui
DENODO_PASSWORD=sua_senha_aqui
DENODO_DRIVER_PATH=C:\Users\SEU_USUARIO\AppData\Roaming\DBeaverData\drivers\remote\drivers\jdbc\9\denodo-vdp-jdbcdriver.jar
JAVA_HOME=C:\Program Files\DBeaver\jre
```

Guia detalhado: `docs/ambiente/jupyter.md`

### Executar um indicador

O caminho oficial é o ciclo dos pilotos, com data de execução explícita (ver
[guia de extração mensal](../docs/indicadores/extracao-mensal.md)):

```bash
python -m tools.executar_pilotos --capacidade I02 --data-execucao AAAA-MM-DD                          # simula
python -m tools.executar_pilotos --capacidade I02 --data-execucao AAAA-MM-DD --modo real --validar
```

Chamado diretamente (só para diagnóstico técnico), o script conecta ao Denodo,
consulta o universo nacional para cada período da janela, adiciona as colunas de
metadado (tipo de ciclo, rótulo, datas, status, duração) e salva o CSV legado em
`artefatos_local/ocde/entregas/AAAA-MM/`. Sempre informe a data; o script não tem
modo de simulação, e `--dry-run` ou `--help` executam a extração real:

```bash
python ocde/indicadores/IND_OCDE_02.1_run.py --data-execucao AAAA-MM-DD
```

### Especificar a pasta de destino

```bash
python ocde/indicadores/IND_OCDE_02.1_run.py --data-execucao AAAA-MM-DD --month 2026-06
```

Por padrão, a pasta é o mês da data de execução. Use `--month` para gerar em uma
pasta específica; a janela de análise continua definida por `--data-execucao`.

---

## Periodicidade por indicador

| Instrumento | Indicadores | Ciclo 2025 | Ciclo 2026 |
| --- | --- | --- | --- |
| Plano de Entrega (PE) | I02, I03, I04, I07, I08, I12 | Trimestral (T1–T4) | Quadrimestral (Q1–Q3) |
| Plano de Trabalho (PT) | I01, I05, I06, I09, I10, I11 | Trimestral (T1–T4) | Mensal (M01–M12) |

Calendário completo de execução mensal: `docs/indicadores/extracao-mensal.md`

---

## Onde os arquivos são salvos

| Tipo de arquivo | Pasta | Quem usa |
| --- | --- | --- |
| CSVs de indicadores (entrega) | `artefatos_local/ocde/entregas/AAAA-MM/` | COCAGE, Power BI |
| CSVs diagnósticos (uso interno) | `artefatos_local/ocde/diagnosticos/AAAA-MM/` | Equipe técnica |
| Scripts de diagnóstico (A4) | `artefatos_local/ocde/diagnosticos/` | Equipe técnica |
| Relatórios de validação (A5) | `artefatos_local/validacao/` | CGOV, auditoria |

A pasta `artefatos_local/` é **exclusivamente local e privada** — está no `.gitignore` e
sincronizada via OneDrive. Nunca é versionada no GitHub.

---

## Regras de segurança

- Nunca grave credenciais (CPF, senha, token) nesta pasta.
- Nunca salve CSV, PDF ou relatório dentro de `ocde/` — use `artefatos_local/`.
- Antes de qualquer `git push`, execute o checklist em `docs/ambiente/seguranca-publicacao.md`.
- Os scripts desta pasta são seguros para compartilhar com outros órgãos da APF
  que utilizem PETRVS + Denodo — esta é uma das finalidades do repositório.
