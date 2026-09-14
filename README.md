# pgd-ocde-icmbio — Indicadores OCDE/PGD via Denodo

Consultas SQL e documentação para calcular os **12 indicadores OCDE/PGD** do ICMBio diretamente do banco PETRVS em tempo real, via Denodo (MGI/Dataprev). Sem Docker, sem ETL, sem instalação de banco de dados local.

Desenvolvido pela Coordenação de Governança (CGOV/ICMBio) no âmbito do piloto OCDE/MGI para transformação do PGD em instrumento de gestão de desempenho.

> **Para outros órgãos da APF:** este repositório pode ser reutilizado por qualquer instituição que utilize o PETRVS e tenha acesso ao Denodo do MGI/Dataprev. As queries funcionam sem modificação — basta apontar para o schema do seu órgão.

---

## 📌 Últimas atualizações

| Data | O que mudou | Onde |
| --- | --- | --- |
| 14.09.2026 | **D18 homologada e GR2 certificada:** G02 1.0.0 aprovado sem ajustes, anexo nominal autorizado somente no produto restrito e 14 alvos recertificados automaticamente. As edições finais restrita e compartilhável foram geradas com manifesto certificado; a expansão nacional continua suspensa. | [ficha G02](docs/gestao/IND_GEST_02-execucao-entregas.md) |
| 13.09.2026 | **Governança documental:** o caderno metodológico e o registro de decisões de homologação da CGOV deixam a pasta pública `docs/` e passam a ser mantidos só no acervo privado da CGOV. A documentação pública cita o identificador de cada decisão (D01…D18) e seu efeito técnico. | [Estado da homologação](#estado-da-homologação) |
| 13.09.2026 | Família **`gestao/`** reorganizada no namespace `IND_GEST_XX` (D17 ratificada): o `PT_STATUS` vira o indicador **G01 — Situação dos Planos de Trabalho**, com ficha própria e `formula_version` 4.0.0. | [índice de gestão](docs/14-status-planos-trabalho-gestores.md) · [ficha G01](docs/gestao/IND_GEST_01-situacao-planos-trabalho.md) |
| 13.09.2026 | Decisões CGOV D01–D14 implementadas: namespace `IND_OCDE_`, visão estatística do I05, dias úteis no I07/I08, dupla perspectiva no I08, média por plano no I09, `volume_suficiente` no I10/I11 e identificação nominal nos produtos internos do G01. | [Estado da homologação](#estado-da-homologação) |
| 13.09.2026 | Integração do ciclo gerencial retomável, Relatório V2 e gates de segurança. | [docs/16-skills-e-relatorio-gerencial-v2.md](docs/16-skills-e-relatorio-gerencial-v2.md) |
| 12.09.2026 | Protocolo A1–A5 automatizado com contratos, extrações atômicas, oráculos independentes, drift, diagnósticos e fixtures sintéticas sem efeito de homologação. | [docs/09-protocolo-validacao-indicadores.md](docs/09-protocolo-validacao-indicadores.md) |
| 11.09.2026 | Relatório cumulativo e anonimizado com escopos explícitos, proteção `k≥5`, supressão complementar, PDF e expansão controlada da GR2 para o nível nacional. | [docs/15-relatorio-gerencial-cumulativo-anonimizado.md](docs/15-relatorio-gerencial-cumulativo-anonimizado.md) |
| 08.09.2026 | Novo grupo de análises **`gestao/`** — acompanhamento operacional para chefias, separado dos 12 indicadores OCDE. Primeira análise: situação dos Planos de Trabalho por unidade (rascunho, aguardando assinatura, em execução, aguardando avaliação, concluído), com data/hora da última mudança de status e quem procurar. Achado: "aguardando avaliação" não existe no campo `status` do plano — vive na consolidação mensal. | [gestao/](gestao/) · [docs/14-status-planos-trabalho-gestores.md](docs/14-status-planos-trabalho-gestores.md) |
| 21.08.2026 | Documentação de como o **status** dos artefatos PGD (PE/PT) é obtido no PETRVS — status nativo do sistema vs. `periodo_status` calculado — com matriz técnica por indicador (I01–I12) e uma versão em linguagem não técnica para analistas de negócio. Corrigida uma generalização incorreta sobre a escala de notas do Eixo 4 (só I09 e I12 invertem a nota; I10 e I11 testam categoria diretamente). | [docs/07.1-estrutura-banco-dados.md §12](docs/07.1-estrutura-banco-dados.md) · [docs/07.2-status_artefatos_pgd_icmbio.md](docs/07.2-status_artefatos_pgd_icmbio.md) |
| 05.08.2026 | Nova coluna **`mesogrupo`** (agrupador organizacional intermediário, ex. "Presidência", "DIPLAN") nos 12 CSVs de indicadores, cruzando a estrutura oficial do ICMBio com o cadastro do PETRVS. Corrigido um bug em 8 scripts onde a nova coluna deslocava os avisos de qualidade pós-CSV. | `lib/estrutura_organizacional.py` |
| 24.07.2026 | Criados os 12 guias de execução via Jupyter Notebook (Opção B) — um por indicador, com a query e a tabela de períodos vigente, sem credenciais. | [ocde/indicadores/guia-jupyter/](ocde/indicadores/guia-jupyter/) |

> O histórico público está na tabela acima, nas fichas técnicas e nos commits. Deliberações da CGOV (caderno metodológico e atas) não são publicadas neste repositório.

---

## Estado da homologação

Situação em 14.09.2026. O registro contém **14 alvos** — I01 a I12, G01 e G02.
D15 e D18 foram aprovadas, D17 ratificada e D16 ajustada. Os 14 alvos estão em
`CERTIFICADO_AUTOMATICAMENTE` na GR2. A expansão nacional está suspensa até o
aceite formal do piloto CGOV.

| Alvo | `formula_version` | Decisão aplicada | Efeito |
| --- | --- | --- | --- |
| I01 | 2.0.0 | — | exposição por ciclo mantida |
| I02 | 2.0.0 | D04 | carteira ativa confirmada |
| I03 | 2.0.0 | D05 | superexecução sem teto confirmada |
| I04 | 2.0.0 | D06 | média simples confirmada |
| I05 | **3.0.0** | D07 | nova visão estatística sem identificação (`v2`) |
| I06 | 2.0.0 | D08 | "1 servidor" lido como risco, não infração |
| I07 | **3.0.0** | D09 | rateio por dias úteis; `num_planos_trabalho_alocados` |
| I08 | **3.0.0** | D09, D10 | visões dona (`v1`) e executora (`v2`) |
| I09 | **3.0.0** | D11 | média por Plano de Trabalho |
| I10, I11 | **3.0.0** | D12 | coluna `volume_suficiente` |
| I12 | 2.0.0 | D13 | uso como triagem |
| G01 | **4.0.0** | D14, D17 | nomes só nos produtos internos; universo e supressão revistos |
| G02 | **1.0.0** | D18 | histórico PE + fotografia PT; perspectivas dona e executora; anexo nominal somente restrito |

**Próximo gate institucional:** executar e obter o aceite formal do piloto CGOV;
somente nova deliberação poderá liberar a expansão nacional.
O manifesto integrado de referência tem data de execução 13/09/2026, janela
`01/07/2025–31/08/2026` e resultado global `sucesso`. A regressão associada passou
em 459 testes, com 2 skips esperados de plataforma. O G02 preserva como observação
gerencial 114 vínculos sem entrega de PE identificável.
Séries de I05, I07, I08, I09, I10 e I11
anteriores a 13.09.2026 **não são comparáveis** às atuais sem reprocessamento.

---

## Para quem não programa: como ler este projeto

Este repositório mistura três tipos de conteúdo. Se você é gestor ou analista de negócio, o que interessa está quase sempre na primeira coluna:

| Se você quer... | Vá para... |
| --- | --- |
| Entender o que cada indicador mede, sem código | [docs/08-guia-rapido-gestores.md](docs/08-guia-rapido-gestores.md) |
| Ver o contexto do piloto OCDE/PGD e por que ele existe | [docs/05-contexto-ocde-pgd.md](docs/05-contexto-ocde-pgd.md) |
| Consultar a ficha técnica de um indicador específico (I01–I12) | [docs/ocde/06-indicadores-ocde-denodo.md](docs/ocde/06-indicadores-ocde-denodo.md) |
| Pegar os números já prontos (CSV/planilha) | Pasta `artefatos_local/` — só existe no computador de quem já rodou o processo; não fica no GitHub |
| Rodar as consultas você mesmo | Seções "Início rápido" abaixo |

Tudo o que aparece como pasta com nome técnico (`lib/`, `ocde/relatorios/` etc.) é código de apoio — você não precisa abrir esses arquivos para entender os resultados.

---

## Pré-requisitos

| Ferramenta | Para quê | Como obter |
| --- | --- | --- |
| DBeaver Community | Executar as queries SQL | [dbeaver.io/download](https://dbeaver.io/download/) — gratuito |
| Acesso ao Denodo | Credenciais + IP liberado | Solicitar ao gestor responsável pelo PGD no seu órgão |
| VS Code + Python | Apenas para o Notebook Jupyter ou os scripts mensais | Opcional — só se quiser usar a Opção B ou C |

Não é necessário MySQL, Docker, PostgreSQL ou qualquer banco de dados local.

---

## Início rápido

### Para gestores (sem SQL)

Leia [docs/08-guia-rapido-gestores.md](docs/08-guia-rapido-gestores.md) — entenda os indicadores e interprete os resultados sem precisar executar código.

---

### Para analistas — Opção A: DBeaver (recomendado)

1. Configure a conexão Denodo no DBeaver seguindo [docs/03-acesso-direto-denodo-dbeaver.md](docs/03-acesso-direto-denodo-dbeaver.md) (detalhamento em [docs/04-configuracao-dbeaver.md](docs/04-configuracao-dbeaver.md))
2. Abra o índice do manual: [docs/ocde/06-indicadores-ocde-denodo.md](docs/ocde/06-indicadores-ocde-denodo.md)
3. Navegue até o indicador desejado e copie a query para um SQL Editor
4. Ajuste as datas no bloco `parametros` e execute com `Ctrl + A` > `Ctrl + Enter`

---

### Para analistas — Opção B: Jupyter Notebook no VS Code

#### Passo 1 — Clone ou baixe este repositório

```bash
git clone https://github.com/lpchagas/pgd-ocde-icmbio.git
```

Ou clique em **Code > Download ZIP** no GitHub e extraia a pasta.

#### Passo 2 — Copie o arquivo de configuração

Na pasta do projeto, localize o arquivo `.env.example`. Faça uma cópia e renomeie para `.env`:

```text
.env.example  →  .env
```

#### Passo 3 — Preencha suas credenciais

Abra o arquivo `.env` com o Bloco de Notas e preencha com as credenciais fornecidas pelo gestor responsável pelo PGD no seu órgão:

```ini
DENODO_USER=seu_cpf_aqui
DENODO_PASSWORD=sua_senha_aqui
DENODO_DRIVER_PATH=C:/Users/SEU_USUARIO/AppData/Roaming/DBeaverData/...
```

> O arquivo `.env` fica apenas no seu computador. Ele não vai para o GitHub. Sua senha nunca sai da sua máquina.

#### Passo 4 — Execute o notebook

Abra o arquivo `consultas_denodo_template.ipynb` no VS Code e execute as células em ordem.

Guia completo para quem nunca usou Python: [docs/10-jupyter-guia-iniciantes.md](docs/10-jupyter-guia-iniciantes.md)

Guia passo a passo por indicador (qual query colar, quais parâmetros ajustar, como exportar): [ocde/indicadores/guia-jupyter/](ocde/indicadores/guia-jupyter/) — um arquivo `IND_OCDE_XX_guia_jupyter.md` para cada um dos 12 indicadores.

---

### Para rotina mensal — Scripts Python sanitizados

Os scripts em `ocde/indicadores/` geram os CSVs mensais dos indicadores sem armazenar credenciais no código. Eles leem a conexão do arquivo local `.env` e salvam as saídas em `artefatos_local/` (pasta ignorada pelo git, presente só no computador de quem executa).

Exemplo:

```powershell
python ocde/indicadores/IND_OCDE_02.1_run.py --data-execucao 2026-09-13
```

Fluxo completo, calendário mensal e checklist: [docs/11-guia-extracao-mensal.md](docs/11-guia-extracao-mensal.md)

Checklist de segurança antes de publicar: [docs/12-seguranca-publicacao.md](docs/12-seguranca-publicacao.md)

---

## Indicadores disponíveis

| # | Indicador | Eixo | Documento |
| --- | --- | --- | --- |
| I01 | Proporção de servidores por regime de trabalho | 1. Trabalho Remoto | [06.1.1-i01.md](docs/ocde/06.1.1-i01.md) |
| I02 | Taxa de cumprimento das entregas por unidade | 2. Execução | [06.2.1-i02.md](docs/ocde/06.2.1-i02.md) |
| I03 | Taxa de cumprimento de metas por entrega | 2. Execução | [06.2.2-i03.md](docs/ocde/06.2.2-i03.md) |
| I04 | Índice de atingimento de metas — score médio | 2. Execução | [06.2.3-i04.md](docs/ocde/06.2.3-i04.md) |
| I05 | Distribuição das entregas entre os servidores | 3. Carga de Trabalho | [06.3.1-i05.md](docs/ocde/06.3.1-i05.md) |
| I06 | Grau de responsabilidade pelas entregas | 3. Carga de Trabalho | [06.3.2-i06.md](docs/ocde/06.3.2-i06.md) |
| I07 | Horas por entrega — planejadas (absoluto) | 3. Carga de Trabalho | [06.3.3-i07.md](docs/ocde/06.3.3-i07.md) |
| I08 | Proporção de horas por entrega — planejadas (%) | 3. Carga de Trabalho | [06.3.4-i08.md](docs/ocde/06.3.4-i08.md) |
| I09 | Média da avaliação do Plano de Trabalho por unidade | 4. Desempenho e Avaliação | [06.4.1-i09.md](docs/ocde/06.4.1-i09.md) |
| I10 | Percentual de avaliações inadequadas | 4. Desempenho e Avaliação | [06.4.2-i10.md](docs/ocde/06.4.2-i10.md) |
| I11 | Percentual de avaliações excepcionais | 4. Desempenho e Avaliação | [06.4.3-i11.md](docs/ocde/06.4.3-i11.md) |
| I12 | Coerência entre avaliação do PT e do PE | 4. Desempenho e Avaliação | [06.4.4-i12.md](docs/ocde/06.4.4-i12.md) |

Índice navegável com descrição completa de cada indicador: [docs/ocde/06-indicadores-ocde-denodo.md](docs/ocde/06-indicadores-ocde-denodo.md)

---

## Estrutura do projeto — o que cada pasta faz

A tabela abaixo descreve **todas as pastas de primeiro nível** do repositório e para que servem. As marcadas como "código" só interessam a quem programa; as demais são de interesse geral.

| Pasta | Tipo | Finalidade |
| --- | --- | --- |
| **`docs/`** | 📄 Documentação | Manual do projeto: visão geral, guia para gestores, contexto OCDE/PGD, fichas técnicas dos 12 indicadores, protocolos de validação e segurança. É o ponto de entrada para entender o "o quê" e o "porquê" — veja detalhamento abaixo. |
| **`ocde/`** | ⚙️ Código | Scripts que calculam os 12 indicadores OCDE/PGD a partir do Denodo (a iniciativa principal deste repositório). Inclui os scripts de extração mensal, os módulos de relatório gerencial e os templates de diagnóstico. |
| **`gestao/`** | ⚙️ Código | Análises de **acompanhamento operacional** para chefias de unidade — respondem "o que está travado na minha equipe hoje e quem devo procurar", diferente dos 12 indicadores OCDE, que medem desempenho agregado ao longo do tempo. Veja detalhamento abaixo. |
| **`mgi/`** | ⚙️ Código (embrionário) | Reservado para futuros indicadores solicitados diretamente pelo MGI, com prefixo `IND_MGI_XX` e janela anual (D01, D02). Hoje contém apenas a estrutura inicial. |
| **`lib/`** | ⚙️ Código | Biblioteca compartilhada usada por todos os scripts de indicadores: conexão com o Denodo, definição dos períodos de análise (mensal/trimestral/quadrimestral), limpeza e exportação de CSV, checagens automáticas de qualidade. Nada aqui precisa ser lido por quem só consome os resultados. |
| **`artefatos_local/`** | 📊 Dados (não versionado) | Onde ficam os CSVs prontos (por mês, por indicador) depois que alguém executa a extração. **Não existe no GitHub** — só no computador de quem rodou o processo e sincroniza via OneDrive. É aqui que estão as planilhas que alimentam o Power BI/COCAGE. |
| **`cgov/`** | 🔒 Privado (não versionado) | Análises internas ad hoc da Coordenação de Governança. Fica em uma pasta do OneDrive "linkada" ao projeto (Junction) — nunca é publicada no GitHub. |
| **`setup/`** | 🔒 Privado (não versionado) | Scripts de configuração do ambiente local (backup, criação dos links privados). Uso exclusivo de quem administra o repositório na própria máquina. |
| **`.claude/` / `.codex/` / `.agents/`** | 🤖 Automação | Comandos e automações ("skills") usadas pelos assistentes de IA (Claude Code, Codex, Antigravity) que ajudam a manter este projeto. Não afeta os resultados dos indicadores. |
| **`.venv/`** | ⚙️ Ambiente técnico | Ambiente Python isolado do projeto (dependências). Gerado automaticamente — nunca precisa ser aberto manualmente. |

> As pastas `cgov/` e `setup/` aparecem no Explorador de Arquivos porque são *Junctions* (atalhos do Windows) apontando para pastas do OneDrive fora do repositório Git. Elas nunca sobem para o GitHub. Detalhes em [docs/13-organizacao-publico-privado.md](docs/13-organizacao-publico-privado.md).

### Dentro de `docs/` — o manual do projeto

| Arquivo/Pasta | Conteúdo |
| --- | --- |
| [01-visao-geral.md](docs/01-visao-geral.md) | Conceito do projeto, como funciona o fluxo via Denodo, comparação com a versão anterior (datamart/ETL) |
| [03-acesso-direto-denodo-dbeaver.md](docs/03-acesso-direto-denodo-dbeaver.md) | Como conectar no Denodo usando o DBeaver |
| [04-configuracao-dbeaver.md](docs/04-configuracao-dbeaver.md) | Configuração detalhada do driver e da conexão no DBeaver |
| [05-contexto-ocde-pgd.md](docs/05-contexto-ocde-pgd.md) | Contexto do piloto OCDE/PGD, perfil do ICMBio, achados quantitativos gerais |
| [07.1-estrutura-banco-dados.md](docs/07.1-estrutura-banco-dados.md) | Dicionário das tabelas e campos do banco PETRVS usados nos cálculos, incluindo a matriz técnica de como o status de cada indicador é inferido (Seção 12) |
| [07.2-status_artefatos_pgd_icmbio.md](docs/07.2-status_artefatos_pgd_icmbio.md) | Versão em linguagem não técnica da Seção 12 acima — como o status de PE/PT é obtido, com glossário e explicação de código, para quem não programa |
| [08-guia-rapido-gestores.md](docs/08-guia-rapido-gestores.md) | **Ponto de partida para quem não programa** — o que cada indicador significa e como interpretá-lo |
| [09-protocolo-validacao-indicadores.md](docs/09-protocolo-validacao-indicadores.md) | Como cada indicador é validado (etapas A1 a A5) antes de virar dado oficial |
| [10-jupyter-guia-iniciantes.md](docs/10-jupyter-guia-iniciantes.md) | Passo a passo para usar o Notebook Jupyter sem experiência prévia em Python |
| [11-guia-extracao-mensal.md](docs/11-guia-extracao-mensal.md) | Calendário e comandos da rotina mensal de extração dos indicadores |
| [12-seguranca-publicacao.md](docs/12-seguranca-publicacao.md) | Checklist para evitar vazamento de credenciais e dados pessoais antes de publicar |
| [13-organizacao-publico-privado.md](docs/13-organizacao-publico-privado.md) | O que é público (GitHub), privado (OneDrive) e local em cada pasta |
| [14-status-planos-trabalho-gestores.md](docs/14-status-planos-trabalho-gestores.md) | Índice da família de indicadores de gestão (G01 e seguintes) e convenção `IND_GEST_XX` |
| [15-relatorio-gerencial-cumulativo-anonimizado.md](docs/15-relatorio-gerencial-cumulativo-anonimizado.md) | Rotina do relatório cumulativo: corte no mês anterior, escopos, anonimização, PDF e expansão GR2 → nacional |
| [16-skills-e-relatorio-gerencial-v2.md](docs/16-skills-e-relatorio-gerencial-v2.md) | Arquitetura das skills, extrações automatizadas e Relatório Gerencial V2 |
| `docs/ocde/` | As **fichas técnicas dos 12 indicadores** (uma por indicador) + 4 fichas de eixo + o índice geral [06-indicadores-ocde-denodo.md](docs/ocde/06-indicadores-ocde-denodo.md) |
| `docs/gestao/` | Fichas técnicas dos indicadores de gestão — [G01](docs/gestao/IND_GEST_01-situacao-planos-trabalho.md) e [G02](docs/gestao/IND_GEST_02-execucao-entregas.md) |

> Cadernos metodológicos e registros de decisão da CGOV **não ficam em `docs/`**:
> são documentos deliberativos internos. A numeração 17 e 18, antes usada por eles,
> fica vaga.
| `docs/cgov/` e `docs/mgi/` | Páginas públicas de apresentação das iniciativas CGOV e MGI (sem dados sensíveis) |

### Dentro de `ocde/` — o motor dos indicadores

| Subpasta | Conteúdo |
| --- | --- |
| `indicadores/` | Um script por indicador (`IND_OCDE_01.1_run.py` a `IND_OCDE_12.1_run.py`). Cada um se conecta ao Denodo, roda a query oficial e salva o CSV do período. |
| `indicadores/guia-jupyter/` | Guias `IND_OCDE_XX_guia_jupyter.md` (um por indicador) com o passo a passo para rodar a mesma query manualmente pelo Notebook Jupyter (Opção B), sem precisar executar o script Python. |
| `relatorios/` | Módulos que leem os CSVs já extraídos e montam análises gerenciais (classificação de desempenho, métricas agregadas, geração de relatório). |
| `diagnosticos/` | Modelo (template) usado para investigar achados inesperados de um indicador antes de fechar a validação. |

Relatório piloto GR2 de setembro/2026 (janela encerrada em 31/08/2026):

```bash
.venv/bin/python -m ocde.relatorios.relatorio_cumulativo \
  --data-execucao 2026-09-11 --regional GR2 --reextrair --salvar --pdf
```

Os CSVs detalhados da reextração ficam somente em memória durante o cálculo;
apenas produtos agregados e anonimizados são gravados em
`artefatos_local/relatorios/AAAA-MM/`.

### Dentro de `gestao/` — acompanhamento operacional das chefias

Enquanto `ocde/` mede **desempenho agregado** (como a unidade se saiu no
quadrimestre), `gestao/` responde a uma pergunta diferente e imediata: **o que
está travado na minha equipe agora e com quem eu falo para destravar.** As duas
famílias leem o mesmo banco, mas têm público, periodicidade e saída distintos.

Cada indicador de gestão tem uma subpasta `gestao/IND_GEST_XX/` e código lógico
`GXX` (D17). Convenção e roteiro para novos indicadores: [gestao/README.md](gestao/README.md).

| Código | Script | O que responde | Ficha |
| --- | --- | --- | --- |
| G01 | [`IND_GEST_01.1_run.py`](gestao/IND_GEST_01/IND_GEST_01.1_run.py) | Situação de cada Plano de Trabalho da unidade — rascunho, aguardando assinatura, em execução, aguardando avaliação ou suspenso — com há quantos dias está parado, quem fez a última mudança e qual servidor procurar | [IND_GEST_01](docs/gestao/IND_GEST_01-situacao-planos-trabalho.md) |
| G02 | [`IND_GEST_02.1_run.py`](gestao/IND_GEST_02/IND_GEST_02.1_run.py) | Execução das entregas nas perspectivas dona e executora, reconciliando histórico do PE com a fotografia dos PT | [IND_GEST_02](docs/gestao/IND_GEST_02-execucao-entregas.md) |

```powershell
python -m gestao.runner --analise todas --data-execucao 2026-09-13 --regional GR2 --produto restrito
python gestao/IND_GEST_01/IND_GEST_01.1_run.py --unidade CGGP --incluir-subordinadas
```

As saídas vão para `artefatos_local/gestao/AAAA-MM/escopos/<scope-key>/` (não versionado): um CSV de
detalhe e um painel unidade × status. Nos produtos `operacional` e `restrito`, o
detalhe **contém nome de servidores** (D14) — tratar como dado pessoal. O produto
`compartilhavel` só gera o painel, com supressão k<5 e complementar.

> **Por que não é um indicador OCDE:** os 12 indicadores medem resultado com
> período fechado e vão para a COCAGE. Os indicadores de `gestao/` são fotografias
> do estado atual, para ação imediata da chefia. Passam pelo mesmo protocolo de
> validação A1–A5, com oracle independente, mas não entram no pacote da COCAGE.
> Índice da família: [docs/14](docs/14-status-planos-trabalho-gestores.md).

---

## Ciclo de vida de um indicador (resumo)

1. **A1 — produção:** contrato e script executável do indicador.
2. **A2 — resultado:** CSV, schema, janela e manifesto com hashes.
3. **A3 — validação independente:** oráculo Python recalcula a métrica a partir de extrações atômicas.
4. **A4 — diagnóstico:** classifica divergências, drift, cobertura e riscos de privacidade.
5. **A5 — dossiê:** consolida evidências e recomenda; a homologação continua sendo decisão da CGOV.

Mudança de `formula_version` devolve o alvo a `HOMOLOGACAO_INICIAL_PENDENTE` automaticamente. Sem mudança e sem divergência, a baseline homologada passa a `CERTIFICADO_AUTOMATICAMENTE` a cada ciclo.

Protocolo completo: [docs/09-protocolo-validacao-indicadores.md](docs/09-protocolo-validacao-indicadores.md)

---

## Projeto relacionado

[DM_Petrvs_icmbio_postgre](https://github.com/lpchagas/DM_Petrvs_icmbio_postgre) — fluxo completo com ETL, datamart PostgreSQL e dashboards Apache Superset. Indicado quando o objetivo é monitoramento contínuo com visualizações prontas, em vez de análise ad hoc via SQL.
