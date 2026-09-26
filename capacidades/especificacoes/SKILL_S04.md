# S04 — Administrador do Catálogo de Entregas

**Versão:** 0.1 | **Estado:** especificada documentalmente; não implementada | **Onda:** 2 | **Gate:** G2

## 1. Identificação e versão

ID canônico `S04`. Mudança incompatível exige nova versão do contrato; o ID não é reutilizado.

## 2. Objetivo funcional

Entrega criada ou nova versão, código legível e histórico, para administrador do catálogo de entregas de modo rastreável.

## 3. Usuários e permissões

Usuário principal: chefia ou administrador de catálogo. Leitura, proposta e confirmação devem respeitar o papel e o contexto da unidade.

## 4. Momento de uso

Criação, reutilização, revisão ou desativação de entrega.

## 5. Pré-condições

S03 ou solicitação fundamentada e modelo comum disponível.

## 6. Entradas

Entrega candidata/existente, unidade, descrição, resultado e metadados. O contrato Pydantic definitivo será criado na implementação.

## 7. Saídas

Entrega criada ou nova versão, código legível e histórico. A resposta também contém execução, status, fontes/regras, alertas, confiança aplicável e decisões/perguntas.

## 8. Regras negociais

Reusar ID persistente; alteração cria versão; entrega é resultado observável; desativação é lógica. Regras ainda não validadas permanecem propostas.

## 9. Fontes

Fontes institucionais aprovadas em Q5, atos normativos vigentes e artefatos metodológicos identificados no índice. Trecho, versão e vigência acompanham a saída.

## 10. Cálculos determinísticos

UUID/código, versão, campos, unicidade e transação. Devem alcançar 100% na bateria definida.

## 11. Uso permitido do LLM

Melhorar título/descrição e detectar similaridade, sem fundir automaticamente. O modelo não toma decisão humana nem altera cálculo.

## 12. Comportamento em ambiguidade

Baixa confiança, conflito ou falta de contexto produz alerta e pergunta pendente; não há preenchimento silencioso.

## 13. Perguntas pendentes

Registrar dado faltante, motivo, destinatário e item bloqueado. A execução pode ficar `aguardando_dados`.

## 14. Decisões humanas

A confirmação do usuário autorizado é persistida separadamente da sugestão automática, com justificativa quando exigida.

## 15. Entidades consultadas

Candidatas, entregas/versões, competências e decisões.

## 16. Entidades gravadas

Entregas, entregas_versoes, execucoes_skill e decisões. Entidades versionáveis usam exclusivamente `agente/dados/versoes.py`.

## 17. Dependências

S01, S03 e serviço de versões.

## 18. Fluxo principal

Buscar similar → validar estrutura → propor criar/reusar/versionar → confirmar → persistir via versoes.py.

## 19. Fluxos alternativos

Similaridade alta pede escolha; erro de versão interrompe; desativação preserva histórico.

## 20. Erros e contingências

Contrato inválido é rejeitado; serviço indisponível não gera resultado inventado; falha transacional executa rollback; erro retorna código seguro e identificador da execução.

## 21. Privacidade e segurança

Catálogo não contém nome de participante nem informação pessoal. Conteúdo restrito não é enviado a serviço externo.

## 22. Observabilidade e rastreabilidade

Registrar `execucao_id`, skill/versão, duração, estado, fontes/regras, entidades, alertas e erro. Logs não repetem segredo ou conteúdo sensível.

## 23. Casos de teste

S04-T01 criar; T02 versionar; T03 reutilizar; T04 concorrência; T05 desativar; T06 rollback. Acrescentar casos de contrato, autorização, dado ausente, falha externa e regressão.

## 24. Critérios de aceite

Identidade e histórico íntegros, sem INSERT/UPDATE manual em versão; todos os casos críticos aprovados e aceite humano registrado.

## 25. Limites e itens fora da skill

Não define meta ou capacidade.

## 26. Estado de desenvolvimento

Ficha v6 criada. Implementação, conjunto anotado, testes e validação institucional continuam pendentes.

## 27. Histórico de alterações

| Versão | Data | Alteração |
| --- | --- | --- |
| 0.1 | 23/08/2026 | Especificação operacional inicial da proposta v6 |

