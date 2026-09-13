# Situação dos Planos de Trabalho por Unidade — método de extração

**Data:** 08 de setembro de 2026
**Fonte:** banco `petrvs_icmbio` via Denodo (MGI/Dataprev) — introspecção e validação em tempo real
**Script:** [`gestao/PT_STATUS.1_run.py`](../gestao/PT_STATUS.1_run.py)
**Público:** chefias de unidade, CGOV, COCAGE

---

## 1. Resposta curta

**Sim.** O Denodo expõe o status de situação de cada Plano de Trabalho, o servidor
responsável, a unidade organizacional **e a data/hora da última mudança de status,
com o nome de quem a executou**.

A ressalva importante é que **os cinco status de negócio não estão em um único
campo**. O PETRVS distribui o ciclo de vida do PT em duas camadas, e o status
"aguardando avaliação" não existe em `planos_trabalhos.status` — ele vive na
tabela de consolidações mensais. Ler só o campo `status` produziria um painel
que nunca mostra a fila de avaliação da chefia, que é justamente a pendência
mais acionável.

---

## 2. O modelo de status real do PETRVS

### Camada 1 — ciclo de vida do plano (`planos_trabalhos.status`)

```text
INCLUIDO ──► AGUARDANDO_ASSINATURA ──► ATIVO ──► CONCLUIDO
                                         └──► SUSPENSO / CANCELADO
```

Distribuição medida em 08.09.2026 (`deleted_at IS NULL`, 19.566 planos):

| Código | Planos | Leitura de negócio |
| --- | ---: | --- |
| CONCLUIDO | 16.177 | Plano encerrado (99,9% com `avaliado_at` preenchido) |
| ATIVO | 1.978 | Em execução |
| CANCELADO | 683 | Cancelado |
| AGUARDANDO_ASSINATURA | 421 | TCR pendente de assinatura |
| INCLUIDO | 306 | Rascunho, ainda não submetido |
| SUSPENSO | 3 | Suspenso |

> **Achado:** o valor `AVALIADO` está previsto na enumeração do PETRVS, mas
> **não ocorre** em `planos_trabalhos.status` nesta base. A avaliação é registrada
> na camada 2 e refletida no plano por `avaliado_at` + `status = CONCLUIDO`.

### Camada 2 — ciclo de avaliação de cada período mensal (`planos_trabalhos_consolidacoes.status`)

```text
INCLUIDO (período aberto) ──► CONCLUIDO (servidor entregou) ──► AVALIADO (chefia avaliou)
```

| Código | Períodos | Leitura de negócio |
| --- | ---: | --- |
| AVALIADO | 29.425 | Ciclo do período fechado |
| INCLUIDO | 4.161 | Período em preenchimento pelo servidor |
| CONCLUIDO | 887 | **Aguardando avaliação — fila da chefia** |

### Mapeamento para os cinco status da pergunta

| Status de negócio | Como é obtido |
| --- | --- |
| Rascunho | `planos_trabalhos.status = 'INCLUIDO'` |
| Aguardando assinatura | `planos_trabalhos.status = 'AGUARDANDO_ASSINATURA'` |
| Em execução | `planos_trabalhos.status = 'ATIVO'` **e** nenhuma consolidação `CONCLUIDO` |
| **Aguardando avaliação** | existe consolidação com `status = 'CONCLUIDO'` (plano `ATIVO` ou `CONCLUIDO`) |
| Concluído | `planos_trabalhos.status = 'CONCLUIDO'` e todas as consolidações `AVALIADO` |

A camada 2 tem **precedência** na derivação: um período já entregue e não avaliado
é a pendência que exige ação, mesmo com o plano ainda `ATIVO`.

---

## 3. Data e hora da última mudança de status — é possível

A tabela **`status_justificativas`** é uma trilha de auditoria de transições de
status. Cada linha registra uma mudança:

| Coluna | Uso |
| --- | --- |
| `codigo` | o status para o qual transitou (mesma enumeração das camadas 1 e 2) |
| `created_at` | **data e hora da transição** |
| `usuario_id` | quem executou a transição |
| `justificativa` | texto livre (ex.: "Plano de Trabalho repactuado", "Registrada a assinatura do servidor: …") |
| `plano_trabalho_id` / `plano_trabalho_consolidacao_id` / `plano_entrega_id` / `atividade_id` | a que artefato a transição se refere |

**Cobertura medida:** 19.329 de 19.566 planos ativos têm trilha (**98,8%**).
Os 237 sem trilha são **todos** `INCLUIDO` — rascunhos que nunca transitaram.

**Consistência:** para 19.179 planos o último código da trilha é idêntico ao campo
`status` da tabela. As divergências são residuais e explicáveis:

| Situação | Planos | Causa |
| --- | ---: | --- |
| `status = CONCLUIDO`, trilha termina em `ATIVO` | 185 | encerramento automático por data, sem ação de usuário registrada |
| `status = SUSPENSO`, trilha termina em `ATIVO` | 2 | idem |
| `status = ATIVO`, trilha termina em `CONCLUIDO` | 2 | reabertura/repactuação |

