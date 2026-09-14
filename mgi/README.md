# mgi/ — Indicadores de Gestão de Pessoas (MGI)

> Em construção. Os scripts MGI serão implementados aqui, seguindo o mesmo padrão
> dos scripts OCDE em `ocde/indicadores/`.

## Estrutura prevista

- `indicadores/` — scripts `IND_MGI_XX.1_run.py` para cada indicador MGI
- Módulos compartilhados: `lib/` (raiz do repositório — mesmos módulos usados pela iniciativa OCDE)
- Documentação técnica: `docs/mgi/`

## Namespace (decisão CGOV D01 — 13.09.2026)

Os catálogos OCDE e MGI são separados por prefixo de arquivo, para evitar colisão
no painel executivo entre indicadores com propósitos, naturezas e recortes
temporais distintos:

| Família | Prefixo | Pasta |
| --- | --- | --- |
| Piloto OCDE/PGD | `IND_OCDE_XX` | `ocde/indicadores/` |
| Governamentais MGI | `IND_MGI_XX` | `mgi/indicadores/` |

O prefixo vale para todos os artefatos da cadeia (`.1_run.py`, `.2_*.csv`,
`.3`, `.4`, `.5`). O código lógico de cada indicador (`I01`…`I12`) permanece sem
o namespace — ele identifica o alvo, não o arquivo.

## Janela temporal (decisão CGOV D02 — 13.09.2026)

Diferentemente da janela cumulativa da OCDE (`lib.periodos.analysis_window()`,
início fixo em 01/07/2025), os indicadores MGI são **anuais**: os scripts desta
pasta devem filtrar de 1º de janeiro a 31 de dezembro do ano de referência
vigente.

## Modelo de referência

Seguir o padrão canônico estabelecido em `ocde/`:

- Script de indicador: `ocde/indicadores/IND_OCDE_02.1_run.py`
- Ficha técnica: `docs/ocde/06.2.1-i02.md`
- Módulos compartilhados: `lib/denodo_config.py`, `lib/periodos.py`, `lib/csv_utils.py`
