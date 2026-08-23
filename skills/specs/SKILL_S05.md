# S05 — Designer de Metas, Indicadores e Critérios de Aceite

**Versão:** 0.1 | **Estado:** especificada documentalmente; não implementada | **Onda:** 1 | **Gate:** G1

## 1. Identificação e versão

ID canônico `S05`. Mudança incompatível exige nova versão do contrato; o ID não é reutilizado.

## 2. Objetivo funcional

Meta, indicador, fórmula, critério de aceite e perguntas, para designer de metas, indicadores e critérios de aceite de modo rastreável.

## 3. Usuários e permissões

Usuário principal: chefia e equipe que pactuam a entrega. Leitura, proposta e confirmação devem respeitar o papel e o contexto da unidade.

## 4. Momento de uso

Antes de pactuar PE ou revisar uma entrega.

## 5. Pré-condições

Entrega identificada e período/contexto conhecidos.

## 6. Entradas

Entrega, resultado esperado, unidade de medida, baseline, prazo e evidência. O contrato Pydantic definitivo será criado na implementação.

## 7. Saídas

Meta, indicador, fórmula, critério de aceite e perguntas. A resposta também contém execução, status, fontes/regras, alertas, confiança aplicável e decisões/perguntas.

## 8. Regras negociais

Meta mensurável e compatível com entrega; critério observável; distinguir quantidade, qualidade e prazo. Regras ainda não validadas permanecem propostas.

## 9. Fontes

Fontes institucionais aprovadas em Q5, atos normativos vigentes e artefatos metodológicos identificados no índice. Trecho, versão e vigência acompanham a saída.

## 10. Cálculos determinísticos

Unidades, fórmulas, intervalos, datas e consistência entre meta e critério. Devem alcançar 100% na bateria definida.

## 11. Uso permitido do LLM

Propor redação e opções de indicador/aceite. O modelo não toma decisão humana nem altera cálculo.

## 12. Comportamento em ambiguidade

Baixa confiança, conflito ou falta de contexto produz alerta e pergunta pendente; não há preenchimento silencioso.

## 13. Perguntas pendentes

Registrar dado faltante, motivo, destinatário e item bloqueado. A execução pode ficar `aguardando_dados`.

## 14. Decisões humanas

A confirmação do usuário autorizado é persistida separadamente da sugestão automática, com justificativa quando exigida.

## 15. Entidades consultadas

Entrega/versão, regras e exemplos.

## 16. Entidades gravadas

Nova versão da entrega, execucoes_skill, perguntas e decisão. Entidades versionáveis usam exclusivamente `src/dados/versoes.py`.

## 17. Dependências

S01, B01 e B03.

## 18. Fluxo principal

Analisar entrega → identificar resultado → propor métricas → validar cálculo/evidência → pactuar → versionar.

## 19. Fluxos alternativos

Sem baseline apresenta opções; meta qualitativa exige rubrica; indicador inviável vira pendência.

## 20. Erros e contingências

Contrato inválido é rejeitado; serviço indisponível não gera resultado inventado; falha transacional executa rollback; erro retorna código seguro e identificador da execução.

## 21. Privacidade e segurança

Métrica de equipe não deve expor pessoa sem necessidade. Conteúdo restrito não é enviado a serviço externo.

## 22. Observabilidade e rastreabilidade

Registrar `execucao_id`, skill/versão, duração, estado, fontes/regras, entidades, alertas e erro. Logs não repetem segredo ou conteúdo sensível.

## 23. Casos de teste

S05-T01 quantitativa; T02 qualitativa; T03 sem baseline; T04 fórmula inválida; T05 critério circular. Acrescentar casos de contrato, autorização, dado ausente, falha externa e regressão.

## 24. Critérios de aceite

Meta, indicador, fórmula, fonte de evidência e aceite são coerentes e confirmados; todos os casos críticos aprovados e aceite humano registrado.

## 25. Limites e itens fora da skill

Não calcula capacidade nem avalia execução.

## 26. Estado de desenvolvimento

Ficha v6 criada. Implementação, conjunto anotado, testes e validação institucional continuam pendentes.

## 27. Histórico de alterações

| Versão | Data | Alteração |
| --- | --- | --- |
| 0.1 | 23/08/2026 | Especificação operacional inicial da proposta v6 |

