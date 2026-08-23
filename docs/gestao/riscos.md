# Matriz de riscos — pgd-agente-icmbio

> Extraída da Seção 10 ("Matriz de riscos consolidada") de `proposta-projeto-v5.md` (que
> substitui a `proposta-projeto-v4.md` como documento de planejamento vigente e formaliza
> RP16 e o bloco RP17–RP24; RP01–RP15 permanecem como identificados na v4 §10, apenas
> herdados pela v5). Este arquivo é o registro ativo de acompanhamento (Entregável de
> Gestão do Incremento I0); a proposta permanece a fonte normativa — em caso de
> divergência, ela prevalece. Atualize a coluna **Status** conforme os riscos forem
> mitigados, materializados ou encerrados; não edite o histórico de identificação
> (RP01–RP15) sem registrar o motivo.

| ID | Risco | Probabilidade | Impacto | Mitigação | Responsável | Status |
| --- | --- | --- | --- | --- | --- | --- |
| RP01 | Provisionamento Azure/Connector atrasar e travar I7 | Alta | Alto | Processo com TI iniciado em I6; Streamlit como plano B | Coordenador | Aberto |
| RP02 | Agente alucinar números ou regras | Média | Alto | Indicadores só via tool calling; toda regra com fonte; confiança explícita; validação humana em baixa confiança | Coordenador | Aberto |
| RP03 | Confusão entre norma e recomendação (PA3) | Alta | Alto | Natureza da regra é campo obrigatório (`ENUM` no banco); teste S01-T04 | Analistas | Mitigado (schema) |
| RP04 | Meta confundir esforço com resultado; meta × progresso (PA1) | Alta | Alto | Campos distintos `meta`/`meta_final` no esquema + validador; teste S05-T04 | Analistas | Mitigado (schema) |
| RP05 | Cálculos de capacidade com falsa precisão | Alta | Médio | Faixas e cenários; incerteza sempre visível | Coordenador | Aberto |
| RP06 | Dados individuais de disponibilidade expostos | Média | Alto | Espelho mínimo D2 (sem CPF/e-mail); pseudônimos; agregação; checklist da Seção 11 | Coordenador | Mitigado (schema) |
| RP07 | OKR-D afirmar causalidade indevida | Alta | Alto | Justificativa obrigatória (`NOT NULL` no banco); linguagem de contribuição plausível | Analistas | Mitigado (schema) |
| RP08 | Excesso de alertas tornar o agente irritante | Média | Alto | Gravidade + confiança + limiar configurável; revisão com usuários no I4 | Analistas | Aberto |
| RP09 | Escopo crescer ("já que estamos fazendo…") | Alta | Alto | S11–S20 fora do MVP; inclusão exige v5 | Coordenador | Materializado uma vez, pelo rito previsto (v5 incorporou S21–S24 como Fase 2, sem alterar o MVP S01–S10) |
| RP10 | Dependência de pessoa única | Alta | Alto | ADRs, specs em Markdown, tutoriais, pareamento; ciclo de vida com papéis explícitos | Todos | Mitigado parcial (ADRs 001-006 registrados) |
| RP11 | Equipe não absorver o papel de ED/QA | Média | Alto | RC6 mede autonomia; passos 1–4 do ciclo são não técnicos | Coordenador | Aberto |
| RP12 | Credencial vazar em repositório | Baixa | Alto | `.gitignore` desde o dia zero (inclui `.env` com credenciais MySQL); verificação pré-push | Coordenador | Mitigado (.gitignore ativo) |
| RP13 | Integrações perderem histórico/IDs | Média | Alto | Triggers de imutabilidade no banco (AT-01 §6.3) — nem script com bug sobrescreve histórico; teste RC4/INT-T01 | Coordenador | Mitigado (triggers testados em produção local, 26.07.2026) |
| RP14 | Custo de API sair do controle | Baixa | Baixo | Limite mensal no provedor (Tutorial T3) | Coordenador | Aberto |
| RP15 | Indisponibilidade ou corrupção do serviço MySQL local travar o trabalho | Baixa | Médio | `mysqldump` diário para pasta com backup (padrão `backup.ps1`); script de reinstalação + `schema.sql` versionado permitem reconstruir o ambiente em horas | Coordenador | Mitigado (tarefa agendada `pgd_agente_backup` ativa; dumps confirmados) |

