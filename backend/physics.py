import math
import numpy as np

G = 6.67430e-11
MAX_INTEGRATION_STEP_SECONDS = 60 * 60
MAX_SUBSTEPS = 240


def compute_gravitational_force(body1, body2):
    r_vec = body2.position - body1.position
    distance = np.linalg.norm(r_vec)

    if distance == 0:
        return np.zeros(3, dtype=float)

    force_magnitude = G * body1.mass * body2.mass / (distance**2)
    force_direction = r_vec / distance

    return force_magnitude * force_direction


def compute_accelerations(bodies):
    accelerations = [np.zeros(3, dtype=float) for _ in bodies]

    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            body1 = bodies[i]
            body2 = bodies[j]
            r_vec = body2.position - body1.position
            distance = np.linalg.norm(r_vec)

            if distance == 0:
                continue

            force_direction = r_vec / distance
            force_magnitude = G * body1.mass * body2.mass / (distance**2)
            force = force_direction * force_magnitude

            accelerations[i] += force / body1.mass
            accelerations[j] -= force / body2.mass

    return accelerations


def integrate_velocity_verlet(bodies, dt):
    initial_accelerations = compute_accelerations(bodies)

    for body, acceleration in zip(bodies, initial_accelerations):
        body.velocity += 0.5 * acceleration * dt
        body.position += body.velocity * dt

    final_accelerations = compute_accelerations(bodies)

    for body, acceleration in zip(bodies, final_accelerations):
        body.velocity += 0.5 * acceleration * dt


def merge_bodies(primary, secondary):
    total_mass = primary.mass + secondary.mass
    primary.position = (
        primary.position * primary.mass + secondary.position * secondary.mass
    ) / total_mass
    primary.velocity = (
        primary.velocity * primary.mass + secondary.velocity * secondary.mass
    ) / total_mass
    primary.mass = total_mass
    primary.radius_m = (primary.radius_m**3 + secondary.radius_m**3) ** (1 / 3)


def resolve_collisions(bodies):
    if len(bodies) < 2:
        return

    merged = True
    while merged:
        merged = False

        for i in range(len(bodies)):
            for j in range(i + 1, len(bodies)):
                body1 = bodies[i]
                body2 = bodies[j]
                collision_distance = body1.radius_m + body2.radius_m

                if collision_distance <= 0:
                    continue

                distance = np.linalg.norm(body2.position - body1.position)
                if distance > collision_distance:
                    continue

                if (body2.mass, body2.radius_m) > (body1.mass, body1.radius_m):
                    primary, secondary = body2, body1
                    primary_index, secondary_index = j, i
                else:
                    primary, secondary = body1, body2
                    primary_index, secondary_index = i, j

                merge_bodies(primary, secondary)
                del bodies[secondary_index]

                if secondary_index < primary_index:
                    primary_index -= 1

                bodies[primary_index] = primary
                merged = True
                break

            if merged:
                break


def update_bodies(bodies, dt):
    if dt == 0 or not bodies:
        return

    substep_count = max(1, math.ceil(abs(dt) / MAX_INTEGRATION_STEP_SECONDS))
    substep_count = min(substep_count, MAX_SUBSTEPS)
    substep_dt = dt / substep_count

    for _ in range(substep_count):
        resolve_collisions(bodies)
        integrate_velocity_verlet(bodies, substep_dt)
        resolve_collisions(bodies)
