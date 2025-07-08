import React from 'react';

interface StatsPanelProps {
  state: any;
}

const StatsPanel: React.FC<StatsPanelProps> = ({ state }) => {
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

  return (
    <div style={{ background: '#e3f2fd', color: '#000', padding: 16, borderRadius: 8, marginTop: 24, marginBottom: 16, maxWidth: 600 }}>
      <h2 style={{ marginTop: 0 }}>Simulation Stats</h2>
      <div><b>Total Vehicles:</b> {totalVehicles}</div>
      <div><b>Emergency Vehicles:</b> {emergencyVehicles}</div>
      <div><b>Average Congestion (vehicles/lane):</b> {avgCongestion}</div>
      <div><b>Peak Congestion Intersection:</b> {peakIntersection ? `${peakIntersection} (${peakDensity})` : 'N/A'}</div>
      {currentTick !== undefined && <div><b>Current Tick:</b> {currentTick}</div>}
    </div>
  );
};

export default StatsPanel; 