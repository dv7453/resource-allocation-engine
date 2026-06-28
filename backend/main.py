from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from models import Truck, Order
from data_generator import generate_data
from algorithms.greedy import greedy_allocate
from algorithms.hungarian import hungarian_allocate
from algorithms.weighted_hungarian import weighted_hungarian_allocate
from metrics import compute_metrics

app = FastAPI(title="Resource Allocation Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Pydantic schemas ----------

class TruckIn(BaseModel):
    id: str
    name: str
    lat: float
    lon: float
    capacity: float


class OrderIn(BaseModel):
    id: str
    lat: float
    lon: float
    weight: float
    priority: str


class AllocateRequest(BaseModel):
    trucks: list[TruckIn]
    orders: list[OrderIn]


# ---------- Endpoints ----------

@app.get("/generate")
def generate(
    num_trucks: int = Query(8, ge=2, le=20),
    num_orders: int = Query(12, ge=2, le=30),
    seed: int = Query(42),
):
    """Return a fresh set of randomly placed trucks and orders."""
    trucks, orders = generate_data(num_trucks, num_orders, seed)
    return {
        "trucks": [t.__dict__ for t in trucks],
        "orders": [o.__dict__ for o in orders],
    }


@app.post("/allocate")
def allocate(req: AllocateRequest):
    """
    Run all three algorithms on the same dataset and return a side-by-side comparison.

    - Greedy            : priority-first, nearest available truck (fast, locally optimal)
    - Hungarian         : globally optimal total distance, ignores priority
    - Weighted Hungarian: Hungarian with priority discounts in the cost matrix,
                          balances distance optimality with order urgency
    """
    trucks = [Truck(**t.model_dump()) for t in req.trucks]
    orders = [Order(**o.model_dump()) for o in req.orders]
    n = len(orders)

    g_assign,  g_unassigned,  g_ms  = greedy_allocate(trucks, orders)
    h_assign,  h_unassigned,  h_ms  = hungarian_allocate(trucks, orders)
    wh_assign, wh_unassigned, wh_ms = weighted_hungarian_allocate(trucks, orders)

    return {
        "greedy": {
            "assignments": [a.__dict__ for a in g_assign],
            "unassigned": g_unassigned,
            "metrics": compute_metrics(g_assign, g_unassigned, g_ms, n),
        },
        "hungarian": {
            "assignments": [a.__dict__ for a in h_assign],
            "unassigned": h_unassigned,
            "metrics": compute_metrics(h_assign, h_unassigned, h_ms, n),
        },
        "weighted_hungarian": {
            "assignments": [a.__dict__ for a in wh_assign],
            "unassigned": wh_unassigned,
            "metrics": compute_metrics(wh_assign, wh_unassigned, wh_ms, n),
        },
    }
