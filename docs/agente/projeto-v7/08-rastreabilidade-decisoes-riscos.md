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
| C | ciclo quinzenal do cronograma |
| M | marco |
| G | gate |
| ADR | decisão arquitetural |
| DP | decisão de estrutura do projeto |
| D | deliberação da CGOV (citada só pelo identificador e efeito técnico) |

IDs não são reutilizados. Renumeração exige tabela de correspondência.

## 3. Decisões de arquitetura

| ADR | Decisão | Estado | Consequência |
| --- | --- | --- | --- |
| 001 | SQLite inicial | Substituída | preservada apenas como histórico |
| 002 | Denodo somente leitura | Vigente | nenhuma escrita no PETRVS |
| 003 | arquitetura em capacidades | Vigente | RAG, indicadores e skills separados |
| 004 | modelo de linguagem substituível | Princípio vigente; estratégia revisada pela 014 | contratos não dependem do fornecedor |
| 005 | stack RAG | Vigente com revisão local-first | corpus e citações governados |
| 006 | MySQL 8 local | Vigente | 21 tabelas/6 triggers atuais |
| 007 | execução e avaliação S21–S24 | Aprovada, com regras institucionais pendentes | migração `002` permanece planejada |
| 008 | desenvolvimento individual local-first S01–S24 | Aprovada; item 7 revisado pela 014 | 104 semanas e custo incremental zero |
| 009 | arquitetura integrada do monorepo | Vigente | agente em `agente/`; o núcleo analítico não o importa |
| 010 | sincronia das instruções | Revisada pela 013 | núcleo comum e verificação no CI |
| 011 | unidades piloto | Vigente | CGOV, COCAGE e GR2 com seletores exatos |
| 012 | configuração do Denodo | Vigente | ponto único em `lib/denodo_config.py` |
| 013 | retirada do Codex | Vigente | dois pares de instruções: `CLAUDE.md` e `PROJECT.md` |
| 014 | servidor MCP local e arranjo híbrido | Vigente | gate de classe no servidor; Ollama para o institucional; FastAPI opcional |

Decisões de estrutura e processo (DP-01 a DP-09) ficam no
[registro de decisões do projeto](../../decisoes/registro-decisoes-projeto.md). As que
afetam a v7 são DP-07 (ADR-013), DP-08 (ADR-014) e DP-09 (catálogo único e fonte
metodológica canônica).

## 4. Questões abertas consolidadas

| ID | Questão | Destinatário | Bloqueia | Status/evidência necessária |
| --- | --- | --- | --- | --- |
| Q05 | Quais fontes entram no registro/RAG inicial? | analistas/autoridade | G1 (corpus institucional) | pendente, exige validação e ata; até lá, só allowlist pública |
| Q17 | Qual calendário institucional deve alimentar prazos futuros? | CGGE | — | **respondida em 14.09.2026:** Q1 = 01/01–30/04, Q2 = 01/05–31/08, Q3 = 01/09–31/12, sem Q4; o Q2 termina sempre em 31/08 |
| Q18 | Faixa percentual CGOV será mantida, revista ou descartada? | CGGE/CGOV | S22 | decisão como regra institucional |
| Q19 | Medidas para conceitos 4/5 do PE | direção/CGGE | S22 | regra e fonte/decisão |
| Q20 | Tratamento de chefia dispensada sem PT | CGGE | S21/S24 | decisão funcional |
| Q21 | Unidade responsável por contribuição interunidade | CGGE | S15/S23 | regra pactuada |
| Q22 | Parecer deve tramitar no SEI? | CGGE/SEI | operação S22/S24 | fluxo e tipo documental |
| Q23 | Conjunto histórico suficiente para S19 | governança | validação real S19 | base autorizada e critérios; candidato: histórico cumulativo dos indicadores |
| Q24 | Ambiente/licenças para piloto multiusuário | TI/autoridade | G6 | decisão institucional |
| Q25 | Responsáveis permanentes por regras, dados e suporte | autoridade | adoção | designação formal |

