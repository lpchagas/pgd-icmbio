# Guia de Extração Mensal dos Indicadores OCDE/PGD — ICMBio

> **Escopos e gestão (14.09.2026):** toda execução do ciclo integrado informa um seletor
> organizacional. A2–A5, manifestos, relatórios e anexos ficam em
> `AAAA-MM/escopos/<scope-key>/`. O ciclo inclui G01 e G02. O relatório final exige
> `--manifesto-validacao`. A D18 homologou o G02 e o anexo nominal somente restrito;
> edições finais exigem os 14 alvos certificados. A expansão nacional está suspensa
> até o aceite formal do piloto CGOV.

> **Estado certificado:** a referência GR2 usa data de execução 13/09/2026, janela
> `01/07/2025–31/08/2026` e 14/14 alvos certificados automaticamente. O próximo
> passo institucional é o piloto CGOV; não executar escopo nacional.

Este guia descreve **quando e como** gerar os CSVs dos 12 indicadores OCDE/PGD
para alimentar o Painel Power BI do ICMBio — sem precisar entender programação.
Basta copiar os comandos e seguir os passos.

**Analogia para gestores:** os scripts funcionam como um relatório automático do
sistema. Você executa o comando, o script busca os dados no PETRVS via Denodo e
salva o resultado na pasta certa, já formatado para o Excel.

---

## 1. Periodicidade dos indicadores

Os indicadores se dividem em dois grupos com cadências diferentes a partir de 2026:

| Cadência | Instrumento base | Indicadores | Períodos gerados |
| --- | --- | --- | --- |
| **Mensal** | Plano de Trabalho (PT) | I01, I05, I06, I09, I10, I11 | M01-2026 … M12-2026 |
| **Quadrimestral** | Plano de Entrega (PE) | I02, I03, I04, I07, I08, I12 | Q1-2026, Q2-2026, Q3-2026 |

> **Histórico 2025 (trimestral):** a janela oficial começa em 01/07/2025. Todos os 12 indicadores incluem T3-2025 e T4-2025; T1 e T2 são excluídos por baixa confiabilidade.

### Por que as cadências são diferentes?

Os Planos de Trabalho individuais passaram a ter ciclos mensais em 2026 (M01 a
M12), enquanto os Planos de Entrega das unidades continuam seguindo ciclos
quadrimestrais (Q1: jan–abr, Q2: mai–ago, Q3: set–dez). Cada indicador é
atualizado no ritmo do instrumento que usa como fonte principal.

A lógica de períodos está em `lib/periodos.py`:

- `build_periods_pe()` — usado por I02, I03, I04, I07, I08, I12
- `build_periods_pt()` — usado por I01, I05, I06, I09, I10, I11

---

## 2. Calendário anual 2026

Cada execução usa cumulativamente 01/07/2025 até o último dia do mês anterior à `--data-execucao`. Ciclos iniciados depois do corte são excluídos; ciclos que o atravessam recebem `periodo_fim_efetivo` e `periodo_status = parcial_no_corte`.

| Mês de execução | Período encerrado | O que rodar | Scripts |
| --- | --- | --- | --- |
| Fevereiro | M01-2026 (jan) | PT mensais | I01, I05, I06, I09, I10, I11 |
| Março | M02-2026 (fev) | PT mensais | I01, I05, I06, I09, I10, I11 |
| Abril | M03-2026 (mar) | PT mensais | I01, I05, I06, I09, I10, I11 |
| **Maio** | M04-2026 (abr) + **Q1-2026** (jan–abr) | **PT mensais + PE quadrimestrais** | **I01–I12** |
| Junho | M05-2026 (mai) | PT mensais | I01, I05, I06, I09, I10, I11 |
| Julho | M06-2026 (jun) | PT mensais | I01, I05, I06, I09, I10, I11 |
| Agosto | M07-2026 (jul) | PT mensais | I01, I05, I06, I09, I10, I11 |
| **Setembro** | M08-2026 (ago) + **Q2-2026** (mai–ago) | **PT mensais + PE quadrimestrais** | **I01–I12** |
| Outubro | M09-2026 (set) | PT mensais | I01, I05, I06, I09, I10, I11 |
| Novembro | M10-2026 (out) | PT mensais | I01, I05, I06, I09, I10, I11 |
| Dezembro | M11-2026 (nov) | PT mensais | I01, I05, I06, I09, I10, I11 |
| **Janeiro 2027** | M12-2026 (dez) + **Q3-2026** (set–dez) | **PT mensais + PE quadrimestrais** | **I01–I12** |

