# ADR-008 — Desenvolvimento individual, local-first e catálogo S01–S24 em ondas

**Data:** 23.08.2026 | **Estado:** aprovada

## Contexto

O protótipo é desenvolvido por uma pessoa, sem workspace gerenciado elegível e sem
orçamento incremental. Cronogramas anteriores pressupunham frentes técnica e negocial
paralelas. As ferramentas de desenvolvimento individuais ajudam a desenvolver, mas não licenciam uma solução
institucional.

## Decisão

1. O protótipo é local-first.
2. A capacidade-base é 12 horas semanais, com 8–9 efetivas.
3. O horizonte S01–S24 é 104 semanas, em cinco ondas e estabilização.
4. Há no máximo duas skills em andamento.
5. Serviços externos gratuitos recebem somente dados públicos ou sintéticos.
6. O custo incremental obrigatório é zero.
7. FastAPI `/docs` é a interface-base; Microsoft é opção futura.
8. Protótipo, piloto e solução institucional são estágios separados.

## Alternativas consideradas

| Alternativa | Motivo do descarte como base |
| --- | --- |
| GPT personalizado | plano individual não cria novo GPT e não cobre persistência/governança |
| Copilot Studio trial | temporário e dependente de licença/publicação |
| API paga desde a fundação | viola custo incremental zero |
| Implementar 24 skills como único MVP | risco alto de atraso e ausência de valor intermediário |
| Hospedagem pública gratuita | não adequada a conteúdo institucional ou SLA |

## Consequências

- protótipo utilizável chega antes do catálogo completo;
- a data final é replanejada com capacidade real;
- adoção institucional exige nova decisão, licença e segurança;
- ferramentas de desenvolvimento individuais não se tornam componentes de produção;
- documentação, testes e automação reduzem a dependência de pessoa única.

## Referências

- [AT-02](../agente/recursos-local-first.md)
- [Cronograma](../agente/projeto-v6/04-cronograma-capacidade-marcos.md)
- [Segurança e fontes](../agente/projeto-v6/06-seguranca-privacidade-fontes.md)
