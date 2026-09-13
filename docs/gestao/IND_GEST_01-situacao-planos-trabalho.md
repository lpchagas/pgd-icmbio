# G01 — Situação dos Planos de Trabalho

| Campo | Valor |
| --- | --- |
| Código lógico | `G01` (até 13.09.2026: `PT_STATUS`, ainda aceito como alias na CLI) |
| Família | Gestão — [`gestao/`](../../gestao/README.md) |
| Script A1 | [`gestao/IND_GEST_01/IND_GEST_01.1_run.py`](../../gestao/IND_GEST_01/IND_GEST_01.1_run.py) |
| Artefatos | `IND_GEST_01.2_detalhe_*`, `IND_GEST_01.2_painel_*`, `IND_GEST_01.{3,4,5}_*` |
| `formula_version` | **4.0.0** |
| Decisões | D14 (identificação nominal), D17 (namespace e correções, pendente de ratificação CGOV) |
| Estado de validação | `HOMOLOGACAO_INICIAL_PENDENTE` |
| Lente temporal | `operacional`: fotografia na data de execução |
| Público | Chefias de unidade e CGOV |
| Fonte | `petrvs_icmbio` via Denodo (MGI/Dataprev), consulta direta |

---

## 1. Finalidade

O G01 responde, para cada unidade, a duas perguntas da chefia: **em que ponto do
fluxo está cada Plano de Trabalho da equipe** e **com quem falar para destravá-lo**.

É um indicador tático de acompanhamento, não de desempenho. Não mede se o servidor
cumpriu as entregas, e sim onde o processo está parado: rascunho não enviado, termo
sem assinatura, período entregue que a chefia ainda não avaliou. Por isso usa a
data do dia, e não a janela cumulativa dos indicadores OCDE, e traz identificação
nominal nos produtos internos da unidade (D14).

---

## 2. Modelo de status do PETRVS — duas camadas

O PETRVS não guarda os status de negócio num único campo. O ciclo de vida do PT fica
distribuído em duas tabelas.

### Camada 1 — ciclo de vida do plano (`planos_trabalhos.status`)

```text
INCLUIDO ──► AGUARDANDO_ASSINATURA ──► ATIVO ──► CONCLUIDO
                                         └──► SUSPENSO / CANCELADO
```

| Código | Planos em 08.09.2026 | Leitura de negócio |
| --- | ---: | --- |
| CONCLUIDO | 16.177 | Plano encerrado |
| ATIVO | 1.978 | Em execução |
| CANCELADO | 683 | Cancelado |
| AGUARDANDO_ASSINATURA | 421 | Termo pendente de assinatura |
| INCLUIDO | 306 | Rascunho, ainda não submetido |
| SUSPENSO | 3 | Suspenso |

O valor `AVALIADO` está previsto na enumeração do PETRVS, mas **não ocorre** em
`planos_trabalhos.status` nesta base.

### Camada 2 — avaliação de cada período mensal (`planos_trabalhos_consolidacoes.status`)

```text
INCLUIDO (período aberto) ──► CONCLUIDO (servidor entregou) ──► AVALIADO (chefia avaliou)
```

| Código | Períodos em 08.09.2026 | Leitura de negócio |
| --- | ---: | --- |
| AVALIADO | 29.425 | Ciclo do período fechado |
| INCLUIDO | 4.161 | Período em preenchimento pelo servidor |
| CONCLUIDO | 887 | **Aguardando avaliação: fila da chefia** |

"Aguardando avaliação" **não existe** em `planos_trabalhos.status`. Um painel que
lesse só esse campo nunca mostraria a fila de avaliação, que é a pendência mais
acionável.

---

## 3. Regra de derivação do `status_negocio`

A camada 2 tem precedência: um período já entregue e não avaliado é a pendência que
exige ação, mesmo com o plano ainda `ATIVO`.

| Status de negócio | Condição |
| --- | --- |
| **Aguardando avaliação** | plano `ATIVO` ou `CONCLUIDO` **e** ao menos uma consolidação `CONCLUIDO` |
| Rascunho | plano `INCLUIDO` |
| Aguardando assinatura | plano `AGUARDANDO_ASSINATURA` |
| Em execução | plano `ATIVO` sem consolidação `CONCLUIDO` |
| Suspenso | plano `SUSPENSO`, mesmo com período pendente |
| Concluído | plano `CONCLUIDO` sem consolidação `CONCLUIDO` (só com `--incluir-encerrados`) |
| Cancelado | plano `CANCELADO` (só com `--incluir-encerrados`) |

