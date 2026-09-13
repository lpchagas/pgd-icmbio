# Visão Geral do Projeto

## Para quem é este documento

Este documento é para **qualquer perfil** — gestores, analistas ou equipe técnica. Se você é gestor e quer entender os indicadores sem SQL, comece pelo [08-guia-rapido-gestores.md](08-guia-rapido-gestores.md).

---

## 1. O que é o pgd-ocde-icmbio

Este projeto é um conjunto de **consultas SQL e documentação** para calcular os **indicadores OCDE/PGD do ICMBio** diretamente dos dados originais do PETRVS, sem nenhuma transformação intermediária.

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

O projeto cobre quatro eixos de análise, totalizando 12 indicadores. O índice navegável completo está em [06-indicadores-ocde-denodo.md](ocde/06-indicadores-ocde-denodo.md).

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

## 8. Próximo passo

- **Para configurar o acesso:** [03-acesso-direto-denodo-dbeaver.md](03-acesso-direto-denodo-dbeaver.md)
- **Para entender os indicadores sem SQL:** [08-guia-rapido-gestores.md](08-guia-rapido-gestores.md)
- **Para executar as consultas:** [06-indicadores-ocde-denodo.md](ocde/06-indicadores-ocde-denodo.md)
