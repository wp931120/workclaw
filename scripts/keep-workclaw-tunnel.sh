#!/usr/bin/env bash
set -euo pipefail
cd /Users/wp931120/project/my_work/workclaw/frontend
HOST="workclaw-wp931120.loca.lt"
URL="https://${HOST}"

# Ensure backend is alive on 8010
if ! curl -fsS --max-time 5 http://127.0.0.1:8010/api/v1/health >/dev/null 2>&1; then
  cd /Users/wp931120/project/my_work/workclaw/backend
  nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8010 > /tmp/workclaw-backend.log 2>&1 &
  echo $! > /tmp/workclaw-backend.pid
  sleep 3
fi

# Ensure frontend is alive on 3010
if ! curl -fsS --max-time 5 http://127.0.0.1:3010 >/dev/null 2>&1; then
  cd /Users/wp931120/project/my_work/workclaw/frontend
  nohup npm run dev -- --host 0.0.0.0 --port 3010 > /tmp/workclaw-frontend.log 2>&1 &
  echo $! > /tmp/workclaw-frontend.pid
  sleep 5
fi

# Ensure localtunnel public URL works
if ! curl -fsS -L --max-time 15 "${URL}/api/v1/health" >/dev/null 2>&1; then
  if [ -f /tmp/workclaw-localtunnel.pid ] && kill -0 "$(cat /tmp/workclaw-localtunnel.pid)" 2>/dev/null; then
    kill "$(cat /tmp/workclaw-localtunnel.pid)" || true
    sleep 2
  fi
  cd /Users/wp931120/project/my_work/workclaw/frontend
  nohup npx --yes localtunnel --port 3010 --subdomain workclaw-wp931120 > /tmp/workclaw-localtunnel.log 2>&1 &
  echo $! > /tmp/workclaw-localtunnel.pid
fi

echo "$(date '+%F %T') WorkClaw tunnel keepalive checked: ${URL}"
