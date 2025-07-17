import React from "react";
import MapView from "./components/MapView";
import StatsPanel from "./components/StatsPanel";
import { getState, tick, reset } from "./api";
import './App.css';

function App() {
  const [state, setState] = React.useState<any>(null);
  const [loading, setLoading] = React.useState(false);
  const [darkMode, setDarkMode] = React.useState(false);
  const [shortestPath, setShortestPath] = React.useState<any>(null);
  const [loadingPath, setLoadingPath] = React.useState(false);

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
    <div className={`app-container${darkMode ? ' dark-mode' : ''}`}>
      <div className="map-main">
        <MapView
          state={state}
          darkMode={darkMode}
          setShortestPath={setShortestPath}
          setLoadingPath={setLoadingPath}
        />
      </div>
      <div className="bottom-panel">
        <div className="floating-stats">
          <StatsPanel state={state} />
        </div>
        <div className="controls-inline">
          <button onClick={handleTick} disabled={loading}>Next Tick</button>
          <button onClick={handleReset} disabled={loading}>Reset</button>
          <button
            aria-label="Toggle dark mode"
            style={{ marginLeft: 12, fontSize: 22, background: 'none', color: 'var(--color-text)', border: 'none', cursor: 'pointer', padding: '6px 10px' }}
            onClick={() => setDarkMode((d) => !d)}
            title={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {darkMode ? '🌙' : '☀️'}
          </button>
        </div>
      </div>
      {/* Shortest path info always visible at the bottom left */}
      {(loadingPath || shortestPath) && (
        <div
          style={{
            position: 'fixed',
            left: 32,
            bottom: 32,
            background: darkMode ? '#232a36' : '#fff',
            color: darkMode ? '#fff' : '#111',
            padding: '22px 28px',
            borderRadius: '16px',
            zIndex: 9999,
            boxShadow: '0 4px 32px rgba(0,0,0,0.18)',
            border: darkMode ? '2px solid #333a4d' : '2px solid #e3e3e3',
            fontWeight: 500,
            fontSize: '1.08rem',
            maxWidth: 340,
            minWidth: 220,
            width: 'fit-content',
            textAlign: 'center',
            letterSpacing: '0.01em',
            pointerEvents: 'auto',
            lineHeight: 1.7,
          }}
        >
          {loadingPath ? (
            'Calculating shortest path...'
          ) : (
            <>
              <div style={{ fontWeight: 700, fontSize: '1.13rem', marginBottom: 10 }}>
                Shortest Path:<br />
                <span style={{ fontWeight: 800 }}>{shortestPath.path.join(' → ')}</span>
              </div>
              <div style={{ margin: '8px 0 0 0', fontWeight: 600 }}>
                <span>Total Distance (km): <b>{shortestPath.total_distance_km}</b></span><br />
                <span>Estimated Time (min): <b>{shortestPath.estimated_time_min}</b></span>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
