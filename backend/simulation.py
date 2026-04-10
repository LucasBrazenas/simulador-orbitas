import numpy as np
import matplotlib.pyplot as plt

from body import Body
from physics import compute_gravitational_force

def simulate_step(bodies, dt):
    """
    Ejecuta un paso de simulación:
    1. resetea aceleraciones
    2. calcula fuerzas gravitatorias entre todos los pares
    3. actualiza posición y velocidad de cada cuerpo
    """

    # Reiniciar aceleraciones
    for body in bodies:
        body.reset_acceleration()

    # Calcular fuerzas entre todos los cuerpos
    n = len(bodies)
    for i in range(n):
        for j in range(i + 1, n):
            body1 = bodies[i]
            body2 = bodies[j]

            force = compute_gravitational_force(body1, body2)

            # Acción y reacción
            body1.add_force(force)
            body2.add_force(-force)

    # Actualizar movimiento
    for body in bodies:
        body.update(dt)


def run_simulation():
    # Crear cuerpos
    sun = Body(
        name="Sol",
        mass=1.989e30,
        position=[0, 0, 0],
        velocity=[0, 0, 0],
        radius=20,
        color="orange"
    )

    earth = Body(
        name="Tierra",
        mass=5.972e24,
        position=[1.496e11, 0, 0],   # 1 UA aprox
        velocity=[0, 29780, 0],      # velocidad orbital aprox
        radius=8,
        color="blue"
    )

    bodies = [sun, earth]

    # Parámetros de simulación
    dt = 60 * 60 * 24   # 1 día en segundos
    steps = 183        # en días

    # Trayectorias
    trajectories = {body.name: [] for body in bodies}

    # Simulación
    for step in range(steps):
        simulate_step(bodies, dt)

        for body in bodies:
            trajectories[body.name].append(body.position.copy())

    return bodies, trajectories


def plot_trajectories(trajectories):
    plt.figure(figsize=(8, 8))

    for body_name, positions in trajectories.items():
        positions = np.array(positions)
        plt.plot(positions[:, 0], positions[:, 1], label=body_name)

        # Dibujar posición inicial
        plt.scatter(positions[0, 0], positions[0, 1], s=30)

    plt.xlabel("X (m)")
    plt.ylabel("Y (m)")
    plt.title("Simulación de órbitas")
    plt.axis("equal")
    plt.grid(True)
    plt.legend()
    plt.show()


if __name__ == "__main__":
    bodies, trajectories = run_simulation()
    plot_trajectories(trajectories)