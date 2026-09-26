# Matriz de riscos — pgd-agente-icmbio

**Última revisão de status:** 23.08.2026

> Este é o registro ativo vinculado à [`00_proposta-projeto-v6.md`](../agente/projeto-v6/00_proposta-projeto-v6.md).
> A v6 consolidou RP01–RP24 e acrescentou os riscos do desenvolvimento individual,
> serviços pessoais e adoção institucional. Atualize a coluna **Status** conforme forem
> mitigados, materializados ou encerrados; não edite o histórico de identificação
> (RP01–RP15) sem registrar o motivo.

| ID | Risco | Probabilidade | Impacto | Mitigação | Responsável | Status |
| --- | --- | --- | --- | --- | --- | --- |
| RP01 | Provisionamento Azure/Connector atrasar e travar I7 | Alta | Alto | Processo com TI iniciado em I6; Streamlit como plano B | Coordenador | Aberto |
| RP02 | Agente alucinar números ou regras | Média | Alto | Indicadores só via tool calling; toda regra com fonte/localização; RAG em camadas; allowlist aprovada na Q5; OCR normativo revisado; confiança explícita; validação humana em baixa confiança | Coordenador | Mitigado parcial (arquitetura e classificação documentadas; corpus e Q5 pendentes) |
| RP03 | Confusão entre norma e recomendação (PA3) | Alta | Alto | Natureza da regra é campo obrigatório (`ENUM` no banco); precedência e matriz fonte a fonte em `fontes-institucionais.md`; teste S01-T04 | Analistas | Mitigado parcial (schema e proposta; aprovação Q5 pendente) |
| RP04 | Meta confundir esforço com resultado; meta × progresso (PA1) | Alta | Alto | Campos distintos `meta`/`meta_final` no esquema + validador; teste S05-T04 | Analistas | Mitigado (schema) |
| RP05 | Cálculos de capacidade com falsa precisão | Alta | Médio | Faixas e cenários; incerteza sempre visível | Coordenador | Aberto |
| RP06 | Dados individuais de disponibilidade expostos | Média | Alto | Espelho mínimo D2 (sem CPF/e-mail); pseudônimos; agregação; exclusão de I03/P01–P08/R01–R09 do RAG bruto; checklist da Seção 11 | Coordenador | Mitigado parcial (schema; saneamento físico do acervo restrito pendente) |
| RP07 | OKR-D afirmar causalidade indevida | Alta | Alto | Justificativa obrigatória (`NOT NULL` no banco); linguagem de contribuição plausível | Analistas | Mitigado (schema) |
| RP08 | Excesso de alertas tornar o agente irritante | Média | Alto | Gravidade + confiança + limiar configurável; revisão com usuários no I4 | Analistas | Aberto |
| RP09 | Escopo crescer ("já que estamos fazendo…") | Alta | Alto | Catálogo S01–S24 fechado; inclusão exige análise de dependências, ADR e replanejamento | Coordenador | Materializado; mitigação revista na v6 |
| RP10 | Dependência de pessoa única | Alta | Alto | ADRs, specs em Markdown, tutoriais, pareamento; ciclo de vida com papéis explícitos | Todos | Mitigado parcial (ADRs 001-006 registrados) |
| RP11 | Equipe não absorver o papel de ED/QA | Média | Alto | RC6 mede autonomia; passos 1–4 do ciclo são não técnicos | Coordenador | Aberto |
| RP12 | Credencial vazar em repositório | Baixa | Alto | `.gitignore` desde o dia zero (inclui `.env` com credenciais MySQL); verificação pré-push | Coordenador | Mitigado (.gitignore ativo) |
| RP13 | Integrações perderem histórico/IDs | Média | Alto | Triggers de imutabilidade no banco (AT-01 §6.3) — nem script com bug sobrescreve histórico; teste RC4/INT-T01 | Coordenador | Mitigado (triggers testados em produção local, 26.07.2026) |
| RP14 | Custo de API sair do controle | Baixa | Baixo | Núcleo sem API paga obrigatória; limite zero por padrão e ativação externa deliberada | Coordenador | Mitigado pela arquitetura local-first |
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
| RP20 | Datas do ciclo 2026 inconsistentes (C-01) fariam o motor de prazos calcular errado | Alta | Alto | Calendário decidido em 14.09.2026 (Q17): Q1 = 01/01–30/04, Q2 = 01/05–31/08, Q3 = 01/09–31/12, sem Q4; o Q2 termina sempre em 31/08, como em `lib/periodos.py`. A página da CGGE, inconsistente, não é usada. Calendário por configuração, não por constante | Analistas | Fechado (decisão de 14.09.2026) |
| RP21 | Faixa percentual sem lastro normativo (A-01) migrar para o agente como se fosse norma | Média | Médio | Registro como regra institucional com fonte e vigência; rotulagem obrigatória na saída (S22-T07) | Analistas | Aberto (planejado) |
| RP22 | Uso indevido da avaliação do PGD como avaliação de desempenho anual (RN-36) | Média | Médio | Ressalva obrigatória em todo parecer (S24-T09); menção na capacitação | Analistas | Aberto (planejado) |
| RP23 | Volume do ciclo mensal (PT mensal × N participantes × 12 meses) inviabilizar o uso manual | Média | Médio | Processamento em lote no S18 (pós-MVP); priorizar unidades-piloto; medir tempo médio por registro no E7 | Coordenador | Aberto (planejado) |
| RP24 | Exposição de dados individuais em relatórios de transparência | Média | Alto | Pseudônimos (`participantes.rotulo`); agregação por unidade; nenhum ranking individual | Coordenador | Aberto (planejado) |

RP17–RP24 pertencem à Onda 5, mas seus controles influenciam contratos e privacidade desde
a fundação.

## Riscos incorporados na v6 — desenvolvimento individual e adoção

| ID | Risco | Probabilidade | Impacto | Mitigação | Responsável | Status |
| --- | --- | --- | --- | --- | --- | --- |
| RP25 | Catálogo S01–S24 exceder a capacidade individual | Alta | Alto | 104 semanas, 8–9 h efetivas, revisão bimestral e no máximo duas skills em andamento | Coordenador | Aberto/monitorado |
| RP26 | Muitos itens iniciados e nenhum aprovado | Média | Alto | gates por onda, definição de pronto e limite de WIP | Coordenador | Mitigado no planejamento |
| RP27 | Acúmulo de papéis gerar autoaprovação de regra | Alta | Alto | separar papéis na RACI; validação humana/ata permanece externa | Coordenador/Analistas | Aberto |
| RP28 | Retrabalho por integração tardia | Média | Alto | fluxo ponta a ponta na fundação e regressão em cada onda | Coordenador | Mitigado no planejamento |
| RP29 | Plano pessoal ser confundido com licença institucional | Média | Alto | AT-02, rótulos explícitos e gate próprio de adoção | Coordenador/TI | Mitigado parcial |
| RP30 | Tier gratuito mudar ou ser encerrado | Alta | Médio | nenhum serviço gratuito é dependência crítica; revalidar antes de ativar | Coordenador | Aberto/aceito |
| RP31 | Conteúdo institucional ser enviado a API gratuita | Média | Alto | externo somente público/sintético; processamento institucional local; teste SEC | Coordenador | Aberto |
| RP32 | Protótipo pessoal ser publicado sem controles institucionais | Baixa | Alto | separar estágios; exigir autorização, identidade, suporte, licença e segurança | Autoridade/TI | Aberto |
| RP33 | Mudança normativa durante os 24 meses invalidar regras | Alta | Alto | revisão trimestral/por evento, vigência e reexecução de testes | Analistas | Aberto |
