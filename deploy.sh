#!/bin/bash
set -e

echo "=== ShopWriter AI Deploy ==="

# Backend
echo "→ Installing backend dependencies..."
cd /root/shopwriter/backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Bot
echo "→ Installing bot dependencies..."
cd /root/shopwriter/bot
python3 -m venv .venv
.venv/bin/pip install aiogram httpx pydantic-settings

# Frontend
echo "→ Building frontend..."
cd /root/shopwriter/frontend
npm install
npm run build

# Nginx
echo "→ Setting up Nginx..."
cp /root/shopwriter/nginx.conf /etc/nginx/sites-available/shopwriter
ln -sf /etc/nginx/sites-available/shopwriter /etc/nginx/sites-enabled/shopwriter
nginx -t && systemctl reload nginx

# PM2
echo "→ Starting PM2 apps..."
cd /root/shopwriter
pm2 start ecosystem.config.js
pm2 save

echo "=== Deploy complete ==="
echo "Run: certbot --nginx -d shopwriter.botapps.pro"
