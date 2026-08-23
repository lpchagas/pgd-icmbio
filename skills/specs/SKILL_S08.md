# S08 — Matriz de Cobertura das Entregas pela Equipe

**Versão:** 0.1 | **Estado:** especificada documentalmente; não implementada | **Onda:** 2 | **Gate:** G2

## 1. Identificação e versão

ID canônico `S08`. Mudança incompatível exige nova versão do contrato; o ID não é reutilizado.

## 2. Objetivo funcional

Matriz pessoa×entrega, lacunas, concentração e cenários, para matriz de cobertura das entregas pela equipe de modo rastreável.

## 3. Usuários e permissões

Usuário principal: chefia e equipe. Leitura, proposta e confirmação devem respeitar o papel e o contexto da unidade.

## 4. Momento de uso

Após capacidade e antes da pactuação do PT.

## 5. Pré-condições

S07 e entregas/metas disponíveis.

## 6. Entradas

Capacidade, entregas, competências e alocações propostas. O contrato Pydantic definitivo será criado na implementação.

## 7. Saídas

Matriz pessoa×entrega, lacunas, concentração e cenários. A resposta também contém execução, status, fontes/regras, alertas, confiança aplicável e decisões/perguntas.

## 8. Regras negociais

Alocação não excede CHD; entrega crítica precisa cobertura; evitar dependência única sem justificativa. Regras ainda não validadas permanecem propostas.

## 9. Fontes

Fontes institucionais aprovadas em Q5, atos normativos vigentes e artefatos metodológicos identificados no índice. Trecho, versão e vigência acompanham a saída.

## 10. Cálculos determinísticos

Somas, percentuais, cobertura, sobrecarga e concentração. Devem alcançar 100% na bateria definida.

## 11. Uso permitido do LLM

Sugerir combinações e explicar trade-offs. O modelo não toma decisão humana nem altera cálculo.

## 12. Comportamento em ambiguidade

Baixa confiança, conflito ou falta de contexto produz alerta e pergunta pendente; não há preenchimento silencioso.

## 13. Perguntas pendentes

Registrar dado faltante, motivo, destinatário e item bloqueado. A execução pode ficar `aguardando_dados`.

## 14. Decisões humanas

A confirmação do usuário autorizado é persistida separadamente da sugestão automática, com justificativa quando exigida.

## 15. Entidades consultadas

Planos_capacidade, participantes, alocações e entregas.

## 16. Entidades gravadas

Alocacoes, execucoes_skill, perguntas e decisões. Entidades versionáveis usam exclusivamente `src/dados/versoes.py`.

## 17. Dependências

S07, B03 e B04.

## 18. Fluxo principal

Cruzar capacidade/entregas → validar cobertura → sinalizar concentração → gerar cenários → pactuar.

## 19. Fluxos alternativos

Sem competência cria lacuna; sobrecarga exige ajuste; contribuição externa encaminha a S15.

## 20. Erros e contingências

Contrato inválido é rejeitado; serviço indisponível não gera resultado inventado; falha transacional executa rollback; erro retorna código seguro e identificador da execução.

## 21. Privacidade e segurança

Exibir nomes somente a atores autorizados; relatórios gerais agregados. Conteúdo restrito não é enviado a serviço externo.

## 22. Observabilidade e rastreabilidade

Registrar `execucao_id`, skill/versão, duração, estado, fontes/regras, entidades, alertas e erro. Logs não repetem segredo ou conteúdo sensível.

## 23. Casos de teste

S08-T01 cobertura plena; T02 lacuna; T03 sobrecarga; T04 pessoa única; T05 capacidade zero. Acrescentar casos de contrato, autorização, dado ausente, falha externa e regressão.

## 24. Critérios de aceite

Totais fecham, lacunas visíveis e decisão de alocação registrada; todos os casos críticos aprovados e aceite humano registrado.

## 25. Limites e itens fora da skill

Não cria PT e não avalia participante.

## 26. Estado de desenvolvimento

Ficha v6 criada. Implementação, conjunto anotado, testes e validação institucional continuam pendentes.

## 27. Histórico de alterações

| Versão | Data | Alteração |
| --- | --- | --- |
| 0.1 | 23/08/2026 | Especificação operacional inicial da proposta v6 |

