# Registro de Execução do Plano de Entregas por período

> **Para quem é este documento:** chefias de unidade de execução que precisam
> fechar o registro de execução do Plano de Entregas (PE) de um quadrimestre e
> saber, com evidência, se ele já pode ser concluído.

---

## 1. Por que este produto existe

Fechar o Plano de Entregas de um quadrimestre exige responder duas perguntas que
nenhum artefato anterior deste repositório respondia junto:

1. **O que aconteceu com cada entrega do PE no período?** Progresso esperado
   contra progresso realizado, prazo, meta pactuada.
2. **Os planos de trabalho da equipe foram executados?** A **RN-04** condiciona a
   conclusão do PE à verificação de que *todos* os PT dos servidores da unidade
   no período foram registrados e avaliados. Como o PE é quadrimestral e o PT é
   mensal desde 2026, isso significa **quatro ciclos mensais completos por
   servidor**.

O `PT_STATUS` responde "qual plano de trabalho está parado agora" — uma
fotografia operacional. O relatório gerencial responde "como os indicadores
evoluíram" — uma série cumulativa. Nenhum dos dois recorta um período fechado do
PE nem cruza as duas camadas. É essa lacuna que o `REG_EXEC` preenche.

---

## 2. Q2 é um quadrimestre, não um trimestre

Desde 2026 o Plano de Entregas das unidades do ICMBio é **quadrimestral**: três
períodos de quatro meses por ano.

| Rótulo | Início | Fim | Ciclos mensais de PT contidos |
|---|---|---|---|
| `Q1-AAAA` | 01/01 | 30/04 | M01, M02, M03, M04 |
| `Q2-AAAA` | 01/05 | 31/08 | M05, M06, M07, M08 |
| `Q3-AAAA` | 01/09 | 31/12 | M09, M10, M11, M12 |

**Não existe Q4.** O texto herdado das planilhas de controle da CGOV chamava
esses períodos de "trimestres" e previa um "Q4 implícito" — resíduo do ciclo
trimestral de 2025, que de fato usava `T1`–`T4`. A nomenclatura correta para
2026 em diante é a da tabela acima, e é a que `lib/periodos.py` implementa.

### 2.1 Divergência aberta com o calendário publicado

A página do ciclo do PGD mantida pela CGGE publica as faixas como
`01/01–31/04`, `01/05–30/07` e `01/08–31/12`. As três são internamente
inconsistentes: **31/04 não existe**, há lacuna entre 30/07 e 01/08, e a
terceira faixa tem cinco meses. Para o segundo período a divergência é material
— `01/05–30/07` (CGGE) contra `01/05–31/08` (código).

Este produto adota a segmentação implementada e testada, e **registra a
divergência em toda edição do relatório**. A confirmação formal da CGGE segue
pendente; até lá, conferir o recorte antes de usar os números em ato oficial.

---

## 3. Recorte de período e janela cumulativa

As duas noções coexistem e não se substituem:

- A **janela de análise** é sempre cumulativa: de 01/07/2025 até o último dia do
  mês anterior à data de execução. É ela que garante comparabilidade entre
  edições e continua valendo para todos os indicadores.
- O **recorte de período** é um corte interno dessa janela. `Q2-2026` só é
  resolvível se estiver contido nela.

Rodando em setembro de 2026, a janela termina em 31/08/2026 e `Q2-2026` sai como
`encerrado`. Rodando antes disso, o mesmo rótulo sai como `parcial_no_corte` e o
relatório abre com aviso de parcialidade — os números existem, mas não fecham o
quadrimestre.

Três desfechos são distinguidos de propósito, porque a orientação ao operador
muda em cada caso:

| Situação | Resultado |
|---|---|
| Rótulo fora da gramática (`Q9-2026`, `M13-2026`) | erro de rótulo desconhecido |
| Rótulo válido, período posterior ao corte (`Q3-2026` em setembro) | erro de período indisponível, com a orientação de rodar depois |
| Rótulo válido e contido na janela | resolvido, com `periodo_status` dizendo se encerrou |

---

## 4. Como executar

### 4.1 Pré-requisitos

1. Arquivo `.env` na raiz do projeto com as credenciais do Denodo — ver
   `.env.example`.
2. Java e o driver JDBC do Denodo instalados (o DBeaver os instala na primeira
   conexão), com `jpype` disponível no interpretador usado.
