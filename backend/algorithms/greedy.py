"""
Greedy Algorithm
----------------
Process orders one at a time (highest priority first).
For each order, pick the nearest available truck that can carry the load.

Pros : fast, simple, works well in real-time / low-load situations.
Cons : makes locally optimal choices — may miss the globally best assignment.
"""

import time
from models import Truck, Order, Assignment, haversine

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


def greedy_allocate(
    trucks: list[Truck], orders: list[Order]
) -> tuple[list[Assignment], list[str], float]:
    t_start = time.perf_counter()

    sorted_orders = sorted(orders, key=lambda o: PRIORITY_RANK[o.priority])

    available_trucks = set(t.id for t in trucks)
    assignments: list[Assignment] = []
    unassigned: list[str] = []

    for order in sorted_orders:
        best_truck = None
        best_dist = float("inf")

        for truck in trucks:
            if truck.id not in available_trucks:
                continue
            if truck.capacity < order.weight:
                continue

            dist = haversine(truck.lat, truck.lon, order.lat, order.lon)
            if dist < best_dist:
                best_dist = dist
                best_truck = truck

        if best_truck:
            reason = (
                f"Nearest available truck to {order.id} ({round(best_dist, 2)} km). "
                f"Capacity {best_truck.capacity} kg ≥ order weight {order.weight} kg. "
                f"Order priority: {order.priority}."
            )
            assignments.append(Assignment(best_truck.id, order.id, round(best_dist, 4), reason))
            available_trucks.remove(best_truck.id)
        else:
            unassigned.append(order.id)

    elapsed_ms = (time.perf_counter() - t_start) * 1000
    return assignments, unassigned, elapsed_ms
