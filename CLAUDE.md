# Instruções do projeto — Claude Code

<!-- nucleo-comum:inicio -->
## Projeto

**PGD-ICMBio** (`pgd-icmbio`; no GitHub, `lpchagas/pgd-icmbio`, antes `pgd-ocde-icmbio`)
calcula, valida e documenta indicadores do Programa de Gestão e Desempenho do ICMBio a
partir do PETRVS, lido via Denodo (MGI/Dataprev), sem ETL nem datamart. Responsável
técnico: CGOV/ICMBio. Contexto: piloto OCDE/MGI/ICMBio/UFRN (Portaria ICMBio nº
5.592/2025).

| Família | Alvos | Código | Janela |
| --- | --- | --- | --- |
| OCDE/PGD | I01–I12 | `ocde/indicadores/IND_OCDE_XX.1_run.py` | cumulativa (regra 7) |
| Gestão — G01 | Situação dos Planos de Trabalho | `gestao/IND_GEST_01/` | fotografia na data de execução |
| Gestão — G02 | Execução das Entregas | `gestao/IND_GEST_02/` | PE: histórico até o fim da janela; PT: fotografia na data de execução |
| MGI | planejado | `mgi/` (sem scripts) | anual |
| Agente de gestão | S01–S24 especificadas | `agente/dados/` (dados); `capacidades/` | — |

Responda e documente sempre em **português do Brasil**.

## Regras invioláveis

**Segurança e dados pessoais**

1. Credenciais do Denodo e chaves de serviço só no `.env` local (nomes em
   `.env.example`). Credenciais do MySQL só em arquivos `.cnf` locais, fora do Git
   (backup e instância isolada). Nunca em código, docs, skills, logs, exemplos ou
   nestas instruções. Nunca exibir valores.
2. Nunca versionar: `.env*` (exceto `.env.example`), `*.cnf`, dumps, CSV e planilhas
   fora de `tests/fixtures/`, PDF/PPT/DOC, notebooks com resultado, `artefatos_local/`,
   `cgov/`, `setup/`, `data/`, `.agents/`, `.claude/`, `.codex/`, `.github/skills/`.
3. Indicadores OCDE nunca expõem nome, CPF, e-mail ou telefone. Exceções deliberadas
   (D14, D18): G01 nominal só nos produtos `operacional`/`restrito`; anexo nominal do
   G02 só no `restrito`, sem CPF, e-mail, telefone ou endereço. Produto
   `compartilhavel`: sem identificação, k≥5 e supressão complementar.
4. Agente: conteúdo `99_restrito` não entra em Git, RAG ou serviço externo; serviço
   externo recebe só dado público ou sintético.

**Governança documental**

5. Deliberações da CGOV (cadernos metodológicos, decisões, homologações, aceites) ficam
   no acervo privado (`artefatos_local/validacao/`), **nunca em `docs/`**. A
   documentação pública cita só o identificador (Dnn) e o efeito técnico, sem link
   para o acervo.
6. Precedência entre **fontes**: decisão CGOV > contratos executáveis
   (`lib/validation_contracts.py`) > scripts > fichas em `docs/` > artefatos A3–A5.
   Entre estes três arquivos de instruções **não há hierarquia**: o núcleo é idêntico
   nos três (ver "Estas instruções").

**Tempo**

7. OCDE: `lib.periodos.analysis_window()` — de 01/07/2025 ao último dia do mês
   anterior à execução, fuso `America/Sao_Paulo`. PE: `build_periods_pe()`; PT:
   `build_periods_pt()`. Sempre passar `--data-execucao`; **nunca `date.today()`**.
8. Calendário do PE em 2026: Q1 01/01–30/04, Q2 01/05–31/08, Q3 01/09–31/12. PT em
   2026: mensal. T1–T2/2025 excluídos por baixa qualidade.

**Dados e cálculo**

9. Soft-delete: `deleted_at IS NULL` em toda tabela do FROM/JOIN, inclusive
   `planos_trabalhos_consolidacoes`. Única exceção declarada: autor da transição de
   status no G01.
10. Avaliação: `6 - tan.sequencia` só em I09 e I12; I10 usa `sequencia = 4` e I11
    `sequencia = 1`. Nunca `tan.nota` nem `JSON_UNQUOTE`.