Duas precisões registradas na D17:

- **"Concluído" não exige que todas as consolidações estejam `AVALIADO`.** Basta não
  haver período aguardando avaliação. Em 13.09.2026, 16 planos concluídos tinham
  período ainda `INCLUIDO` (nunca enviado) e aparecem como "Concluído" (F6).
- **Plano suspenso continua "Suspenso"** mesmo com período pendente: a suspensão é o
  fato a tratar primeiro. Nenhum caso em 13.09.2026 (F9).
- Planos `INCLUIDO` ou `AGUARDANDO_ASSINATURA` com consolidação `CONCLUIDO` (3 e 2
  casos em 13.09.2026) são inconsistências do PETRVS e seguem o status do plano.

---

## 4. Universo e filtros

**Universo padrão** (sem `--incluir-encerrados`):

- planos com status aberto: `INCLUIDO`, `AGUARDANDO_ASSINATURA`, `ATIVO`, `SUSPENSO`;
- **mais** planos `CONCLUIDO` que ainda têm período aguardando avaliação (D17/F1).

O PETRVS encerra planos automaticamente quando a vigência termina. Antes da D17, esse
encerramento tirava do painel planos cujo último período ainda esperava a avaliação
da chefia, embora a própria regra de derivação os classificasse como "Aguardando
avaliação". Em 13.09.2026 eram 7 planos em 6 unidades.

**Demais condições:**

- `deleted_at IS NULL` no plano, na unidade, no servidor, nas consolidações e na
  trilha;
- a unidade e o servidor do plano precisam estar ativos (INNER JOIN), tanto no A1
  quanto no oracle (D17/F5);
- **exceção declarada:** o autor da última transição (`status_alterado_por`) é lido
  sem filtro de `deleted_at`, porque autoria histórica é fato de auditoria e continua
  valendo se o usuário foi desativado depois (D17/F4).

**Escopo por unidade:** `--unidade` (repetível ou separado por vírgula), `--todas`, ou
`--incluir-subordinadas` com `--niveis N` (padrão 3). O Denodo não tem CTE recursiva,
então a hierarquia é expandida em Python, uma consulta por nível. Quando a expansão
para antes de esgotar a hierarquia, o script emite aviso; há 5 unidades no 4º nível
abaixo da DIPLAN (D17/F10).

---

## 5. Data da última mudança de status

A tabela **`status_justificativas`** é a trilha de auditoria das transições:

| Coluna | Uso |
| --- | --- |
| `codigo` | status para o qual o artefato transitou |
| `created_at` | data e hora da transição |
| `usuario_id` | quem executou |
| `plano_trabalho_id` / `plano_trabalho_consolidacao_id` / `plano_entrega_id` / `atividade_id` | artefato a que a transição se refere |

**Regra:** `planos_trabalhos.status` diz *qual* é o status; a trilha, filtrada pelo
código igual ao status atual (`MAX(created_at)`), diz *desde quando*. Sem trilha para
aquele código, vale `planos_trabalhos.updated_at`. A coluna `origem_data_status`
declara a fonte usada em cada linha.

| Medida | Valor |
| --- | --- |
| Cobertura da trilha (08.09.2026) | 19.329 de 19.566 planos (98,8%); os 237 sem trilha são todos `INCLUIDO` |
| Último código da trilha igual ao `status` | 19.179 planos; divergências residuais por encerramento automático (185), suspensão (2) e reabertura (2) |
| Linhas da trilha de PT que referenciam também consolidação, PE ou atividade (13.09.2026) | **0** de 143.548 (D17/F2: sem risco de datar o plano com transição de período) |
| Empates de (plano, código, `created_at`) | **140** grupos (D17/F3) |

Os empates duplicavam o plano quando o responsável era buscado com uma segunda junção
na trilha bruta. Desde a D17, o responsável vem de um CTE agregado por
(plano, código, data) e o script **aborta** se a consulta devolver o mesmo plano
duas vezes.

