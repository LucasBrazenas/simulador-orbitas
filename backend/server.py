import asyncio
from dataclasses import dataclass
from datetime import timedelta
import time

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from backend.body import Body
from backend.orbits import (
    AU_METERS,
    DEFAULT_TIME_SCALE,
    build_solar_system_bodies,
    utc_now,
)
from backend.physics import (
    DEFAULT_INTEGRATION_METHOD,
    normalize_integration_method,
    resolve_collisions,
    update_bodies,
)

FRAME_DELAY_SECONDS = 1 / 30
MAX_TIME_SCALE = 31_536_000.0

app = FastAPI()


@dataclass(frozen=True)
class CustomBodySpec:
    name: str
    mass: float
    radius_m: float
    color: str
    position_m: tuple[float, float, float]
    velocity_m_s: tuple[float, float, float]


def serialize_body(body: Body) -> dict[str, object]:
    return {
        "name": body.name,
        "position": body.position.tolist(),
        "radiusMeters": body.radius_m,
        "color": body.color,
        "isCustom": body.is_custom,
    }


def body_from_custom_spec(spec: CustomBodySpec) -> Body:
    return Body(
        name=spec.name,
        mass=spec.mass,
        position=spec.position_m,
        velocity=spec.velocity_m_s,
        radius_m=spec.radius_m,
        color=spec.color,
        is_custom=True,
    )


def clamp_time_scale(value: float) -> float:
    return max(0.0, min(value, MAX_TIME_SCALE))


def normalize_custom_name(name: str, existing_names: set[str]) -> str:
    base_name = (name or "Cuerpo extra").strip()[:30] or "Cuerpo extra"

    if base_name not in existing_names:
        return base_name

    suffix = 2
    while f"{base_name} {suffix}" in existing_names:
        suffix += 1

    return f"{base_name} {suffix}"


class SimulationSession:
    def __init__(self):
        self.time_scale = DEFAULT_TIME_SCALE
        self.integration_method = DEFAULT_INTEGRATION_METHOD
        self.has_started = False
        self.simulation_time = utc_now()
        self.last_real_tick = time.monotonic()
        self.custom_specs: list[CustomBodySpec] = []
        self.bodies: list[Body] = []
        self.reset(moment=self.simulation_time, keep_custom=False)

    def reset(self, moment=None, keep_custom=True):
        if moment is None:
            moment = utc_now()

        preserved_specs = list(self.custom_specs) if keep_custom else []
        self.custom_specs = preserved_specs
        self.simulation_time = moment
        self.last_real_tick = time.monotonic()
        self.bodies = build_solar_system_bodies(moment)

        for spec in self.custom_specs:
            self.bodies.append(body_from_custom_spec(spec))

        resolve_collisions(self.bodies)

    def advance(self):
        now = time.monotonic()
        elapsed_real_seconds = now - self.last_real_tick
        self.last_real_tick = now

        if not self.has_started:
            return

        simulated_delta_seconds = elapsed_real_seconds * self.time_scale
        if simulated_delta_seconds == 0:
            return

        update_bodies(self.bodies, simulated_delta_seconds, self.integration_method)
        self.simulation_time += timedelta(seconds=simulated_delta_seconds)

    def snapshot(self):
        return {
            "type": "snapshot",
            "simulationTime": self.simulation_time.isoformat().replace("+00:00", "Z"),
            "timeScale": self.time_scale,
            "integrationMethod": self.integration_method,
            "isStarted": self.has_started,
            "bodies": [serialize_body(body) for body in self.bodies],
        }

    def start(self, integration_method, time_scale):
        self.integration_method = normalize_integration_method(integration_method)
        self.time_scale = clamp_time_scale(float(time_scale))
        self.has_started = True
        self.last_real_tick = time.monotonic()

    def set_time_scale(self, time_scale):
        self.advance()
        self.time_scale = clamp_time_scale(float(time_scale))

    def set_integration_method(self, integration_method):
        self.advance()
        self.integration_method = normalize_integration_method(integration_method)

    def sync_to_now(self):
        self.reset(moment=utc_now(), keep_custom=True)

    def reset_system(self):
        self.custom_specs = []
        self.reset(moment=utc_now(), keep_custom=False)

    def add_custom_body(
        self,
        name,
        mass,
        radius_m,
        color,
        position_au,
        velocity_km_s,
    ):
        self.advance()

        existing_names = {body.name for body in self.bodies}
        unique_name = normalize_custom_name(name, existing_names)

        spec = CustomBodySpec(
            name=unique_name,
            mass=float(mass),
            radius_m=float(radius_m),
            color=color,
            position_m=tuple(float(component) * AU_METERS for component in position_au),
            velocity_m_s=tuple(float(component) * 1_000.0 for component in velocity_km_s),
        )

        self.custom_specs.append(spec)
        self.bodies.append(body_from_custom_spec(spec))
        resolve_collisions(self.bodies)


