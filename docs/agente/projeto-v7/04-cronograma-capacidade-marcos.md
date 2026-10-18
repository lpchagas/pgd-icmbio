# 04 — Cronograma, capacidade e marcos

## 1. Linha de base

O cronograma começa em 31/08/2026 e termina em 27/08/2028. Datas de aprovação humana não
são prometidas: quando um gate depender de decisão, o ciclo prepara evidências e registra
o bloqueio.

### Premissas

- 12 horas brutas por semana;
- 8–9 horas efetivas após administração e interrupções;
- ciclos de 14 dias;
- máximo de duas skills simultâneas;
- revisão a cada quatro ciclos;
- reserva de 12 semanas;
- nenhuma dependência obrigatória de API paga.

## 2. Visão por etapa

| Etapa | Ciclos | Semanas | Resultado |
| --- | --- | ---: | --- |
| Fundação | C01–C04 | 8 | fluxo local mínimo e contratos comuns |
| Onda 1 | C05–C12 | 16 | S01, S02, S03, S05, S09, S17 |
| Onda 2 | C13–C21 | 18 | S04, S06, S07, S08, S10, S20 |
| Onda 3 | C22–C29 | 16 | S11, S12, S13, S14 |
| Onda 4 | C30–C38 | 18 | S15, S16, S18, S19 |
| Onda 5 | C39–C46 | 16 | S21, S22, S23, S24 |
| Estabilização | C47–C52 | 12 | regressão, documentação e piloto controlado |

## 3. Plano quinzenal

| Ciclo | Início | Fim | Onda | Foco | Entrega/validação | Dependência ou margem |
| --- | --- | --- | --- | --- | --- | --- |
| C01 | 31/08/2026 | 13/09/2026 | Fundação | contratos e registro de skills | esqueleto validado | ambiente local |
| C02 | 14/09/2026 | 27/09/2026 | Fundação | API e execução mínima | `POST /skill` de prova | sem dado real |
| C03 | 28/09/2026 | 11/10/2026 | Fundação | RAG local e indicador de prova | fluxo com fonte/tool | corpus público/sintético |
| C04 | 12/10/2026 | 25/10/2026 | Fundação | integração, segurança e M1 | teste ponta a ponta | corrigir fundação |
| C05 | 26/10/2026 | 08/11/2026 | Onda 1 | S01 especificação/regras | contrato e casos | Q5 continua pendente |
| C06 | 09/11/2026 | 22/11/2026 | Onda 1 | S01 implementação/teste | fontes versionadas | corpus permitido |
| C07 | 23/11/2026 | 06/12/2026 | Onda 1 | S02 | conformidade e conflitos | S01 |
| C08 | 07/12/2026 | 20/12/2026 | Onda 1 | S03 | competências/candidatas | S01 |
| C09 | 21/12/2026 | 03/01/2027 | Onda 1 | reserva/férias e revisão | correções/documentação | margem planejada |
| C10 | 04/01/2027 | 17/01/2027 | Onda 1 | S05 | metas e aceite | S01 |
| C11 | 18/01/2027 | 31/01/2027 | Onda 1 | S09 e S17 | vínculos/evidências | S01/S05 |
| C12 | 01/02/2027 | 14/02/2027 | Onda 1 | integração e G1/M2 | regressão da onda | validação humana |
| C13 | 15/02/2027 | 28/02/2027 | Onda 2 | S04 | catálogo versionado | S03 |
| C14 | 01/03/2027 | 14/03/2027 | Onda 2 | S06 | auditoria de portfólio | S02/S04/S05 |
| C15 | 15/03/2027 | 28/03/2027 | Onda 2 | S07 especificação/cálculo | CHD e cenários | referências/calendário |
| C16 | 29/03/2027 | 11/04/2027 | Onda 2 | S07 teste | bateria determinística | S05 |
| C17 | 12/04/2027 | 25/04/2027 | Onda 2 | S08 | cobertura e concentração | S07 |
| C18 | 26/04/2027 | 09/05/2027 | Onda 2 | S10 | riscos/restrições | S05/S07 |
| C19 | 10/05/2027 | 23/05/2027 | Onda 2 | S20 contratos | importação/exportação | modelo comum |
| C20 | 24/05/2027 | 06/06/2027 | Onda 2 | S20 reconciliação | relatório de divergência | dados sintéticos |
| C21 | 07/06/2027 | 20/06/2027 | Onda 2 | integração e G2/M3 | regressão da onda | margem/correções |
| C22 | 21/06/2027 | 04/07/2027 | Onda 3 | S11 especificação | minuta de PE | S02/S06/S07/S10 |
| C23 | 05/07/2027 | 18/07/2027 | Onda 3 | S11 implementação | PE versionado | contratos prontos |
| C24 | 19/07/2027 | 01/08/2027 | Onda 3 | S12 especificação | minuta de PT | S07/S08/S11 |
| C25 | 02/08/2027 | 15/08/2027 | Onda 3 | S12 implementação | PT versionado | S11 |
| C26 | 16/08/2027 | 29/08/2027 | Onda 3 | S13 | check-in rastreável | S10/S12/S17 |
| C27 | 30/08/2027 | 12/09/2027 | Onda 3 | S14 especificação | análise de impacto | S13 |
| C28 | 13/09/2027 | 26/09/2027 | Onda 3 | S14 implementação | nova versão preservada | serviço de versões |
| C29 | 27/09/2027 | 10/10/2027 | Onda 3 | integração e G3/M4 | ciclo PE/PT | validação humana |
| C30 | 11/10/2027 | 24/10/2027 | Onda 4 | S15 | contribuição interunidades | S08/S12/S14 |
| C31 | 25/10/2027 | 07/11/2027 | Onda 4 | S16 especificação | critérios de análise | S05/S13/S17 |
| C32 | 08/11/2027 | 21/11/2027 | Onda 4 | S16 implementação | análise intermediária | decisão humana |
| C33 | 22/11/2027 | 05/12/2027 | Onda 4 | S18 contratos/agregação | relatório sem ranking | S06–S17 |
| C34 | 06/12/2027 | 19/12/2027 | Onda 4 | S18 implementação | relatório gerencial | privacidade |
| C35 | 20/12/2027 | 02/01/2028 | Onda 4 | reserva/férias | correções e dados | margem planejada |
| C36 | 03/01/2028 | 16/01/2028 | Onda 4 | S19 estatística | suficiência e métricas | histórico mínimo |
| C37 | 17/01/2028 | 30/01/2028 | Onda 4 | S19 semântica | hipóteses/recomendações | S18 |
| C38 | 31/01/2028 | 13/02/2028 | Onda 4 | integração e G4/M5 | regressão/inteligência | pode usar sintéticos |
| C39 | 14/02/2028 | 27/02/2028 | Onda 5 | fundação migração `002` | SQL e testes revisados | não aplicar sem gate |
| C40 | 28/02/2028 | 12/03/2028 | Onda 5 | S21 especificação | execução PE | S04/S05/S07/S17 |
| C41 | 13/03/2028 | 26/03/2028 | Onda 5 | S21 implementação | progresso/intercorrência | S14 |
| C42 | 27/03/2028 | 09/04/2028 | Onda 5 | S23 | execução PT | S12/S17/S21 |
| C43 | 10/04/2028 | 23/04/2028 | Onda 5 | S22 | avaliação PE | S10/S16/S21 |
| C44 | 24/04/2028 | 07/05/2028 | Onda 5 | S24 | avaliação PT | S23 |
| C45 | 08/05/2028 | 21/05/2028 | Onda 5 | recurso e conciliação | ciclo completo | Denodo opcional em QA |
| C46 | 22/05/2028 | 04/06/2028 | Onda 5 | integração e G5/M6 | S21→S24 | validação humana |
| C47 | 05/06/2028 | 18/06/2028 | Estabilização | regressão funcional | S01–S24 | reserva |
| C48 | 19/06/2028 | 02/07/2028 | Estabilização | segurança/LGPD | auditoria e correções | dados autorizados |
| C49 | 03/07/2028 | 16/07/2028 | Estabilização | desempenho/backup | restauração e carga | ambiente local |
| C50 | 17/07/2028 | 30/07/2028 | Estabilização | documentação/capacitação | manuais finais | feedback |
| C51 | 31/07/2028 | 13/08/2028 | Estabilização | piloto controlado | métricas e incidentes | autorização necessária |
| C52 | 14/08/2028 | 27/08/2028 | Estabilização | G6/M7 | relatório de prontidão | decisão institucional futura |

