# Visão Geral do Projeto

## Para quem é este documento

Este documento é para **qualquer perfil** — gestores, analistas ou equipe técnica. Se você é gestor e quer entender os indicadores sem SQL, comece pelo [guia rápido para gestores](../indicadores/guia-rapido-gestores.md).

---

## 1. O que é o PGD-ICMBio

Este projeto (`pgd-icmbio`; no GitHub, `pgd-ocde-icmbio` até a renomeação) reúne as **consultas, os scripts e a documentação** para calcular e validar os **indicadores do PGD do ICMBio** diretamente dos dados originais do PETRVS, sem nenhuma transformação intermediária:

- os **12 indicadores OCDE/PGD** (I01–I12);
- os **indicadores de gestão** para as chefias (G01 e G02);
- os **relatórios gerenciais** que os apresentam;
- a base e as especificações do **agente de gestão** (S01–S24), incorporado do projeto `pgd-agente-icmbio`.

Cada indicador passa por validação independente (protocolo A1–A5) antes de virar dado oficial.

**Em linguagem simples:** imagine que o PETRVS é um grande arquivo de tabelas de dados. Este projeto é o conjunto de fórmulas e instruções para extrair as métricas que você precisa dessas tabelas, sem criar cópias ou versões modificadas dos dados.

Os dados são acessados em **tempo real**, diretamente do banco do Dataprev via Denodo — não é necessário instalar banco de dados na máquina, restaurar arquivos de backup nem ter conhecimento de infraestrutura.

---

## 2. Quando usar este projeto

| Situação | Recomendação |
| --- | --- |
| Calcular os indicadores OCDE/PGD com dados atualizados | **Este projeto** |
| Validar a origem dos dados | **Este projeto** |
| Auditoria ou investigação pontual | **Este projeto** |
| Ambiente sem instalação de software servidor | **Este projeto** |
| Dashboards recorrentes e automatizados | DM_Petrvs_icmbio_postgre |
| ETL completo com dimensões e fatos | DM_Petrvs_icmbio_postgre |

---

## 3. Como funciona — o fluxo em três etapas

```text
Banco PETRVS (Dataprev)
        |
        v
  Denodo (acesso via internet, dados em tempo real)
        |
        v
  DBeaver (ferramenta de consulta — interface gráfica, gratuita)
        |
        v
  Resultado exportável para Excel ou CSV
```

Não há transformação de dados. As consultas leem diretamente as tabelas originais do PETRVS. O Denodo é a camada de acesso — ele entrega os dados sem que você precise instalar um banco de dados na sua máquina.

**O que você precisa para começar:**