11. Arredondamento meio para cima (`lib/arredondamento.py`) nas saídas em Python (D24).
12. Mudança de fórmula ou schema incrementa `formula_version` no contrato; a correção
    entra na produção **e** no oracle, cada um com o seu código (nunca compartilhado).
13. Hash de baseline nunca é editado à mão: só `tools.approve_validation_baseline`.
14. Resultado do PE nunca é substituído por atividade do PT; o relatório preserva a
    unidade dona e a executora.
15. CSV: delimitador `|`, `utf-8-sig`, `clean()` com
    `re.sub(r"[\r\n]+", " / ", str(val))`, colunas em snake_case (`_perc`, `_total`,
    `_media`).

**Agente**

16. Denodo é somente leitura. Cálculo determinístico fica em Python. Dado ausente vira
    pergunta, e decisão humana fica separada da saída automática.
17. Escrita versionável só por `agente/dados/versoes.py`: UUID persistente + código
    legível; alteração cria versão, nunca sobrescreve. Funções de dados recebem `conn`
    e quem chama controla a transação.
18. O núcleo analítico não importa `agente`, `pymysql` nem `anthropic` (ADR-009).

## Pilotos e liberação

Cadastro: `config/unidades-piloto.json`. Fluxo: `docs/projeto/fluxo-unidades-piloto.md`.

| Piloto | Seletor exato | Subordinadas |
| --- | --- | --- |
| CGOV | `--unidade CGOV` | não |
| COCAGE | `--unidade COCAGE` | não |
| GR2 | `--regional GR2` | sim, pela hierarquia do PETRVS (D19) |

- O recorte precisa ser exatamente o cadastrado (`--regional CGOV` não é o piloto
  CGOV). Trava de divergência e conciliações: `config/conciliacoes-unidades.json`.
- Aquisição no Denodo por família:
  - **OCDE:** os A1 consultam o universo nacional e o filtro por escopo é aplicado
    depois, sobre o CSV. Com `--pilotos`, cada A1 roda uma vez, o staging é descartado e
    só o A2 de cada piloto é gravado. Nunca chamar esse filtro de "consulta restrita".
  - **Gestão (G01, G02):** os A1 recebem as siglas do escopo resolvido (`--unidade`,
    repetido pelo `gestao.runner`) e filtram na própria consulta.
- **Sem seletor, a extração OCDE assume o escopo nacional e grava A2 nacional.** Sempre
  informar `--pilotos` ou o seletor exato de um piloto.
- Resultados saem **separados por piloto**; nunca somar taxas entre pilotos.
- Fora dos pilotos, produto final ou compartilhável exige três aceites da mesma
  identidade e deliberação de expansão (`lib/liberacao.py`). A expansão está suspensa
  (D16). Os A1 são primitivas internas, não canal de liberação.
- A certificação automática A1–A5 é evidência técnica: **não substitui o aceite humano
  dos pilotos** nem a deliberação de expansão.

## Denodo e VQL

- Views com prefixo obrigatório `petrvs_icmbio_`. Configuração única em
  `lib/denodo_config.py` (ADR-012); a suíte de testes nunca abre o Denodo
  (`PGD_BLOQUEAR_DENODO=1`). Pré-requisito: IP liberado pelo Dataprev.
- `CAST('AAAA-MM-DD' AS DATE)`, nunca `DATE()`. Sem `SET SESSION`, CTE recursiva,
  `DIFF`, `DATEDIFF` ou `TIMESTAMPDIFF`: usar subtração de datas ou Python.
- Dias úteis (`lib/calendario.py`) e hierarquias: em Python.
- `* 100.0` antes de dividir; `NULLIF` contra divisão por zero. Window functions:
  testar no DBeaver antes do JDBC.
- Modelo de dados, status do PT em duas camadas e campos:
  `docs/dados-petrvs/estrutura-banco-dados.md`.

## Estrutura

