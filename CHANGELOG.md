# Changelog

Mudanças de estrutura e de uso do repositório. As mudanças metodológicas dos
indicadores seguem registradas nas fichas e no protocolo de validação.

## 17.10.2026 — LLM em execução do agente (DP-08, ADR-014)

- **ADR-014:** o servidor MCP local passa a ser a interface-base das ferramentas do
  agente. Um gate de classe de dado no servidor só deixa chegar ao cliente externo dado
  público, sintético ou agregado compartilhável (k≥5). O institucional comum vai para um
  modelo local (Ollama), e o FastAPI vira adaptador opcional.
- **Revisões:** a ADR-004 (API comercial direta → Azure OpenAI) fica marcada como
  revisada, com o corpo mantido como registro histórico. O item 7 da ADR-008 e o AT-02
  passam a apontar o MCP como base.
- **Q9:** `docs/agente/instrucoes-assistente-externo-v1.md` segue vigente como base de um
  Gem só com conteúdo público. `docs/governanca-projeto/validacao-modelo-comum.md` segue
  vigente até o G1.

## 17.10.2026 — aceites dos pilotos e 2ª etapa nacional (D44, D45)

- **Pilotos:** I05 3.0.2, I07 3.2.0 e I08 3.2.0 homologados nos três escopos. Depois de
  uma rodada completa sobre o código atual, foram registrados os aceites dos 14 alvos
  nos três pilotos.
- **Nacional (D36, 2ª etapa):** a baseline nacional de I03–I09 foi homologada e a
  deliberação de expansão foi registrada. Com a 1ª etapa, os 12 indicadores OCDE ficam
  elegíveis para o produto nacional, com nota ao painel sobre as duplicidades atômicas
  (I01, I05–I08) e sobre os vínculos com força de trabalho fora de 0–100 (fora do
  cálculo de I07 e I08). O I05 vai ao painel só na visão estatística (v2).
- **G01 nacional (D44, D45):** expansão deliberada. No compartilhável, a supressão k≥5
  esconderia a maior parte das unidades, por isso o G01 vai à COCAGE no produto
  restrito (sem supressão; nominal, sem CPF, e-mail, telefone ou endereço), com acesso
  restrito no painel. A regra k≥5 do produto compartilhável não muda.

## 17.10.2026 — I05 3.0.2, I07 3.2.0 e I08 3.2.0 (D43)

- **I05 3.0.2:** o VQL devolve só a contagem de entregas por servidor. O A1 calcula a
  média da unidade da visão nominal com aritmética exata e arredonda meio para cima
  (D24), como no I09 3.0.3. A posição relativa compara com a média arredondada, e as
  colunas do CSV não mudam.
- **I07 3.2.0 e I08 3.2.0:** o vínculo com força de trabalho fora de 0–100 fica fora do
  cálculo e é contado num alerta de qualidade, na produção e no oracle. No I07 ele
  também não conta em `num_planos_trabalho_alocados`.
- **Oracle do I07 e do I08:** o plano sem carga horária não conta como plano alocado,
  como já acontecia na produção. Era a causa das divergências de ±1 no nacional.
- **Validação:** em I05–I08, a força de trabalho fora de 0–100 passa a ser alerta, não
  bloqueio.
- **Regra 9:** as junções de unidade (I05, I07, I08) e de usuário (I05) passam a filtrar
  `deleted_at`. A fixture de replay do I05 foi regerada.
- **Identidade:** a mudança no contrato revoga os aceites dos pilotos, que serão
  registrados de novo depois da revalidação.

## 17.10.2026 — aceites dos pilotos e 1ª etapa nacional (D42)

- **Pilotos:** I04 2.1.0 e I09 3.0.3 homologados nos três escopos. Depois de uma
  rodada completa sobre o código atual, foram registrados os aceites dos 14 alvos nos
  três pilotos.
