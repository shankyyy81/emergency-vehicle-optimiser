const BASE_URL = "http://localhost:8000";

export async function getState() {
  const res = await fetch(`${BASE_URL}/state`);
  return res.json();
}

export async function tick() {
  const res = await fetch(`${BASE_URL}/tick`, { method: "POST" });
  return res.json();
}

export async function reset() {
  const res = await fetch(`${BASE_URL}/reset`, { method: "POST" });
  return res.json();
}

export async function getHistory(intersectionId: string) {
  const res = await fetch(`${BASE_URL}/history/${intersectionId}`);
  return res.json();
}

export async function updateTraffic({ intersection_id, direction, congestion, incident, incident_duration }: {
  intersection_id: string;
  direction: string;
  congestion?: number;
  incident?: string;
  incident_duration?: number;
}) {
  const res = await fetch(`${BASE_URL}/update_traffic`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ intersection_id, direction, congestion, incident, incident_duration })
  });
  return res.json();
} 