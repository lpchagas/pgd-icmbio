# S11 — Assistente de Pactuação do Plano de Entregas

**Versão:** 0.1 | **Estado:** especificada documentalmente; não implementada | **Onda:** 3 | **Gate:** G3

## 1. Identificação e versão

ID canônico `S11`. Mudança incompatível exige nova versão do contrato; o ID não é reutilizado.

## 2. Objetivo funcional

Minuta estruturada de PE, pendências e versão pactuada após decisão, para assistente de pactuação do plano de entregas de modo rastreável.

## 3. Usuários e permissões

Usuário principal: chefia da unidade. Leitura, proposta e confirmação devem respeitar o papel e o contexto da unidade.

## 4. Momento de uso

Antes do ciclo de execução do PE.

## 5. Pré-condições

Portfólio auditado, capacidade, metas e riscos disponíveis.

## 6. Entradas

Unidade, período, entregas, metas, capacidade, riscos e vínculos. O contrato Pydantic definitivo será criado na implementação.

## 7. Saídas

Minuta estruturada de PE, pendências e versão pactuada após decisão. A resposta também contém execução, status, fontes/regras, alertas, confiança aplicável e decisões/perguntas.

## 8. Regras negociais

PE usa entregas da unidade; metas e critérios claros; respeitar competência, período e capacidade. Regras ainda não validadas permanecem propostas.

## 9. Fontes

Fontes institucionais aprovadas em Q5, atos normativos vigentes e artefatos metodológicos identificados no índice. Trecho, versão e vigência acompanham a saída.

## 10. Cálculos determinísticos

Completude, datas, totais, IDs e coerência de período. Devem alcançar 100% na bateria definida.

## 11. Uso permitido do LLM

Redigir justificativas e resumo da pactuação. O modelo não toma decisão humana nem altera cálculo.

## 12. Comportamento em ambiguidade

Baixa confiança, conflito ou falta de contexto produz alerta e pergunta pendente; não há preenchimento silencioso.

## 13. Perguntas pendentes

Registrar dado faltante, motivo, destinatário e item bloqueado. A execução pode ficar `aguardando_dados`.

## 14. Decisões humanas

A confirmação do usuário autorizado é persistida separadamente da sugestão automática, com justificativa quando exigida.

## 15. Entidades consultadas

S02/S06/S07/S10, entregas, capacidade, riscos e objetivos.

## 16. Entidades gravadas

Entidade/versões futuras de PE, execucoes_skill, perguntas e decisões. Entidades versionáveis usam exclusivamente `agente/dados/versoes.py`.

## 17. Dependências

S02, S06, S07 e S10.

## 18. Fluxo principal

Selecionar período → compor entregas → validar → apresentar pendências → pactuar → persistir versão.

## 19. Fluxos alternativos

Capacidade insuficiente gera cenário; regra conflitante bloqueia; minuta pode ser salva como rascunho.

## 20. Erros e contingências

Contrato inválido é rejeitado; serviço indisponível não gera resultado inventado; falha transacional executa rollback; erro retorna código seguro e identificador da execução.

## 21. Privacidade e segurança

PE é organizacional; excluir informação individual desnecessária. Conteúdo restrito não é enviado a serviço externo.

## 22. Observabilidade e rastreabilidade

Registrar `execucao_id`, skill/versão, duração, estado, fontes/regras, entidades, alertas e erro. Logs não repetem segredo ou conteúdo sensível.

## 23. Casos de teste

S11-T01 completo; T02 sem meta; T03 capacidade insuficiente; T04 regra conflitante; T05 versão. Acrescentar casos de contrato, autorização, dado ausente, falha externa e regressão.

## 24. Critérios de aceite

PE coerente, rastreável, pactuado e versionado; todos os casos críticos aprovados e aceite humano registrado.

## 25. Limites e itens fora da skill

Não registra execução nem avaliação.

## 26. Estado de desenvolvimento

Ficha v6 criada. Implementação, conjunto anotado, testes e validação institucional continuam pendentes.

## 27. Histórico de alterações

| Versão | Data | Alteração |
| --- | --- | --- |
| 0.1 | 23/08/2026 | Especificação operacional inicial da proposta v6 |