- **Nacional (D36, 1ª etapa):** a baseline nacional de I01, I02, I10, I11 e I12 foi
  homologada e a deliberação de expansão foi registrada. Os cinco ficam elegíveis para
  o produto nacional; o I01 sai com nota sobre as duplicidades atômicas. I03, I04 e I09
  validaram sem divergência no nacional e ficam para a etapa seguinte; I05–I08
  aguardam decisão metodológica.

## 17.10.2026 — I04 2.1.0 e I09 3.0.3 (D41)

- **I04 2.1.0:** sai o valor absoluto do realizado. A entrega com realizado negativo
  continua em `total_no_ciclo`, mas fica fora da média do score, e a unidade sem
  entrega válida no período é omitida. A correção entrou na produção e no oracle.
- **I09 3.0.3:** o VQL devolve só contagens inteiras (por unidade e, numa segunda
  consulta, por plano). O A1 calcula as duas médias com aritmética exata e arredonda
  meio para cima (D24); a faixa de desempenho usa a média arredondada. A 3.0.2, que só
  tirava o `ROUND` do VQL, ainda divergia em 0,01 por causa do ponto flutuante do
  Denodo. O gerador de fixtures do replay passa a emitir a consulta por plano.
- **Identidade:** como na D39, a mudança no contrato revoga os aceites dos pilotos, que
  são registrados de novo depois da revalidação.

## 17.10.2026 — I03 3.1.0 e aceites dos pilotos (D39, D40)

- **I03 3.1.0 (D39):** entrega com realizado negativo no PETRVS não tem taxa.
  `taxa_atingimento_perc` e `taxa_meta_integral_perc` ficam vazias, o status é
  `Dado inconsistente` e o realizado bruto continua em `meta_executada`. A correção
  entrou na produção e no oracle, cada um com o seu código, e o relatório deixa as
  entregas sem taxa fora das proporções.
- **Identidade:** como `lib/validation_contracts.py` é dependência de todas as
  capacidades, a mudança da versão do I03 revogou os aceites anteriores.
- **Pilotos (D40):** a rodada completa (OCDE, G01, G02) foi revalidada, o I03 foi
  homologado nos três escopos e foram registrados os aceites dos 14 alvos nos três
  pilotos. A expansão nacional segue a D36.

## 17.10.2026 — retirada do Codex (DP-07, ADR-013)

O projeto passa a usar duas ferramentas de desenvolvimento: Claude Code (principal) e
Antigravity (secundária). A [ADR-013](docs/decisoes/ADR-013-retirada-codex.md) revisa a
ADR-010.

- **Instruções:** `CLAUDE.md` e `PROJECT.md` são os dois pares sem hierarquia, e o
  `AGENTS.md` sai da raiz. O `config/instrucoes.lock.json` foi regravado pelo
  sincronizador, com dois arquivos e o novo hash do núcleo. O hook de pre-commit
  verifica os dois.
- **Sincronizador:** a numeração dos estados (1–8) foi mantida, e o estado 6 não ocorre
  com dois arquivos.
- **Defesa:**
  - o `.gitignore` ignora o `AGENTS.md` também na raiz;
  - o auditor de segurança o recusa ali com o novo motivo `instrucao_retirada`, que não é
    motivo de privacidade;
  - `.codex` continua como caminho proibido.
- **Skills:** o `tools/skills_manager.py` e o `tools/bootstrap_skills.py` deixam de
  conhecer o cliente `codex`, e a homologação passa a valer nas duas ferramentas.
- **Documentação:** foram atualizados o README, o guia de sincronia, a organização
  público-privado (5 links privados), a segurança de publicação, o AT-02 (v1.1) e os
  caps. 02, 06 e 07 da proposta v6.

## 17.10.2026 — retirada das páginas-ponte (DP-06)

As páginas-ponte da L4b foram retiradas antes dos dois ciclos mensais previstos:
nenhum link para os caminhos antigos foi compartilhado fora da equipe
([DP-06](docs/decisoes/registro-decisoes-projeto.md)). O placeholder docs/mgi/README.md
também saiu; a pasta será recriada com a primeira ficha MGI. Quem chegar por um caminho
antigo encontra o conteúdo em:

