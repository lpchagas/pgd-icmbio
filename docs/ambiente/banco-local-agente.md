# Banco local do agente: backup, restauração e testes

O agente usa um MySQL 8.4 local (instância principal, porta 3306, banco `pgd_agente`).
Esta página cobre o backup diário, a restauração comprovada e o banco de teste.
Vigente desde o lote L6 da reorganização.

## Backup diário

- Script: `agente/dados/backup.ps1`, agendado na tarefa `pgd_agente_backup` (diária, nível
  de usuário).
- Credenciais: arquivo administrativo local no perfil do usuário, fora do Git. Ele só é
  usado pelo backup.
- **Destino:** variável de ambiente do usuário `PGD_BACKUP_DIR`.
  - Tem de ser um caminho absoluto, não a raiz de um disco e não uma pasta versionada.
    O script recusa os outros casos.
  - Sem a variável, o destino é `data\backups` na raiz do projeto, que é ignorada pelo Git.
- **Retenção:** 14 dias, aplicada só no destino validado e só a arquivos no padrão
  `pgd_agente_AAAAMMDD_HHMM.dump.sql`.

Conferir o destino sem gerar dump:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File agente\dados\backup.ps1 -SomenteValidar
```

## Instância isolada

O `schema.sql` e os dumps trazem `CREATE DATABASE`/`USE pgd_agente`: acrescentar `_teste`
ao nome não isola nada. Por isso, a restauração e os testes de schema usam uma **segunda
instância**:

- porta 3307, só em `127.0.0.1`;
- datadir próprio no perfil do usuário;
- sem serviço do Windows e sem binlog.

```powershell
agente\dados\mysql_isolada.ps1 inicializar   # uma vez: cria a instância e as contas
agente\dados\mysql_isolada.ps1 iniciar
agente\dados\mysql_isolada.ps1 parar
```

As contas geradas ficam em arquivos `.cnf` no diretório da instância e nunca são
impressas. O usuário de teste só tem privilégio em `pgd_agente_teste`.

## Restauração e banco de teste

```powershell
.venv\Scripts\python agente\dados\banco_teste.py restaurar --dump <arquivo .dump.sql>
.venv\Scripts\python agente\dados\banco_teste.py preparar
```

- `restaurar` confere antes de executar: servidor, porta, datadir, conta, `DATABASE()` e
  privilégios. Recusa a instância principal.
- `preparar` reescreve o schema para `pgd_agente_teste` e **recusa qualquer SQL que ainda
  cite `pgd_agente`**.
- Os dois relatam só a estrutura: tabelas, triggers, versão do schema e uma transação
  funcional (o trigger de imutabilidade bloqueia o UPDATE e o ROLLBACK restaura a
  contagem). Nenhum conteúdo é exibido.

Testes contra a instância isolada (opt-in):

```powershell
$env:PGD_MYSQL_TESTE = '1'; .venv\Scripts\python -m pytest -m mysql tests\agente
```

## Linux e WSL

Os scripts `.ps1` só rodam no Windows. No Linux/WSL, os equivalentes em
`agente/dados/` têm as mesmas regras de destino, retenção, porta e credenciais:

| Windows | Linux/WSL |
| --- | --- |
| `backup.ps1 -SomenteValidar` | `backup.sh --somente-validar` |
| `mysql_isolada.ps1 <ação>` | `mysql_isolada.sh <ação>` |
| tarefa `pgd_agente_backup` | timer de usuário do systemd `pgd-agente-backup` |

Diferenças do ambiente Linux:

- **Servidor:** pacote `mysql-server` da distribuição (instância principal na porta
  3306, iniciada pelo systemd). No WSL, o systemd precisa estar ativo.
- **Credenciais do backup:** `PGD_BACKUP_CNF`; sem a variável, `~/.pgd_agente.cnf`,
  conta com privilégios só em `pgd_agente` (o `root` do MySQL no Ubuntu autentica pelo
  sistema e não usa `.cnf`). O arquivo não pode ter a opção `database=`, que o
  `mysqldump` recusa.
- **Instância isolada:** diretório `PGD_MYSQL_ISOLADA_DIR`; sem a variável,
  `~/.local/share/pgd-icmbio/mysql-isolada` (o mesmo padrão de `banco_teste.py`). Roda
  como processo do usuário, com socket e datadir próprios. Se a inicialização falhar
  depois de ligar o servidor, o script o desliga antes de sair.
- **Binários:** `PGD_MYSQL_BIN` (cliente, padrão `/usr/bin`) e `PGD_MYSQLD` (servidor,
  padrão `/usr/sbin/mysqld`).

```bash
agente/dados/backup.sh --somente-validar
agente/dados/mysql_isolada.sh inicializar   # uma vez: cria a instância e as contas
agente/dados/mysql_isolada.sh iniciar
.venv/bin/python agente/dados/banco_teste.py restaurar --dump <arquivo .dump.sql>
.venv/bin/python agente/dados/banco_teste.py preparar
PGD_MYSQL_TESTE=1 .venv/bin/python -m pytest -m mysql tests/agente
```

Agendamento diário (timer de usuário do systemd; os arquivos ficam em
`~/.config/systemd/user/`, fora do Git):

```ini
# pgd-agente-backup.service
[Unit]
Description=Backup diário do banco pgd_agente

[Service]
Type=oneshot
WorkingDirectory=%h/projetos/pgd-icmbio
# Environment=PGD_BACKUP_DIR=/caminho/absoluto/fora/do/git
ExecStart=%h/projetos/pgd-icmbio/agente/dados/backup.sh

# pgd-agente-backup.timer
[Unit]
Description=Agenda o backup diário do banco pgd_agente

[Timer]
OnCalendar=*-*-* 19:00
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
systemctl --user daemon-reload
systemctl --user enable --now pgd-agente-backup.timer
systemctl --user list-timers pgd-agente-backup.timer
```

No WSL, o timer só dispara enquanto a distribuição está em execução; `Persistent=true`
faz o backup perdido rodar na próxima inicialização.
