#!/usr/bin/env bash
set -euo pipefail

cd /app

echo "[entrypoint] Iniciando…"

# --- Config por entorno (con defaults) ---
DB_PATH="${DB_PATH:-/app/db/hotel.db}"          # archivo SQLite final
SCHEMA_PATH="${SCHEMA_PATH:-DB/schema.sql}"     # ruta schema
SEED_PATH="${SEED_PATH:-DB/seed.sql}"           # ruta seed
FORCE_DB_RELOAD="${FORCE_DB_RELOAD:-0}"         # 0=no, 1=sí
PORT="${PORT:-8000}"

# --- Preparar carpeta de base ---
mkdir -p "$(dirname "$DB_PATH")"

# --- Crear/cargar base si falta o si se fuerza ---
if [ ! -f "$DB_PATH" ] || [ "$FORCE_DB_RELOAD" = "1" ]; then
  if [ -f "$DB_PATH" ]; then
    echo "[entrypoint] Borrando DB existente (FORCE_DB_RELOAD=1): $DB_PATH"
    rm -f "$DB_PATH"
  fi

  echo "[entrypoint] Creando nueva DB en: $DB_PATH"

  if [ -f "$SCHEMA_PATH" ]; then
    echo "[entrypoint] Cargando schema: $SCHEMA_PATH"
    sqlite3 "$DB_PATH" < "$SCHEMA_PATH"
  else
    echo "[entrypoint][WARN] No se encontró schema en $SCHEMA_PATH"
  fi

  if [ -f "$SEED_PATH" ]; then
    echo "[entrypoint] Cargando seed: $SEED_PATH"
    sqlite3 "$DB_PATH" < "$SEED_PATH"
  else
    echo "[entrypoint][WARN] No se encontró seed en $SEED_PATH"
  fi
else
  echo "[entrypoint] DB existente detectada: $DB_PATH (no recargo)"
fi

# --- Arrancar Django ---
echo "[entrypoint] Ejecutando runserver en 0.0.0.0:${PORT}"
exec uv run python manage.py runserver "0.0.0.0:${PORT}"