| Caminho antigo | Caminho atual |
| --- | --- |
| docs/01-visao-geral.md | [`docs/projeto/visao-geral.md`](docs/projeto/visao-geral.md) |
| docs/03-acesso-direto-denodo-dbeaver.md | [`docs/ambiente/acesso-denodo-dbeaver.md`](docs/ambiente/acesso-denodo-dbeaver.md) |
| docs/04-configuracao-dbeaver.md | [`docs/ambiente/configuracao-dbeaver.md`](docs/ambiente/configuracao-dbeaver.md) |
| docs/05-contexto-ocde-pgd.md | [`docs/projeto/contexto-ocde-pgd.md`](docs/projeto/contexto-ocde-pgd.md) |
| docs/07.1-estrutura-banco-dados.md | [`docs/dados-petrvs/estrutura-banco-dados.md`](docs/dados-petrvs/estrutura-banco-dados.md) |
| docs/07.2-status_artefatos_pgd_icmbio.md | [`docs/dados-petrvs/status-artefatos.md`](docs/dados-petrvs/status-artefatos.md) |
| docs/08-guia-rapido-gestores.md | [`docs/indicadores/guia-rapido-gestores.md`](docs/indicadores/guia-rapido-gestores.md) |
| docs/09-protocolo-validacao-indicadores.md | [`docs/indicadores/protocolo-validacao.md`](docs/indicadores/protocolo-validacao.md) |
| docs/10-jupyter-guia-iniciantes.md | [`docs/ambiente/jupyter.md`](docs/ambiente/jupyter.md) |
| docs/11-guia-extracao-mensal.md | [`docs/indicadores/extracao-mensal.md`](docs/indicadores/extracao-mensal.md) |
| docs/12-seguranca-publicacao.md | [`docs/ambiente/seguranca-publicacao.md`](docs/ambiente/seguranca-publicacao.md) |
| docs/13-organizacao-publico-privado.md | [`docs/ambiente/organizacao-publico-privado.md`](docs/ambiente/organizacao-publico-privado.md) |
| docs/14-status-planos-trabalho-gestores.md | [`docs/gestao/README.md`](docs/gestao/README.md) |
| docs/15-relatorio-gerencial-cumulativo-anonimizado.md | [`docs/relatorios/relatorio-cumulativo.md`](docs/relatorios/relatorio-cumulativo.md) |
| docs/16-skills-e-relatorio-gerencial-v2.md | [`docs/relatorios/relatorio-v2-ciclo-gerencial.md`](docs/relatorios/relatorio-v2-ciclo-gerencial.md) |
| docs/ocde/06-indicadores-ocde-mysql.md | [`docs/ocde/06-indicadores-ocde-denodo.md`](docs/ocde/06-indicadores-ocde-denodo.md) |
| docs/templates/A3_checklist_validacao_cgov.md | [`docs/modelos/A3_checklist_validacao_cgov.md`](docs/modelos/A3_checklist_validacao_cgov.md) |

## 27.09.2026 — reorganização em monorepo (`pgd-icmbio`)

### Publicação (L8)

- Integrada ao `main` por PR única com merge commit (`lpchagas/pgd-icmbio#4`).
- Repositório renomeado de `pgd-ocde-icmbio` para `pgd-icmbio` no GitHub; o endereço antigo
  redireciona.

### Estrutura

- O agente de gestão foi incorporado com histórico: `agente/dados/` e `tests/agente/`.
- Os relatórios passaram para o pacote de nível superior `relatorios/`.
- A raiz do projeto tem uma fonte única, `lib/caminhos.py`.
- A configuração Denodo tem um único adaptador (`lib/denodo_config.py`), que aceita temporariamente os nomes antigos do agente como aliases: `DENODO_PASS`, `DENODO_JDBC_JAR` e `DENODO_URL`.

### Documentação e capacidades

