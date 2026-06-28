const METRICS = [
  { key: 'total_distance_km', label: 'Total Distance',  unit: ' km', lowerIsBetter: true },
  { key: 'avg_distance_km',   label: 'Avg Distance',    unit: ' km', lowerIsBetter: true },
  { key: 'max_distance_km',   label: 'Max Distance',    unit: ' km', lowerIsBetter: true },
  { key: 'assigned_count',    label: 'Assigned Orders', unit: '',    lowerIsBetter: false },
  { key: 'unassigned_count',  label: 'Unassigned',      unit: '',    lowerIsBetter: true },
  { key: 'fulfillment_pct',   label: 'Fulfillment',     unit: '%',   lowerIsBetter: false },
  { key: 'runtime_ms',        label: 'Runtime',         unit: ' ms', lowerIsBetter: true },
]

function bestOf(key, values, lowerIsBetter) {
  const filtered = values.filter(v => v !== null && v !== undefined)
  if (!filtered.length) return null
  return lowerIsBetter ? Math.min(...filtered) : Math.max(...filtered)
}

export default function MetricsPanel({ results }) {
  const gm  = results.greedy.metrics
  const hm  = results.hungarian.metrics
  const whm = results.weighted_hungarian.metrics

  return (
    <div className="metrics-panel">
      <h2>Algorithm Comparison</h2>

      <div className="metrics-grid">
        <div className="metrics-header">
          <span />
          <span className="col-label greedy-color">Greedy</span>
          <span className="col-label hungarian-color">Hungarian</span>
          <span className="col-label wh-color">Wt. Hungarian</span>
        </div>

        {METRICS.map(({ key, label, unit, lowerIsBetter }) => {
          const vals = [gm[key], hm[key], whm[key]]
          const best = bestOf(key, vals, lowerIsBetter)
          return (
            <div className="metric-row" key={key}>
              <span className="metric-label">{label}</span>
              {[gm, hm, whm].map((m, i) => (
                <span
                  key={i}
                  className={`metric-val ${m[key] === best ? 'winner' : ''}`}
                >
                  {m[key] ?? '—'}{unit}
                </span>
              ))}
            </div>
          )
        })}
      </div>

      <div className="legend">
        <p className="legend-title">Map Legend</p>
        <div className="legend-item">
          <span className="dot" style={{ background: '#2563eb' }} /> Trucks
        </div>
        <div className="legend-item">
          <span className="dot" style={{ background: '#dc2626' }} /> Orders
        </div>
        <div className="legend-item">
          <span className="line-sample dashed blue" /> Greedy
        </div>
        <div className="legend-item">
          <span className="line-sample solid amber" /> Hungarian
        </div>
        <div className="legend-item">
          <span className="line-sample dotted purple" /> Weighted Hungarian
        </div>
        <p className="winner-note">🟢 Green value = best result</p>
      </div>

      <div className="unassigned-section">
        {results.greedy.unassigned.length > 0 && (
          <p><strong>Greedy unassigned:</strong> {results.greedy.unassigned.join(', ')}</p>
        )}
        {results.hungarian.unassigned.length > 0 && (
          <p><strong>Hungarian unassigned:</strong> {results.hungarian.unassigned.join(', ')}</p>
        )}
        {results.weighted_hungarian.unassigned.length > 0 && (
          <p><strong>Wt. Hungarian unassigned:</strong> {results.weighted_hungarian.unassigned.join(', ')}</p>
        )}
      </div>
    </div>
  )
}
