# AT-01 — Análise da estrutura de dados do PETRVS e proposta de esquema MySQL para o modelo comum de dados

**Versão:** 1.0 (para aprovação) | **Data:** 26.07.2026
**Série:** AT (Tecnologia) — governança de artefatos da proposta v3, §5.1
**Insumo para:** `proposta-projeto-v4.md` (revisão das decisões de persistência da v3, §3.2–3.3)
**Fontes:** introspecção JDBC do banco `petrvs_icmbio` via Denodo (documentada em
`pgd-ocde-icmbio/docs/07-estrutura-banco-dados.md`, 24.05.2026); artefato
`03_especificacao-funcional-skills_v2.md`, §5 e §16.2; `proposta-projeto-v3.md`, §3.2.

---

## 1. Sumário executivo

A v3 prescreve o modelo comum de dados em **SQLite** (arquivo único, 6 entidades do `03`,
§5) com um serviço mínimo de IDs/versões. Esta análise propõe substituí-lo por um esquema
**MySQL 8** modelado sobre as convenções do banco original do PETRVS — o mesmo SGBD do
sistema-fonte, acessado hoje via Denodo/DBeaver.

A mudança não é cosmética. O PETRVS já resolve, em produção, os mesmos problemas que as
"regras de ouro" da v3 §3.2 tentam resolver: identidade persistente (UUID CHAR(36)),
não-destruição de dados (soft-delete universal), auditoria temporal (created/updated/deleted_at)
e vínculos estratégicos muitos-para-muitos (tabelas `planos_entregas_entregas_resultados_chaves`
etc.). Adotar as mesmas convenções torna o modelo comum **interoperável por construção** com
os dados reais extraídos via Denodo: uma entrega estruturada do agente referencia a
`unidade_id` real do ICMBio, pode ser comparada campo a campo com uma
`planos_entregas_entregas` real e, num cenário futuro, exportada sem tradução de esquema.

O documento está organizado em: análise do PETRVS (§2), mapeamento entidade a entidade
(§3), justificativa e trade-offs da troca SQLite→MySQL (§4), esquema DDL proposto (§5),
implementação das regras de ouro (§6), integração com o Denodo (§7) e impactos na v4 (§8).

---

## 2. Análise da estrutura de dados do PETRVS

### 2.1. Arquitetura em 4 camadas

O banco `petrvs_icmbio` (123 views via Denodo; MySQL 8 na origem Dataprev) organiza-se em:

| Camada | Conteúdo | Tabelas-chave | Volumetria (05/2026) |
| --- | --- | --- | --- |
| 1. Referência | Servidores, unidades, programas, catálogos `tipos_*` | `usuarios` (7.403), `unidades` (811), `programas`, `entregas` (catálogo) | — |
| 2. Planejamento | PEs, PTs, metas, vínculos estratégicos | `planos_entregas` (1.634), `planos_entregas_entregas` (18.831), `planos_trabalhos` (14.168), `planos_trabalhos_entregas` (69.208) | núcleo do negócio |
| 3. Execução | Atividades, consolidações, afastamentos | `atividades` (141.724), `planos_trabalhos_consolidacoes` (40.880), `afastamentos` (7.456) | — |
| 4. Avaliação | Notas, escala de conceitos | `avaliacoes` (26.931), `tipos_avaliacoes_notas` (escala 1–5) | — |

### 2.2. Convenções estruturais do PETRVS (a herdar no modelo comum)

| Convenção | Como o PETRVS implementa | Relevância para o modelo comum |
| --- | --- | --- |
| **Identidade** | PK `id CHAR(36)` UUID em todas as tabelas; nunca inteiro auto-incremento | Regra de ouro 1 (ID persistente) sai de graça; IDs gerados localmente nunca colidem com IDs do PETRVS |
| **Não-destruição** | Soft-delete universal: `deleted_at TIMESTAMP NULL`; dado nunca é apagado fisicamente | Regra de ouro 2 (nunca sobrescrever) — o PETRVS só resolve metade (não apaga, mas **sobrescreve** via UPDATE); o modelo comum completa com versionamento imutável (§6) |
| **Auditoria** | `created_at` / `updated_at` / `deleted_at` em toda tabela de negócio | Base do rastro exigido pelo `03` §17.1 |
| **Status enumerado** | CHAR com enumerações fixas (`INCLUIDO`, `ATIVO`, `CONCLUIDO`, `AVALIADO`…) | Modelar como `ENUM` MySQL nativo — validação no banco |
| **Estruturas flexíveis** | JSON em LONGVARCHAR (`meta`, `realizado`, `checklist`, `criterios_avaliacao`) | Modelar como `JSON` nativo do MySQL 8 (validação `JSON_VALID` automática + colunas geradas) |
| **Métricas** | `DECIMAL(5,2)` para progresso e dedicação (0–100) | Mesmos tipos → comparações diretas sem conversão |
| **Hierarquia** | Autorreferência (`unidades.unidade_pai_id`, `entregas.entrega_pai_id`) + campo `path` materializado | Mesmo padrão para estrutura organizacional do S01 |
| **Vínculos estratégicos** | Tabelas de junção N:N: `planos_entregas_entregas_objetivos`, `..._resultados_chaves`, `..._processos` | O `VinculoOKRD` do `03` §5.5 já existe conceitualmente no PETRVS — copiar a forma |

