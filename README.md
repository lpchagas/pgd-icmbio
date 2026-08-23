# pgd-agente-icmbio

Agente de apoio ao Programa de Gestão e Desempenho do ICMBio. Combina conhecimento com
fonte (RAG), consulta aos 12 indicadores OCDE/PGD via Denodo e 24 skills executáveis para
planejamento, pactuação, execução, avaliação e aprendizagem.

## Documentação vigente

- [Proposta de projeto v6](proposta-projeto-v6.md) — visão completa e normativa.
- [Portal da v6](docs/projeto-v6/README.md) — capítulos por público e assunto.
- [Catálogo S01–S24](docs/projeto-v6/03-catalogo-skills-s01-s24.md).
- [Especificações das skills](skills/specs/README.md).
- [AT-01 — PETRVS/MySQL](docs/tecnologia/AT-01_analise-petrvs-esquema-mysql_v1.md).
- [AT-02 — recursos e local-first](docs/tecnologia/AT-02_recursos-arquitetura-local-first_v1.md).
- [ADRs](docs/gestao/decisoes/) e [riscos](docs/gestao/riscos.md).

As propostas anteriores foram consolidadas na v6 e removidas da árvore ativa. A evolução
está resumida em [Memória e evolução](docs/projeto-v6/09-memoria-evolucao.md) e permanece
recuperável no histórico do Git.

## Estado atual

**Incremento I0 — Fundação, em andamento.**

| Item | Estado |
| --- | --- |
| MySQL 8.4.9 / serviço `MySQL84` | operacional |
| Migração `001` | aplicada |
| Banco atual | 21 tabelas e 6 triggers |
| Migração `002` | planejada, não aplicada; alvo 33 tabelas/14 triggers |
| Serviço de versões | smoke test aprovado |
| Backup | diário às 19h, retenção 14 dias |
| Espelhos Denodo | 816 unidades e 19 usuários CGOV/COCAGE |
| Q5 | pendente de validação humana e ata |
| Motor/API/RAG/S01–S24 | planejados no cronograma de 104 semanas |

## Pré-requisitos

- Windows;
- Python 3.14 e `.venv` local;
- MySQL 8 Community na porta local configurada;
- variáveis `MYSQL_*` no `.env` ignorado;
- rede/credenciais Denodo somente para consultas autorizadas.

## Verificação rápida

```powershell
.venv\Scripts\python src\dados\versoes.py --teste
```

O teste usa rollback: cria e versiona uma entrega, confirma histórico e não deixa registro.

Sincronização Denodo, quando a rede estiver disponível:

```powershell
.venv\Scripts\python src\dados\sincronizar_ref.py
```

Backup manual:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File src\dados\backup.ps1
```

## Estrutura

```text
proposta-projeto-v6.md       Documento normativo principal
docs/projeto-v6/             Nove capítulos vinculantes
docs/gestao/                 Fontes, glossários, riscos, decisões e validações
docs/tecnologia/             AT-01, AT-02 e referências técnicas
docs/referencias-pgd/        Acervo local; somente README é versionado
skills/specs/                Fichas S01–S24
skills/                      Insumos metodológicos/históricos
src/dados/                   Banco, versões, sincronização e backup
src/agente|rag|skills_engine|api/  Componentes futuros
data/                        Artefatos locais ignorados
```

## Regras essenciais

- Denodo/PETRVS somente leitura.
- Escrita versionável somente por `src/dados/versoes.py`.
- Cálculo determinístico em Python, não no LLM.
- Fonte, regra, confiança, decisão e pergunta ficam rastreáveis.
- `99_restrito` nunca entra no Git, RAG ou serviço externo.
- Não criar commit ou push sem revisão do estado e dos commits de saída.

Para instalação, Git, API, Denodo, RAG, backup e diagnóstico, consulte
[Operação e capacitação](docs/projeto-v6/07-operacao-capacitacao.md).
