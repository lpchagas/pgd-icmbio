# Agente PGD/ICMBio

Agente de apoio ao Programa de Gestão e Desempenho do ICMBio. Combina conhecimento com
fonte (RAG), os indicadores OCDE/PGD e de gestão já certificados pelo projeto analítico e
24 skills executáveis para planejamento, pactuação, execução, avaliação e aprendizagem.
As ferramentas serão expostas por um servidor MCP local, com gate de classe de dado
([ADR-014](../decisoes/ADR-014-llm-execucao-mcp-hibrido.md)).

## Documentação vigente

- [Proposta de projeto v7](projeto-v7/00_proposta-projeto-v7.md) — visão completa e normativa.
- [Portal da v7](projeto-v7/README.md) — capítulos por público e assunto.
- [Catálogo S01–S24](projeto-v7/03-catalogo-skills-s01-s24.md).
- [Fichas das skills S01–S24](../../capacidades/fichas/README.md), geradas do [catálogo único](../../capacidades/catalogo.yaml).
- [Componentes metodológicos B01–B04](metodologia/00_skill-plano-entregas-v1.md) (base canônica, DP-09).
- [Protótipos Cowork da CGOV, versionados](../../capacidades/prototipos-cowork/README.md) (referência operacional).
- [AT-01 — PETRVS/MySQL](../dados-petrvs/esquema-mysql-agente.md).
- [AT-02 — recursos e local-first](recursos-local-first.md).
- [ADRs](../decisoes/) e [riscos](../governanca-projeto/riscos.md).

As propostas anteriores foram consolidadas na v7 e removidas da árvore ativa. A evolução,
inclusive o que mudou da v6 para a v7, está em
[Memória e evolução](projeto-v7/09-memoria-evolucao.md) e permanece recuperável no
histórico do Git.

## Estado em 17/10/2026

**Incremento I0 — Fundação, em andamento.** Fundação técnica (C01–C04) a partir de
02/11/2026.

| Item | Estado |
| --- | --- |
| MySQL 8.4 (WSL, pacote da distribuição) | operacional |
| Migração `001` | aplicada: 21 tabelas e 6 triggers |
| Migração `002` | planejada, não aplicada; alvo 33 tabelas/14 triggers (Onda 5) |
| Serviço de versões | smoke test aprovado |
| Backup | diário às 19h (timer do systemd), retenção de 14 dias |
| Instância isolada | restauração e testes de schema na porta 3307 |
| Espelhos Denodo | 816 unidades e 19 usuários CGOV/COCAGE (sincronização de 22/08/2026) |
| Catálogo S01–S24 | especificado em `capacidades/catalogo.yaml` (fichas 0.2); não implementado |
| Q5 | pendente de validação humana e ata |
| Contratos, motor, servidor MCP, RAG | planejados para C01–C04 |

## Pré-requisitos

- Linux/WSL (ambiente principal) ou Windows;
- Python 3.14 e `.venv` local;
- MySQL 8.4 na porta local configurada (pacote `mysql-server` da distribuição no Linux; Community no Windows);
- credenciais do MySQL em `.cnf` local e do Denodo no `.env`, ambos fora do Git;
- rede/credenciais Denodo somente para consultas autorizadas.

## Verificação rápida

```bash
.venv/bin/python agente/dados/versoes.py --teste
```

No Windows: `.venv\Scripts\python agente\dados\versoes.py --teste`.

O teste usa rollback: cria e versiona uma entrega, confirma histórico e não deixa registro.

Sincronização Denodo, quando a rede estiver disponível:

```bash
.venv/bin/python agente/dados/sincronizar_ref.py
```

No Windows: `.venv\Scripts\python agente\dados\sincronizar_ref.py`.

Backup manual (destino em `PGD_BACKUP_DIR`), instância isolada e banco de teste:
ver [Banco local do agente](../ambiente/banco-local-agente.md).

## Estrutura

```text
agente/dados/                  banco, versões, sincronização, backup e instância isolada
agente/mcp/                    servidor MCP (planejado, C03)
capacidades/catalogo.yaml      fonte única das capacidades S01–S24
capacidades/fichas/            fichas geradas (características e teste em outras IAs)
capacidades/prototipos-cowork/ protótipos cgov-* do Cowork (referência)
docs/agente/projeto-v7/        proposta v7 (00_, normativa) e nove capítulos vinculantes
docs/agente/metodologia/       componentes metodológicos B01–B04 (canônicos)
docs/decisoes/                 ADRs e registro de decisões do projeto
docs/governanca-projeto/       fontes, riscos, validações e cobertura dos requisitos
tests/agente/                  testes do banco (MySQL opt-in, instância isolada)
data/                          artefatos locais ignorados pelo Git
```

## Regras essenciais

- Denodo/PETRVS somente leitura.
- Escrita versionável somente por `agente/dados/versoes.py`.
- Cálculo determinístico em Python, não no LLM; indicadores vêm dos A2 certificados.
- Cliente externo de LLM só recebe dado público, sintético ou agregado compartilhável.
- Fonte, regra, confiança, decisão e pergunta ficam rastreáveis.
- `99_restrito` nunca entra no Git, RAG ou serviço externo.
- O núcleo analítico não importa `agente`, `pymysql` nem `anthropic` (ADR-009).
- Não criar commit ou push sem revisão do estado e dos commits de saída.

Para instalação, Git, MCP, Denodo, RAG, testes, backup e diagnóstico, consulte
[Operação e capacitação](projeto-v7/07-operacao-capacitacao.md).
