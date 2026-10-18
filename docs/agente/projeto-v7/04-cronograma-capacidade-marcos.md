# 04 — Cronograma, capacidade e marcos

## 1. Linha de base

O cronograma começa em 02/11/2026 e termina em 29/10/2028: 52 ciclos de 14 dias. Datas
de aprovação humana não são prometidas: quando um gate depender de decisão, o ciclo
prepara evidências e registra o bloqueio.

A grade da v6 (31/08/2026 a 27/08/2028) foi deslocada nove semanas. O início da Fundação
foi ocupado pela Fase A: fechamento da validação dos indicadores nos pilotos, retirada do
Codex (ADR-013) e decisão sobre o LLM em execução (ADR-014). Dentro das ondas, as reservas
de fim de ano foram reposicionadas para dezembro e janeiro (C05 e C31).

### Premissas

- 12 horas brutas por semana;
- 8–9 horas efetivas após administração e interrupções;
- 1–2 horas por mês reservadas ao ciclo gerencial mensal dos indicadores nos pilotos;
- ciclos de 14 dias;
- máximo de duas skills simultâneas;
- revisão de capacidade a cada quatro ciclos;
- margem: dois ciclos de reserva de fim de ano (C05 e C31), um ciclo de integração ao fim
  de cada onda e a Estabilização;
- nenhuma dependência obrigatória de API paga.

## 2. Antecedentes (out./2026)

| Etapa | Resultado | Situação |
| --- | --- | --- |
| Fase A — fechamento e transição | indicadores homologados nos pilotos e deliberação nacional (D36–D45); ADR-013; ADR-014 | concluída em 17/10/2026 |
| B1 — catálogo e proposta | `capacidades/catalogo.yaml`, fichas 0.2 com teste em outras IAs (DP-09) e esta proposta v7 | concluída em 17/10/2026, antes do C01 |

A B1 estava prevista para o C01. Como terminou antes, a grade não foi antecipada: o C01
começa a B2, e a folga fica como margem da Fundação.

## 3. Visão por etapa

| Etapa | Ciclos | Período | Semanas | Resultado |
| --- | --- | --- | ---: | --- |
| Fundação | C01–C04 | 02/11–27/12/2026 | 8 | contratos, motor mínimo, servidor MCP, indicador, RAG mínimo e M1 |
| Onda 1 | C05–C12 | 28/12/2026–18/04/2027 | 16 | S01, S02, S03, S05, S09, S17 |
| Onda 2 | C13–C21 | 19/04–22/08/2027 | 18 | S04, S06, S07, S08, S10, S20 |
| Onda 3 | C22–C29 | 23/08–12/12/2027 | 16 | S11, S12, S13, S14 |
| Onda 4 | C30–C38 | 13/12/2027–16/04/2028 | 18 | S15, S16, S18, S19 |
| Onda 5 | C39–C46 | 17/04–06/08/2028 | 16 | S21, S22, S23, S24 |
| Estabilização | C47–C52 | 07/08–29/10/2028 | 12 | regressão, documentação e piloto controlado |

## 4. Plano quinzenal