## 4. Marcos e gates

| Marco | Gate | Evidência |
| --- | --- | --- |
| M0 — execução mínima | durante G0 | chamada, registro e resposta estruturada |
| M1 — fundação | G0 | testes comuns e ambiente reproduzível |
| M2 — fundamentos | G1 | fontes/regras/evidências rastreáveis |
| M3 — entregas | G2 | portfólio e capacidade coerentes |
| M4 — trabalho | G3 | PE/PT pactuáveis e versionados |
| M5 — inteligência | G4 | relatórios e aprendizagem com limites |
| M6 — avaliação | G5 | ciclo execução→avaliação completo |
| M7 — estabilização | G6 | regressão e piloto autorizado |

## 5. Controle de capacidade

Em cada ciclo registrar: horas disponíveis, horas usadas, trabalho concluído, defeitos,
dependências, decisões pendentes e previsão. A baseline é revista se houver desvio maior
que quatro semanas, disponibilidade menor que nove horas brutas por dois meses, mudança
normativa, substituição de componente ou bloqueio externo prolongado.

## 6. Cenários

| Horas brutas/semana | Efetivas estimadas | Duração |
| ---: | ---: | ---: |
| 8 | 5,5–6 | 30–34 meses |
| 12 | 8–9 | 22–24 meses |
| 20 | 14–15 | 15–17 meses |

Prazo inferior a 15 meses requer reduzir escopo/qualidade, aumentar dedicação ou incluir
outra pessoa. Não se comprimem gates de segurança e validação para cumprir data.

## 7. Dependências humanas e externas

| Dependência | Tratamento no cronograma |
| --- | --- |
| Q5 | desenvolvimento com público/sintético; aprovação da onda fica condicionada |
| Ata real | nunca gerar automaticamente; registrar bloqueio |
| Dados históricos S19 | preparar até C36; validar com sintéticos se ausentes |
| Denodo | necessário para validação real, não para todos os testes unitários |
| Licença institucional | não bloqueia protótipo local; bloqueia publicação ampla |
| Disponibilidade individual | recalcular baseline bimestralmente |
