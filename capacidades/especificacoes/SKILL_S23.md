# S23 — Registro de Execução do Plano de Trabalho do Participante

**Versão:** 0.1 | **Estado:** especificada documentalmente; não implementada | **Onda:** 5 | **Gate:** G5

## 1. Identificação e versão

ID canônico `S23`. Mudança incompatível exige nova versão do contrato; o ID não é reutilizado.

## 2. Objetivo funcional

Registro versionado de execução do PT, totais, alertas e pendências, para registro de execução do plano de trabalho do participante de modo rastreável.

## 3. Usuários e permissões

Usuário principal: participante. Leitura, proposta e confirmação devem respeitar o papel e o contexto da unidade.

## 4. Momento de uso

Durante e até o prazo de registro do PT.

## 5. Pré-condições

PT pactuado, participante autenticado e período válido.

## 6. Entradas

PT, contribuições realizadas, horas, evidências, ocorrências e ajustes. O contrato Pydantic definitivo será criado na implementação.

## 7. Saídas

Registro versionado de execução do PT, totais, alertas e pendências. A resposta também contém execução, status, fontes/regras, alertas, confiança aplicável e decisões/perguntas.

## 8. Regras negociais

Separar ocorrência de evento planejado; respeitar CHD; contribuição vinculada ao PE; saúde só como categoria/impacto. Regras ainda não validadas permanecem propostas.

## 9. Fontes

Fontes institucionais aprovadas em Q5, atos normativos vigentes e artefatos metodológicos identificados no índice. Trecho, versão e vigência acompanham a saída.

## 10. Cálculos determinísticos

Horas, totais, datas, limites e vínculos. Devem alcançar 100% na bateria definida.

## 11. Uso permitido do LLM

Classificar ocorrência e resumir contribuição. O modelo não toma decisão humana nem altera cálculo.

## 12. Comportamento em ambiguidade

Baixa confiança, conflito ou falta de contexto produz alerta e pergunta pendente; não há preenchimento silencioso.

## 13. Perguntas pendentes

Registrar dado faltante, motivo, destinatário e item bloqueado. A execução pode ficar `aguardando_dados`.

## 14. Decisões humanas

A confirmação do usuário autorizado é persistida separadamente da sugestão automática, com justificativa quando exigida.

## 15. Entidades consultadas

S12/S14/S17/S21, PT e PE.

## 16. Entidades gravadas

Execução/versões futuras, evidências/vínculos, execução da skill, perguntas e decisão. Entidades versionáveis usam exclusivamente `agente/dados/versoes.py`.

## 17. Dependências

S12, S14, S17 e S21.

## 18. Fluxo principal

Selecionar PT → registrar contribuições/horas/evidências → validar → classificar ocorrência → confirmar.

## 19. Fluxos alternativos

Férias não é intercorrência; contribuição externa chama S15; mudança material chama S14.

## 20. Erros e contingências

Contrato inválido é rejeitado; serviço indisponível não gera resultado inventado; falha transacional executa rollback; erro retorna código seguro e identificador da execução.

## 21. Privacidade e segurança

Não persistir diagnóstico; restringir registro nominal. Conteúdo restrito não é enviado a serviço externo.

## 22. Observabilidade e rastreabilidade

Registrar `execucao_id`, skill/versão, duração, estado, fontes/regras, entidades, alertas e erro. Logs não repetem segredo ou conteúdo sensível.

## 23. Casos de teste

S23-T01 registro; T02 férias; T03 CHD; T04 excesso; T05 prazo; T06 saúde; T07 vínculo PE. Acrescentar casos de contrato, autorização, dado ausente, falha externa e regressão.

## 24. Critérios de aceite

Horas exatas, ocorrência correta, evidência e histórico íntegros; todos os casos críticos aprovados e aceite humano registrado.

## 25. Limites e itens fora da skill

Não atribui conceito nem altera PE/PT pactuado.

## 26. Estado de desenvolvimento

Ficha v6 criada. Implementação, conjunto anotado, testes e validação institucional continuam pendentes.

## 27. Histórico de alterações

| Versão | Data | Alteração |
| --- | --- | --- |
| 0.1 | 23/08/2026 | Especificação operacional inicial da proposta v6 |

