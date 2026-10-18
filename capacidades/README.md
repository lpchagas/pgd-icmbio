# Skills do agente PGD/ICMBio

## Fonte vigente

O catálogo das capacidades S01–S24 tem uma **única fonte editável**:
[`catalogo.yaml`](catalogo.yaml) (DP-09). Dela, `tools/gerar_catalogo_capacidades.py` gera as
[fichas](fichas/README.md), a tabela de capacidades do [`CATALOGO.md`](CATALOGO.md) e as tabelas
do [capítulo 03 da proposta](../docs/agente/projeto-v6/03-catalogo-skills-s01-s24.md). Os
protótipos que hoje operam no Cowork da CGOV, e que S21–S24 pretendem substituir, estão
versionados em [`prototipos-cowork/`](prototipos-cowork/README.md).

## Onde estão os artefatos das skills

| Grupo | Local | Papel | Precedência |
| --- | --- | --- | --- |
| Catálogo S01–S24 | [`catalogo.yaml`](catalogo.yaml) + [`TEMPLATE_SKILL.md`](TEMPLATE_SKILL.md) | fonte única: especificação, planejamento, dependências e casos de teste | principal |
| Fichas S01–S24 | [`fichas/`](fichas/README.md) | geradas: características (seções 1–27) e teste em outras ferramentas de IA | derivada do catálogo |
| Catálogo de estado | [`CATALOGO.md`](CATALOGO.md) | estado de cada capacidade e dos indicadores | tabela S01–S24 gerada; o resto, manual |
| Componentes metodológicos B01–B04 (`00_skill-*.md`) | [`docs/agente/metodologia/`](../docs/agente/metodologia/00_skill-plano-entregas-v1.md) | base metodológica | **canônica** (DP-09) |
| Protótipos Cowork | [`prototipos-cowork/`](prototipos-cowork/README.md) | referência operacional versionada do domínio S21–S24 (e S04/S05, no caso do `cgov-elaborar-entrega`) | não canônica: em conflito, prevalecem a metodologia e as RN |
| Análise, matriz, especificação inicial, backlog e plano de execução/avaliação (`01_` a `05_`) | retirados da árvore no L4f; recuperáveis no histórico do Git | insumos da proposta v6 | histórico; destino de cada regra e trecho na [cobertura dos requisitos](../docs/governanca-projeto/cobertura-requisitos.md) |

Cada skill aponta suas fontes metodológicas no campo `fontes_metodologicas` do YAML; a ficha as
lista como material de apoio.

## Como revisar uma skill

1. Edite a entrada da skill em `catalogo.yaml`. Mudança de conteúdo sobe a `versao_ficha` e
   acrescenta uma linha ao `historico`.
2. Rode `python -m tools.gerar_catalogo_capacidades gerar`.
3. Confira o diff das fichas e das tabelas geradas. O teste da suíte (e o comando `verificar`)
   falha se algum arquivo gerado divergir do YAML.
4. Se houver impacto, atualize cronograma, riscos, regras e testes na mesma alteração.