| Ciclo | Início | Fim | Etapa | Foco | Entrega/validação | Dependência ou margem |
| --- | --- | --- | --- | --- | --- | --- |
| C01 | 02/11/2026 | 15/11/2026 | Fundação | B2 — contratos Pydantic comuns | contratos com `classe_dado`; testes de contrato | B1 concluída antes do ciclo |
| C02 | 16/11/2026 | 29/11/2026 | Fundação | B2 — motor mínimo | registro de skills lido do `catalogo.yaml`; gravação de execuções, perguntas e decisões por `versoes.py` | testes de contrato e de rollback |
| C03 | 30/11/2026 | 13/12/2026 | Fundação | B3 — servidor MCP e ferramenta `indicador` | A2 certificado servido com liberação por piloto; gate de classe; DEN-01 contra o CSV oficial | A2 dos pilotos |
| C04 | 14/12/2026 | 27/12/2026 | Fundação | B4 — RAG mínimo, integração e M1 | RAG sobre a allowlist pública com citação; spike do Ollama; ponta a ponta Claude Code → MCP; testes G0 | corpus público; hardware local |
| C05 | 28/12/2026 | 10/01/2027 | Onda 1 | reserva de fim de ano | correções da Fundação e documentação | margem planejada |
| C06 | 11/01/2027 | 24/01/2027 | Onda 1 | S01 especificação/regras | contrato e casos | Q5 continua pendente |
| C07 | 25/01/2027 | 07/02/2027 | Onda 1 | S01 implementação/teste | fontes versionadas | só corpus público até a Q5 |
| C08 | 08/02/2027 | 21/02/2027 | Onda 1 | S02 | conformidade e conflitos | S01 |
| C09 | 22/02/2027 | 07/03/2027 | Onda 1 | S03 | competências/candidatas | S01 |
| C10 | 08/03/2027 | 21/03/2027 | Onda 1 | S05 | metas e aceite | S01 |
| C11 | 22/03/2027 | 04/04/2027 | Onda 1 | S09 e S17 | vínculos/evidências | S01/S05; calendário Q1–Q3 (Q17) |
| C12 | 05/04/2027 | 18/04/2027 | Onda 1 | integração e G1/M2 | regressão da onda | validação humana |
| C13 | 19/04/2027 | 02/05/2027 | Onda 2 | S04 | catálogo versionado | S03 |
| C14 | 03/05/2027 | 16/05/2027 | Onda 2 | S06 | auditoria de portfólio | S02/S04/S05 |
| C15 | 17/05/2027 | 30/05/2027 | Onda 2 | S07 especificação/cálculo | CHD e cenários | `lib/calendario.py` (dias úteis, D29) |
| C16 | 31/05/2027 | 13/06/2027 | Onda 2 | S07 teste | bateria determinística | S05 |
| C17 | 14/06/2027 | 27/06/2027 | Onda 2 | S08 | cobertura e concentração | S07 |
| C18 | 28/06/2027 | 11/07/2027 | Onda 2 | S10 | riscos/restrições | S05/S07 |
| C19 | 12/07/2027 | 25/07/2027 | Onda 2 | S20 contratos | importação/exportação | modelo comum; PETRVS só via Denodo |
| C20 | 26/07/2027 | 08/08/2027 | Onda 2 | S20 reconciliação | relatório de divergência | dados sintéticos |
| C21 | 09/08/2027 | 22/08/2027 | Onda 2 | integração e G2/M3 | regressão da onda | margem/correções |
| C22 | 23/08/2027 | 05/09/2027 | Onda 3 | S11 especificação | minuta de PE | S02/S06/S07/S10 |
| C23 | 06/09/2027 | 19/09/2027 | Onda 3 | S11 implementação | PE versionado | contratos prontos |
| C24 | 20/09/2027 | 03/10/2027 | Onda 3 | S12 especificação | minuta de PT | S07/S08/S11 |
| C25 | 04/10/2027 | 17/10/2027 | Onda 3 | S12 implementação | PT versionado | S11 |
| C26 | 18/10/2027 | 31/10/2027 | Onda 3 | S13 | check-in rastreável | S10/S12/S17; G01 e G02 como fatos, sem recálculo |
| C27 | 01/11/2027 | 14/11/2027 | Onda 3 | S14 especificação | análise de impacto | S13 |
| C28 | 15/11/2027 | 28/11/2027 | Onda 3 | S14 implementação | nova versão preservada | serviço de versões |
| C29 | 29/11/2027 | 12/12/2027 | Onda 3 | integração e G3/M4 | ciclo PE/PT | validação humana |
| C30 | 13/12/2027 | 26/12/2027 | Onda 4 | S15 | contribuição interunidades | S08/S12/S14 |
| C31 | 27/12/2027 | 09/01/2028 | Onda 4 | reserva de fim de ano | correções e dados | margem planejada |
| C32 | 10/01/2028 | 23/01/2028 | Onda 4 | S16 especificação | critérios de análise | S05/S13/S17 |
| C33 | 24/01/2028 | 06/02/2028 | Onda 4 | S16 implementação | análise intermediária | decisão humana |
| C34 | 07/02/2028 | 20/02/2028 | Onda 4 | S18 contratos/agregação | relatório sem ranking | S06–S17; parte do `relatorio_v2` e da política de privacidade |
| C35 | 21/02/2028 | 05/03/2028 | Onda 4 | S18 implementação | relatório gerencial | privacidade |
| C36 | 06/03/2028 | 19/03/2028 | Onda 4 | S19 estatística | suficiência e métricas | histórico cumulativo dos indicadores (Q23) |
| C37 | 20/03/2028 | 02/04/2028 | Onda 4 | S19 semântica | hipóteses/recomendações | S18 |
| C38 | 03/04/2028 | 16/04/2028 | Onda 4 | integração e G4/M5 | regressão/inteligência | pode usar sintéticos |
| C39 | 17/04/2028 | 30/04/2028 | Onda 5 | migração `002` | SQL revisado, backup, restauração, 33/14 | aplicar só com o gate da migração |
| C40 | 01/05/2028 | 14/05/2028 | Onda 5 | S21 especificação | execução PE | S04/S05/S07/S17 |
| C41 | 15/05/2028 | 28/05/2028 | Onda 5 | S21 implementação | progresso/intercorrência | S14 |
| C42 | 29/05/2028 | 11/06/2028 | Onda 5 | S23 | execução PT | S12/S17/S21 |
| C43 | 12/06/2028 | 25/06/2028 | Onda 5 | S22 | avaliação PE | S10/S16/S21; Q18–Q19 |
| C44 | 26/06/2028 | 09/07/2028 | Onda 5 | S24 | avaliação PT | S23; Q20–Q22 |
| C45 | 10/07/2028 | 23/07/2028 | Onda 5 | recurso e conciliação | ciclo completo | Denodo opcional em QA |
| C46 | 24/07/2028 | 06/08/2028 | Onda 5 | integração e G5/M6 | S21→S24, em substituição aos protótipos Cowork | validação humana |
| C47 | 07/08/2028 | 20/08/2028 | Estabilização | regressão funcional | S01–S24 | reserva |
| C48 | 21/08/2028 | 03/09/2028 | Estabilização | segurança/LGPD | auditoria, gate de classe e correções | dados autorizados |
| C49 | 04/09/2028 | 17/09/2028 | Estabilização | desempenho/backup | restauração e carga | ambiente local |
| C50 | 18/09/2028 | 01/10/2028 | Estabilização | documentação/capacitação | manuais finais | feedback |
| C51 | 02/10/2028 | 15/10/2028 | Estabilização | piloto controlado CGOV/COCAGE | métricas e incidentes | autorização necessária (Q24) |
| C52 | 16/10/2028 | 29/10/2028 | Estabilização | G6/M7 | relatório de prontidão | decisão institucional futura |