### 2.3. Estruturas do PETRVS que espelham diretamente as 6 entidades do `03` §5

1. **Entrega estruturada ≈ `planos_entregas_entregas`** (21 colunas): `descricao`,
   `destinatario`, `progresso_esperado/realizado DECIMAL(5,2)`, `meta` JSON
   (`{"quantitativo": N}` ou `{"porcentagem": N}`), `data_inicio/fim`, hierarquia
   (`entrega_pai_id`), vínculo a template de catálogo (`entrega_id`) e à unidade.
2. **Catálogo de entregas (S04) ≈ `entregas`**: templates com `nome`, `descricao`,
   `tipo_indicador`, `checklist`/`etiquetas` JSON, por unidade.
3. **Plano de capacidade (S07) ≈ `planos_trabalhos` + `afastamentos`**: `carga_horaria`
   interpretada por `forma_contagem_carga_horaria` (`HORAS`|`DIAS`×8); afastamentos com
   período e horas parciais.
4. **Matriz de cobertura (S08) ≈ `planos_trabalhos_entregas`**: vínculo servidor×entrega com
   `forca_trabalho DECIMAL(5,2)` (% de esforço 0–100).
5. **OKR-D (S09) ≈ `okrs`, `okrs_objetivos`, `okrs_objetivos_resultados_chaves` +
   `planos_entregas_entregas_resultados_chaves`**: cadeia objetivo→KR→entrega N:N.
6. **Regras institucionais (S01) — sem equivalente**: o PETRVS guarda apenas `programas.normativa`
   (nome da portaria) e configs JSON. A entidade `RegraInstitucional` é genuinamente nova.
   Idem `EntregaCandidata` e `RegistroDeRisco` (novidades do agente).

### 2.4. Lições operacionais do acesso via Denodo (do projeto `pgd-ocde-icmbio`)

- Denodo é **somente leitura** e virtualização: não há como criar tabelas lá; o modelo comum
  precisa de banco próprio de qualquer forma.
- Restrições VQL (sem `DATE()`, sem `DATEDIFF`, sem CTE recursiva, divisão inteira, window
  functions instáveis via JDBC) **não se aplicam** ao banco local — mas as queries de
  espelhamento (§7) devem respeitá-las.
- `tipos_modalidades` é inacessível via Denodo; anomalias de escala em `progresso_esperado`
  (0–1 vs 0–100) e 9 registros com `progresso_realizado < 0` existem em produção — o modelo
  comum deve prever `CHECK`s que o PETRVS não tem.

---

## 3. Mapeamento: modelo comum (`03` §5) × PETRVS × esquema proposto

| Entidade do `03` §5 | Equivalente PETRVS | Tabela(s) proposta(s) | Observação |
| --- | --- | --- | --- |
| 5.1 RegraInstitucional | — (inexistente) | `fontes_institucionais`, `regras_institucionais` + `regras_institucionais_versoes` | Fonte separada da regra (S01-US01 vs US02) |
| 5.2 EntregaCandidata | — (inexistente) | `entregas_candidatas` | Estado próprio (S03-US03); vira `entregas` ao aprovar |
| 5.3 EntregaEstruturada | `planos_entregas_entregas` + catálogo `entregas` | `entregas` + `entregas_versoes` | Campos espelham o PETRVS (`meta` JSON, `destinatario`, `progresso_esperado`); + campos 4Q1P do método |
| 5.4 PlanoDeCapacidade | `planos_trabalhos` + `afastamentos` | `planos_capacidade`, `participantes`, `indisponibilidades`, `alocacoes` | `alocacoes` = matriz S08 (espelha `planos_trabalhos_entregas.forca_trabalho`) |
| 5.5 VinculoOKRD | `..._resultados_chaves` (junção N:N) | `okrd_objetivos`, `okrd_resultados_chave`, `vinculos_okrd` | KR local pode referenciar UUID real do PETRVS (`petrvs_id`) |
| 5.6 RegistroDeRisco | — (inexistente) | `registros_risco` | Tipologia risco/impedimento/dependência/restrição |
| — (governança, v3 §3.1 Camada 4) | — | `execucoes_skill`, `decisoes_humanas`, `perguntas_pendentes` | Implementa o contrato de saída v3 §8.3 e regras de ouro 3–5 |
| — (referência) | `unidades`, `usuarios` | `ref_unidades`, `ref_usuarios` (espelhos Denodo) | §7 — FKs locais apontam para UUIDs reais do ICMBio |

