#!/usr/bin/env bash
# 01_system_setup.sh — Install system dependencies
# Idempotent: safe to re-run
set -euo pipefail

echo "==================================================================="
echo "[01] System Setup — $(date)"
echo "==================================================================="

export DEBIAN_FRONTEND=noninteractive

echo ">>> Updating package lists..."
apt-get update -q

echo ">>> Upgrading installed packages (non-interactive)..."
apt-get upgrade -y -q \
  -o Dpkg::Options::="--force-confold" \
  -o Dpkg::Options::="--force-confdef"

echo ">>> Installing required packages..."
apt-get install -y -q \
  python3 \
  python3-venv \
  python3-dev \
  python3-pip \
  postgresql \
  postgresql-contrib \
  nginx \
  tesseract-ocr \
  tesseract-ocr-fra \
  git \
  build-essential \
  libpq-dev \
  libjpeg-dev \
  zlib1g-dev \
  curl

echo ">>> Enabling and starting postgresql..."
systemctl enable postgresql
systemctl start postgresql

echo ">>> Enabling and starting nginx..."
systemctl enable nginx
systemctl start nginx

echo ""
echo ">>> Verification:"
echo -n "  python3: "; python3 --version
echo -n "  psql:    "; psql --version
echo -n "  nginx:   "; nginx -v 2>&1
echo -n "  tesseract: "; tesseract --version 2>&1 | head -1
echo "  tesseract langs available:"
tesseract --list-langs 2>&1

echo ""
echo "==================================================================="
echo "[01] Done."
echo "==================================================================="
