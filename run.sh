#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

cleanup() {
  if [[ -n "${BACKEND_PID:-}" ]] && kill -0 "$BACKEND_PID" 2>/dev/null; then
    kill "$BACKEND_PID" 2>/dev/null || true
  fi

  if [[ -n "${FRONTEND_PID:-}" ]] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
    kill "$FRONTEND_PID" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

echo "Iniciando backend en http://127.0.0.1:8000 ..."
python -m uvicorn backend.server:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

echo "Iniciando frontend estático en http://127.0.0.1:5173 ..."
python -m http.server 5173 &
FRONTEND_PID=$!

echo
echo "Simulador disponible en: http://127.0.0.1:5173/frontend/"
echo "Presiona Ctrl+C para detener ambos servicios."

echo
wait "$BACKEND_PID" "$FRONTEND_PID"
