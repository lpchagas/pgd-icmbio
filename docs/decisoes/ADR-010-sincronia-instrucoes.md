# ADR-010 — Instruções dos assistentes: pares sincronizados, sem hierarquia

**Data:** 27.09.2026 | **Estado:** aprovada (DP-03; conteúdo aprovado na H1)

## Contexto

O projeto é mantido com três assistentes de programação: Claude Code, Codex e
Antigravity. Cada um lê o próprio arquivo de instruções na raiz (`CLAUDE.md`,
`AGENTS.md` e `PROJECT.md`). Esses arquivos eram privados, mantidos à mão e ligados à
pasta privada por hardlinks. Com o tempo, divergiram:

- comandos de teste diferentes;
- contagens e datas desatualizadas;
- regras de Git conflitantes;
- estado do projeto misturado com regras.

Os hardlinks também se romperam sem aviso.

## Decisão

1. **Três pares sem hierarquia.** Nenhum dos arquivos é mestre: qualquer um pode ser
   editado.
2. **Núcleo comum idêntico** nos três, entre `<!-- nucleo-comum:inicio -->` e
   `<!-- nucleo-comum:fim -->`. Ele contém:
   - regras invioláveis;
   - pilotos;
   - Denodo;
   - estrutura;
   - validação;
   - ambiente;
   - Git;
   - skills.
3. **Bloco da ferramenta** depois do marcador final: até 40 linhas, só com os títulos
   "Mecânica da ferramenta", "Skills desta ferramenta" e "Comandos da ferramenta".
4. **Os três arquivos são públicos e versionados.**
   - Não contêm segredos, dados pessoais nem números voláteis: contagens, datas de
     execução e resultados de teste ficam no `CHANGELOG.md` e em
     `capacidades/CATALOGO.md`.
   - São arquivos regulares, nunca links.
   - Instruções aninhadas (por exemplo, `agente/AGENTS.md`) continuam proibidas e fora do Git.
5. **Sincronia verificável** por `tools/sincronizar_instrucoes.py`:
   - o hash do núcleo normalizado fica em `config/instrucoes.lock.json`;
   - a tabela de 8 estados decide entre propagar, atualizar o lock ou recusar por
     conflito;
   - o hook de pre-commit e o CI só **verificam**; quem escreve é a pessoa, pelo modo
     `sincronizar`.
6. **Garantias honestas:**
   - a escrita é atômica **por arquivo**, e não há transação sobre o conjunto;
   - o diário de operação, o compare-and-swap e o lock de exclusão detectam estado
     parcial e permitem retomar ou desfazer.

## Alternativas consideradas

| Alternativa | Motivo do descarte |
| --- | --- |
| Fonte canônica única com adaptadores gerados | A simetria entre as ferramentas foi exigência confirmada (DP-03) |
| Manter os arquivos privados | O conteúdo divergia sem controle; as regras do projeto são públicas por natureza |
| Hardlinks para a pasta privada | Rompem sem aviso e escondem a divergência; o sincronizador os recusa |
| Hook que corrige sozinho | Alteraria arquivos no commit sem revisão; o hook só verifica |

## Consequências

- toda mudança do núcleo passa por revisão de conteúdo na PR. A sincronia textual não
  equivale a aprovação;
- o teste de títulos valida a estrutura do bloco, mas uma regra de negócio escondida
  sob título permitido só é detectada na revisão;
- as skills continuam privadas (`.agents/skills`). Os links de descoberta são locais de
  cada computador e são recriados pelo instalador.

## Referências

- [Sincronia das instruções — guia de operação](../governanca-projeto/sincronia-instrucoes.md)
- [Organização público-privado](../ambiente/organizacao-publico-privado.md)
- [Registro de decisões do projeto](registro-decisoes-projeto.md)