**Regra adotada no script:** o campo `planos_trabalhos.status` é a verdade sobre
*qual* é o status; a trilha é consultada **filtrada pelo código igual ao status
atual** (`MAX(created_at)`) para responder *desde quando*. Quando não há trilha
para aquele código, cai no fallback `planos_trabalhos.updated_at`. A coluna
`origem_data_status` no CSV declara qual das duas fontes foi usada em cada linha,
para que ninguém trate uma estimativa como registro de auditoria.

> `petrvs_icmbio_audits` (Laravel Auditing, com `old_values`/`new_values` em JSON)
> também guarda o histórico completo e foi avaliada. Foi descartada como fonte
> primária: exigiria parse de JSON em LONGVARCHAR — prática vedada pela §6.5 do
> [07.1-estrutura-banco-dados.md](07.1-estrutura-banco-dados.md) — e tem volume
> muito maior (134.574 eventos `updated` só de `PlanoTrabalho`). Fica como fonte
> secundária para auditorias pontuais que precisem do valor anterior do campo.

---

## 4. O método de extração

### Como rodar

```powershell
cd "C:\Projetos\pgd-ocde-icmbio"

# Uma unidade
python gestao/PT_STATUS.1_run.py --unidade CGGP --data-execucao 2026-09-13

# Unidade + toda a hierarquia subordinada (até 3 níveis)
python gestao/PT_STATUS.1_run.py --unidade CGGP --incluir-subordinadas

# Várias unidades
python gestao/PT_STATUS.1_run.py --unidade CGGP,DIPLAN

# Instituto inteiro
python gestao/PT_STATUS.1_run.py --todas

# Incluir também os planos já encerrados (CONCLUIDO/CANCELADO)
python gestao/PT_STATUS.1_run.py --unidade CGGP --incluir-encerrados
```

Por padrão o script traz apenas os **status abertos** (`INCLUIDO`,
`AGUARDANDO_ASSINATURA`, `ATIVO`, `SUSPENSO`) — os que exigem ação de alguém.

**Desempenho observado em 08.09.2026:** cerca de 10 segundos para o instituto inteiro
(2.708 planos abertos, 376 unidades). Os valores são um retrato histórico, não um
baseline fixo. Não requer datamart nem ETL — consulta direta ao Denodo.

### Restrições Denodo tratadas

- **Sem CTE recursiva:** a expansão da hierarquia de unidades (`unidade_pai_id`)
  é feita por iteração em Python, uma consulta por nível (`expandir_subordinadas`).
- **Sem `DATEDIFF`:** o cálculo de `dias_no_status_atual` é feito em Python sobre
  o timestamp retornado.
- **`deleted_at IS NULL`** aplicado em todas as tabelas do FROM/JOIN.

### Saídas

Dois CSVs pipe-delimited, `utf-8-sig`, em
`artefatos_local/gestao/YYYY-MM/`:

**`PT_STATUS.2_detalhe_<escopo>_AAAAMMDD_HHMM.csv`** — uma linha por plano:

| Coluna | Conteúdo |
| --- | --- |
| `unidade_sigla`, `unidade_nome`, `mesogrupo`, `unidade_pai_sigla` | localização organizacional |
| `servidor_nome`, `servidor_email` | **quem procurar** |
| `plano_numero`, `plano_inicio`, `plano_fim` | identificação do PT |
| `status_codigo` | código bruto do banco (camada 1) |
| `status_negocio` | rótulo derivado das duas camadas |
| `data_ultima_mudanca_status` | **data e hora da última transição** |
| `origem_data_status` | `trilha_status_justificativas` ou `fallback_updated_at` |
| `dias_no_status_atual` | há quantos dias está parado |
| `status_alterado_por` | quem executou a última transição |
| `periodos_aguardando_avaliacao` | períodos entregues e não avaliados |
| `periodos_em_preenchimento`, `periodos_avaliados`, `periodos_total` | composição do PT |
| `periodo_pendente_fim` | fim do período mais recente pendente de avaliação |
| `acao_sugerida` | frase pronta dizendo o que fazer e com quem |

**`PT_STATUS.2_painel_<escopo>_AAAAMMDD_HHMM.csv`** — contagem por unidade × status,
para Power BI ou visão rápida da chefia.

---

## 5. Retrato histórico nacional em 08.09.2026 (planos abertos)

| Status de negócio | Planos |
| --- | ---: |
| Em execução | 1.297 |
| **Aguardando avaliação** | **684** |
| Aguardando assinatura | 417 |
| Rascunho | 307 |
| Suspenso | 3 |
| **Total** | **2.708** em 376 unidades |

Os 684 planos aguardando avaliação são a fila acumulada das chefias — o número
mais acionável do painel, e invisível para quem lê apenas `planos_trabalhos.status`.

---

## 6. Cuidados

- O CSV de detalhe contém **nome e e-mail funcional de servidores**. A saída fica
  em `artefatos_local/`, que está no `.gitignore` — **nunca versionar**.
- O script não contém credenciais: lê do `.env` local via `lib/denodo_config.py`.
- A coluna `mesogrupo` usa planilhas organizacionais locais opcionais, cujos formatos
  estão descritos em `lib/estrutura_organizacional.py`; na ausência delas o valor sai
  como `Não mapeado` e o restante do CSV continua íntegro.
- `dias_no_status_atual` calculado sobre `fallback_updated_at` mede a última
  alteração **de qualquer campo** do plano, não necessariamente do status. Filtrar
  por `origem_data_status` quando o rigor da data importar.
