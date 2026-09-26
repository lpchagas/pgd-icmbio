# S07 — Planejador de Capacidade da Unidade

**Versão:** 0.1 | **Estado:** especificada documentalmente; não implementada | **Onda:** 2 | **Gate:** G2

## 1. Identificação e versão

ID canônico `S07`. Mudança incompatível exige nova versão do contrato; o ID não é reutilizado.

## 2. Objetivo funcional

CHD individual pseudonimizada, capacidade agregada, demanda e cenários, para planejador de capacidade da unidade de modo rastreável.

## 3. Usuários e permissões

Usuário principal: chefia da unidade. Leitura, proposta e confirmação devem respeitar o papel e o contexto da unidade.

## 4. Momento de uso

Planejamento do período e replanejamento.

## 5. Pré-condições

Período, participantes e indisponibilidades mínimas disponíveis.

## 6. Entradas

Participantes, jornadas, período, feriados, ausências e demanda. O contrato Pydantic definitivo será criado na implementação.

## 7. Saídas

CHD individual pseudonimizada, capacidade agregada, demanda e cenários. A resposta também contém execução, status, fontes/regras, alertas, confiança aplicável e decisões/perguntas.

## 8. Regras negociais

Usar calendário configurado; ausência não é intercorrência; não detalhar motivo sensível. Regras ainda não validadas permanecem propostas.

## 9. Fontes

Fontes institucionais aprovadas em Q5, atos normativos vigentes e artefatos metodológicos identificados no índice. Trecho, versão e vigência acompanham a saída.

## 10. Cálculos determinísticos

Dias úteis, jornada, indisponibilidade, soma, percentual e cenários. Devem alcançar 100% na bateria definida.

## 11. Uso permitido do LLM

Explicar gargalos e opções sem alterar números. O modelo não toma decisão humana nem altera cálculo.

## 12. Comportamento em ambiguidade

Baixa confiança, conflito ou falta de contexto produz alerta e pergunta pendente; não há preenchimento silencioso.

## 13. Perguntas pendentes

Registrar dado faltante, motivo, destinatário e item bloqueado. A execução pode ficar `aguardando_dados`.

## 14. Decisões humanas

A confirmação do usuário autorizado é persistida separadamente da sugestão automática, com justificativa quando exigida.

## 15. Entidades consultadas

Ref_usuarios, participantes, indisponibilidades, regras e entregas.

## 16. Entidades gravadas

Planos_capacidade, participantes, indisponibilidades, alocacoes, execução e decisão. Entidades versionáveis usam exclusivamente `agente/dados/versoes.py`.

## 17. Dependências

S05, B03/B04 e referências.

## 18. Fluxo principal

Validar período/pessoas → calcular CHD → comparar demanda → gerar cenários → escolha humana.

## 19. Fluxos alternativos

Dado ausente cria faixa e pergunta; calendário indefinido bloqueia prazo exato.

## 20. Erros e contingências

Contrato inválido é rejeitado; serviço indisponível não gera resultado inventado; falha transacional executa rollback; erro retorna código seguro e identificador da execução.

## 21. Privacidade e segurança

Pseudônimos em análise; nunca persistir diagnóstico ou motivo clínico. Conteúdo restrito não é enviado a serviço externo.

## 22. Observabilidade e rastreabilidade

Registrar `execucao_id`, skill/versão, duração, estado, fontes/regras, entidades, alertas e erro. Logs não repetem segredo ou conteúdo sensível.

## 23. Casos de teste

S07-T01 período normal; T02 férias; T03 parcial; T04 feriado; T05 ausência de jornada; T06 soma. Acrescentar casos de contrato, autorização, dado ausente, falha externa e regressão.

## 24. Critérios de aceite

100% de exatidão na bateria e cenário escolhido registrado; todos os casos críticos aprovados e aceite humano registrado.

## 25. Limites e itens fora da skill

Não decide prioridade ou alocação final.

## 26. Estado de desenvolvimento

Ficha v6 criada. Implementação, conjunto anotado, testes e validação institucional continuam pendentes.

## 27. Histórico de alterações

| Versão | Data | Alteração |
| --- | --- | --- |
| 0.1 | 23/08/2026 | Especificação operacional inicial da proposta v6 |

