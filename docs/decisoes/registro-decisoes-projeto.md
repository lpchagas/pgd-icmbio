# Registro de decisões do projeto (reorganização `pgd-icmbio`)

Decisões de estrutura e de processo tomadas pelo responsável técnico durante a
reorganização em monorepo. Cada linha tem data e efeito, para que a decisão não dependa
de memória de conversa.

**Fora deste registro:**

- As **deliberações metodológicas da CGOV** (Dnn) ficam no acervo privado; a
  documentação pública cita só o identificador e o efeito técnico.
- As decisões sobre **histórico do Git e publicabilidade** ficam no registro privado do
  plano de reorganização.

## Decisões de estrutura (DP)

| ID | Decisão | Data | Efeito |
| --- | --- | --- | --- |
| DP-01 | Monorepo, com o histórico do agente preservado por merge | 23.09.2026 | Agente em `agente/`; [ADR-009](ADR-009-arquitetura-integrada.md) |
| DP-02 | Nome final `pgd-icmbio` | 23.09.2026 | Repositório renomeado no GitHub na etapa final (L8), em 27.09.2026; o endereço antigo `pgd-ocde-icmbio` redireciona |
| DP-03 | `CLAUDE.md`, `AGENTS.md` e `PROJECT.md` como pares sem hierarquia, com regra de sincronia | 23.09.2026 | [ADR-010](ADR-010-sincronia-instrucoes.md) |
| DP-04 | Unidades piloto: CGOV, COCAGE e GR2 | 23.09.2026 | [ADR-011](ADR-011-unidades-piloto.md); `config/unidades-piloto.json` |
| DP-05 | Atualizar todos os `.md`, corrigir links e excluir obsoletos | 23.09.2026 | Revisão integral e verificador de links bloqueante |

## Decisões humanas do plano (H)

| ID | Decisão | Data | Efeito |
| --- | --- | --- | --- |
| H1 | Núcleo comum das instruções aprovado para publicação | 27.09.2026 | Os três arquivos passam a ser versionados; `config/instrucoes.lock.json`; `tools/sincronizar_instrucoes.py` |
| H4 | GR2 como regional (com subordinadas); CGOV e COCAGE sem subordinadas | 26.09.2026 | Cadastro dos pilotos; seletores exatos |
| H5 | ADR-007 e ADR-008 aprovadas (a ADR-007 mantém a ressalva de regras institucionais pendentes) | 25.09.2026 | Cabeçalhos e lista de pendências da proposta do agente corrigidos na revisão documental |
| H8 | Aquisição real no piloto: nacional minimizada (opção a) | 25.09.2026 | Uma aquisição nacional por data, staging descartado, só A2 por piloto gravado |

## Decisões de processo (27.09.2026)

| Tema | Decisão |
| --- | --- |
| Instruções dos assistentes | Núcleo público, sem estado volátil. O excedente técnico e publicável vai para `docs/`; o operacional e o deliberativo, para o acervo privado |
| Git | Fora da reorganização, trabalho direto no `main`. Durante ela, branch `reorg/*` e uma PR única na publicação |
| Skills no Windows | Descoberta por junção de diretório (um link por skill), criada pelo instalador; links locais de cada computador |
| Pasta privada | Raiz em `PGD_PRIVADO_DIR` no script de links. Migração futura para biblioteca SharePoint de acesso restrito à equipe |

## Referências

- [ADR-009 — Arquitetura integrada](ADR-009-arquitetura-integrada.md)
- [ADR-010 — Sincronia das instruções](ADR-010-sincronia-instrucoes.md)
- [ADR-011 — Unidades piloto](ADR-011-unidades-piloto.md)
- [ADR-012 — Configuração Denodo](ADR-012-configuracao-denodo.md)
