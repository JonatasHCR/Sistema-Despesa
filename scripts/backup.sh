#!/bin/sh
set -e

BACKUP_DIR=/backups
INTERVAL=${BACKUP_INTERVAL_HOURS:-24}
KEEP=${BACKUP_KEEP:-7}

mkdir -p "$BACKUP_DIR"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

do_backup() {
  FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M).sql"
  log "Iniciando backup..."
  # --clean/--if-exists nao sao opcionais: sem os DROPs o arquivo so sabe
  # criar tabelas do zero, e restaurar por cima de um banco existente aplica
  # so os COPY que nao conflitam — foi assim que alembic_version ganhou uma
  # segunda linha e derrubou o backend.
  if PGPASSWORD="$POSTGRES_PASSWORD" pg_dump -h db -U "$POSTGRES_USER"       --clean --if-exists --no-owner --no-privileges "$POSTGRES_DB" > "$FILE"; then
    log "Backup salvo: $(basename "$FILE")"
    COUNT=$(ls -t "$BACKUP_DIR"/backup_*.sql 2>/dev/null | wc -l)
    if [ "$COUNT" -gt "$KEEP" ]; then
      ls -t "$BACKUP_DIR"/backup_*.sql | tail -n +$((KEEP + 1)) | xargs rm -f
      log "Rotação: removidos $((COUNT - KEEP)) backup(s) antigo(s), mantendo $KEEP"
    fi
  else
    log "ERRO: backup falhou"
    rm -f "$FILE"
  fi
}

log "Serviço de backup iniciado (intervalo: ${INTERVAL}h, retenção: ${KEEP} backups)"

while true; do
  do_backup
  log "Próximo backup em ${INTERVAL}h"
  sleep "$((INTERVAL * 3600))"
done
