# S18 — Gerador de Relatório Gerencial do PGD

**Versão:** 0.1 | **Estado:** especificada documentalmente; não implementada | **Onda:** 4 | **Gate:** G4

## 1. Identificação e versão

ID canônico `S18`. Mudança incompatível exige nova versão do contrato; o ID não é reutilizado.

## 2. Objetivo funcional

Indicadores, tabelas, síntese, limitações e relatório exportável, para gerador de relatório gerencial do pgd de modo rastreável.

## 3. Usuários e permissões

Usuário principal: chefias e governança. Leitura, proposta e confirmação devem respeitar o papel e o contexto da unidade.

## 4. Momento de uso

Acompanhamento periódico e fechamento de ciclo.

## 5. Pré-condições

Dados consistentes, finalidade e público definidos.

## 6. Entradas

Planos, execução, riscos, avaliações, filtros e nível de agregação. O contrato Pydantic definitivo será criado na implementação.

## 7. Saídas

Indicadores, tabelas, síntese, limitações e relatório exportável. A resposta também contém execução, status, fontes/regras, alertas, confiança aplicável e decisões/perguntas.

## 8. Regras negociais

Sem ranking individual; separar fato e interpretação; explicar denominador/filtro; suprimir célula de risco. Regras ainda não validadas permanecem propostas.

## 9. Fontes

Fontes institucionais aprovadas em Q5, atos normativos vigentes e artefatos metodológicos identificados no índice. Trecho, versão e vigência acompanham a saída.

## 10. Cálculos determinísticos

Agregações, percentuais, períodos, supressão e reconciliação. Devem alcançar 100% na bateria definida.

## 11. Uso permitido do LLM

Redigir síntese e destacar padrões sem causalidade indevida. O modelo não toma decisão humana nem altera cálculo.

## 12. Comportamento em ambiguidade

Baixa confiança, conflito ou falta de contexto produz alerta e pergunta pendente; não há preenchimento silencioso.

## 13. Perguntas pendentes

Registrar dado faltante, motivo, destinatário e item bloqueado. A execução pode ficar `aguardando_dados`.

## 14. Decisões humanas

A confirmação do usuário autorizado é persistida separadamente da sugestão automática, com justificativa quando exigida.

## 15. Entidades consultadas

S06–S17, execuções, decisões e referências.

## 16. Entidades gravadas

Execução e artefato de relatório; metadados de publicação. Entidades versionáveis usam exclusivamente `src/dados/versoes.py`.

## 17. Dependências

S06, S07, S08, S10, S13, S15 e S16.

## 18. Fluxo principal

Definir público/filtros → validar dados → agregar → suprimir risco → redigir → revisar/publicar.

## 19. Fluxos alternativos

Base incompleta gera ressalva; grupo pequeno é suprimido; divergência fica em anexo.

## 20. Erros e contingências

Contrato inválido é rejeitado; serviço indisponível não gera resultado inventado; falha transacional executa rollback; erro retorna código seguro e identificador da execução.

## 21. Privacidade e segurança

Agregação por unidade e nenhuma exposição individual. Conteúdo restrito não é enviado a serviço externo.

## 22. Observabilidade e rastreabilidade

Registrar `execucao_id`, skill/versão, duração, estado, fontes/regras, entidades, alertas e erro. Logs não repetem segredo ou conteúdo sensível.

## 23. Casos de teste

S18-T01 agregado; T02 grupo pequeno; T03 filtro; T04 denominador; T05 dado divergente; T06 sem ranking. Acrescentar casos de contrato, autorização, dado ausente, falha externa e regressão.

## 24. Critérios de aceite

Números reproduzíveis, limitações claras e divulgação humana aprovada; todos os casos críticos aprovados e aceite humano registrado.

## 25. Limites e itens fora da skill

Não mede produtividade individual nem publica sem autorização.

## 26. Estado de desenvolvimento

Ficha v6 criada. Implementação, conjunto anotado, testes e validação institucional continuam pendentes.

## 27. Histórico de alterações

| Versão | Data | Alteração |
| --- | --- | --- |
| 0.1 | 23/08/2026 | Especificação operacional inicial da proposta v6 |

