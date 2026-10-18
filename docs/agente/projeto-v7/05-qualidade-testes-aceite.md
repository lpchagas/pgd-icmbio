# 05 — Qualidade, testes e aceite

## 1. Princípio

Qualidade é evidência reproduzível, não impressão. Uma skill pode estar implementada e
ainda não estar aprovada. Regras de negócio são aceitas por pessoas competentes; código
é aceito por testes; a onda exige ambos.

## 2. Ciclo de vida de uma skill

| Passo | Responsabilidade | Artefato | Critério de saída |
| ---: | --- | --- | --- |
| 1. Especificar | produto/analista | entrada em `capacidades/catalogo.yaml` (ficha gerada) | objetivo, entradas, saídas e limites claros |
| 2. Formalizar regras | analista | RN, fonte e vigência | conflito e autoridade identificados |
| 3. Anotar exemplos | analista/usuário | conjunto de exemplos; casos `teste_ia` da ficha | cobertura de situações típicas e críticas |
| 4. Desenhar testes | analista+desenvolvedor | casos identificados | esperado verificável |
| 5. Implementar | desenvolvedor | código e migração quando necessária | revisão e testes unitários |
| 6. Integrar | desenvolvedor | ferramenta no servidor MCP, ponta a ponta | contrato, classe do dado, persistência e falhas validados |
| 7. Aceitar | negócio+técnica | registro em `docs/testes/` (pasta planejada) | critérios e pendências registrados |

Os casos sintéticos de cada ficha (`teste_ia`) servem também para testar a especificação
em outras ferramentas de IA antes do código, pelo roteiro de
[`capacidades/fichas/COMO_TESTAR.md`](../../../capacidades/fichas/COMO_TESTAR.md). Esse
teste mede a clareza da ficha; não substitui os passos 4 a 7.

## 3. Definição de pronto

Uma skill só recebe estado `aprovada` se:

1. ficha completa e versionada;
2. regras com fonte, natureza e vigência;
3. conflitos e lacunas explícitos;
4. contratos de entrada e saída validados, com a classe do dado;
5. exemplos anotados suficientes ao risco;
6. testes positivos, negativos e limítrofes aprovados;
7. cálculos determinísticos com 100% de exatidão;
8. persistência apenas pelos serviços permitidos;
9. execução rastreável;
10. decisão humana separada;
11. revisão de segurança e privacidade, inclusive do gate de classe;
12. documentação de uso, erro e recuperação;
13. aceite da onda registrado por pessoa responsável.

## 4. Pirâmide de testes

| Tipo | Objetivo | Exemplo | Execução |
| --- | --- | --- | --- |
| Unidade | validar função isolada | cálculo de CHD, prazo ou faixa | toda alteração |
| Contrato | validar schema e fronteira | campo ausente, enum inválido, classe ausente | toda versão |
| Persistência | garantir histórico | v1→v2 sem sobrescrita | toda entidade versionável |
| Integração | validar componentes | S05→S07→S08 pelo servidor MCP | por fluxo |
| RAG | validar recuperação/citação | pergunta com fonte conhecida | por corpus/modelo |
| Indicador | validar a ferramenta | valor servido igual ao A2 certificado (DEN-01) | por versão e por ciclo mensal |
| Segurança/LGPD | impedir exposição | conteúdo institucional pedido por cliente externo é recusado | toda alteração do gate e por gate |
| Aceitação | validar utilidade negocial | caso completo anotado | fim de onda |
| Regressão | evitar quebra anterior | S01–S24 | integração e release |
| Recuperação | restaurar serviço/dados | dump → restauração na instância isolada | fundação e estabilização |

## 5. Ambiente de testes

- A suíte do repositório roda offline, sem Denodo nem MySQL, no computador e no CI
  (`.venv/bin/python -m pytest tests -q -p no:cacheprovider`).
- Testes contra MySQL são opt-in (`-m mysql`, `PGD_MYSQL_TESTE=1`) e usam só a instância
  isolada; a instância principal é recusada.
- Testes do agente que precisarem de indicador usam A2 de fixture; o teste DEN-01 compara
  com o CSV oficial em execução real.
- O gerador do catálogo é verificado na suíte: ficha ou tabela editada à mão falha.

## 6. Identificação de testes

Formato: `Sxx-Tnn`. Testes transversais usam `INT-nn`, `SEC-nn`, `RAG-nn`, `DEN-nn` e
`REC-nn`. Cada registro informa versão da skill, dados, resultado esperado, resultado
obtido, evidência, executor, data e conclusão.

