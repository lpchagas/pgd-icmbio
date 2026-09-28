# ADR-006 — Persistência do modelo comum de dados em MySQL 8 (revisa ADR-001)

**Data:** 26.07.2026 | **Estado:** aprovada
**Decisor:** Coordenador do projeto (Leandro) | **Consultoria:** análise AT-01
**Documentos:** `docs/dados-petrvs/esquema-mysql-agente.md`;
proposta v6 (que consolidou a decisão e seu histórico)

## Contexto

A proposta v3 (§3.2–3.3, ADR-001) definia SQLite local como persistência do modelo comum
de dados — 6 entidades do artefato `03` §5 — pela lógica "zero infraestrutura; migrar só
quando a dor de escala aparecer". A análise AT-01 da estrutura real do PETRVS (MySQL 8 na
origem Dataprev, acessado via Denodo) mostrou que a dor não é de escala, e sim de
**interoperabilidade**: o requisito de referenciar e comparar objetos reais do ICMBio
(unidades, servidores, entregas com UUID `CHAR(36)`, `meta` JSON, `DECIMAL(5,2)`) existe
desde o dia 1, e o PETRVS já pratica as convenções que as "regras de ouro" da v3 §3.2
exigem — exceto versionamento imutável, que o modelo comum precisa acrescentar.

## Decisão

1. **D1 — SGBD:** o modelo comum será persistido em **MySQL 8 Community local**, com o
   esquema de 21 tabelas do AT-01 §5 (6 entidades do `03` §5 + versões imutáveis + camada
   de governança + espelhos `ref_*`), versionado em `agente/dados/schema.sql`. As convenções
   estruturais do PETRVS são herdadas: PK UUID `CHAR(36)`, soft-delete (`deleted_at`),
   auditoria `created/updated_at`, `ENUM` para status, `JSON` nativo, `DECIMAL(5,2)` para
   métricas. A imutabilidade de versões é garantida por **triggers no banco** (AT-01 §6.3),
   não apenas na aplicação.
2. **D2 — Espelho de servidores:** `ref_usuarios` sincroniza **apenas os servidores da
   unidade-piloto**, com campos mínimos (id, nome, matrícula, participa_pgd, unidade) —
   sem CPF, e-mail ou situação funcional. Relatórios usam pseudônimos
   (`participantes.rotulo`).
3. **D3 — Identidade dupla:** todo objeto versionável tem UUID (identidade técnica) e
   **código legível** (`ENT-2026-0001`, `R-014`) para citação nas saídas das skills
   (contrato v3 §8.3).
4. **D4 — Provisionamento:** MySQL Community instalado como **serviço Windows** na máquina
   local, porta 3306, **sem Docker** (coerente com o ecossistema `pgd-*`). Credenciais no
   `.env` local (fora do Git). Backup por `mysqldump` diário no padrão do
   `backup_privado.ps1`.

## Alternativas descartadas

| Alternativa | Motivo do descarte |
| --- | --- |
| Manter SQLite (ADR-001) | Sem `ENUM`/`CHECK` efetivos, JSON nativo, triggers robustos e controle de acesso por usuário (`03` §17.3); dialeto diferente do sistema-fonte obrigaria camada de tradução para comparar dados do Denodo |
| PostgreSQL local | SGBD excelente, mas introduz um terceiro dialeto no ecossistema; a paridade com o PETRVS (MySQL 8) é o ganho central da mudança |
| MySQL em Docker | Docker não é usado em nenhum projeto do ecossistema; a equipe já operou MySQL 8 nativo na fase do dump (tag `v1.0-dump-mysql` do `pgd-ocde-icmbio`) |
| Escrever no próprio PETRVS/Denodo | Denodo é somente leitura; escrita no PETRVS está explicitamente fora do escopo (v3 §2.3) |

## Consequências

- **Positivas:** interoperabilidade por construção com dados reais do ICMBio (FKs lógicas
  por UUID real + espelhos `ref_*`); comparação agente×PETRVS campo a campo no piloto
  (campos `petrvs_entrega_id`/`petrvs_catalogo_id`); regra de ouro 2 garantida pelo banco;
  ferramental DBeaver já dominado pela equipe.
- **Negativas/custos:** perde-se o zero-infraestrutura do SQLite — o I0 ganha a instalação
  do serviço MySQL e a rotina de backup; surge o risco RP15 (indisponibilidade do serviço
  local), mitigado por dump diário e script de reinstalação documentado.
- **Propagação:** revisa §3.2, §3.3, §6.2 (I0), §7, §10, §11 e §12 da proposta — motivo da
  emissão da **versão 4** (v3, nota final). O restante da v3 (escopo, skills S01–S10,
  roadmap I0–I7, papéis, qualidade) permanece inalterado.
