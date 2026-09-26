# Changelog

Mudanças de estrutura e de uso do repositório. As mudanças metodológicas dos
indicadores seguem registradas nas fichas e no protocolo de validação.

## [Não publicado] — reorganização em monorepo (`pgd-icmbio`)

### Estrutura

- O agente de gestão foi incorporado com histórico: `agente/dados/` e `tests/agente/`.
- Os relatórios passaram para o pacote de nível superior `relatorios/`.
- A raiz do projeto tem uma fonte única, `lib/caminhos.py`.
- A configuração Denodo tem um único adaptador (`lib/denodo_config.py`), que aceita temporariamente os nomes antigos do agente como aliases: `DENODO_PASS`, `DENODO_JDBC_JAR` e `DENODO_URL`.

### Documentação e capacidades

- `docs/` foi reorganizado por público (L4b), com página-ponte em cada caminho numerado antigo.
- Os documentos do agente estão em `docs/agente/`, `docs/decisoes/`, `docs/governanca-projeto/`, `docs/projeto/` e `docs/dados-petrvs/`.
- As fichas S01–S24 e os protótipos estão em `capacidades/`, com o `CATALOGO.md` (L4c).

### Escopo e pilotos (L5)

- A resolução de escopo é única (`relatorios.escopo`) nos cinco pontos oficiais. Regional sem estrutura, unidade inexistente e sigla ambígua passaram a ser erro; as chaves `tipo_unidade-…` e `lista_unidades-<hash>` são as mesmas em todos os pontos (a de lista não depende mais do nome do arquivo).
- `lib.escopos` só normaliza; o `ScopeSpec` duplicado foi retirado.
- Cadastro das três unidades piloto em `config/unidades-piloto.json` e gate de liberação (`lib/liberacao.py`): fora dos pilotos, produto final ou compartilhável exige três aceites da mesma identidade e deliberação de expansão. O relatório cumulativo e o V2 compartilhável no escopo nacional passam a ser recusados até lá.
- Novas CLIs: `tools/executar_pilotos.py` e `tools/registrar_aceite_piloto.py`. Fluxo em `docs/projeto/fluxo-unidades-piloto.md`.

### Pontes temporárias

| Ponte | Destino | Criada | Retirada |
| --- | --- | --- | --- |
| `ocde.relatorios.privacidade` | `relatorios.privacidade` | L4a | Na próxima revisão metodológica do G01 (importada pelo A1 certificado) |
| `ocde.relatorios.textos_execucao` | `relatorios.textos_execucao` | L4a | Na próxima revisão metodológica do G02 (importada pelo A1 certificado) |
| Demais `ocde.relatorios.*` (14 módulos, incluindo as CLIs `relatorio_v2` e `relatorio_cumulativo`) | `relatorios.*` | L4a | Após dois ciclos mensais completos sem consumidor conhecido |
| Aliases `DENODO_PASS`, `DENODO_JDBC_JAR`, `DENODO_URL` | nomes canônicos `DENODO_*` | L3 | Com evidência de que não há consumidor **e** uma execução operacional compatível |
| Páginas-ponte `docs/01…16-*.md` e `docs/templates/` (16) | pastas temáticas `docs/projeto/`, `docs/ambiente/`, `docs/dados-petrvs/`, `docs/indicadores/`, `docs/relatorios/`, `docs/gestao/README.md` e `docs/modelos/` | L4b | Após dois ciclos mensais completos sem consumidor conhecido (links compartilhados) |

Cada retirada deve ser registrada aqui, com a data e a evidência.
