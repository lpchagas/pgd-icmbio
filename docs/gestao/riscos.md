# Matriz de riscos — pgd-agente-icmbio

> Extraída da Seção 10 ("Matriz de riscos consolidada") de `proposta-projeto-v4.md`.
> Este arquivo é o registro ativo de acompanhamento (Entregável de Gestão do Incremento
> I0); a proposta permanece a fonte normativa — em caso de divergência, ela prevalece.
> Atualize a coluna **Status** conforme os riscos forem mitigados, materializados ou
> encerrados; não edite o histórico de identificação (RP01–RP15) sem registrar o motivo.

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
| RP09 | Escopo crescer ("já que estamos fazendo…") | Alta | Alto | S11–S20 fora do MVP; inclusão exige v5 | Coordenador | Aberto |
| RP10 | Dependência de pessoa única | Alta | Alto | ADRs, specs em Markdown, tutoriais, pareamento; ciclo de vida com papéis explícitos | Todos | Mitigado parcial (ADRs 001-006 registrados) |
| RP11 | Equipe não absorver o papel de ED/QA | Média | Alto | RC6 mede autonomia; passos 1–4 do ciclo são não técnicos | Coordenador | Aberto |
| RP12 | Credencial vazar em repositório | Baixa | Alto | `.gitignore` desde o dia zero (inclui `.env` com credenciais MySQL); verificação pré-push | Coordenador | Mitigado (.gitignore ativo) |
| RP13 | Integrações perderem histórico/IDs | Média | Alto | Triggers de imutabilidade no banco (AT-01 §6.3) — nem script com bug sobrescreve histórico; teste RC4/INT-T01 | Coordenador | Mitigado (triggers testados em produção local, 26.07.2026) |
| RP14 | Custo de API sair do controle | Baixa | Baixo | Limite mensal no provedor (Tutorial T3) | Coordenador | Aberto |
| RP15 | Indisponibilidade ou corrupção do serviço MySQL local travar o trabalho | Baixa | Médio | `mysqldump` diário para pasta com backup (padrão `backup.ps1`); script de reinstalação + `schema.sql` versionado permitem reconstruir o ambiente em horas | Coordenador | Mitigado (tarefa agendada `pgd_agente_backup` ativa; dumps confirmados) |

## Risco de ambiente identificado em 26.07.2026 (adicional, fora da matriz original)

| ID | Risco | Probabilidade | Impacto | Mitigação | Responsável | Status |
| --- | --- | --- | --- | --- | --- | --- |
| RP16 | Máquina de desenvolvimento sem rota de rede para o Denodo institucional impede `sincronizar_ref.py` de popular `ref_unidades`/`ref_usuarios` | Alta (confirmada) | Alto (bloqueia D2, aceite do I0 e todo o Incremento I5) | Executar a sincronização de uma máquina com VPN/rede institucional ativa; documentar o procedimento de rede exigido | Coordenador | **Aberto — bloqueia aceite do I0** |
