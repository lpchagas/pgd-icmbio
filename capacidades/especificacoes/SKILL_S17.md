# S17 — Organizador de Evidências

**Versão:** 0.1 | **Estado:** especificada documentalmente; não implementada | **Onda:** 1 | **Gate:** G1

## 1. Identificação e versão

ID canônico `S17`. Mudança incompatível exige nova versão do contrato; o ID não é reutilizado.

## 2. Objetivo funcional

Evidência catalogada, hash, tipo, vínculo, classe e alertas, para organizador de evidências de modo rastreável.

## 3. Usuários e permissões

Usuário principal: participante, chefia e skills consumidoras. Leitura, proposta e confirmação devem respeitar o papel e o contexto da unidade.

## 4. Momento de uso

Pactuação, execução, monitoramento ou avaliação.

## 5. Pré-condições

Entidade de destino identificada e acesso permitido.

## 6. Entradas

Arquivo, link, registro, metadados, autoria funcional, período e vínculo. O contrato Pydantic definitivo será criado na implementação.

## 7. Saídas

Evidência catalogada, hash, tipo, vínculo, classe e alertas. A resposta também contém execução, status, fontes/regras, alertas, confiança aplicável e decisões/perguntas.

## 8. Regras negociais

Evidência não prova automaticamente resultado; preservar proveniência; evitar duplicata; acesso acompanha classe. Regras ainda não validadas permanecem propostas.

## 9. Fontes

Fontes institucionais aprovadas em Q5, atos normativos vigentes e artefatos metodológicos identificados no índice. Trecho, versão e vigência acompanham a saída.

## 10. Cálculos determinísticos

Hash, tipo, tamanho, data, integridade e duplicidade. Devem alcançar 100% na bateria definida.

## 11. Uso permitido do LLM

Classificar tipo e pertinência com confiança. O modelo não toma decisão humana nem altera cálculo.

## 12. Comportamento em ambiguidade

Baixa confiança, conflito ou falta de contexto produz alerta e pergunta pendente; não há preenchimento silencioso.

## 13. Perguntas pendentes

Registrar dado faltante, motivo, destinatário e item bloqueado. A execução pode ficar `aguardando_dados`.

## 14. Decisões humanas

A confirmação do usuário autorizado é persistida separadamente da sugestão automática, com justificativa quando exigida.

## 15. Entidades consultadas

Entidades relacionadas, evidências existentes e regras de acesso.

## 16. Entidades gravadas

Evidencias futuras, vínculos, execução, perguntas e decisão. Entidades versionáveis usam exclusivamente `agente/dados/versoes.py`.

## 17. Dependências

S01, S05 e armazenamento local.

## 18. Fluxo principal

Receber → classificar acesso → calcular hash → vincular → avaliar pertinência → confirmar.

## 19. Fluxos alternativos

Link indisponível gera alerta; duplicata reutiliza ID; sensível é recusada/minimizada.

## 20. Erros e contingências

Contrato inválido é rejeitado; serviço indisponível não gera resultado inventado; falha transacional executa rollback; erro retorna código seguro e identificador da execução.

## 21. Privacidade e segurança

Não copiar conteúdo desnecessário; 99_restrito fica segregado. Conteúdo restrito não é enviado a serviço externo.

## 22. Observabilidade e rastreabilidade

Registrar `execucao_id`, skill/versão, duração, estado, fontes/regras, entidades, alertas e erro. Logs não repetem segredo ou conteúdo sensível.

## 23. Casos de teste

S17-T01 arquivo; T02 link; T03 duplicata; T04 sem vínculo; T05 restrita; T06 hash alterado. Acrescentar casos de contrato, autorização, dado ausente, falha externa e regressão.

## 24. Critérios de aceite

Origem, integridade, classe e vínculo recuperáveis; nenhuma aprovação automática; todos os casos críticos aprovados e aceite humano registrado.

## 25. Limites e itens fora da skill

Não decide se a meta foi cumprida.

## 26. Estado de desenvolvimento

Ficha v6 criada. Implementação, conjunto anotado, testes e validação institucional continuam pendentes.

## 27. Histórico de alterações

| Versão | Data | Alteração |
| --- | --- | --- |
| 0.1 | 23/08/2026 | Especificação operacional inicial da proposta v6 |

