import React, { useEffect, useState } from "react";
import { getState, tick, reset } from "./api";

function App() {
  const [state, setState] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const fetchState = async () => {
    setLoading(true);
    setState(await getState());
    setLoading(false);
  };

  useEffect(() => {
    fetchState();
  }, []);

  const handleTick = async () => {
    await tick();
    fetchState();
  };

  const handleReset = async () => {
    await reset();
    fetchState();
  };

  return (
    <div style={{ padding: 24 }}>
      <h1>Smart Traffic Light Dashboard</h1>
      <button onClick={handleTick} disabled={loading}>Next Tick</button>
      <button onClick={handleReset} disabled={loading} style={{ marginLeft: 8 }}>Reset</button>
      <pre style={{ marginTop: 24, background: "#f0f0f0", padding: 16, color: "#000" }}>
        {state ? JSON.stringify(state, null, 2) : "Loading..."}
      </pre>
    </div>
  );
}

export default App;