- `docs/` foi reorganizado por público (L4b), com página-ponte em cada caminho numerado antigo.
- Os documentos do agente estão em `docs/agente/`, `docs/decisoes/`, `docs/governanca-projeto/`, `docs/projeto/` e `docs/dados-petrvs/`.
- As fichas S01–S24 e os protótipos estão em `capacidades/`, com o `CATALOGO.md` (L4c).

### Exclusões com cobertura (L4f)

- Retirados da árvore os nove documentos intermediários vindos do repositório do agente:
  os documentos de trabalho `01_` a `05_` das skills, o portal antigo, o resumo do projeto
  analítico, a página de histórico de evolução e o prompt de planejamento inicial. Todos
  continuam recuperáveis no histórico do Git.
- `docs/governanca-projeto/cobertura-requisitos.md`:
  - destino de cada regra RN-01 a RN-36 (catálogo S01–S24, §11), com a capacidade e a
    fonte normativa (D1–D9);
  - trechos sem destino na v6, apontados como histórico classificado, com a revisão do
    Git para consulta;
  - destino dos documentos de apoio.
- O verificador de links fica sem nenhuma exceção (`config/verificar-links-excecoes.json`
  vazio).

### Revisão da documentação e gates (L4e)

- **Auditoria de segurança** (regras `2026.09.27-l4e`):
  - lista versionada de ocorrências já revisadas (`config/auditoria-ocorrencias-conhecidas.json`,
    com justificativa em cada item);
  - o status passa a contar só as ocorrências novas, e o histórico mantido deixa de
    impedir `completo_sem_ocorrencia`;
  - valor exato, CPF válido e dump nunca entram na lista;
  - um caminho proibido revisado no histórico não esconde o mesmo caminho de volta ao
    índice.
- **Verificador de links:**
  - fonte e destino são classificados antes de qualquer leitura, e o que passa por
    link ou área privada não é aberto (RL2-03);
  - passa a ser **bloqueante** no CI, com exceções só por arquivo e com justificativa
    (`config/verificar-links-excecoes.json`).
- **Código:**
  - o rodapé dos relatórios cita `docs/ocde/06-indicadores-ocde-denodo.md`;
  - o `--reextrair` do relatório cumulativo roda os A1 do contrato, e não mais um
    driver privado inexistente.
- **Documentação:**
  - README reescrito para o monorepo;
  - marcos do projeto em `docs/projeto/visao-geral.md`;
  - mesogrupo e avisos pós-CSV em `estrutura-banco-dados.md`;
  - cópia do driver `.jar` no guia do DBeaver;
  - comandos pelas pontes `ocde.relatorios.*` trocados por `relatorios.*`;
  - caminho local antigo atualizado;
  - atas passam a ser citadas no acervo privado;
  - ADR-007 e 008 como aprovadas na proposta v6 (H5);
  - removida a página pública de apresentação da CGOV (README da pasta docs/cgov), que
    repetia o guia de organização público-privado;
  - menções a assinaturas individuais de ferramentas de IA neutralizadas.

### Instruções dos assistentes (L4d)

- `CLAUDE.md`, `AGENTS.md` e `PROJECT.md` da raiz passam a ser versionados. Os três
  têm um **núcleo comum idêntico**, sem segredos, dados pessoais ou estado volátil,
  seguido de um bloco curto de cada ferramenta (ADR-010). Instruções aninhadas
  continuam proibidas.
- **Sincronizador `tools/sincronizar_instrucoes.py`:**
  - modos `verificar` (inclusive `--staged`), `sincronizar`, `recuperar` e `importar`;
  - lock do núcleo em `config/instrucoes.lock.json`;
  - diário de operação, compare-and-swap, lock de exclusão e recusa de links e
    hardlinks.
  - Guia: `docs/governanca-projeto/sincronia-instrucoes.md`.
