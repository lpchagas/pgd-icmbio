# Changelog

Mudanças de estrutura e de uso do repositório. As mudanças metodológicas dos
indicadores seguem registradas nas fichas e no protocolo de validação.

## [Não publicado] — reorganização em monorepo (`pgd-icmbio`)

### Estrutura

- O agente de gestão foi incorporado com histórico: `agente/dados/` e `tests/agente/`.
- Os relatórios passaram para o pacote de nível superior `relatorios/`.
- A raiz do projeto tem uma fonte única, `lib/caminhos.py`.
- A configuração Denodo tem um único adaptador (`lib/denodo_config.py`), que aceita temporariamente os nomes antigos do agente como aliases: `DENODO_PASS`, `DENODO_JDBC_JAR` e `DENODO_URL`.

### Pontes temporárias

| Ponte | Destino | Criada | Retirada |
| --- | --- | --- | --- |
| `ocde.relatorios.privacidade` | `relatorios.privacidade` | L4a | Na próxima revisão metodológica do G01 (importada pelo A1 certificado) |
| `ocde.relatorios.textos_execucao` | `relatorios.textos_execucao` | L4a | Na próxima revisão metodológica do G02 (importada pelo A1 certificado) |
| Demais `ocde.relatorios.*` (14 módulos, incluindo as CLIs `relatorio_v2` e `relatorio_cumulativo`) | `relatorios.*` | L4a | Após dois ciclos mensais completos sem consumidor conhecido |
| Aliases `DENODO_PASS`, `DENODO_JDBC_JAR`, `DENODO_URL` | nomes canônicos `DENODO_*` | L3 | Com evidência de que não há consumidor **e** uma execução operacional compatível |

Cada retirada deve ser registrada aqui, com a data e a evidência.