---

## 4. Decisão: SQLite → MySQL 8 — justificativa e trade-offs

### 4.1. Por que MySQL

1. **Paridade de dialeto com o sistema-fonte.** O PETRVS é MySQL 8. Tipos (`CHAR(36)`,
   `DECIMAL(5,2)`, `JSON`), funções e semântica de comparação idênticos — extratos do Denodo
   carregam 1:1 nos espelhos locais, e qualquer query validada contra o espelho vale
   conceitualmente contra a origem.
2. **Ferramental já dominado.** O DBeaver já é a ferramenta padrão do ecossistema; a equipe
   operou MySQL 8 local na fase do dump (tag `v1.0-dump-mysql` do `pgd-ocde-icmbio`) — não é
   tecnologia nova para o projeto.
3. **Recursos ausentes no SQLite necessários ao modelo:** `ENUM` e `CHECK` efetivos, `JSON`
   nativo com validação e colunas geradas, `TIMESTAMP` com timezone-awareness, triggers para
   imutabilidade de versões (§6.3), controle de acesso por usuário do banco (requisito
   `03` §17.3) e concorrência real quando houver mais de um analista.
4. **Interoperabilidade por construção.** As FKs do modelo comum referenciam UUIDs reais do
   ICMBio (unidades, usuários, entregas do PETRVS) — comparações agente×realidade e uma
   eventual exportação futura não exigem camada de tradução.

### 4.2. O que se perde (e mitigação)

| Perda vs. SQLite | Mitigação |
| --- | --- |
| Zero-infraestrutura (arquivo único) | MySQL Community local, serviço Windows único, porta 3306, sem Docker (coerente com o ecossistema); script de instalação documentado no I0 |
| Portabilidade trivial do arquivo | `mysqldump` diário automatizado para pasta com backup (mesmo padrão do `backup_privado.ps1`) |
| Simplicidade da v2/v3 ("migrar só quando doer") | A dor já é conhecida: o requisito de interoperar com um sistema MySQL existe desde o dia 1 — não é especulação de escala |

**Decisão sujeita a ADR:** esta troca revisa os ADRs 001 (persistência SQLite) da v3 §3.3 e
deve ser registrada em `docs/gestao/decisoes/` quando aprovada, motivando a versão 4 da
proposta (conforme v3, nota final).

---

## 5. Esquema MySQL proposto (v1)

### 5.1. Convenções globais

```sql
-- Banco dedicado, charset alinhado ao PETRVS
CREATE DATABASE pgd_agente
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Toda tabela: ENGINE=InnoDB e o "quarteto PETRVS":
--   id         CHAR(36) PRIMARY KEY          (UUID v4 gerado pela aplicação)
--   created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
--   updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP
--   deleted_at TIMESTAMP NULL                (soft-delete; nunca DELETE físico)
```

Regras transversais: snake_case; enums de domínio como `ENUM`; JSON como tipo `JSON`
nativo; graus de confiança sempre `ENUM('alta','media','baixa')`; nenhuma FK física para
objetos do PETRVS — vínculo lógico por UUID com espelho local (§7).

### 5.2. Camada de referência — espelhos do Denodo

