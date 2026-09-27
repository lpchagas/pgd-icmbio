# ADR-009 — Arquitetura integrada do monorepo

**Data:** 27.09.2026 | **Estado:** aprovada (reorganização, decisões DP-01 e DP-02)

## Contexto

O projeto nasceu em dois repositórios: o analítico (`pgd-ocde-icmbio`), com os
indicadores OCDE e de gestão, e o do agente de gestão (`pgd-agente-icmbio`), com a base
local em MySQL e as especificações S01–S24. A reorganização os une num só repositório,
`pgd-icmbio`, com o histórico do agente preservado. Sem regras de fronteira, a junção
permitiria que o cálculo dos indicadores passasse a depender de componentes do agente,
como o banco local ou a API de modelo, que não fazem parte da validação A1–A5.

## Decisão

1. **Um repositório só** (`pgd-icmbio`), com o agente incorporado em `agente/` e o
   histórico preservado por merge.
2. **Responsabilidades separadas:**

   | Componente | Papel | Limite |
   | --- | --- | --- |
   | Denodo | Fonte de dados do PETRVS | Somente leitura (ADR-002) |
   | Núcleo analítico (`lib/`, `ocde/`, `gestao/`, `mgi/`, `relatorios/`) | Fórmulas, validação e relatórios | Não importa `agente`, `pymysql` nem `anthropic` |
   | Relatórios (`relatorios/`) | Apresentação dos resultados | Não repetem fórmulas: consomem os A2 |
   | Oracle de validação | Cálculo independente (A3) | Código próprio, nunca compartilhado com a produção |
   | Banco local do agente (MySQL) | Apoio ao agente: referências, versões, sincronização | Não é datamart dos indicadores |
   | Agente (`agente/`) | Capacidades S01–S24 | Só chama funções autorizadas do núcleo; os limites de `contratos-e-limites` são critério de ativação de cada capacidade |

3. **A dependência só vai num sentido:** o agente pode usar o núcleo, nunca o contrário.
   O teste `tests/regression/test_fronteira_nucleo.py` falha se um módulo do núcleo
   importar `agente`, `pymysql`, `anthropic` ou o `db` do agente.
4. **Caminhos:** a raiz do projeto vem de uma fonte única, `lib/caminhos.py`. Mover um
   módulo de pasta não muda o caminho dos artefatos.
5. **Pontes de compatibilidade:** os módulos que saíram de `ocde/relatorios/` para
   `relatorios/` mantêm pontes sem lógica, retiradas pela regra registrada no
   `CHANGELOG.md`.

## Alternativas consideradas

| Alternativa | Motivo do descarte |
| --- | --- |
| Manter dois repositórios | Configuração do Denodo e escopo dos pilotos divergentes; documentação duplicada |
| Incorporar o agente sem histórico | Perde autoria e rastreabilidade das decisões do agente |
| Reescrever em layout `src/` | Fora do escopo: muda caminhos certificados sem ganho funcional |
| Núcleo e agente importando-se livremente | O cálculo certificado passaria a depender de MySQL e de API externa |

## Consequências

- a validação A1–A5 continua dependendo só do Denodo e do Python do núcleo;
- o agente evolui sem risco de alterar indicadores certificados;
- mudança estrutural precisa provar equivalência por replay (`tools/replay_producao.py`);
  sem prova, vira mudança funcional com revalidação;
- as pontes têm prazo de retirada e são registradas no `CHANGELOG.md`.

## Referências

- [ADR-002 — Denodo somente leitura](ADR-002-denodo-somente-leitura.md)
- [ADR-003 — Arquitetura do agente](ADR-003-arquitetura-agente.md)
- [ADR-012 — Configuração Denodo única](ADR-012-configuracao-denodo.md)
- [Registro de decisões do projeto](registro-decisoes-projeto.md)