`petrvs_icmbio_audits` (Laravel Auditing) também guarda o histórico, mas foi
descartada como fonte primária: exigiria parse de JSON em LONGVARCHAR, vedado pela
§6.5 do [07.1](../07.1-estrutura-banco-dados.md), e tem volume muito maior.

---

## 6. Consulta (Denodo VQL)

O script substitui `{filtro_status}` e `{filtro_unidade}`. No universo padrão,
`{filtro_status}` é:

```sql
AND (pt.status IN ('INCLUIDO', 'AGUARDANDO_ASSINATURA', 'ATIVO', 'SUSPENSO')
     OR (pt.status = 'CONCLUIDO' AND c.qtd_aguardando_avaliacao > 0))
```

```sql
WITH trilha AS (
    SELECT sj.plano_trabalho_id AS pid,
           sj.codigo            AS cod,
           MAX(sj.created_at)   AS dt
    FROM petrvs_icmbio_status_justificativas sj
    WHERE sj.deleted_at IS NULL
      AND sj.plano_trabalho_id IS NOT NULL
    GROUP BY sj.plano_trabalho_id, sj.codigo
),
responsavel AS (
    SELECT sj.plano_trabalho_id AS pid,
           sj.codigo            AS cod,
           sj.created_at        AS dt,
           MAX(sj.usuario_id)   AS usuario_id
    FROM petrvs_icmbio_status_justificativas sj
    WHERE sj.deleted_at IS NULL
      AND sj.plano_trabalho_id IS NOT NULL
    GROUP BY sj.plano_trabalho_id, sj.codigo, sj.created_at
),
consolidacao AS (
    SELECT c.plano_trabalho_id AS pid,
           SUM(CASE WHEN c.status = 'CONCLUIDO' THEN 1 ELSE 0 END) AS qtd_aguardando_avaliacao,
           SUM(CASE WHEN c.status = 'INCLUIDO'  THEN 1 ELSE 0 END) AS qtd_periodos_abertos,
           SUM(CASE WHEN c.status = 'AVALIADO'  THEN 1 ELSE 0 END) AS qtd_periodos_avaliados,
           COUNT(*)                                                AS qtd_periodos_total,
           MAX(CASE WHEN c.status = 'CONCLUIDO' THEN c.data_fim END) AS periodo_pendente_fim
    FROM petrvs_icmbio_planos_trabalhos_consolidacoes c
    WHERE c.deleted_at IS NULL
    GROUP BY c.plano_trabalho_id
)
SELECT
    pt.id                                   AS plano_trabalho_id,   -- só para checar unicidade; não é persistido
    u.sigla                                 AS unidade_sigla,
    u.nome                                  AS unidade_nome,
    up.sigla                                AS unidade_pai_sigla,
    pt.usuario_id                           AS id_servidor,
    us.nome                                 AS servidor_nome,
    pt.numero                               AS plano_numero,
    CAST(pt.data_inicio AS DATE)            AS plano_inicio,
    CAST(pt.data_fim AS DATE)               AS plano_fim,
    pt.status                               AS status_codigo,
    t.dt                                    AS status_desde_trilha,
    pt.updated_at                           AS plano_updated_at,
    pt.avaliado_at                          AS plano_avaliado_at,
    COALESCE(c.qtd_aguardando_avaliacao, 0) AS periodos_aguardando_avaliacao,
    COALESCE(c.qtd_periodos_abertos, 0)     AS periodos_em_preenchimento,
    COALESCE(c.qtd_periodos_avaliados, 0)   AS periodos_avaliados,
    COALESCE(c.qtd_periodos_total, 0)       AS periodos_total,
    c.periodo_pendente_fim                  AS periodo_pendente_fim,
    resp.nome                               AS status_alterado_por
FROM petrvs_icmbio_planos_trabalhos pt
JOIN petrvs_icmbio_unidades  u  ON u.id  = pt.unidade_id AND u.deleted_at IS NULL
JOIN petrvs_icmbio_usuarios  us ON us.id = pt.usuario_id AND us.deleted_at IS NULL
LEFT JOIN petrvs_icmbio_unidades up ON up.id = u.unidade_pai_id AND up.deleted_at IS NULL
LEFT JOIN trilha t ON t.pid = pt.id AND t.cod = pt.status
LEFT JOIN responsavel r ON r.pid = t.pid AND r.cod = t.cod AND r.dt = t.dt
LEFT JOIN petrvs_icmbio_usuarios resp ON resp.id = r.usuario_id   -- exceção declarada (F4)
LEFT JOIN consolidacao c ON c.pid = pt.id
WHERE pt.deleted_at IS NULL
  {filtro_status}
  {filtro_unidade}
ORDER BY u.sigla, us.nome, pt.numero
```

