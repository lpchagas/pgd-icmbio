# S02 — Verificador Normativo e de Conformidade

**Versão:** 0.1 | **Estado:** especificada documentalmente; não implementada | **Onda:** 1 | **Gate:** G1

## 1. Identificação e versão

ID canônico `S02`. Mudança incompatível exige nova versão do contrato; o ID não é reutilizado.

## 2. Objetivo funcional

Achados classificados, regras/fontes, conflitos, severidade e perguntas, para verificador normativo e de conformidade de modo rastreável.

## 3. Usuários e permissões

Usuário principal: analista, chefia ou skill consumidora. Leitura, proposta e confirmação devem respeitar o papel e o contexto da unidade.

## 4. Momento de uso

Antes da pactuação, alteração, execução ou avaliação.

## 5. Pré-condições

S01 disponível e objeto a verificar identificado.

## 6. Entradas

Objeto, contexto institucional, data de referência e conjunto de verificações. O contrato Pydantic definitivo será criado na implementação.

## 7. Saídas

Achados classificados, regras/fontes, conflitos, severidade e perguntas. A resposta também contém execução, status, fontes/regras, alertas, confiança aplicável e decisões/perguntas.

## 8. Regras negociais

Aplicar somente regra vigente e compatível; diferenciar obrigação, recomendação e exemplo; não resolver conflito. Regras ainda não validadas permanecem propostas.

## 9. Fontes

Fontes institucionais aprovadas em Q5, atos normativos vigentes e artefatos metodológicos identificados no índice. Trecho, versão e vigência acompanham a saída.

## 10. Cálculos determinísticos

Completude, datas, precedência conhecida, enums e invariantes estruturais. Devem alcançar 100% na bateria definida.

## 11. Uso permitido do LLM

Localizar correspondência entre objeto e regra e explicar o achado. O modelo não toma decisão humana nem altera cálculo.

## 12. Comportamento em ambiguidade

Baixa confiança, conflito ou falta de contexto produz alerta e pergunta pendente; não há preenchimento silencioso.

## 13. Perguntas pendentes

Registrar dado faltante, motivo, destinatário e item bloqueado. A execução pode ficar `aguardando_dados`.

## 14. Decisões humanas

A confirmação do usuário autorizado é persistida separadamente da sugestão automática, com justificativa quando exigida.

## 15. Entidades consultadas

Fontes, regras/versões, conflitos e entidade analisada.

## 16. Entidades gravadas

Execucoes_skill, perguntas_pendentes e decisoes_humanas quando confirmadas. Entidades versionáveis usam exclusivamente `agente/dados/versoes.py`.

## 17. Dependências

S01 e base metodológica B01/B03/B04.

## 18. Fluxo principal

Validar objeto/data → selecionar regras → executar controles → classificar achados → citar fontes → pedir decisões.

## 19. Fluxos alternativos

Sem regra aplicável gera insuficiência; conflito bloqueia conclusão; recomendação nunca vira não conformidade normativa.

## 20. Erros e contingências

Contrato inválido é rejeitado; serviço indisponível não gera resultado inventado; falha transacional executa rollback; erro retorna código seguro e identificador da execução.

## 21. Privacidade e segurança

Usar apenas campos necessários e ocultar dados individuais em relatórios. Conteúdo restrito não é enviado a serviço externo.

## 22. Observabilidade e rastreabilidade

Registrar `execucao_id`, skill/versão, duração, estado, fontes/regras, entidades, alertas e erro. Logs não repetem segredo ou conteúdo sensível.

## 23. Casos de teste

S02-T01 conforme; T02 não conforme; T03 recomendação; T04 regra expirada; T05 conflito; T06 dado ausente. Acrescentar casos de contrato, autorização, dado ausente, falha externa e regressão.

## 24. Critérios de aceite

Todo achado possui regra, natureza, fonte, severidade e ação humana quando necessária; todos os casos críticos aprovados e aceite humano registrado.

## 25. Limites e itens fora da skill

Não homologa plano nem emite parecer jurídico.

## 26. Estado de desenvolvimento

Ficha v6 criada. Implementação, conjunto anotado, testes e validação institucional continuam pendentes.

## 27. Histórico de alterações

| Versão | Data | Alteração |
| --- | --- | --- |
| 0.1 | 23/08/2026 | Especificação operacional inicial da proposta v6 |