```text
lib/            núcleo: denodo_config, periodos, calendario, escopos, liberacao,
                indicator_extraction, ciclo_gerencial, validation_*
ocde/ gestao/ mgi/   A1 por família (IND_OCDE_XX, IND_GEST_XX, IND_MGI_XX)
relatorios/     V2, cumulativo, escopo, privacidade (ocde/relatorios/ = pontes)
agente/dados/   banco local do agente (MySQL), versões, sincronização, backup
capacidades/    CATALOGO.md, especificações S01–S24, protótipos
config/         unidades-piloto, conciliações, baseline de exemplo, lock das instruções
tools/          auditoria, pilotos, aceites, baseline, replay, links, sincronia, skills
tests/          unit, regression, replay, agente, integração opt-in
docs/           público, por assunto: projeto, ambiente, dados-petrvs, indicadores,
                ocde, gestao, relatorios, agente, decisoes, governanca-projeto
```

Privados, fora do Git: `artefatos_local/`, `cgov/`, `setup/`, `.agents/`, `.claude/`,
`.codex/`. São links locais para a pasta privada sincronizada, de acesso restrito à
equipe (symlinks no Linux/WSL, junções no Windows). Os links são de cada computador e
não se sincronizam: recriá-los em cada ambiente. No WSL, a pasta sincronizada precisa
estar disponível neste dispositivo (arquivo só na nuvem dá erro de leitura). Detalhes:
`docs/ambiente/organizacao-publico-privado.md`.

## Validação A1–A5 e comandos

Protocolo: `docs/indicadores/protocolo-validacao.md`. A1 = script de produção; A2 = CSV
no acervo, por escopo; A3 = oracle Python independente; A4 = diagnóstico; A5 =
relatório. Estados: `HOMOLOGACAO_INICIAL_PENDENTE` → `HOMOLOGADO` →
`CERTIFICADO_AUTOMATICAMENTE` (também `FALHA_TECNICA`, `AGUARDANDO_DECISAO`,
`REPROVADO`). Modo fixture sempre sai `pendente` e nunca homologa. Mudar a
`formula_version` devolve o alvo a pendente.

**Comando padrão dos pilotos** (resolve o cadastro, aquisição única, sem total
agregado; `--modo dry-run` é o padrão):

```text
python -m tools.executar_pilotos --capacidade ocde --data-execucao AAAA-MM-DD --modo real --validar
python -m tools.executar_pilotos --capacidade G01 --data-execucao AAAA-MM-DD --produto restrito --modo real --validar
python -m tools.executar_pilotos --capacidade G02 --data-execucao AAAA-MM-DD --produto compartilhavel --modo real --validar
```

**Comandos diretos** (um piloto por vez, com o seletor exato da tabela acima; os
exemplos usam GR2, e para CGOV ou COCAGE troque por `--unidade CGOV` ou
`--unidade COCAGE`):

```text
python -m lib.indicator_extraction --data-execucao AAAA-MM-DD --pilotos --salvar-manifesto
python -m lib.indicator_extraction --data-execucao AAAA-MM-DD --regional GR2 --salvar-manifesto
python -m gestao.runner --analise todas --data-execucao AAAA-MM-DD --regional GR2 --produto restrito
python -m lib.validation_runner --familia todas --alvo todos --modo integrado --data-execucao AAAA-MM-DD --regional GR2
python -m relatorios.relatorio_v2 --data-execucao AAAA-MM-DD --regional GR2 --produto ambos --lente ambas --salvar
python -m lib.ciclo_gerencial --data-execucao AAAA-MM-DD --regional GR2 --produto ambos --lente ambas --salvar --pdf
```

**Atos humanos** (só com a decisão registrada no acervo; os nomes de arquivo são
ilustrativos):

```text
python -m tools.approve_validation_baseline --manifesto manifesto_validacao.json --alvo I02 --papel-aprovador coordenacao-cgov --decisao HOMOLOGADO --justificativa "texto da decisão"
python -m tools.registrar_aceite_piloto verificar --capacidade I02
```

Novo indicador de gestão: roteiro em `gestao/README.md`.

## Ambiente e testes

- Ambiente principal: Linux/WSL, repositório no filesystem Linux,
  `.venv/bin/python` (Python 3.14). No Windows: `.venv\Scripts\python.exe`. CI: Python
  3.12 (`.github/workflows/quality.yml`). Dependências: `requirements-report.txt`,
  `requirements-agente.txt`, `requirements-dev.txt`.
