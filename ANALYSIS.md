# Algorithm Comparison Analysis

## Problem Recap

We have a set of trucks (each with a location and a weight capacity) and a set of delivery orders (each with a location, weight, and priority). The goal is to assign trucks to orders in a way that is both feasible (capacity respected) and efficient (minimises travel distance).

---

## Algorithm 1: Greedy

**How it works:**  
Sort orders by priority (high first). Go through them one at a time. For each order, scan all available trucks and pick the nearest one that can carry the load. Once a truck is assigned, it is removed from the pool.

**What it does well:**  
- Very fast — O(n × m) where n = orders, m = trucks.
- Naturally respects priority: high-priority orders get first pick of trucks.
- Easy to understand and extend for real-time dispatch (new orders can be slotted in as they arrive).

**Where it falls short:**  
- It is locally greedy — it commits to each assignment without seeing the full picture. A truck assigned to an order early on might have been the only good option for a later, more distant order.
- Total distance is not minimised globally.

---

## Algorithm 2: Hungarian (Kuhn–Munkres)

**How it works:**  
Build a cost matrix of size (trucks × orders), where each cell holds the distance between that truck and that order (set to a large infeasible value if capacity is violated). Pass the matrix to `scipy.optimize.linear_sum_assignment`, which returns the set of pairings that minimises the sum of all distances simultaneously.

**What it does well:**  
- Globally optimal for total distance — no other 1-to-1 assignment can have a lower total travel cost.
- Considers all trucks and orders at the same time, so it avoids the "greedy trap" of committing too early.

**Where it falls short:**  
- Treats all orders as equally important — priority is not factored in.
- Batch-only: all orders must be known upfront. Not suitable for real-time/streaming dispatch.
- Slightly slower for large inputs, though in practice the difference is negligible for fleet sizes relevant to this problem.

---

## What I Observed

Running both algorithms on the same synthetic dataset consistently showed:

- **Hungarian almost always achieves a lower or equal total distance** compared to Greedy. The saving is most visible when trucks are clustered together and orders are spread out — Greedy may assign a close truck to a low-priority order, leaving a far truck for a high-priority one, whereas Hungarian would swap those assignments to reduce total distance.

- **Greedy wins on priority-sensitive scenarios.** When one high-priority order is far from all trucks, Greedy guarantees it gets the best available truck first. Hungarian might assign that truck to a nearby low-priority order because it produces a lower total cost.

- **The difference narrows with more trucks than orders.** When trucks are abundant, both algorithms have good options for every order and converge on similar solutions.

- **Runtime:** Both algorithms run in milliseconds for the dataset sizes used here. For very large fleets (hundreds of trucks and orders), the O(n³) complexity of Hungarian would eventually become a bottleneck where Greedy remains practical.

---

## Takeaway

Neither algorithm is universally better. The right choice depends on the operational context:

| Context | Recommended Algorithm |
|---|---|
| Real-time dispatch, orders arrive live | Greedy |
| Priority is the primary concern | Greedy |
| Batch planning, all orders known upfront | Hungarian |
| Minimising total fleet mileage / fuel cost | Hungarian |
| Mixed priority + cost optimisation | Custom heuristic combining both |
