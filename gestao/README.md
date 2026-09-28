# gestao/ — Indicadores gerenciais para as chefias

Indicadores de acompanhamento operacional, feitos para a chefia da unidade agir no
dia a dia. Diferem dos indicadores OCDE (`ocde/indicadores/`) em quatro pontos:

| | Gestão (`gestao/`) | OCDE (`ocde/indicadores/`) |
| --- | --- | --- |
| Pergunta | O que está parado e com quem falar? | Como a unidade desempenhou no ciclo? |
| Tempo | Fotografia na data de execução (lente `operacional`) | Janela cumulativa desde 01/07/2025 |
| Destino | Chefias e CGOV | COCAGE, Power BI, relatório V2 |
| Identificação nominal | Permitida nos produtos internos conforme D14 (G01) e D18 (G02) | Nunca |

A validação usa o mesmo protocolo automatizado A1–A5, com oracle independente
(`lib/validation_oracles.py`), e cada indicador tem contrato próprio em
`lib/validation_contracts.py`.

**Estado em 14.09.2026:** G01 4.0.0 e G02 1.0.0 estão certificados
automaticamente na GR2. A D18 autorizou o anexo nominal G02 exclusivamente no
produto restrito. O próximo gate institucional é o piloto CGOV; a expansão nacional
continua suspensa.

## Namespace (D17 — ratificada em 13.09.2026)

Mesmo modelo do D01 da família OCDE:

| Elemento | Padrão | Exemplo |
| --- | --- | --- |
| Pasta | `gestao/IND_GEST_XX/` | `gestao/IND_GEST_01/` |
| Script A1 | `IND_GEST_XX.1_run.py` | `IND_GEST_01.1_run.py` |
| Artefatos | `IND_GEST_XX.{2,3,4,5}_*` | `IND_GEST_01.2_painel_restrito_…csv` |
| Código lógico | `GXX` | `G01` |
| Ficha | `docs/gestao/IND_GEST_XX-<slug>.md` | `docs/gestao/IND_GEST_01-situacao-planos-trabalho.md` |

O prefixo tem fonte única em `lib/validation_contracts.py` (`GEST_ARTIFACT_PREFIX`,
`gest_artifact`, `target_artifact_prefix`). O código lógico não carrega o namespace:
ele identifica o indicador, não o arquivo.

## Indicadores

| Código | Pasta | Nome | Ficha | Código anterior |
| --- | --- | --- | --- | --- |
| G01 | [`IND_GEST_01/`](IND_GEST_01/) | Situação dos Planos de Trabalho | [ficha](../docs/gestao/IND_GEST_01-situacao-planos-trabalho.md) | `PT_STATUS` (aceito como alias na CLI) |
| G02 | [`IND_GEST_02/`](IND_GEST_02/) | Execução das Entregas | [ficha](../docs/gestao/IND_GEST_02-execucao-entregas.md) | — |

## Como executar

```powershell
# Pelo runner, que valida o registro, aplica o seletor de escopo e gera manifesto
python -m gestao.runner --analise status-pt --data-execucao 2026-09-13 --regional GR2 --produto restrito

# Diretamente, para uso imediato da chefia
python gestao/IND_GEST_01/IND_GEST_01.1_run.py --unidade CGGP --incluir-subordinadas
python -m gestao.runner --analise execucao-entregas --data-execucao 2026-09-13 --regional GR2 --produto restrito
```

As saídas vão para `artefatos_local/gestao/AAAA-MM/escopos/<scope-key>/`, que nunca é versionado.

## Como incluir um novo indicador

1. Criar `gestao/IND_GEST_XX/IND_GEST_XX.1_run.py` e um `README.md` curto na pasta.
   A pasta não é pacote Python: o runner chama o script pelo caminho.
2. Declarar `TARGETS["GXX"]` em `lib/validation_contracts.py`, com contrato de saída
   `gest_artifact("XX", "2_<visao>_*.csv")`.
3. Implementar o oracle independente em `lib/validation_oracles.py` e os extratores
   atômicos em `lib/validation_extractors.py`, com fixtures em
   `tests/fixtures/validation/`.
4. Registrar em `gestao/registry.py`. A chave é o nome da skill, em kebab-case.
5. Escrever a ficha em `docs/gestao/` e incluir a linha na tabela acima e em
   `docs/gestao/README.md`.
