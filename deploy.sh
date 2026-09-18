#!/usr/bin/env bash
#
# One-command deploy/update for the Jacqueline Magawa portfolio on a VPS.
# Pulls latest code, installs backend deps, syncs the static site, and restarts services.
#
# Usage:  sudo bash /opt/jacq/deploy.sh
#
# Assumes the VPS layout from VPS_AND_BACKEND_HOSTING.md:
#   - repo cloned at        /opt/jacq
#   - python venv at        /opt/jacq/backend/venv
#   - static web root at    /var/www/jacqmagawa
#   - systemd unit named    jacq-api
#
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/jacq}"
WEB_ROOT="${WEB_ROOT:-/var/www/jacqmagawa}"
SERVICE="${SERVICE:-jacq-api}"
STATIC_ITEMS=(index.html css js assets sitemap.xml robots.txt googlee2baf0cc1b65fae8.html)

if [[ $EUID -ne 0 ]]; then
  echo "Please run with sudo (needs to restart services): sudo bash $0"
  exit 1
fi

echo "==> [1/5] Pulling latest code in $APP_DIR"
cd "$APP_DIR"
git pull --ff-only

echo "==> [2/5] Installing backend dependencies"
"$APP_DIR/backend/venv/bin/pip" install -q --upgrade pip
"$APP_DIR/backend/venv/bin/pip" install -q -r "$APP_DIR/backend/requirements.txt"

echo "==> [3/5] Syncing static files to $WEB_ROOT"
mkdir -p "$WEB_ROOT"
for item in "${STATIC_ITEMS[@]}"; do
  if [[ -e "$APP_DIR/$item" ]]; then
    cp -a "$APP_DIR/$item" "$WEB_ROOT/"
    echo "    synced: $item"
  fi
done

echo "==> [4/5] Restarting backend service ($SERVICE)"
systemctl restart "$SERVICE"

echo "==> [5/5] Reloading Nginx"
nginx -t && systemctl reload nginx

echo "==> Health check"
sleep 2
if curl -fsS http://127.0.0.1:8001/api/health >/dev/null; then
  echo "    backend healthy ✔"
else
  echo "    WARNING: backend health check failed — check: journalctl -u $SERVICE -n 50"
  exit 1
fi

echo "==> Deploy complete ✅  https://jacqmagawa.com"