```sql
-- Espelho mínimo de unidades (PK = UUID real do PETRVS)
CREATE TABLE ref_unidades (
  id              CHAR(36) PRIMARY KEY,          -- petrvs.unidades.id
  sigla           VARCHAR(100) NOT NULL,
  nome            VARCHAR(256) NOT NULL,
  path            TEXT NULL,                     -- hierarquia materializada
  unidade_pai_id  CHAR(36) NULL,
  executora       TINYINT(1) NOT NULL DEFAULT 0,
  sincronizado_em TIMESTAMP NOT NULL,            -- momento da extração Denodo
  INDEX idx_ref_unidades_sigla (sigla)
) ENGINE=InnoDB;

-- Espelho mínimo de servidores — SOMENTE o necessário (LGPD, v3 §11):
-- sem CPF, sem e-mail, sem dados funcionais sensíveis
CREATE TABLE ref_usuarios (
  id              CHAR(36) PRIMARY KEY,          -- petrvs.usuarios.id
  nome            VARCHAR(256) NOT NULL,
  matricula       VARCHAR(50) NULL,
  participa_pgd   TINYINT(1) NOT NULL DEFAULT 0,
  unidade_id      CHAR(36) NULL,                 -- lotação (ref_unidades)
  sincronizado_em TIMESTAMP NOT NULL
) ENGINE=InnoDB;
```

### 5.3. Configuração institucional — S01/S02

```sql
CREATE TABLE fontes_institucionais (
  id                     CHAR(36) PRIMARY KEY,
  titulo                 VARCHAR(500) NOT NULL,
  tipo_documento         ENUM('portaria','instrucao_normativa','regimento',
                              'cadeia_valor','metodologia','outro') NOT NULL,
  identificacao_oficial  VARCHAR(255) NULL,      -- ex.: "Portaria ICMBio nº 5.592/2025"
  versao_documento       VARCHAR(50) NULL,
  versao_confirmada      TINYINT(1) NOT NULL DEFAULT 0,   -- S01-T02: alerta se 0
  data_publicacao        DATE NULL,
  url_ou_localizacao     VARCHAR(1000) NULL,
  hash_conteudo          CHAR(64) NULL,          -- SHA-256: detecção de duplicidade S01-US01.3
  documento_substituido_id CHAR(36) NULL,        -- S01-US01.4: versão anterior no histórico
  responsavel_cadastro   VARCHAR(256) NOT NULL,
  status                 ENUM('vigente','substituida','pendente_validacao') NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP NULL,
  FOREIGN KEY (documento_substituido_id) REFERENCES fontes_institucionais(id)
) ENGINE=InnoDB;

-- Cabeçalho: identidade estável da regra (regra de ouro 1)
CREATE TABLE regras_institucionais (
  id            CHAR(36) PRIMARY KEY,
  codigo        VARCHAR(20) NOT NULL UNIQUE,     -- "R-014" — citável nas saídas (v3 §8.3)
  versao_atual  INT NOT NULL DEFAULT 1,
  status        ENUM('vigente','revogada','conflitante','pendente') NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP NULL
) ENGINE=InnoDB;

-- Versões imutáveis: INSERT-only (regra de ouro 2; trigger no §6.3)
CREATE TABLE regras_institucionais_versoes (
  id                 CHAR(36) PRIMARY KEY,
  regra_id           CHAR(36) NOT NULL,
  versao             INT NOT NULL,
  titulo             VARCHAR(500) NOT NULL,
  descricao          TEXT NOT NULL,
  natureza           ENUM('norma','regra_institucional',
                          'recomendacao','exemplo') NOT NULL,  -- PA3 / S01-T04
  fonte_id           CHAR(36) NOT NULL,
  localizacao_fonte  VARCHAR(500) NULL,          -- artigo, seção, página
  inicio_vigencia    DATE NULL,
  fim_vigencia       DATE NULL,                  -- S02-US03: verificação por época
  confianca_extracao ENUM('alta','media','baixa') NOT NULL,
  validacao_humana   ENUM('pendente','validada','rejeitada') NOT NULL DEFAULT 'pendente',
  execucao_id        CHAR(36) NULL,              -- rastreio: qual execução gerou (regra 3)
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_regra_versao (regra_id, versao),
  FOREIGN KEY (regra_id) REFERENCES regras_institucionais(id),
  FOREIGN KEY (fonte_id) REFERENCES fontes_institucionais(id)
) ENGINE=InnoDB;

-- Conflitos normativos: registrados, nunca resolvidos automaticamente (S01-T03)
CREATE TABLE regras_conflitos (
  id           CHAR(36) PRIMARY KEY,
  regra_a_id   CHAR(36) NOT NULL,
  regra_b_id   CHAR(36) NOT NULL,
  descricao    TEXT NOT NULL,
  status       ENUM('aberto','resolvido') NOT NULL DEFAULT 'aberto',
  decisao_id   CHAR(36) NULL,                    -- FK → decisoes_humanas
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (regra_a_id) REFERENCES regras_institucionais(id),
  FOREIGN KEY (regra_b_id) REFERENCES regras_institucionais(id)
) ENGINE=InnoDB;
```