## 5. Marcos e gates

| Marco | Gate | Evidência |
| --- | --- | --- |
| M0 — execução mínima | durante G0 | chamada pelo MCP, registro e resposta estruturada |
| M1 — fundação | G0 | ambiente WSL reproduzível; pergunta com citação; indicador igual ao A2; execução rastreada no MySQL; teste negativo do gate de classe |
| M2 — fundamentos | G1 | fontes/regras/evidências rastreáveis |
| M3 — entregas | G2 | portfólio e capacidade coerentes |
| M4 — trabalho | G3 | PE/PT pactuáveis e versionados |
| M5 — inteligência | G4 | relatórios e aprendizagem com limites |
| M6 — avaliação | G5 | ciclo execução→avaliação completo |
| M7 — estabilização | G6 | regressão e piloto autorizado |

## 6. Controle de capacidade

Em cada ciclo registrar: horas disponíveis, horas usadas (inclusive no ciclo dos
indicadores), trabalho concluído, defeitos, dependências, decisões pendentes e previsão. A
baseline é revista a cada quatro ciclos e também se houver desvio maior que quatro
semanas, disponibilidade menor que nove horas brutas por dois meses, mudança normativa,
substituição de componente ou bloqueio externo prolongado.

## 7. Cenários

| Horas brutas/semana | Efetivas estimadas | Duração |
| ---: | ---: | ---: |
| 8 | 5,5–6 | 30–34 meses |
| 12 | 8–9 | 22–24 meses |
| 20 | 14–15 | 15–17 meses |

Prazo inferior a 15 meses requer reduzir escopo ou qualidade, aumentar dedicação ou
incluir outra pessoa. Não se comprimem gates de segurança e validação para cumprir data.

## 8. Dependências humanas e externas

| Dependência | Tratamento no cronograma |
| --- | --- |
| Q5 | desenvolvimento com público/sintético; aprovação da Onda 1 fica condicionada |
| Ata real | nunca gerar automaticamente; registrar bloqueio |
| A2 certificados dos pilotos | necessários desde o C03; vêm do ciclo gerencial mensal |
| Hardware para o modelo local | spike no C04; sem ele, o institucional fica só nas ferramentas determinísticas |
| Dados históricos S19 | preparar até o C36; validar com sintéticos se ausentes |
| Denodo | necessário para espelhos e S20, não para os testes unitários |
| Licença institucional | não bloqueia o protótipo local; bloqueia publicação ampla |
| Disponibilidade individual | recalcular a baseline a cada quatro ciclos |
