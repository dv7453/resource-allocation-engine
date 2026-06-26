# Resource Allocation Engine

A delivery fleet optimisation tool that assigns trucks to delivery orders using two different algorithms and lets you compare them visually on a map.

## Domain

**Delivery Fleet** — trucks are dispatched to fulfil delivery orders across a city.  
Each truck has a capacity (kg). Each order has a weight and a priority (high / medium / low).

## Algorithms

### Greedy
Process orders one at a time, highest priority first.  
For each order, pick the nearest available truck that can carry the load.

- **Strength:** fast, intuitive, good for real-time dispatch.  
- **Weakness:** locally optimal — commits to each choice without seeing the full picture.

### Hungarian (Kuhn–Munkres)
Build a cost matrix (distance from every truck to every order) and find the assignment that minimises **total** distance across all trucks simultaneously.  
Uses `scipy.optimize.linear_sum_assignment` under the hood.

- **Strength:** globally optimal total distance.  
- **Weakness:** batch-only — slower and doesn't account for priority ordering.

### When does each win?
| Scenario | Winner |
|---|---|
| Orders arrive one by one in real time | Greedy |
| All orders known upfront, minimise fleet mileage | Hungarian |
| Uneven priority distribution | Greedy (respects priority) |
| Uniform priority, many trucks | Hungarian |

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI + Python |
| Optimisation | SciPy (`linear_sum_assignment`), NumPy |
| Frontend | React (Vite) |
| Maps | Leaflet + OpenStreetMap (free, no API key) |

---

## Setup & Running

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs at **http://localhost:8000**  
API docs available at **http://localhost:8000/docs**

### 2. Frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at **http://localhost:5173**

### 3. Tests

```bash
# from the project root
pip install pytest          # if not already installed
pytest tests/ -v
```

---

## How to Use

1. Open **http://localhost:5173** in your browser.
2. Adjust the **Trucks** and **Orders** sliders.
3. Click **Generate Data** — trucks (blue) and orders (red) appear on the map.
4. Click **Run Algorithms** — assignment lines appear and the metrics panel fills in.
5. Use the **Greedy / Hungarian / Both** toggle to compare routes visually.

Green values in the metrics panel indicate the better result for that metric.

---

## Project Structure

```
resource-allocation-engine/
├── backend/
│   ├── main.py             # FastAPI app & endpoints
│   ├── models.py           # Truck, Order, Assignment dataclasses + haversine
│   ├── data_generator.py   # Synthetic data generator
│   ├── metrics.py          # Compute comparison metrics
│   ├── algorithms/
│   │   ├── greedy.py
│   │   └── hungarian.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── components/
│   │       ├── MapView.jsx      # Leaflet map with markers + lines
│   │       └── MetricsPanel.jsx # Side-by-side comparison table
│   ├── index.html
│   └── package.json
├── tests/
│   ├── conftest.py
│   └── test_algorithms.py
└── README.md
```
