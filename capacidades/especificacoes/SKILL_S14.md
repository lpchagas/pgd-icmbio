# S14 — Gestor de Alterações e Replanejamento

**Versão:** 0.1 | **Estado:** especificada documentalmente; não implementada | **Onda:** 3 | **Gate:** G3

## 1. Identificação e versão

ID canônico `S14`. Mudança incompatível exige nova versão do contrato; o ID não é reutilizado.

## 2. Objetivo funcional

Comparação, proposta de nova versão, pendências e decisão, para gestor de alterações e replanejamento de modo rastreável.

## 3. Usuários e permissões

Usuário principal: chefia e participante conforme competência. Leitura, proposta e confirmação devem respeitar o papel e o contexto da unidade.

## 4. Momento de uso

Quando mudança material afeta PE/PT.

## 5. Pré-condições

Plano vigente, motivo e impacto identificados.

## 6. Entradas

Plano atual, solicitação, justificativa, impacto, riscos e proposta. O contrato Pydantic definitivo será criado na implementação.

## 7. Saídas

Comparação, proposta de nova versão, pendências e decisão. A resposta também contém execução, status, fontes/regras, alertas, confiança aplicável e decisões/perguntas.

## 8. Regras negociais

Não sobrescrever; preservar anterior; mudança exige justificativa/competência; efeito prospectivo conforme regra. Regras ainda não validadas permanecem propostas.

## 9. Fontes

Fontes institucionais aprovadas em Q5, atos normativos vigentes e artefatos metodológicos identificados no índice. Trecho, versão e vigência acompanham a saída.

## 10. Cálculos determinísticos

Diff estruturado, versão, datas, totais e compatibilidade. Devem alcançar 100% na bateria definida.

## 11. Uso permitido do LLM

Resumir mudança, impacto e justificativa. O modelo não toma decisão humana nem altera cálculo.

## 12. Comportamento em ambiguidade

Baixa confiança, conflito ou falta de contexto produz alerta e pergunta pendente; não há preenchimento silencioso.

## 13. Perguntas pendentes

Registrar dado faltante, motivo, destinatário e item bloqueado. A execução pode ficar `aguardando_dados`.

## 14. Decisões humanas

A confirmação do usuário autorizado é persistida separadamente da sugestão automática, com justificativa quando exigida.

## 15. Entidades consultadas

Planos/versões, check-ins, riscos, regras e decisões.

## 16. Entidades gravadas

Nova versão por serviço, execução, perguntas e decisão. Entidades versionáveis usam exclusivamente `agente/dados/versoes.py`.

## 17. Dependências

S02, S11 e S13.

## 18. Fluxo principal

Receber mudança → comparar → avaliar impacto/regras → propor versão → decidir → persistir.

## 19. Fluxos alternativos

Ajuste pequeno pode ser registro sem versão conforme regra; conflito bloqueia; rejeição preserva atual.

## 20. Erros e contingências

Contrato inválido é rejeitado; serviço indisponível não gera resultado inventado; falha transacional executa rollback; erro retorna código seguro e identificador da execução.

## 21. Privacidade e segurança

Mostrar apenas dados necessários aos decisores. Conteúdo restrito não é enviado a serviço externo.

## 22. Observabilidade e rastreabilidade

Registrar `execucao_id`, skill/versão, duração, estado, fontes/regras, entidades, alertas e erro. Logs não repetem segredo ou conteúdo sensível.

## 23. Casos de teste

S14-T01 nova versão; T02 rejeitada; T03 concorrência; T04 impacto CHD; T05 regra conflitante. Acrescentar casos de contrato, autorização, dado ausente, falha externa e regressão.

## 24. Critérios de aceite

Histórico íntegro, decisão e justificativa vinculadas, nenhuma sobrescrita; todos os casos críticos aprovados e aceite humano registrado.

## 25. Limites e itens fora da skill

Não aprova mudança nem reescreve evidência passada.

## 26. Estado de desenvolvimento

Ficha v6 criada. Implementação, conjunto anotado, testes e validação institucional continuam pendentes.

## 27. Histórico de alterações

| Versão | Data | Alteração |
| --- | --- | --- |
| 0.1 | 23/08/2026 | Especificação operacional inicial da proposta v6 |

