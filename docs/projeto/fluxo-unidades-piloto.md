# Fluxo das unidades piloto

Como uma capacidade (indicador, análise de gestão ou relatório) passa das três
unidades piloto para outros escopos. Vigente desde o lote L5 da reorganização.

## Pilotos

O cadastro versionado [`config/unidades-piloto.json`](../../config/unidades-piloto.json)
define as três unidades e o recorte de cada uma:

| Piloto | Seletor | Subordinadas |
| --- | --- | --- |
| CGOV | `--unidade CGOV` | não |
| COCAGE | `--unidade COCAGE` | não |
| GR2 | `--regional GR2` | sim, pela hierarquia do PETRVS, em qualquer profundidade |

`--regional CGOV` não é o piloto CGOV: o recorte precisa ser exatamente o
cadastrado.

O `id_petrvs` de cada piloto foi conferido na fonte em 26/09/2026. Antes de cada
execução real e de cada registro de aceite, o cadastro é conferido de novo contra a
hierarquia atual: se o id não for a unidade resolvida, a operação é recusada.

## Escopo resolvido

A seleção por escopo tem um único caminho (`relatorios.escopo`), usado pela
extração OCDE, pelos relatórios, pelo ciclo gerencial, pelo `gestao.runner` e pelo
`validation_runner`.

**Qual hierarquia vale:** a subordinação segue a hierarquia do próprio **PETRVS**
(`unidade_pai_id`), de onde vêm os PE e os PT. A decisão é de 26/09/2026 e é
provisória até a CGOV deliberar a Q1 (fonte primária da taxonomia).

- O motivo: na estrutura oficial, a maior parte das unidades subordinadas à GR2 não
  tem sigla. Como os produtos são filtrados pela sigla, o recorte "GR2" certificado
  antes disso cobria só a própria regional.
- A hierarquia é lida de um retrato local e privado, gerado por
  `python -m tools.atualizar_unidades_petrvs`. O hash do arquivo identifica a
  hierarquia usada.
- A estrutura oficial continua servindo aos seletores por rótulo (`--mesogrupo` e
  `--tipo-unidade`).

São erro, nunca outro critério em silêncio:

- `--regional`, `--unidade` ou `--lista-unidades` sem o retrato da hierarquia;
- unidade inexistente;
- sigla repetida no PETRVS com homônimas dos dois lados do recorte. Quando todas as
  homônimas ficam dentro do recorte, ele é exato.

A chave do escopo (pasta dos artefatos) é a mesma nos cinco pontos:
`regional-gr2`, `unidade-cgov`, `tipo_unidade-uc`, e `lista_unidades-<hash>` para
listas — o hash depende só das siglas, nunca do nome do arquivo.

## Gate de liberação

| Escopo | Produto | Resultado |
| --- | --- | --- |
| Piloto | qualquer | executa |
| Fora dos pilotos | restrito, rascunho ou A2 intermediário | executa (uso restrito atual) |
| Fora dos pilotos | final ou compartilhável | só com a capacidade **elegível** |

Uma capacidade é elegível quando há, para a **mesma identidade do candidato**, um
aceite válido em cada um dos três pilotos e uma deliberação de expansão. A
identidade reúne a capacidade, a versão de fórmula ou contrato, o fingerprint
(último commit que tocou as dependências e o hash de cada dependência transitiva),
a versão da política, a versão do cadastro e o escopo resolvido de cada piloto.

O aceite é recusado quando a evidência falta, foi alterada ou revogada, quando o
manifesto veio de fixture, de retomada ou de consolidação, quando o escopo
resolvido mudou e quando a versão é a mesma mas o fingerprint não. Mudança
estrutural equivalente segue procedimento de transição próprio: não herda aceite.

O gate é aplicado em `lib.indicator_extraction`, `gestao.runner`,
`relatorios.relatorio_v2`, `relatorios.relatorio_cumulativo` e
`lib.ciclo_gerencial` (as pontes `ocde.relatorios.*` herdam). Os scripts A1 são
primitivas internas: **não são canal de liberação**, e a política não é uma
barreira técnica contra a chamada direta.

## Comandos

Execução nos três pilotos, com resultado separado por piloto e sem total agregado:

```bash
python -m tools.executar_pilotos --capacidade I02 --data-execucao 2026-09-26
```

Registro de aceite, deliberação, revogação e verificação (acervo privado; a
evidência aponta para o ato humano, e o registro não é assinatura):

```bash
python -m tools.registrar_aceite_piloto verificar --capacidade I02
```

Os registros antigos do marco GR2 → nacional do relatório cumulativo ficam
marcados como política `gr2-v1`, sem reinterpretação.