def parse_custom_body_message(message):
    name = message.get("name", "")
    mass = float(message.get("mass"))
    radius_m = float(message.get("radiusMeters"))
    color = str(message.get("color", "#ff6b4a"))
    position_au = tuple(message.get("positionAu", [0, 0, 0]))
    velocity_km_s = tuple(message.get("velocityKmS", [0, 0, 0]))

    if mass <= 0 or radius_m <= 0:
        raise ValueError("Mass and radius must be positive")

    if len(position_au) != 3 or len(velocity_km_s) != 3:
        raise ValueError("Position and velocity vectors must have 3 components")

    return name, mass, radius_m, color, position_au, velocity_km_s


async def receive_client_messages(websocket: WebSocket, session: SimulationSession, lock: asyncio.Lock) -> None:
    while True:
        message = await websocket.receive_json()

        if not isinstance(message, dict):
            continue

        message_type = message.get("type")

        async with lock:
            if message_type == "start_simulation":
                try:
                    session.start(
                        message.get("integrationMethod", DEFAULT_INTEGRATION_METHOD),
                        float(message.get("timeScale", DEFAULT_TIME_SCALE)),
                    )
                except (TypeError, ValueError):
                    continue
                continue

            if message_type == "set_time_scale":
                try:
                    session.set_time_scale(float(message.get("value", DEFAULT_TIME_SCALE)))
                except (TypeError, ValueError):
                    continue
                continue

            if message_type == "set_integration_method":
                try:
                    session.set_integration_method(
                        message.get("value", DEFAULT_INTEGRATION_METHOD)
                    )
                except (TypeError, ValueError):
                    continue
                continue

            if message_type == "sync_to_now":
                session.sync_to_now()
                continue

            if message_type == "reset_system":
                session.reset_system()
                continue

            if message_type == "add_custom_body":
                try:
                    session.add_custom_body(*parse_custom_body_message(message))
                except (TypeError, ValueError):
                    continue


async def stream_simulation(websocket: WebSocket, session: SimulationSession, lock: asyncio.Lock) -> None:
    while True:
        async with lock:
            session.advance()
            payload = session.snapshot()

        await websocket.send_json(payload)
        await asyncio.sleep(FRAME_DELAY_SECONDS)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Cliente conectado al WebSocket")

    session = SimulationSession()
    lock = asyncio.Lock()
    sender_task = asyncio.create_task(stream_simulation(websocket, session, lock))
    receiver_task = asyncio.create_task(receive_client_messages(websocket, session, lock))

    try:
        done, pending = await asyncio.wait(
            {sender_task, receiver_task},
            return_when=asyncio.FIRST_COMPLETED,
        )

        for task in pending:
            task.cancel()

        await asyncio.gather(*pending, return_exceptions=True)

        for task in done:
            exception = task.exception()
            if exception and not isinstance(exception, (RuntimeError, WebSocketDisconnect)):
                raise exception
    except WebSocketDisconnect:
        pass
    finally:
        sender_task.cancel()
        receiver_task.cancel()
        await asyncio.gather(sender_task, receiver_task, return_exceptions=True)
        print("Cliente desconectado")
