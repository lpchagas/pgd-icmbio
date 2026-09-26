# S20 — Importador, Exportador e Integrador de Planos

**Versão:** 0.1 | **Estado:** especificada documentalmente; não implementada | **Onda:** 2 | **Gate:** G2

## 1. Identificação e versão

ID canônico `S20`. Mudança incompatível exige nova versão do contrato; o ID não é reutilizado.

## 2. Objetivo funcional

Prévia, erros, divergências, importação versionada ou exportação, para importador, exportador e integrador de planos de modo rastreável.

## 3. Usuários e permissões

Usuário principal: administrador técnico/negocial. Leitura, proposta e confirmação devem respeitar o papel e o contexto da unidade.

## 4. Momento de uso

Carga, intercâmbio, conciliação ou portabilidade.

## 5. Pré-condições

Schema de origem/destino e autorização definidos.

## 6. Entradas

Arquivo/contrato, mapeamento, versão, unidade, modo de validação. O contrato Pydantic definitivo será criado na implementação.

## 7. Saídas

Prévia, erros, divergências, importação versionada ou exportação. A resposta também contém execução, status, fontes/regras, alertas, confiança aplicável e decisões/perguntas.

## 8. Regras negociais

Validar antes de gravar; nunca sobrescrever; IDs preservados quando confiáveis; conflito exige decisão. Regras ainda não validadas permanecem propostas.

## 9. Fontes

Fontes institucionais aprovadas em Q5, atos normativos vigentes e artefatos metodológicos identificados no índice. Trecho, versão e vigência acompanham a saída.

## 10. Cálculos determinísticos

Schema, tipos, enums, datas, totais, hashes e reconciliação. Devem alcançar 100% na bateria definida.

## 11. Uso permitido do LLM

Sugerir mapeamento de campos e explicar divergência. O modelo não toma decisão humana nem altera cálculo.

## 12. Comportamento em ambiguidade

Baixa confiança, conflito ou falta de contexto produz alerta e pergunta pendente; não há preenchimento silencioso.

## 13. Perguntas pendentes

Registrar dado faltante, motivo, destinatário e item bloqueado. A execução pode ficar `aguardando_dados`.

## 14. Decisões humanas

A confirmação do usuário autorizado é persistida separadamente da sugestão automática, com justificativa quando exigida.

## 15. Entidades consultadas

Fontes, regras, modelo comum, entidades e referências.

## 16. Entidades gravadas

Entidades via serviços, execuções, perguntas e decisões. Entidades versionáveis usam exclusivamente `src/dados/versoes.py`.

## 17. Dependências

S01, S02 e modelo comum.

## 18. Fluxo principal

Identificar formato → validar/mapear → simular → apresentar divergências → confirmar → importar/exportar.

## 19. Fluxos alternativos

Campo desconhecido fica pendente; arquivo inválido é rejeitado; dry-run não grava.

## 20. Erros e contingências

Contrato inválido é rejeitado; serviço indisponível não gera resultado inventado; falha transacional executa rollback; erro retorna código seguro e identificador da execução.

## 21. Privacidade e segurança

Exportar somente campos autorizados; mascarar/pseudonimizar quando necessário. Conteúdo restrito não é enviado a serviço externo.

## 22. Observabilidade e rastreabilidade

Registrar `execucao_id`, skill/versão, duração, estado, fontes/regras, entidades, alertas e erro. Logs não repetem segredo ou conteúdo sensível.

## 23. Casos de teste

S20-T01 importação; T02 dry-run; T03 schema inválido; T04 conflito ID; T05 exportação mínima; T06 rollback. Acrescentar casos de contrato, autorização, dado ausente, falha externa e regressão.

## 24. Critérios de aceite

Reconciliação completa, histórico preservado e nenhuma escrita não confirmada; todos os casos críticos aprovados e aceite humano registrado.

## 25. Limites e itens fora da skill

Não escreve no PETRVS e não substitui governança de integração.

## 26. Estado de desenvolvimento

Ficha v6 criada. Implementação, conjunto anotado, testes e validação institucional continuam pendentes.

## 27. Histórico de alterações

| Versão | Data | Alteração |
| --- | --- | --- |
| 0.1 | 23/08/2026 | Especificação operacional inicial da proposta v6 |

