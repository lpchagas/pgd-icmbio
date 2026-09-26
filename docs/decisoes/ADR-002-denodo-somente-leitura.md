# ADR-002 — Acesso ao PETRVS somente leitura via Denodo; o agente não escreve no PETRVS

**Data:** registrada na proposta v2, reafirmada em v3 e v4 | **Estado:** aprovada, vigente
**Decisor:** Coordenador do projeto (Leandro)
**Documentos vigentes:** [Proposta v6](../agente/projeto-v6/00_proposta-projeto-v6.md) e
[arquitetura](../agente/projeto-v6/02-arquitetura-tecnologia-dados.md)

> **Nota de reconstrução:** este ADR formaliza uma restrição de governança já registrada
> como decisão explícita nas propostas v2/v3, sem conteúdo novo.

## Contexto

O agente acessa o PETRVS via Denodo (virtualização de dados, consulta em tempo real sem
cópia) para os indicadores OCDE/PGD e para os objetos reais do ICMBio (unidades,
servidores, entregas). Era necessário deixar explícito o limite de atuação do agente sobre
o sistema de origem, tanto por governança quanto por segurança de dados institucionais.

## Decisão

O agente **não escreve no PETRVS**. Acesso somente leitura, reforçado no escopo do projeto
e na credencial de acesso ao Denodo utilizada pela aplicação. No escopo formal (v2 §2.3 /
v3 §2.3): "escrita de dados no PETRVS (o agente **não altera** planos nem avaliações)" fica
**fora do escopo do MVP**; qualquer inclusão futura exigiria nova versão da proposta.

## Alternativas descartadas

| Alternativa | Motivo do descarte |
| --- | --- |
| Escrever no próprio PETRVS/Denodo | Denodo é somente leitura por natureza; escrita no PETRVS está explicitamente fora do escopo (v3 §2.3). Reafirmado no ADR-006 como motivo do descarte da alternativa equivalente para o modelo comum |

## Consequências

- **Positivas:** reforça a transparência com os usuários — a interface deve declarar que o
  agente é "apoio à consulta e à redação, não ferramenta de decisão automatizada"; a
  credencial de acesso ao Denodo é o mecanismo técnico de enforcement (não depende só de
  disciplina de código).
- **Negativas/custos:** qualquer objeto que o agente precise "criar" (entregas, versões,
  vínculos OKR-D, riscos) precisa de um destino de escrita próprio — o que motivou o modelo
  comum de dados (ADR-001/ADR-006) como camada de persistência separada do PETRVS.