## Risco de ambiente identificado em 26.07.2026, formalizado na v5 (18.08.2026)

| ID | Risco | Probabilidade | Impacto | Mitigação | Responsável | Status |
| --- | --- | --- | --- | --- | --- | --- |
| RP16 | Máquina de desenvolvimento sem rota de rede para o Denodo institucional impede `sincronizar_ref.py` de popular `ref_unidades`/`ref_usuarios` | Alta (confirmada) | Alto (bloqueia D2, aceite do I0, o Incremento I5 e a etapa E6 da Fase 2) | Executar a sincronização de uma máquina com VPN/rede institucional ativa; documentar o procedimento de rede exigido; acionar TI/Dataprev (Q16); contingência sintética para E6 | Coordenador | **Mitigado — rota de rede restabelecida e `sincronizar_ref.py` executado com sucesso em 22.08.2026 (816 `ref_unidades`, 19 `ref_usuarios` via `unidades_integrantes`, sem fallback); ver CLAUDE.md §10** |

## Riscos incorporados na v5 (Fase 2 — S21–S24), 18.08.2026

| ID | Risco | Probabilidade | Impacto | Mitigação | Responsável | Status |
| --- | --- | --- | --- | --- | --- | --- |
| RP17 | Dado sensível de saúde em intercorrência (a IN cita "situações de saúde" como intercorrência a registrar) | Alta | Alto | `ocorrencias.sensivel = 1`; armazenar apenas categoria e impacto em horas; conteúdo clínico nunca persistido; S23-T06 como teste de segurança obrigatório | Coordenador | Aberto (planejado — depende da migração `002`) |
| RP18 | Agente induzindo o conceito — sugestão com aparência de decisão enviesa a chefia e gera contestação com efeito funcional | Média | Alto | Invariante I2; `origem_conceito` explícito; parecer não homologado ostenta marcação; justificativa sempre da chefia | Coordenador | Aberto (planejado) |
| RP19 | Assimetria PE × PT (C-02): tratar as duas avaliações como um só objeto ofereceria recurso onde ele não existe | Média | Alto | Separação estrutural desde o modelo de dados (`avaliacoes.objeto_tipo`); testes de regressão específicos | Coordenador | Aberto (planejado) |
| RP20 | Datas do ciclo 2026 inconsistentes (C-01) fariam o motor de prazos calcular errado | Alta | Alto | E0 bloqueia a implementação até confirmação da CGGE (Q9); calendário por configuração, não por constante | Analistas | Aberto (planejado) |
| RP21 | Faixa percentual sem lastro normativo (A-01) migrar para o agente como se fosse norma | Média | Médio | Registro como regra institucional com fonte e vigência; rotulagem obrigatória na saída (S22-T07) | Analistas | Aberto (planejado) |
| RP22 | Uso indevido da avaliação do PGD como avaliação de desempenho anual (RN-36) | Média | Médio | Ressalva obrigatória em todo parecer (S24-T09); menção na capacitação | Analistas | Aberto (planejado) |
| RP23 | Volume do ciclo mensal (PT mensal × N participantes × 12 meses) inviabilizar o uso manual | Média | Médio | Processamento em lote no S18 (pós-MVP); priorizar unidades-piloto; medir tempo médio por registro no E7 | Coordenador | Aberto (planejado) |
| RP24 | Exposição de dados individuais em relatórios de transparência | Média | Alto | Pseudônimos (`participantes.rotulo`); agregação por unidade; nenhum ranking individual | Coordenador | Aberto (planejado) |

RP17–RP24 são riscos da **Fase 2** (S21–S24), que só inicia após o Incremento I2 — não
afetam o aceite do I0, listado apenas como planejamento antecipado.
