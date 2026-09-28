# Validação do modelo comum — nomenclatura do sistema × vocabulário do PGD

**Última revisão:** 23.08.2026
**Situação:** quadro atualizado após auditoria de 55 conteúdos únicos; ata ainda pendente
**Vínculo v6:** [Arquitetura, tecnologia e dados](../agente/projeto-v6/02-arquitetura-tecnologia-dados.md)

> **Status:** quadro de trabalho para a reunião de validação formal do modelo comum pelos
> analistas — terceiro item da pendência de **Trilha N** do Incremento I0. Este documento
> **não substitui a ata de validação**: é o insumo que permite à reunião ser objetiva, campo a
> campo, em vez de uma leitura corrida do esquema. Feche o item do checklist de aceite do I0
> ("Ata de aprovação formal do modelo pelos analistas") registrando a ata no
> acervo privado (`artefatos_local/validacao/`) depois da reunião.
>
> **Bases comparadas:** o esquema de `docs/dados-petrvs/esquema-mysql-agente.md`
> §5 (= `agente/dados/schema.sql`, 21 tabelas) contra o vocabulário consolidado em
> `docs/projeto/glossario-institucional.md`. A revisão agora inclui fontes primárias do
> ICMBio e do MGI, os seis módulos do Guia Prático, manuais do Petrvs, notas técnicas,
> materiais Enap e Acórdãos do TCU. Transcrições e evidências individuais não fundamentam
> equivalência terminológica.
>
> **Legenda de veredito:** ✅ equivalência direta e confirmada pelas fontes · 🟡 equivalência
> parcial ou nomenclatura divergente — validar redação/rótulo com os analistas · 🔵 conceito
> genuinamente novo do sistema, sem termo correspondente no PGD oficial — validar se a
> ausência é aceitável ou se merece um nome mais próximo do vocabulário PGD.