3. Opcionalmente, o arquivo de estrutura organizacional em
   `artefatos_local/ocde/diagnosticos/ICMBIO_estrutura.csv`. Sem ele a coluna
   `mesogrupo` sai como `Não mapeado` e todo o resto funciona.

### 4.2 Sequência recomendada

```bash
# 1) Ensaio — valida período, escopo e destino sem abrir conexão
python gestao/REG_EXEC.1_run.py --unidade CGOV --periodo Q2-2026 \
    --data-execucao 2026-09-14 --dry-run

# 2) Extração e relatório nominal, para uso interno da chefia
python gestao/REG_EXEC.1_run.py --unidade CGOV --incluir-subordinadas \
    --periodo Q2-2026 --data-execucao 2026-09-14 \
    --produto operacional --relatorio

# 3) Versão sem nomes, para circular fora da unidade
python gestao/REG_EXEC.1_run.py --unidade CGOV --periodo Q2-2026 \
    --data-execucao 2026-09-14 --produto restrito --relatorio
```

Omitir `--periodo` seleciona automaticamente o último período de PE **encerrado**
na janela — em setembro de 2026, `Q2-2026`.

### 4.3 Argumentos

| Argumento | Efeito |
|---|---|
| `--unidade SIGLA` | Igualdade exata de sigla; repetível ou `A,B,C` |
| `--incluir-subordinadas` | Acrescenta as unidades filhas, até três níveis |
| `--todas` | Todas as unidades do ICMBio |
| `--periodo` | Rótulo do período de PE; padrão é o último encerrado |
| `--exigir-encerrado` | Recusa período ainda aberto no corte |
| `--produto` | `operacional`, `restrito` ou `compartilhavel` |
| `--relatorio` | Além dos CSVs, gera o registro em Markdown |
| `--data-execucao` | Data reprodutível da apuração |
| `--dry-run` | Não abre conexão |

---

## 5. Artefatos gerados

Todos em `artefatos_local/gestao/AAAA-MM/`, pipe-delimitados e em `utf-8-sig`.

| Arquivo | Conteúdo |
|---|---|
| `REG_EXEC.2_entregas_*.csv` | Uma linha por entrega do PE vigente no período |
| `REG_EXEC.2_ciclos_pt_*.csv` | Uma linha por servidor × ciclo mensal, com o veredito da RN-04 |
| `REG_EXEC.2_vinculos_*.csv` | Força de trabalho declarada de cada PT em cada entrega |
| `REG_EXEC.2_painel_*.csv` | Agregado por unidade, com a aptidão à conclusão |
| `REG_EXEC.5_registro_execucao_*.md` | O registro de execução redigido |

As sete primeiras colunas de todos os CSVs são as colunas canônicas de período
(`ciclo_tipo`, `periodo`, `periodo_inicio`, `periodo_fim`, `periodo_fim_efetivo`,
`periodo_status`, `duracao_dias`), na mesma ordem dos demais produtos do projeto.

---

## 6. Como o cumprimento da entrega é medido

```text
cumprida  ⟺  progresso_esperado > 0  E  progresso_realizado >= progresso_esperado
taxa      =  entregas_cumpridas / entregas_com_meta x 100
```

Três consequências que não são acidentais:

1. **Entrega sem meta pactuada nunca conta como cumprida.** `progresso_esperado`
   igual a zero significa meta não pactuada, não meta trivialmente atingida.
   Ela aparece no relatório com `meta_tipo = N/D`, como pendência.
2. **O progresso vem da meta, nunca da contagem de atividades ou de etapas.**
   Conclusão de atividade ou de plano de trabalho não substitui a meta própria
   da entrega — é o que separa esforço de resultado.
3. **Superexecução é preservada.** Valores acima de 100% não são truncados.

O produto também **exporta** `progresso_esperado` e a meta em JSON lado a lado e
sinaliza divergência de escala na coluna `anomalia_escala`, em vez de escolher um
dos dois campos em silêncio. O banco de origem tem escalas mistas (0–1 e 0–100) e
valores negativos documentados.

---

## 7. A verificação da RN-04

O universo verificado é o dos **planos de trabalho vigentes** no período, não o
das consolidações existentes. A diferença é o ponto central: um ciclo que nunca
foi aberto não aparece em nenhuma consulta de consolidações — e é exatamente
esse o caso que impede a conclusão do PE sem que ninguém perceba.

