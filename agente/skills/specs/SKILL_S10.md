# S10 — Analisador de Riscos, Dependências e Restrições

**Versão:** 0.1 | **Estado:** especificada documentalmente; não implementada | **Onda:** 2 | **Gate:** G2

## 1. Identificação e versão

ID canônico `S10`. Mudança incompatível exige nova versão do contrato; o ID não é reutilizado.

## 2. Objetivo funcional

Riscos estruturados, nível, respostas, responsáveis e alertas, para analisador de riscos, dependências e restrições de modo rastreável.

## 3. Usuários e permissões

Usuário principal: chefia e equipe. Leitura, proposta e confirmação devem respeitar o papel e o contexto da unidade.

## 4. Momento de uso

Planejamento, check-in e replanejamento.

## 5. Pré-condições

Entregas/metas e capacidade disponíveis.

## 6. Entradas

Entrega, contexto, dependências, probabilidade, impacto e controles. O contrato Pydantic definitivo será criado na implementação.

## 7. Saídas

Riscos estruturados, nível, respostas, responsáveis e alertas. A resposta também contém execução, status, fontes/regras, alertas, confiança aplicável e decisões/perguntas.

## 8. Regras negociais

Risco é evento incerto; separar causa, evento e consequência; resposta exige responsável/prazo. Regras ainda não validadas permanecem propostas.

## 9. Fontes

Fontes institucionais aprovadas em Q5, atos normativos vigentes e artefatos metodológicos identificados no índice. Trecho, versão e vigência acompanham a saída.

## 10. Cálculos determinísticos

Matriz P×I, campos, datas, estado e risco residual. Devem alcançar 100% na bateria definida.

## 11. Uso permitido do LLM

Propor redação, categorias e respostas. O modelo não toma decisão humana nem altera cálculo.

## 12. Comportamento em ambiguidade

Baixa confiança, conflito ou falta de contexto produz alerta e pergunta pendente; não há preenchimento silencioso.

## 13. Perguntas pendentes

Registrar dado faltante, motivo, destinatário e item bloqueado. A execução pode ficar `aguardando_dados`.

## 14. Decisões humanas

A confirmação do usuário autorizado é persistida separadamente da sugestão automática, com justificativa quando exigida.

## 15. Entidades consultadas

Entregas, capacidade, regras e registros de risco.

## 16. Entidades gravadas

Registros_risco, execucoes_skill, perguntas e decisões. Entidades versionáveis usam exclusivamente `src/dados/versoes.py`.

## 17. Dependências

S05 e S07.

## 18. Fluxo principal

Identificar → estruturar → calcular nível → propor resposta → decidir → monitorar.

## 19. Fluxos alternativos

Problema já ocorrido vira ocorrência; dependência vira vínculo; dado insuficiente não recebe nível exato.

## 20. Erros e contingências

Contrato inválido é rejeitado; serviço indisponível não gera resultado inventado; falha transacional executa rollback; erro retorna código seguro e identificador da execução.

## 21. Privacidade e segurança

Não registrar condição pessoal detalhada como risco. Conteúdo restrito não é enviado a serviço externo.

## 22. Observabilidade e rastreabilidade

Registrar `execucao_id`, skill/versão, duração, estado, fontes/regras, entidades, alertas e erro. Logs não repetem segredo ou conteúdo sensível.

## 23. Casos de teste

S10-T01 risco válido; T02 problema; T03 sem responsável; T04 residual; T05 dado sensível. Acrescentar casos de contrato, autorização, dado ausente, falha externa e regressão.

## 24. Critérios de aceite

Causa/evento/consequência, P×I, resposta e autoridade estão claros; todos os casos críticos aprovados e aceite humano registrado.

## 25. Limites e itens fora da skill

Não aceita risco em nome da chefia.

## 26. Estado de desenvolvimento

Ficha v6 criada. Implementação, conjunto anotado, testes e validação institucional continuam pendentes.

## 27. Histórico de alterações

| Versão | Data | Alteração |
| --- | --- | --- |
| 0.1 | 23/08/2026 | Especificação operacional inicial da proposta v6 |

