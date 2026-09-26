# S12 — Assistente de Pactuação do Plano de Trabalho

**Versão:** 0.1 | **Estado:** especificada documentalmente; não implementada | **Onda:** 3 | **Gate:** G3

## 1. Identificação e versão

ID canônico `S12`. Mudança incompatível exige nova versão do contrato; o ID não é reutilizado.

## 2. Objetivo funcional

Minuta de PT, compatibilidade de carga, pendências e versão pactuada, para assistente de pactuação do plano de trabalho de modo rastreável.

## 3. Usuários e permissões

Usuário principal: chefia e participante. Leitura, proposta e confirmação devem respeitar o papel e o contexto da unidade.

## 4. Momento de uso

Antes do período de execução do PT.

## 5. Pré-condições

PE vigente, participante autorizado e capacidade disponível.

## 6. Entradas

PE, participante, período, contribuições, CHD, regime e critérios. O contrato Pydantic definitivo será criado na implementação.

## 7. Saídas

Minuta de PT, compatibilidade de carga, pendências e versão pactuada. A resposta também contém execução, status, fontes/regras, alertas, confiança aplicável e decisões/perguntas.

## 8. Regras negociais

PT deriva do PE; contribuições cabem na CHD; pactuação é humana; regime/modalidade respeita regra vigente. Regras ainda não validadas permanecem propostas.

## 9. Fontes

Fontes institucionais aprovadas em Q5, atos normativos vigentes e artefatos metodológicos identificados no índice. Trecho, versão e vigência acompanham a saída.

## 10. Cálculos determinísticos

CHD, somas, período, vínculos e campos obrigatórios. Devem alcançar 100% na bateria definida.

## 11. Uso permitido do LLM

Redigir contribuição e critérios de acompanhamento. O modelo não toma decisão humana nem altera cálculo.

## 12. Comportamento em ambiguidade

Baixa confiança, conflito ou falta de contexto produz alerta e pergunta pendente; não há preenchimento silencioso.

## 13. Perguntas pendentes

Registrar dado faltante, motivo, destinatário e item bloqueado. A execução pode ficar `aguardando_dados`.

## 14. Decisões humanas

A confirmação do usuário autorizado é persistida separadamente da sugestão automática, com justificativa quando exigida.

## 15. Entidades consultadas

PE, S07/S08, participante, regras e entregas.

## 16. Entidades gravadas

Entidade/versões futuras de PT, alocações, execução, perguntas e decisões. Entidades versionáveis usam exclusivamente `src/dados/versoes.py`.

## 17. Dependências

S07, S08 e S11.

## 18. Fluxo principal

Identificar PE/pessoa → propor contribuições → validar CHD/regras → negociar → pactuar/versionar.

## 19. Fluxos alternativos

Chefia dispensada sem PT segue Q20; contribuição externa encaminha S15; excesso exige replanejar.

## 20. Erros e contingências

Contrato inválido é rejeitado; serviço indisponível não gera resultado inventado; falha transacional executa rollback; erro retorna código seguro e identificador da execução.

## 21. Privacidade e segurança

Acesso nominal restrito; relatórios posteriores agregados. Conteúdo restrito não é enviado a serviço externo.

## 22. Observabilidade e rastreabilidade

Registrar `execucao_id`, skill/versão, duração, estado, fontes/regras, entidades, alertas e erro. Logs não repetem segredo ou conteúdo sensível.

## 23. Casos de teste

S12-T01 completo; T02 excesso CHD; T03 sem vínculo PE; T04 dispensado; T05 contribuição externa. Acrescentar casos de contrato, autorização, dado ausente, falha externa e regressão.

## 24. Critérios de aceite

PT vinculado ao PE, carga exata, critérios claros e decisão registrada; todos os casos críticos aprovados e aceite humano registrado.

## 25. Limites e itens fora da skill

Não avalia participante nem registra execução.

## 26. Estado de desenvolvimento

Ficha v6 criada. Implementação, conjunto anotado, testes e validação institucional continuam pendentes.

## 27. Histórico de alterações

| Versão | Data | Alteração |
| --- | --- | --- |
| 0.1 | 23/08/2026 | Especificação operacional inicial da proposta v6 |
