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