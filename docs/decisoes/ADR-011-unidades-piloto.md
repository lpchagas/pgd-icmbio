# ADR-011 — Política das três unidades piloto

**Data:** 27.09.2026 | **Estado:** aprovada (DP-04; H4 e H8)

## Contexto

Antes da reorganização, cada parte do projeto tratava o piloto de um jeito: o agente
filtrava `CGOV` e `COCAGE` por sigla, e o relatório cumulativo usava a GR2 como etapa
para o escopo nacional. Havia duas implementações de escopo com semânticas diferentes.
Sem uma política única, um produto poderia ser liberado além das unidades que o
validaram.

## Decisão

1. **Três unidades piloto**, cadastradas em `config/unidades-piloto.json` com o
   `id_petrvs` conferido na fonte:

   | Piloto | Seletor | Subordinadas |
   | --- | --- | --- |
   | CGOV | `--unidade CGOV` | não |
   | COCAGE | `--unidade COCAGE` | não |
   | GR2 | `--regional GR2` | sim, pela hierarquia do PETRVS (decisão CGOV D19, com trava de divergência) |

2. **Escopo resolvido único** (`relatorios.escopo`) nos pontos oficiais. Unidade
   ausente, sigla ambígua ou fonte indisponível **é erro**; nunca há queda silenciosa
   para o escopo nacional.
3. **Aquisição (H8, opção a):**
   - Os A1 OCDE consultam o universo nacional **uma vez**. O staging é descartado, e só
     o A2 de cada piloto é gravado.
   - O registro declara "escopo de aquisição nacional", e o filtro posterior nunca é
     chamado de consulta restrita.
   - Os A1 de gestão filtram as siglas na própria consulta.
4. **Resultados separados por piloto.** Não há total agregado: somar taxas exigiria
   recompor numeradores e denominadores, e pessoas e planos podem estar em mais de um
   recorte.
5. **Gate de liberação** (`lib/liberacao.py`):
   - fora dos pilotos, produto final ou compartilhável exige três aceites da mesma
     identidade (capacidade, versão, fingerprint do candidato, política, cadastro e
     escopo) e uma deliberação de expansão;
   - a verificação é aplicada nos pontos oficiais;
   - os A1 são primitivas internas, não canal de liberação.
6. **Certificação automática não é aceite.** A1–A5 são evidência técnica. O aceite é
   ato humano, registrado com referência ao documento no acervo privado.

## Alternativas consideradas

| Alternativa | Motivo do descarte |
| --- | --- |
| Cinco pilotos (com ACADEBIO e GR1) | Reduzido a três (DP-04) para caber no calendário de aceite |
| Consultas filtradas no Denodo para a OCDE (H8, opção b) | Alteraria os A1 certificados e exigiria revalidação completa |
| Total consolidado dos três pilotos | Estatisticamente incorreto e sujeito a dupla contagem |
| Liberação pela certificação automática | Confunde evidência técnica com decisão institucional |

## Consequências

- a expansão para além dos pilotos depende de deliberação própria e continua suspensa
  (decisão CGOV D16);
- mudança de fórmula ou do cadastro muda a identidade e não herda aceite em silêncio;
- o executor `tools/executar_pilotos.py` roda os três pilotos com uma aquisição só.

## Referências

- [Fluxo das unidades piloto](../projeto/fluxo-unidades-piloto.md)
- [Protocolo de validação A1–A5](../indicadores/protocolo-validacao.md)
- [Registro de decisões do projeto](registro-decisoes-projeto.md)
