from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import math

from backend.body import Body

AU_METERS = 149_597_870_700.0
J2000_JULIAN_DAY = 2_451_545.0
SECONDS_PER_DAY = 86_400.0
DEFAULT_TIME_SCALE = 86_400.0
VELOCITY_SAMPLE_SECONDS = 60 * 60

SUN_MASS = 1.989e30
EARTH_MASS = 5.972e24
MOON_MASS = 7.34767309e22
EARTH_MOON_MASS_RATIO = MOON_MASS / (EARTH_MASS + MOON_MASS)


@dataclass(frozen=True)
class OrbitalElements:
    a0: float
    a_rate: float
    e0: float
    e_rate: float
    i0: float
    i_rate: float
    l0: float
    l_rate: float
    peri0: float
    peri_rate: float
    node0: float
    node_rate: float
    b: float = 0.0
    c: float = 0.0
    s: float = 0.0
    f: float = 0.0


@dataclass(frozen=True)
class MoonElements:
    semi_major_axis_m: float
    eccentricity: float
    inclination_deg: float
    mean_anomaly_deg: float
    arg_periapsis_deg: float
    ascending_node_deg: float
    sidereal_period_days: float


@dataclass(frozen=True)
class BodyInfo:
    mass: float
    radius_m: float
    color: str


PLANETARY_ELEMENTS = {
    "Mercurio": OrbitalElements(
        a0=0.38709843,
        a_rate=0.00000000,
        e0=0.20563661,
        e_rate=0.00002123,
        i0=7.00559432,
        i_rate=-0.00590158,
        l0=252.25166724,
        l_rate=149472.67486623,
        peri0=77.45771895,
        peri_rate=0.15940013,
        node0=48.33961819,
        node_rate=-0.12214182,
    ),
    "Venus": OrbitalElements(
        a0=0.72332102,
        a_rate=-0.00000026,
        e0=0.00676399,
        e_rate=-0.00005107,
        i0=3.39777545,
        i_rate=0.00043494,
        l0=181.97970850,
        l_rate=58517.81560260,
        peri0=131.76755713,
        peri_rate=0.05679648,
        node0=76.67261496,
        node_rate=-0.27274174,
    ),
    "EM_Bary": OrbitalElements(
        a0=1.00000018,
        a_rate=-0.00000003,
        e0=0.01673163,
        e_rate=-0.00003661,
        i0=-0.00054346,
        i_rate=-0.01337178,
        l0=100.46691572,
        l_rate=35999.37306329,
        peri0=102.93005885,
        peri_rate=0.31795260,
        node0=-5.11260389,
        node_rate=-0.24123856,
    ),
    "Marte": OrbitalElements(
        a0=1.52371243,
        a_rate=0.00000097,
        e0=0.09336511,
        e_rate=0.00009149,
        i0=1.85181869,
        i_rate=-0.00724757,
        l0=-4.56813164,
        l_rate=19140.29934243,
        peri0=-23.91744784,
        peri_rate=0.45223625,
        node0=49.71320984,
        node_rate=-0.26852431,
    ),
    "Jupiter": OrbitalElements(
        a0=5.20248019,
        a_rate=-0.00002864,
        e0=0.04853590,
        e_rate=0.00018026,
        i0=1.29861416,
        i_rate=-0.00322699,
        l0=34.33479152,
        l_rate=3034.90371757,
        peri0=14.27495244,
        peri_rate=0.18199196,
        node0=100.29282654,
        node_rate=0.13024619,
        b=-0.00012452,
        c=0.06064060,
        s=-0.35635438,
        f=38.35125000,
    ),
    "Saturno": OrbitalElements(
        a0=9.54149883,
        a_rate=-0.00003065,
        e0=0.05550825,
        e_rate=-0.00032044,
        i0=2.49424102,
        i_rate=0.00451969,
        l0=50.07571329,
        l_rate=1222.11494724,
        peri0=92.86136063,
        peri_rate=0.54179478,
        node0=113.63998702,
        node_rate=-0.25015002,
        b=0.00025899,
        c=-0.13434469,
        s=0.87320147,
        f=38.35125000,
    ),
    "Urano": OrbitalElements(
        a0=19.18797948,
        a_rate=-0.00020455,
        e0=0.04685740,
        e_rate=-0.00001550,
        i0=0.77298127,
        i_rate=-0.00180155,
        l0=314.20276625,
        l_rate=428.49512595,
        peri0=172.43404441,
        peri_rate=0.09266985,
        node0=73.96250215,
        node_rate=0.05739699,
        b=0.00058331,
        c=-0.97731848,
        s=0.17689245,
        f=7.67025000,
    ),
    "Neptuno": OrbitalElements(
        a0=30.06952752,
        a_rate=0.00006447,
        e0=0.00895439,
        e_rate=0.00000818,
        i0=1.77005520,
        i_rate=0.00022400,
        l0=304.22289287,
        l_rate=218.46515314,
        peri0=46.68158724,
        peri_rate=0.01009938,
        node0=131.78635853,
        node_rate=-0.00606302,
        b=-0.00041348,
        c=0.68346318,
        s=-0.10162547,
        f=7.67025000,
    ),
}

