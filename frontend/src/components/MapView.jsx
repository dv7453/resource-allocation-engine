import { MapContainer, TileLayer, CircleMarker, Polyline, Tooltip } from 'react-leaflet'

const CENTER = [12.9716, 77.5946]  // Bangalore

export default function MapView({ data, results, activeView }) {
  if (!data) {
    return (
      <div className="map-placeholder">
        <p>Click <strong>Generate Data</strong> to place trucks and orders on the map.</p>
      </div>
    )
  }

  const greedyAssignments    = results?.greedy?.assignments ?? []
  const hungarianAssignments = results?.hungarian?.assignments ?? []
  const whAssignments        = results?.weighted_hungarian?.assignments ?? []

  function truckPos(id) {
    const t = data.trucks.find(t => t.id === id)
    return t ? [t.lat, t.lon] : null
  }

  function orderPos(id) {
    const o = data.orders.find(o => o.id === id)
    return o ? [o.lat, o.lon] : null
  }

  const showGreedy    = activeView === 'greedy'             || activeView === 'all'
  const showHungarian = activeView === 'hungarian'          || activeView === 'all'
  const showWH        = activeView === 'weighted_hungarian' || activeView === 'all'
  const multiAlgo     = activeView === 'all'

  return (
    <div className="map-wrapper">
      <MapContainer center={CENTER} zoom={12} style={{ height: '100%', width: '100%' }}>
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution="© OpenStreetMap contributors"
        />

        {/* Trucks — blue markers */}
        {data.trucks.map(truck => (
          <CircleMarker
            key={truck.id}
            center={[truck.lat, truck.lon]}
            radius={10}
            pathOptions={{ color: '#1d4ed8', fillColor: '#2563eb', fillOpacity: 0.85 }}
          >
            <Tooltip direction="top" offset={[0, -8]}>
              <strong>{truck.name}</strong><br />
              Capacity: {truck.capacity} kg
            </Tooltip>
          </CircleMarker>
        ))}

        {/* Orders — red markers */}
        {data.orders.map(order => (
          <CircleMarker
            key={order.id}
            center={[order.lat, order.lon]}
            radius={7}
            pathOptions={{ color: '#b91c1c', fillColor: '#dc2626', fillOpacity: 0.85 }}
          >
            <Tooltip direction="top" offset={[0, -6]}>
              <strong>{order.id}</strong><br />
              {order.weight} kg — <em>{order.priority}</em>
            </Tooltip>
          </CircleMarker>
        ))}

        {/* Greedy — blue dashed lines */}
        {showGreedy && greedyAssignments.map(a => {
          const tp = truckPos(a.truck_id)
          const op = orderPos(a.order_id)
          if (!tp || !op) return null
          return (
            <Polyline
              key={`g-${a.truck_id}-${a.order_id}`}
              positions={[tp, op]}
              pathOptions={{
                color: '#2563eb',
                weight: multiAlgo ? 2 : 3,
                dashArray: multiAlgo ? '6 4' : null,
                opacity: 0.8,
              }}
            >
              <Tooltip sticky>
                <strong>Greedy: {a.truck_id} → {a.order_id}</strong><br />
                {a.distance_km} km<br />
                <em style={{ fontSize: '0.8em', color: '#475569' }}>{a.reason}</em>
              </Tooltip>
            </Polyline>
          )
        })}

        {/* Hungarian — amber solid lines */}
        {showHungarian && hungarianAssignments.map(a => {
          const tp = truckPos(a.truck_id)
          const op = orderPos(a.order_id)
          if (!tp || !op) return null
          return (
            <Polyline
              key={`h-${a.truck_id}-${a.order_id}`}
              positions={[tp, op]}
              pathOptions={{ color: '#d97706', weight: multiAlgo ? 2 : 3, opacity: 0.8 }}
            >
              <Tooltip sticky>
                <strong>Hungarian: {a.truck_id} → {a.order_id}</strong><br />
                {a.distance_km} km<br />
                <em style={{ fontSize: '0.8em', color: '#475569' }}>{a.reason}</em>
              </Tooltip>
            </Polyline>
          )
        })}

        {/* Weighted Hungarian — purple dotted lines */}
        {showWH && whAssignments.map(a => {
          const tp = truckPos(a.truck_id)
          const op = orderPos(a.order_id)
          if (!tp || !op) return null
          return (
            <Polyline
              key={`wh-${a.truck_id}-${a.order_id}`}
              positions={[tp, op]}
              pathOptions={{
                color: '#7c3aed',
                weight: multiAlgo ? 2 : 3,
                dashArray: multiAlgo ? '2 5' : '4 4',
                opacity: 0.85,
              }}
            >
              <Tooltip sticky>
                <strong>Weighted Hungarian: {a.truck_id} → {a.order_id}</strong><br />
                {a.distance_km} km<br />
                <em style={{ fontSize: '0.8em', color: '#475569' }}>{a.reason}</em>
              </Tooltip>
            </Polyline>
          )
        })}
      </MapContainer>
    </div>
  )
}
