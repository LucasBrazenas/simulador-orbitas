# Simulador de órbitas

Este repositorio contiene:

- **Backend** en Python con **FastAPI** y WebSocket para generar posiciones orbitales aproximadas del Sistema Solar en función del tiempo simulado.
- **Frontend** en HTML + JavaScript (Three.js) para visualizar Sol, Luna y los ocho planetas en 3D sobre un fondo estrellado panorámico.

## Requisitos

- Python 3.10+
- `pip`

## Instalación

Desde la raíz del proyecto:

```bash
python3 -m venv .venv
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

## Funcionalidades

- Todos los planetas del Sistema Solar visibles al mismo tiempo.
- Fondo estrellado 3D con un mapa celeste panorámico.
- Modo de tamaño **real** para respetar la diferencia física entre el Sol y los planetas.
- Modo de tamaño **aumentado** para hacer visibles los cuerpos pequeños sin alterar la escala de las órbitas.
- Velocidad del tiempo configurable desde la UI, incluyendo pausa, tiempo real (`1x`) y aceleración.
- Botón para resincronizar la simulación con el instante actual.
- Seguimiento de cámara desde la UI sobre cualquier cuerpo.
- Formulario para agregar cuerpos personalizados desde la UI con masa, radio, color, posición y velocidad iniciales.
- Reinicio del sistema para volver al sistema solar base y eliminar cuerpos personalizados.
- Colisiones resueltas por fusión: el cuerpo más dominante absorbe al otro y el absorbido desaparece.

## Ejecución manual (opcional)

### 1) Backend

```bash
uvicorn backend.server:app --host 127.0.0.1 --port 8000 --reload
```

### 2) Frontend

En otra terminal, desde la raíz del proyecto:

```bash
python3 -m http.server 5173
```

Y abre `http://127.0.0.1:5173/frontend/`.

## Notas

- El frontend se conecta al WebSocket en `ws://127.0.0.1:8000/ws`.
- Si cambias host o puerto del backend, actualiza esa URL en `frontend/main.js`.
- El sistema solar base se inicializa con elementos orbitales aproximados de JPL y luego evoluciona mediante integración gravitatoria N-cuerpos.
- La textura de Marte proviene del recurso oficial de NASA Science para modelos 3D. Las restantes texturas planetarias se almacenan en `frontend/textures/`.
- El fondo estrellado usa `Tycho Star Map`, disponible en NASA Science 3D Resources.
