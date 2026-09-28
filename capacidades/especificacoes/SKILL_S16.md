# S16 — Avaliador de Entregas

**Versão:** 0.1 | **Estado:** especificada documentalmente; não implementada | **Onda:** 4 | **Gate:** G4

## 1. Identificação e versão

ID canônico `S16`. Mudança incompatível exige nova versão do contrato; o ID não é reutilizado.

## 2. Objetivo funcional

Análise intermediária fundamentada, sem efeito de avaliação final, para avaliador de entregas de modo rastreável.

## 3. Usuários e permissões

Usuário principal: chefia responsável pelo acompanhamento. Leitura, proposta e confirmação devem respeitar o papel e o contexto da unidade.

## 4. Momento de uso

Análise intermediária de uma entrega.

## 5. Pré-condições

Entrega, critérios pactuados e evidências disponíveis.

## 6. Entradas

Meta, realizado, critérios, evidências, riscos e fatores externos. O contrato Pydantic definitivo será criado na implementação.

## 7. Saídas

Análise intermediária fundamentada, sem efeito de avaliação final. A resposta também contém execução, status, fontes/regras, alertas, confiança aplicável e decisões/perguntas.

## 8. Regras negociais

Subordinada a S22; não confundir com avaliação do PE; separar fatores externos; critério pactuado é obrigatório. Regras ainda não validadas permanecem propostas.

## 9. Fontes

Fontes institucionais aprovadas em Q5, atos normativos vigentes e artefatos metodológicos identificados no índice. Trecho, versão e vigência acompanham a saída.

## 10. Cálculos determinísticos

Realizado × meta, faixa e completude. Devem alcançar 100% na bateria definida.

## 11. Uso permitido do LLM

Fundamentar análise e organizar evidências. O modelo não toma decisão humana nem altera cálculo.

## 12. Comportamento em ambiguidade

Baixa confiança, conflito ou falta de contexto produz alerta e pergunta pendente; não há preenchimento silencioso.

## 13. Perguntas pendentes

Registrar dado faltante, motivo, destinatário e item bloqueado. A execução pode ficar `aguardando_dados`.

## 14. Decisões humanas

A confirmação do usuário autorizado é persistida separadamente da sugestão automática, com justificativa quando exigida.

## 15. Entidades consultadas

Entregas, critérios, check-ins, riscos e evidências.

## 16. Entidades gravadas

Análise intermediária futura, execução, perguntas e decisão. Entidades versionáveis usam exclusivamente `agente/dados/versoes.py`.

## 17. Dependências

S05, S13, S14 e S17.

## 18. Fluxo principal

Validar critério → calcular alcance → revisar evidências/fatores → propor análise → decisão humana.

## 19. Fluxos alternativos

Sem critério impede conclusão; evidência insuficiente pede complemento; conflito retorna S02.

## 20. Erros e contingências

Contrato inválido é rejeitado; serviço indisponível não gera resultado inventado; falha transacional executa rollback; erro retorna código seguro e identificador da execução.

## 21. Privacidade e segurança

Avaliar resultado da entrega, não comportamento individual. Conteúdo restrito não é enviado a serviço externo.

## 22. Observabilidade e rastreabilidade

Registrar `execucao_id`, skill/versão, duração, estado, fontes/regras, entidades, alertas e erro. Logs não repetem segredo ou conteúdo sensível.

## 23. Casos de teste

S16-T01 alcançada; T02 parcial; T03 sem critério; T04 fator externo; T05 evidência conflitante. Acrescentar casos de contrato, autorização, dado ausente, falha externa e regressão.

## 24. Critérios de aceite

Cálculo correto, fundamentação rastreável e rótulo explícito de análise intermediária; todos os casos críticos aprovados e aceite humano registrado.

## 25. Limites e itens fora da skill

Não substitui S22 nem emite conceito final.

## 26. Estado de desenvolvimento

Ficha v6 criada. Implementação, conjunto anotado, testes e validação institucional continuam pendentes.

## 27. Histórico de alterações

| Versão | Data | Alteração |
| --- | --- | --- |
| 0.1 | 23/08/2026 | Especificação operacional inicial da proposta v6 |

