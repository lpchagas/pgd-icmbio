# Protocolo Automatizado de Validação dos Indicadores OCDE/PGD e de Gestão

## 1. Objetivo

Este protocolo define a validação reproduzível dos indicadores I01–I12 e das
análises habilitadas em `gestao/`. A conferência numérica não depende de
consultas manuais ao PETRVS: uma implementação de produção (A1) é comparada com
um cálculo de referência independente em Python (A3), alimentado por extrações
atômicas somente leitura.

A participação humana é reservada à homologação inicial da definição de
negócio e às exceções: mudança metodológica, mudança de fonte ou schema,
divergência inexplicada e aceitação de risco. Fórmulas homologadas e estáveis
são recertificadas automaticamente a cada ciclo.

Fonte: Denodo, database `petrvs_icmbio`. Credenciais são lidas exclusivamente
do `.env` local por `lib.denodo_config`; nunca aparecem em scripts, comandos,
logs, manifestos ou artefatos.

## 2. Princípios obrigatórios

1. **Independência:** A1 e A3 não compartilham SQL nem funções de fórmula.
2. **Reprodutibilidade:** toda execução tem data injetada, `run_id`, hashes e manifesto.
3. **Temporalidade única:** produção usa `lib.periodos`; testes confirmam a regra por casos conhecidos independentes.
4. **Somente leitura:** todas as consultas Denodo são `SELECT`/CTE de leitura.
5. **Falha explícita:** resultado parcial, artefato ausente ou pendência bloqueante nunca vira sucesso.
6. **Privacidade:** snapshots e evidências excluem nomes, CPF, contatos e texto pessoal não sanitizado.
7. **Rastreabilidade:** um status aprovado sempre aponta para A1–A5 físicos e seus hashes.
8. **Exceção humana:** consulta manual é `E1`, nunca requisito ordinário do A3.

Para execução em setembro/2026, a janela obrigatória é `01/07/2025–31/08/2026`.
O mês corrente nunca entra na lente acumulada.

## 3. Contrato executável do alvo

Cada indicador e análise de gestão é declarado como `ValidationTarget` em
`lib.validation_contracts`, contendo:

```text
code, family, name
production_entrypoint, oracle_name, atomic_extractors
outputs, business_keys, metrics, output_schema
formula_version, temporal_lenses, supported_scopes
invariants, tolerances, drift_policy
privacy_class, baseline, enabled_in_monthly_cycle
```

Nenhum alvo entra no ciclo mensal sem entrypoint, oracle, fixture, schema,
chave de negócio, invariantes, tolerâncias e política de drift válidos.

## 4. Artefatos A1–A5

### A1 — Especificação executável e produção

A1 é o script de produção mais seu contrato. Deve explicitar objetivo, fórmula,
numerador, denominador, granularidade, fontes, chaves, temporalidade, nulos,
duplicidades, unidade dona/executora, privacidade e versão metodológica.

Requisitos:

- `--data-execucao AAAA-MM-DD` obrigatório no runner;
- `analysis_window()`, `build_periods_pe()` ou `build_periods_pt()`;
- conexão apenas por `lib.denodo_config`;
- SQL Denodo somente leitura e com prefixo `petrvs_icmbio_`;
- saída determinística com pipe e `utf-8-sig`;
- nenhuma credencial ou dado pessoal desnecessário;
- execução por fixture sem Denodo;
- alteração de `formula_version` para mudança material.

### A2 — Resultado e manifesto

Padrões existentes são preservados:

```text
IND_OCDE_XX.2_<nome>_AAAAMMDD_HHMM.csv
PT_STATUS.2_<visao>_<produto>_<escopo>_AAAAMMDD_HHMM.csv
```

O manifesto inclui `run_id`, janela, escopo, lente, produto, data/hora, versão,
hash do A1/SQL/schema/CSV, colunas, linhas, datas mínima/máxima e classificação
de privacidade.

A2 falha em arquivo ausente, vazio indevido, largura irregular, schema
divergente, chave duplicada, fato fora da janela, dado pessoal vedado ou
manifesto inconsistente.

