# ADR-012 — Configuração única do Denodo

**Data:** 27.09.2026 | **Estado:** aprovada (tabela de configuração aprovada em 24.09.2026)

## Contexto

Os dois repositórios de origem liam o Denodo com nomes de variáveis diferentes. O
analítico usava `DENODO_PASSWORD`, `DENODO_DRIVER_PATH`, `DENODO_HOST`, `DENODO_PORT` e
`DENODO_DATABASE`; o agente usava `DENODO_PASS`, `DENODO_JDBC_JAR` e uma `DENODO_URL`
completa. Duas configurações para a mesma fonte abrem espaço para conexões diferentes
e para credenciais repetidas.

## Decisão

1. **Um adaptador só:** `lib/denodo_config.py`. Os nomes canônicos estão em
   `.env.example`, e as credenciais só existem no `.env` local.
2. **Aliases temporários** para os nomes do agente:

   | Nome antigo | Nome canônico | Regra |
   | --- | --- | --- |
   | `DENODO_PASS` | `DENODO_PASSWORD` | Se os dois existirem com valores diferentes, é erro, sem exibir valores |
   | `DENODO_JDBC_JAR` | `DENODO_DRIVER_PATH` | Caminhos normalizados antes de comparar |
   | `DENODO_URL` | `DENODO_HOST`, `DENODO_PORT`, `DENODO_DATABASE` | Conversão de `jdbc:denodo://host:porta/base`; parâmetro extra é recusado, não descartado |
   | `DENODO_JVM_DLL` | `DENODO_JVM_DLL` | Já canônica |
   | `JAVA_HOME` | resolução alternativa da JVM | Precedência mantida |

   O uso de um alias emite aviso, e o nome canônico é o preferido.
3. **A suíte de testes nunca abre o Denodo:** com `PGD_BLOQUEAR_DENODO=1`, definida
   pelo `conftest`, `lib.denodo_config.connect` recusa qualquer conexão, também nos A1
   executados em subprocesso.
4. **Somente leitura** (ADR-002). O acesso depende de IP liberado pelo Dataprev.

## Alternativas consideradas

| Alternativa | Motivo do descarte |
| --- | --- |
| Manter os dois conjuntos de variáveis | Duas fontes de verdade para a mesma conexão |
| Trocar os nomes de uma vez, sem aliases | Quebraria ambientes do agente ainda configurados com os nomes antigos |
| Descartar parâmetros extras da URL | Mudaria a conexão em silêncio |

## Consequências

- **Retirada dos aliases:** só com evidência de que não há consumidor **e** com uma
  execução operacional compatível, registrada no `CHANGELOG.md`;
- um erro de configuração nunca exibe valores de variáveis;
- a mesma configuração serve à produção, à validação e ao agente.

## Referências

- [ADR-002 — Denodo somente leitura](ADR-002-denodo-somente-leitura.md)
- [Acesso ao Denodo e DBeaver](../ambiente/acesso-denodo-dbeaver.md)
- [Checklist de segurança para publicação](../ambiente/seguranca-publicacao.md)
