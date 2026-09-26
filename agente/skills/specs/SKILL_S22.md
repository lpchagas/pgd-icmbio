# S22 — Avaliação do Plano de Entregas da Unidade

**Versão:** 0.1 | **Estado:** especificada documentalmente; não implementada | **Onda:** 5 | **Gate:** G5

## 1. Identificação e versão

ID canônico `S22`. Mudança incompatível exige nova versão do contrato; o ID não é reutilizado.

## 2. Objetivo funcional

Cálculo, análise, parecer, conceito proposto, ressalvas e decisão requerida, para avaliação do plano de entregas da unidade de modo rastreável.

## 3. Usuários e permissões

Usuário principal: chefia hierarquicamente superior. Leitura, proposta e confirmação devem respeitar o papel e o contexto da unidade.

## 4. Momento de uso

Após encerramento do PE, no prazo configurado.

## 5. Pré-condições

S21 concluída, critérios/evidências e competência validados.

## 6. Entradas

PE, execução, metas, critérios, evidências, riscos, fatores externos e avaliador. O contrato Pydantic definitivo será criado na implementação.

## 7. Saídas

Cálculo, análise, parecer, conceito proposto, ressalvas e decisão requerida. A resposta também contém execução, status, fontes/regras, alertas, confiança aplicável e decisões/perguntas.

## 8. Regras negociais

Competência e dispensas; quatro questionamentos; escala de cinco; fatores externos separados; avaliação humana obrigatória. Regras ainda não validadas permanecem propostas.

## 9. Fontes

Fontes institucionais aprovadas em Q5, atos normativos vigentes e artefatos metodológicos identificados no índice. Trecho, versão e vigência acompanham a saída.

## 10. Cálculos determinísticos

Prazo, competência conhecida, alcance/faixa e completude. Devem alcançar 100% na bateria definida.

## 11. Uso permitido do LLM

Fundamentar parecer sem induzir decisão. O modelo não toma decisão humana nem altera cálculo.

## 12. Comportamento em ambiguidade

Baixa confiança, conflito ou falta de contexto produz alerta e pergunta pendente; não há preenchimento silencioso.

## 13. Perguntas pendentes

Registrar dado faltante, motivo, destinatário e item bloqueado. A execução pode ficar `aguardando_dados`.

## 14. Decisões humanas

A confirmação do usuário autorizado é persistida separadamente da sugestão automática, com justificativa quando exigida.

## 15. Entidades consultadas

S05/S10/S16/S17/S21, regras e ref_unidades.

## 16. Entidades gravadas

Avaliação/versões futuras, execução, perguntas e decisão. Entidades versionáveis usam exclusivamente `src/dados/versoes.py`.

## 17. Dependências

S10, S16, S17 e S21.

## 18. Fluxo principal

Validar competência/prazo → calcular → analisar evidências/fatores → gerar minuta → chefia decide → persistir.

## 19. Fluxos alternativos

Sem critério impede; divergência pede decisão; faixa institucional é rotulada como tal.

## 20. Erros e contingências

Contrato inválido é rejeitado; serviço indisponível não gera resultado inventado; falha transacional executa rollback; erro retorna código seguro e identificador da execução.

## 21. Privacidade e segurança

Avaliar unidade/PE; não expor dados individuais. Conteúdo restrito não é enviado a serviço externo.

## 22. Observabilidade e rastreabilidade

Registrar `execucao_id`, skill/versão, duração, estado, fontes/regras, entidades, alertas e erro. Logs não repetem segredo ou conteúdo sensível.

## 23. Casos de teste

S22-T01 competência; T02 questionamentos; T03 fator; T04 faixa; T05 escala; T06 prazo; T07 regra institucional; T08 decisão. Acrescentar casos de contrato, autorização, dado ausente, falha externa e regressão.

## 24. Critérios de aceite

Nenhum conceito sem decisão humana, parecer cita regras e ressalvas; todos os casos críticos aprovados e aceite humano registrado.

## 25. Limites e itens fora da skill

Não substitui avaliação de desempenho e não oferece recurso de PT indevidamente.

## 26. Estado de desenvolvimento

Ficha v6 criada. Implementação, conjunto anotado, testes e validação institucional continuam pendentes.

## 27. Histórico de alterações

| Versão | Data | Alteração |
| --- | --- | --- |
| 0.1 | 23/08/2026 | Especificação operacional inicial da proposta v6 |