## 7. Casos mínimos por skill

| Categoria | Caso obrigatório |
| --- | --- |
| Positivo | entrada completa e resultado esperado |
| Ausência | campo necessário ausente gera pergunta |
| Limite | zero, máximo, virada de período ou faixa |
| Conflito | fontes ou dados incompatíveis |
| Autorização | ator sem competência não conclui decisão |
| Persistência | nova versão e histórico íntegro |
| Segurança | texto pessoal/sensível não vaza; classe acima do permitido é recusada |
| Falha externa | Denodo, A2, modelo ou arquivo indisponível |

## 8. Métricas

| Métrica | Meta inicial | Observação |
| --- | ---: | --- |
| Cálculos determinísticos | 100% | nenhuma tolerância para fórmula conhecida |
| Contratos válidos | 100% | entradas inválidas são rejeitadas |
| Indicador servido igual ao A2 | 100% | qualquer diferença bloqueia |
| Citações corretas | ≥ 95% no conjunto aprovado | medir fonte e sustentação |
| Cobertura de casos críticos | 100% | privacidade, autoridade e histórico |
| Defeitos críticos abertos no gate | 0 | bloqueia avanço |
| Perda de versão | 0 | bloqueia release |
| Conteúdo não público entregue a cliente externo | 0 | interrompe fluxo e exige resposta |
| Macro-F1 semântico | registrar baseline por classificador | meta definida após conjunto anotado |

## 9. Avaliação de RAG

O conjunto de avaliação registra pergunta, resposta esperada, fontes aceitas, trechos
relevantes e alertas. Avaliam-se recuperação, fidelidade, completude, citação, recusa e
tratamento de conflito. Uma resposta fluente sem suporte é falha. A avaliação é repetida
com o modelo local, porque a qualidade de redação muda com o modelo.

## 10. Avaliação semântica

Classificadores de competência, entrega, risco, ocorrência ou evidência usam exemplos
anotados, divisão treino/teste quando aplicável, matriz de confusão e revisão dos falsos
positivos/negativos. A confiança acompanha a saída; baixa confiança gera revisão humana.

## 11. Dados de teste

- público: permitido;
- sintético: padrão para automação e para testes com cliente externo;
- institucional comum: somente local e autorizado, com o modelo local;
- pessoal real: evitar; se indispensável, minimizar/pseudonimizar e registrar base legal;
- `99_restrito`: excluído dos testes, do RAG e do repositório.

## 12. Gates

| Gate | Testes mínimos |
| --- | --- |
| G0 | contrato comum, erro, persistência, backup, fluxo mínimo, DEN-01 e SEC do gate de classe |
| G1 | fonte, citação, conflito, S01/S02, privacidade de corpus e SEC |
| G2 | cálculos de capacidade, versões, portfólio, integração e SEC |
| G3 | PE/PT, pactuação, alteração, histórico e SEC |
| G4 | agregação, suficiência estatística, ausência de ranking e SEC |
| G5 | prazos, competência, avaliação, recurso, decisão humana e SEC |
| G6 | regressão, segurança, desempenho, restauração e piloto |

## 13. Aceite conjunto

O registro de aceite contém: escopo, versões, casos executados, defeitos, riscos residuais,
pendências humanas, restrições de uso e decisão `aprovar`, `aprovar com restrição` ou
`não aprovar`. Uma pendência documental nunca é ocultada para obter aprovação.

## 14. Piloto

O piloto só usa unidades e pessoas autorizadas. Mede utilidade, tempo, erros, perguntas,
intervenções humanas, compreensão das fontes e confiança. Não mede produtividade
individual nem cria ranking. Incidente crítico suspende o caso afetado.

## 15. Checklist de release documental/técnico

- [ ] versão e changelog;
- [ ] contratos sincronizados;
- [ ] migrações e estado real conferidos;
- [ ] suíte completa verde e testes registrados;
- [ ] catálogo em sincronia (`python -m tools.gerar_catalogo_capacidades verificar`);
- [ ] links válidos (`python -m tools.verificar_links`);
- [ ] `detect-secrets` nos arquivos alterados;
- [ ] backup/restauração quando aplicável;
- [ ] riscos e questões atualizados;
- [ ] antes de push: auditoria de segurança com status `completo_sem_ocorrencia` e commits
  de saída identificados.
