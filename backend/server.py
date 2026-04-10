import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from backend.body import Body
from backend.physics import update_bodies

app = FastAPI()

bodies = [
    Body("Sol", 1.989e30, [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]),
    Body("Tierra", 5.972e24, [1.496e11, 0.0, 0.0], [0.0, 29780.0, 0.0]),
    Body("Luna", 7.34767309e22, [1.496e11 + 384400000, 0.0, 0.0], [0.0, 29780.0 + 1022.0, 0.0]),
]

# más grande para que el movimiento sea visible
dt = 60 * 60 * 24  # 1 día por frame

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Cliente conectado al WebSocket")

    try:
        while True:
            update_bodies(bodies, dt)

            data = [
                {
                    "name": b.name,
                    "position": b.position.tolist()
                }
                for b in bodies
            ]

            await websocket.send_json(data)
            await asyncio.sleep(1 / 30)  # 30 actualizaciones por segundo
    except WebSocketDisconnect:
        print("Cliente desconectado")