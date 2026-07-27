# pgd-agente-icmbio

Agente de apoio ao Plano de Gestão de Desempenho (PGD) do ICMBio: conhecimento
institucional (RAG), consulta de indicadores reais do PETRVS via Denodo e skills
executáveis (S01–S10) para montagem e auditoria de portfólio, capacidade e estratégia.

Documento normativo do projeto: [`proposta-projeto-v4.md`](proposta-projeto-v4.md).
Análise técnica do esquema de dados: [`docs/tecnologia/AT-01_analise-petrvs-esquema-mysql_v1.md`](docs/tecnologia/AT-01_analise-petrvs-esquema-mysql_v1.md).
Decisões arquiteturais: [`docs/gestao/decisoes/`](docs/gestao/decisoes/) (ADR-001 a ADR-006).

## Pré-requisitos

- Python 3.14 (`.venv` local do repositório)
- MySQL 8 Community, instalado como serviço Windows local (porta 3306) — ver
  [ADR-006](docs/gestao/decisoes/ADR-006-persistencia-mysql.md) e D4
- Acesso ao Denodo institucional (JDBC) apenas para `sincronizar_ref.py` — requer rede/VPN
  do ICMBio; driver `denodo-vdp-jdbcdriver.jar` e `jvm.dll` configurados no `.env`

## Setup local

```powershell
.venv\Scripts\pip install -r requirements.txt
copy .env.example .env   # preencher com as credenciais reais (nunca commitar)
mysql -u <usuario> -p < src\dados\schema.sql
```

O `schema.sql` cria o banco `pgd_agente` (21 tabelas + 6 triggers de imutabilidade —
UPDATE/DELETE em versões históricas e em `execucoes_skill` são rejeitados pelo próprio
banco).

## Estrutura do repositório

```text
src/dados/       Camada de dados do modelo comum (Incremento I0)
  schema.sql        Esquema (21 tabelas), aplicado uma vez por ambiente
  db.py             Conexão PyMySQL (lê MYSQL_* do .env)
  versoes.py        Única via de escrita para entidades versionáveis (IDs + versões)
  sincronizar_ref.py Espelhos ref_unidades/ref_usuarios (Denodo → MySQL local)
  backup.ps1        mysqldump diário (agendado via Tarefas do Windows)
docs/
  gestao/           ADRs, matriz de riscos (riscos.md), atas
  tecnologia/       Análises técnicas (AT-xx)
skills/             Metodologia PGD/OCDE (B01-B04) e specs das skills (S01-S10)
data/backups/       Dumps mysqldump (ignorado pelo Git)
```

Estrutura completa alvo (todos os incrementos I0–I7): ver Seção 7 de
[`proposta-projeto-v4.md`](proposta-projeto-v4.md).

## Verificação do ambiente (smoke test)

```powershell
.venv\Scripts\python src\dados\versoes.py --teste
```

Cria uma entrega, versiona, confirma que o histórico é preservado e desfaz tudo com
`ROLLBACK` — não grava dados permanentes. Usado para validar que a conexão MySQL e o
esquema estão corretos sem exigir acesso ao Denodo.

## Sincronização com o PETRVS

```powershell
.venv\Scripts\python src\dados\sincronizar_ref.py
```

Requer rede institucional (VPN) até o Denodo — falha com
`Connection error: Check the host name and port number are correct` fora dela. Populate
`ref_unidades` (todas as unidades) e `ref_usuarios` (apenas as unidades-piloto CGOV e
COCAGE, sem CPF/e-mail — ver [ADR-006](docs/gestao/decisoes/ADR-006-persistencia-mysql.md), D2).
