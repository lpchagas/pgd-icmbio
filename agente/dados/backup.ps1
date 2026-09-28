# backup.ps1 — Backup diário do banco pgd_agente (v4 §7; risco RP15; plano §10, L6)
# Agendado via Tarefas do Windows (tarefa "pgd_agente_backup", nível de usuário).
# Usa as credenciais administrativas locais em ~\.pgd_agente_root.cnf (fora do Git).
#
# Destino: $env:PGD_BACKUP_DIR — absoluto, nunca a raiz de um disco e nunca dentro de
# uma pasta versionada. Sem a variável, o padrão é <raiz do projeto>\data\backups
# (raiz = $PSScriptRoot subindo dois níveis; data/ é ignorada pelo Git).
# A retenção (14 dias) só atua no diretório validado e só em pgd_agente_*.dump.sql.
param(
    [string]$Destino = $env:PGD_BACKUP_DIR,
    [int]$RetencaoDias = 14,
    [switch]$SomenteValidar
)

$ErrorActionPreference = 'Stop'
$raiz = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
if ([string]::IsNullOrWhiteSpace($Destino)) { $Destino = Join-Path $raiz 'data\backups' }
if (-not [System.IO.Path]::IsPathRooted($Destino)) { throw 'PGD_BACKUP_DIR deve ser um caminho absoluto.' }
$Destino = [System.IO.Path]::GetFullPath($Destino).TrimEnd('\')
if ($Destino -eq [System.IO.Path]::GetPathRoot($Destino).TrimEnd('\')) { throw 'PGD_BACKUP_DIR não pode ser a raiz de um disco.' }
if ($RetencaoDias -lt 1) { throw 'A retenção deve ser de pelo menos 1 dia.' }

# Fora do Git: se o destino (ou o ancestral existente mais próximo) estiver numa árvore
# Git, só aceita quando o caminho é ignorado por ela (caso do padrão data\backups).
$existente = $Destino
while (-not (Test-Path -LiteralPath $existente)) { $existente = Split-Path $existente -Parent }
# (no PowerShell 5.1, o stderr de um executável vira erro fatal sob 'Stop')
$ErrorActionPreference = 'Continue'
$arvore = git -C $existente rev-parse --show-toplevel 2>$null
$dentroDoGit = $LASTEXITCODE -eq 0 -and $arvore
if ($dentroDoGit) { git -C $existente check-ignore -q --no-index -- $Destino 2>$null; $ignorado = $LASTEXITCODE -eq 0 }
$ErrorActionPreference = 'Stop'
if ($dentroDoGit -and -not $ignorado) { throw 'PGD_BACKUP_DIR está dentro de uma pasta versionada e não é ignorado pelo Git.' }
if ($SomenteValidar) { "destino validado: $Destino"; return }

$cnf     = Join-Path $env:USERPROFILE '.pgd_agente_root.cnf'
$dump    = 'C:\Program Files\MySQL\MySQL Server 8.4\bin\mysqldump.exe'
$stamp   = Get-Date -Format 'yyyyMMdd_HHmm'
$arquivo = Join-Path $Destino "pgd_agente_$stamp.dump.sql"

New-Item -ItemType Directory -Force $Destino | Out-Null

& $dump --defaults-extra-file=$cnf --databases pgd_agente --routines --triggers `
    --result-file=$arquivo
if ($LASTEXITCODE -ne 0) { throw "mysqldump falhou (exit $LASTEXITCODE)" }

# Retenção: remove, só no destino validado, dumps com mais de $RetencaoDias dias
Get-ChildItem -LiteralPath $Destino -Filter 'pgd_agente_*.dump.sql' -File |
    Where-Object { $_.Name -match '^pgd_agente_\d{8}_\d{4}\.dump\.sql$' -and $_.LastWriteTime -lt (Get-Date).AddDays(-$RetencaoDias) } |
    Remove-Item -Force

"$(Get-Date -Format o) backup ok: $arquivo" |
    Out-File -LiteralPath (Join-Path $Destino 'backup.log') -Append -Encoding utf8
