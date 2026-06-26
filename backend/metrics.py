from models import Assignment


def compute_metrics(
    assignments: list[Assignment],
    unassigned: list[str],
    elapsed_ms: float,
    num_orders: int,
) -> dict:
    if not assignments:
        return {
            "total_distance_km": 0,
            "avg_distance_km": 0,
            "max_distance_km": 0,
            "assigned_count": 0,
            "unassigned_count": num_orders,
            "fulfillment_pct": 0.0,
            "runtime_ms": round(elapsed_ms, 3),
        }

    distances = [a.distance_km for a in assignments]
    return {
        "total_distance_km": round(sum(distances), 2),
        "avg_distance_km": round(sum(distances) / len(distances), 2),
        "max_distance_km": round(max(distances), 2),
        "assigned_count": len(assignments),
        "unassigned_count": len(unassigned),
        "fulfillment_pct": round(len(assignments) / num_orders * 100, 1),
        "runtime_ms": round(elapsed_ms, 3),
    }
