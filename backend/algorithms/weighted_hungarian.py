"""
Weighted Hungarian Algorithm
-----------------------------
Same solver as the vanilla Hungarian algorithm but the cost matrix is modified
to give high-priority orders a discount, making the optimiser prefer assigning
valuable orders over cheap-but-unimportant ones.

Cost formula
------------
  cost[i][j] = distance(truck_i, order_j) - (PRIORITY_WEIGHT × priority_score(order_j))

  priority_score : high → 3 | medium → 2 | low → 1
  PRIORITY_WEIGHT: tunable multiplier (default 5 km per score point)

Why this works
--------------
The Hungarian solver minimises the *sum* of cost values.  By subtracting a
priority bonus we make high-priority cells look cheaper to the optimiser, so it
prefers those pairings when capacity allows.  The actual distance stored in the
Assignment is still the real haversine distance — the weight only influences
which pairings get chosen.

Pros : inherits Hungarian's global optimality guarantee while respecting
       business priority; only one knob to tune (PRIORITY_WEIGHT).
Cons : the priority bonus can cause longer actual distances — a high-priority
       order across the city may be chosen over a nearby low-priority one.
       The right PRIORITY_WEIGHT depends on how much extra distance the
       business is willing to spend to guarantee priority fulfilment.
"""

import time
import numpy as np
from scipy.optimize import linear_sum_assignment
from models import Truck, Order, Assignment, haversine

INFEASIBLE = 1e9
PRIORITY_SCORE = {"high": 3, "medium": 2, "low": 1}
PRIORITY_WEIGHT = 5  # km discount per priority score point


def weighted_hungarian_allocate(
    trucks: list[Truck],
    orders: list[Order],
    priority_weight: float = PRIORITY_WEIGHT,
) -> tuple[list[Assignment], list[str], float]:
    t_start = time.perf_counter()

    n_trucks = len(trucks)
    n_orders = len(orders)

    # Build the modified cost matrix
    cost = np.full((n_trucks, n_orders), INFEASIBLE)
    for i, truck in enumerate(trucks):
        for j, order in enumerate(orders):
            if truck.capacity >= order.weight:
                dist = haversine(truck.lat, truck.lon, order.lat, order.lon)
                score = PRIORITY_SCORE.get(order.priority, 1)
                # Subtract priority bonus — high priority orders look cheaper
                cost[i][j] = dist - (priority_weight * score)

    row_ind, col_ind = linear_sum_assignment(cost)

    assignments: list[Assignment] = []
    assigned_order_indices: set[int] = set()

    for i, j in zip(row_ind, col_ind):
        if cost[i][j] < INFEASIBLE:
            truck, order = trucks[i], orders[j]
            real_dist = haversine(truck.lat, truck.lon, order.lat, order.lon)
            score = PRIORITY_SCORE.get(order.priority, 1)
            discount = priority_weight * score
            reason = (
                f"Weighted Hungarian: priority '{order.priority}' gave a "
                f"{discount} km discount (score {score} × weight {priority_weight}). "
                f"Adjusted cost {round(real_dist - discount, 2)} km drove the "
                f"optimiser to choose {truck.id}. Real distance: {round(real_dist, 2)} km."
            )
            assignments.append(
                Assignment(truck.id, order.id, round(real_dist, 4), reason)
            )
            assigned_order_indices.add(j)

    unassigned = [orders[j].id for j in range(n_orders) if j not in assigned_order_indices]

    elapsed_ms = (time.perf_counter() - t_start) * 1000
    return assignments, unassigned, elapsed_ms
