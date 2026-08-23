# 08 — Rastreabilidade, decisões e riscos

## 1. Cadeia de rastreabilidade

```text
objetivo → resultado-chave → incremento/onda → skill → regra/fonte
         → contrato → teste → execução → decisão humana → risco/pendência
```

Todo item deve poder responder: por que existe, qual fonte sustenta, quem decide, como é
testado e qual evidência demonstra seu estado.

## 2. Namespaces

| Prefixo | Uso |
| --- | --- |
| RK | resultado-chave |
| CA | critério de aceite |
| RP | risco do projeto |
| Q | questão aberta |
| RN | regra negocial |
| CT | controle técnico |
| S | skill |
| I | incremento técnico/negocial |
| M | marco |
| G | gate |
| ADR | decisão arquitetural |

IDs não são reutilizados. Renumeração exige tabela de correspondência.

## 3. Decisões

| ADR | Decisão | Estado | Consequência |
| --- | --- | --- | --- |
| 001 | SQLite inicial | Substituída | preservada apenas como histórico |
| 002 | Denodo somente leitura | Vigente | nenhuma escrita no PETRVS |
| 003 | arquitetura em capacidades | Vigente | RAG, indicadores e skills separados |
| 004 | modelo de linguagem substituível | Vigente | contratos não dependem do fornecedor |
| 005 | stack RAG | Vigente com revisão local-first | corpus e citações governados |
| 006 | MySQL 8 local | Vigente | 21 tabelas/6 triggers atuais |
| 007 | execução e avaliação S21–S24 | Registrada na v6 | migração `002` permanece planejada |
| 008 | desenvolvimento solo local-first S01–S24 | Registrada na v6 | 104 semanas e custo incremental zero |

## 4. Questões abertas consolidadas

| ID | Questão | Destinatário | Bloqueia | Status/evidência necessária |
| --- | --- | --- | --- | --- |
| Q05 | Quais fontes entram no registro/RAG inicial? | analistas/autoridade | G1 | pendente, exige validação e ata |
| Q17 | Qual calendário institucional deve alimentar prazos futuros? | CGGE | S21–S24 | configuração validada |
| Q18 | Faixa percentual CGOV será mantida, revista ou descartada? | CGGE/CGOV | S22 | decisão como regra institucional |
| Q19 | Medidas para conceitos 4/5 do PE | direção/CGGE | S22 | regra e fonte/decisão |
| Q20 | Tratamento de chefia dispensada sem PT | CGGE | S21/S24 | decisão funcional |
| Q21 | Unidade responsável por contribuição interunidade | CGGE | S15/S23 | regra pactuada |
| Q22 | Parecer deve tramitar no SEI? | CGGE/SEI | operação S22/S24 | fluxo e tipo documental |
| Q23 | Conjunto histórico suficiente para S19 | governança | validação real S19 | base autorizada e critérios |
| Q24 | Ambiente/licenças para piloto multiusuário | TI/autoridade | G6 | decisão institucional |
| Q25 | Responsáveis permanentes por regras, dados e suporte | autoridade | adoção | designação formal |

## 5. Riscos por tema

O registro detalhado e mutável fica em [`docs/gestao/riscos.md`](../gestao/riscos.md).

| Tema | IDs principais | Controles |
| --- | --- | --- |
| Qualidade de IA | RP02 e correlatos | tool calling, citação, confiança, revisão |
| Dados pessoais | RP06, RP17, RP24 | minimização, pseudônimo, agregação |
| Histórico | RP13 | versões e triggers |
| Infraestrutura | RP15, RP16 | backup, contingência e erros controlados |
| Execução/avaliação | RP18–RP23 | autoridade, prazos e separação PE/PT |
| Desenvolvimento individual | RP25–RP28 | capacidade real, WIP e gates |
| Serviços pessoais/gratuitos | RP29–RP31 | local-first e ausência de dependência crítica |
| Adoção institucional | RP32–RP33 | decisão e arquitetura próprias |

## 6. Matriz de rastreabilidade mínima

| Resultado | Entrega | Skills | Testes | Riscos |
| --- | --- | --- | --- | --- |
| RK01 | RAG citável | S01/S02 | RAG-01.. | RP02/Q01 |
| RK02 | indicadores por ferramenta | transversal | DEN-01.. | RP02/RP16 |
| RK03 | motor comum | S01–S24 | CT/INT | RP13/RP28 |
| RK04 | validadores | S05/S07/S08/S21–S24 | unidade/limite | RP18/RP20 |
| RK05 | histórico | S04/S11/S12/S14/S21–S24 | persistência | RP13 |
| RK06 | perguntas pendentes | todas | ausência/conflito | RP02 |
| RK07 | privacidade | S17/S18/S23/S24 | SEC/LGPD | RP06/RP17/RP24 |
| RK08 | custo zero | plataforma | execução local | RP29–RP31 |
| RK09 | ondas integradas | grupos de skills | regressão/gate | RP25–RP28 |
| RK10 | fronteira institucional | G6 | checklist de adoção | RP32–RP33 |

## 7. Estado e comprovação

| Afirmação | Estado | Evidência |
| --- | --- | --- |
| MySQL 8.4.9 instalado | Concluído | serviço local e testes prévios |
| Migração `001` aplicada | Concluído | `schema_migracoes` |
| 21 tabelas/6 triggers | Atual | inspeção do banco |
| Migração `002` aplicada | Não | estado-alvo 33/14 |
| Denodo sincronizado | Concluído/monitorado | 816 unidades, 19 usuários piloto |
| Q5 aprovada | Não | falta validação/ata |
| S01–S24 implementadas | Não | cronograma futuro |
| Protótipo institucional | Não | somente desenvolvimento individual |

## 8. Regra de fechamento

Questão fecha com decisão e evidência. Risco fecha ou muda de estado com evidência de
controle. Skill aprova com definição de pronto. Gate avança com registro. Texto de
planejamento não satisfaz nenhum desses requisitos isoladamente.
