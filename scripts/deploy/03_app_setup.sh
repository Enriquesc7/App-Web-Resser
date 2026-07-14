#!/usr/bin/env bash
# 03_app_setup.sh — Clone repo, create venv, install deps, create DB tables
# Idempotent: safe to re-run
set -euo pipefail

APP_DIR="/home/ubuntu/App-Web-Resser"
REPO_URL="https://github.com/Enriquesc7/App-Web-Resser.git"
VENV="$APP_DIR/venv"

echo "==================================================================="
echo "[03] App Setup — $(date)"
echo "==================================================================="

# ── Clone or update repo ────────────────────────────────────────────────
if [ -d "$APP_DIR/.git" ]; then
  echo ">>> Repo already exists — pulling latest..."
  cd "$APP_DIR"
  # Warn about unexpected files before pulling
  UNTRACKED=$(git status --short --untracked-files=no | grep -v '\.env' || true)
  if [ -n "$UNTRACKED" ]; then
    echo "WARNING: Unexpected tracked changes in repo:"
    echo "$UNTRACKED"
    echo "Proceeding with git pull (untracked files left as-is)..."
  fi
  git pull --ff-only
else
  echo ">>> Cloning repository..."
  git clone "$REPO_URL" "$APP_DIR"
  cd "$APP_DIR"
fi

echo ""
echo ">>> Repo HEAD: $(git log -1 --oneline)"

# Check for unexpected sensitive files
if [ -f "$APP_DIR/.claude" ] || [ -d "$APP_DIR/.claude" ]; then
  echo "WARNING: .claude/ directory found in repo. Review before proceeding."
fi

# ── .env check ─────────────────────────────────────────────────────────
if [ ! -f "$APP_DIR/.env" ]; then
  echo "ERROR: $APP_DIR/.env not found. Run SCP first."
  exit 1
fi
echo ">>> .env present."

# ── Create virtual environment ──────────────────────────────────────────
if [ ! -d "$VENV" ]; then
  echo ">>> Creating Python venv..."
  python3 -m venv "$VENV"
else
  echo ">>> Venv already exists — skipping creation."
fi

# ── Install Python dependencies ─────────────────────────────────────────
echo ">>> Installing requirements (this may take a minute)..."
"$VENV/bin/pip" install --upgrade pip --quiet
"$VENV/bin/pip" install -r "$APP_DIR/requirements.txt" --quiet

echo ">>> Key packages installed:"
"$VENV/bin/pip" show fastapi uvicorn sqlalchemy pydantic psycopg2-binary pytesseract \
  | grep -E '^(Name|Version):' | paste - -

# ── Upload directory ────────────────────────────────────────────────────
echo ">>> Creating upload directories..."
mkdir -p "$APP_DIR/static/uploads/receipts"
chmod 755 "$APP_DIR/static/uploads/receipts"
chown -R ubuntu:ubuntu "$APP_DIR/static"

# ── Create DB tables (via SQLAlchemy create_all) ────────────────────────
# NOTE: No alembic migrations exist in this project.
# Tables are created directly via Base.metadata.create_all() when the app starts.
# We trigger it here explicitly so we can verify before starting uvicorn.
echo ">>> Creating database tables..."
cd "$APP_DIR"
"$VENV/bin/python" -c "
import sys
sys.path.insert(0, '.')
from db import engine, Base

# Import all models so they register with Base.metadata
import models.user
import models.receipt

Base.metadata.create_all(bind=engine)
print('Tables created (or already exist).')
"

# ── Show tables ─────────────────────────────────────────────────────────
echo ">>> Tables in database:"
DB_USER=$(grep '^DB_USER=' "$APP_DIR/.env" | cut -d= -f2 | tr -d '"'"'"' ')
DB_PASSWORD=$(grep '^DB_PASSWORD=' "$APP_DIR/.env" | cut -d= -f2 | tr -d '"'"'"' ')
DB_NAME=$(grep '^DB_NAME=' "$APP_DIR/.env" | cut -d= -f2 | tr -d '"'"'"' ')
PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USER" -d "$DB_NAME" -h localhost -c "\dt"

echo ""
echo "==================================================================="
echo "[03] Done. App is set up."
echo "==================================================================="
