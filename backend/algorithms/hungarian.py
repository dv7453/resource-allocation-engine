"""
Hungarian Algorithm  (via scipy.optimize.linear_sum_assignment)
---------------------------------------------------------------
Build a cost matrix where cost[i][j] = distance from truck i to order j.
The algorithm finds the assignment that minimises the *total* distance
across all trucks at once — it sees the full picture, unlike greedy.

Pros : globally optimal for total distance.
Cons : slightly slower; treats all orders as a single batch (not real-time).
"""

import time
import numpy as np
from scipy.optimize import linear_sum_assignment
from models import Truck, Order, Assignment, haversine

INFEASIBLE = 1e9  # cost used when a truck cannot serve an order


def hungarian_allocate(
    trucks: list[Truck], orders: list[Order]
) -> tuple[list[Assignment], list[str], float]:
    start = time.perf_counter()

    n_trucks = len(trucks)
    n_orders = len(orders)

    # Build cost matrix (trucks × orders)
    cost = np.full((n_trucks, n_orders), INFEASIBLE)
    for i, truck in enumerate(trucks):
        for j, order in enumerate(orders):
            if truck.capacity >= order.weight:   # hard constraint: capacity
                cost[i][j] = haversine(truck.lat, truck.lon, order.lat, order.lon)

    # scipy returns the optimal row/col index pairs
    row_ind, col_ind = linear_sum_assignment(cost)

    assignments: list[Assignment] = []
    assigned_order_indices: set[int] = set()

    for i, j in zip(row_ind, col_ind):
        if cost[i][j] < INFEASIBLE:
            reason = (
                f"Globally optimal assignment by Hungarian algorithm. "
                f"Distance {round(cost[i][j], 2)} km minimises total fleet distance. "
                f"Capacity {trucks[i].capacity} kg ≥ order weight {orders[j].weight} kg."
            )
            assignments.append(Assignment(trucks[i].id, orders[j].id, round(cost[i][j], 4), reason))
            assigned_order_indices.add(j)

    unassigned = [orders[j].id for j in range(n_orders) if j not in assigned_order_indices]

    elapsed_ms = (time.perf_counter() - start) * 1000
    return assignments, unassigned, elapsed_ms
