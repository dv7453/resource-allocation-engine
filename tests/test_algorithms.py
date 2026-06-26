"""
Tests that verify correctness and compare algorithm behaviour.

Run with:  pytest tests/
"""

from models import Truck, Order
from algorithms.greedy import greedy_allocate
from algorithms.hungarian import hungarian_allocate


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


# ---------- Comparison test ----------

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
