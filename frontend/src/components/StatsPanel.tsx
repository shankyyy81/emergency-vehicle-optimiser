import React, { useState } from 'react';
import { updateTraffic } from '../api';

interface StatsPanelProps {
  state: any;
}

const directions = ['N', 'S', 'E', 'W'];

const StatsPanel: React.FC<StatsPanelProps> = ({ state }) => {
  const [intersectionId, setIntersectionId] = useState('');
  const [direction, setDirection] = useState('N');
  const [congestion, setCongestion] = useState<number | ''>('');
  const [incident, setIncident] = useState('');
  const [incidentDuration, setIncidentDuration] = useState<number | ''>('');
  const [message, setMessage] = useState('');

  if (!state) return <div>Loading stats...</div>;

  // Total vehicles
  const totalVehicles = state.vehicles ? state.vehicles.length : 0;
  // Emergency vehicles
  const emergencyVehicles = state.vehicles ? state.vehicles.filter((v: any) => v.is_emergency).length : 0;
  // Average congestion (vehicles per lane)
  let totalLanes = 0;
  let totalDensity = 0;
  let peakIntersection = null;
  let peakDensity = -1;
  if (state.intersections) {
    Object.values(state.intersections).forEach((i: any) => {
      let intersectionDensity = 0;
      i.lanes.forEach((lane: any) => {
        totalLanes++;
        totalDensity += lane.traffic_density;
        intersectionDensity += lane.traffic_density;
      });
      if (intersectionDensity > peakDensity) {
        peakDensity = intersectionDensity;
        peakIntersection = i.id;
      }
    });
  }
  const avgCongestion = totalLanes ? (totalDensity / totalLanes).toFixed(2) : 0;
  // Current tick (if available)
  const currentTick = state.tick_counter !== undefined ? state.tick_counter : undefined;

  // Gather intersection options
  const intersectionOptions = state.intersections ? Object.keys(state.intersections) : [];

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!intersectionId || !direction) {
      setMessage('Please select intersection and direction.');
      return;
    }
    const res = await updateTraffic({
      intersection_id: intersectionId,
      direction,
      congestion: congestion === '' ? undefined : Number(congestion),
      incident: incident || undefined,
      incident_duration: incidentDuration === '' ? undefined : Number(incidentDuration),
    });
    if (res.status === 'success') {
      setMessage('Traffic update sent!');
    } else {
      setMessage('Error: ' + (res.message || 'Unknown error'));
    }
  };

  return (
    <div style={{ background: '#e3f2fd', color: '#000', padding: 16, borderRadius: 8, marginTop: 24, marginBottom: 16, maxWidth: 600 }}>
      <h2 style={{ marginTop: 0 }}>Simulation Stats</h2>
      <div><b>Total Vehicles:</b> {totalVehicles}</div>
      <div><b>Emergency Vehicles:</b> {emergencyVehicles}</div>
      <div><b>Average Congestion (vehicles/lane):</b> {avgCongestion}</div>
      <div><b>Peak Congestion Intersection:</b> {peakIntersection ? `${peakIntersection} (${peakDensity})` : 'N/A'}</div>
      {currentTick !== undefined && <div><b>Current Tick:</b> {currentTick}</div>}
      <hr style={{ margin: '18px 0' }} />
      <form onSubmit={handleUpdate} style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        <div style={{ fontWeight: 600 }}>Manual Traffic Update</div>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <select value={intersectionId} onChange={e => setIntersectionId(e.target.value)} required>
            <option value="">Select Intersection</option>
            {intersectionOptions.map((id: string) => (
              <option key={id} value={id}>{id}</option>
            ))}
          </select>
          <select value={direction} onChange={e => setDirection(e.target.value)} required>
            {directions.map(d => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>
          <input
            type="number"
            min={0}
            placeholder="Congestion (vehicles)"
            value={congestion}
            onChange={e => setCongestion(e.target.value === '' ? '' : Number(e.target.value))}
            style={{ width: 120 }}
          />
          <input
            type="text"
            placeholder="Incident (e.g. accident)"
            value={incident}
            onChange={e => setIncident(e.target.value)}
            style={{ width: 120 }}
          />
          <input
            type="number"
            min={1}
            placeholder="Incident Duration (ticks)"
            value={incidentDuration}
            onChange={e => setIncidentDuration(e.target.value === '' ? '' : Number(e.target.value))}
            style={{ width: 120 }}
          />
          <button type="submit">Send Update</button>
        </div>
        {message && <div style={{ color: message.startsWith('Error') ? 'red' : 'green', marginTop: 4 }}>{message}</div>}
      </form>
    </div>
  );
};

export default StatsPanel; 