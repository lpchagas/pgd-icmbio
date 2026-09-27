# 14 — Indicadores de gestão para as chefias

**Atualizado em:** 14 de setembro de 2026 (D17 e D18)
**Pasta de código:** [`gestao/`](../../gestao/README.md)
**Público:** chefias de unidade, CGOV

> **Mudança de 13.09.2026.** Este documento descrevia só a extração da situação dos
> Planos de Trabalho (`PT_STATUS`). Esse conteúdo virou a ficha técnica do indicador
> **G01**, em [`docs/gestao/IND_GEST_01-situacao-planos-trabalho.md`](IND_GEST_01-situacao-planos-trabalho.md).
> Este arquivo passa a ser o índice da família de gestão e mantém o nome para não
> quebrar links já compartilhados.

---

## 1. O que é a família de gestão

Indicadores de acompanhamento operacional, feitos para a chefia agir no dia a dia:
o que está parado, desde quando e com quem falar.

| | Gestão | OCDE/PGD |
| --- | --- | --- |
| Pergunta | O que está travado e com quem falar? | Como a unidade desempenhou no ciclo? |
| Tempo | Fotografia na data de execução | Janela cumulativa desde 01/07/2025 |
| Destino | Chefias e CGOV | COCAGE, Power BI, relatório V2 |
| Identificação nominal | Nos produtos internos, conforme D14 (G01) e D18 (G02) | Nunca |
| Validação | Protocolo A1–A5 com oracle independente | Protocolo A1–A5 com oracle independente |
| Pasta | `gestao/IND_GEST_XX/` | `ocde/indicadores/` |
| Fichas | `docs/gestao/` | `docs/ocde/` |

---

## 2. Convenção de nomes (D17)

Mesmo modelo do D01 da família OCDE:

| Elemento | Padrão | G01 |
| --- | --- | --- |
| Código lógico | `GXX` | `G01` |
| Pasta | `gestao/IND_GEST_XX/` | `gestao/IND_GEST_01/` |
| Script A1 | `IND_GEST_XX.1_run.py` | `IND_GEST_01.1_run.py` |
| CSV A2 | `IND_GEST_XX.2_<visao>_<produto>_<escopo>_AAAAMMDD_HHMM.csv` | `IND_GEST_01.2_painel_restrito_TODAS_20260913_1550.csv` |
| A3–A5 | `IND_GEST_XX.{3,4,5}_*_<run_id>` | `IND_GEST_01.5_relatorio_validacao_<run_id>.md` |
| Ficha | `docs/gestao/IND_GEST_XX-<slug>.md` | `docs/gestao/IND_GEST_01-situacao-planos-trabalho.md` |

O prefixo tem fonte única em `lib/validation_contracts.py`. O roteiro para incluir um
novo indicador está em [`gestao/README.md`](../../gestao/README.md).

---

## 3. Indicadores

| Código | Nome | Pergunta | `formula_version` | Estado | Ficha |
| --- | --- | --- | --- | --- | --- |
| **G01** | Situação dos Planos de Trabalho | Em que ponto do fluxo está cada PT da equipe e com quem falar para destravá-lo? | 4.0.0 | Baseline D15; recertificação automática GR2 | [IND_GEST_01](IND_GEST_01-situacao-planos-trabalho.md) |
| **G02** | Execução das Entregas | Como o histórico do PE se reconcilia com a fotografia dos PT nas perspectivas dona e executora? | 1.0.0 | D18 homologada; recertificação automática GR2 | [IND_GEST_02](IND_GEST_02-execucao-entregas.md) |

Na referência vigente, os dois indicadores estão certificados automaticamente na
GR2. O G02 mantém 114 vínculos sem entrega identificável como alerta cadastral não
bloqueante. Seu anexo nominal é exclusivo do produto restrito.

---

## 4. Como executar

```powershell
cd "C:\Projetos\pgd-icmbio"

# Todos os indicadores de gestão registrados, com manifesto
python -m gestao.runner --analise todas --data-execucao 2026-09-13 --regional GR2 --produto restrito

# Um indicador, direto
python gestao/IND_GEST_01/IND_GEST_01.1_run.py --unidade CGGP --incluir-subordinadas

# Validação automatizada
python -m lib.validation_runner --familia gestao --alvo G01,G02 --modo integrado --produto restrito --data-execucao 2026-09-13 --regional GR2
```

As saídas ficam em `artefatos_local/gestao/AAAA-MM/escopos/<scope-key>/`, que nunca é versionado.

---

## 5. Transição `PT_STATUS` → `G01`

| Antes de 13.09.2026 | Depois |
| --- | --- |
| `PT_STATUS.1_run.py` (nome antigo, na pasta `gestao/`) | `gestao/IND_GEST_01/IND_GEST_01.1_run.py` |
| `PT_STATUS.2_detalhe_*` / `PT_STATUS.2_painel_*` | `IND_GEST_01.2_detalhe_*` / `IND_GEST_01.2_painel_*` |
| `--alvo PT_STATUS` | `--alvo G01` (`PT_STATUS` e `IND_GEST_01` seguem aceitos) |
| `TARGETS["PT_STATUS"]` | `TARGETS["G01"]` |
| skill `status-pt` | inalterada |

CSVs `PT_STATUS.2_*` já gravados em `artefatos_local/gestao/2026-09/` foram gerados
com a fórmula 3.0.0 ou anterior e não são comparáveis aos da 4.0.0 (ficha, §11).
