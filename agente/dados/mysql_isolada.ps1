# mysql_isolada.ps1 — Segunda instância MySQL local, isolada da principal (plano §10, L6).
#
# Porta 3307, só 127.0.0.1, datadir próprio, sem serviço do Windows e sem binlog.
# Usada para a restauração fiel dos backups e para os testes de schema (-m mysql).
# Credenciais geradas aqui ficam em root.cnf e teste.cnf no diretório da instância
# (fora do Git, perfil do usuário); nunca são impressas. O usuário de teste só tem
# privilégio em pgd_agente_teste.
#
# Uso: mysql_isolada.ps1 inicializar | iniciar | parar | status
param([Parameter(Mandatory)][ValidateSet('inicializar', 'iniciar', 'parar', 'status')][string]$Acao)

$ErrorActionPreference = 'Stop'
$bin = if ($env:PGD_MYSQL_BIN) { $env:PGD_MYSQL_BIN } else { 'C:\Program Files\MySQL\MySQL Server 8.4\bin' }
$base = if ($env:PGD_MYSQL_ISOLADA_DIR) { $env:PGD_MYSQL_ISOLADA_DIR } else { Join-Path $env:LOCALAPPDATA 'pgd-icmbio\mysql-isolada' }
$porta = 3307
$ini = Join-Path $base 'my.ini'
$dados = Join-Path $base 'data'
$root = Join-Path $base 'root.cnf'
$teste = Join-Path $base 'teste.cnf'

function Test-Ativa {
    $ErrorActionPreference = 'Continue'  # no PowerShell 5.1, stderr do executável vira erro sob 'Stop'
    if (-not (Test-Path $root)) { return $false }
    & (Join-Path $bin 'mysqladmin.exe') "--defaults-extra-file=$root" --protocol=TCP --connect-timeout=2 ping 2>$null | Out-Null
    return $LASTEXITCODE -eq 0
}

function New-Senha {
    $bytes = [byte[]]::new(24)
    [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)  # também no PowerShell 5.1
    return (-join ($bytes | ForEach-Object { 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789'[$_ % 57] }))  # pragma: allowlist secret (alfabeto, não é segredo)
}

function Write-Cnf([string]$Caminho, [string]$Usuario, [string]$Senha) {
    "[client]`nuser=$Usuario`npassword=$Senha`nhost=127.0.0.1`nport=$porta`n" |
        Set-Content -Path $Caminho -Encoding ascii -NoNewline
}

function Start-Instancia {
    if (Test-Ativa) { return }
    Start-Process -FilePath (Join-Path $bin 'mysqld.exe') -ArgumentList "--defaults-file=`"$ini`"" -WindowStyle Hidden
    $ErrorActionPreference = 'Continue'
    foreach ($i in 1..30) {
        Start-Sleep -Seconds 1
        & (Join-Path $bin 'mysqladmin.exe') --protocol=TCP -h 127.0.0.1 -P $porta --connect-timeout=1 ping 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) { return }
    }
    throw "Instância isolada não respondeu na porta $porta (ver $base\erro.log)."
}

switch ($Acao) {
    'inicializar' {
        if (Test-Path $dados) { throw "Instância já inicializada em $base." }
        New-Item -ItemType Directory -Force $base | Out-Null
        $basedir = (Split-Path $bin -Parent) -replace '\\', '/'
        $b = $base -replace '\\', '/'
        @"
[mysqld]
basedir="$basedir"
datadir="$b/data"
port=$porta
bind-address=127.0.0.1
mysqlx=OFF
skip-log-bin
character-set-server=utf8mb4
collation-server=utf8mb4_unicode_ci
default-storage-engine=InnoDB
max_connections=20
log-error="$b/erro.log"

[client]
port=$porta
"@ | Set-Content -Path $ini -Encoding ascii
        & (Join-Path $bin 'mysqld.exe') "--defaults-file=$ini" --initialize-insecure 2>$null
        if ($LASTEXITCODE -ne 0) { throw "mysqld --initialize-insecure falhou (ver $base\erro.log)." }
        Start-Instancia
        $senhaRoot = New-Senha
        $senhaTeste = New-Senha
        $sql = Join-Path $base 'configurar.sql'
        @"
ALTER USER 'root'@'localhost' IDENTIFIED BY '$senhaRoot';
CREATE USER 'pgd_teste'@'localhost' IDENTIFIED BY '$senhaTeste';
GRANT ALL PRIVILEGES ON ``pgd_agente_teste``.* TO 'pgd_teste'@'localhost';
FLUSH PRIVILEGES;
"@ | Set-Content -Path $sql -Encoding ascii
        try {
            Get-Content $sql -Raw | & (Join-Path $bin 'mysql.exe') --protocol=TCP -h 127.0.0.1 -P $porta -u root
            if ($LASTEXITCODE -ne 0) { throw 'Configuração inicial das contas falhou.' }
        } finally { Remove-Item $sql -Force }
        Write-Cnf $root 'root' $senhaRoot
        Write-Cnf $teste 'pgd_teste' $senhaTeste
        "Instância isolada inicializada em $base (porta $porta)."
    }
    'iniciar' { Start-Instancia; "Instância isolada ativa na porta $porta." }
    'parar' {
        if (-not (Test-Ativa)) { "Instância isolada já parada."; break }
        & (Join-Path $bin 'mysqladmin.exe') "--defaults-extra-file=$root" --protocol=TCP shutdown
        "Instância isolada parada."
    }
    'status' { if (Test-Ativa) { "ativa (porta $porta, $base)" } else { "parada ($base)" } }
}
