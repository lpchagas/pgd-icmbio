# ADR-013 — Retirada do Codex: dois pares de instruções

**Data:** 17.10.2026 | **Estado:** aprovada (DP-07) | **Revisa:** [ADR-010](ADR-010-sincronia-instrucoes.md)

## Contexto

A [ADR-010](ADR-010-sincronia-instrucoes.md) organizou as instruções dos assistentes em
três pares sem hierarquia, um por ferramenta: `CLAUDE.md` (Claude Code), `AGENTS.md`
(Codex) e `PROJECT.md` (Antigravity). O projeto passou a usar só duas ferramentas:

- **Claude Code**, como ferramenta principal de desenvolvimento;
- **Antigravity**, como ferramenta secundária, para reduzir a dependência de um único
  fornecedor.

Manter um terceiro par sem ferramenta que o leia custa sincronia, testes e revisão de
conteúdo, e não traz ganho.

## Decisão

1. **Dois pares sem hierarquia:** `CLAUDE.md` e `PROJECT.md`. O resto da ADR-010
   continua valendo:
   - núcleo comum idêntico;
   - bloco da ferramenta com até 40 linhas;
   - arquivos públicos e regulares;
   - sincronia verificável.
2. **`AGENTS.md` retirado.** O arquivo sai da raiz e passa a ser recusado também ali:
   - o `.gitignore` o ignora em qualquer nível;
   - o auditor de segurança devolve o motivo `instrucao_retirada`.

   O nome continua na lista de instruções, então link e aninhamento seguem recusados.
3. **`.codex` mantido como caminho proibido** no `.gitignore` e no auditor, por defesa,
   mesmo sem uso. O link local deixa de ser criado.
4. **Skills:** a homologação exige descoberta única e equivalência funcional nas **duas**
   ferramentas. O gerenciador de skills deixa de conhecer o cliente `codex`.
5. **Sincronizador:** a tabela de estados mantém a numeração de 1 a 8. Com dois arquivos,
   o estado 6 (dois iguais e diferentes do lock, um igual ao lock) não ocorre: os dois
   iguais e diferentes do lock são o estado 2.

## Alternativas consideradas

| Alternativa | Motivo do descarte |
| --- | --- |
| Manter os três pares | Arquivo sem leitor, com custo de sincronia e revisão |
| Fonte canônica única com adaptadores gerados | Já descartada na ADR-010; a simetria entre as ferramentas continua exigida |
| Renumerar os estados do sincronizador | Mudaria mensagens, guia e testes sem ganho funcional |
| Liberar `.codex` no `.gitignore` | Abriria caminho para configuração local voltar ao Git sem revisão |

## Consequências

- `config/instrucoes.lock.json` passa a listar dois arquivos, e o hash do núcleo é
  regravado pelo sincronizador.
- O hook de pre-commit e o CI verificam os dois arquivos.
- Para trazer de volta uma terceira ferramenta, é preciso uma nova ADR que revise esta.

## Referências

- [ADR-010 — Sincronia das instruções](ADR-010-sincronia-instrucoes.md)
- [Sincronia das instruções — guia de operação](../governanca-projeto/sincronia-instrucoes.md)
- [Registro de decisões do projeto](registro-decisoes-projeto.md)
