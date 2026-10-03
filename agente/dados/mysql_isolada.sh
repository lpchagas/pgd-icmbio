#!/usr/bin/env bash
# mysql_isolada.sh — Segunda instância MySQL local no Linux/WSL, isolada da principal
# (equivalente a mysql_isolada.ps1).
#
# Porta 3307, só 127.0.0.1, datadir e socket próprios, processo do usuário (sem serviço
# do sistema) e sem binlog. Usada para a restauração fiel dos backups e para os testes
# de schema (-m mysql). Credenciais geradas aqui ficam em root.cnf e teste.cnf no
# diretório da instância (fora do Git, permissão 600); nunca são impressas. O usuário de
# teste só tem privilégio em pgd_agente_teste.
#
# Diretório: $PGD_MYSQL_ISOLADA_DIR; sem a variável,
# ${XDG_DATA_HOME:-~/.local/share}/pgd-icmbio/mysql-isolada.
# Binários: $PGD_MYSQL_BIN (cliente) e $PGD_MYSQLD (servidor); padrão /usr/bin e
# /usr/sbin/mysqld.
#
# Uso: mysql_isolada.sh inicializar | iniciar | parar | status
set -euo pipefail

acao="${1:-}"
case "$acao" in inicializar|iniciar|parar|status) ;; *) echo "Uso: $0 inicializar|iniciar|parar|status" >&2; exit 2 ;; esac

bin="${PGD_MYSQL_BIN:-/usr/bin}"
mysqld="${PGD_MYSQLD:-/usr/sbin/mysqld}"
base="${PGD_MYSQL_ISOLADA_DIR:-${XDG_DATA_HOME:-$HOME/.local/share}/pgd-icmbio/mysql-isolada}"
porta=3307
ini="$base/my.cnf"
dados="$base/data"
root="$base/root.cnf"
teste="$base/teste.cnf"

ativa() {
    [ -f "$root" ] || return 1
    "$bin/mysqladmin" --defaults-extra-file="$root" --protocol=TCP --connect-timeout=2 ping >/dev/null 2>&1
}

nova_senha() {
    # Alfabeto sem caracteres ambíguos; 24 caracteres de fonte criptográfica. Lê um bloco
    # finito: "tr < /dev/urandom | head" morre por SIGPIPE e derruba o script sob pipefail.
    local s=""
    while [ "${#s}" -lt 24 ]; do
        s+="$(head -c 1024 /dev/urandom | LC_ALL=C tr -dc 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789')"  # pragma: allowlist secret (alfabeto, não é segredo)
    done
    printf '%s' "${s:0:24}"
}

escrever_cnf() {  # caminho usuário senha
    (umask 077; printf '[client]\nuser=%s\npassword=%s\nhost=127.0.0.1\nport=%s\n' "$2" "$3" "$porta" > "$1")
}

iniciar() {
    ativa && return 0
    "$mysqld" --defaults-file="$ini" --daemonize >/dev/null 2>&1 \
        || { echo "mysqld não iniciou (ver $base/erro.log)." >&2; exit 1; }
    for _ in $(seq 30); do
        sleep 1
        "$bin/mysqladmin" --protocol=TCP -h 127.0.0.1 -P "$porta" --connect-timeout=1 ping >/dev/null 2>&1 && return 0
    done
    echo "Instância isolada não respondeu na porta $porta (ver $base/erro.log)." >&2
    exit 1
}

case "$acao" in
    inicializar)
        [ ! -e "$dados" ] || { echo "Instância já inicializada em $base." >&2; exit 1; }
        mkdir -p -- "$base"
        chmod 700 -- "$base"
        cat > "$ini" <<EOF
[mysqld]
datadir=$dados
port=$porta
bind-address=127.0.0.1
socket=$base/mysqld.sock
pid-file=$base/mysqld.pid
mysqlx=OFF
secure-file-priv=NULL
skip-log-bin
character-set-server=utf8mb4
collation-server=utf8mb4_unicode_ci
default-storage-engine=InnoDB
max_connections=20
log-error=$base/erro.log

[client]
port=$porta
EOF
        "$mysqld" --defaults-file="$ini" --initialize-insecure >/dev/null 2>&1 \
            || { echo "mysqld --initialize-insecure falhou (ver $base/erro.log)." >&2; exit 1; }
        iniciar
        # Até as contas terem senha, o root não tem: qualquer falha desliga a instância.
        trap '"$bin/mysqladmin" --protocol=TCP -h 127.0.0.1 -P "$porta" -u root shutdown >/dev/null 2>&1 || true' EXIT
        senha_root="$(nova_senha)"
        senha_teste="$(nova_senha)"
        # SQL pela entrada padrão: as senhas não aparecem em argumentos nem em arquivo.
        "$bin/mysql" --protocol=TCP -h 127.0.0.1 -P "$porta" -u root <<EOF || { echo 'Configuração inicial das contas falhou.' >&2; exit 1; }
ALTER USER 'root'@'localhost' IDENTIFIED BY '$senha_root';
CREATE USER 'pgd_teste'@'localhost' IDENTIFIED BY '$senha_teste';
GRANT ALL PRIVILEGES ON \`pgd_agente_teste\`.* TO 'pgd_teste'@'localhost';
FLUSH PRIVILEGES;
EOF
        escrever_cnf "$root" root "$senha_root"
        escrever_cnf "$teste" pgd_teste "$senha_teste"
        trap - EXIT
        echo "Instância isolada inicializada em $base (porta $porta)."
        ;;
    iniciar) iniciar; echo "Instância isolada ativa na porta $porta." ;;
    parar)
        if ! ativa; then echo "Instância isolada já parada."; exit 0; fi
        "$bin/mysqladmin" --defaults-extra-file="$root" --protocol=TCP shutdown
        echo "Instância isolada parada."
        ;;
    status) if ativa; then echo "ativa (porta $porta, $base)"; else echo "parada ($base)"; fi ;;
esac
