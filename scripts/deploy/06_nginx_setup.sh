#!/usr/bin/env bash
# 06_nginx_setup.sh — Configure Nginx as reverse proxy on port 80
# Idempotent: safe to re-run
set -euo pipefail

SITE_CONF="/etc/nginx/sites-available/resser"

echo "==================================================================="
echo "[06] Nginx Setup — $(date)"
echo "==================================================================="

echo ">>> Writing $SITE_CONF..."
cat > "$SITE_CONF" << 'EOF'
server {
    listen 80 default_server;
    server_name _;

    client_max_body_size 20M;

    location / {
        proxy_pass         http://127.0.0.1:8000;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }
}
EOF

echo ">>> Removing default site..."
rm -f /etc/nginx/sites-enabled/default

echo ">>> Enabling resser site..."
ln -sf "$SITE_CONF" /etc/nginx/sites-enabled/resser

echo ">>> Testing nginx configuration..."
nginx -t

echo ">>> Reloading nginx..."
systemctl reload nginx

echo ">>> Verifying public access..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 http://127.0.0.1/ || echo "FAILED")
echo "    HTTP response code from nginx: $HTTP_CODE"

if [ "$HTTP_CODE" = "FAILED" ]; then
  echo "ERROR: nginx is not proxying correctly."
  journalctl -u nginx -n 20 --no-pager
  exit 1
fi

echo ""
echo "==================================================================="
echo "[06] Done. Nginx is live on port 80."
echo "    Public URL: http://13.38.119.28"
echo "==================================================================="
