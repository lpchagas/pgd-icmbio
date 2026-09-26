# S09 — Designer e Auditor de Encadeamento OKR-D

**Versão:** 0.1 | **Estado:** especificada documentalmente; não implementada | **Onda:** 1 | **Gate:** G1

## 1. Identificação e versão

ID canônico `S09`. Mudança incompatível exige nova versão do contrato; o ID não é reutilizado.

## 2. Objetivo funcional

Vínculos N:N, achados de alinhamento e perguntas, para designer e auditor de encadeamento okr-d de modo rastreável.

## 3. Usuários e permissões

Usuário principal: chefia e área de estratégia. Leitura, proposta e confirmação devem respeitar o papel e o contexto da unidade.

## 4. Momento de uso

Desenho e revisão do alinhamento estratégico.

## 5. Pré-condições

Objetivos oficiais e entregas identificadas.

## 6. Entradas

Objetivos, resultados-chave, entregas e justificativas. O contrato Pydantic definitivo será criado na implementação.

## 7. Saídas

Vínculos N:N, achados de alinhamento e perguntas. A resposta também contém execução, status, fontes/regras, alertas, confiança aplicável e decisões/perguntas.

## 8. Regras negociais

Não inventar objetivo; vínculo exige justificativa; entrega pode contribuir para vários objetivos. Regras ainda não validadas permanecem propostas.

## 9. Fontes

Fontes institucionais aprovadas em Q5, atos normativos vigentes e artefatos metodológicos identificados no índice. Trecho, versão e vigência acompanham a saída.

## 10. Cálculos determinísticos

IDs, vigência, cardinalidade e completude. Devem alcançar 100% na bateria definida.

## 11. Uso permitido do LLM

Avaliar coerência do vínculo e melhorar justificativa. O modelo não toma decisão humana nem altera cálculo.

## 12. Comportamento em ambiguidade

Baixa confiança, conflito ou falta de contexto produz alerta e pergunta pendente; não há preenchimento silencioso.

## 13. Perguntas pendentes

Registrar dado faltante, motivo, destinatário e item bloqueado. A execução pode ficar `aguardando_dados`.

## 14. Decisões humanas

A confirmação do usuário autorizado é persistida separadamente da sugestão automática, com justificativa quando exigida.

## 15. Entidades consultadas

Fontes, objetivos, resultados, entregas e vínculos.

## 16. Entidades gravadas

Okrd_objetivos, okrd_resultados_chave, vinculos_okrd, execução e decisão. Entidades versionáveis usam exclusivamente `src/dados/versoes.py`.

## 17. Dependências

S01, B01 e B02.

## 18. Fluxo principal

Selecionar objetivos → propor vínculo → justificar → auditar coerência → confirmar/persistir.

## 19. Fluxos alternativos

Objetivo local não se passa por nacional; vínculo fraco fica como recomendação.

## 20. Erros e contingências

Contrato inválido é rejeitado; serviço indisponível não gera resultado inventado; falha transacional executa rollback; erro retorna código seguro e identificador da execução.

## 21. Privacidade e segurança

Sem dado individual; usar estruturas organizacionais. Conteúdo restrito não é enviado a serviço externo.

## 22. Observabilidade e rastreabilidade

Registrar `execucao_id`, skill/versão, duração, estado, fontes/regras, entidades, alertas e erro. Logs não repetem segredo ou conteúdo sensível.

## 23. Casos de teste

S09-T01 vínculo forte; T02 múltiplos; T03 objetivo inexistente; T04 justificativa circular. Acrescentar casos de contrato, autorização, dado ausente, falha externa e regressão.

## 24. Critérios de aceite

Todo vínculo tem IDs persistentes, fonte e justificativa confirmada; todos os casos críticos aprovados e aceite humano registrado.

## 25. Limites e itens fora da skill

Não redefine a estratégia institucional.

## 26. Estado de desenvolvimento

Ficha v6 criada. Implementação, conjunto anotado, testes e validação institucional continuam pendentes.

## 27. Histórico de alterações

| Versão | Data | Alteração |
| --- | --- | --- |
| 0.1 | 23/08/2026 | Especificação operacional inicial da proposta v6 |

