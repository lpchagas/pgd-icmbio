# S15 — Gestor de Contribuições Interunidades

**Versão:** 0.1 | **Estado:** especificada documentalmente; não implementada | **Onda:** 4 | **Gate:** G4

## 1. Identificação e versão

ID canônico `S15`. Mudança incompatível exige nova versão do contrato; o ID não é reutilizado.

## 2. Objetivo funcional

Vínculo de contribuição, impacto de capacidade, pendências e acordos, para gestor de contribuições interunidades de modo rastreável.

## 3. Usuários e permissões

Usuário principal: chefias cedente/beneficiária e participante. Leitura, proposta e confirmação devem respeitar o papel e o contexto da unidade.

## 4. Momento de uso

Pactuação ou ajuste de contribuição entre unidades.

## 5. Pré-condições

Unidades, PE/PT e capacidade identificados.

## 6. Entradas

Demanda, unidades, entrega, participante, carga, período e responsabilidades. O contrato Pydantic definitivo será criado na implementação.

## 7. Saídas

Vínculo de contribuição, impacto de capacidade, pendências e acordos. A resposta também contém execução, status, fontes/regras, alertas, confiança aplicável e decisões/perguntas.

## 8. Regras negociais

Definir unidade dona da entrega, responsável por acompanhamento e efeito na CHD; evitar dupla contagem. Regras ainda não validadas permanecem propostas.

## 9. Fontes

Fontes institucionais aprovadas em Q5, atos normativos vigentes e artefatos metodológicos identificados no índice. Trecho, versão e vigência acompanham a saída.

## 10. Cálculos determinísticos

Carga, período, IDs, sobreposição e totais. Devem alcançar 100% na bateria definida.

## 11. Uso permitido do LLM

Redigir responsabilidades e justificativa. O modelo não toma decisão humana nem altera cálculo.

## 12. Comportamento em ambiguidade

Baixa confiança, conflito ou falta de contexto produz alerta e pergunta pendente; não há preenchimento silencioso.

## 13. Perguntas pendentes

Registrar dado faltante, motivo, destinatário e item bloqueado. A execução pode ficar `aguardando_dados`.

## 14. Decisões humanas

A confirmação do usuário autorizado é persistida separadamente da sugestão automática, com justificativa quando exigida.

## 15. Entidades consultadas

PE/PT, alocações, unidades, regras e decisões.

## 16. Entidades gravadas

Contribuições futuras, alocações, execução e decisões. Entidades versionáveis usam exclusivamente `agente/dados/versoes.py`.

## 17. Dependências

S08, S12 e S14.

## 18. Fluxo principal

Identificar demanda/atores → calcular impacto → propor acordo → colher decisões → vincular planos.

## 19. Fluxos alternativos

Sem acordo fica pendente; time volante segue regra específica; sobrecarga retorna S08/S14.

## 20. Erros e contingências

Contrato inválido é rejeitado; serviço indisponível não gera resultado inventado; falha transacional executa rollback; erro retorna código seguro e identificador da execução.

## 21. Privacidade e segurança

Acesso nominal limitado às chefias/participante; agregação em relatórios. Conteúdo restrito não é enviado a serviço externo.

## 22. Observabilidade e rastreabilidade

Registrar `execucao_id`, skill/versão, duração, estado, fontes/regras, entidades, alertas e erro. Logs não repetem segredo ou conteúdo sensível.

## 23. Casos de teste

S15-T01 acordo; T02 dupla contagem; T03 sobrecarga; T04 unidades divergentes; T05 encerramento. Acrescentar casos de contrato, autorização, dado ausente, falha externa e regressão.

## 24. Critérios de aceite

Propriedade, carga, acompanhamento e vínculo estão inequívocos; todos os casos críticos aprovados e aceite humano registrado.

## 25. Limites e itens fora da skill

Não transfere lotação nem decide competência administrativa.

## 26. Estado de desenvolvimento

Ficha v6 criada. Implementação, conjunto anotado, testes e validação institucional continuam pendentes.

## 27. Histórico de alterações

| Versão | Data | Alteração |
| --- | --- | --- |
| 0.1 | 23/08/2026 | Especificação operacional inicial da proposta v6 |

