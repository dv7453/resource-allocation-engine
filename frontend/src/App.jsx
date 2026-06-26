import { useState } from 'react'
import MapView from './components/MapView'
import MetricsPanel from './components/MetricsPanel'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const VIEWS = [
  { id: 'greedy',    label: 'Greedy' },
  { id: 'hungarian', label: 'Hungarian' },
  { id: 'all',       label: 'All' },
]

export default function App() {
  const [numTrucks, setNumTrucks] = useState(8)
  const [numOrders, setNumOrders] = useState(12)
  const [data,       setData]      = useState(null)
  const [results,    setResults]   = useState(null)
  const [loading,    setLoading]   = useState(false)
  const [activeView, setActiveView] = useState('all')
  const [error,      setError]     = useState(null)

  async function handleGenerate() {
    setError(null)
    setResults(null)
    try {
      const res = await fetch(`${API}/generate?num_trucks=${numTrucks}&num_orders=${numOrders}`)
      setData(await res.json())
    } catch {
      setError('Could not reach the backend. Make sure it is running on port 8000.')
    }
  }

  async function handleAllocate() {
    if (!data) return
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API}/allocate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
      setResults(await res.json())
    } catch {
      setError('Allocation request failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header>
        <div>
          <h1>Resource Allocation Engine</h1>
          <p>Delivery Fleet Optimisation — Greedy (priority-first) · Hungarian (globally optimal)</p>
        </div>
      </header>

      <div className="controls">
        <label>
          Trucks&nbsp;<strong>{numTrucks}</strong>
          <input
            type="range" min="3" max="15" value={numTrucks}
            onChange={e => setNumTrucks(Number(e.target.value))}
          />
        </label>

        <label>
          Orders&nbsp;<strong>{numOrders}</strong>
          <input
            type="range" min="3" max="25" value={numOrders}
            onChange={e => setNumOrders(Number(e.target.value))}
          />
        </label>

        <button className="btn-primary" onClick={handleGenerate}>
          Generate Data
        </button>

        <button
          className="btn-primary"
          onClick={handleAllocate}
          disabled={!data || loading}
        >
          {loading ? 'Running…' : 'Run Algorithms'}
        </button>

        {results && (
          <div className="view-toggle">
            <span className="toggle-label">Show:</span>
            {VIEWS.map(v => (
              <button
                key={v.id}
                className={activeView === v.id ? 'active' : ''}
                onClick={() => setActiveView(v.id)}
              >
                {v.label}
              </button>
            ))}
          </div>
        )}
      </div>

      {error && <div className="error-bar">{error}</div>}

      <div className="main">
        <MapView data={data} results={results} activeView={activeView} />
        {results && <MetricsPanel results={results} />}
      </div>
    </div>
  )
}