- Denodo via JPype: a JVM é do mesmo sistema do Python. No WSL, JDK Linux e
  `DENODO_JVM_DLL` apontando para `libjvm.so`; no Windows, `JAVA_HOME` (deriva a
  `jvm.dll`). Driver: `.jar` JDBC da Denodo em `DENODO_DRIVER_PATH`, fora do repositório
  (`docs/ambiente/acesso-denodo-dbeaver.md`). Nomes das variáveis: `.env.example`.
- Suíte completa (offline; não abre Denodo nem MySQL):
  `.venv/bin/python -m pytest tests -q -p no:cacheprovider`. Testes MySQL só
  com `-m mysql` e `PGD_MYSQL_TESTE=1`, na instância isolada
  (`docs/ambiente/banco-local-agente.md`; scripts `.sh` no Linux e `.ps1` no Windows).
- Resultado de testes e estado do projeto não ficam nestas instruções: ver
  `CHANGELOG.md` e `capacidades/CATALOGO.md`.

## Git e publicação

- Fora da reorganização: trabalho direto no `main`. Durante a reorganização: branch
  `reorg/*` e uma PR única na publicação.
- Commit só com autorização explícita e **depois da suíte completa verde**; o comando
  condiciona o commit ao resultado. Nunca push, rebase ou reescrita de histórico sem
  autorização. Não reverter mudanças do usuário.
- Antes de commit: `detect-secrets` nos arquivos alterados.
- Antes de push, auditoria completa com o `.env` local e o perfil do monorepo:

  ```text
  python -m tools.security_audit --alvos todos --perfil monorepo --env .env --out artefatos_local/auditoria/pre-push.json
  ```

  Só se publica com status **`completo_sem_ocorrencia`** (saída 0).
  `completo_com_ocorrencia` (1) e `incompleto` (2) bloqueiam; sem `--env`, o modo
  exato fica `incompleto`. Depois, revisar `docs/ambiente/seguranca-publicacao.md` e,
  como checagem rápida, `rg -n "PASS|CPF|[0-9]{11}" docs gestao ocde lib README.md`.
- Mudança estrutural prova equivalência por replay (`tools/replay_producao.py`); se não
  provar, vira mudança funcional com revalidação.

## Skills

- Fonte canônica privada: `.agents/skills`, com manifesto `.agents/skills-manifest.json`;
  validar com `python -m tools.skills_manager validate`.
- Skills não incorporam SQL, fórmulas, drivers ou credenciais; roteiam para `lib/`,
  `ocde/`, `gestao/` e `relatorios/`. Principal: `ciclo-gerencial-mensal`.
- Homologação de skill exige descoberta única e equivalência funcional nas três
  ferramentas. Como cada ferramenta descobre as skills: bloco da ferramenta, abaixo.

## Estas instruções

- `CLAUDE.md`, `AGENTS.md` e `PROJECT.md` são pares sem hierarquia (DP-03, ADR-010).
  Este núcleo é idêntico nos três; o bloco após o marcador final é da ferramenta.
- Edite o núcleo em qualquer um dos três e rode
  `python -m tools.sincronizar_instrucoes sincronizar`. O hook e o CI rodam `verificar`.
- Sem segredos, sem dados pessoais e sem números voláteis (contagens, datas de execução,
  resultados de teste). Mudança do núcleo passa por revisão de conteúdo.
<!-- nucleo-comum:fim -->

## Mecânica da ferramenta

- O Claude Code carrega este arquivo em toda sessão. A memória automática do usuário é
  contexto, não regra: em conflito, vale o núcleo acima.
- Abrir a sessão com a pasta de trabalho na raiz do repositório.

## Skills desta ferramenta

- Descoberta em `.claude/skills/<nome>`: um link por skill para `.agents/skills/<nome>`
  (junção no Windows; symlink em Linux e contêiner), criado por
  `python -m tools.skills_manager install --apply`.
- Os links são locais e não se sincronizam: em outro computador ou contêiner, rodar o
  instalador de novo.
- Invocação: `/nome-da-skill`.
