# ADR-001 — Persistência do modelo comum de dados em SQLite local (revisada pelo ADR-006)

**Data:** registrada na proposta v3 | **Estado:** **substituída** por [ADR-006](ADR-006-persistencia-mysql.md) em 26.07.2026
**Decisor:** Coordenador do projeto (Leandro)
**Documentos vigentes:** [Memória de evolução](../../projeto-v6/09-memoria-evolucao.md) e ADR-006

> **Nota de reconstrução:** este ADR foi formalizado a partir do texto já registrado na
> proposta v3 (não é uma decisão nova). O ADR-006 já citava "ADR-001" como a decisão
> original de SQLite; este documento materializa esse registro que faltava como arquivo
> próprio em `docs/gestao/decisoes/`.

## Contexto

A proposta v3 introduziu um modelo comum de dados vinculante (`RegraInstitucional`,
`EntregaCandidata`, `EntregaEstruturada`, `PlanoDeCapacidade`, `VinculoOKRD`,
`RegistroDeRisco` — artefato `03` §5) com cinco "regras de ouro" (IDs persistentes,
versionamento sem sobrescrita, rastreabilidade de origem/confiança, separação decisão
humana × sugestão do agente, dados ausentes viram perguntas pendentes). Era preciso
escolher onde persistir esse modelo para uma única unidade-piloto, sem infraestrutura de
servidor prévia.

## Decisão

Persistir o modelo comum em **SQLite local** — arquivo único, sem servidor, consultável
via Python e DBeaver — com esquema versionado em `src/dados/schema.sql`. Classificada na
tabela de stack (v3 §3.3) como decisão **Reversível**: "Zero infraestrutura; suficiente
para 1 unidade-piloto; esquema portável".

## Alternativas descartadas

| Alternativa | Motivo do descarte |
| --- | --- |
| PostgreSQL/Azure | Adiada explicitamente — "só se a dor de escala aparecer (mesma lógica de simplicidade da v2, §8.8)" |

## Consequências

- **Positivas (esperadas):** setup imediato, sem dependência de serviço externo.
- **Como se resolveu:** a análise AT-01 da estrutura real do PETRVS (MySQL 8 na origem
  Dataprev, acessado via Denodo) mostrou que a dor não era de escala, e sim de
  **interoperabilidade** — SQLite não oferece paridade de dialeto, `ENUM`/`CHECK` efetivos
  nem triggers robustos para a imutabilidade exigida pela regra de ouro 2. Esta decisão foi
  **revisada e substituída pelo [ADR-006](ADR-006-persistencia-mysql.md)** (MySQL 8
  Community local), aprovado em 26.07.2026.
