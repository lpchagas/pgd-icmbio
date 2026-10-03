#!/usr/bin/env bash
# backup.sh — Backup diário do banco pgd_agente no Linux/WSL (equivalente a backup.ps1).
# Agendado pelo timer de usuário do systemd "pgd-agente-backup" (ver
# docs/ambiente/banco-local-agente.md).
# Credenciais: $PGD_BACKUP_CNF (arquivo .cnf local, fora do Git). Sem a variável, usa
# ~/.pgd_agente.cnf, a conta com privilégios só em pgd_agente.
#
# Destino: $PGD_BACKUP_DIR — absoluto, nunca a raiz do sistema e nunca dentro de uma
# pasta versionada. Sem a variável, o padrão é <raiz do projeto>/data/backups
# (data/ é ignorada pelo Git).
# A retenção (14 dias) só atua no diretório validado e só em pgd_agente_*.dump.sql.
#
# Uso: backup.sh [--destino DIR] [--retencao-dias N] [--somente-validar]
set -euo pipefail

raiz="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
destino="${PGD_BACKUP_DIR:-}"
retencao=14
somente_validar=0

while [ $# -gt 0 ]; do
    case "$1" in
        --destino) destino="${2:-}"; shift 2 ;;
        --retencao-dias) retencao="${2:-}"; shift 2 ;;
        --somente-validar) somente_validar=1; shift ;;
        *) echo "Opção desconhecida: $1" >&2; exit 2 ;;
    esac
done

falhar() { echo "$1" >&2; exit 1; }

[ -n "$destino" ] || destino="$raiz/data/backups"
case "$destino" in /*) ;; *) falhar 'PGD_BACKUP_DIR deve ser um caminho absoluto.' ;; esac
destino="$(realpath -m -- "$destino")"
[ "$destino" != "/" ] || falhar 'PGD_BACKUP_DIR não pode ser a raiz do sistema.'
[[ "$retencao" =~ ^[0-9]+$ ]] && [ "$retencao" -ge 1 ] || falhar 'A retenção deve ser de pelo menos 1 dia.'

# Fora do Git: se o destino (ou o ancestral existente mais próximo) estiver numa árvore
# Git, só aceita quando o caminho é ignorado por ela (caso do padrão data/backups).
existente="$destino"
while [ ! -e "$existente" ]; do existente="$(dirname -- "$existente")"; done
if git -C "$existente" rev-parse --show-toplevel >/dev/null 2>&1; then
    git -C "$existente" check-ignore -q --no-index -- "$destino" 2>/dev/null \
        || falhar 'PGD_BACKUP_DIR está dentro de uma pasta versionada e não é ignorado pelo Git.'
fi
if [ "$somente_validar" = 1 ]; then echo "destino validado: $destino"; exit 0; fi

cnf="${PGD_BACKUP_CNF:-$HOME/.pgd_agente.cnf}"
[ -f "$cnf" ] || falhar "Credencial do backup ausente: $(basename -- "$cnf")"
dump="${PGD_MYSQL_BIN:-/usr/bin}/mysqldump"
arquivo="$destino/pgd_agente_$(date +%Y%m%d_%H%M).dump.sql"

mkdir -p -- "$destino"
umask 077
# --no-tablespaces: dispensa o privilégio global PROCESS (a conta só enxerga pgd_agente).
"$dump" --defaults-extra-file="$cnf" --databases pgd_agente --routines --triggers \
    --no-tablespaces --single-transaction --result-file="$arquivo" \
    || falhar "mysqldump falhou (exit $?)"

# Retenção: remove, só no destino validado, dumps com mais de $retencao dias
find "$destino" -maxdepth 1 -type f -regextype posix-extended \
    -regex '.*/pgd_agente_[0-9]{8}_[0-9]{4}\.dump\.sql' -mtime "+$((retencao - 1))" -delete

echo "$(date -Iseconds) backup ok: $arquivo" >> "$destino/backup.log"
