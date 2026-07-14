#!/usr/bin/env bash
# 02_database_setup.sh — Create PostgreSQL user and database
# Reads DB_USER, DB_PASSWORD, DB_NAME from /home/ubuntu/App-Web-Resser/.env
# Idempotent: safe to re-run
set -euo pipefail

ENV_FILE="/home/ubuntu/App-Web-Resser/.env"

echo "==================================================================="
echo "[02] Database Setup — $(date)"
echo "==================================================================="

if [ ! -f "$ENV_FILE" ]; then
  echo "ERROR: $ENV_FILE not found. Transfer .env.production first via SCP."
  exit 1
fi

# Read vars from .env (strip quotes and export)
DB_USER=$(grep '^DB_USER=' "$ENV_FILE" | cut -d= -f2 | tr -d '"'"'"' ')
DB_PASSWORD=$(grep '^DB_PASSWORD=' "$ENV_FILE" | cut -d= -f2 | tr -d '"'"'"' ')
DB_NAME=$(grep '^DB_NAME=' "$ENV_FILE" | cut -d= -f2 | tr -d '"'"'"' ')

echo ">>> Config: user=$DB_USER  db=$DB_NAME"

echo ">>> Creating role '$DB_USER' (skip if exists)..."
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" \
  | grep -q 1 \
  || sudo -u postgres psql -c "CREATE ROLE $DB_USER WITH LOGIN PASSWORD '$DB_PASSWORD';"

echo ">>> Setting/refreshing password for '$DB_USER'..."
sudo -u postgres psql -c "ALTER ROLE $DB_USER WITH PASSWORD '$DB_PASSWORD';"

echo ">>> Creating database '$DB_NAME' owned by '$DB_USER' (skip if exists)..."
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" \
  | grep -q 1 \
  || sudo -u postgres createdb -O "$DB_USER" "$DB_NAME"

echo ">>> Testing connection as $DB_USER..."
PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USER" -d "$DB_NAME" -h localhost -c "SELECT version();"

echo ""
echo "==================================================================="
echo "[02] Done. Database is ready."
echo "==================================================================="
