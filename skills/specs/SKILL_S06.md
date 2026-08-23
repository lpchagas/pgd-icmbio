# S06 — Auditor de Portfólio de Entregas

**Versão:** 0.1 | **Estado:** especificada documentalmente; não implementada | **Onda:** 2 | **Gate:** G2

## 1. Identificação e versão

ID canônico `S06`. Mudança incompatível exige nova versão do contrato; o ID não é reutilizado.

## 2. Objetivo funcional

Achados de lacuna, duplicidade, sobreposição, granularidade e recomendação, para auditor de portfólio de entregas de modo rastreável.

## 3. Usuários e permissões

Usuário principal: chefia e analista de governança. Leitura, proposta e confirmação devem respeitar o papel e o contexto da unidade.

## 4. Momento de uso

Antes da pactuação e em revisões do portfólio.

## 5. Pré-condições

Catálogo, competências e critérios disponíveis.

## 6. Entradas

Conjunto de entregas, competências, metas e período. O contrato Pydantic definitivo será criado na implementação.

## 7. Saídas

Achados de lacuna, duplicidade, sobreposição, granularidade e recomendação. A resposta também contém execução, status, fontes/regras, alertas, confiança aplicável e decisões/perguntas.

## 8. Regras negociais

Não excluir/fundir automaticamente; cobertura deve ser justificada; recomendação não é decisão. Regras ainda não validadas permanecem propostas.

## 9. Fontes

Fontes institucionais aprovadas em Q5, atos normativos vigentes e artefatos metodológicos identificados no índice. Trecho, versão e vigência acompanham a saída.

## 10. Cálculos determinísticos

Campos, cobertura por vínculo, datas, estados e duplicidade exata. Devem alcançar 100% na bateria definida.

## 11. Uso permitido do LLM

Similaridade, sobreposição de resultado e clareza. O modelo não toma decisão humana nem altera cálculo.

## 12. Comportamento em ambiguidade

Baixa confiança, conflito ou falta de contexto produz alerta e pergunta pendente; não há preenchimento silencioso.

## 13. Perguntas pendentes

Registrar dado faltante, motivo, destinatário e item bloqueado. A execução pode ficar `aguardando_dados`.

## 14. Decisões humanas

A confirmação do usuário autorizado é persistida separadamente da sugestão automática, com justificativa quando exigida.

## 15. Entidades consultadas

Fontes/regras, candidatas, entregas/versões e competências.

## 16. Entidades gravadas

Execucoes_skill, perguntas e decisões. Entidades versionáveis usam exclusivamente `src/dados/versoes.py`.

## 17. Dependências

S02, S04 e S05.

## 18. Fluxo principal

Validar conjunto → medir cobertura → analisar duplicidades/granularidade → priorizar achados → revisão humana.

## 19. Fluxos alternativos

Competência sem entrega vira lacuna; entrega sem competência pede justificativa; conflito normativo bloqueia.

## 20. Erros e contingências

Contrato inválido é rejeitado; serviço indisponível não gera resultado inventado; falha transacional executa rollback; erro retorna código seguro e identificador da execução.

## 21. Privacidade e segurança

Resultado agregado por portfólio; sem avaliação individual. Conteúdo restrito não é enviado a serviço externo.

## 22. Observabilidade e rastreabilidade

Registrar `execucao_id`, skill/versão, duração, estado, fontes/regras, entidades, alertas e erro. Logs não repetem segredo ou conteúdo sensível.

## 23. Casos de teste

S06-T01 íntegro; T02 lacuna; T03 duplicidade; T04 sobreposição; T05 granularidade; T06 exceção justificada. Acrescentar casos de contrato, autorização, dado ausente, falha externa e regressão.

## 24. Critérios de aceite

Achados reproduzíveis e decisões registradas sem alteração automática do catálogo; todos os casos críticos aprovados e aceite humano registrado.

## 25. Limites e itens fora da skill

Não pactua PE e não aloca pessoas.

## 26. Estado de desenvolvimento

Ficha v6 criada. Implementação, conjunto anotado, testes e validação institucional continuam pendentes.

## 27. Histórico de alterações

| Versão | Data | Alteração |
| --- | --- | --- |
| 0.1 | 23/08/2026 | Especificação operacional inicial da proposta v6 |

