import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, CircleMarker } from 'react-leaflet';
import L from 'leaflet';
import type { LatLngExpression } from 'leaflet';
import { getState } from '../api';

const chennaiCenter: LatLngExpression = [13.0827, 80.2707];
const zoom = 12;

// Marker icons for signal states
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

// Vehicle icons/colors
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

const MapView: React.FC = () => {
  const [intersections, setIntersections] = useState<Intersection[]>([]);
  const [roads, setRoads] = useState<{ from: LatLngExpression; to: LatLngExpression }[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);

  useEffect(() => {
    getState().then((data) => {
      // Extract intersections
      const ints: Intersection[] = Object.values(data.intersections).map((i: any) => ({
        id: i.id,
        coordinates: i.coordinates as LatLngExpression,
        signal_state: i.signal_state,
        lanes: i.lanes,
      }));
      setIntersections(ints);
      // Extract roads
      if (data.roads) {
        const rds = Object.values(data.roads).map((r: any) => ({
          from: data.intersections[r.from_intersection].coordinates as LatLngExpression,
          to: data.intersections[r.to_intersection].coordinates as LatLngExpression,
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
      // Extract vehicles and assign to intersections
      const vehs: Vehicle[] = (data.vehicles || []).map((v: any) => {
        // Try to find the intersection where this vehicle is present
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
    });
  }, []);

  // Helper: get marker icon by signal state
  const getMarkerIcon = (signal_state: any) => {
    if (!signal_state) return redIcon;
    return (signal_state.green_lanes && signal_state.green_lanes.length > 0) ? greenIcon : redIcon;
  };

  return (
    <MapContainer center={chennaiCenter} zoom={zoom} style={{ height: '500px', width: '100%' }}>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {roads.map((road, idx) => (
        <Polyline key={idx} positions={[road.from, road.to]} pathOptions={{ color: 'blue' }} />
      ))}
      {intersections.map((intersection) => (
        <Marker
          key={intersection.id}
          position={intersection.coordinates}
          icon={getMarkerIcon(intersection.signal_state)}
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
              {vehicles.filter(v => v.intersectionId === intersection.id).map(v => (
                <li key={v.id} style={{ color: v.is_emergency ? emergencyColor : vehicleColor }}>
                  {v.id} ({v.type}) {v.is_emergency ? '🚨' : ''}
                </li>
              ))}
            </ul>
          </Popup>
          {/* Show vehicles as colored dots at the intersection */}
          {vehicles.filter(v => v.intersectionId === intersection.id).map((v, idx) => (
            <CircleMarker
              key={v.id}
              center={intersection.coordinates}
              radius={6 + (v.is_emergency ? 2 : 0)}
              pathOptions={{ color: v.is_emergency ? emergencyColor : vehicleColor, fillColor: v.is_emergency ? emergencyColor : vehicleColor, fillOpacity: 1 }}
            />
          ))}
        </Marker>
      ))}
    </MapContainer>
  );
};

export default MapView; 