- **Auditor de segurança** (regras `2026.09.27-l4d`):
  - as três instruções da raiz são versionáveis;
  - instrução aninhada, ou como pasta, sai como `instrucao_aninhada`;
  - link para instrução, ou instrução que seja link, é recusado.
  - O `.gitignore` acompanha: `**/<nome>` com exceção `!/<nome>`.
- **Skills no Windows:**
  - `tools/skills_manager.py install` cria um link por skill escolhido pela plataforma
    (junção no Windows, symlink no Linux e no WSL) e identifica link pela etiqueta de
    reparse, porque pastas do OneDrive também têm atributo de reparse;
  - links antigos são trocados sem tocar o destino.
- **`tools/bootstrap_skills.py`:**
  - pontos de entrada em `relatorios.*`, sem as pontes;
  - catálogo alinhado ao manifesto vigente;
  - não regrava arquivo igual nem sobrescreve `SKILL.md` ou manifesto que evoluíram
    (só com `--forcar`).
- **Documentos novos:**
  - ADR-009 (arquitetura integrada), ADR-010 (sincronia das instruções), ADR-011
    (unidades piloto) e ADR-012 (configuração Denodo);
  - `docs/decisoes/registro-decisoes-projeto.md`;
  - `docs/indicadores/licoes-tecnicas.md`.
  - Os guias `organizacao-publico-privado.md` e `seguranca-publicacao.md` foram
    corrigidos: as instruções são públicas, as junções são só de pastas, e a auditoria
    completa com `--env` e resultado `completo_sem_ocorrencia` é o gate de publicação.

### Escopo e pilotos (L5)

- A resolução de escopo é única (`relatorios.escopo`) nos cinco pontos oficiais. Regional sem estrutura, unidade inexistente e sigla ambígua passaram a ser erro; as chaves `tipo_unidade-…` e `lista_unidades-<hash>` são as mesmas em todos os pontos (a de lista não depende mais do nome do arquivo).
- `lib.escopos` só normaliza; o `ScopeSpec` duplicado foi retirado.
- Cadastro das três unidades piloto em `config/unidades-piloto.json` e gate de liberação (`lib/liberacao.py`): fora dos pilotos, produto final ou compartilhável exige três aceites da mesma identidade e deliberação de expansão. O relatório cumulativo e o V2 compartilhável no escopo nacional passam a ser recusados até lá.
- Novas CLIs: `tools/executar_pilotos.py` e `tools/registrar_aceite_piloto.py`. Fluxo em `docs/projeto/fluxo-unidades-piloto.md`.

### Versão coordenada D35 (decisões CGOV D19–D35, 27/09/2026)

- **Recorte (D19/D20):** trava de divergência no recorte regional (unidade mapeada no dicionário CGOV em regionais diferentes no PETRVS e na estrutura oficial é recusada até constar de `config/conciliacoes-unidades.json`); `ScopeSpec` registra as conciliações aplicadas e as unidades sem mapeamento.
- **Fórmulas:** I03 3.0.0 (entrega só com plano sobreposto ao período, D22); I07 e I08 3.1.0 (vínculo plano de trabalho × entrega conta uma vez, D25; calendário com pontos facultativos federais das portarias do MGI e com o feriado de 20/11, que faltava, D29); I11 3.1.0 (rótulo "Uso baixo da nota máxima" e faixas só com volume suficiente, D31); I01 2.0.1 e I05 3.0.1 (arredondamento meio para cima em empates, D24). Quebra de série nos indicadores com mudança de versão maior ou menor.
- **Soft-delete das consolidações (correção, revalidação dos pilotos):** I09 3.0.1, I10 3.0.1, I11 3.1.1 e I12 2.0.1 passam a filtrar `planos_trabalhos_consolidacoes.deleted_at`, como exige a regra do projeto; avaliações de consolidações excluídas eram contadas.
- **Falha dos A1 (D33):** falha na consulta de qualquer período encerra o A1 com erro, sem gravar A2 parcial (fecha o DP-L2-01).
- **Validação:** oracle com arredondamento meio para cima (D24) e sem linha para unidade sem entrega no ciclo (D23); datas invertidas no G01 viram alerta (D26); validação independente do G02 compartilhável por propriedades da supressão (D27).
- **Errata:** o commit `714de22` e o CHANGELOG do L7 chamaram a escolha da hierarquia de "provisória até a Q1". A Q1 do caderno trata da fonte da taxonomia OCDE; a hierarquia é a decisão D19.

