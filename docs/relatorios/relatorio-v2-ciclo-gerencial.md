# Catálogo de skills e Relatório Gerencial V2

## Objetivo

Este documento público registra a arquitetura implementada para automatizar as
extrações OCDE e de gestão e produzir o Relatório Gerencial V2. Os contratos
públicos abaixo são suficientes para compreender e testar o ciclo. Catálogos de
assistentes mantidos em áreas locais privadas são opcionais e não constituem
fonte indispensável nem gate da integração contínua.

## Componentes canônicos

- `lib/indicator_extraction.py`: runner oficial I01–I12, janela única,
  checksums e manifesto.
- `gestao/registry.py`: registro explícito de análises de gestão homologadas.
- `gestao/runner.py`: execução por lente, escopo e produto.
- `lib/ciclo_gerencial.py`: ciclo retomável com gates bloqueantes.
- `relatorios/analisar_execucao_pgd.py`: leitura somente local/Denodo de
  PE, PT e atividades, preservando unidade dona e executora.
- `relatorios/textos_execucao.py`: sanitização local de nomes e dados
  pessoais e regras transparentes de prioridade.
- `relatorios/relatorio_v2.py`: relatório restrito e compartilhável,
  evidências, riscos, tendências, apêndice I01–I12 e capítulo dinâmico de gestão.
- `gestao/IND_GEST_02/IND_GEST_02.1_run.py`: G02 e seus produtos; o renderizador
  consome A2/manifestos certificados e não repete consultas nem fórmulas.
- `tools/skills_manager.py`: validação local, instalação idempotente, backup e
  certificação multiplataforma do catálogo opcional de assistentes.

## Regra temporal

A análise acumulada inicia em 01/07/2025 e termina no último dia do mês
anterior. A fotografia operacional é separada e recebe data/hora própria. Em
setembro/2026, o acumulado termina em 31/08/2026.

## Produtos e privacidade

O relatório restrito mantém unidades, planos, entregas, atividades e textos de
negócio sanitizados. O anexo nominal G02 é um artefato separado e restrito, com
nome e identificador interno autorizados pela D18, mas sem CPF, e-mail, telefone
ou endereço. O produto compartilhável não contém identificação pessoal e aplica
k≥5 às unidades/entregas envolvidas e supressão complementar.

Textos são processados localmente. Os gatilhos de prioridade são prazo vencido
sem conclusão, meta de PE abaixo do pactuado, status operacional que requer
ação e esforço acima do planejado. Atividades de PT nunca substituem a medição
do resultado do PE.

## Execução

```text
python -m lib.indicator_extraction --data-execucao 2026-09-13 --regional GR2 --salvar-manifesto
python -m gestao.runner --analise todas --data-execucao 2026-09-13 --lente ambas --regional GR2 --produto restrito
python -m relatorios.relatorio_v2 --data-execucao 2026-09-13 --regional GR2 --produto ambos --lente ambas --manifesto-validacao <manifesto.json> --salvar --pdf
python -m lib.ciclo_gerencial --data-execucao 2026-09-13 --regional GR2 --produto ambos --lente ambas --retomar --salvar --pdf
```

No Windows, usar um Python compatível com a JVM do DBeaver. O runtime WSL não
carrega uma `jvm.dll` Windows. Quando os runtimes forem distintos, configurar
`PGD_DENODO_PYTHON` para o Python com JPype/JVM e `PGD_TEST_PYTHON` para o
Python com pytest; o preflight bloqueia o ciclo se qualquer dependência faltar.

## Gates e conclusão

O ciclo só recebe sucesso se todas as etapas concluírem. Os produtos finais e
compartilháveis são liberados só nas unidades piloto (CGOV, COCAGE e GR2); além
delas, o gate de liberação exige aceites e deliberação de expansão, hoje suspensa
(D16) — ver o [fluxo das unidades piloto](../projeto/fluxo-unidades-piloto.md). A edição final exige todos os alvos ativos certificados, com data e
escopo coerentes. `--rascunho` continua reservado a material privado não homologado;
não pode ser registrado como edição final. A certificação local do catálogo de assistentes só recebe estado `certificado`
quando as ferramentas configuradas estiverem disponíveis e produzirem
descoberta/hash equivalentes. Esse controle local não participa dos checks da PR.

## Registro histórico: estado operacional em 14.09.2026

> Fotografia da primeira edição final (GR2, sede regional). A situação atual está no
> [catálogo de capacidades](../../capacidades/CATALOGO.md) e no [CHANGELOG](../../CHANGELOG.md).

- A extração I01–I12 foi concluída com a janela `01/07/2025–31/08/2026`.
- O manifesto integrado vigente é `20260914T071359-f2e1a481`, com data de execução
  13/09/2026 e `status_global=sucesso`.
- O gate integrado GR2 comparou A1 e oracle para I01–I12, G01 e G02 sem divergência bloqueante.
- O registro contém 14 alvos; todos foram recertificados automaticamente na GR2.
- A D18 homologou o G02 1.0.0 e autorizou seu anexo nominal exclusivamente restrito.
- O G02 processou 2.454 registros atômicos e 341 linhas no oracle; 114 vínculos sem
  entrega identificável permanecem como alerta cadastral não bloqueante.
- A suíte offline registrou 459 testes aprovados e 2 skips esperados de plataforma.
- O catálogo local de 33 skills passou pela validação estrutural e pela instalação idempotente; a certificação funcional externa permanece fora do escopo desta publicação.
- A auditoria pública confirmou que o código e a documentação não incorporam credenciais; o acesso ao Denodo continua restrito ao `.env` local.
- I01–I12 e G01 foram recertificados após D15; G02 foi registrado separadamente e
  recertificado após D18. As edições finais da GR2 foram geradas com o manifesto
  dos 14 alvos. O próximo gate é o piloto CGOV; a expansão nacional continua
  suspensa até seu aceite formal e nova deliberação.
