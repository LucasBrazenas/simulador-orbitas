import numpy as np


class Body:
    def __init__(
        self,
        name,
        mass,
        position,
        velocity,
        radius_m=0.0,
        color="#ffffff",
        is_custom=False,
    ):
        self.name = name
        self.mass = mass
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.radius_m = float(radius_m)
        self.color = color
        self.is_custom = is_custom
        self.force = np.zeros(3, dtype=float)
