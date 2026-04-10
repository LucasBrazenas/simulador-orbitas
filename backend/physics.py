import numpy as np

G = 6.67430e-11

def compute_gravitational_force(body1, body2):
    r_vec = body2.position - body1.position
    distance = np.linalg.norm(r_vec)

    if distance == 0:
        return np.zeros(3, dtype=float)

    force_magnitude = G * body1.mass * body2.mass / (distance ** 2)
    force_direction = r_vec / distance

    return force_magnitude * force_direction


def update_bodies(bodies, dt):
    # reset fuerzas
    for body in bodies:
        body.force[:] = 0.0

    # calcular fuerzas entre todos
    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            force = compute_gravitational_force(bodies[i], bodies[j])
            bodies[i].force += force
            bodies[j].force -= force

    # integrar (Euler)
    for body in bodies:
        acceleration = body.force / body.mass
        body.velocity += acceleration * dt
        body.position += body.velocity * dt