### 5.4. Portfólio — S03/S04/S05/S06

```sql
CREATE TABLE entregas_candidatas (
  id                  CHAR(36) PRIMARY KEY,
  texto_origem        TEXT NOT NULL,
  fonte_id            CHAR(36) NOT NULL,
  localizacao_fonte   VARCHAR(500) NULL,         -- S03-US01.1: vínculo com o trecho
  classificacao       ENUM('entrega','objetivo','atividade',
                           'tarefa','responsabilidade') NOT NULL,
  titulo_sugerido     VARCHAR(500) NULL,
  justificativa       TEXT NOT NULL,
  confianca           ENUM('alta','media','baixa') NOT NULL,
  estado              ENUM('pendente','aprovada','rejeitada',
                           'agrupada') NOT NULL DEFAULT 'pendente',   -- S03-US03.1
  justificativa_estado TEXT NULL,                -- S03-US03.2
  candidata_agrupadora_id CHAR(36) NULL,         -- quando agrupada
  entrega_id          CHAR(36) NULL,             -- preenchido ao aprovar (S03-T06)
  execucao_id         CHAR(36) NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP NULL,
  FOREIGN KEY (fonte_id) REFERENCES fontes_institucionais(id)
) ENGINE=InnoDB;

-- Cabeçalho da entrega estruturada / item de catálogo (S04)
CREATE TABLE entregas (
  id             CHAR(36) PRIMARY KEY,
  codigo         VARCHAR(20) NOT NULL UNIQUE,    -- "ENT-2026-0001"
  versao_atual   INT NOT NULL DEFAULT 1,
  estado         ENUM('rascunho','em_validacao','publicada',
                      'arquivada') NOT NULL DEFAULT 'rascunho',  -- S04-T06
  unidade_id     CHAR(36) NULL,                  -- ref_unidades (UUID real ICMBio)
  candidata_origem_id  CHAR(36) NULL,            -- rastreabilidade INT-T01
  entrega_referencia_id CHAR(36) NULL,           -- S04-T05: modelo reutilizado
  petrvs_entrega_id     CHAR(36) NULL,           -- planos_entregas_entregas.id real (comparação)
  petrvs_catalogo_id    CHAR(36) NULL,           -- entregas.id real (template PETRVS)
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP NULL,
  FOREIGN KEY (entrega_referencia_id) REFERENCES entregas(id)
) ENGINE=InnoDB;

-- Payload versionado e imutável — campos espelham planos_entregas_entregas + 4Q1P
CREATE TABLE entregas_versoes (
  id                  CHAR(36) PRIMARY KEY,
  entrega_id          CHAR(36) NOT NULL,
  versao              INT NOT NULL,
  titulo              VARCHAR(500) NOT NULL,
  descricao           TEXT NULL,
  forma_geracao       ENUM('projeto','processo') NOT NULL,
  natureza_resultado  ENUM('produto','servico') NOT NULL,
  demandante          VARCHAR(500) NOT NULL,
  destinatario        VARCHAR(500) NOT NULL,     -- mesmo conceito do PETRVS
  meta                JSON NOT NULL,             -- compatível PETRVS: {"quantitativo":N}
                                                 -- ou {"porcentagem":N} + extensões
  meta_final          JSON NULL,                 -- PA1: meta final ≠ progresso do ciclo
  progresso_esperado  DECIMAL(5,2) NULL
                      CHECK (progresso_esperado BETWEEN 0 AND 100),  -- evita anomalia 0–1
  prazo_inicio        DATE NULL,
  prazo_fim           DATE NOT NULL,
  criterios_aceite    JSON NULL,                 -- lista (S05-US03)
  evidencias_esperadas JSON NULL,
  motivo_versao       VARCHAR(500) NOT NULL,     -- por que esta versão existe
  execucao_id         CHAR(36) NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_entrega_versao (entrega_id, versao),
  FOREIGN KEY (entrega_id) REFERENCES entregas(id)
) ENGINE=InnoDB;
```

### 5.5. Viabilidade — S07/S08

