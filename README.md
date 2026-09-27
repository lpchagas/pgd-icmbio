# PGD-ICMBio — indicadores do Programa de Gestão e Desempenho

Cálculo, validação e documentação dos indicadores do **Programa de Gestão e Desempenho (PGD)** do ICMBio, lidos diretamente do PETRVS em tempo real via Denodo (MGI/Dataprev). Sem ETL, sem datamart e sem banco de dados local para os indicadores.

Desenvolvido pela Coordenação de Governança (CGOV/ICMBio) no âmbito do piloto OCDE/MGI/ICMBio/UFRN para transformar o PGD em instrumento de gestão de desempenho (Portaria ICMBio nº 5.592/2025).

> **Para outros órgãos da APF:** as consultas e os scripts podem ser reutilizados por qualquer instituição que use o PETRVS e tenha acesso ao Denodo do MGI/Dataprev — basta apontar para o schema do seu órgão.

> **Nome do repositório:** o projeto se chama `pgd-icmbio`. No GitHub, o endereço continua `pgd-ocde-icmbio` até a renomeação, prevista para o fim da reorganização em monorepo.

---

## O que o projeto entrega

| Família | O que mede | Onde |
| --- | --- | --- |
| **OCDE/PGD — I01 a I12** | Trabalho remoto, execução das entregas, carga de trabalho e avaliação, em janela cumulativa | [fichas](docs/ocde/06-indicadores-ocde-denodo.md) · `ocde/` |
| **Gestão — G01 e G02** | Situação dos Planos de Trabalho e execução das entregas, como fotografia para as chefias | [índice](docs/gestao/README.md) · `gestao/` |
| **Relatórios** | Relatório Gerencial V2, Relatório de Execução de Entregas e relatório cumulativo anonimizado | [V2](docs/relatorios/relatorio-v2-ciclo-gerencial.md) · [cumulativo](docs/relatorios/relatorio-cumulativo.md) · `relatorios/` |
| **Agente de gestão — S01 a S24** | Capacidades de apoio às chefias, especificadas e ainda não implementadas | [catálogo](capacidades/CATALOGO.md) · `agente/` |
| **MGI** | Indicadores solicitados pelo MGI, em janela anual | planejado (`mgi/`) |

**Situação atual:** os 12 indicadores OCDE e os dois de gestão estão homologados e aceitos nas três **unidades piloto** — CGOV, COCAGE e GR2. A expansão para além dos pilotos está suspensa até deliberação própria. O estado de cada item está no [catálogo de capacidades](capacidades/CATALOGO.md), e as mudanças, no [CHANGELOG](CHANGELOG.md).

---

## Para quem não programa: por onde começar

| Se você quer... | Vá para... |
| --- | --- |
| Entender o que cada indicador mede, sem código | [Guia rápido para gestores](docs/indicadores/guia-rapido-gestores.md) |
| Ver o contexto do piloto OCDE/PGD e por que ele existe | [Contexto OCDE/PGD](docs/projeto/contexto-ocde-pgd.md) |
| Conhecer o projeto e sua evolução | [Visão geral e marcos](docs/projeto/visao-geral.md) |
| Consultar a ficha técnica de um indicador | [Índice das fichas I01–I12](docs/ocde/06-indicadores-ocde-denodo.md) · [G01](docs/gestao/IND_GEST_01-situacao-planos-trabalho.md) · [G02](docs/gestao/IND_GEST_02-execucao-entregas.md) |
| Saber como um indicador vira dado oficial | [Protocolo de validação A1–A5](docs/indicadores/protocolo-validacao.md) |
| Entender o piloto nas três unidades | [Fluxo das unidades piloto](docs/projeto/fluxo-unidades-piloto.md) |
| Pegar os números prontos (CSV, relatórios) | Não ficam no GitHub: estão na pasta privada da equipe (`artefatos_local/`) |

Pastas com nome técnico (`lib/`, `relatorios/`, `tools/` etc.) são código de apoio — não é preciso abri-las para entender os resultados.

---

## Pré-requisitos