### A3 — Validação independente em Python

Artefatos:

```text
IND_OCDE_XX.3_validacao_independente_<run_id>.json
IND_OCDE_XX.3_validacao_independente_<run_id>.md
PT_STATUS.3_validacao_independente_<run_id>.json
PT_STATUS.3_validacao_independente_<run_id>.md
```

O oracle:

1. executa uma ou mais consultas atômicas próprias, conforme o contrato;
2. recalcula a métrica em Python;
3. compara chaves e métricas com A2;
4. aplica tolerâncias por tipo;
5. executa invariantes e testes metamórficos;
6. registra cobertura, hashes e achados.

É proibido ao oracle importar `ocde.indicadores`, `lib.docs_sql` ou funções de
fórmula de produção. Consultas atômicas não contêm agregação da métrica final.

Tolerâncias padrão:

| Tipo | Tolerância |
|---|---:|
| Contagens e chaves | igualdade exata |
| Percentuais | 0,05 ponto percentual |
| Horas | 0,01 |
| Médias, scores e diferenças | 0,01 |
| Categorias e status | igualdade exata |

Exceções precisam de justificativa no contrato.

### A4 — Diagnóstico automatizado

Artefatos:

```text
IND_OCDE_XX.4_diagnostico_<run_id>.json
IND_OCDE_XX.4_diagnostico_<run_id>.md
IND_OCDE_XX.4_qN_<descricao>_<run_id>.csv
```

A4 resumido é sempre gerado. Evidências detalhadas surgem apenas para regras
acionadas: volumetria, duplicidade, órfãos, nulos, cobertura, status, extremos,
escala, JSON, hierarquia, unidade dona/executora, A1 × A3, drift e privacidade.

Cada achado registra severidade `informativo`, `alerta` ou `bloqueante`; apenas a última impede certificação automática.

Classificações:

```text
BUG_PROVAVEL
DIVERGENCIA_SEMANTICA
MUDANCA_DE_SCHEMA
ANOMALIA_DE_DADOS
DRIFT_RELEVANTE
DECISAO_METODOLOGICA
SEM_DIVERGENCIA
```

### A5 — Dossiê e decisão

Artefatos:

```text
IND_OCDE_XX.5_relatorio_validacao_<run_id>.md
PT_STATUS.5_relatorio_validacao_<run_id>.md
```

A5 é gerado dos manifestos anteriores. Contém objetivo, versão, janela,
escopo, hashes, cobertura, comparação, invariantes, drift, diagnósticos,
limitações, riscos, recomendação, decisão e inventário dos arquivos.

Estados permitidos:

```text
HOMOLOGACAO_INICIAL_PENDENTE
CERTIFICADO_AUTOMATICAMENTE
AGUARDANDO_DECISAO
FALHA_TECNICA
REPROVADO
HOMOLOGADO
```

Após homologação inicial, a certificação mensal é automática quando fórmula,
SQL, oracle e schema não mudaram, A1/A3 convergem, os testes passam e não há
drift bloqueante. Mudança metodológica ou divergência abre decisão CGOV. A homologação inicial é registrada, sem nome pessoal, por `python -m tools.approve_validation_baseline --manifesto ARQUIVO --alvo IXX --papel-aprovador CGOV --decisao HOMOLOGADO --justificativa TEXTO`; fixtures não podem criar baseline homologada.

### E1 — Consulta humana excepcional

Consulta humana ao PETRVS somente ocorre quando A3/A4 não explicam a
divergência. O registro recebe o prefixo `E1_consulta_humana`, informa pergunta,
data, papel responsável e conclusão, e não substitui A3.

PDFs A3 históricos permanecem como evidência legada, sem serem usados como
gate do ciclo automatizado.

## 5. Oracles registrados

