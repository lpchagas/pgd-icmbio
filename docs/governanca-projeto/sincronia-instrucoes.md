# Sincronia das instruções dos assistentes

> **Para quem é:** quem edita `CLAUDE.md`, `AGENTS.md` ou `PROJECT.md`. A decisão e as
> alternativas estão na [ADR-010](../decisoes/ADR-010-sincronia-instrucoes.md).

## 1. Como os arquivos são organizados

Os três arquivos da raiz têm a mesma estrutura:

```text
# Instruções do projeto — <ferramenta>        ← título (única linha antes do núcleo)

<!-- nucleo-comum:inicio -->
... núcleo comum, idêntico nos três ...
<!-- nucleo-comum:fim -->

## Mecânica da ferramenta                      ← bloco da ferramenta (até 40 linhas)
## Skills desta ferramenta
## Comandos da ferramenta
```

- **Núcleo comum:** regras do projeto. Sem segredos, dados pessoais ou números voláteis
  (contagens, datas de execução, resultados de teste).
- **Bloco da ferramenta:** só o que é próprio de cada assistente, com no máximo 40 linhas
  e apenas os três títulos acima.
- Os três são **arquivos regulares** versionados no Git. Link, junção ou hardlink é
  recusado.
- Instruções em subpastas (por exemplo, `agente/AGENTS.md`) são proibidas e ficam fora do Git:
  o `.gitignore` e o auditor de segurança as recusam.

## 2. Editar o núcleo

1. Edite o núcleo em **qualquer um** dos três arquivos.
2. Propague para os outros dois e atualize o lock:

   ```text
   python -m tools.sincronizar_instrucoes sincronizar
   ```

3. Confira e prepare o commit:

   ```text
   python -m tools.sincronizar_instrucoes verificar
   git add CLAUDE.md AGENTS.md PROJECT.md config/instrucoes.lock.json
   ```

A mudança do núcleo passa por revisão de conteúdo na PR: a sincronia só garante que os
três textos são iguais, não que o conteúdo está correto.

## 3. Estados

O hash do núcleo normalizado (UTF-8 sem BOM, LF, sem espaço no fim da linha) fica em
`config/instrucoes.lock.json`.

| # | Situação | `verificar` | `sincronizar` |
| --- | --- | --- | --- |
| 1 | Os três iguais ao lock | ok (saída 0) | nada a fazer |
| 2 | Os três iguais entre si e diferentes do lock | falha (1) | atualiza o lock |
| 3 | Lock ausente e os três iguais | falha (1) | cria o lock |
| 4 | Lock ausente e núcleos diferentes | conflito (2) | não escreve; grava relatório de diferenças |
| 5 | Um alterado, dois iguais ao lock | falha (1) | propaga o alterado |
| 6 | Dois iguais entre si e diferentes do lock, um igual ao lock | falha (1) | só retoma operação interrompida registrada no diário; sem diário, conflito (2) |
| 7 | Dois ou três alterados de formas diferentes | conflito (2) | não escreve; grava relatório de diferenças |
| 8 | Marcador ausente ou duplicado, texto antes do núcleo, título não permitido ou bloco com mais de 40 linhas | erro (3) | não escreve |

A saída 4 indica outra operação em andamento (lock de exclusão presente).

**Conflito:** resolva à mão, deixando o núcleo desejado em um arquivo e os outros dois
iguais ao lock, e rode `sincronizar`. O relatório de diferenças
(`conflito-<data>.md`) fica na pasta de sincronia da área privada, fora do Git.

## 4. Interrupção e recuperação

Cada arquivo é gravado de forma atômica, mas não há transação sobre os três. Se a
operação for interrompida no meio:

```text
python -m tools.sincronizar_instrucoes recuperar              # retoma a operação
python -m tools.sincronizar_instrucoes recuperar --desfazer   # volta ao estado anterior
python -m tools.sincronizar_instrucoes recuperar --abandonar  # encerra sem escrever
```

- O **diário** registra, para cada arquivo, o hash lido, o esperado e se já foi escrito,
  com cópias do antes e do depois. Ele fica na área privada de sincronia.
- Antes de cada substituição, o script confere se o arquivo ainda tem o hash lido
  (compare-and-swap). Se alguém editou no meio, nada mais é escrito.
- O **lock de exclusão** registra pid, host e operação. Ele só é removido pela
  recuperação quando foi criado neste computador e o processo não existe mais. A idade
  do lock nunca conta.

## 5. Hook e CI

- **Hook local** (`.githooks/pre-commit`): roda `verificar --staged`, que lê os
  arquivos preparados no índice, e **nunca** modifica arquivos. Se falhar, rode
  `sincronizar` e `git add`.
- **CI** (`.github/workflows/quality.yml`): roda `verificar` sem depender do hook.

## 6. Migrar instruções antigas

Para comparar instruções antigas com o núcleo, sem copiar nada:

```text
python -m tools.sincronizar_instrucoes importar --de <pasta-com-as-instrucoes-antigas>
```

O modo `importar` só lista os títulos e o número de linhas das seções fora do núcleo.
Você decide o que migrar, e o conteúdo técnico publicável vai para `docs/`.
