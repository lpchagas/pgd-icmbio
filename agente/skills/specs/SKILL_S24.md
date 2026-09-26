# S24 — Avaliação do Plano de Trabalho do Participante

**Versão:** 0.1 | **Estado:** especificada documentalmente; não implementada | **Onda:** 5 | **Gate:** G5

## 1. Identificação e versão

ID canônico `S24`. Mudança incompatível exige nova versão do contrato; o ID não é reutilizado.

## 2. Objetivo funcional

Parecer, conceito proposto, decisão, notificação, recurso/reavaliação e ação de desenvolvimento, para avaliação do plano de trabalho do participante de modo rastreável.

## 3. Usuários e permissões

Usuário principal: chefia da unidade de execução. Leitura, proposta e confirmação devem respeitar o papel e o contexto da unidade.

## 4. Momento de uso

Após registro do PT e dentro do prazo configurado.

## 5. Pré-condições

S23 concluída, critérios pactuados, evidências e avaliador competente.

## 6. Entradas

PT, execução, critérios, evidências, fatores, avaliador, notificação e eventual recurso. O contrato Pydantic definitivo será criado na implementação.

## 7. Saídas

Parecer, conceito proposto, decisão, notificação, recurso/reavaliação e ação de desenvolvimento. A resposta também contém execução, status, fontes/regras, alertas, confiança aplicável e decisões/perguntas.

## 8. Regras negociais

Avaliação única do plano; cinco critérios; justificativa para extremos; recurso/reavaliação versionada; contribuição, não comportamento. Regras ainda não validadas permanecem propostas.

## 9. Fontes

Fontes institucionais aprovadas em Q5, atos normativos vigentes e artefatos metodológicos identificados no índice. Trecho, versão e vigência acompanham a saída.

## 10. Cálculos determinísticos

Prazo de avaliação/recurso, faixa, competência, completude e estados. Devem alcançar 100% na bateria definida.

## 11. Uso permitido do LLM

Fundamentar parecer e organizar manifestação, sem decidir. O modelo não toma decisão humana nem altera cálculo.

## 12. Comportamento em ambiguidade

Baixa confiança, conflito ou falta de contexto produz alerta e pergunta pendente; não há preenchimento silencioso.

## 13. Perguntas pendentes

Registrar dado faltante, motivo, destinatário e item bloqueado. A execução pode ficar `aguardando_dados`.

## 14. Decisões humanas

A confirmação do usuário autorizado é persistida separadamente da sugestão automática, com justificativa quando exigida.

## 15. Entidades consultadas

S10/S12/S17/S21/S23, regras, avaliações e recursos.

## 16. Entidades gravadas

Avaliação/versões futuras, notificação, recurso, ação, execução e decisão. Entidades versionáveis usam exclusivamente `src/dados/versoes.py`.

## 17. Dependências

S10, S12, S17, S21 e S23.

## 18. Fluxo principal

Validar → calcular/analisar → gerar minuta → chefia decide/notifica → recurso quando aplicável → nova versão.

## 19. Fluxos alternativos

Sem critério impede; conceito extremo sem justificativa bloqueia; recurso preserva avaliação original.

## 20. Erros e contingências

Contrato inválido é rejeitado; serviço indisponível não gera resultado inventado; falha transacional executa rollback; erro retorna código seguro e identificador da execução.

## 21. Privacidade e segurança

Dados individuais com acesso estrito; relatório coletivo agregado. Conteúdo restrito não é enviado a serviço externo.

## 22. Observabilidade e rastreabilidade

Registrar `execucao_id`, skill/versão, duração, estado, fontes/regras, entidades, alertas e erro. Logs não repetem segredo ou conteúdo sensível.

## 23. Casos de teste

S24-T01 critérios; T02 notificação; T03 prazos; T04 única; T05 sem critério; T06 evidência; T07 desenvolvimento; T08 comportamento; T09 ressalva; T10 integração. Acrescentar casos de contrato, autorização, dado ausente, falha externa e regressão.

## 24. Critérios de aceite

Decisão humana obrigatória, prazos exatos, original preservado e ressalva funcional; todos os casos críticos aprovados e aceite humano registrado.

## 25. Limites e itens fora da skill

Não substitui avaliação anual nem aplica punição automática.

## 26. Estado de desenvolvimento

Ficha v6 criada. Implementação, conjunto anotado, testes e validação institucional continuam pendentes.

## 27. Histórico de alterações

| Versão | Data | Alteração |
| --- | --- | --- |
| 0.1 | 23/08/2026 | Especificação operacional inicial da proposta v6 |

