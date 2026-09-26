# 05 — Qualidade, testes e aceite

## 1. Princípio

Qualidade é evidência reproduzível, não impressão. Uma skill pode estar implementada e
ainda não estar aprovada. Regras de negócio são aceitas por pessoas competentes; código
é aceito por testes; a onda exige ambos.

## 2. Ciclo de vida de uma skill

| Passo | Responsabilidade | Artefato | Critério de saída |
| ---: | --- | --- | --- |
| 1. Especificar | produto/analista | ficha `SKILL_Sxx.md` | objetivo, entradas, saídas e limites claros |
| 2. Formalizar regras | analista | RN, fonte e vigência | conflito e autoridade identificados |
| 3. Anotar exemplos | analista/usuário | conjunto de exemplos | cobertura de situações típicas e críticas |
| 4. Desenhar testes | analista+desenvolvedor | casos identificados | esperado verificável |
| 5. Implementar | desenvolvedor | código e migração quando necessária | revisão e testes unitários |
| 6. Integrar | desenvolvedor | fluxo ponta a ponta | contrato, persistência e falhas validados |
| 7. Aceitar | negócio+técnica | registro em `docs/testes/` | critérios e pendências registrados |

## 3. Definição de pronto

Uma skill só recebe estado `aprovada` se:

1. ficha completa e versionada;
2. regras com fonte, natureza e vigência;
3. conflitos e lacunas explícitos;
4. contratos de entrada e saída validados;
5. exemplos anotados suficientes ao risco;
6. testes positivos, negativos e limítrofes aprovados;
7. cálculos determinísticos com 100% de exatidão;
8. persistência apenas pelos serviços permitidos;
9. execução rastreável;
10. decisão humana separada;
11. revisão de segurança e privacidade;
12. documentação de uso, erro e recuperação;
13. aceite da onda registrado por pessoa responsável.

## 4. Pirâmide de testes

| Tipo | Objetivo | Exemplo | Execução |
| --- | --- | --- | --- |
| Unidade | validar função isolada | cálculo de CHD, prazo ou faixa | toda alteração |
| Contrato | validar schema e fronteira | campo ausente, enum inválido | toda versão |
| Persistência | garantir histórico | v1→v2 sem sobrescrita | toda entidade versionável |
| Integração | validar componentes | S05→S07→S08 | por fluxo |
| RAG | validar recuperação/citação | pergunta com fonte conhecida | por corpus/modelo |
| Denodo | validar consulta real | indicador contra CSV oficial | quando rota disponível |
| Segurança/LGPD | impedir exposição | conteúdo de saúde/restrito | por gate |
| Aceitação | validar utilidade negocial | caso completo anotado | fim de onda |
| Regressão | evitar quebra anterior | S01–S24 | integração e release |
| Recuperação | restaurar serviço/dados | dump→restore | fundação e estabilização |

## 5. Identificação de testes

Formato: `Sxx-Tnn`. Testes transversais usam `INT-nn`, `SEC-nn`, `RAG-nn`, `DEN-nn` e
`REC-nn`. Cada registro informa versão da skill, dados, resultado esperado, resultado
obtido, evidência, executor, data e conclusão.

## 6. Casos mínimos por skill

| Categoria | Caso obrigatório |
| --- | --- |
| Positivo | entrada completa e resultado esperado |
| Ausência | campo necessário ausente gera pergunta |
| Limite | zero, máximo, virada de período ou faixa |
| Conflito | fontes ou dados incompatíveis |
| Autorização | ator sem competência não conclui decisão |
| Persistência | nova versão e histórico íntegro |
| Segurança | texto pessoal/sensível não vaza |
| Falha externa | Denodo/modelo/arquivo indisponível |

## 7. Métricas

| Métrica | Meta inicial | Observação |
| --- | ---: | --- |
| Cálculos determinísticos | 100% | nenhuma tolerância para fórmula conhecida |
| Contratos válidos | 100% | entradas inválidas são rejeitadas |
| Citações corretas | ≥ 95% no conjunto aprovado | medir fonte e sustentação |
| Cobertura de casos críticos | 100% | privacidade, autoridade e histórico |
| Defeitos críticos abertos no gate | 0 | bloqueia avanço |
| Perda de versão | 0 | bloqueia release |
| Incidente de conteúdo restrito externo | 0 | interrompe fluxo e exige resposta |
| Macro-F1 semântico | registrar baseline por classificador | meta definida após conjunto anotado |

## 8. Avaliação de RAG

O conjunto de avaliação registra pergunta, resposta esperada, fontes aceitas, trechos
relevantes e alertas. Avaliam-se recuperação, fidelidade, completude, citação, recusa e
tratamento de conflito. Uma resposta fluente sem suporte é falha.

## 9. Avaliação semântica

Classificadores de competência, entrega, risco, ocorrência ou evidência usam exemplos
anotados, divisão treino/teste quando aplicável, matriz de confusão e revisão dos falsos
positivos/negativos. A confiança acompanha a saída; baixa confiança gera revisão humana.

## 10. Dados de teste

- público: permitido;
- sintético: padrão para automação;
- institucional comum: somente local e autorizado;
- pessoal real: evitar; se indispensável, minimizar/pseudonimizar e registrar base legal;
- `99_restrito`: excluído dos testes externos e do repositório.

## 11. Gates

| Gate | Testes mínimos |
| --- | --- |
| G0 | contrato comum, erro, persistência, backup e fluxo mínimo |
| G1 | fonte, citação, conflito, S01/S02 e privacidade de corpus |
| G2 | cálculos de capacidade, versões, portfólio e integração |
| G3 | PE/PT, pactuação, alteração e histórico |
| G4 | agregação, suficiência estatística e ausência de ranking |
| G5 | prazos, competência, avaliação, recurso e decisão humana |
| G6 | regressão, segurança, desempenho, restauração e piloto |

## 12. Aceite conjunto

O registro de aceite contém: escopo, versões, casos executados, defeitos, riscos residuais,
pendências humanas, restrições de uso e decisão `aprovar`, `aprovar com restrição` ou
`não aprovar`. Uma pendência documental nunca é ocultada para obter aprovação.

## 13. Piloto

O piloto só usa unidades e pessoas autorizadas. Mede utilidade, tempo, erros, perguntas,
intervenções humanas, compreensão das fontes e confiança. Não mede produtividade
individual nem cria ranking. Incidente crítico suspende o caso afetado.

## 14. Checklist de release documental/técnico

- [ ] versão e changelog;
- [ ] contratos sincronizados;
- [ ] migrações e estado real conferidos;
- [ ] testes registrados;
- [ ] links e documentação válidos;
- [ ] varredura de segredos/dados;
- [ ] backup/restauração quando aplicável;
- [ ] riscos e questões atualizados;
- [ ] commits que seriam publicados identificados antes de eventual push.