> **Resumo prático:** rodar **todos os 12 indicadores juntos apenas três vezes
> no ano** (maio, setembro e janeiro), e só os 6 indicadores PT nos demais meses.
> Nos três meses de rodada completa, o CSV dos PE substituirá a versão anterior
> no Power BI com os dados do quadrimestre fechado. O relatório gerencial
> cumulativo é uma rotina distinta e reextrai I01–I12 em cada edição; consulte
> [15-relatorio-gerencial-cumulativo-anonimizado.md](../relatorios/relatorio-cumulativo.md).

---

## 3. CSVs esperados por execução

Referência de nomes de arquivo, volume de dados e tamanho aproximado
(valores do run de produção de 17/06/2026 — crescem mensalmente):

| # | Indicador | Arquivo CSV | Linhas | Tamanho |
|---|-----------|-------------|--------|---------|
| 1 | I01 — Regime de trabalho (resumo) | `IND_OCDE_01.2_v1_proporcao_mensal_AAAAMMDD_HHMM.csv` | ~137 | ~8 KB |
| 2 | I01 — Regime de trabalho (por unidade) | `IND_OCDE_01.2_v2_proporcao_unidade_mensal_AAAAMMDD_HHMM.csv` | ~10.367 | ~1 MB |
| 3 | I02 — Taxa de cumprimento das entregas | `IND_OCDE_02.2_taxa_cumprimento_temporal_AAAAMMDD_HHMM.csv` | ~1.935 | ~345 KB |
| 4 | I03 — Taxa de cumprimento por entrega | `IND_OCDE_03.2_taxa_cumprimento_temporal_AAAAMMDD_HHMM.csv` | ~16.219 | ~7 MB |
| 5 | I04 — Índice de atingimento de metas | `IND_OCDE_04.2_score_atingimento_metas_AAAAMMDD_HHMM.csv` | ~1.935 | ~323 KB |
| 6 | I05 — Distribuição de entregas por servidor | `IND_OCDE_05.2_distribuicao_entregas_servidores_AAAAMMDD_HHMM.csv` | ~9.546 | ~1,8 MB |
| 7 | I06 — Grau de responsabilidade por entrega | `IND_OCDE_06.2_grau_responsabilidade_entregas_AAAAMMDD_HHMM.csv` | ~4.921 | ~643 KB |
| 8 | I07 — Horas por entrega (absoluto) | `IND_OCDE_07.2_horas_por_entrega_AAAAMMDD_HHMM.csv` | ~25.307 | ~6,8 MB |
| 9 | I08 — Proporção de horas por entrega (%) | `IND_OCDE_08.2_proporcao_horas_entrega_AAAAMMDD_HHMM.csv` | ~25.307 | ~5,6 MB |
| 10 | I09 — Média das avaliações do PT | `IND_OCDE_09.2_media_avaliacao_pt_AAAAMMDD_HHMM.csv` | ~1.996 | ~273 KB |
| 11 | I10 — Percentual de avaliações inadequadas | `IND_OCDE_10.2_perc_inadequado_pt_AAAAMMDD_HHMM.csv` | ~1.996 | ~263 KB |
| 12 | I11 — Percentual de avaliações excepcionais | `IND_OCDE_11.2_perc_excepcional_pt_AAAAMMDD_HHMM.csv` | ~1.996 | ~265 KB |
| 13 | I12 — Coerência PT × PE | `IND_OCDE_12.2_coerencia_pt_pe_AAAAMMDD_HHMM.csv` | ~1.295 | ~190 KB |

> Os números de linhas e tamanhos aumentam a cada mês à medida que novos dados
> são registrados no PETRVS.

---

## 4. Pré-requisitos

Verifique os itens abaixo **uma única vez** antes da primeira execução.
Nas rodadas seguintes, basta executar os scripts.

