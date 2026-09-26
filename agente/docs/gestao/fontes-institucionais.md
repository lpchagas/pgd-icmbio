# Fontes institucionais do PGD — classificação e proposta de decisão da Q5

**Última revisão:** 23.08.2026
**Situação:** preparação técnica ampliada — **Q5 ainda não aprovada**
**Responsável pela decisão:** coordenação e analistas da CGGE/ICMBio
**Inventário do acervo:** [`docs/referencias-pgd/README.md`](../referencias-pgd/README.md)
**Vínculo v6:** [Segurança, privacidade e fontes](../projeto-v6/06-seguranca-privacidade-fontes.md)

> [!NOTE]
> **Termos técnicos usados neste documento**
>
> - **RAG (Retrieval-Augmented Generation / Geração Aumentada por Recuperação):** técnica em
>   que a IA busca trechos de documentos relevantes antes de responder, em vez de confiar só
>   no que aprendeu previamente — assim a resposta pode citar a fonte exata.
>   📚 [O que é RAG — AWS](https://aws.amazon.com/what-is/retrieval-augmented-generation/)
> - **Chunk:** pedaço de um documento, cortado em tamanho menor, que o RAG indexa e recupera
>   individualmente — não o documento inteiro de uma vez.
> - **Hash SHA-256:** uma "impressão digital" do arquivo — uma sequência fixa de caracteres
>   calculada a partir do conteúdo, usada para conferir se dois arquivos são idênticos byte a
>   byte. 📚 [O que é uma função hash — Cloudflare](https://www.cloudflare.com/learning/ssl/what-is-a-hash-function/)
> - **OCR (Optical Character Recognition / Reconhecimento Óptico de Caracteres):** tecnologia
>   que "lê" o texto dentro de uma imagem (como um PDF escaneado) e o transforma em texto
>   pesquisável e copiável.

## 1. Conclusão executiva

A revisão ampliada muda a conclusão técnica anterior. O acervo não tem mais como lacunas a
Portaria ICMBio nº 2.494/2024, a IN ICMBio nº 14/2025, as INs Conjuntas nº 24/2023,
nº 52/2023 e nº 21/2024, os módulos 2, 4, 5 e 6 do Guia Prático ou os Acórdãos TCU
nº 526/2025 e nº 1.197/2025. Esses documentos agora estão presentes e foram analisados.

O conjunto possui **55 conteúdos únicos**:

- **37 candidatos a cadastro** em `fontes_institucionais`: N01–N10, G01–G17,
  I01–I04 e C01/C03–C07;
- **1 exemplo operacional (C02)** a manter fora da carga inicial;
- **8 transcrições de plantões (P01–P08)** a manter fora do cadastro e do RAG bruto;
- **9 evidências individuais (R01–R09)** a excluir permanentemente do corpus do agente.

Entre os 37 candidatos, I03 deve receber **somente metadados** enquanto não existir versão
saneada e validada. Os demais não estão automaticamente aprovados: devem iniciar como
`status = 'pendente_validacao'` e `versao_confirmada = 0`.

A lacuna normativa local de prioridade máxima passou a ser o **Decreto nº 11.072/2022**.
Para versionamento histórico completo, também faltam os atos autônomos IN nº 20/2025 e IN
nº 137/2026, embora seus efeitos estejam incorporados à versão consolidada N08.

**Recomendação:** aprovar tecnicamente a classificação e o plano de uso; não encerrar a Q5
até que haja (a) confirmação humana de versão e vigência, (b) saneamento de privacidade,
(c) OCR revisado das normas em imagem, (d) decisão fonte a fonte e (e) ata formal.

## 2. Escopo e método

Foram usados cinco controles:

1. inventário físico por formato, tamanho, página e SHA-256;
2. extração textual integral de 51 PDFs e 8 DOCX, sem publicar dados pessoais extraídos;
3. inspeção visual das 22 páginas das quatro normas sem camada textual;
4. inspeção estrutural e visual da planilha C02, com duas abas e campos didáticos de
   entrega, tipo, prioridade, mês, responsável e anotações;
5. conferência do marco atual nos portais oficiais do ICMBio, Portal do Servidor/MGI,
   Presidência da República e TCU em 23.08.2026.

As fontes oficiais confirmam que o PGD do ICMBio foi instituído pela Portaria nº
2.494/2024 e é atualmente regido, no Instituto, pela IN ICMBio nº 14/2025. O Portal do
Servidor lista como vigentes o Decreto nº 11.072/2022, a IN nº 24/2023 consolidada, suas
alterações nº 21/2024, nº 20/2025 e nº 137/2026 e a IN nº 52/2023.

Links de conferência:

- [PGD no ICMBio — página institucional](https://www.gov.br/icmbio/pt-br/acesso-a-informacao/governanca-e-gestao-de-pessoas/programa-de-gestao-e-desempenho-pgd)
- [Legislação do PGD — Portal do Servidor/MGI](https://www.gov.br/servidor/pt-br/assuntos/programa-de-gestao/nova-in-2023/legislacao)
- [IN nº 24/2023 consolidada em abril de 2026](https://www.gov.br/servidor/pt-br/assuntos/programa-de-gestao/nova-in-2023/legislacao/in-24-ajustada.pdf/view)
- [Decreto nº 11.072/2022 — Presidência da República](https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2022/decreto/d11072.htm)
- [Acórdão TCU nº 1.197/2025 — texto integral](https://pesquisa.apps.tcu.gov.br/doc/acordao-completo/1197/2025/Plen%C3%A1rio)

## 3. Regras de classificação no modelo comum

### 3.1 Documento, regra e trecho recuperável são objetos distintos

`fontes_institucionais` registra o documento, origem, hash e situação. O tipo técnico
disponível no esquema é `portaria`, `instrucao_normativa`, `regimento`, `cadeia_valor`,
`metodologia` ou `outro`.

`regras_institucionais_versoes` registra proposições derivadas, com uma das naturezas:
`norma`, `regra_institucional`, `recomendacao` ou `exemplo`. Um guia que cita uma norma não
se transforma em norma; a proposição normativa deve apontar também para a fonte primária.

Um chunk do RAG é apenas uma unidade de recuperação. Ele não deve mudar a natureza da
fonte nem decidir vigência. A resposta final precisa citar a localização humana — artigo,
parágrafo, seção ou página — e não somente o chunk.

### 3.2 Exemplos de tratamento

| Conteúdo | Fonte | Natureza possível | Regra de uso |
| --- | --- | --- | --- |
| Definição de participante ou entrega | N04/N08 | `norma` | Extrair do artigo vigente e validar a redação |
| Periodicidade operacional adotada no ICMBio | I01 | `regra_institucional` | Confirmar autoria, data e compatibilidade com N04 |
| Perguntas para diferenciar tarefa de entrega | C05 | `recomendacao` ou `exemplo` | Pode apoiar S03, sem linguagem de obrigação |
| Passo de navegação no Petrvs | G08–G12 | `recomendacao` operacional | Registrar versão/data do manual e conferir interface atual |
| Resposta dada em um plantão | P01–P08 | nenhuma, enquanto bruta | Transformar apenas após anonimização, síntese e validação institucional |

### 3.3 Condições gerais de carga

- usar `status = 'pendente_validacao'` e `versao_confirmada = 0` antes da ata;
- guardar o SHA-256 completo recalculado, não apenas a impressão abreviada do índice;
- não preencher `documento_substituido_id` quando a mudança for parcial;
- versionar regras com vigências próprias quando um artigo for alterado;
- registrar divergências em `regras_conflitos`;
- escrever somente pela camada de serviço prevista para S01/S02, nunca por INSERT manual;
- manter fonte primária e material interpretativo ligados, sem fundir suas autoridades.

## 4. Matriz de decisão por conjunto

Os nomes completos de cada código estão no catálogo ([`referencias-pgd/README.md`](../referencias-pgd/README.md) §4); esta tabela traz somente as colunas de decisão, para não duplicar a descrição.

| Códigos | `tipo_documento` | Regras deriváveis | Cadastro | RAG | Proposta para Q5 |
| --- | --- | --- | --- | --- | --- |
| N03–N08 | `portaria` / `instrucao_normativa` | `norma` | Sim | Sim, após OCR/validação quando aplicável | **Aprovar condicionadamente** como núcleo normativo; N04 revoga o art. 4º e o § 2º do art. 6º de N03 |
| N01 | `regimento` | `norma` para competências | Sim | Seletivo | **Aprovar** para estrutura e competência, não como norma central do PGD |
| N02, N09, N10 | `outro` | `norma` apenas para comando aplicável; `recomendacao` para achados | Sim | Seletivo por tema | **Aprovar com escopo controlado** |
| G01, G02, G04–G07 | `metodologia` | `recomendacao` / `exemplo` | Sim | Sim | **Aprovar como orientação oficial**, subordinada às normas |
| G08–G12 | `outro` | `recomendacao` operacional | Sim | Coleção separada | **Condicionar** à identificação de versão e data |
| G13–G17 | `outro` | `recomendacao` interpretativa; contexto de norma | Sim | Seletivo | **Aprovar como histórico e motivação**, nunca como substituto do ato final |
| G03 | `outro` | `recomendacao` | Sim | Sim | **Aprovar**, confrontando obrigações com N08 |
| I01, I02, I04 | `metodologia` | `regra_institucional` / `recomendacao` | Sim | Sim, após confirmação | **Condicionar** à validação pela área responsável e à data de referência |
| I03 | `metodologia` | somente após saneamento e revisão de vigência | Metadados | Não, enquanto bruto | **Cadastrar metadados; não indexar o original** |
| C01, C03, C07 | `metodologia` | `recomendacao` / `exemplo` | Sim | Sim, peso inferior | **Aprovar como apoio didático** |
| C04–C06 | `outro` | `exemplo` / `recomendacao` | Sim | Sim, baixa prioridade | **Aprovar como exemplos**, não como formulários oficiais |
| C02 | `outro` | `exemplo` | Não inicialmente | Não | **Manter como apoio local**, sem confundir com contrato Pydantic ou modelo comum |
| P01–P08 | — | — | Não | Não | **Excluir do corpus bruto**; permitir apenas derivados anonimizados e aprovados |
| R01–R09 | — | — | Não | Não | **Excluir permanentemente do corpus e do cadastro** |

### Síntese quantitativa

- núcleo normativo e de controle: **10 fontes**;
- orientação federal, operação e motivação normativa: **17 fontes**;
- orientação institucional: **4 fontes**, uma delas restrita ao nível de metadados;
- material Enap cadastrável: **6 fontes**;
- total de candidatos a cadastro: **37**;
- fora da carga inicial: C02, P01–P08 e R01–R09.

## 5. Arquitetura recomendada do RAG

| Camada | Conteúdo | Filtro obrigatório | Comportamento esperado |
| --- | --- | --- | --- |
| A — normativa corrente | N03, N04, N06, N08 e Decreto nº 11.072 quando incorporado | vigência, artigo e validação humana | responder obrigações e conceitos com citação precisa |
| B — histórico normativo | N05, N07 e atos autônomos nº 20/2025 e nº 137/2026 quando obtidos | intervalo de vigência | explicar evolução; não sobrescrever versão anterior |
| C — institucional | I01, I02, I04 e N01 | autoria, data e competência | apresentar explicitamente como regra/orientação do ICMBio |
| D — orientação oficial e didática | G01–G07, G03, C01, C03–C07 | vínculo com norma primária | explicar método, exemplos e boas práticas |
| E — sistema | G08–G12 | versão do Petrvs | responder operação, sem criar regra de negócio |
| F — controle e motivação | N02, N09, N10, G13–G17 | tema e escopo | oferecer contexto, riscos e racional regulatório |

**Fora do RAG:** C02, I03 bruto, P01–P08 e R01–R09.

### Requisitos de preparação

1. segmentar normas por artigo/parágrafo e preservar cabeçalho do ato;
2. segmentar guias por módulo/seção e marcar `natureza = recomendacao`;
3. manter os manuais em coleção operacional com versão explícita;
4. excluir assinaturas, rodapés repetitivos, contatos e cabeçalhos sem valor semântico;
5. revisar manualmente o OCR de números, percentuais, prazos e remissões;
6. testar recuperação de conflitos e de normas alteradas;
7. exigir citação de localização e sinalização da natureza em toda resposta.

## 6. Lacunas e pendências remanescentes

### 6.1 Prioridade zero para a Q5

| Item | Situação em 23.08.2026 | Evidência de fechamento |
| --- | --- | --- |
| Decreto nº 11.072/2022 no acervo local | Ausente; versão oficial vigente confirmada no Planalto | PDF/HTML oficial preservado, hash e código estável |
| Confirmação de origem e versão | Arquivos presentes, mas nem todos têm URL/edição registrada no nome | ficha fonte a fonte com URL, data e responsável |
| OCR de N03, N05, N06 e N07 | PDFs são imagens; inspeção visual concluída | texto revisado contra as 22 páginas e ligado ao hash do original |
| Privacidade de I03 e P01–P08 | Originais contêm contatos, nomes ou fala livre; P01–P08 estão fora da área restrita | arquivos segregados e decisão sobre derivados |
| Aprovação humana | Não realizada | ata em `docs/gestao/atas/` |

### 6.2 Prioridade um para versionamento e qualidade

- incorporar os textos autônomos da IN nº 20/2025 e da IN nº 137/2026;
- registrar versão/data dos manuais G08–G12 e conferir compatibilidade com o Petrvs atual;
- eliminar as cinco cópias excedentes depois de autorização e validação dos alvos;
- normalizar nomes físicos sem quebrar os códigos estáveis;
- produzir FAQ derivado de I03/P01–P08 somente com perguntas gerais, sem nomes, contatos
  ou afirmações não confirmadas em fonte aprovada.

## 7. Roteiro de decisão para fechar a Q5

### Preparação técnica

- [ ] Incorporar o Decreto nº 11.072/2022 e registrar origem/hash.
- [ ] Confirmar versão, publicação, vigência e URL de N01–N10.
- [ ] Produzir e revisar OCR de N03, N05, N06 e N07.
- [ ] Segregar P01–P08 e remover a duplicata geral de I03, após autorização.
- [ ] Definir a versão de referência dos manuais G08–G12.
- [ ] Preparar uma linha de decisão para cada um dos 37 candidatos.

### Decisões humanas

- [ ] Aprovar, condicionar ou rejeitar cada fonte candidata.
- [ ] Confirmar autoria e validade institucional de I01, I02, I03 e I04.
- [ ] Confirmar precedência e natureza permitida para cada conjunto.
- [ ] Autorizar as coleções e os filtros do RAG.
- [ ] Aprovar política de retenção de P01–P08 e R01–R09.
- [ ] Registrar conflitos normativos ou operacionais ainda abertos.

### Evidência de encerramento

- [ ] Registrar ata real em `docs/gestao/atas/`.
- [ ] Alterar este documento de “proposta” para “aprovado”, citando a ata.
- [ ] Atualizar o índice do acervo e o checklist do I0.
- [ ] Somente após a ata, promover fontes para `vigente` e marcar
  `versao_confirmada = 1` quando a persistência de S01 estiver disponível.

Este documento, isoladamente, não conclui a Q5 nem o aceite da Trilha N.

## 8. Critérios de aceite da carga futura

Uma fonte só poderá entrar em produção quando:

- o SHA-256 conferir com o original aprovado;
- a versão e a vigência forem conhecidas;
- a classificação documental e a natureza das regras estiverem aprovadas;
- dados pessoais desnecessários tiverem sido removidos dos chunks;
- o OCR, quando existente, tiver sido revisado;
- pelo menos uma consulta positiva e uma consulta de conflito forem testadas;
- a resposta recuperar título, localização e natureza corretos;
- a decisão humana estiver ligada à execução de carga.
