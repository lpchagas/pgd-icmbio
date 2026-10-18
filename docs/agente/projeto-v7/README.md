# Portal documental da proposta v7

Este diretório reúne os capítulos vinculantes da
[`00_proposta-projeto-v7.md`](00_proposta-projeto-v7.md). O conjunto é autocontido: as
propostas anteriores não são necessárias para desenvolver, testar ou operar o agente. O
que mudou da v6 para a v7 está no [capítulo 09](09-memoria-evolucao.md#8-da-v6-para-a-v7).

## Trilha rápida por público

| Público | Ordem recomendada |
| --- | --- |
| Gestor ou patrocinador | proposta v7 → 01 → 04 → 08 |
| Analista de negócio | proposta v7 → 03 → fichas em `capacidades/fichas` → 05 |
| Desenvolvedor | 02 → 03 → 05 → 07 |
| Usuário iniciante | proposta v7 → 07 |
| Auditor/LGPD | 06 → 08 → registro ativo de riscos |

## Capítulos

1. [Visão do produto e governança](01-visao-produto-governanca.md)
2. [Arquitetura, tecnologia e dados](02-arquitetura-tecnologia-dados.md)
3. [Catálogo de skills S01–S24](03-catalogo-skills-s01-s24.md)
4. [Cronograma, capacidade e marcos](04-cronograma-capacidade-marcos.md)
5. [Qualidade, testes e aceite](05-qualidade-testes-aceite.md)
6. [Segurança, privacidade e fontes](06-seguranca-privacidade-fontes.md)
7. [Operação e capacitação](07-operacao-capacitacao.md)
8. [Rastreabilidade, decisões e riscos](08-rastreabilidade-decisoes-riscos.md)
9. [Memória e evolução](09-memoria-evolucao.md)

## Fontes complementares vigentes

- [AT-01 — análise PETRVS e esquema MySQL](../../dados-petrvs/esquema-mysql-agente.md)
- [AT-02 — recursos e arquitetura local-first](../recursos-local-first.md)
- [ADR-014 — servidor MCP local e arranjo híbrido](../../decisoes/ADR-014-llm-execucao-mcp-hibrido.md)
- [Fontes institucionais e Q5](../../governanca-projeto/fontes-institucionais.md)
- [Validação do modelo comum](../../governanca-projeto/validacao-modelo-comum.md)
- [Registro ativo de riscos](../../governanca-projeto/riscos.md)
- [Banco local do agente](../../ambiente/banco-local-agente.md)
- [Índice do acervo PGD](../../referencias-pgd/README.md)
- [Fichas S01–S24](../../../capacidades/fichas/README.md) (geradas de `capacidades/catalogo.yaml`)

## Regra de manutenção

- Atualize a fonte principal do assunto; nos demais documentos, use links e resumos.
- Não transforme questão aberta em decisão.
- Não descreva estado-alvo como estado atual; date o estado atual.
- Ao mudar uma skill, edite `capacidades/catalogo.yaml`, rode o gerador e atualize o
  cronograma quando afetado. As tabelas geradas do capítulo 03 não se editam à mão.
- Ao mudar arquitetura, registre ou revise uma ADR.
- Ao mudar regra institucional, registre fonte, vigência e validação humana.
- Uma nova versão da proposta muda a pasta por `git mv` e registra a evolução no
  capítulo 09, sem páginas-ponte.
