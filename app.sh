#!/bin/sh
set -eu

APP_MODULE="${APP_MODULE:-main:app}"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8888}"
WORKERS="${WORKERS:-1}"

if [ -f requirements.txt ]; then
  python -m pip install --upgrade pip
  python -m pip install -r requirements.txt
fi

exec uvicorn "$APP_MODULE" --host "$HOST" --port "$PORT" --workers "$WORKERS"