```sql
CREATE TABLE planos_capacidade (
  id            CHAR(36) PRIMARY KEY,
  unidade_id    CHAR(36) NOT NULL,               -- ref_unidades
  periodo_inicio DATE NOT NULL,
  periodo_fim    DATE NOT NULL,
  atividades_indiretas_perc DECIMAL(5,2) NULL,   -- PA2: parâmetro, alerta — não proibição
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP NULL
) ENGINE=InnoDB;

CREATE TABLE participantes (
  id                 CHAR(36) PRIMARY KEY,
  plano_capacidade_id CHAR(36) NOT NULL,
  usuario_id         CHAR(36) NULL,              -- ref_usuarios (real) OU NULL se sintético
  rotulo             VARCHAR(100) NOT NULL,      -- pseudônimo p/ relatórios (LGPD, v3 §11)
  carga_horaria      DECIMAL(7,2) NOT NULL,      -- convenção PETRVS
  forma_contagem     ENUM('HORAS','DIAS') NOT NULL DEFAULT 'HORAS',
  externo            TINYINT(1) NOT NULL DEFAULT 0,   -- S08-T05
  unidade_origem_id  CHAR(36) NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP NULL,
  FOREIGN KEY (plano_capacidade_id) REFERENCES planos_capacidade(id)
) ENGINE=InnoDB;

-- Espelha 'afastamentos' do PETRVS; motivo NUNCA detalhado (v3 §11.1)
CREATE TABLE indisponibilidades (
  id             CHAR(36) PRIMARY KEY,
  participante_id CHAR(36) NOT NULL,
  data_inicio    DATE NOT NULL,
  data_fim       DATE NOT NULL,
  horas          DECIMAL(7,2) NULL,              -- parcial, como no PETRVS
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP NULL,
  FOREIGN KEY (participante_id) REFERENCES participantes(id)
) ENGINE=InnoDB;

-- Matriz S08 — espelha planos_trabalhos_entregas.forca_trabalho
CREATE TABLE alocacoes (
  id              CHAR(36) PRIMARY KEY,
  participante_id CHAR(36) NOT NULL,
  entrega_id      CHAR(36) NOT NULL,
  esforco_perc    DECIMAL(5,2) NOT NULL
                  CHECK (esforco_perc > 0 AND esforco_perc <= 100),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP NULL,
  UNIQUE KEY uk_aloc (participante_id, entrega_id),
  FOREIGN KEY (participante_id) REFERENCES participantes(id),
  FOREIGN KEY (entrega_id) REFERENCES entregas(id)
) ENGINE=InnoDB;
-- Totalização = 100% por participante: validador Python (cálculo determinístico,
-- exatidão 100% — v3 §3.3), não constraint, para permitir estados intermediários.
```

### 5.6. Estratégia e riscos — S09/S10

```sql
CREATE TABLE okrd_objetivos (
  id          CHAR(36) PRIMARY KEY,
  descricao   TEXT NOT NULL,
  petrvs_id   CHAR(36) NULL,        -- okrs_objetivos.id real, quando importado
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP NULL
) ENGINE=InnoDB;

CREATE TABLE okrd_resultados_chave (
  id          CHAR(36) PRIMARY KEY,
  objetivo_id CHAR(36) NOT NULL,
  descricao   TEXT NOT NULL,
  medida      VARCHAR(500) NULL,    -- S09-US01.2: medida de avanço
  petrvs_id   CHAR(36) NULL,        -- okrs_objetivos_resultados_chaves.id real
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP NULL,
  FOREIGN KEY (objetivo_id) REFERENCES okrd_objetivos(id)
) ENGINE=InnoDB;

-- N:N preservado (S09-T06) — mesma forma de planos_entregas_entregas_resultados_chaves
CREATE TABLE vinculos_okrd (
  id                   CHAR(36) PRIMARY KEY,
  resultado_chave_id   CHAR(36) NOT NULL,
  entrega_id           CHAR(36) NOT NULL,
  tipo_contribuicao    ENUM('direta','indireta','contextual') NOT NULL,
  forca_contribuicao   ENUM('alta','media','baixa') NOT NULL,
  justificativa        TEXT NOT NULL,            -- obrigatória (RP07: nunca causalidade)
  evidencia_logica     TEXT NULL,
  validacao_humana     ENUM('pendente','validada','rejeitada') NOT NULL DEFAULT 'pendente',
  execucao_id          CHAR(36) NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP NULL,
  UNIQUE KEY uk_vinculo (resultado_chave_id, entrega_id),
  FOREIGN KEY (resultado_chave_id) REFERENCES okrd_resultados_chave(id),
  FOREIGN KEY (entrega_id) REFERENCES entregas(id)
) ENGINE=InnoDB;

CREATE TABLE registros_risco (
  id            CHAR(36) PRIMARY KEY,
  entrega_id    CHAR(36) NOT NULL,
  tipo          ENUM('risco','impedimento','dependencia','restricao') NOT NULL,
  causa         TEXT NULL,
  evento        TEXT NOT NULL,
  impacto       TEXT NULL,                       -- ausência gera pergunta, não preenchimento
  probabilidade TINYINT NULL CHECK (probabilidade BETWEEN 1 AND 5),
  severidade    TINYINT NULL CHECK (severidade BETWEEN 1 AND 5),
  resposta      TEXT NULL,
  responsavel   VARCHAR(256) NULL,
  origem_externa VARCHAR(500) NULL,              -- S10-US03: dependências
  data_necessaria DATE NULL,
  prazo_revisao DATE NULL,
  status        ENUM('aberto','mitigado','materializado',
                     'encerrado') NOT NULL DEFAULT 'aberto',
  execucao_id   CHAR(36) NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP NULL,
  FOREIGN KEY (entrega_id) REFERENCES entregas(id)
) ENGINE=InnoDB;
```

