import math
from dataclasses import dataclass


@dataclass
class Truck:
    id: str
    name: str
    lat: float
    lon: float
    capacity: float  # max weight in kg


@dataclass
class Order:
    id: str
    lat: float
    lon: float
    weight: float   # kg required
    priority: str   # 'high', 'medium', 'low'


@dataclass
class Assignment:
    truck_id: str
    order_id: str
    distance_km: float
    reason: str = ""


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Straight-line distance between two lat/lon points in km."""
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))
