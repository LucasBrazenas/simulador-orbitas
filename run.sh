#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

resolve_python() {
  if [[ -x "$ROOT_DIR/.venv/bin/python" ]]; then
    printf '%s\n' "$ROOT_DIR/.venv/bin/python"
    return 0
  fi

  if command -v python3 >/dev/null 2>&1; then
    command -v python3
    return 0
  fi

  if command -v python >/dev/null 2>&1; then
    command -v python
    return 0
  fi

  return 1
}

cleanup() {
  if [[ -n "${BACKEND_PID:-}" ]] && kill -0 "$BACKEND_PID" 2>/dev/null; then
    kill "$BACKEND_PID" 2>/dev/null || true
  fi

  if [[ -n "${FRONTEND_PID:-}" ]] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
    kill "$FRONTEND_PID" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

if ! PYTHON_BIN="$(resolve_python)"; then
  echo "Error: no se encontró un intérprete de Python. Instala Python 3 o crea .venv." >&2
  exit 1
fi

if ! "$PYTHON_BIN" -c "import uvicorn" >/dev/null 2>&1; then
  echo "Error: faltan dependencias del backend. Ejecuta '$PYTHON_BIN -m pip install -r requirements.txt'." >&2
  exit 1
fi

echo "Iniciando backend en http://127.0.0.1:8000 ..."
"$PYTHON_BIN" -m uvicorn backend.server:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

sleep 1
if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
  wait "$BACKEND_PID" || true
  echo "Error: el backend no pudo iniciarse." >&2
  exit 1
fi

echo "Iniciando frontend estático en http://127.0.0.1:5173 ..."
"$PYTHON_BIN" -m http.server 5173 &
FRONTEND_PID=$!

sleep 1
if ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
  wait "$FRONTEND_PID" || true
  echo "Error: el frontend estático no pudo iniciarse." >&2
  exit 1
fi

echo
echo "Simulador disponible en: http://127.0.0.1:5173/frontend/"
echo "Presiona Ctrl+C para detener ambos servicios."

echo
wait "$BACKEND_PID" "$FRONTEND_PID"
