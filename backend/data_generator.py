import random
from models import Truck, Order

# Centred on Bangalore — spread ~15 km in each direction
BASE_LAT = 12.9716
BASE_LON = 77.5946
SPREAD = 0.12


def generate_data(num_trucks: int = 8, num_orders: int = 12, seed: int = 42):
    random.seed(seed)

    trucks = []
    for i in range(num_trucks):
        trucks.append(Truck(
            id=f"T{i + 1}",
            name=f"Truck {i + 1}",
            lat=BASE_LAT + random.uniform(-SPREAD, SPREAD),
            lon=BASE_LON + random.uniform(-SPREAD, SPREAD),
            capacity=random.choice([500, 750, 1000]),
        ))

    orders = []
    for i in range(num_orders):
        orders.append(Order(
            id=f"O{i + 1}",
            lat=BASE_LAT + random.uniform(-SPREAD, SPREAD),
            lon=BASE_LON + random.uniform(-SPREAD, SPREAD),
            weight=round(random.uniform(50, 400), 1),
            priority=random.choice(["high", "medium", "low"]),
        ))

    return trucks, orders
