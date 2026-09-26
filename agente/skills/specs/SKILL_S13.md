# S13 — Check-in de Execução e Monitoramento

**Versão:** 0.1 | **Estado:** especificada documentalmente; não implementada | **Onda:** 3 | **Gate:** G3

## 1. Identificação e versão

ID canônico `S13`. Mudança incompatível exige nova versão do contrato; o ID não é reutilizado.

## 2. Objetivo funcional

Registro de acompanhamento, alertas, perguntas e sugestões de ação, para check-in de execução e monitoramento de modo rastreável.

## 3. Usuários e permissões

Usuário principal: chefia e participante. Leitura, proposta e confirmação devem respeitar o papel e o contexto da unidade.

## 4. Momento de uso

Durante a execução, em rito leve e periódico.

## 5. Pré-condições

PE/PT pactuado, ator autorizado e período aberto.

## 6. Entradas

Plano, status, progresso, fatos, ocorrências, riscos e evidências. O contrato Pydantic definitivo será criado na implementação.

## 7. Saídas

Registro de acompanhamento, alertas, perguntas e sugestões de ação. A resposta também contém execução, status, fontes/regras, alertas, confiança aplicável e decisões/perguntas.

## 8. Regras negociais

Check-in não é avaliação; férias/evento planejado não é intercorrência; fato e opinião são separados. Regras ainda não validadas permanecem propostas.

## 9. Fontes

Fontes institucionais aprovadas em Q5, atos normativos vigentes e artefatos metodológicos identificados no índice. Trecho, versão e vigência acompanham a saída.

## 10. Cálculos determinísticos

Datas, progresso, pendências, prazos e vínculos. Devem alcançar 100% na bateria definida.

## 11. Uso permitido do LLM

Resumir relato e classificar ocorrência com confiança. O modelo não toma decisão humana nem altera cálculo.

## 12. Comportamento em ambiguidade

Baixa confiança, conflito ou falta de contexto produz alerta e pergunta pendente; não há preenchimento silencioso.

## 13. Perguntas pendentes

Registrar dado faltante, motivo, destinatário e item bloqueado. A execução pode ficar `aguardando_dados`.

## 14. Decisões humanas

A confirmação do usuário autorizado é persistida separadamente da sugestão automática, com justificativa quando exigida.

## 15. Entidades consultadas

PE/PT, riscos, evidências e acompanhamentos anteriores.

## 16. Entidades gravadas

Acompanhamento/execução futura, execucoes_skill, perguntas e decisões. Entidades versionáveis usam exclusivamente `src/dados/versoes.py`.

## 17. Dependências

S10, S11, S12 e S17.

## 18. Fluxo principal

Selecionar plano/período → registrar fatos/evidências → validar → sinalizar desvio → confirmar.

## 19. Fluxos alternativos

Mudança material chama S14; risco novo chama S10; conteúdo sensível é reduzido a categoria/impacto.

## 20. Erros e contingências

Contrato inválido é rejeitado; serviço indisponível não gera resultado inventado; falha transacional executa rollback; erro retorna código seguro e identificador da execução.

## 21. Privacidade e segurança

Não registrar detalhe de saúde ou juízo comportamental. Conteúdo restrito não é enviado a serviço externo.

## 22. Observabilidade e rastreabilidade

Registrar `execucao_id`, skill/versão, duração, estado, fontes/regras, entidades, alertas e erro. Logs não repetem segredo ou conteúdo sensível.

## 23. Casos de teste

S13-T01 regular; T02 desvio; T03 férias; T04 risco novo; T05 dado sensível; T06 sem evidência. Acrescentar casos de contrato, autorização, dado ausente, falha externa e regressão.

## 24. Critérios de aceite

Registro distingue fato, ocorrência, risco e ação; não emite avaliação; todos os casos críticos aprovados e aceite humano registrado.

## 25. Limites e itens fora da skill

Não altera plano nem atribui conceito.

## 26. Estado de desenvolvimento

Ficha v6 criada. Implementação, conjunto anotado, testes e validação institucional continuam pendentes.

## 27. Histórico de alterações

| Versão | Data | Alteração |
| --- | --- | --- |
| 0.1 | 23/08/2026 | Especificação operacional inicial da proposta v6 |