| Ferramenta | Para quê | Como obter |
| --- | --- | --- |
| DBeaver Community | Executar as consultas manualmente | [dbeaver.io/download](https://dbeaver.io/download/) — gratuito |
| Acesso ao Denodo | Credenciais individuais e IP liberado pelo Dataprev | Solicitar ao gestor responsável pelo PGD no seu órgão |
| Python 3.12 ou superior | Scripts mensais, validação e relatórios | Opcional para quem só usa o DBeaver |

---

## Início rápido

### Para gestores (sem SQL)

Leia o [guia rápido para gestores](docs/indicadores/guia-rapido-gestores.md): o que cada indicador significa e como interpretar os resultados, sem executar código.

### Para analistas — opção A: DBeaver (recomendado)

1. Configure a conexão Denodo no DBeaver seguindo o guia de [acesso ao Denodo e DBeaver](docs/ambiente/acesso-denodo-dbeaver.md) (detalhes em [configuração do DBeaver](docs/ambiente/configuracao-dbeaver.md)).
2. Abra o [índice das fichas](docs/ocde/06-indicadores-ocde-denodo.md) e escolha o indicador.
3. Copie a consulta para um SQL Editor, ajuste as datas no bloco `parametros` e execute.

### Para analistas — opção B: Jupyter Notebook

1. Clone o repositório:

   ```bash
   git clone https://github.com/lpchagas/pgd-ocde-icmbio.git
   ```

2. Copie `.env.example` para `.env` e preencha suas credenciais. O `.env` fica só no seu computador e nunca vai para o GitHub.
3. Abra `consultas_denodo_template.ipynb` no VS Code e execute as células em ordem.

Guia para quem nunca usou Python: [Jupyter para iniciantes](docs/ambiente/jupyter.md). Passo a passo por indicador: [`ocde/indicadores/guia-jupyter/`](ocde/indicadores/guia-jupyter/).

### Para a rotina mensal — scripts Python

Os scripts leem a conexão do `.env` local e gravam as saídas na pasta privada `artefatos_local/`. Sempre informe a data de execução: a janela de análise é calculada a partir dela.

```powershell
python -m tools.executar_pilotos --capacidade ocde --data-execucao AAAA-MM-DD --modo real --validar
python -m lib.ciclo_gerencial --data-execucao AAAA-MM-DD --regional GR2 --produto ambos --lente ambas --salvar --pdf
```

- Calendário, comandos e checklist: [guia da extração mensal](docs/indicadores/extracao-mensal.md).
- Recortes permitidos e liberação de produtos: [fluxo das unidades piloto](docs/projeto/fluxo-unidades-piloto.md).
- Antes de publicar qualquer coisa: [checklist de segurança](docs/ambiente/seguranca-publicacao.md).

---

## Indicadores disponíveis

| # | Indicador | Eixo | Ficha |
| --- | --- | --- | --- |
| I01 | Proporção de servidores por regime de trabalho | 1. Trabalho remoto | [06.1.1](docs/ocde/06.1.1-i01.md) |
| I02 | Taxa de cumprimento das entregas por unidade | 2. Execução | [06.2.1](docs/ocde/06.2.1-i02.md) |
| I03 | Taxa de cumprimento de metas por entrega | 2. Execução | [06.2.2](docs/ocde/06.2.2-i03.md) |
| I04 | Índice de atingimento de metas — score médio | 2. Execução | [06.2.3](docs/ocde/06.2.3-i04.md) |
| I05 | Distribuição das entregas entre os servidores | 3. Carga de trabalho | [06.3.1](docs/ocde/06.3.1-i05.md) |
| I06 | Grau de responsabilidade pelas entregas | 3. Carga de trabalho | [06.3.2](docs/ocde/06.3.2-i06.md) |
| I07 | Horas planejadas por entrega (absoluto) | 3. Carga de trabalho | [06.3.3](docs/ocde/06.3.3-i07.md) |
| I08 | Proporção de horas por entrega (%) | 3. Carga de trabalho | [06.3.4](docs/ocde/06.3.4-i08.md) |
| I09 | Média da avaliação do Plano de Trabalho por unidade | 4. Desempenho e avaliação | [06.4.1](docs/ocde/06.4.1-i09.md) |
| I10 | Percentual de avaliações inadequadas | 4. Desempenho e avaliação | [06.4.2](docs/ocde/06.4.2-i10.md) |
| I11 | Percentual de avaliações excepcionais | 4. Desempenho e avaliação | [06.4.3](docs/ocde/06.4.3-i11.md) |
| I12 | Coerência entre avaliação do PT e do PE | 4. Desempenho e avaliação | [06.4.4](docs/ocde/06.4.4-i12.md) |
| G01 | Situação dos Planos de Trabalho | Gestão | [IND_GEST_01](docs/gestao/IND_GEST_01-situacao-planos-trabalho.md) |
| G02 | Execução das Entregas | Gestão | [IND_GEST_02](docs/gestao/IND_GEST_02-execucao-entregas.md) |

A versão vigente de cada fórmula está no contrato (`lib/validation_contracts.py`) e na ficha. Mudanças de versão maior ou menor sinalizam quebra de série e são registradas no [CHANGELOG](CHANGELOG.md).

---

## Estrutura do projeto

| Pasta | Tipo | Finalidade |
| --- | --- | --- |
| **`docs/`** | 📄 Documentação | Manual do projeto, organizado por assunto (detalhes abaixo) |
| **`ocde/`** | ⚙️ Código | Scripts A1 dos 12 indicadores OCDE (`ocde/indicadores/`), guias Jupyter e modelo de diagnóstico |
| **`gestao/`** | ⚙️ Código | Indicadores de gestão para chefias (`IND_GEST_XX`), com registro e executor próprios. Roteiro para novos indicadores: [gestao/README.md](gestao/README.md) |
| **`mgi/`** | ⚙️ Código (reservado) | Futuros indicadores do MGI (`IND_MGI_XX`), em janela anual |
| **`relatorios/`** | ⚙️ Código | Relatório V2, relatório cumulativo, escopos e privacidade. `ocde/relatorios/` guarda só pontes temporárias de compatibilidade |
| **`lib/`** | ⚙️ Código | Núcleo compartilhado: conexão com o Denodo, períodos, calendário, escopos, liberação, extração e validação A1–A5 |
| **`agente/`** | ⚙️ Código | Base local do agente de gestão (MySQL), versões, sincronização e backup |
| **`capacidades/`** | 📋 Catálogo | [Catálogo de capacidades](capacidades/CATALOGO.md), especificações S01–S24 e protótipos |
| **`config/`** | ⚙️ Configuração | Cadastro das unidades piloto, conciliações, lock das instruções, ocorrências de auditoria já revisadas |
| **`tools/`** | ⚙️ Código | Auditoria de segurança, pilotos, aceites, baseline, replay, links, sincronia das instruções e skills |
| **`tests/`** | ✅ Testes | Suíte automatizada, que nunca acessa o Denodo nem o MySQL de produção ([tests/README.md](tests/README.md)) |
| `CLAUDE.md`, `AGENTS.md`, `PROJECT.md` | 🤖 Instruções | Instruções para os assistentes de programação (Claude Code, Codex e Antigravity), com núcleo comum sincronizado ([como editar](docs/governanca-projeto/sincronia-instrucoes.md)) |
| `artefatos_local/`, `cgov/`, `setup/`, `.agents/`, `.claude/`, `.codex/` | 🔒 Privado | Pastas locais ligadas à pasta privada da equipe; nunca vão para o GitHub ([organização público-privado](docs/ambiente/organizacao-publico-privado.md)) |

### Dentro de `docs/`

| Pasta | Conteúdo |
| --- | --- |
| [`docs/projeto/`](docs/projeto/visao-geral.md) | Visão geral e marcos, contexto OCDE/PGD, fluxo das unidades piloto, glossários |
| [`docs/ambiente/`](docs/ambiente/organizacao-publico-privado.md) | Acesso ao Denodo e DBeaver, Jupyter, banco local do agente, organização público-privado, segurança de publicação |
| [`docs/dados-petrvs/`](docs/dados-petrvs/estrutura-banco-dados.md) | Estrutura do banco PETRVS, status dos planos em linguagem de negócio, esquema do banco do agente |
| [`docs/indicadores/`](docs/indicadores/guia-rapido-gestores.md) | Guia para gestores, protocolo de validação A1–A5, extração mensal, lições técnicas |
| [`docs/ocde/`](docs/ocde/06-indicadores-ocde-denodo.md) e [`docs/gestao/`](docs/gestao/README.md) | Fichas técnicas dos indicadores |
| [`docs/relatorios/`](docs/relatorios/relatorio-v2-ciclo-gerencial.md) | Relatório V2, ciclo gerencial e relatório cumulativo |
| [`docs/agente/`](docs/agente/README.md) | Proposta, metodologia e recursos do agente de gestão |
| [`docs/decisoes/`](docs/decisoes/registro-decisoes-projeto.md) | Registro de decisões do projeto e ADRs |
| [`docs/governanca-projeto/`](docs/governanca-projeto/riscos.md) | Riscos, fontes institucionais, validação do modelo comum, sincronia das instruções |

> Cadernos metodológicos, atas e registros de decisão da CGOV **não ficam em `docs/`**: são documentos deliberativos, mantidos no acervo privado. A documentação pública cita só o identificador da decisão (D01, D02…) e o efeito técnico.

---

## Ciclo de vida de um indicador

1. **A1 — produção:** contrato e script executável do indicador.
2. **A2 — resultado:** CSV, schema, janela e manifesto com hashes.
3. **A3 — validação independente:** oráculo Python recalcula a métrica a partir de extrações atômicas.
4. **A4 — diagnóstico:** classifica divergências, drift, cobertura e riscos de privacidade.
5. **A5 — dossiê:** consolida as evidências. A homologação é decisão da CGOV, e a liberação fora dos pilotos exige aceite humano e deliberação de expansão.

Mudar a `formula_version` devolve o alvo a `HOMOLOGACAO_INICIAL_PENDENTE`. Sem mudança e sem divergência, a baseline homologada passa a `CERTIFICADO_AUTOMATICAMENTE` a cada ciclo. Protocolo completo: [docs/indicadores/protocolo-validacao.md](docs/indicadores/protocolo-validacao.md).

---

## Projeto relacionado

[DM_Petrvs_icmbio_postgre](https://github.com/lpchagas/DM_Petrvs_icmbio_postgre) — fluxo com ETL, datamart PostgreSQL e dashboards Apache Superset, indicado para monitoramento contínuo com visualizações prontas.
