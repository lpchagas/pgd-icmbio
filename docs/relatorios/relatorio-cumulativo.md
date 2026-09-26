# Relatório gerencial cumulativo e anonimizado

## Finalidade

Este fluxo oferece à Gerência Regional Nordeste (GR2) e, depois do piloto,
ao ICMBio uma visão integrada de Planos de Entregas (PE), Planos de Trabalho
(PT), atividades, consolidações, avaliações, transições e indicadores I01–I12.
O produto é gerencial e agregado: não é uma avaliação individual.

## Regra temporal única

`lib/periodos.py` é a fonte canônica. `analysis_window(data_execucao)` fixa o
início em `01/07/2025` e calcula o fim como o último dia do mês anterior no
fuso `America/Sao_Paulo`. A execução falha se o fim anteceder a base.

Exemplo obrigatório:

```text
data_execucao = 2026-09-11
inicio        = 2025-07-01
fim           = 2026-08-31
mes_execucao  = 2026-09
```

PE usa trimestres em 2025 e quadrimestres a partir de 2026; PT usa trimestres
em 2025 e meses a partir de 2026. Cada ciclo possui fim programado, fim efetivo
e estado `encerrado` ou `parcial_no_corte`. Ciclos iniciados após o corte são
excluídos. Em setembro/2026, portanto, Q3-2026 e M09-2026 não aparecem.

Campos atuais de progresso de PE não reconstroem, por si, o estado que existia
na data de corte. Em ciclo parcial, I02–I04 ficam indisponíveis até que o
histórico de progressos seja identificado e validado; eventos confiáveis são
filtrados pela própria data. Correções retroativas dentro da janela são aceitas
como estado observado na data/hora de extração.

## Instalação

No WSL (necessário para que `--reextrair` use memória volátil):

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-report.txt
```

Para testes, use `requirements-dev.txt`.

## Execução do piloto GR2

Prévia sem gravação e sem Denodo:

```bash
.venv/bin/python -m ocde.relatorios.relatorio_cumulativo \
  --data-execucao 2026-09-11 --regional GR2
```

Execução completa, reextraindo do Denodo e gerando Markdown, CSVs, manifesto e
PDF:

```bash
.venv/bin/python -m ocde.relatorios.relatorio_cumulativo \
  --data-execucao 2026-09-11 --regional GR2 --reextrair --salvar --pdf
```

`--reextrair` executa I01–I12 em uma área temporária em memória (`/dev/shm` no WSL). Quando a JVM é executada pelo Python Windows, defina `PGD_VOLATILE_TMP` para a rota UNC do mesmo tmpfs. Os CSVs detalhados, que podem conter identificadores necessários à
deduplicação, são apagados ao final. Permanecem apenas:

- relatório Markdown e PDF;
- painel acumulado anonimizado;
- painel temporal anonimizado;
- execução agregada de PE/PT, atividades, consolidações e eventos;
- manifesto de reprodução e validação.

Os produtos ficam em `artefatos_local/relatorios/AAAA-MM/` e nunca devem ser
versionados. A pasta representa o mês da execução; o manifesto separa
`mes_execucao`, `periodo_analise_inicio`, `periodo_analise_fim` e
`data_hora_extracao`.

## Seletores mutuamente exclusivos

Use exatamente um:

```text
--escopo nacional
--regional GR2
--unidade SIGLA
--mesogrupo NOME
--tipo-unidade TIPO
--lista-unidades ARQUIVO
```

O filtro é exato e nunca retorna silenciosamente aos dados nacionais. A lista
aceita TXT ou CSV com uma sigla por linha. O caminho local do arquivo não é
gravado no manifesto.

## Fontes e semântica

O painel integra I01–I12 e uma extração adicional, agregada no banco, de:

- `planos_entregas`, `planos_entregas_entregas` e histórico de progressos;
- `planos_trabalhos` e `planos_trabalhos_entregas`;
- `atividades` aceitas quando distribuição, início ou entrega cai na janela; horas planejadas seguem a distribuição e horas despendidas/conclusão seguem a entrega;
- `planos_trabalhos_consolidacoes` pelo período, `data_conclusao` e `data_avaliacao` vinculada;
- `status_justificativas` pela data do evento.

As consultas não selecionam nomes, e-mail, CPF, descrições, justificativas,
afastamentos, ocorrências, recursos ou checklists. Status sem histórico só é usado como estado observado na extração quando o plano já terminou até o corte; para planos que ultrapassam o corte, esse estado fica fora do cálculo retroativo. Atividade concluída é medida
de processo; cumprimento da meta continua sendo calculado nos campos do PE.

## Protocolo LGPD

- Identificadores de servidor existem somente em memória para deduplicação.
- Nenhum UUID, pseudônimo ou trajetória individual integra os produtos.
- Toda métrica ligada a pessoas exige pelo menos cinco pessoas distintas.
- Em I09–I12, a cobertura é calculada sobre os servidores efetivamente avaliados, e não sobre todo o quadro do escopo. Usa-se a maior cobertura distinta comprovada em uma única unidade e ciclo como limite inferior conservador; não se somam unidades nem ciclos, pois uma pessoa pode aparecer em mais de um grupo. A célula também exige ao menos cinco avaliações. Nenhum identificador usado nessa contagem é persistido.
- Grupos pequenos são elevados ao agregado superior; se isso não resolver,
  ficam suprimidos.
- Quando a publicação de total e subtotais permitir diferença, os detalhes são
  retirados (supressão complementar conservadora).
- Contagens são faixas; percentuais têm uma casa decimal.
- Datas individuais viram mês, ciclo ou faixa.
- Markdown, CSV, JSON e texto do PDF são varridos para CPF, e-mail, UUID e
  campos proibidos antes de registrar sucesso.
- Cada edição requer reavaliação de combinações raras e comparação longitudinal.

O controlador e o encarregado devem revisar a primeira edição. Marque as duas
revisões somente depois de concluídas:

```text
--registrar-validacao-gerencial --registrar-validacao-lgpd
```

## Expansão e critério de conclusão

O estado privado `artefatos_local/relatorios/expansao_status.json` começa em
`piloto_gr2`. Uma GR2 tecnicamente válida, com as duas revisões, muda a fase
para `expansao_nacional_obrigatoria`; não conclui o projeto.

Depois, executar e reconciliar o nacional:

```bash
.venv/bin/python -m ocde.relatorios.relatorio_cumulativo \
  --data-execucao 2026-09-11 --escopo nacional --reextrair --salvar --pdf \
  --aprovar-nacional --reconciliar-nacional
```

Por fim, executar ao menos uma vez os quatro seletores: unidade, mesogrupo,
tipo de unidade e lista arbitrária. O projeto somente recebe
`projeto_concluido=true` quando GR2, nacional, reconciliação e os quatro
seletores estiverem aprovados.

## Testes e bloqueios

```bash
.venv/bin/python -m pytest -q
```

A suíte cobre setembro/2026, virada de ano, fevereiro bissexto, truncamento,
exclusão de Q3/M09, `k<5`, supressão complementar, ausência de fallback de
escopo e a máquina de estados da expansão. A execução também falha se qualquer
linha divulgada ultrapassar a janela registrada no manifesto.