### Checklist de pré-requisitos

- [ ] **IP liberado pelo Dataprev** — sem isso, a conexão falha silenciosamente.
  Se você consegue acessar o PETRVS pelo DBeaver, o IP já está liberado.
- [ ] **Java do mesmo sistema do Python** — no WSL (ambiente principal), o JDK do
  Linux (`sudo apt install -y openjdk-21-jre-headless`); no Windows, o Java embutido
  no DBeaver (`C:\Program Files\DBeaver\`).
- [ ] **Driver Denodo disponível** — o arquivo `.jar` JDBC da Denodo, fora do
  repositório: no WSL, `~/.local/share/denodo/jdbc/9/denodo-vdp-jdbcdriver-9.x.jar`;
  no Windows, numa pasta fixa ou na cópia `.jar` do driver do DBeaver. Como obter:
  [acesso ao Denodo e DBeaver](../ambiente/acesso-denodo-dbeaver.md).
- [ ] **Arquivo `.env` configurado** — o arquivo `.env` na raiz do projeto deve
  existir com suas credenciais. Veja a seção abaixo.
- [ ] **Ambiente Python do projeto** — no terminal, na raiz do projeto, execute
  `.venv/bin/python --version` (WSL) ou `.venv\Scripts\python.exe --version`
  (Windows). Deve retornar `Python 3.x.x`.
- [ ] **jpype instalado** — execute `.venv/bin/python -c "import jpype; print('OK')"`.
  Se retornar erro, instale as dependências: `.venv/bin/python -m pip install -r requirements-report.txt`.

### Configuração do arquivo `.env`

O arquivo `.env` fica na raiz do projeto (`pgd-icmbio/.env`) e
contém as credenciais de acesso ao Denodo. Ele **nunca é publicado no repositório**
(está no `.gitignore`). Copie o `.env.example` como `.env` (no WSL:
`cp .env.example .env && chmod 600 .env`) e preencha:

```
DENODO_USER=<seu_cpf_sem_pontos>
DENODO_PASSWORD=<sua_senha_denodo>
DENODO_DRIVER_PATH=/home/<seu_usuario>/.local/share/denodo/jdbc/9/denodo-vdp-jdbcdriver.jar
DENODO_HOST=denodo-pgd.dataprev.gov.br
DENODO_PORT=443
DENODO_DATABASE=petrvs_icmbio
JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
DENODO_JVM_DLL=/usr/lib/jvm/java-21-openjdk-amd64/lib/server/libjvm.so
```

No Windows, use o bloco "Windows" do `.env.example`
(`JAVA_HOME=C:/Program Files/DBeaver/jre` e o driver em caminho `C:/...`, sem
`DENODO_JVM_DLL`).

> **Atenção:** se sua senha do Denodo mudar, atualize `DENODO_PASSWORD`.
> Se outro usuário for executar em outra máquina, substitua `<seu_usuario>` pelo
> nome de usuário correspondente (WSL: `whoami`; Windows: `echo %USERNAME%`).

---

## 5. Preparação antes de cada rodada

**Data de execução.** Todo comando recebe `--data-execucao AAAA-MM-DD` (regra 7 das
instruções do projeto): use a data do dia da rodada e repita **a mesma data** em
todos os comandos do ciclo. A janela de análise vai de 01/07/2025 ao último dia do
mês anterior a essa data (ex.: `--data-execucao 2026-10-01` analisa até 30/09/2026).
Nunca rode sem a data: o resultado passaria a depender do dia em que o comando foi
executado.

Nos comandos abaixo, `python` é o Python do ambiente do projeto: no WSL,
`.venv/bin/python` (ou ative o ambiente uma vez por terminal com
`source .venv/bin/activate`); no Windows, `.venv\Scripts\python.exe` (ou
`.venv\Scripts\Activate.ps1`). Execute sempre na raiz do projeto
(`~/projetos/pgd-icmbio` no WSL; `C:\Projetos\pgd-icmbio` no Windows).

```bash
# 1. Atualizar o repositório local
git pull

# 2. Verificar que o .env existe (sem exibir as credenciais na tela)
test -f .env && echo ".env presente"          # Windows: Test-Path .env

# 3. Simular o ciclo, sem abrir o Denodo e sem gravar nada
python -m tools.executar_pilotos --capacidade ocde --data-execucao AAAA-MM-DD
```

A simulação é o modo padrão do `tools.executar_pilotos`: mostra a janela de
análise, os pilotos do cadastro (`config/unidades-piloto.json`) e o escopo de
entrega de cada um, e termina com `"status_global": "dry-run"`.

> **Atenção:** os scripts `IND_OCDE_XX.1_run.py` **não** têm modo de simulação nem
> ajuda. Chamá-los com `--dry-run` ou `--help` executa a extração **real e
> nacional**. Para testar, use sempre o comando 3 acima.

---

## 6. Execução

O ciclo oficial roda pelos **pilotos** cadastrados: os A1 consultam o universo
nacional uma única vez, e o recorte de cada piloto é aplicado depois. Os resultados
saem separados por piloto, em `artefatos_local/ocde/entregas/AAAA-MM/escopos/<scope-key>/`;
nunca some taxas entre pilotos. Sem seletor, a extração assume o escopo nacional,
que está suspenso (D16).

### 6a. Ciclo completo dos 12 indicadores (recomendado)

Depois da simulação da seção 5, execute (5 a 15 minutos, conforme a conexão com o
Dataprev):

```bash
python -m tools.executar_pilotos --capacidade ocde --data-execucao AAAA-MM-DD --modo real --validar
```

- `--modo real` faz a aquisição única no Denodo e grava os A2 de cada piloto.
- `--validar` roda a validação integrada A1–A5 de cada piloto
  ([protocolo de validação](protocolo-validacao.md)).
- Acrescente `--salvar` para gravar o registro da execução no acervo privado.

A saída é um JSON com o resultado por piloto. O ciclo terminou bem quando nenhum
piloto tem `erro` preenchido; investigue antes de compartilhar qualquer arquivo.

### 6b. Um indicador específico

Use quando precisar gerar ou refazer apenas um indicador (por exemplo, depois de
uma correção). Simule e depois execute com a mesma data:

```bash
python -m tools.executar_pilotos --capacidade I02 --data-execucao AAAA-MM-DD
python -m tools.executar_pilotos --capacidade I02 --data-execucao AAAA-MM-DD --modo real --validar
```

| Indicador | `--capacidade` | O que mostra |
|-----------|---------|-------------|
| **I01** | `I01` | Gera 2 arquivos: resumo nacional + detalhamento por unidade |
| **I02** | `I02` | % das entregas de cada unidade concluídas no período |
| **I03** | `I03` | Status de cada entrega individual (concluída / em andamento / não iniciada) |
| **I04** | `I04` | Score médio de atingimento das metas por unidade (0 a 100+) |
| **I05** | `I05` | Quantas entregas cada servidor está responsável por unidade |
| **I06** | `I06` | Quantos servidores compartilham cada entrega e com que % de força de trabalho |
| **I07** | `I07` | Total de horas planejadas para cada entrega em cada unidade |
| **I08** | `I08` | % da capacidade total da unidade alocado em cada entrega |
| **I09** | `I09` | Nota média (1 a 5) das avaliações dos servidores por unidade |
| **I10** | `I10` | % das avaliações com nota "Inadequado" por unidade |
| **I11** | `I11` | % das avaliações com nota "Excepcional" por unidade |
| **I12** | `I12` | Se a avaliação individual (PT) está alinhada com a avaliação coletiva (PE) da unidade |

### 6c. Indicadores PT e PE no calendário

O ciclo da seção 6a sempre executa os 12 indicadores, com a janela definida pela
data de execução. A cadência da seção 2 continua valendo para a **leitura** dos
resultados: os indicadores de PT (I01, I05, I06, I09, I10, I11) fecham todo mês; os
de PE (I02, I03, I04, I07, I08, I12) só fecham um quadrimestre em maio, setembro e
janeiro, e nos demais meses o período corrente aparece como parcial.

### 6d. Comandos diretos (uso avançado)

O `tools.executar_pilotos` chama por baixo o `lib.indicator_extraction`, que também
pode ser usado diretamente, sempre com um seletor de piloto:

```bash
python -m lib.indicator_extraction --data-execucao AAAA-MM-DD --pilotos --dry-run
python -m lib.indicator_extraction --data-execucao AAAA-MM-DD --pilotos --salvar-manifesto
python -m lib.indicator_extraction --data-execucao AAAA-MM-DD --pilotos --so I02 --salvar-manifesto
```

Executar um script `IND_OCDE_XX.1_run.py` diretamente só serve para diagnóstico
técnico: ele consulta o **universo nacional**, grava uma saída legada em
`artefatos_local/ocde/entregas/AAAA-MM/` (fora dos escopos) e não passa pela
validação. Se for indispensável, informe a data, que o script lê da linha de
comando:

```bash
python ocde/indicadores/IND_OCDE_02.1_run.py --data-execucao AAAA-MM-DD
```

---

## 7. Como abrir os CSVs no Excel

Os arquivos usam **pipe (`|`)** como separador em vez de vírgula ou ponto-e-vírgula.
Isso evita que descrições de entregas (que frequentemente contêm `;`) corrompam
o arquivo.

### Passos para abrir corretamente

1. Abra o Excel.
2. Menu **Dados** → **Obter Dados** → **De Arquivo** → **De Texto/CSV**.
3. Navegue até `artefatos_local\ocde\entregas\AAAA-MM\`.
4. Selecione o arquivo desejado.
5. Na janela de importação, altere o **Delimitador** para **Personalizado** e
   digite `|` (pipe).
6. Clique em **Carregar**.

> **Dica:** se você importar uma vez e salvar como `.xlsx`, não precisa repetir
> o processo. Para ter os dados mais recentes, reimporte o CSV atualizado.

---

## 8. Fluxo após extração

### Rotina mensal recomendada

```
Primeiro dia útil do mês:
  1. Simular e executar o ciclo dos pilotos com --data-execucao (seções 5 e 6a)
  2. Confirmar que o ciclo terminou sem erro em nenhum piloto
  3. Abrir os CSVs no Excel para verificação visual rápida
  4. Enviar à COCAGE/Power BI conforme protocolo vigente

Até o dia 5 do mês:
  5. Revisar e encaminhar os arquivos de entrega
```

### Calendário de execução

| Quando | O que fazer |
|--------|-------------|
| **Primeiro dia útil do mês** | Executar o ciclo dos pilotos (seção 6a) |
| **Até o dia 5 do mês** | Revisar os CSVs e enviar à COCAGE |
| **A qualquer momento** | Executar um indicador específico após correção ou solicitação pontual (seção 6b) |
| **Antes de qualquer commit** | Executar o checklist `docs/ambiente/seguranca-publicacao.md` |

---

## 9. Organização dos arquivos

Arquivos públicos do repositório:

```text
docs/                         documentação pública
ocde/indicadores/          executores IND_OCDE_XX.1_run.py
lib/                  funções comuns sem credenciais
```

Arquivos locais, **nunca versionados** (caminhos gerenciados por `lib/csv_utils.py`):

```text
artefatos_local/
  ocde/
    entregas/
      AAAA-MM/
        escopos/<scope-key>/  A2 do ciclo oficial, isolados por escopo
        IND_OCDE_XX.2_*       saídas legadas de scripts executados diretamente
    diagnosticos/
      AAAA-MM/            CSVs diagnósticos A4 (uso interno — não enviar)
                          IND_OCDE_XX.4_qN_<descricao>.csv
      IND_OCDE_XX.4_diagnostico_DD.MM.AAAA.py
  validacao/
    AAAA-MM/escopos/<scope-key>/  A3–A5 e manifestos do protocolo automatizado
    baselines.json                 baseline privada registrada somente pela CLI
  docs_internos/          Protocolo de validação e docs não publicáveis
  backup_scripts_a1/      Cópias locais dos scripts A1 (backup jun 2026)
  historico/              Artefatos legados (dump e validação inicial mai/2026)
```

Os caminhos são gerenciados por `lib/csv_utils.py`:

- `indicator_csv_dir()` → `artefatos_local/ocde/entregas/AAAA-MM/`; o runner move
  apenas as linhas do escopo para `escopos/<scope-key>/`
- `diagnostic_csv_dir()` → `artefatos_local/ocde/diagnosticos/AAAA-MM/`

---

## 10. Importação no Power BI

Os CSVs gerados usam **pipe (`|`) como delimitador** e **UTF-8 com BOM** como
codificação — configure assim ao importar:

- **Delimitador:** pipe `|`
- **Codificação:** UTF-8 (a opção "UTF-8 com BOM" resolve automaticamente
  problemas com acentos)
- **Primeira linha como cabeçalho:** sim
- **Tipos de dado:** deixar o Power BI inferir; ajustar manualmente colunas de
  percentual (`DECIMAL`) e de data (`DATE`)

Para manter o painel sempre atualizado:

1. Gere os CSVs conforme o calendário da seção 2
2. Substitua os arquivos anteriores na pasta de destino do Power BI
3. Clique em "Atualizar" no Power BI Desktop

> **Atenção:** os CSVs têm nomes com timestamp
> (`IND_OCDE_02.2_taxa_cumprimento_temporal_20260614_2050.csv`). Configure o Power BI
> para apontar para a **pasta** e não para um arquivo específico, usando a função
> `Folder.Files` — assim uma nova execução não quebra o relatório.

---

## 11. Auditoria dos CSVs

Cada script executa uma auditoria estrutural básica ao final:

- quantidade de linhas de dados
- quantidade de colunas
- consistência da largura das linhas no CSV

Antes de importar para o Power BI, verifique no terminal se a auditoria não
apontou `ALERTA`. Se apontar, rode `/p3b-auditar` para investigar antes de
compartilhar os resultados.

---

## 12. Solução de problemas frequentes

### Erro: "Configure DENODO_USER, DENODO_PASSWORD..."

**Causa:** o arquivo `.env` não existe ou ainda tem os placeholders padrão.

**Solução:** abra `.env` (no WSL, `nano .env`; no Windows, Bloco de Notas) e
preencha as credenciais conforme a seção 4.

---

### Erro: "JVM não iniciada" ou "No module named 'jpype'"

**Causa:** o jpype não está instalado no ambiente Python atual, ou a JVM
configurada não é do mesmo sistema do Python.

**Solução:**

```bash
.venv/bin/python -m pip install jpype1
```

Se o erro persistir: no WSL, confira se `DENODO_JVM_DLL` no `.env` aponta para o
`libjvm.so` do Java do Linux (o Python do WSL não carrega a `jvm.dll` do Windows);
no Windows, se `JAVA_HOME` aponta para o diretório correto do DBeaver
(`C:/Program Files/DBeaver/jre`).

---

### Erro: "Connection refused" ou timeout sem mensagem

**Causa:** IP não liberado pelo Dataprev, ou VPN corporativa bloqueando.

**Solução:**

1. Teste a conexão no DBeaver — se o DBeaver conectar, o script também conecta.
2. Se o DBeaver também falhar: solicitar liberação de IP ao responsável pelo
   acesso Denodo no ICMBio.
3. Em home office: verificar se a VPN do ICMBio está ativa.

---

### Erro: arquivo `.jar` não encontrado

**Causa:** o caminho de `DENODO_DRIVER_PATH` não existe, ou (no Windows, com a
cópia do driver do DBeaver) o DBeaver atualizou o driver e o `.jar` foi substituído.

**Solução no WSL:** confira o caminho com `ls -l "$(grep ^DENODO_DRIVER_PATH= .env | cut -d= -f2-)"`.
Se o arquivo não existir, obtenha o `.jar` JDBC conforme o
[guia de acesso ao Denodo](../ambiente/acesso-denodo-dbeaver.md); o download
automático pode trazer o pacote ODBC, que não serve.

**Solução no Windows:** execute no PowerShell (substituindo `<seu_usuario>` pelo
seu usuário Windows):

```powershell
$dir = "C:\Users\<seu_usuario>\AppData\Roaming\DBeaverData\drivers\remote\drivers\jdbc\9"
Copy-Item "$dir\denodo-vdp-jdbcdriver" "$dir\denodo-vdp-jdbcdriver.jar" -Force
Write-Host "Driver copiado com sucesso."
```

---

### Um indicador gerou 0 linhas

**Causa mais comum:** período futuro (ex: Q3-2026 ainda sem dados suficientes
no PETRVS), ou filtro temporal sem correspondência nos dados.

**Como verificar:** simule o indicador com a mesma data de execução e confira a
janela de análise (`periodo_analise_inicio` e `periodo_analise_fim`) na saída:

```bash
python -m tools.executar_pilotos --capacidade IXX --data-execucao AAAA-MM-DD
```

A simulação não conecta ao Denodo. Não use `--dry-run` direto no script
`IND_OCDE_XX.1_run.py`: ele não tem esse modo e executaria a extração real.

---

### O CSV está corrompido no Excel (tudo em uma coluna)

**Causa:** o Excel tentou abrir com delimitador errado.

**Solução:** siga os passos da seção 7, garantindo que o delimitador seja `|` (pipe).

---

## 13. Registro histórico de testes em produção (17/06/2026)

Os 12 indicadores foram executados com conexão real ao Denodo nessa data. Esse
registro demonstra viabilidade técnica, mas não é o baseline do ciclo atual: a
janela oficial passou a iniciar em 01/07/2025 e os números variam com a base
operacional. Para validação reproduzível, use o protocolo público descrito em
[09-protocolo-validacao-indicadores.md](protocolo-validacao.md),
sempre informando `--data-execucao`.

---

## 14. Prompts para ferramentas de IA

Prompts prontos para as principais ferramentas de IA disponíveis no projeto.
Adapte substituindo `XX` pelo número do indicador e `ERRO` pela mensagem real.

### Assistente de código com acesso ao repositório

**Executar a extração mensal completa:**
```
Execute a extração mensal completa dos 12 indicadores OCDE. Rode todos os scripts em
ocde/indicadores/ em sequência, registre os resultados (linhas geradas por período e
por indicador) e me informe quais funcionaram e quais falharam. Se houver erros, diagnostique
a causa com base nos logs, nas fichas em `docs/ocde/` e no protocolo público de validação.
```

**Diagnosticar um erro específico:**
```
O script IND_OCDE_XX.1_run.py falhou com o seguinte erro:
[cole aqui a mensagem de erro completa]

Com base no projeto `pgd-ocde-icmbio` e em `docs/ocde/`, identifique a causa e proponha
a correção. Leve em conta que o banco é acessado via Denodo VQL (não MySQL), que funções
MySQL como json_unquote(), date_add() e WITH RECURSIVE não funcionam, e que os nomes de
tabela precisam do prefixo petrvs_icmbio_ no JDBC.
```

**Verificar se um CSV foi gerado corretamente:**
```
Analise o arquivo artefatos_local/ocde/entregas/AAAA-MM/IND_OCDE_XX.2_*.csv e verifique:
1. Quantas linhas foram geradas por período (T3-2025 a Q2-2026)?
2. Há linhas com campos vazios no campo unidade_sigla?
3. Os valores numéricos estão dentro dos intervalos esperados (percentuais entre 0 e 100)?
4. Compare com o baseline público e com o A5 do ciclo, se disponíveis.
```

**Gerar relatório de qualidade dos dados:**
```
Leia todos os CSVs gerados em artefatos_local/ocde/entregas/AAAA-MM/ e produza um relatório
resumido de qualidade com: total de linhas por indicador, períodos que retornaram 0 linhas,
unidades que aparecem em todos os indicadores e unidades com dados ausentes em algum indicador.
```

**Atualizar a documentação de um indicador:**
```
O indicador IXX teve sua lógica ajustada conforme o protocolo público de validação.
Atualize a ficha `docs/ocde/06.X.X-iXX.md` refletindo o estado atual
do script e do último relatório de validação.
```

### GitHub Copilot (Chat / Inline — útil para código dentro do editor)

**Explicar um erro no terminal:**
```
@terminal Esse é o erro do script Python que executa o indicador IXX do projeto PETRVS:
[cole o erro]
Explique o que significa e sugira como corrigir considerando que o banco é Denodo VQL
(não MySQL) e não suporta json_unquote() nem WITH RECURSIVE.
```

**Gerar um script de verificação rápida:**
```
@workspace Baseando-se nos scripts em ocde/indicadores/ e em lib/, crie um script
Python chamado verificar_csvs.py que: (1) liste todos os CSVs em artefatos_local/ocde/entregas/[mês
atual]/; (2) para cada CSV, mostre nome, número de linhas e colunas; (3) alerte se algum CSV
tiver 0 linhas. Use delimitador pipe (|) e encoding utf-8-sig.
```

### Gemini / ChatGPT — análise de dados e geração de relatórios

**Interpretar resultados de um indicador:**
```
Tenho um CSV com resultados do Indicador I09 (Média das Avaliações do Plano de Trabalho
por Unidade) do ICMBio. A escala de notas é: 1=Não executado, 2=Inadequado, 3=Adequado,
4=Alto desempenho, 5=Excepcional. Com base nas linhas abaixo, identifique as 5 unidades
com melhor e pior desempenho e proponha uma narrativa para apresentar à liderança do ICMBio:
[cole aqui 20–30 linhas do CSV]
```

**Adaptar uma query MySQL para Denodo VQL:**
```
Adapte a query MySQL abaixo para Denodo VQL. Regras obrigatórias:
- Substituir DATE(campo) por CAST(campo AS DATE)
- Substituir JSON_UNQUOTE(campo) pelo campo diretamente
- Substituir WITH RECURSIVE por aritmética de datas: (data_fim - data_inicio) + 1
- Adicionar prefixo petrvs_icmbio_ em todos os nomes de tabela

Query MySQL original:
[cole a query aqui]
```

---

## 15. Validação manual pela CGOV

Quando houver validação pela equipe CGOV:

- salve PDFs de consulta PETRVS em `artefatos_local/validacao/`
- copie `ocde/diagnosticos/IND_OCDE_XX.4_diagnostico_template.py` para
  `artefatos_local/ocde/diagnosticos/` e preencha as queries locais
- salve CSVs diagnósticos em `artefatos_local/ocde/diagnosticos/AAAA-MM/`
- salve relatórios internos em `artefatos_local/validacao/`

Esses arquivos podem conter dados operacionais e não devem ser publicados.

---

## 16. Antes de publicar alterações no repositório

Execute a checklist de `docs/ambiente/seguranca-publicacao.md`. Se qualquer busca
apontar CPF, senha, CSV, PDF, relatório interno ou script local com credencial,
interrompa a publicação e corrija antes do commit.

---

## 17. Notas técnicas

### Periodicidade dos instrumentos (regra ICMBio vigente desde 2026)

| Instrumento | 2025 | 2026 |
|-------------|------|------|
| Plano de Entregas (PE) | Trimestral (T1–T4) | Quadrimestral (Q1–Q3) |
| Plano de Trabalho (PT) | Trimestral (T1–T4) | **Mensal (M01–M12)** |

- Scripts de I02, I03, I04, I07, I08, I12 (baseados em PE): `build_periods_pe()` → ciclos quadrimestrais em 2026
- Scripts de I01, I05, I06, I09, I10, I11 (baseados em PT): `build_periods_pt()` → ciclos mensais em 2026

### Correções aplicadas em 17/06/2026

Dois problemas foram corrigidos durante a preparação para produção:

1. **I08 — CTE recursiva incompatível com Denodo:** o script usava `WITH RECURSIVE`
   e funções MySQL (`date_add`, `dayofweek`, `concat`) para gerar calendário de dias
   úteis. Denodo VQL não suporta CTEs recursivas. Reescrito com aritmética de datas
   proporcional, mesma abordagem do I07.

2. **I09/I10/I11/I12 — `json_unquote()` inexistente no Denodo:** as queries usavam
   `JSON_UNQUOTE(tan.nota)`. Removido automaticamente na camada de adaptação
   (`adapt_for_jdbc` em `lib/docs_sql.py`), mantendo o
   `TRIM(BOTH '"' FROM ...)` externo que já faz a remoção de aspas quando necessário.
