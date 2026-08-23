# Documentação do projeto

**Última revisão:** 23.08.2026

Este índice orienta a leitura dos artefatos em `docs/`. O documento de planejamento
vigente continua sendo [`proposta-projeto-v5.md`](../proposta-projeto-v5.md); os arquivos
desta pasta detalham decisões, fontes, riscos, validações e tecnologia.

## Trilha de leitura para analistas de negócio

Se você não tem formação técnica e está abrindo esta pasta pela primeira vez, leia nesta
ordem:

1. **Glossário institucional** ([`gestao/glossario-institucional.md`](gestao/glossario-institucional.md)) — comece pelo vocabulário do PGD, antes de qualquer outro documento.
2. **Catálogo de fontes** ([`referencias-pgd/README.md`](referencias-pgd/README.md)) — veja quais normas e guias sustentam o projeto.
3. **Fontes institucionais e decisão Q5** ([`gestao/fontes-institucionais.md`](gestao/fontes-institucionais.md)) — entenda que decisão está pendente e por quê.
4. **Validação do modelo comum** ([`gestao/validacao-modelo-comum.md`](gestao/validacao-modelo-comum.md)) — veja como os nomes do sistema se conectam ao vocabulário que você já aprendeu no passo 1.
5. **Riscos** ([`gestao/riscos.md`](gestao/riscos.md)) — veja o que pode dar errado e o que já foi mitigado.

Quem precisa de vocabulário de tecnologia (IA, RAG, infraestrutura) usa o
[`gestao/glossario-tecnico.md`](gestao/glossario-tecnico.md); quem vai mexer no código ou no
banco de dados segue para a linha de tecnologia da tabela abaixo.

## Por onde começar

| Necessidade | Documento |
| --- | --- |
| Entender o acervo PGD e localizar uma fonte | [`referencias-pgd/README.md`](referencias-pgd/README.md) |
| Decidir quais fontes entram no cadastro ou no RAG | [`gestao/fontes-institucionais.md`](gestao/fontes-institucionais.md) |
| Consultar termos de negócio do PGD | [`gestao/glossario-institucional.md`](gestao/glossario-institucional.md) |
| Consultar termos técnicos de IA e infraestrutura | [`gestao/glossario-tecnico.md`](gestao/glossario-tecnico.md) |
| Validar nomes do modelo de dados com analistas | [`gestao/validacao-modelo-comum.md`](gestao/validacao-modelo-comum.md) |
| Acompanhar riscos do projeto | [`gestao/riscos.md`](gestao/riscos.md) |
| Entender o modelo MySQL e o PETRVS | [`tecnologia/AT-01_analise-petrvs-esquema-mysql_v1.md`](tecnologia/AT-01_analise-petrvs-esquema-mysql_v1.md) |
| Reutilizar padrões do projeto de indicadores OCDE | [`tecnologia/referencia-pgd-ocde-icmbio.md`](tecnologia/referencia-pgd-ocde-icmbio.md) |

## Governo e decisões

As decisões arquiteturais estão em [`gestao/decisoes/`](gestao/decisoes/):

- ADR-001 registra a decisão histórica de SQLite;
- ADR-002 confirma Denodo somente leitura;
- ADR-003 define a arquitetura do agente;
- ADR-004 registra o modelo de linguagem;
- ADR-005 define a stack de RAG;
- ADR-006 substitui SQLite por MySQL 8 local;
- ADR-007 ainda está pendente e deverá formalizar as decisões da proposta v5.

As atas reais de validação devem ser registradas em `gestao/atas/`. A ausência de ata não
pode ser substituída por um texto gerado: Q5 e a validação formal do modelo continuam
pendentes até reunião e aprovação humanas.

## Estado da Trilha N do I0

| Entregável | Estado em 23.08.2026 | Próxima evidência |
| --- | --- | --- |
| Levantamento de fontes institucionais (Q5) | Auditoria técnica ampliada concluída; 55 conteúdos únicos; Q5 não aprovada | decisão fonte a fonte e ata |
| Glossário institucional | Revisado com normas primárias presentes no acervo | validação pelos analistas |
| Validação do modelo comum | Quadro campo a campo atualizado | reunião e ata formal |

## Regras de manutenção

- Atualize o documento mais específico e crie links nos demais; evite copiar inventários.
- Preserve códigos estáveis de fontes, riscos e decisões.
- Diferencie estado atual, estado-alvo e decisão pendente.
- Ao citar um documento do catálogo (`referencias-pgd/README.md`), referencie o código (ex.:
  N03) em vez de repetir descrição, formato ou hash — essa tabela é a única fonte para esses
  dados.
- Termos técnicos usados em documentos de negócio (`gestao/`) devem ter uma caixa `> [!NOTE]`
  explicativa na primeira aparição, com um link "saiba mais" quando possível.
- Não publique credenciais, dados pessoais, transcrições brutas ou evidências individuais.
- Depois de uma mudança relevante, releia links, números, datas, identificadores e o
  estado do projeto em `AGENTS.md`.