- DBeaver Community instalado (gratuito, [dbeaver.io/download](https://dbeaver.io/download/))
- Credenciais de acesso ao Denodo fornecidas pelo responsável do projeto no seu órgão
- IP da sua máquina ou rede liberado pelo Dataprev

---

## 4. Como o PETRVS organiza os dados — analogia para entender

O PETRVS trabalha com dois tipos de planos. Entender a diferença é essencial para interpretar os indicadores.

### Plano de Entregas (nível da unidade)

É o contrato de resultados da **unidade**. A CGOV, por exemplo, define no início do semestre quais entregas vai produzir e qual é a meta numérica de cada uma.

No banco de dados, isso fica em duas tabelas:

- `planos_entregas` — o "cabeçalho" do plano (período, unidade, status)
- `planos_entregas_entregas` — cada entrega individual (meta planejada, meta executada)

### Plano de Trabalho (nível do servidor)

É a agenda individual de cada servidor. O servidor declara em quais entregas da unidade vai trabalhar e qual percentual da sua carga horária vai dedicar a cada uma.

No banco de dados, isso fica em:

- `planos_trabalhos` — o plano do servidor (quem, qual unidade, período)
- `planos_trabalhos_entregas` — o vínculo entre o plano do servidor e cada entrega (com o percentual de dedicação, campo `forca_trabalho`)

**A pergunta que os indicadores respondem:** as metas foram atingidas? O esforço foi distribuído de forma equilibrada entre as entregas e os servidores?

---

## 5. Tabelas do PETRVS utilizadas pelas consultas

| Tabela | Papel nos indicadores |
| --- | --- |
| `planos_entregas_entregas` | Metas planejadas e executadas (I02, I03, I04) |
| `planos_trabalhos_entregas` | Vínculo servidor × entrega + percentual dedicação (I05, I06, I07, I08) |
| `planos_trabalhos` | Plano de trabalho do servidor (I05 a I08) |
| `planos_entregas` | Contexto do ciclo de planejamento (I07, I08) |
| `unidades` | Sigla e nome da unidade (todos os indicadores) |
| `usuarios` | Nome do servidor (I05, I06) |
| `tipos_modalidades` | Regime de trabalho — presencial, híbrido, remoto (I01) |
| `avaliacoes` | Notas das avaliações individuais e de unidade (I09 a I12) |

---

## 6. Os 12 indicadores OCDE/PGD

O projeto cobre quatro eixos de análise, totalizando 12 indicadores. O índice navegável completo está em [índice dos indicadores OCDE](../ocde/06-indicadores-ocde-denodo.md). Os indicadores de gestão (G01 e G02) têm [índice próprio](../gestao/README.md).

| Eixo | Indicadores | Foco |
| --- | --- | --- |
| 1 — Trabalho Remoto | I01 | Distribuição por regime (presencial / híbrido / remoto) |
| 2 — Execução | I02, I03, I04 | Cumprimento de entregas e atingimento de metas |
| 3 — Carga de Trabalho | I05, I06, I07, I08 | Distribuição de esforço e horas por entrega |
| 4 — Desempenho e Avaliação | I09, I10, I11, I12 | Notas, coerência entre avaliações individual e de unidade |

---

## 7. Diferença em relação ao projeto datamart

| Aspecto | Este projeto (Denodo) | Projeto datamart (postgre) |
| --- | --- | --- |
| Acesso aos dados | Denodo — tempo real, via internet | PostgreSQL em container Docker local |
| Instalação local necessária | Apenas DBeaver (gratuito) | Docker + PostgreSQL + Superset |
| Transformação de dados | Nenhuma — leitura direta | ETL completo (stage → dim → fato) |
| Dashboards visuais | Não — resultado em tabela/CSV | Sim — Superset com gráficos |
| Complexidade de setup | Baixa | Alta |
| Fidelidade à origem | Máxima | Média (dados transformados) |
| Atualização dos dados | Tempo real | Depende da frequência do ETL |

---

## 8. Marcos

Evolução pública do projeto. Deliberações da CGOV são citadas só pelo identificador (Dnn) e pelo efeito técnico; o detalhe das mudanças está no [CHANGELOG](../../CHANGELOG.md) e nas fichas.

| Data | Marco |
| --- | --- |
| 14.05.2026 | Fim do dump MySQL local: os indicadores passam a ler o PETRVS em tempo real via Denodo |
| 14–19.06.2026 | Periodicidade oficial dos planos de entregas e de trabalho; reescrita dos scripts dos eixos 2, 3 e 4 |
| 24.07.2026 | Guias de execução via Jupyter, um por indicador |
| 05.08.2026 | Coluna `mesogrupo` (agrupador organizacional) nos 12 CSVs; correção dos avisos de qualidade deslocados pela nova coluna |
| 21.08.2026 | Documentação de como o status dos planos é obtido; correção da escala de notas (só I09 e I12 invertem a nota) |
| 08.09.2026 | Família de gestão (`gestao/`), com a primeira análise da situação dos Planos de Trabalho (hoje G01); descoberta das duas camadas de status |
| 11–12.09.2026 | Relatório cumulativo anonimizado; protocolo de validação A1–A5 automatizado, com oráculos independentes |
| 13.09.2026 | Ciclo gerencial retomável e Relatório Gerencial V2; decisões D01–D14 implementadas; namespace `IND_GEST_` (D17) |
| 14.09.2026 | G02 — Execução das Entregas (D18); indicadores certificados na regional GR2 |
| 23.09.2026 | Início da reorganização em monorepo (`pgd-icmbio`) |
| 26.09.2026 | Agente de gestão incorporado com histórico; relatórios em `relatorios/`; documentação por assunto; política das unidades piloto; ambiente local migrado |
| 27.09.2026 | Recortes pela hierarquia do PETRVS (D19); versão coordenada das decisões D19–D35; pilotos CGOV, COCAGE e GR2 validados e aceitos; instruções dos assistentes versionadas com núcleo comum |

---

## 9. Próximo passo

- **Para configurar o acesso:** [acesso ao Denodo e DBeaver](../ambiente/acesso-denodo-dbeaver.md)
- **Para entender os indicadores sem SQL:** [guia rápido para gestores](../indicadores/guia-rapido-gestores.md)
- **Para executar as consultas:** [índice dos indicadores OCDE](../ocde/06-indicadores-ocde-denodo.md)
