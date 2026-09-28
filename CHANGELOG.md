# Changelog

Mudanças de estrutura e de uso do repositório. As mudanças metodológicas dos
indicadores seguem registradas nas fichas e no protocolo de validação.

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
| Páginas-ponte `docs/01…16-*.md` e `docs/templates/` (16) | pastas temáticas `docs/projeto/`, `docs/ambiente/`, `docs/dados-petrvs/`, `docs/indicadores/`, `docs/relatorios/`, `docs/gestao/README.md` e `docs/modelos/` | L4b | Após dois ciclos mensais completos sem consumidor conhecido (links compartilhados) |

Cada retirada deve ser registrada aqui, com a data e a evidência.