Também pendentes, sem número próprio: validação humana do glossário e do modelo comum
(até o G1) e validação pela CGOV dos casos sintéticos das fichas.

## 5. Riscos por tema

O registro detalhado e mutável fica em [`docs/governanca-projeto/riscos.md`](../../governanca-projeto/riscos.md).

| Tema | IDs principais | Controles |
| --- | --- | --- |
| Qualidade de IA | RP02 e correlatos | ferramentas determinísticas, citação, confiança, revisão |
| Dados pessoais | RP06, RP17, RP24 | minimização, pseudônimo, agregação |
| Histórico | RP13 | versões e triggers |
| Infraestrutura | RP15, RP16 | backup, instância isolada, erros controlados |
| Execução/avaliação | RP18–RP23 | autoridade, prazos e separação PE/PT |
| Desenvolvimento individual | RP25–RP28 | capacidade real, WIP e gates |
| Serviços pessoais/gratuitos | RP29–RP31 | local-first e ausência de dependência crítica |
| Adoção institucional | RP32–RP33 | decisão e arquitetura próprias |
| Arranjo híbrido (v7) | RP34–RP36 | segunda ferramenta de desenvolvimento, gate de classe no servidor, spike do modelo local |

## 6. Matriz de rastreabilidade mínima

| Resultado | Entrega | Skills | Testes | Riscos |
| --- | --- | --- | --- | --- |
| RK01 | RAG citável | S01/S02 | RAG-01.. | RP02 |
| RK02 | indicadores por ferramenta sobre o A2 | transversal | DEN-01.. | RP02/RP16 |
| RK03 | motor e contratos comuns | S01–S24 | CT/INT | RP13/RP28 |
| RK04 | validadores | S05/S07/S08/S21–S24 | unidade/limite | RP18/RP20 |
| RK05 | histórico | S04/S11/S12/S14/S21–S24 | persistência | RP13 |
| RK06 | perguntas pendentes | todas | ausência/conflito | RP02 |
| RK07 | privacidade e gate de classe | S17/S18/S23/S24 e servidor MCP | SEC/LGPD | RP06/RP17/RP24/RP35 |
| RK08 | custo zero | plataforma | execução local | RP29–RP31/RP36 |
| RK09 | ondas integradas | grupos de skills | regressão/gate | RP25–RP28/RP34 |
| RK10 | fronteira institucional | G6 | checklist de adoção | RP32–RP33 |

## 7. Estado e comprovação em 17/10/2026

| Afirmação | Estado | Evidência |
| --- | --- | --- |
| MySQL 8.4 ativo no WSL | Concluído | serviço do systemd |
| Migração `001` aplicada | Concluído | `schema_migracoes` |
| 21 tabelas/6 triggers | Atual | inspeção do banco |
| Migração `002` aplicada | Não | estado-alvo 33/14, Onda 5 |
| Backup diário | Ativo | timer `pgd-agente-backup`; dumps com retenção de 14 dias |
| Restauração comprovada | Concluído | instância isolada e `banco_teste.py` |
| Espelhos Denodo | Sincronizados em 22/08/2026 | 816 unidades, 19 usuários piloto |
| Indicadores homologados nos pilotos | Concluído | certificação A1–A5 e aceites por piloto (projeto analítico) |
| Catálogo único e fichas 0.2 | Concluído | `capacidades/catalogo.yaml`; gerador verificado na suíte |
| Contratos, motor, servidor MCP, RAG | Não | Fundação, C01–C04 |
| Q5 aprovada | Não | falta validação/ata |
| S01–S24 implementadas | Não | cronograma por ondas |
| Protótipo institucional | Não | somente desenvolvimento individual |

## 8. Regra de fechamento

Questão fecha com decisão e evidência. Risco fecha ou muda de estado com evidência de
controle. Skill aprova com definição de pronto. Gate avança com registro. Texto de
planejamento não satisfaz nenhum desses requisitos isoladamente.
