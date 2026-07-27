# ADR-004 — Modelo de linguagem: API direta nas fases iniciais, migração para Azure OpenAI condicionada à Q2

**Data:** registrada em v1/v2 | **Estado:** aprovada, vigente (fase atual: API direta)
**Decisor:** Coordenador do projeto (Leandro)
**Documentos:** `proposta-projeto-v1.md` §3; `proposta-projeto-v2.md` §6 e §3.2 (questão
Q2); `proposta-projeto-v3.md` — Incremento I7 ("migração do modelo para Azure OpenAI se Q2
confirmada")

> **Nota de reconstrução:** este ADR formaliza uma decisão já registrada em v1/v2, sem
> conteúdo novo. A condição de disparo (Q2) segue em aberto — ver Seção 2.4 da proposta v4.

## Contexto

O ICMBio já possui Azure/Microsoft 365 contratado, o que favorece Azure OpenAI
institucionalmente para a fase de exposição a gestores. Provisionar isso desde o início do
projeto, porém, atrasaria o aprendizado inicial com burocracia de TI.

## Decisão

- **Fases 1–3 (aprendizado, I0–I5):** usar **API comercial direta** (Anthropic ou OpenAI) —
  "setup em minutos com uma chave" e custo baixo de entrada.
- **Fases 4–5 (institucional, a partir do I6/I7):** **migrar para Azure OpenAI/AI Foundry**,
  para "aproveitar contrato e rede já homologados pelo ICMBio — menos fricção de segurança
  ao expor a gestores", condicionada à resposta da **questão Q2** ("O Azure AI Foundry está
  provisionado no tenant do ICMBio ou exige chamado ao TI?").

## Alternativas descartadas

| Alternativa | Motivo do descarte |
| --- | --- |
| Azure OpenAI desde o início | Exige burocracia de provisionamento institucional antes de começar a aprender |
| Manter API direta também na fase institucional | Não aproveita a infraestrutura de segurança/rede já homologada pelo ICMBio |
| Modelo open-source local (ex.: Llama/Hugging Face) | Custo de GPU e curva de aprendizado altos frente ao ganho, descartado como caminho principal |

## Consequências

- Classificada como **Reversível** nas fases 1–3 e **Estruturante** a partir da fase
  institucional.
- Recomendação explícita de não travar o início do projeto esperando a definição de Q2 —
  "comece com API direta... e volte a essa tabela na Fase 4/5".
- Risco associado **RP01** (matriz de riscos): atraso no provisionamento Azure pode travar
  o Incremento I7; mitigado por iniciar o processo com o TI a partir do I6.
