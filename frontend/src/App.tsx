import React from "react";
import MapView from "./components/MapView";
import { getState, tick, reset } from "./api";

function App() {
  const [state, setState] = React.useState<any>(null);
  const [loading, setLoading] = React.useState(false);

  const fetchState = async () => {
    setLoading(true);
    setState(await getState());
    setLoading(false);
  };

  React.useEffect(() => {
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
      <MapView />
      <button onClick={handleTick} disabled={loading}>Next Tick</button>
      <button onClick={handleReset} disabled={loading} style={{ marginLeft: 8 }}>Reset</button>
      <pre style={{ marginTop: 24, background: "#f0f0f0", padding: 16, color: "#000" }}>
        {state ? JSON.stringify(state, null, 2) : "Loading..."}
      </pre>
    </div>
  );
}

export default App;