MOON_ELEMENTS = MoonElements(
    semi_major_axis_m=384_400_000.0,
    eccentricity=0.0554,
    inclination_deg=5.16,
    mean_anomaly_deg=135.27,
    arg_periapsis_deg=318.15,
    ascending_node_deg=125.08,
    sidereal_period_days=27.322,
)

SOLAR_SYSTEM_BODY_INFO = {
    "Sol": BodyInfo(mass=SUN_MASS, radius_m=695_700_000, color="#ffe08a"),
    "Mercurio": BodyInfo(mass=3.3011e23, radius_m=2_439_700, color="#b2a394"),
    "Venus": BodyInfo(mass=4.8675e24, radius_m=6_051_800, color="#d9b36d"),
    "Tierra": BodyInfo(mass=EARTH_MASS, radius_m=6_371_000, color="#7bb0ff"),
    "Luna": BodyInfo(mass=MOON_MASS, radius_m=1_737_400, color="#d0d0d0"),
    "Marte": BodyInfo(mass=6.4171e23, radius_m=3_389_500, color="#c96b3b"),
    "Jupiter": BodyInfo(mass=1.8982e27, radius_m=69_911_000, color="#dab07c"),
    "Saturno": BodyInfo(mass=5.6834e26, radius_m=58_232_000, color="#d8c18d"),
    "Urano": BodyInfo(mass=8.6810e25, radius_m=25_362_000, color="#95daef"),
    "Neptuno": BodyInfo(mass=1.02413e26, radius_m=24_622_000, color="#5375ff"),
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def datetime_to_julian_day(moment: datetime) -> float:
    utc_moment = moment.astimezone(timezone.utc)
    unix_epoch_julian_day = 2_440_587.5
    return unix_epoch_julian_day + utc_moment.timestamp() / SECONDS_PER_DAY


def normalize_degrees(angle_deg: float) -> float:
    return (angle_deg + 180.0) % 360.0 - 180.0


def rotate_orbital_plane(
    x_prime: float,
    y_prime: float,
    inclination_deg: float,
    ascending_node_deg: float,
    arg_periapsis_deg: float,
) -> tuple[float, float, float]:
    inclination = math.radians(inclination_deg)
    ascending_node = math.radians(ascending_node_deg)
    arg_periapsis = math.radians(arg_periapsis_deg)

    cos_omega = math.cos(arg_periapsis)
    sin_omega = math.sin(arg_periapsis)
    cos_node = math.cos(ascending_node)
    sin_node = math.sin(ascending_node)
    cos_inclination = math.cos(inclination)
    sin_inclination = math.sin(inclination)

    x_ecl = (
        (cos_omega * cos_node - sin_omega * sin_node * cos_inclination) * x_prime
        + (-sin_omega * cos_node - cos_omega * sin_node * cos_inclination) * y_prime
    )
    y_ecl = (
        (cos_omega * sin_node + sin_omega * cos_node * cos_inclination) * x_prime
        + (-sin_omega * sin_node + cos_omega * cos_node * cos_inclination) * y_prime
    )
    z_ecl = (sin_omega * sin_inclination) * x_prime + (
        cos_omega * sin_inclination
    ) * y_prime

    return x_ecl, y_ecl, z_ecl


def solve_kepler(mean_anomaly_deg: float, eccentricity: float) -> float:
    eccentricity_deg = math.degrees(eccentricity)
    eccentric_anomaly = mean_anomaly_deg + eccentricity_deg * math.sin(
        math.radians(mean_anomaly_deg)
    )

    for _ in range(15):
        delta_mean_anomaly = mean_anomaly_deg - (
            eccentric_anomaly
            - eccentricity_deg * math.sin(math.radians(eccentric_anomaly))
        )
        delta_eccentric_anomaly = delta_mean_anomaly / (
            1.0 - eccentricity * math.cos(math.radians(eccentric_anomaly))
        )
        eccentric_anomaly += delta_eccentric_anomaly

        if abs(delta_eccentric_anomaly) <= 1e-6:
            break

    return eccentric_anomaly


def heliocentric_planet_position(name: str, julian_day: float) -> tuple[float, float, float]:
    elements = PLANETARY_ELEMENTS[name]
    centuries = (julian_day - J2000_JULIAN_DAY) / 36_525.0

    semi_major_axis_au = elements.a0 + elements.a_rate * centuries
    eccentricity = elements.e0 + elements.e_rate * centuries
    inclination_deg = elements.i0 + elements.i_rate * centuries
    mean_longitude_deg = elements.l0 + elements.l_rate * centuries
    long_periapsis_deg = elements.peri0 + elements.peri_rate * centuries
    ascending_node_deg = elements.node0 + elements.node_rate * centuries
    arg_periapsis_deg = long_periapsis_deg - ascending_node_deg

    mean_anomaly_deg = (
        mean_longitude_deg
        - long_periapsis_deg
        + elements.b * centuries**2
        + elements.c * math.cos(math.radians(elements.f * centuries))
        + elements.s * math.sin(math.radians(elements.f * centuries))
    )
    mean_anomaly_deg = normalize_degrees(mean_anomaly_deg)

    eccentric_anomaly_deg = solve_kepler(mean_anomaly_deg, eccentricity)
    eccentric_anomaly = math.radians(eccentric_anomaly_deg)

    x_prime_au = semi_major_axis_au * (math.cos(eccentric_anomaly) - eccentricity)
    y_prime_au = semi_major_axis_au * math.sqrt(1.0 - eccentricity**2) * math.sin(
        eccentric_anomaly
    )

    x_au, y_au, z_au = rotate_orbital_plane(
        x_prime=x_prime_au,
        y_prime=y_prime_au,
        inclination_deg=inclination_deg,
        ascending_node_deg=ascending_node_deg,
        arg_periapsis_deg=arg_periapsis_deg,
    )

    return x_au * AU_METERS, y_au * AU_METERS, z_au * AU_METERS


def moon_geocentric_position(julian_day: float) -> tuple[float, float, float]:
    days_since_j2000 = julian_day - J2000_JULIAN_DAY
    mean_motion_deg_per_day = 360.0 / MOON_ELEMENTS.sidereal_period_days
    mean_anomaly_deg = normalize_degrees(
        MOON_ELEMENTS.mean_anomaly_deg + mean_motion_deg_per_day * days_since_j2000
    )
    eccentric_anomaly_deg = solve_kepler(
        mean_anomaly_deg,
        MOON_ELEMENTS.eccentricity,
    )
    eccentric_anomaly = math.radians(eccentric_anomaly_deg)

    x_prime = MOON_ELEMENTS.semi_major_axis_m * (
        math.cos(eccentric_anomaly) - MOON_ELEMENTS.eccentricity
    )
    y_prime = (
        MOON_ELEMENTS.semi_major_axis_m
        * math.sqrt(1.0 - MOON_ELEMENTS.eccentricity**2)
        * math.sin(eccentric_anomaly)
    )

    return rotate_orbital_plane(
        x_prime=x_prime,
        y_prime=y_prime,
        inclination_deg=MOON_ELEMENTS.inclination_deg,
        ascending_node_deg=MOON_ELEMENTS.ascending_node_deg,
        arg_periapsis_deg=MOON_ELEMENTS.arg_periapsis_deg,
    )


def solar_system_positions(moment: datetime) -> dict[str, tuple[float, float, float]]:
    julian_day = datetime_to_julian_day(moment)

    mercury = heliocentric_planet_position("Mercurio", julian_day)
    venus = heliocentric_planet_position("Venus", julian_day)
    earth_moon_barycenter = heliocentric_planet_position("EM_Bary", julian_day)
    mars = heliocentric_planet_position("Marte", julian_day)
    jupiter = heliocentric_planet_position("Jupiter", julian_day)
    saturn = heliocentric_planet_position("Saturno", julian_day)
    uranus = heliocentric_planet_position("Urano", julian_day)
    neptune = heliocentric_planet_position("Neptuno", julian_day)

    moon_relative = moon_geocentric_position(julian_day)
    earth = tuple(
        earth_moon_barycenter[index] - moon_relative[index] * EARTH_MOON_MASS_RATIO
        for index in range(3)
    )
    moon = tuple(earth[index] + moon_relative[index] for index in range(3))

    return {
        "Sol": (0.0, 0.0, 0.0),
        "Mercurio": mercury,
        "Venus": venus,
        "Tierra": earth,
        "Luna": moon,
        "Marte": mars,
        "Jupiter": jupiter,
        "Saturno": saturn,
        "Urano": uranus,
        "Neptuno": neptune,
    }


def estimate_velocities(moment: datetime) -> dict[str, tuple[float, float, float]]:
    previous_positions = solar_system_positions(
        moment - timedelta(seconds=VELOCITY_SAMPLE_SECONDS)
    )
    next_positions = solar_system_positions(moment + timedelta(seconds=VELOCITY_SAMPLE_SECONDS))

    velocities = {}
    denominator = 2 * VELOCITY_SAMPLE_SECONDS

    for name in previous_positions:
        velocities[name] = tuple(
            (next_positions[name][index] - previous_positions[name][index]) / denominator
            for index in range(3)
        )

    total_momentum = [0.0, 0.0, 0.0]

    for name, velocity in velocities.items():
        if name == "Sol":
            continue

        mass = SOLAR_SYSTEM_BODY_INFO[name].mass
        for index in range(3):
            total_momentum[index] += mass * velocity[index]

    velocities["Sol"] = tuple(-value / SUN_MASS for value in total_momentum)
    return velocities


def build_solar_system_bodies(moment: datetime) -> list[Body]:
    positions = solar_system_positions(moment)
    velocities = estimate_velocities(moment)

    return [
        Body(
            name=name,
            mass=SOLAR_SYSTEM_BODY_INFO[name].mass,
            position=positions[name],
            velocity=velocities[name],
            radius_m=SOLAR_SYSTEM_BODY_INFO[name].radius_m,
            color=SOLAR_SYSTEM_BODY_INFO[name].color,
        )
        for name in (
            "Sol",
            "Mercurio",
            "Venus",
            "Tierra",
            "Luna",
            "Marte",
            "Jupiter",
            "Saturno",
            "Urano",
            "Neptuno",
        )
    ]


def solar_system_snapshot(moment: datetime) -> list[dict[str, list[float] | str | float | bool]]:
    return [
        {
            "name": body.name,
            "position": body.position.tolist(),
            "radiusMeters": body.radius_m,
            "color": body.color,
            "isCustom": body.is_custom,
        }
        for body in build_solar_system_bodies(moment)
    ]
