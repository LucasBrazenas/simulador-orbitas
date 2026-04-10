# Simulador de órbitas

Este repositorio contiene:

- **Backend** en Python con **FastAPI** y WebSocket para calcular la simulación orbital.
- **Frontend** en HTML + JavaScript (Three.js) para visualizar Sol, Tierra y Luna en 3D.

## Requisitos

- Python 3.10+
- `pip`

## Instalación

Desde la raíz del proyecto:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecutar todo con un solo comando

Se incluye el script `run.sh` para levantar backend y frontend al mismo tiempo.

```bash
./run.sh
```

Esto inicia:

- Backend en `http://127.0.0.1:8000`
- Frontend estático en `http://127.0.0.1:5173`

Luego abre en tu navegador:

- `http://127.0.0.1:5173/frontend/`

Para detener ambos servicios, usa `Ctrl + C` en la terminal donde corre `run.sh`.

## Ejecución manual (opcional)

### 1) Backend

```bash
uvicorn backend.server:app --host 127.0.0.1 --port 8000 --reload
```

### 2) Frontend

En otra terminal, desde la raíz del proyecto:

```bash
python -m http.server 5173
```

Y abre `http://127.0.0.1:5173/frontend/`.

## Notas

- El frontend se conecta al WebSocket en `ws://127.0.0.1:8000/ws`.
- Si cambias host o puerto del backend, actualiza esa URL en `frontend/main.js`.
