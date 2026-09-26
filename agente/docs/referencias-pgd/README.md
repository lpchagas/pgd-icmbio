# Índice de referências do Programa de Gestão e Desempenho

**Última revisão:** 23.08.2026
**Fotografia física:** 60 artefatos, além deste índice — 51 PDF, 8 DOCX e 1 XLSX
**Conteúdo efetivo:** 55 conteúdos únicos — 37 elegíveis para análise institucional e 18 de acesso controlado
**Situação:** inventário técnico concluído; aprovação das fontes permanece pendente no I0/Q5

> [!NOTE]
> **Termos técnicos usados neste documento**
>
> - **Hash SHA-256:** uma "impressão digital" do arquivo — uma sequência fixa de caracteres
>   calculada a partir do conteúdo, usada para conferir se dois arquivos são idênticos byte a
>   byte. 📚 [O que é uma função hash — Cloudflare](https://www.cloudflare.com/learning/ssl/what-is-a-hash-function/)
> - **OCR (Optical Character Recognition / Reconhecimento Óptico de Caracteres):** tecnologia
>   que "lê" o texto dentro de uma imagem (como um PDF escaneado) e o transforma em texto
>   pesquisável e copiável.

## 1. Conclusão da auditoria

O acervo foi ampliado de forma relevante. Ele agora contém as normas centrais do PGD no
ICMBio, a versão original e a versão consolidada da IN Conjunta nº 24/2023, a IN nº
52/2023, o ato alterador nº 21/2024, os seis módulos do Guia Prático, cinco manuais do
Petrvs, cinco notas técnicas do MGI, três cadernos da Enap e três Acórdãos do TCU.

A análise integral dos formatos identificou:

- **55 conteúdos únicos**: 46 hoje localizados fora de `99_restrito/` e 9 evidências
  individuais ali segregadas;
- **18 conteúdos que devem ter acesso controlado**: 9 evidências individuais, o FAQ do
  ICMBio e 8 transcrições de plantões;
- **5 duplicidades de conteúdo**, totalizando 5 arquivos físicos excedentes;
- **4 normas em PDF de imagem**, com 22 páginas sem camada textual pesquisável; elas foram
  conferidas visualmente, mas exigem OCR controlado antes de eventual indexação;
- **9 evidências individuais**, com 26 páginas sem camada textual; não se recomenda OCR,
  pois isso criaria derivados com dados pessoais sem finalidade para o agente;
- aproximadamente **2,17 milhões de caracteres extraíveis** nos conteúdos únicos com
  camada textual, incluídas cerca de 698 mil caracteres de transcrições de reuniões.

O acervo está tecnicamente muito mais completo, mas sua organização física ainda não está
saneada. A existência de um arquivo nesta pasta **não autoriza** seu cadastro como fonte
vigente, sua indexação no RAG ou a transformação de um trecho em regra. Essas decisões são
tratadas em [`fontes-institucionais.md`](../gestao/fontes-institucionais.md) e dependem da
aprovação humana da Q5.

## 2. Como interpretar as fontes

Use a seguinte precedência:

1. **Norma vigente e aplicável**, com atenção a alterações e revogações parciais.
2. **Decisão de controle externo**, apenas no escopo da determinação ou conclusão aplicável.
3. **Orientação oficial do órgão central**, sempre confrontada com a norma vigente.
4. **Regra ou orientação institucional do ICMBio**, confirmada pela área competente.
5. **Manual de sistema**, somente para comportamento operacional da versão correspondente.
6. **Material didático, modelo ou exemplo**, sem criação autônoma de obrigação.
7. **Fala de plantão ou FAQ**, como pista para validação, nunca como fonte normativa bruta.
8. **Evidência individual**, fora do corpus do agente.

Cada regra derivada deve registrar fonte, localização precisa, natureza, vigência,
confiança e validação humana. Quando duas versões produzirem comandos diferentes, registre
o conflito; não deixe o RAG ou a LLM escolher silenciosamente.

## 3. Navegação rápida por tema

| Tema | Fontes de partida | Complementos |
| --- | --- | --- |
| Marco normativo federal | N05, N06, N07, N08 | G13–G17; Decreto nº 11.072/2022 ainda ausente do acervo local |
| PGD no ICMBio | N03, N04 | I01, I02, I04; N01 para competências |
| Seleção, participação e TCR | G04, G06, N04, N06 | G09, G12, C03, C04 |
| Plano de Entregas | G02, I02, C03, C05, C06 | G10, N04 |
| Plano de Trabalho | G05, N04, N08 | G11, C03, C07 |
| Execução, monitoramento e avaliação | N04, N08, C07 | I01, G10, G11 |
| Modalidades e teletrabalho | G06, N03, N04, N06, I04 | N02, N09, N10 |
| Transparência e governança | G03, N08, N10 | N01, N02, N09 |
| Operação do Petrvs | G08–G12 | I01, I02; conferir versão do sistema |
| Histórico e motivação normativa | G13–G17 | N05–N08 |

## 4. Catálogo dos 37 conteúdos elegíveis para decisão da Q5

O hash abreviado contém os 12 primeiros caracteres do SHA-256 e serve para conferência
rápida. O hash completo deve ser recalculado do arquivo antes do cadastro no banco.

### 4.1 Normas e controle

| Código | Documento | Papel no projeto | Formato | Hash | Acesso canônico atual |
| --- | --- | --- | --- | --- | --- |
| N01 | Portaria ICMBio nº 5.592/2025 — Regimento Interno | Estrutura, competências e responsabilidades institucionais; não é a norma central do PGD | PDF, 94 p., texto | `aa8c7f0f00fa` | [Abrir](01_normas-e-controle/portaria-icmbio-5592-2025-regimento-interno.pdf) |
| N02 | Acórdão TCU nº 2.564/2022 — Plenário | Governança e diagnóstico do teletrabalho; uso seletivo e contextual | PDF, 39 p., texto | `f450c1dc7a9e` | [Abrir](01_normas-e-controle/Acordãos%20TCU/acordao-tcu-2564-2022-teletrabalho-servico-publico.pdf) |
| N03 | Portaria ICMBio nº 2.494/2024 | Autoriza e institui o PGD no ICMBio; contém TCRs anexos; art. 4º e § 2º do art. 6º revogados por N04 | PDF, 5 p., imagem | `8258f2ecb36e` | [Abrir](<01_normas-e-controle/Normas Específicas do PGD/2024.08.21_PORTARIA ICMBIO Nº 2.494.pdf>) |
| N04 | IN ICMBio nº 14/2025 | Procedimentos atuais de participação, ciclo, execução e avaliação no Instituto | PDF, 13 p., texto | `6067431573d9` | [Abrir](<01_normas-e-controle/Normas Específicas do PGD/2025.03.17_INSTRUÇÃO NORMATIVA ICMBIO Nº 14.pdf>) |
| N05 | IN Conjunta SEGES-SGPRT/MGI nº 24/2023 — publicação original | Marco geral original do PGD; necessária para histórico de vigência | PDF, 9 p., imagem | `0e35c469ffcf` | [Abrir](<01_normas-e-controle/Normas Gerais do PGD/2023.08.28_INSTRUÇÃO NORMATIVA CONJUNTA SEGES-SGPRT-MGI Nº 24.pdf>) |
| N06 | IN Conjunta SGP-SRT-SEGES/MGI nº 52/2023 | Regras de gestão de pessoas, adicionais, banco de horas, saúde e afastamentos | PDF, 5 p., imagem | `d792a1c89c64` | [Abrir](<01_normas-e-controle/Normas Gerais do PGD/2023.12.21_INSTRUÇÃO NORMATIVA CONJUNTA SGP-SRT-SEGES-MGI Nº 52.pdf>) |
| N07 | IN Conjunta SEGES-SGP-SRT/MGI nº 21/2024 | Altera a IN nº 24/2023; importante para a linha histórica | PDF, 3 p., imagem | `b5a684734b0a` | [Abrir](<01_normas-e-controle/Normas Gerais do PGD/2024.07.16_INSTRUÇÃO NORMATIVA CONJUNTA SEGES-SGP-SRT-MGI Nº 21.pdf>) |
| N08 | IN nº 24/2023 comparada e consolidada — abril/2026 | Melhor fonte local para consulta corrente; incorpora alterações até a IN nº 137/2026 | PDF, 19 p., texto | `b54c586a60a4` | [Abrir](<01_normas-e-controle/Normas Gerais do PGD/IN do PGD (comparada e consolidada) - abr 2026.pdf>) |
| N09 | Acórdão TCU nº 526/2025 — Plenário | Auditoria sobre trabalho remoto; riscos, controles e transparência | PDF, 52 p., texto | `4d29debd0bc2` | [Abrir](<01_normas-e-controle/Acordãos TCU/Acórdão 526 de 2025 Plenário.pdf>) |
| N10 | Acórdão TCU nº 1.197/2025 — Plenário | Levantamento amplo do PGD e teletrabalho na APF; governança e resultados | PDF, 64 p., texto | `349a25036ef9` | [Abrir](<01_normas-e-controle/Acordãos TCU/Acórdão 1197 de 2025 Plenário.pdf>) |

### 4.2 Guias, manuais e notas técnicas do Governo Federal

| Código | Documento | Papel no projeto | Formato | Hash | Acesso |
| --- | --- | --- | --- | --- | --- |
| G01 | Guia Prático PGD — Módulo 1: Introdução | Autorização, instituição e fundamentos | PDF, 32 p. | `99e4d8a8c3bd` | [Abrir](<02_guias-governo-federal/01_Guia Prático PGD_Módulo 1_Introdução.pdf>) |
| G04 | Guia Prático PGD — Módulo 2: Seleção dos participantes | Seleção, modalidades e TCR | PDF, 21 p. | `5bc3a4fd5045` | [Abrir](<02_guias-governo-federal/02_Guia Prático PGD_Módulo 2_Seleção dos participantes.pdf>) |
| G02 | Guia Prático PGD — Módulo 3: Plano de Entregas | Elaboração e avaliação do Plano de Entregas | PDF, 64 p. | `9f98183478c3` | [Abrir](<02_guias-governo-federal/03_Guia Prático PGD_Módulo 3_Plano de Entregas.pdf>) |
| G05 | Guia Prático PGD — Módulo 4: Plano de Trabalho | Contribuições, carga horária e avaliação | PDF, 36 p. | `4b82c0173d9c` | [Abrir](<02_guias-governo-federal/04_Guia Prático PGD_Módulo 4_Plano de Trabalho.pdf>) |
| G06 | Guia Prático PGD — Módulo 5: Modalidades e regimes | Presencial, teletrabalho parcial/integral e exterior | PDF, 42 p. | `106684b5f3bb` | [Abrir](<02_guias-governo-federal/05_Guia Prático PGD_Módulo 5_Modalidades e regimes de execução.pdf>) |
| G07 | Guia Prático PGD — Módulo 6: Responsabilidades | Papéis dos atores e governança | PDF, 39 p. | `7c6fc191d37a` | [Abrir](<02_guias-governo-federal/06_Guia Prático PGD_Módulo 6_Responsabilidades.pdf>) |
| G08 | Manual Petrus — Regras Gerais | Comportamento operacional geral do sistema | PDF, 10 p. | `be3b4009427f` | [Abrir](<02_guias-governo-federal/Manuais PETRVS/01_Manual Petrus Regras Gerais — Portal do Servidor.pdf>) |
| G09 | Manual Petrus — Administrador Negocial | Configuração e administração negocial | PDF, 11 p. | `0cead5e25a76` | [Abrir](<02_guias-governo-federal/Manuais PETRVS/02_Manual Petrus- Administrador Negocial — Portal do Servidor.pdf>) |
| G10 | Manual Petrus — Chefia de Unidade | Fluxos de chefia e gestão dos planos | PDF, 16 p. | `044e813b21ac` | [Abrir](<02_guias-governo-federal/Manuais PETRVS/03_Manual Petrus- Chefia de Unidade — Portal do Servidor.pdf>) |
| G11 | Manual Petrus — Participante | Fluxos individuais de plano e execução | PDF, 9 p. | `c1ff9b3dcf17` | [Abrir](<02_guias-governo-federal/Manuais PETRVS/04_Manual Petrus- Participante — Portal do Servidor.pdf>) |
| G12 | Manual Petrus — Erros e Soluções | Diagnóstico operacional; conteúdo dependente da versão | PDF, 3 p. | `9f426659bd56` | [Abrir](<02_guias-governo-federal/Manuais PETRVS/05_Manual de Erros e Soluções — Portal do Servidor.pdf>) |
| G13 | Nota Técnica Conjunta nº 29/2023/MGI | Fundamentação da IN nº 52/2023 | PDF, 10 p. | `f963889deb0e` | [Abrir](<02_guias-governo-federal/Notas Técnicas MGI/NotaTcnicaConjuntaparaAtosNormativosSEIn29.2023MGI.pdf>) |
| G14 | Nota Técnica Conjunta nº 20/2023/MGI | Fundamentação da IN nº 24/2023 | PDF, 16 p. | `c5ff3be040f6` | [Abrir](<02_guias-governo-federal/Notas Técnicas MGI/SEI_35790844_Nota_Tecnica_Conjunta_para_Atos_Normativos_201.pdf>) |
| G15 | Nota Técnica Conjunta nº 9/2024/MGI | Fundamentação da IN nº 21/2024 | PDF, 6 p. | `20ac4a27430a` | [Abrir](<02_guias-governo-federal/Notas Técnicas MGI/SEI_43514551_Nota_Tecnica_Conjunta_para_Atos_Normativos_92.pdf>) |
| G16 | Nota Técnica nº 456/2024/MGI | Proposta sobre agentes contratados por tempo determinado | PDF, 7 p. | `1d4220a15ef0` | [Abrir](<02_guias-governo-federal/Notas Técnicas MGI/SEI_47179549_Nota_Tecnica_para_Atos_Normativos_4561.pdf>) |
| G17 | Nota Técnica Conjunta nº 16/2025/MGI | Fundamentação da alteração de 2025 da IN nº 24 | PDF, 8 p. | `1bc4bec9f15a` | [Abrir](<02_guias-governo-federal/Notas Técnicas MGI/SEI_53306176_Nota_Tecnica_Conjunta_para_Atos_Normativos_162.pdf>) |
| G03 | Guia para sítio de transparência do PGD | Conteúdo recomendado para transparência institucional | PDF, 4 p. | `54ca1f29a23b` | [Abrir](03_orientacoes-icmbio/GuiaparasitedetransparenciadoPGD.pdf) |

### 4.3 Orientações institucionais e materiais da Enap

| Código | Documento | Papel no projeto | Formato | Hash | Acesso |
| --- | --- | --- | --- | --- | --- |
| I01 | Entendendo o Ciclo do PGD no ICMBio | Síntese institucional do ciclo e da periodicidade | PDF, 4 p. | `39a5bae35df1` | [Abrir](03_orientacoes-icmbio/orientacao-icmbio-ciclo-pgd-2026.pdf) |
| I02 | Entenda como criar um Plano de Entregas | Orientação institucional e fluxo no Petrvs | PDF, 2 p. | `f50c5e1bd73b` | [Abrir](03_orientacoes-icmbio/orientacao-icmbio-criacao-plano-entregas-2026.pdf) |
| I04 | Diferenças entre modalidades de trabalho no ICMBio | Explicação institucional de presencial e teletrabalho | PDF, 4 p. | `bd1b51aace91` | [Abrir](<03_orientacoes-icmbio/Entenda as diferenças entre as modalidades de trabalho do PGD no ICMBio.pdf>) |
| C01 | Caderno Enap — Fundamentos do PGD | Apoio didático e histórico | PDF, 42 p. | `1b04e122cb08` | [Abrir](04_cursos-enap/01_fundamentos-pgd/caderno-curso-fundamentos-pgd-enap-2026.pdf) |
| C02 | Modelo Enap — Controle de Entregas | Exemplo didático com duas abas; não é contrato do projeto | XLSX | `709df591210c` | [Abrir](04_cursos-enap/01_fundamentos-pgd/modelo-controle-entregas-enap.xlsx) |
| C03 | Caderno Enap — Elaboração de Planos de Entrega e de Trabalho | 4Q1P, TCR, PE e PT | PDF, 45 p. | `74f6a2c52aab` | [Abrir](04_cursos-enap/02_elaboracao-planos/caderno-curso-elaboracao-planos-pgd-enap-2026.pdf) |
| C04 | Canvas de TCR | Exemplo visual, não formulário oficial do ICMBio | PDF, 1 p. | `74c7b01b2be4` | [Abrir](04_cursos-enap/02_elaboracao-planos/canvas-tcr-pgd-enap-2026.pdf) |
| C05 | Diferença entre entregas, tarefas e rotinas | Apoio à classificação de objetos de trabalho | PDF, 1 p. | `c6fee70e1478` | [Abrir](04_cursos-enap/02_elaboracao-planos/informativo-diferenca-entregas-tarefas-rotinas.pdf) |
| C06 | Qualificação de uma entrega | Checklist didático de tangibilidade, mensuração e utilidade | PDF, 1 p. | `a3e727350587` | [Abrir](04_cursos-enap/02_elaboracao-planos/informativo-qualificacao-entrega.pdf) |
| C07 | Caderno Enap — Execução e Avaliação | Registros, conceitos, recurso e reavaliação | PDF, 25 p. | `5df6ae9b0dc4` | [Abrir](04_cursos-enap/03_execucao-avaliacao/caderno-curso-execucao-avaliacao-planos-pgd-enap-2026.pdf) |

## 5. Conteúdo de acesso controlado — 18 itens

Não há links nesta seção. Os códigos identificam o conteúdo sem publicar nomes, contatos,
notas ou respostas. Nenhum desses arquivos deve integrar o RAG bruto.

| Código | Conteúdo | Quantidade | Tratamento |
| --- | --- | --- | --- |
| I03 | Perguntas e respostas do PGD no ICMBio | 1 PDF, 12 p. | Cadastrar no máximo metadados; só indexar derivado saneado e validado |
| P01–P08 | Transcrições de oito plantões de dúvidas realizados entre 1º e 4.04.2025 | 8 DOCX; cerca de 698 mil caracteres | Mover para área restrita após autorização; não usar como regra; extrair apenas perguntas frequentes anonimizadas e validadas |
| R01 | Exportação individual do Guia do Participante — Fundamentos | 1 PDF, 10 p. | Evidência individual; fora do cadastro e do RAG |
| R02–R04 | Resultados individuais — Fundamentos, módulos 1 a 3 | 3 PDFs, 2 p. cada | Evidência individual; fora do cadastro e do RAG |
| R05–R07 | Resultados individuais — Elaboração de Planos, módulos 2 a 4 | 3 PDFs, 2 p. cada | Evidência individual; fora do cadastro e do RAG |
| R08–R09 | Resultados individuais — Execução e Avaliação, módulos 1 e 2 | 2 PDFs, 2 p. cada | Evidência individual; fora do cadastro e do RAG |

As transcrições P01–P08 estão fisicamente em `03_orientacoes-icmbio/Plantões/`, fora de
`99_restrito/`. Essa localização é inadequada ao conteúdo. O PDF I03 também possui uma
cópia idêntica fora da área restrita. Esta auditoria registra o problema, mas não moveu ou
excluiu arquivos sem autorização específica.

## 6. Duplicidades confirmadas

| Conteúdo único | Cópia canônica adotada no índice | Cópia excedente | Evidência |
| --- | --- | --- | --- |
| Acórdão TCU nº 2.564/2022 | `.../acordao-tcu-2564-2022-teletrabalho-servico-publico.pdf` | `.../Acórdão 2564 de 2022 Plenário.pdf` | Texto extraído idêntico; binários diferem por empacotamento/metadados |
| Regimento Interno — Portaria nº 5.592/2025 | `01_normas-e-controle/portaria-icmbio-5592-2025-regimento-interno.pdf` | arquivo de mesmo conteúdo na raiz do acervo | SHA-256 idêntico |
| Ciclo do PGD no ICMBio | `orientacao-icmbio-ciclo-pgd-2026.pdf` | arquivo de título longo na mesma pasta | SHA-256 idêntico |
| Criação do Plano de Entregas | `orientacao-icmbio-criacao-plano-entregas-2026.pdf` | arquivo de título longo na mesma pasta | SHA-256 idêntico |
| Perguntas e respostas do PGD | cópia em `99_restrito/orientacoes-icmbio/` | cópia em `03_orientacoes-icmbio/` | SHA-256 idêntico; a cópia geral viola a classificação recomendada |

## 7. Qualidade, limites e lacunas remanescentes

- **Ausência normativa local:** o Decreto nº 11.072/2022 continua fora da pasta, embora
  seja a base legal federal citada por todo o conjunto.
- **Histórico incompleto:** a IN nº 20/2025 e a IN nº 137/2026 não estão armazenadas como
  atos autônomos. A N08 consolida seus efeitos para consulta corrente, mas não substitui os
  atos individuais para versionamento histórico artigo a artigo.
- **OCR:** N03, N05, N06 e N07 são imagens. A fonte é legível visualmente, porém o RAG não
  deve receber OCR não revisado, sobretudo em artigos, parágrafos, percentuais e prazos.
- **Atualização de sistema:** G08–G12 descrevem uma versão do Petrvs e podem divergir da
  interface atual. Devem ser usados como orientação operacional versionada.
- **Conteúdo oral:** P01–P08 contêm erros de transcrição, nomes e respostas de contexto.
  Uma fala não equivale a orientação aprovada.
- **FAQ:** I03 contém dados de contato e referências a atos anteriores. Um derivado
  anonimizado ainda exigirá revisão de vigência antes de uso.
- **Arquivos públicos com nomes de autoridades:** assinaturas e nomes publicados em atos
  oficiais não tornam a norma restrita, mas devem ser excluídos de chunks que não precisem
  deles.

## 8. Organização física observada e organização recomendada

```text
referencias-pgd/
  README.md
  01_normas-e-controle/           # normas e acórdãos
  02_guias-governo-federal/       # guias, manuais e notas técnicas
  03_orientacoes-icmbio/          # somente materiais institucionais publicáveis
  04_cursos-enap/                 # cadernos, exemplos e planilha didática
  99_restrito/
    orientacoes-icmbio/            # FAQ bruto e, após autorização, transcrições
    evidencias-formacao/           # resultados individuais
```

O saneamento recomendado é: manter uma cópia canônica de cada duplicidade, mover P01–P08
para `99_restrito/`, remover a cópia geral de I03 e normalizar nomes para ASCII/kebab-case.
Essas operações são destrutivas ou movimentam conteúdo pessoal e, portanto, exigem uma
ação separada com alvos confirmados.

## 9. Política de manutenção

Ao adicionar ou substituir uma referência:

1. confirme origem oficial, título, número, edição, publicação e vigência;
2. classifique o documento por autoridade e finalidade antes de discutir o RAG;
3. calcule SHA-256 e verifique duplicidade binária e duplicidade textual;
4. examine dados pessoais, falas, resultados individuais e informação restrita;
5. use código estável; nunca recicle um código de documento removido;
6. registre alterações e revogações artigo a artigo quando afetarem regras;
7. teste links do índice e mantenha apenas este `README.md` versionado dentro da pasta;
8. não marque `versao_confirmada = 1` nem `status = 'vigente'` sem a decisão humana da Q5.

Nunca registre neste índice credenciais, CPF, matrícula, telefone, e-mail pessoal, notas,
respostas individuais ou nomes extraídos de transcrições.
