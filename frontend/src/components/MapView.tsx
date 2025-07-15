import React, { useEffect, useState, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, CircleMarker, Tooltip } from 'react-leaflet';
import L from 'leaflet';
import type { LatLngExpression } from 'leaflet';
import { getState } from '../api';

const chennaiCenter: LatLngExpression = [13.0827, 80.2707];
const zoom = 12;

const greenIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
  shadowSize: [41, 41],
});
const redIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
  shadowSize: [41, 41],
});

const carIcon = new L.DivIcon({
  html: '🚗',
  iconSize: [48, 48],
  className: '',
});

const vehicleColor = '#1976d2';
const emergencyColor = '#d32f2f';

interface Intersection {
  id: string;
  coordinates: LatLngExpression;
  signal_state: any;
  lanes: any[];
}

interface Vehicle {
  id: string;
  type: string;
  is_emergency: boolean;
  intersectionId?: string;
}

interface ShortestPathResult {
  path: string[];
  total_distance_km: number;
  estimated_time_min: number;
}

// Helper: get congestion color based on vehicle count
const getCongestionColor = (count: number) => {
  if (count < 20) return '#43a047'; // green
  if (count <= 70) return '#fbc02d'; // yellow
  return '#e53935'; // red
};

// Helper: create a colored DivIcon for congestion
const createCongestionIcon = (count: number) => {
  const color = getCongestionColor(count);
  return new L.DivIcon({
    html: `<div style="background:${color};width:32px;height:32px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;font-weight:bold;font-size:16px;border:2px solid #222;box-shadow:0 0 6px ${color};">${count}</div>`,
    className: '',
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -16],
  });
};

interface MapViewProps {
  state: any;
}

