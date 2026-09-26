# S03 — Extrator de Competências e Responsabilidades em Entregas

**Versão:** 0.1 | **Estado:** especificada documentalmente; não implementada | **Onda:** 1 | **Gate:** G1

## 1. Identificação e versão

ID canônico `S03`. Mudança incompatível exige nova versão do contrato; o ID não é reutilizado.

## 2. Objetivo funcional

Competências estruturadas, responsabilidades e entregas candidatas com proveniência, para extrator de competências e responsabilidades em entregas de modo rastreável.

## 3. Usuários e permissões

Usuário principal: chefia e analista de processos. Leitura, proposta e confirmação devem respeitar o papel e o contexto da unidade.

## 4. Momento de uso

Formação ou revisão do catálogo da unidade.

## 5. Pré-condições

Fontes regimentais e de cadeia de valor cadastradas.

## 6. Entradas

Competências, processos, responsabilidades e contexto da unidade. O contrato Pydantic definitivo será criado na implementação.

## 7. Saídas

Competências estruturadas, responsabilidades e entregas candidatas com proveniência. A resposta também contém execução, status, fontes/regras, alertas, confiança aplicável e decisões/perguntas.

## 8. Regras negociais

Entrega descreve resultado, não tarefa; não inventar competência; manter trecho de origem e unidade. Regras ainda não validadas permanecem propostas.

## 9. Fontes

Fontes institucionais aprovadas em Q5, atos normativos vigentes e artefatos metodológicos identificados no índice. Trecho, versão e vigência acompanham a saída.

## 10. Cálculos determinísticos

Campos obrigatórios, IDs, deduplicação exata e vínculos. Devem alcançar 100% na bateria definida.

## 11. Uso permitido do LLM

Identificar verbos, objetos, beneficiários e resultados potenciais. O modelo não toma decisão humana nem altera cálculo.

## 12. Comportamento em ambiguidade

Baixa confiança, conflito ou falta de contexto produz alerta e pergunta pendente; não há preenchimento silencioso.

## 13. Perguntas pendentes

Registrar dado faltante, motivo, destinatário e item bloqueado. A execução pode ficar `aguardando_dados`.

## 14. Decisões humanas

A confirmação do usuário autorizado é persistida separadamente da sugestão automática, com justificativa quando exigida.

## 15. Entidades consultadas

Fontes/regras S01 e ref_unidades.

## 16. Entidades gravadas

Entregas_candidatas, execucoes_skill, perguntas_pendentes e decisões. Entidades versionáveis usam exclusivamente `src/dados/versoes.py`.

## 17. Dependências

S01 e B01.

## 18. Fluxo principal

Selecionar fonte/unidade → extrair competências → propor candidatas → agrupar similares → revisão humana.

## 19. Fluxos alternativos

Competência ambígua vira pergunta; sobreposição fica como candidatos vinculados, sem fusão automática.

## 20. Erros e contingências

Contrato inválido é rejeitado; serviço indisponível não gera resultado inventado; falha transacional executa rollback; erro retorna código seguro e identificador da execução.

## 21. Privacidade e segurança

Não extrair nomes de ocupantes; trabalhar com unidade/função. Conteúdo restrito não é enviado a serviço externo.

## 22. Observabilidade e rastreabilidade

Registrar `execucao_id`, skill/versão, duração, estado, fontes/regras, entidades, alertas e erro. Logs não repetem segredo ou conteúdo sensível.

## 23. Casos de teste

S03-T01 competência clara; T02 tarefa disfarçada; T03 ambiguidade; T04 duplicidade; T05 unidade errada. Acrescentar casos de contrato, autorização, dado ausente, falha externa e regressão.

## 24. Critérios de aceite

Cada candidata tem competência, fonte, justificativa e decisão de manter/ajustar/rejeitar; todos os casos críticos aprovados e aceite humano registrado.

## 25. Limites e itens fora da skill

Não cria entrega oficial sem S04 e decisão humana.

## 26. Estado de desenvolvimento

Ficha v6 criada. Implementação, conjunto anotado, testes e validação institucional continuam pendentes.

## 27. Histórico de alterações

| Versão | Data | Alteração |
| --- | --- | --- |
| 0.1 | 23/08/2026 | Especificação operacional inicial da proposta v6 |