| Alvo | Regra de referência independente |
|---|---|
| I01 | servidor × período × modalidade, com deduplicação |
| I02 | entregas elegíveis e cumprimento por unidade |
| I03 | normalização da meta e taxa por entrega |
| I04 | média das razões de atingimento |
| I05 | entregas distintas por servidor e média da unidade |
| I06 | responsáveis distintos por entrega e distribuição por faixa |
| I07 | carga proporcional × força de trabalho |
| I08 | horas da entrega ÷ capacidade da unidade |
| I09 | score `6 - sequencia` e universo de avaliações |
| I10 | categoria inadequada por `sequencia = 4` |
| I11 | categoria excepcional por `sequencia = 1` |
| I12 | médias PT/PE e diferença direcional `PT - PE` |
| PT_STATUS | precedência da consolidação e status do plano |

## 6. Testes obrigatórios

### Offline

- fixtures sintéticas revisadas;
- unitários das fórmulas;
- testes baseados em propriedades com `hypothesis`;
- contratos de schema;
- invariância à ordem;
- idempotência;
- soft-delete e fora da janela sem efeito;
- duplicação, nulos e denominador zero;
- datas invertidas, ciclo parcial e ano bissexto;
- reconciliação de totais e subtotais;
- independência estática do oracle;
- privacidade e ausência de segredos.

### Integrado

- extração atômica Denodo somente leitura;
- A1 × A3 por chave;
- cobertura de todas as fontes;
- schema e volumetria;
- drift contra baseline homologada;
- geração física de A3–A5;
- manifesto e hashes;
- retomada somente com fingerprint idêntico.

Fixture sintética aprovada nos testes não substitui o integrado mensal nem constitui homologação.

## 7. Drift

| Regra padrão | Alerta | Bloqueio |
|---|---:|---:|
| Aumento de nulos | > 5 p.p. | > 15 p.p. |
| Variação volumétrica comparável | > 30% | > 60% |
| PSI | > 0,20 | > 0,30 |
| Schema | — | qualquer mudança |
| Chaves A1 × A3 | — | qualquer diferença |

Bases cumulativas são comparadas por ciclo fechado equivalente ou parcela
incremental, nunca pelo total acumulado bruto.

## 8. Interface operacional

```text
python -m lib.validation_runner
  --familia ocde|gestao|todas
  --alvo I01|...|I12|PT_STATUS|todos
  --data-execucao AAAA-MM-DD
  --etapa A1|A2|A3|A4|A5|todas
  --modo fixture|integrado
  --produto restrito|compartilhavel|ambos
  --escopo nacional | --regional SIGLA | --unidade SIGLA |
  --mesogrupo NOME | --tipo-unidade TIPO | --lista-unidades ARQUIVO
  --retomar --revalidar --salvar
```

O runner retorna código diferente de zero para falha, pendência bloqueante ou
artefato ausente.

## 9. Integração mensal

```text
preflight
→ analysis_window
→ extrair_indicadores
→ extrair_gestao
→ validar_contratos_a1_a2
→ validar_oracles_a3
→ diagnosticos_a4
→ gerar_a5
→ validar_periodicidade
→ relatorio_extracao
→ verificar_consistencia
→ relatorio_gerencial_v2
→ auditar_seguranca
```

Falha A1–A5 impede sucesso global. Alteração de código, SQL, schema, janela,
escopo ou snapshot invalida a retomada anterior.

## 10. Gestão e governança

`gestao.registry.ManagementExtraction` deve declarar oracle, extratores,
chaves, schema, versão, invariantes, tolerâncias e baseline. Nova análise não é
habilitada no ciclo mensal sem esse contrato e seu A5 inicial.

O baseline privado e o A5 do ciclo registram o estado dos artefatos, mas não
substituem a deliberação institucional. O estado `HOMOLOGADO` somente é permitido
quando o A5 e o registro formal de decisão existem. Validações verbais devem ser
formalizadas ou permanecer pendentes.

## 11. Critério de conclusão

Um alvo está validado quando:

- contrato, fixture e oracle existem;
- A2 atende ao schema e à janela;
- A1 e A3 convergem;
- A4 não contém bloqueio aberto;
- A5 físico registra decisão válida;
- segurança e privacidade passam;
- o manifesto referencia todos os hashes.

Nenhuma consulta manual é necessária para confirmar números. Humanos aprovam
definições de negócio e exceções, não refazem cálculos operacionais.
