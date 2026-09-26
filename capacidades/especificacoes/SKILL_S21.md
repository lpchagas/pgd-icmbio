# S21 — Registro de Execução do Plano de Entregas da Unidade

**Versão:** 0.1 | **Estado:** especificada documentalmente; não implementada | **Onda:** 5 | **Gate:** G5

## 1. Identificação e versão

ID canônico `S21`. Mudança incompatível exige nova versão do contrato; o ID não é reutilizado.

## 2. Objetivo funcional

Registro versionado de execução, alcance, alertas, bloqueios e pedidos de ajuste, para registro de execução do plano de entregas da unidade de modo rastreável.

## 3. Usuários e permissões

Usuário principal: chefia da unidade de execução. Leitura, proposta e confirmação devem respeitar o papel e o contexto da unidade.

## 4. Momento de uso

Durante e no fechamento do período do PE.

## 5. Pré-condições

PE pactuado, metas/aceite, ator competente e calendário.

## 6. Entradas

PE, progresso realizado, evidências, ocorrências, fatores e solicitações de ajuste. O contrato Pydantic definitivo será criado na implementação.

## 7. Saídas

Registro versionado de execução, alcance, alertas, bloqueios e pedidos de ajuste. A resposta também contém execução, status, fontes/regras, alertas, confiança aplicável e decisões/perguntas.

## 8. Regras negociais

Progresso vem da meta, não da contagem de atividades; conclusão depende das condições dos PT; mudança chama S14. Regras ainda não validadas permanecem propostas.

## 9. Fontes

Fontes institucionais aprovadas em Q5, atos normativos vigentes e artefatos metodológicos identificados no índice. Trecho, versão e vigência acompanham a saída.

## 10. Cálculos determinísticos

Progresso × meta, totais, datas, completude e bloqueios. Devem alcançar 100% na bateria definida.

## 11. Uso permitido do LLM

Classificar ocorrência e resumir justificativa com confiança. O modelo não toma decisão humana nem altera cálculo.

## 12. Comportamento em ambiguidade

Baixa confiança, conflito ou falta de contexto produz alerta e pergunta pendente; não há preenchimento silencioso.

## 13. Perguntas pendentes

Registrar dado faltante, motivo, destinatário e item bloqueado. A execução pode ficar `aguardando_dados`.

## 14. Decisões humanas

A confirmação do usuário autorizado é persistida separadamente da sugestão automática, com justificativa quando exigida.

## 15. Entidades consultadas

S04/S05/S07/S08/S14/S17, PE e PTs relacionados.

## 16. Entidades gravadas

Execução/versões futuras, evidências/vínculos, execução da skill, perguntas e decisão. Entidades versionáveis usam exclusivamente `agente/dados/versoes.py`.

## 17. Dependências

S04, S05, S07, S08, S14 e S17.

## 18. Fluxo principal

Selecionar PE → registrar realizado/evidências → calcular → validar PTs/bloqueios → confirmar/versionar.

## 19. Fluxos alternativos

Caminho curto aceita meta/CHD manual identificada; fator externo separado; conflito retorna S02.

## 20. Erros e contingências

Contrato inválido é rejeitado; serviço indisponível não gera resultado inventado; falha transacional executa rollback; erro retorna código seguro e identificador da execução.

## 21. Privacidade e segurança

Não persistir detalhe clínico; dados da unidade agregados. Conteúdo restrito não é enviado a serviço externo.

## 22. Observabilidade e rastreabilidade

Registrar `execucao_id`, skill/versão, duração, estado, fontes/regras, entidades, alertas e erro. Logs não repetem segredo ou conteúdo sensível.

## 23. Casos de teste

S21-T01 progresso; T02 atividade não é progresso; T03 PT pendente; T04 ajuste; T05 evidência; T06 sensível; T07 prazo. Acrescentar casos de contrato, autorização, dado ausente, falha externa e regressão.

## 24. Critérios de aceite

Progresso exato, bloqueios aplicados, rastreio e decisão humana; todos os casos críticos aprovados e aceite humano registrado.

## 25. Limites e itens fora da skill

Não avalia o PE nem atribui conceito.

## 26. Estado de desenvolvimento

Ficha v6 criada. Implementação, conjunto anotado, testes e validação institucional continuam pendentes.

## 27. Histórico de alterações

| Versão | Data | Alteração |
| --- | --- | --- |
| 0.1 | 23/08/2026 | Especificação operacional inicial da proposta v6 |

