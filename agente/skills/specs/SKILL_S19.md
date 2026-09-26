# S19 — Analisador de Aprendizado entre Ciclos

**Versão:** 0.1 | **Estado:** especificada documentalmente; não implementada | **Onda:** 4 | **Gate:** G4

## 1. Identificação e versão

ID canônico `S19`. Mudança incompatível exige nova versão do contrato; o ID não é reutilizado.

## 2. Objetivo funcional

Padrões, hipóteses, recomendações, incerteza e limitações, para analisador de aprendizado entre ciclos de modo rastreável.

## 3. Usuários e permissões

Usuário principal: governança e chefias. Leitura, proposta e confirmação devem respeitar o papel e o contexto da unidade.

## 4. Momento de uso

Após múltiplos ciclos comparáveis.

## 5. Pré-condições

Histórico mínimo, qualidade e comparabilidade avaliados.

## 6. Entradas

Séries de planos, execução, riscos, avaliações, mudanças e contexto. O contrato Pydantic definitivo será criado na implementação.

## 7. Saídas

Padrões, hipóteses, recomendações, incerteza e limitações. A resposta também contém execução, status, fontes/regras, alertas, confiança aplicável e decisões/perguntas.

## 8. Regras negociais

Não inferir causalidade sem desenho; amostra insuficiente bloqueia conclusão; mudança normativa segmenta série. Regras ainda não validadas permanecem propostas.

## 9. Fontes

Fontes institucionais aprovadas em Q5, atos normativos vigentes e artefatos metodológicos identificados no índice. Trecho, versão e vigência acompanham a saída.

## 10. Cálculos determinísticos

Tamanho amostral, tendência, dispersão, intervalos e comparabilidade. Devem alcançar 100% na bateria definida.

## 11. Uso permitido do LLM

Formular hipóteses e recomendações explicáveis. O modelo não toma decisão humana nem altera cálculo.

## 12. Comportamento em ambiguidade

Baixa confiança, conflito ou falta de contexto produz alerta e pergunta pendente; não há preenchimento silencioso.

## 13. Perguntas pendentes

Registrar dado faltante, motivo, destinatário e item bloqueado. A execução pode ficar `aguardando_dados`.

## 14. Decisões humanas

A confirmação do usuário autorizado é persistida separadamente da sugestão automática, com justificativa quando exigida.

## 15. Entidades consultadas

S14, S16, S18, histórico e metadados.

## 16. Entidades gravadas

Análise, execução, perguntas e decisões. Entidades versionáveis usam exclusivamente `src/dados/versoes.py`.

## 17. Dependências

S14, S16, S18 e dados históricos suficientes.

## 18. Fluxo principal

Avaliar qualidade → definir coortes → calcular → interpretar → revisar hipóteses → decidir ação.

## 19. Fluxos alternativos

Sem histórico usa sintético apenas para teste; quebra de série segmenta; outlier é sinalizado.

## 20. Erros e contingências

Contrato inválido é rejeitado; serviço indisponível não gera resultado inventado; falha transacional executa rollback; erro retorna código seguro e identificador da execução.

## 21. Privacidade e segurança

Usar dados agregados/pseudonimizados; proibir ranking. Conteúdo restrito não é enviado a serviço externo.

## 22. Observabilidade e rastreabilidade

Registrar `execucao_id`, skill/versão, duração, estado, fontes/regras, entidades, alertas e erro. Logs não repetem segredo ou conteúdo sensível.

## 23. Casos de teste

S19-T01 tendência; T02 amostra pequena; T03 quebra normativa; T04 outlier; T05 correlação espúria. Acrescentar casos de contrato, autorização, dado ausente, falha externa e regressão.

## 24. Critérios de aceite

Método, amostra, incerteza e limite explícitos; recomendação revisada; todos os casos críticos aprovados e aceite humano registrado.

## 25. Limites e itens fora da skill

Não prevê desempenho individual nem estabelece causalidade.

## 26. Estado de desenvolvimento

Ficha v6 criada. Implementação, conjunto anotado, testes e validação institucional continuam pendentes.

## 27. Histórico de alterações

| Versão | Data | Alteração |
| --- | --- | --- |
| 0.1 | 23/08/2026 | Especificação operacional inicial da proposta v6 |