A fonte de verdade é a constante `SQL_IND_GEST_01` do script; este bloco é cópia para
leitura.

**Restrições Denodo tratadas:** sem CTE recursiva (hierarquia iterada em Python); sem
`DATEDIFF` (dias no status calculados em Python).

---

## 7. Como executar

```powershell
cd "C:\Projetos\pgd-ocde-icmbio"

# Pelo runner da família (valida o registro, aplica o seletor de escopo, gera manifesto)
python -m gestao.runner --analise status-pt --data-execucao 2026-09-13 --regional GR2 --produto restrito

# Diretamente
python gestao/IND_GEST_01/IND_GEST_01.1_run.py --unidade CGGP --data-execucao 2026-09-13
python gestao/IND_GEST_01/IND_GEST_01.1_run.py --unidade DIPLAN --incluir-subordinadas --niveis 5
python gestao/IND_GEST_01/IND_GEST_01.1_run.py --unidade CGGP,DIPLAN
python gestao/IND_GEST_01/IND_GEST_01.1_run.py --todas --produto compartilhavel
python gestao/IND_GEST_01/IND_GEST_01.1_run.py --unidade CGGP --incluir-encerrados
python gestao/IND_GEST_01/IND_GEST_01.1_run.py --todas --dry-run
```

Desempenho observado: cerca de 10 segundos para o instituto inteiro.

---

## 8. Saídas e dicionário de dados

CSVs pipe-delimited, `utf-8-sig`, em `artefatos_local/gestao/AAAA-MM/`. Nomes:
`IND_GEST_01.2_<visao>_<produto>_<escopo>_AAAAMMDD_HHMM.csv`, com carimbo de hora
em `America/Sao_Paulo`.

### `IND_GEST_01.2_detalhe_*` — uma linha por plano

Gerado apenas nos produtos `operacional` e `restrito`.

| Coluna | Conteúdo |
| --- | --- |
| `unidade_sigla`, `unidade_nome` | unidade do plano |
| `mesogrupo` | agrupador organizacional, via `lib/estrutura_organizacional.py`; `Não mapeado` sem as planilhas locais |
| `unidade_pai_sigla` | unidade imediatamente superior |
| `id_servidor`, `servidor_nome` | **quem procurar** (D14) |
| `plano_numero`, `plano_inicio`, `plano_fim` | identificação do plano |
| `status_codigo` | código bruto da camada 1 |
| `status_desde_trilha` | `MAX(created_at)` da trilha para o código atual |
| `plano_updated_at`, `plano_avaliado_at` | carimbos do plano |
| `periodos_aguardando_avaliacao` | consolidações `CONCLUIDO` |
| `periodos_em_preenchimento`, `periodos_avaliados`, `periodos_total` | composição das consolidações |
| `periodo_pendente_fim` | fim do período pendente mais recente |
| `status_alterado_por` | quem executou a última transição (D14) |
| `status_negocio` | rótulo derivado das duas camadas (§3) |
| `data_ultima_mudanca_status` | data e hora da transição, ou o fallback |
| `origem_data_status` | `trilha_status_justificativas` ou `fallback_updated_at` |
| `dias_no_status_atual` | dias entre a data da mudança e a data da fotografia; **vazio** se a data for posterior à fotografia (D17/F7) |
| `acao_sugerida` | frase dizendo o que fazer e com quem |

### `IND_GEST_01.2_painel_*` — unidade × status

| Coluna | Conteúdo |
| --- | --- |
| `unidade_sigla` | unidade |
| `status_negocio` | rótulo derivado |
| `qtd_planos` | número de planos; `SUPRIMIDO_K` quando ocultado no produto compartilhável |

É a visão declarada no contrato de validação.

---

## 9. Produtos e privacidade

| Produto | Detalhe nominal | Painel | Circulação |
| --- | --- | --- | --- |
| `operacional` | sim | contagens integrais | uso imediato da chefia |
| `restrito` | sim | contagens integrais | interno da unidade |
| `compartilhavel` | **não é gerado** | supressão k<5 **e** supressão complementar | único que sai da unidade |