### 5.7. Governança transversal — regras de ouro 3, 4 e 5

```sql
-- Toda execução de skill: implementa o contrato v3 §8.3 (regra de ouro 3)
CREATE TABLE execucoes_skill (
  id             CHAR(36) PRIMARY KEY,           -- = rastreio_id do contrato
  skill          VARCHAR(10) NOT NULL,           -- 'S01'...'S10'
  versao_skill   VARCHAR(20) NOT NULL,
  modelo         VARCHAR(100) NULL,              -- NULL em cálculo determinístico puro
  entrada        JSON NOT NULL,
  saida          JSON NOT NULL,                  -- saída integral (reprodutibilidade 17.5)
  confianca      ENUM('alta','media','baixa') NULL,
  regras_aplicadas JSON NULL,                    -- ["R-014","R-022"]
  fontes         JSON NULL,
  requer_validacao_humana TINYINT(1) NOT NULL DEFAULT 0,
  duracao_ms     INT NULL,
  executado_em   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Decisões humanas separadas das sugestões (regra de ouro 4)
CREATE TABLE decisoes_humanas (
  id           CHAR(36) PRIMARY KEY,
  objeto_tipo  ENUM('fonte','regra','candidata','entrega','plano_capacidade',
                    'vinculo_okrd','risco','conflito') NOT NULL,
  objeto_id    CHAR(36) NOT NULL,
  objeto_versao INT NULL,
  decisao      ENUM('aprovado','rejeitado','ajustado','justificado') NOT NULL,
  justificativa TEXT NULL,
  decidido_por VARCHAR(256) NOT NULL,
  execucao_id  CHAR(36) NULL,                    -- sugestão que motivou (se houver)
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Dados ausentes viram perguntas registradas (regra de ouro 5; INT-T08)
CREATE TABLE perguntas_pendentes (
  id           CHAR(36) PRIMARY KEY,
  objeto_tipo  VARCHAR(30) NOT NULL,
  objeto_id    CHAR(36) NOT NULL,
  pergunta     TEXT NOT NULL,
  execucao_id  CHAR(36) NOT NULL,
  status       ENUM('aberta','respondida','descartada') NOT NULL DEFAULT 'aberta',
  resposta     TEXT NULL,
  respondido_por VARCHAR(256) NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Controle de evolução do próprio esquema
CREATE TABLE schema_migracoes (
  versao      VARCHAR(20) PRIMARY KEY,           -- '001', '002'...
  descricao   VARCHAR(500) NOT NULL,
  aplicado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
```

---

## 6. Serviço de IDs e versões — implementação das regras de ouro

### 6.1. Padrão cabeçalho + versões

Entidades que evoluem (`regras_institucionais`, `entregas`) usam duas tabelas: o
**cabeçalho** guarda a identidade estável (UUID, código citável, estado, `versao_atual`);
as **versões** guardam o payload completo, INSERT-only. Nenhuma skill referencia payload —
sempre `(id, versao)`. Consulta do estado atual:

```sql
SELECT e.codigo, v.*
FROM entregas e
JOIN entregas_versoes v ON v.entrega_id = e.id AND v.versao = e.versao_atual
WHERE e.deleted_at IS NULL;
```

### 6.2. Serviço Python (`src/dados/versoes.py`)

