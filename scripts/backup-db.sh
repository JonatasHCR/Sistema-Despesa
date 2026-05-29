#!/usr/bin/env bash
# Gera um pg_dump SQL do banco rodando via docker compose.
# Uso: ./scripts/backup-db.sh [diretorio_destino]
# Default destino: ./backups/

set -euo pipefail

DEST_DIR="${1:-./backups}"
mkdir -p "$DEST_DIR"

# Lê POSTGRES_USER/DB do .env (sem expor a senha — psql usa peer/trust dentro do container).
if [[ -f .env ]]; then
  # shellcheck disable=SC1091
  set -a; source .env; set +a
fi

: "${POSTGRES_USER:?POSTGRES_USER não definido (.env)}"
: "${POSTGRES_DB:?POSTGRES_DB não definido (.env)}"

TS=$(date +%Y%m%d_%H%M%S)
OUT="${DEST_DIR}/${POSTGRES_DB}_${TS}.sql"

echo "▶ Gerando dump em $OUT ..."
docker compose exec -T db pg_dump \
  -U "$POSTGRES_USER" \
  -d "$POSTGRES_DB" \
  --clean \
  --if-exists \
  --no-owner \
  --no-privileges \
  > "$OUT"

SIZE=$(du -h "$OUT" | cut -f1)
echo "✓ Backup salvo: $OUT ($SIZE)"