| Estado do ciclo mensal | Semáforo | Bloqueia a conclusão? |
|---|---|---|
| Consolidação avaliada | 🟢 | não |
| Consolidação enviada, sem avaliação da chefia | 🟡 | **sim** |
| Consolidação aberta e não enviada pelo servidor | 🔴 | **sim** |
| Nenhuma consolidação, com PT vigente no mês | 🔴 | **sim** |
| Mês fora da vigência do PT | ⬜ | não, e não conta como esperado |

O estado `CONCLUIDO` da consolidação merece atenção: no PETRVS ele significa
"o servidor enviou e aguarda a avaliação da chefia". Tratá-lo como resolvido é o
erro silencioso mais fácil de cometer neste produto — daí o semáforo amarelo e o
bloqueio.

A última linha — mês fora da vigência — cobre admissão, exoneração e cessão no
meio do quadrimestre. Cobrar de um servidor um ciclo anterior ao início do seu
plano produziria pendência inexistente.

`rn04_apto_conclusao` só vale `SIM` quando não há nenhum ciclo bloqueante.

---

## 8. Separação entre Plano de Entregas e Plano de Trabalho

O produto mantém a separação metodológica do projeto:

- O **resultado** é medido pela meta da entrega do PE, atribuída à unidade dona.
- Os **planos de trabalho** entram por dois caminhos distintos: como verificação
  de execução (seção 7) e como **capacidade planejada** — a coluna
  `horas_contratuais_estimadas`, derivada da carga horária, da proporção de dias
  do plano dentro do período e do campo `forca_trabalho`.

Capacidade planejada **não é esforço realizado**. Esforço vem de
`tempo_despendido` das atividades, exportado em coluna própria. Usar um no lugar
do outro é precisamente a confusão que a separação PE × PT existe para evitar.

---

## 9. Privacidade e os três produtos

| Produto | Nomes de servidores | Uso |
|---|---|---|
| `operacional` | presentes | Uso interno da chefia; nunca sai de `artefatos_local/` |
| `restrito` | substituídos por `SERVIDOR_01..NN` | Circulação interna no ICMBio |
| `compartilhavel` | idem, com agregação | Divulgação mais ampla |

Nos produtos `restrito` e `compartilhavel` a coluna nominal é removida, os textos
livres passam por sanitização de dados pessoais e os arquivos gravados são
varridos automaticamente antes de a execução terminar. O identificador da
entrega é uma referência derivada, não o identificador do PETRVS.

Os pseudônimos têm escopo de execução: se a composição da equipe mudar, os
rótulos mudam. É deliberado — eles não são identidade persistente —, mas
significa que não servem para comparar edições diferentes.

---

## 10. Limites conhecidos

1. **`--unidade` não expande a hierarquia sozinho.** Se algum servidor estiver
   lotado em unidade subordinada e `--incluir-subordinadas` não for usado, ele
   fica fora da verificação e o veredito pode indicar aptidão indevida. Quando a
   expansão acrescenta unidades, o relatório registra quais.
2. **Chefia sem plano de trabalho próprio.** Servidores sem PT vigente no período
   simplesmente não aparecem na matriz. Confira a lotação da equipe contra a
   seção 7 antes de concluir o PE.
3. **O produto `compartilhavel` é pouco útil para coordenações pequenas.** Com
   cerca de cinco servidores, a agregação suprime quase tudo.
4. **Calendário pendente de confirmação da CGGE** — ver a seção 2.1.

---

## 11. Estado de homologação

`REG_EXEC` está registrado em `gestao/registry.py` com
`baseline = HOMOLOGACAO_INICIAL_PENDENTE`, como todos os alvos do projeto. As
tolerâncias seguem o Anexo A do caderno metodológico: contagens exigem igualdade
exata, percentuais toleram 0,05 ponto percentual, horas e escores toleram 0,01.

O relatório é **insumo técnico de apoio**: não homologa avaliação, não atribui
conceito e não substitui o registro no PETRVS. A avaliação do PE pela chefia
superior é ato distinto, com prazo próprio.

Ver também o [caderno metodológico](17-caderno-metodologico-cgov.md) e o
[guia de extração mensal](11-guia-extracao-mensal.md).