- `novo_id()` → UUID v4; `novo_codigo(prefixo)` → sequencial legível (`ENT-2026-0001`).
- `nova_versao(entidade, id, payload, motivo, execucao_id)` → transação: INSERT em
  `*_versoes` com `versao = versao_atual + 1` + UPDATE do cabeçalho. Única via de escrita.
- `registrar_execucao(...)`, `registrar_decisao(...)`, `registrar_pergunta(...)` —
  chamados pelo motor de skills, nunca opcionais.

### 6.3. Imutabilidade garantida no banco (não só na aplicação)

```sql
CREATE TRIGGER trg_entregas_versoes_imutavel
BEFORE UPDATE ON entregas_versoes
FOR EACH ROW
  SIGNAL SQLSTATE '45000'
  SET MESSAGE_TEXT = 'Versões são imutáveis — crie nova versão (regra de ouro 2)';
-- idem para DELETE e para regras_institucionais_versoes / execucoes_skill
```

Isso é o que o SQLite não oferecia com a mesma robustez: mesmo um script com bug não
consegue sobrescrever histórico.

---

## 7. Integração com o Denodo — espelhos `ref_*`

1. **Sem FK física entre bancos.** O Denodo é virtualização somente-leitura; os vínculos
   com objetos do PETRVS são lógicos (UUID armazenado) + espelho local para integridade.
2. **Rotina de sincronização** (`src/dados/sincronizar_ref.py`): reutiliza o padrão
   `run_query()`/JDBC do `pgd-ocde-icmbio`; extrai `unidades` (811 linhas) e o subconjunto
   mínimo de `usuarios` (apenas participantes do piloto), gravando `sincronizado_em`.
   Queries respeitam as restrições VQL documentadas (CAST em datas, sem window functions).
3. **LGPD:** o espelho de usuários exclui CPF, e-mail e situação funcional; relatórios usam
   `participantes.rotulo` (pseudônimo). Alinhado à v3 §11.1.
4. **Comparação agente × realidade:** os campos `petrvs_entrega_id` / `petrvs_catalogo_id`
   permitem, no piloto (I7), confrontar uma entrega redigida via S03–S05 com a entrega real
   correspondente no PETRVS — evidência direta para a rubrica de qualidade (`03` §18.8).

---

## 8. Impactos na proposta v4 (itens a revisar quando aprovado)

| Item da v3 | Mudança na v4 |
| --- | --- |
| §3.2 — "persistência em SQLite local" | MySQL 8 Community local (sem Docker); `schema.sql` v1 = §5 deste documento |
| §3.3 — tabela de stack, linha "Persistência" | Atualizar recomendação + justificativa (paridade com PETRVS); registrar ADR de reversão da decisão SQLite |
| §6.2 — I0, entregável T | "`schema.sql` v1 do modelo comum **em MySQL** (18 tabelas: 6 entidades do `03` §5 + versões + governança + espelhos `ref_*`); serviço de IDs/versões com triggers de imutabilidade; rotina `sincronizar_ref.py`" |
| §7 — estrutura do repositório | `data/pgd_agente.db` → instância MySQL local; `.gitignore` cobre dumps (`*.sql` de dados) e `.env` com credenciais do MySQL |
| §10 — riscos | RP13 (perda de IDs/histórico) ganha mitigação mais forte (trigger §6.3); acrescentar risco novo: indisponibilidade do serviço MySQL local (mitigação: `mysqldump` diário + script de reinstalação documentado) |
| §11 — governança de dados | Explicitar política do espelho `ref_usuarios` (campos mínimos, sem CPF) |
| §12 — checklist I0 | Atualizar itens de aceite: banco criado, triggers ativos, sincronização `ref_unidades` executada |

### Decisões que dependem de aprovação do coordenador

1. **D1 — Trocar SQLite por MySQL 8 local** (recomendado; motivo central deste documento).
2. **D2 — Escopo do espelho `ref_usuarios`**: sincronizar só participantes da unidade-piloto
   (recomendado) ou todos os 7.403 servidores.
3. **D3 — Codigos legíveis** (`R-014`, `ENT-2026-0001`) além do UUID (recomendado — melhora
   citabilidade nas saídas das skills).
4. **D4 — MySQL Community instalado como serviço Windows** (recomendado, coerente com
   "sem Docker") ou outra forma de provisionamento.

---

*Após aprovação deste AT-01, gerar `proposta-projeto-v4.md` incorporando as mudanças da
Seção 8, registrar o ADR correspondente em `docs/gestao/decisoes/` e materializar o §5 em
`src/dados/schema.sql`.*
