-- ============================================================================
-- schema.sql — Modelo comum de dados do pgd-agente-icmbio (v1 / migração 001)
--
-- Materializa o AT-01 §5 (docs/tecnologia/AT-01_analise-petrvs-esquema-mysql_v1.md),
-- aprovado em 26.07.2026 com as decisões D1–D4 (ADR-006). 21 tabelas.
--
-- Convenções herdadas do PETRVS: PK UUID CHAR(36) gerado pela aplicação;
-- soft-delete (deleted_at); auditoria created_at/updated_at; ENUM para status;
-- JSON nativo; DECIMAL(5,2) para métricas. Nenhuma FK física para objetos do
-- PETRVS — vínculo lógico por UUID + espelhos ref_* (AT-01 §7).
--
-- Regras de ouro (03 §16.2 / v4 §3.2): versões são INSERT-only — triggers
-- rejeitam UPDATE/DELETE em *_versoes e execucoes_skill (AT-01 §6.3).
--
-- Execução: mysql -u <usuario> -p < schema.sql
--   (todos os triggers são statements únicos — não requer DELIMITER)
-- ============================================================================

CREATE DATABASE IF NOT EXISTS pgd_agente
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE pgd_agente;

-- ============================================================================
-- GRUPO 0 — Controle do esquema
-- ============================================================================

