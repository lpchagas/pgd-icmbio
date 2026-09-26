# backup.ps1 — Backup diário do banco pgd_agente (v4 §7; risco RP15)
# Agendado via Tarefas do Windows (tarefa "pgd_agente_backup", nível de usuário).
# Usa as credenciais administrativas locais em ~\.pgd_agente_root.cnf (fora do Git).
# Retém 14 dias de dumps em data/backups/ (pasta ignorada pelo Git).

$ErrorActionPreference = 'Stop'
$repo    = 'C:\Projetos\pgd-agente-icmbio'
$destino = Join-Path $repo 'data\backups'
$cnf     = Join-Path $env:USERPROFILE '.pgd_agente_root.cnf'
$dump    = 'C:\Program Files\MySQL\MySQL Server 8.4\bin\mysqldump.exe'
$stamp   = Get-Date -Format 'yyyyMMdd_HHmm'
$arquivo = Join-Path $destino "pgd_agente_$stamp.dump.sql"

New-Item -ItemType Directory -Force $destino | Out-Null

& $dump --defaults-extra-file=$cnf --databases pgd_agente --routines --triggers `
    --result-file=$arquivo
if ($LASTEXITCODE -ne 0) { throw "mysqldump falhou (exit $LASTEXITCODE)" }

# Retenção: remove dumps com mais de 14 dias
Get-ChildItem $destino -Filter 'pgd_agente_*.dump.sql' |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-14) } |
    Remove-Item -Force

"$(Get-Date -Format o) backup ok: $arquivo" |
    Out-File (Join-Path $destino 'backup.log') -Append -Encoding utf8