### Pilotos e hierarquia do PETRVS (L7)

- Os seletores `--regional`, `--unidade` e `--lista-unidades` passam a seguir a hierarquia do PETRVS (`unidade_pai_id`), lida do retrato privado gerado por `tools/atualizar_unidades_petrvs.py` (`lib/unidades_petrvs.py`). Decisão de 26/09/2026, ratificada como D19 (ver errata acima). **Efeito:** o recorte GR2 passa de 3 unidades (só a regional; as subordinadas não têm sigla na estrutura oficial) para 124 siglas do PETRVS. Sigla repetida só é erro quando as homônimas ficam dos dois lados do recorte.
- Aquisição única dos pilotos (H8-a): `lib.indicator_extraction --pilotos` roda cada A1 uma vez sobre o universo nacional (staging descartado) e entrega o A2 filtrado para cada piloto; `tools/executar_pilotos.py --capacidade ocde` usa esse modo, e `--validar` roda a validação integrada por piloto.
- Trava da suíte: com `PGD_BLOQUEAR_DENODO=1` (definida pelo `conftest`) `lib.denodo_config.connect` recusa qualquer conexão, também nos A1 em subprocesso.
- `config/unidades-piloto.json` versão 2: `id_petrvs` de CGOV, COCAGE e GR2 conferidos na fonte; execução real e aceite conferem o cadastro contra a hierarquia atual.

### Ambiente local e banco do agente (L6)

- Caminho local de trabalho congelado em `C:\Projetos\pgd-icmbio` (clone novo; o caminho antigo fica como rollback até o L8), com `.venv` nativo do Windows.
- `agente/dados/backup.ps1`: destino em `PGD_BACKUP_DIR` (absoluto, fora da raiz do disco e de pasta versionada), padrão `data\backups`; retenção só no destino validado e no padrão de nome do dump.
- Instância MySQL isolada (`agente/dados/mysql_isolada.ps1`, porta 3307) e `agente/dados/banco_teste.py` (restauração conferida e banco `pgd_agente_teste` com recusa de SQL que cite `pgd_agente`). Guia em `docs/ambiente/banco-local-agente.md`.

### Pontes temporárias

| Ponte | Destino | Criada | Retirada |
| --- | --- | --- | --- |
| `ocde.relatorios.privacidade` | `relatorios.privacidade` | L4a | Na próxima revisão metodológica do G01 (importada pelo A1 certificado) |
| `ocde.relatorios.textos_execucao` | `relatorios.textos_execucao` | L4a | Na próxima revisão metodológica do G02 (importada pelo A1 certificado) |
| Demais `ocde.relatorios.*` (14 módulos, incluindo as CLIs `relatorio_v2` e `relatorio_cumulativo`) | `relatorios.*` | L4a | Após dois ciclos mensais completos sem consumidor conhecido |
| Aliases `DENODO_PASS`, `DENODO_JDBC_JAR`, `DENODO_URL` | nomes canônicos `DENODO_*` | L3 | Com evidência de que não há consumidor **e** uma execução operacional compatível |
| Páginas-ponte docs/01…16-*.md e docs/templates/ (16) | pastas temáticas `docs/projeto/`, `docs/ambiente/`, `docs/dados-petrvs/`, `docs/indicadores/`, `docs/relatorios/`, `docs/gestao/README.md` e `docs/modelos/` | L4b | **Retiradas em 17.10.2026** (DP-06), com docs/ocde/06-indicadores-ocde-mysql.md |

Cada retirada deve ser registrada aqui, com a data e a evidência.