CREATE TABLE schema_migracoes (
  versao      VARCHAR(20) PRIMARY KEY,
  descricao   VARCHAR(500) NOT NULL,
  aplicado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================================
-- GRUPO 1 — Governança transversal (regras de ouro 3, 4 e 5)
-- Criado primeiro: as demais tabelas referenciam execucoes_skill.
-- ============================================================================

-- Toda execução de skill: implementa o contrato v4 §8.3 (regra de ouro 3).
-- id = rastreio_id do contrato. INSERT-only (triggers abaixo).
CREATE TABLE execucoes_skill (
  id             CHAR(36) PRIMARY KEY,
  skill          VARCHAR(10) NOT NULL,            -- 'S01'...'S10'
  versao_skill   VARCHAR(20) NOT NULL,
  modelo         VARCHAR(100) NULL,               -- NULL em cálculo determinístico puro
  entrada        JSON NOT NULL,
  saida          JSON NOT NULL,                   -- saída integral (reprodutibilidade 03 §17.5)
  confianca      ENUM('alta','media','baixa') NULL,
  regras_aplicadas JSON NULL,                     -- ["R-014","R-022"]
  fontes         JSON NULL,
  requer_validacao_humana TINYINT(1) NOT NULL DEFAULT 0,
  duracao_ms     INT NULL,
  executado_em   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_execucoes_skill (skill, executado_em)
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
  execucao_id  CHAR(36) NULL,                     -- sugestão que motivou (se houver)
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_decisoes_objeto (objeto_tipo, objeto_id),
  CONSTRAINT fk_decisao_execucao FOREIGN KEY (execucao_id)
    REFERENCES execucoes_skill(id)
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
  updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_perguntas_objeto (objeto_tipo, objeto_id),
  INDEX idx_perguntas_status (status),
  CONSTRAINT fk_pergunta_execucao FOREIGN KEY (execucao_id)
    REFERENCES execucoes_skill(id)
) ENGINE=InnoDB;

-- ============================================================================
-- GRUPO 2 — Referência espelhada (Denodo → local; AT-01 §7)
-- PK = UUID real do PETRVS/ICMBio. Populada por src/dados/sincronizar_ref.py.
-- ============================================================================

CREATE TABLE ref_unidades (
  id              CHAR(36) PRIMARY KEY,           -- petrvs.unidades.id
  sigla           VARCHAR(100) NOT NULL,
  nome            VARCHAR(256) NOT NULL,
  path            TEXT NULL,                      -- hierarquia materializada
  unidade_pai_id  CHAR(36) NULL,
  executora       TINYINT(1) NOT NULL DEFAULT 0,
  sincronizado_em TIMESTAMP NOT NULL,             -- momento da extração Denodo
  INDEX idx_ref_unidades_sigla (sigla)
) ENGINE=InnoDB;

-- Espelho mínimo de servidores — SOMENTE unidade-piloto (D2, LGPD, v4 §11):
-- sem CPF, sem e-mail, sem situação funcional.
CREATE TABLE ref_usuarios (
  id              CHAR(36) PRIMARY KEY,           -- petrvs.usuarios.id
  nome            VARCHAR(256) NOT NULL,
  matricula       VARCHAR(50) NULL,
  participa_pgd   TINYINT(1) NOT NULL DEFAULT 0,
  unidade_id      CHAR(36) NULL,                  -- lotação (ref_unidades)
  sincronizado_em TIMESTAMP NOT NULL
) ENGINE=InnoDB;

-- ============================================================================
-- GRUPO 3 — Configuração institucional (S01/S02; entidade 03 §5.1)
-- ============================================================================

CREATE TABLE fontes_institucionais (
  id                     CHAR(36) PRIMARY KEY,
  titulo                 VARCHAR(500) NOT NULL,
  tipo_documento         ENUM('portaria','instrucao_normativa','regimento',
                              'cadeia_valor','metodologia','outro') NOT NULL,
  identificacao_oficial  VARCHAR(255) NULL,       -- ex.: "Portaria ICMBio nº 5.592/2025"
  versao_documento       VARCHAR(50) NULL,
  versao_confirmada      TINYINT(1) NOT NULL DEFAULT 0,   -- S01-T02: alerta se 0
  data_publicacao        DATE NULL,
  url_ou_localizacao     VARCHAR(1000) NULL,
  hash_conteudo          CHAR(64) NULL,           -- SHA-256: duplicidade S01-US01.3
  documento_substituido_id CHAR(36) NULL,         -- S01-US01.4: histórico preservado
  responsavel_cadastro   VARCHAR(256) NOT NULL,
  status                 ENUM('vigente','substituida','pendente_validacao') NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP NULL,
  CONSTRAINT fk_fonte_substituida FOREIGN KEY (documento_substituido_id)
    REFERENCES fontes_institucionais(id)
) ENGINE=InnoDB;

-- Cabeçalho: identidade estável da regra (regra de ouro 1)
CREATE TABLE regras_institucionais (
  id            CHAR(36) PRIMARY KEY,
  codigo        VARCHAR(20) NOT NULL UNIQUE,      -- "R-014" (D3) — citável nas saídas
  versao_atual  INT NOT NULL DEFAULT 1,
  status        ENUM('vigente','revogada','conflitante','pendente') NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP NULL
) ENGINE=InnoDB;

-- Versões imutáveis: INSERT-only (regra de ouro 2; triggers ao final)
CREATE TABLE regras_institucionais_versoes (
  id                 CHAR(36) PRIMARY KEY,
  regra_id           CHAR(36) NOT NULL,
  versao             INT NOT NULL,
  titulo             VARCHAR(500) NOT NULL,
  descricao          TEXT NOT NULL,
  natureza           ENUM('norma','regra_institucional',
                          'recomendacao','exemplo') NOT NULL,   -- PA3 / S01-T04
  fonte_id           CHAR(36) NOT NULL,
  localizacao_fonte  VARCHAR(500) NULL,           -- artigo, seção, página
  inicio_vigencia    DATE NULL,
  fim_vigencia       DATE NULL,                   -- S02-US03: verificação por época
  confianca_extracao ENUM('alta','media','baixa') NOT NULL,
  validacao_humana   ENUM('pendente','validada','rejeitada') NOT NULL DEFAULT 'pendente',
  execucao_id        CHAR(36) NULL,               -- qual execução gerou (regra de ouro 3)
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_regra_versao (regra_id, versao),
  CONSTRAINT fk_rv_regra FOREIGN KEY (regra_id) REFERENCES regras_institucionais(id),
  CONSTRAINT fk_rv_fonte FOREIGN KEY (fonte_id) REFERENCES fontes_institucionais(id),
  CONSTRAINT fk_rv_execucao FOREIGN KEY (execucao_id) REFERENCES execucoes_skill(id)
) ENGINE=InnoDB;

-- Conflitos normativos: registrados, nunca resolvidos automaticamente (S01-T03)
CREATE TABLE regras_conflitos (
  id           CHAR(36) PRIMARY KEY,
  regra_a_id   CHAR(36) NOT NULL,
  regra_b_id   CHAR(36) NOT NULL,
  descricao    TEXT NOT NULL,
  status       ENUM('aberto','resolvido') NOT NULL DEFAULT 'aberto',
  decisao_id   CHAR(36) NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_conflito_regra_a FOREIGN KEY (regra_a_id) REFERENCES regras_institucionais(id),
  CONSTRAINT fk_conflito_regra_b FOREIGN KEY (regra_b_id) REFERENCES regras_institucionais(id),
  CONSTRAINT fk_conflito_decisao FOREIGN KEY (decisao_id) REFERENCES decisoes_humanas(id)
) ENGINE=InnoDB;

-- ============================================================================
-- GRUPO 4 — Portfólio (S03–S06; entidades 03 §5.2 e §5.3)
-- ============================================================================

CREATE TABLE entregas_candidatas (
  id                  CHAR(36) PRIMARY KEY,
  texto_origem        TEXT NOT NULL,
  fonte_id            CHAR(36) NOT NULL,
  localizacao_fonte   VARCHAR(500) NULL,          -- S03-US01.1: vínculo com o trecho
  classificacao       ENUM('entrega','objetivo','atividade',
                           'tarefa','responsabilidade') NOT NULL,
  titulo_sugerido     VARCHAR(500) NULL,
  justificativa       TEXT NOT NULL,
  confianca           ENUM('alta','media','baixa') NOT NULL,
  estado              ENUM('pendente','aprovada','rejeitada',
                           'agrupada') NOT NULL DEFAULT 'pendente',  -- S03-US03.1
  justificativa_estado TEXT NULL,                 -- S03-US03.2
  candidata_agrupadora_id CHAR(36) NULL,
  entrega_id          CHAR(36) NULL,              -- preenchido ao aprovar (S03-T06);
                                                  -- FK adicionada após CREATE de entregas
  execucao_id         CHAR(36) NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP NULL,
  INDEX idx_candidatas_estado (estado),
  CONSTRAINT fk_cand_fonte FOREIGN KEY (fonte_id) REFERENCES fontes_institucionais(id),
  CONSTRAINT fk_cand_agrupadora FOREIGN KEY (candidata_agrupadora_id)
    REFERENCES entregas_candidatas(id),
  CONSTRAINT fk_cand_execucao FOREIGN KEY (execucao_id) REFERENCES execucoes_skill(id)
) ENGINE=InnoDB;

-- Cabeçalho da entrega estruturada / item de catálogo (S04)
CREATE TABLE entregas (
  id             CHAR(36) PRIMARY KEY,
  codigo         VARCHAR(20) NOT NULL UNIQUE,     -- "ENT-2026-0001" (D3)
  versao_atual   INT NOT NULL DEFAULT 1,
  estado         ENUM('rascunho','em_validacao','publicada',
                      'arquivada') NOT NULL DEFAULT 'rascunho',   -- S04-T06
  unidade_id     CHAR(36) NULL,                   -- ref_unidades (UUID real ICMBio)
  candidata_origem_id   CHAR(36) NULL,            -- rastreabilidade INT-T01
  entrega_referencia_id CHAR(36) NULL,            -- S04-T05: modelo reutilizado
  petrvs_entrega_id     CHAR(36) NULL,            -- planos_entregas_entregas.id real
  petrvs_catalogo_id    CHAR(36) NULL,            -- entregas.id real (template PETRVS)
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP NULL,
  INDEX idx_entregas_estado (estado),
  CONSTRAINT fk_entrega_candidata FOREIGN KEY (candidata_origem_id)
    REFERENCES entregas_candidatas(id),
  CONSTRAINT fk_entrega_referencia FOREIGN KEY (entrega_referencia_id)
    REFERENCES entregas(id)
) ENGINE=InnoDB;

-- FK cruzada candidata → entrega (criada após ambas existirem)
ALTER TABLE entregas_candidatas
  ADD CONSTRAINT fk_cand_entrega FOREIGN KEY (entrega_id) REFERENCES entregas(id);

-- Payload versionado e imutável — espelha planos_entregas_entregas + 4Q1P
CREATE TABLE entregas_versoes (
  id                  CHAR(36) PRIMARY KEY,
  entrega_id          CHAR(36) NOT NULL,
  versao              INT NOT NULL,
  titulo              VARCHAR(500) NOT NULL,
  descricao           TEXT NULL,
  forma_geracao       ENUM('projeto','processo') NOT NULL,
  natureza_resultado  ENUM('produto','servico') NOT NULL,
  demandante          VARCHAR(500) NOT NULL,
  destinatario        VARCHAR(500) NOT NULL,      -- mesmo conceito do PETRVS
  meta                JSON NOT NULL,              -- compatível PETRVS:
                                                  -- {"quantitativo":N} ou {"porcentagem":N}
  meta_final          JSON NULL,                  -- PA1: meta final ≠ progresso do ciclo
  progresso_esperado  DECIMAL(5,2) NULL
                      CHECK (progresso_esperado BETWEEN 0 AND 100),  -- evita anomalia 0–1
  prazo_inicio        DATE NULL,
  prazo_fim           DATE NOT NULL,
  criterios_aceite    JSON NULL,                  -- lista (S05-US03)
  evidencias_esperadas JSON NULL,
  motivo_versao       VARCHAR(500) NOT NULL,      -- por que esta versão existe
  execucao_id         CHAR(36) NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_entrega_versao (entrega_id, versao),
  CONSTRAINT fk_ev_entrega FOREIGN KEY (entrega_id) REFERENCES entregas(id),
  CONSTRAINT fk_ev_execucao FOREIGN KEY (execucao_id) REFERENCES execucoes_skill(id)
) ENGINE=InnoDB;

-- ============================================================================
-- GRUPO 5 — Viabilidade (S07/S08; entidade 03 §5.4)
-- ============================================================================

CREATE TABLE planos_capacidade (
  id             CHAR(36) PRIMARY KEY,
  unidade_id     CHAR(36) NOT NULL,               -- ref_unidades
  periodo_inicio DATE NOT NULL,
  periodo_fim    DATE NOT NULL,
  atividades_indiretas_perc DECIMAL(5,2) NULL,    -- PA2: parâmetro/alerta, não proibição
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP NULL
) ENGINE=InnoDB;

CREATE TABLE participantes (
  id                  CHAR(36) PRIMARY KEY,
  plano_capacidade_id CHAR(36) NOT NULL,
  usuario_id          CHAR(36) NULL,              -- ref_usuarios (real) OU NULL se sintético
  rotulo              VARCHAR(100) NOT NULL,      -- pseudônimo p/ relatórios (LGPD, v4 §11)
  carga_horaria       DECIMAL(7,2) NOT NULL,      -- convenção PETRVS
  forma_contagem      ENUM('HORAS','DIAS') NOT NULL DEFAULT 'HORAS',
  externo             TINYINT(1) NOT NULL DEFAULT 0,   -- S08-T05
  unidade_origem_id   CHAR(36) NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP NULL,
  CONSTRAINT fk_part_plano FOREIGN KEY (plano_capacidade_id)
    REFERENCES planos_capacidade(id)
) ENGINE=InnoDB;

-- Espelha 'afastamentos' do PETRVS; motivo NUNCA detalhado (v4 §11.1)
CREATE TABLE indisponibilidades (
  id              CHAR(36) PRIMARY KEY,
  participante_id CHAR(36) NOT NULL,
  data_inicio     DATE NOT NULL,
  data_fim        DATE NOT NULL,
  horas           DECIMAL(7,2) NULL,              -- parcial, como no PETRVS
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP NULL,
  CONSTRAINT fk_indisp_participante FOREIGN KEY (participante_id)
    REFERENCES participantes(id)
) ENGINE=InnoDB;

-- Matriz S08 — espelha planos_trabalhos_entregas.forca_trabalho.
-- Totalização = 100% por participante: validador Python (determinístico,
-- exatidão 100% — v4 §3.3), não constraint, para permitir estados intermediários.
CREATE TABLE alocacoes (
  id              CHAR(36) PRIMARY KEY,
  participante_id CHAR(36) NOT NULL,
  entrega_id      CHAR(36) NOT NULL,
  esforco_perc    DECIMAL(5,2) NOT NULL
                  CHECK (esforco_perc > 0 AND esforco_perc <= 100),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP NULL,
  UNIQUE KEY uk_aloc (participante_id, entrega_id),
  CONSTRAINT fk_aloc_participante FOREIGN KEY (participante_id)
    REFERENCES participantes(id),
  CONSTRAINT fk_aloc_entrega FOREIGN KEY (entrega_id) REFERENCES entregas(id)
) ENGINE=InnoDB;

-- ============================================================================
-- GRUPO 6 — Estratégia e riscos (S09/S10; entidades 03 §5.5 e §5.6)
-- ============================================================================

CREATE TABLE okrd_objetivos (
  id          CHAR(36) PRIMARY KEY,
  descricao   TEXT NOT NULL,
  petrvs_id   CHAR(36) NULL,                      -- okrs_objetivos.id real, se importado
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP NULL
) ENGINE=InnoDB;

CREATE TABLE okrd_resultados_chave (
  id          CHAR(36) PRIMARY KEY,
  objetivo_id CHAR(36) NOT NULL,
  descricao   TEXT NOT NULL,
  medida      VARCHAR(500) NULL,                  -- S09-US01.2: medida de avanço
  petrvs_id   CHAR(36) NULL,                      -- okrs_objetivos_resultados_chaves.id real
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP NULL,
  CONSTRAINT fk_kr_objetivo FOREIGN KEY (objetivo_id) REFERENCES okrd_objetivos(id)
) ENGINE=InnoDB;

-- N:N preservado (S09-T06) — mesma forma de planos_entregas_entregas_resultados_chaves
CREATE TABLE vinculos_okrd (
  id                 CHAR(36) PRIMARY KEY,
  resultado_chave_id CHAR(36) NOT NULL,
  entrega_id         CHAR(36) NOT NULL,
  tipo_contribuicao  ENUM('direta','indireta','contextual') NOT NULL,
  forca_contribuicao ENUM('alta','media','baixa') NOT NULL,
  justificativa      TEXT NOT NULL,               -- obrigatória (RP07: nunca causalidade)
  evidencia_logica   TEXT NULL,
  validacao_humana   ENUM('pendente','validada','rejeitada') NOT NULL DEFAULT 'pendente',
  execucao_id        CHAR(36) NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP NULL,
  UNIQUE KEY uk_vinculo (resultado_chave_id, entrega_id),
  CONSTRAINT fk_vinc_kr FOREIGN KEY (resultado_chave_id)
    REFERENCES okrd_resultados_chave(id),
  CONSTRAINT fk_vinc_entrega FOREIGN KEY (entrega_id) REFERENCES entregas(id),
  CONSTRAINT fk_vinc_execucao FOREIGN KEY (execucao_id) REFERENCES execucoes_skill(id)
) ENGINE=InnoDB;

CREATE TABLE registros_risco (
  id              CHAR(36) PRIMARY KEY,
  entrega_id      CHAR(36) NOT NULL,
  tipo            ENUM('risco','impedimento','dependencia','restricao') NOT NULL,
  causa           TEXT NULL,
  evento          TEXT NOT NULL,
  impacto         TEXT NULL,                      -- ausência gera pergunta, não preenchimento
  probabilidade   TINYINT NULL CHECK (probabilidade BETWEEN 1 AND 5),
  severidade      TINYINT NULL CHECK (severidade BETWEEN 1 AND 5),
  resposta        TEXT NULL,
  responsavel     VARCHAR(256) NULL,
  origem_externa  VARCHAR(500) NULL,              -- S10-US03: dependências
  data_necessaria DATE NULL,
  prazo_revisao   DATE NULL,
  status          ENUM('aberto','mitigado','materializado',
                       'encerrado') NOT NULL DEFAULT 'aberto',
  execucao_id     CHAR(36) NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP NULL,
  INDEX idx_riscos_entrega (entrega_id),
  CONSTRAINT fk_risco_entrega FOREIGN KEY (entrega_id) REFERENCES entregas(id),
  CONSTRAINT fk_risco_execucao FOREIGN KEY (execucao_id) REFERENCES execucoes_skill(id)
) ENGINE=InnoDB;

-- ============================================================================
-- TRIGGERS DE IMUTABILIDADE (AT-01 §6.3 — regra de ouro 2)
-- Histórico é INSERT-only: UPDATE/DELETE rejeitados pelo próprio banco.
-- Statements únicos (SIGNAL sem BEGIN/END) — dispensam DELIMITER.
-- ============================================================================

CREATE TRIGGER trg_regras_versoes_no_update
BEFORE UPDATE ON regras_institucionais_versoes FOR EACH ROW
  SIGNAL SQLSTATE '45000'
  SET MESSAGE_TEXT = 'Versoes sao imutaveis - crie nova versao (regra de ouro 2)';

CREATE TRIGGER trg_regras_versoes_no_delete
BEFORE DELETE ON regras_institucionais_versoes FOR EACH ROW
  SIGNAL SQLSTATE '45000'
  SET MESSAGE_TEXT = 'Versoes sao imutaveis - historico nao pode ser apagado';

CREATE TRIGGER trg_entregas_versoes_no_update
BEFORE UPDATE ON entregas_versoes FOR EACH ROW
  SIGNAL SQLSTATE '45000'
  SET MESSAGE_TEXT = 'Versoes sao imutaveis - crie nova versao (regra de ouro 2)';

CREATE TRIGGER trg_entregas_versoes_no_delete
BEFORE DELETE ON entregas_versoes FOR EACH ROW
  SIGNAL SQLSTATE '45000'
  SET MESSAGE_TEXT = 'Versoes sao imutaveis - historico nao pode ser apagado';

CREATE TRIGGER trg_execucoes_no_update
BEFORE UPDATE ON execucoes_skill FOR EACH ROW
  SIGNAL SQLSTATE '45000'
  SET MESSAGE_TEXT = 'Execucoes sao registro de auditoria imutavel (regra de ouro 3)';

CREATE TRIGGER trg_execucoes_no_delete
BEFORE DELETE ON execucoes_skill FOR EACH ROW
  SIGNAL SQLSTATE '45000'
  SET MESSAGE_TEXT = 'Execucoes sao registro de auditoria imutavel (regra de ouro 3)';

-- ============================================================================
-- Registro desta migração
-- ============================================================================

INSERT INTO schema_migracoes (versao, descricao) VALUES
  ('001', 'Esquema inicial do modelo comum (AT-01 §5, aprovado 26.07.2026 / ADR-006): 21 tabelas + 6 triggers de imutabilidade');