**Supressão complementar (D17/F11).** Quando, numa unidade, uma única célula é
ocultada por k<5, a menor célula visível da mesma unidade também é ocultada. Sem
isso, qualquer total da unidade divulgado em outro produto revelaria a célula por
subtração. Implementação: `ocde.relatorios.privacidade.apply_complementary_suppression`.

**Minimização (D14).** Só nome e identificador do servidor. CPF, e-mail e matrícula
não são lidos nem persistidos. O `servidor_email`, que a consulta selecionava antes
da D14, foi retirado.

---

## 10. Validação automatizada

| Elemento | Onde |
| --- | --- |
| Contrato | `TARGETS["G01"]` em `lib/validation_contracts.py` |
| Oracle independente | `oracle_ind_gest_01` em `lib/validation_oracles.py` |
| Extratores atômicos | `pt_status_planos`, `pt_status_consolidacoes`, `pt_status_transicoes` em `lib/validation_extractors.py` |
| Invariantes | `precedencia_consolidacao`, `fallback_data_status`, `total_subtotais`, `uma_linha_por_plano` |
| Tolerância | contagens: 0 |
| Registro do ciclo mensal | `gestao/registry.py`, chave `status-pt` |

```powershell
python -m lib.validation_runner --familia gestao --alvo G01 --modo integrado --produto restrito --data-execucao 2026-09-13 --regional GR2
```

O A2 validado é o do produto solicitado; `ambos` usa o restrito. Células
`SUPRIMIDO_K` não entram na comparação com o oracle.

Resultado em 13.09.2026 (GR2, produtos `restrito` e `compartilhavel`):
`HOMOLOGACAO_INICIAL_PENDENTE`, sem achado bloqueante.

---

## 11. Retratos nacionais

Fotografias históricas, não baselines.

| Status de negócio | 08.09.2026 (v1) | 13.09.2026 (3.0.0) | 13.09.2026 (4.0.0) |
| --- | ---: | ---: | ---: |
| Em execução | 1.297 | 1.288 | 1.287 |
| **Aguardando avaliação** | **684** | 606 | **613** |
| Aguardando assinatura | 417 | 490 | 490 |
| Rascunho | 307 | 297 | 297 |
| Suspenso | 3 | 3 | 3 |
| **Total** | 2.708 planos, 376 unidades | 2.684 linhas (2.683 planos), 371 unidades | **2.690 planos**, 371 unidades |

Entre as duas colunas de 13.09.2026 a base é a mesma; a diferença é só de método: +7
concluídos com período pendente (F1) e −1 plano que saía duplicado (F3). A variação
entre 08.09 e 13.09 é movimento real da base.

---

## 12. Limitações e cuidados

- **A fotografia não é reproduzível retroativamente.** O Denodo é ao vivo;
  `--data-execucao` passada muda a data de referência dos dias no status, mas não o
  estado dos planos.
- `dias_no_status_atual` calculado sobre `fallback_updated_at` mede a última alteração
  **de qualquer campo** do plano, não necessariamente do status. Filtre por
  `origem_data_status` quando o rigor da data importar.
- O detalhe contém **nome de servidores**. Fica em `artefatos_local/`, fora do
  versionamento; nunca publicar.
- O script não contém credenciais: lê o `.env` local via `lib/denodo_config.py`.
- A coluna `mesogrupo` depende de planilhas locais opcionais; na ausência delas o valor
  sai como `Não mapeado`.

---

## 13. Histórico de versões

| Versão | Data | Mudança |
| --- | --- | --- |
| 1.0 | 08.09.2026 | Primeira extração: duas camadas, trilha de status, detalhe e painel |
| 2.0.0 | até 13.09.2026 | Contrato de validação, oracle, produtos `restrito`/`compartilhavel` (commit `6e642c0`) |
| 3.0.0 | 13.09.2026 | D14: identificação nominal nos produtos internos; retirada do e-mail |
| **4.0.0** | 13.09.2026 | D17: código G01 e namespace `IND_GEST_01`; universo com concluídos pendentes (F1); fim da duplicidade (F3); oracle alinhado (F5); dias sem valor negativo (F7); `--niveis` (F10); supressão complementar (F11) |
