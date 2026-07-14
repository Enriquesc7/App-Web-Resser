#!/usr/bin/env bash
# 05_systemd_service.sh — Install and start the resser systemd service
# Idempotent: safe to re-run
set -euo pipefail

APP_DIR="/home/ubuntu/App-Web-Resser"
SERVICE_FILE="/etc/systemd/system/resser.service"

echo "==================================================================="
echo "[05] Systemd Service — $(date)"
echo "==================================================================="

echo ">>> Writing $SERVICE_FILE..."
cat > "$SERVICE_FILE" << 'EOF'
[Unit]
Description=Resser FastAPI app
After=network.target postgresql.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/App-Web-Resser
Environment="PATH=/home/ubuntu/App-Web-Resser/venv/bin"
EnvironmentFile=/home/ubuntu/App-Web-Resser/.env
ExecStart=/home/ubuntu/App-Web-Resser/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --workers 2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo ">>> Reloading systemd daemon..."
systemctl daemon-reload

echo ">>> Enabling service to start on boot..."
systemctl enable resser

echo ">>> Starting service..."
systemctl restart resser

echo ">>> Waiting 4 seconds for startup..."
sleep 4

echo ">>> Service status:"
systemctl status resser --no-pager

echo ""
echo ">>> Checking app responds on 127.0.0.1:8000..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 http://127.0.0.1:8000/ || echo "FAILED")
echo "    HTTP response code: $HTTP_CODE"

if [ "$HTTP_CODE" = "FAILED" ]; then
  echo ""
  echo "ERROR: App did not respond. Last 50 log lines:"
  journalctl -u resser -n 50 --no-pager
  exit 1
fi

echo ""
echo "==================================================================="
echo "[05] Done. Service is active and responding."
echo "==================================================================="