const MapView: React.FC<MapViewProps> = ({ state }) => {
  const [intersections, setIntersections] = useState<Intersection[]>([]);
  const [roads, setRoads] = useState<{ from: LatLngExpression; to: LatLngExpression }[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [selected, setSelected] = useState<{ from?: string; to?: string }>({});
  const [shortestPath, setShortestPath] = useState<ShortestPathResult | null>(null);
  const [pathCoords, setPathCoords] = useState<LatLngExpression[]>([]);
  const [loadingPath, setLoadingPath] = useState(false);
  const [carPosition, setCarPosition] = useState<LatLngExpression | null>(null);
  const [animating, setAnimating] = useState(false);
  const animationRef = useRef<NodeJS.Timeout | null>(null);

  // Update intersections, roads, and vehicles when state prop changes
  useEffect(() => {
    if (!state) return;
    const ints: Intersection[] = Object.values(state.intersections).map((i: any) => ({
      id: i.id,
      coordinates: i.coordinates as LatLngExpression,
      signal_state: i.signal_state,
      lanes: i.lanes,
    }));
    setIntersections(ints);
    if (state.roads) {
      const rds = Object.values(state.roads).map((r: any) => ({
        from: state.intersections[r.from_intersection].coordinates as LatLngExpression,
        to: state.intersections[r.to_intersection].coordinates as LatLngExpression,
      }));
      setRoads(rds);
    } else {
      setRoads(
        ints.slice(1).map((to, idx) => ({
          from: ints[idx].coordinates,
          to: to.coordinates,
        }))
      );
    }
    const vehs: Vehicle[] = (state.vehicles || []).map((v: any) => {
      let intersectionId = undefined;
      for (const i of ints) {
        for (const lane of i.lanes) {
          if (lane.vehicles.some((veh: any) => veh.id === v.id)) {
            intersectionId = i.id;
            break;
          }
        }
        if (intersectionId) break;
      }
      return { ...v, intersectionId };
    });
    setVehicles(vehs);
  }, [state]);

  // Animate car when pathCoords changes
  useEffect(() => {
    if (pathCoords.length > 1) {
      setCarPosition(pathCoords[0]);
      setAnimating(true);
      let idx = 0;
      if (animationRef.current) clearInterval(animationRef.current);
      animationRef.current = setInterval(() => {
        idx++;
        if (idx < pathCoords.length) {
          setCarPosition(pathCoords[idx]);
        } else {
          setAnimating(false);
          if (animationRef.current) clearInterval(animationRef.current);
        }
      }, 1200); // 1200ms per segment (slower)
    } else {
      setCarPosition(null);
      setAnimating(false);
      if (animationRef.current) clearInterval(animationRef.current);
    }
    return () => {
      if (animationRef.current) clearInterval(animationRef.current);
    };
  }, [pathCoords]);

  // Helper: get marker icon by signal state
  const getMarkerIcon = (signal_state: any) => {
    if (!signal_state) return redIcon;
    return (signal_state.green_lanes && signal_state.green_lanes.length > 0) ? greenIcon : redIcon;
  };

  // Helper: get emoji for vehicle type
  const getVehicleEmoji = (type: string) => {
    if (type === 'car') return '🚗'; // We'll wrap this in a blue background below
    if (type === 'bus') return '🚌';
    if (type === 'bike' || type === 'motorcycle') return '🏍️';
    return '❓';
  };

  // Handle marker click for selection
  const handleMarkerClick = (id: string) => {
    if (!selected.from) {
      setSelected({ from: id });
      setShortestPath(null);
      setPathCoords([]);
    } else if (!selected.to && id !== selected.from) {
      setSelected({ from: selected.from, to: id });
      fetchShortestPath(selected.from, id);
    } else if (id === selected.from) {
      setSelected({});
      setShortestPath(null);
      setPathCoords([]);
    }
  };

  // Fetch shortest path from backend
  const fetchShortestPath = async (from: string, to: string) => {
    setLoadingPath(true);
    setShortestPath(null);
    setPathCoords([]);
    try {
      const res = await fetch(
        `http://localhost:8000/shortest_path?from=${encodeURIComponent(from)}&to=${encodeURIComponent(to)}`
      );
      const data = await res.json();
      setShortestPath(data);
      // Map path to coordinates
      const coords = data.path.map((id: string) => {
        const intersection = intersections.find(i => i.id === id);
        return intersection ? intersection.coordinates : null;
      }).filter(Boolean);
      setPathCoords(coords);
    } catch (e) {
      setShortestPath(null);
      setPathCoords([]);
    }
    setLoadingPath(false);
  };

  // Clear selection
  const clearSelection = () => {
    setSelected({});
    setShortestPath(null);
    setPathCoords([]);
  };

  return (
    <>
      <MapContainer center={chennaiCenter} zoom={zoom} style={{ height: '500px', width: '100%' }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {roads.map((road, idx) => (
          <Polyline key={idx} positions={[road.from, road.to]} pathOptions={{ color: 'blue' }} />
        ))}
        {/* Highlight shortest path */}
        {pathCoords.length > 1 && (
          <Polyline positions={pathCoords} pathOptions={{ color: 'orange', weight: 6 }} />
        )}
        {/* Animated car marker */}
        {carPosition && (
          <Marker position={carPosition} icon={carIcon} zIndexOffset={1000} />
        )}
        {intersections.map((intersection) => {
          // Get vehicles at this intersection
          const vehiclesHere = vehicles.filter(v => v.intersectionId === intersection.id);
          return (
            <Marker
              key={intersection.id}
              position={intersection.coordinates}
              icon={getMarkerIcon(intersection.signal_state)}
              eventHandlers={{
                click: () => handleMarkerClick(intersection.id),
              }}
            >
              <Popup>
                <b>{intersection.id}</b>
                <br />
                <b>Signal:</b> {intersection.signal_state ? `Green: [${intersection.signal_state.green_lanes.join(', ')}], Red: [${intersection.signal_state.red_lanes.join(', ')}]` : 'N/A'}
                <br />
                <b>Lanes:</b>
                <ul>
                  {intersection.lanes.map((lane: any) => (
                    <li key={lane.id}>{lane.id} (Density: {lane.traffic_density})</li>
                  ))}
                </ul>
                <b>Vehicles:</b>
                <ul>
                  {vehiclesHere.map(v => (
                    <li key={v.id} style={{ color: v.is_emergency ? emergencyColor : vehicleColor }}>
                      {v.id} ({v.type}) {v.is_emergency ? '🚨' : ''}
                    </li>
                  ))}
                </ul>
                <br />
                <b>Click to {selected.from === intersection.id ? 'clear selection' : !selected.from ? 'select as start' : 'select as end'}</b>
              </Popup>
              {/* Congestion badge as a Tooltip next to the marker */}
              <Tooltip direction="right" offset={[12, 0]} permanent>
                <span style={{
                  background: getCongestionColor(vehiclesHere.length),
                  color: 'white',
                  fontWeight: 'bold',
                  fontSize: 14,
                  borderRadius: '50%',
                  padding: '4px 10px',
                  border: '2px solid #222',
                  boxShadow: `0 0 6px ${getCongestionColor(vehiclesHere.length)}`,
                  display: 'inline-block',
                }}>{vehiclesHere.length}</span>
              </Tooltip>
            </Marker>
          );
        })}
      </MapContainer>
      <div style={{ marginTop: 16 }}>
        {selected.from && (
          <span>Start: <b>{selected.from}</b></span>
        )}
        {selected.to && (
          <span style={{ marginLeft: 16 }}>End: <b>{selected.to}</b></span>
        )}
        {(selected.from || selected.to) && (
          <button style={{ marginLeft: 16 }} onClick={clearSelection}>Clear Selection</button>
        )}
      </div>
      {loadingPath && <div>Calculating shortest path...</div>}
      {shortestPath && (
        <div style={{ marginTop: 8, background: '#f9fbe7', padding: 12, borderRadius: 8, color: '#000' }}>
          <b>Shortest Path:</b> {shortestPath.path.join(' → ')}<br />
          <b>Total Distance (km):</b> {shortestPath.total_distance_km}<br />
          <b>Estimated Time (min):</b> {shortestPath.estimated_time_min}
        </div>
      )}
    </>
  );
};

export default MapView; 