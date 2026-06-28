"""
Tests that verify correctness and compare algorithm behaviour.

Run with:  pytest tests/
"""

from models import Truck, Order
from algorithms.greedy import greedy_allocate
from algorithms.hungarian import hungarian_allocate
from algorithms.weighted_hungarian import weighted_hungarian_allocate


# ---------- Helpers ----------

def two_trucks_two_orders():
    """Simple 2-truck / 2-order scenario with plenty of capacity."""
    trucks = [
        Truck("T1", "Truck 1", 40.71, -74.01, 1000),
        Truck("T2", "Truck 2", 40.73, -74.00, 1000),
    ]
    orders = [
        Order("O1", 40.72, -74.01, 100, "high"),
        Order("O2", 40.72, -74.00, 100, "low"),
    ]
    return trucks, orders


# ---------- Greedy tests ----------

def test_greedy_assigns_all_when_possible():
    trucks, orders = two_trucks_two_orders()
    assignments, unassigned, _ = greedy_allocate(trucks, orders)
    assert len(assignments) == 2
    assert len(unassigned) == 0


def test_greedy_respects_capacity_hard_constraint():
    """A truck with insufficient capacity must not be assigned."""
    trucks = [Truck("T1", "Truck 1", 40.71, -74.01, 50)]
    orders = [Order("O1", 40.72, -74.01, 200, "high")]
    assignments, unassigned, _ = greedy_allocate(trucks, orders)
    assert len(assignments) == 0
    assert "O1" in unassigned


def test_greedy_processes_high_priority_first():
    """High-priority order should be assigned when there is only one truck."""
    trucks = [Truck("T1", "Truck 1", 40.71, -74.01, 1000)]
    orders = [
        Order("O_low",  40.71, -74.01, 100, "low"),
        Order("O_high", 40.71, -74.01, 100, "high"),
    ]
    assignments, _, _ = greedy_allocate(trucks, orders)
    assert assignments[0].order_id == "O_high"


def test_greedy_each_truck_used_once():
    trucks, orders = two_trucks_two_orders()
    assignments, _, _ = greedy_allocate(trucks, orders)
    truck_ids = [a.truck_id for a in assignments]
    assert len(truck_ids) == len(set(truck_ids)), "A truck was assigned more than once"


# ---------- Hungarian tests ----------

def test_hungarian_assigns_all_when_possible():
    trucks, orders = two_trucks_two_orders()
    assignments, unassigned, _ = hungarian_allocate(trucks, orders)
    assert len(assignments) == 2
    assert len(unassigned) == 0


def test_hungarian_respects_capacity_hard_constraint():
    trucks = [Truck("T1", "Truck 1", 40.71, -74.01, 50)]
    orders = [Order("O1", 40.72, -74.01, 200, "high")]
    assignments, unassigned, _ = hungarian_allocate(trucks, orders)
    assert len(assignments) == 0
    assert "O1" in unassigned


def test_hungarian_each_truck_used_once():
    trucks, orders = two_trucks_two_orders()
    assignments, _, _ = hungarian_allocate(trucks, orders)
    truck_ids = [a.truck_id for a in assignments]
    assert len(truck_ids) == len(set(truck_ids))


def test_hungarian_total_distance_never_worse_than_greedy():
    """
    Hungarian finds the globally optimal assignment, so its total distance
    should always be ≤ greedy's total distance on the same data.
    """
    trucks, orders = two_trucks_two_orders()

    g_assignments, _, _ = greedy_allocate(trucks, orders)
    h_assignments, _, _ = hungarian_allocate(trucks, orders)

    g_total = sum(a.distance_km for a in g_assignments)
    h_total = sum(a.distance_km for a in h_assignments)

    assert h_total <= g_total + 1e-6, (
        f"Hungarian ({h_total:.4f} km) was worse than Greedy ({g_total:.4f} km)"
    )


# ---------- Weighted Hungarian tests ----------

def test_weighted_hungarian_assigns_all_when_possible():
    """Weighted Hungarian should assign all orders when capacity is sufficient."""
    trucks, orders = two_trucks_two_orders()
    assignments, unassigned, _ = weighted_hungarian_allocate(trucks, orders)
    assert len(assignments) == 2
    assert len(unassigned) == 0


def test_weighted_hungarian_respects_capacity_hard_constraint():
    """Capacity constraint must still be honoured despite the priority discount."""
    trucks = [Truck("T1", "Truck 1", 40.71, -74.01, 50)]
    orders = [Order("O1", 40.72, -74.01, 200, "high")]
    assignments, unassigned, _ = weighted_hungarian_allocate(trucks, orders)
    assert len(assignments) == 0
    assert "O1" in unassigned


def test_weighted_hungarian_each_truck_used_once():
    """Each truck may appear in at most one assignment."""
    trucks, orders = two_trucks_two_orders()
    assignments, _, _ = weighted_hungarian_allocate(trucks, orders)
    truck_ids = [a.truck_id for a in assignments]
    assert len(truck_ids) == len(set(truck_ids))


def test_weighted_hungarian_real_distance_stored():
    """Assignment.distance_km must reflect the real haversine distance, not the discounted cost."""
    from models import haversine
    trucks, orders = two_trucks_two_orders()
    assignments, _, _ = weighted_hungarian_allocate(trucks, orders)
    for a in assignments:
        truck = next(t for t in trucks if t.id == a.truck_id)
        order = next(o for o in orders if o.id == a.order_id)
        expected = round(haversine(truck.lat, truck.lon, order.lat, order.lon), 4)
        assert abs(a.distance_km - expected) < 1e-3, (
            f"Stored distance {a.distance_km} does not match real distance {expected}"
        )


def test_weighted_hungarian_prefers_high_priority_over_vanilla():
    """
    When only one truck is available and two orders exist — one high priority
    (farther away) and one low priority (closer) — the priority discount must be
    large enough to make Weighted Hungarian choose the high-priority order,
    while vanilla Hungarian chooses the closer low-priority one.

    Setup
    -----
    Truck at lat=0, lon=0
    High-priority order at lat=0.05, lon=0  (~5.6 km away)
    Low-priority  order at lat=0.01, lon=0  (~1.1 km away)

    Vanilla Hungarian cost: picks 1.1 km (low) over 5.6 km (high) — distance wins.

    Weighted Hungarian cost with weight=5:
      high → 5.6 - 5×3 = 5.6 - 15 = -9.4   ← lower cost
      low  → 1.1 - 5×1 = 1.1 -  5 = -3.9
    Optimiser picks high-priority (lower adjusted cost).
    """
    trucks = [Truck("T1", "Truck 1", 0.0, 0.0, 1000)]
    orders = [
        Order("O_high", 0.05, 0.0, 100, "high"),   # ~5.6 km
        Order("O_low",  0.01, 0.0, 100, "low"),    # ~1.1 km
    ]

    h_assignments,  _, _ = hungarian_allocate(trucks, orders)
    wh_assignments, _, _ = weighted_hungarian_allocate(trucks, orders)

    # Vanilla Hungarian picks the closer (low priority) order
    assert h_assignments[0].order_id == "O_low", (
        "Vanilla Hungarian should pick the closer low-priority order"
    )

    # Weighted Hungarian picks the farther but higher-priority order
    assert wh_assignments[0].order_id == "O_high", (
        "Weighted Hungarian should prefer the high-priority order despite greater distance"
    )
