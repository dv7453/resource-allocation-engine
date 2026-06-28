# Algorithm Comparison Analysis

## Problem Recap

We have a set of trucks (each with a location and a weight capacity) and a set of delivery orders (each with a location, weight, and priority). The goal is to assign trucks to orders in a way that is both feasible (capacity respected) and efficient (minimises travel distance while honouring order urgency).

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
- Treats all orders as equally important — priority is not factored into the cost.
- A nearby low-priority order will always beat a far high-priority one in a pure distance optimisation.
- Batch-only: all orders must be known upfront. Not suitable for real-time/streaming dispatch.

---

## Algorithm 3: Weighted Hungarian

**How it works:**  
Identical to the Hungarian algorithm except the cost matrix entries are modified before being passed to the solver:

```
cost[i][j] = distance(truck_i, order_j) − (priority_weight × priority_score(order_j))
```

Where `priority_score` maps high → 3, medium → 2, low → 1, and `priority_weight` is a tunable multiplier (default 5 km per score point). The discount makes high-priority cells look cheaper to the optimiser, so it prefers assigning those pairings. The actual distance recorded in each assignment is always the real haversine distance — the weight only influences which pairings get chosen.

**What it does well:**  
- Inherits Hungarian's global optimality guarantee while also encoding business priority.
- One knob to tune: increasing `priority_weight` makes priority more aggressive; setting it to 0 reduces to vanilla Hungarian.
- Guaranteed to outperform vanilla Hungarian at assigning high-priority orders when trucks are constrained.

**Where it falls short:**  
- Can produce a higher total distance than vanilla Hungarian — it deliberately accepts a longer route to serve a high-priority order.
- The right value of `priority_weight` depends on business judgement: how many extra kilometres is it worth spending to guarantee a high-priority order gets the best truck?

---

## What We Observed

Running all three algorithms on the same synthetic Bangalore dataset consistently showed:

- **Hungarian achieves the lowest total distance.** It sees every possible pairing at once and picks the globally cheapest combination. Greedy and Weighted Hungarian both produce longer totals.

- **Greedy wins on priority fulfilment in real-time scenarios.** Because it processes high-priority orders first and grabs the nearest available truck, it naturally protects urgent orders. It is also by far the fastest.

- **Weighted Hungarian sits between the two.** It produces a slightly higher total distance than vanilla Hungarian (it pays a distance penalty to serve high-priority orders better) but a lower total distance than Greedy. It is the only algorithm that simultaneously optimises both concerns: global distance efficiency *and* order urgency.

- **The difference between Hungarian and Weighted Hungarian is most visible when trucks are scarce.** When every truck matters, vanilla Hungarian will sacrifice a high-priority order to a farther truck if that reduces total distance. Weighted Hungarian will reassign the nearest truck to the high-priority order even at a cost.

- **All three produce identical results when all orders have the same priority** — with uniform priority scores the weighted cost matrix is just a uniform shift of the distance matrix, which doesn't change which pairing minimises the sum.

---

## When Each Algorithm Wins

| Context | Recommended Algorithm |
|---|---|
| Real-time dispatch, orders arrive live | Greedy |
| Priority is the primary concern | Greedy or Weighted Hungarian |
| Batch planning, minimise total fleet mileage | Hungarian |
| Batch planning, balance distance + priority | Weighted Hungarian |
| Large fleets (100+ trucks), speed matters | Greedy |
| Need a provably optimal baseline | Hungarian |
