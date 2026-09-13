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
- `ocde/relatorios/analisar_execucao_pgd.py`: leitura somente local/Denodo de
  PE, PT e atividades, preservando unidade dona e executora.
- `ocde/relatorios/textos_execucao.py`: sanitização local de nomes e dados
  pessoais e regras transparentes de prioridade.
- `ocde/relatorios/relatorio_v2.py`: relatório restrito e compartilhável,
  evidências, riscos, mitigação, tendências e apêndice I01–I12.
- `tools/skills_manager.py`: validação local, instalação idempotente, backup e
  certificação multiplataforma do catálogo opcional de assistentes.

## Regra temporal

A análise acumulada inicia em 01/07/2025 e termina no último dia do mês
anterior. A fotografia operacional é separada e recebe data/hora própria. Em
setembro/2026, o acumulado termina em 31/08/2026.

## Produtos e privacidade

O produto restrito mantém unidades, planos, entregas, atividades e textos de
negócio sanitizados, sem nomes, CPF, e-mails, telefones, endereços ou UUIDs. O
produto compartilhável aplica adicionalmente k≥5 às unidades envolvidas e
supressão quando necessária.

Textos são processados localmente. Os gatilhos de prioridade são prazo vencido
sem conclusão, meta de PE abaixo do pactuado, status operacional que requer
ação e esforço acima do planejado. Atividades de PT nunca substituem a medição
do resultado do PE.

## Execução

```text
python -m lib.indicator_extraction --data-execucao 2026-09-12 --salvar-manifesto
python -m gestao.runner --analise todas --data-execucao 2026-09-12 --lente ambas --regional GR2 --produto restrito
python -m ocde.relatorios.relatorio_v2 --data-execucao 2026-09-12 --regional GR2 --produto ambos --lente ambas --consultar-denodo --salvar --pdf
python -m lib.ciclo_gerencial --data-execucao 2026-09-12 --regional GR2 --produto ambos --lente ambas --retomar --salvar --pdf
```

No Windows, usar um Python compatível com a JVM do DBeaver. O runtime WSL não
carrega uma `jvm.dll` Windows. Quando os runtimes forem distintos, configurar
`PGD_DENODO_PYTHON` para o Python com JPype/JVM e `PGD_TEST_PYTHON` para o
Python com pytest; o preflight bloqueia o ciclo se qualquer dependência faltar.

## Gates e conclusão

O ciclo só recebe sucesso se todas as etapas concluírem. A aprovação do piloto
GR2 abre a fase nacional, que exige execução nacional, reconciliação e testes
de unidade, mesogrupo, tipo e lista arbitrária. A certificação local do catálogo de assistentes só recebe estado `certificado`
quando as ferramentas configuradas estiverem disponíveis e produzirem
descoberta/hash equivalentes. Esse controle local não participa dos checks da PR.

## Estado operacional em 13.09.2026

- A extração I01–I12 foi concluída com a janela `01/07/2025–31/08/2026`.
- O gate integrado GR2 comparou A1 e oracle para os 12 indicadores e o `PT_STATUS` (hoje G01) sem divergência bloqueante.
- Foram gerados 13 dossiês A5; todos estão em `HOMOLOGACAO_INICIAL_PENDENTE`, pois a decisão institucional não é automatizada.
- A suíte offline registrou 371 testes aprovados e 14 skips esperados de plataforma/homologação.
- O catálogo local de 33 skills passou pela validação estrutural e pela instalação idempotente; a certificação funcional externa permanece fora do escopo desta publicação.
- A auditoria pública confirmou que o código e a documentação não incorporam credenciais; o acesso ao Denodo continua restrito ao `.env` local.
- O próximo gate é a homologação inicial pela CGOV, seguida da recertificação automática, do relatório V2 GR2 e da expansão nacional.