> [!NOTE]
> **Termos técnicos usados neste documento**
>
> - **Tabela e campo (banco de dados):** uma tabela é como uma planilha dentro do banco de
>   dados — cada linha é um registro e cada coluna é um **campo**. `entregas_versoes.demandante`,
>   por exemplo, é o campo "demandante" dentro da tabela "entregas_versoes".
> - **ENUM:** um campo que só aceita um valor de uma lista fixa predefinida (ex.: o campo
>   `forma_geracao` só aceita "projeto" ou "processo" — nunca outro texto).
> - **JSON:** formato de texto estruturado para guardar dados organizados (pares de
>   "campo: valor"), usado quando um campo precisa guardar uma informação mais complexa do
>   que um único valor.
> - **Chave estrangeira (FK):** campo de uma tabela que aponta para o registro correspondente
>   em outra tabela, ligando as duas (ex.: uma entrega "aponta" para a unidade que a demandou).
>
> 📚 Saiba mais: [Conceitos básicos de bancos de dados relacionais — Oracle](https://www.oracle.com/database/what-is-a-relational-database/)

## 1. Configuração institucional — S01/S02

| Tabela/campo | Conceito no PGD oficial | Veredito | Observação |
| --- | --- | --- | --- |
| `fontes_institucionais` | Sem termo único equivalente — corresponde ao catálogo de normas e documentos de apoio | 🟡 | O nome é claro, mas o corpus ampliado expôs limitação em `tipo_documento`: Acórdão, guia, manual e nota técnica caem em `outro` ou `metodologia`. Decidir se o MVP aceita essa agregação ou se será criado `subtipo_documento`/enum ampliado antes da carga |
| `regras_institucionais` / `..._versoes` | Sem termo único no PGD — mais próximo de "regra"/"norma" genérica | 🔵 | Campo `natureza` ENUM('norma','regra_institucional','recomendacao','exemplo') implementa diretamente a distinção que RP03 exige; validar com analistas se os quatro rótulos cobrem os casos reais das fontes (ex.: uma "recomendação" do Guia Prático vs. uma "norma" da IN 24/2023) |
| `regras_conflitos` | Sem equivalente — conceito de governança do agente, não do PGD | 🔵 | Não requer validação de nomenclatura institucional |

## 2. Portfólio — S03/S04/S05/S06

| Tabela/campo | Conceito no PGD oficial | Veredito | Observação |
| --- | --- | --- | --- |
| `entregas_candidatas.classificacao` ENUM('entrega','objetivo','atividade','tarefa','responsabilidade') | **Entrega**, **Objetivo**, **Atividade** e **Tarefa** são objetos de trabalho reconhecíveis; **responsabilidade** é um dever/papel | ✅ / 🟡 | O corpus ampliado usa “responsabilidade” em 32 documentos, mas nunca como a mesma espécie de objeto que entrega/atividade/tarefa. Confirmar se S03 pretende detectar uma frase de atribuição (“compete a...”) e, nesse caso, considerar nome mais explícito como `atribuicao_responsabilidade` |
| `entregas` (cabeçalho) / `entregas_versoes` (payload) | **Plano de Entregas** → item individual = **Entrega** | ✅ | Padrão cabeçalho+versões é decisão de engenharia (regra de ouro 2), não terminologia institucional — não gera conflito |
| `entregas_versoes.demandante` | **Demandante** — "indivíduo, setor ou instância que solicita a entrega" | ✅ | Nome e definição idênticos à IN 24/2023 (citada em M3/ELAB) |
| `entregas_versoes.destinatario` | **Destinatário** — "beneficiário ou usuário da entrega" | ✅ | Idem |
| `entregas_versoes.meta` (JSON, ciclo atual) e `.meta_final` (JSON, meta do fim da entrega) | **Meta** — "quantidade ou percentual" | 🟡 | O PGD oficial tem **um único conceito** de meta; o sistema o desdobra em dois campos (`meta` do ciclo × `meta_final`) para mitigar o RP04 ("meta confundir esforço com resultado; meta × progresso"). É uma extensão deliberada do modelo, não uma tradução literal — **documentar explicitamente para os analistas que essa distinção é do sistema, não da norma**, para não ser lida como divergência de nomenclatura |
| `entregas_versoes.forma_geracao` ENUM('projeto','processo') | **Forma de geração — Projeto / Processo** | ✅ | Nome e valores idênticos ao Guia Módulo 3 |
| `entregas_versoes.natureza_resultado` ENUM('produto','servico') | **Natureza do resultado — Produto / Serviço** | ✅ | Idem |
| `entregas_versoes.prazo_inicio` / `.prazo_fim` | **Prazo** | ✅ | — |
| `entregas_versoes.progresso_esperado` | **Progresso esperado** | ✅ | Nome idêntico ao termo do Guia Módulo 3 |
| `entregas_versoes.criterios_aceite` | O corpus normativo usa **critérios para avaliação das contribuições** no Plano de Trabalho; não define “critério de aceite” da entrega | 🟡 | “Critério de aceite” continua sendo refinamento metodológico do agente. Não renomear automaticamente para “critérios de avaliação”, pois isso misturaria avaliação do PT com qualidade/aceitação da entrega; decidir rótulo e explicar a diferença na interface |
| `entregas.estado` ENUM('rascunho','em_validacao','publicada','arquivada') | Sem equivalente — é o estado de workflow do rascunho dentro do agente, anterior à pactuação real no Petrvs | 🔵 | Não conflita com o PGD porque descreve um momento que só existe no agente (antes de a entrega existir formalmente no Plano de Entregas) |
| `entregas.petrvs_entrega_id` / `.petrvs_catalogo_id` | Ponte para `planos_entregas_entregas` / `entregas` reais do Petrvs | ✅ | Nomenclatura de integração, não de negócio — sem conflito |

## 3. Viabilidade / capacidade — S07/S08

| Tabela/campo | Conceito no PGD oficial | Veredito | Observação |
| --- | --- | --- | --- |
| `planos_capacidade` | Sem termo institucional equivalente — mais próximo de uma visão agregada, por unidade, dos Planos de Trabalho | 🔵 | O próprio AT-01 (§2.3, item 3) já registra isso como "sem equivalente direto" no PETRVS. Sugestão para a validação: confirmar com os analistas se "capacidade" é um nome que a CGOV reconhece, ou se um nome como "consolidação de força de trabalho da unidade" comunicaria melhor |
| `participantes.carga_horaria` + `.forma_contagem` ENUM('HORAS','DIAS') | **Carga Horária Disponível (CHD)** | ✅ | Conceito e granularidade (horas/dias) equivalentes aos da FAQ/ELAB |
| `participantes.rotulo` (pseudônimo) | Sem termo institucional — é controle de LGPD do sistema (v3 §11), não do PGD | 🔵 | Não requer validação de nomenclatura institucional, só confirmação de que o pseudônimo não aparece em nenhuma saída nominal (RP06/RP24) |
| `indisponibilidades` | **Afastamento** — "evento planejado (férias, licenças) — não é intercorrência" | ✅ | Nome do sistema é mais genérico que o termo oficial; confirmar com analistas se "indisponibilidade" deve ficar restrito a afastamentos oficiais ou também cobrir outros bloqueios de agenda não normatizados |
| `alocacoes.esforco_perc` | **Distribuição percentual da carga horária** | ✅ | Espelha `planos_trabalhos_entregas.forca_trabalho` do Petrvs — terminologia consistente nos dois lados |

## 4. Estratégia e riscos — S09/S10

| Tabela/campo | Conceito no PGD oficial | Veredito | Observação |
| --- | --- | --- | --- |
| `okrd_objetivos`, `okrd_resultados_chave`, `vinculos_okrd` | **Nenhuma ocorrência de “OKR” ou “OKR-D” foi encontrada nos 55 conteúdos únicos auditados** | 🔵 | OKR-D é metodologia importada pelo agente. O Petrvs possuir tabelas de OKR não transforma o conceito em vocabulário normativo do PGD; toda saída deve rotulá-lo como método e evitar aparência de obrigação |
| `vinculos_okrd.tipo_contribuicao` / `.forca_contribuicao` / `.justificativa` | Sem termo institucional equivalente | 🔵 | `justificativa` como campo `NOT NULL` implementa a mitigação do RP07 (nunca afirmar causalidade) — arquitetura correta, só falta nome institucional para os analistas reconhecerem o conceito de "vínculo" |
| `registros_risco.tipo` ENUM('risco','impedimento','dependencia','restricao') | Sem termo institucional — vocabulário de gestão de projetos/riscos, não do PGD | 🔵 | Nenhuma das fontes fala de "registro de risco" como prática do PGD; é uma prática que o agente introduz para apoiar a unidade. Não é errado, mas os analistas devem estar cientes de que é um acréscimo do agente, não um instrumento do ciclo do PGD |

## 5. Governança transversal (S/execução do agente)

| Tabela/campo | Conceito no PGD oficial | Veredito | Observação |
| --- | --- | --- | --- |
| `execucoes_skill`, `decisoes_humanas`, `perguntas_pendentes`, `schema_migracoes` | Sem equivalente — são tabelas de governança interna do agente (regras de ouro 3–5) | 🔵 | Não fazem parte do domínio de negócio do PGD; não precisam de validação de nomenclatura institucional, só de confirmação de que os analistas entendem sua função de auditoria/rastreabilidade |
| `decisoes_humanas.decisao` ENUM('aprovado','rejeitado','ajustado','justificado') | Ecoa vagamente a **Avaliação do Plano de Entregas/Trabalho** (que também usa aprovação/homologação) | 🟡 | Confirmar que não há confusão entre "decisão humana sobre uma sugestão do agente" e "avaliação formal de um Plano de Entregas/Trabalho no Petrvs" — são processos paralelos e não devem se misturar nas saídas do agente |

## 6. Referência — espelhos do Denodo

| Tabela/campo | Conceito no PGD oficial | Veredito | Observação |
| --- | --- | --- | --- |
| `ref_unidades` | **Unidade de Execução** / **Unidade Instituidora** | ✅ | `executora` (booleano) distingue os dois papéis institucionais corretamente |
| `ref_usuarios.participa_pgd` | **Participante** vs. agente público em geral | ✅ | O PGD distingue "agente público" (universo elegível) de "participante" (aderiu via TCR); o flag `participa_pgd` implementa exatamente essa distinção |

## 7. Síntese para a reunião de validação

**Confirmar sem ressalva (✅):** a nomenclatura do núcleo de portfólio (`entregas_versoes` —
demandante, destinatário, forma de geração, natureza do resultado, progresso esperado) e de
capacidade (CHD, distribuição percentual) já reflete o vocabulário oficial do PGD com boa
fidelidade — é o resultado mais forte desta validação.

**Decidir em reunião (🟡 — 5 pontos):**
1. `entregas_candidatas.classificacao = 'responsabilidade'` — termo existente, mas de
   natureza diferente dos demais rótulos; manter, renomear ou separar?
2. `meta` × `meta_final` — confirmar que a equipe entende como extensão do sistema (mitigação
   RP04), não como termo oficial duplicado.
3. `criterios_aceite` — manter o nome de engenharia e explicar a distinção em relação aos
   “critérios para avaliação das contribuições” do Plano de Trabalho?
4. `decisoes_humanas` × avaliação formal do Petrvs — reforçar que são processos paralelos nas
   saídas do agente.
5. `fontes_institucionais.tipo_documento` — aceitar `outro` para Acórdão/manual/nota técnica
   no MVP ou criar subtipo controlado antes da carga da Q5?

**Registrar como decisão consciente (🔵 — não é erro, é escopo do agente):** `planos_capacidade`,
OKR-D, `registros_risco` e as tabelas de governança introduzem vocabulário que não existe no
PGD oficial porque cobrem funções que o PGD normativo não prevê (capacidade agregada,
estratégia por OKR, gestão de risco, auditoria do próprio agente). O ponto para a ata não é
"corrigir" esses nomes, e sim registrar formalmente que a equipe está ciente de que são
extensões — para que nenhuma saída do agente as apresente como se fossem instrumentos oficiais
do PGD (mesmo espírito do RP03).
