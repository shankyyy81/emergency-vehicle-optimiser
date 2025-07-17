# Smart Traffic Light Control System Backend

This backend simulates an intelligent, real-time traffic signal system for a city's network of roads and intersections. It uses advanced data structures and algorithms to manage traffic flow, prioritize lanes, detect emergency vehicles, and coordinate multiple intersections.

## Structure
- `models/`: Data models for intersections, roads, lanes, vehicles, and signal states.
- `modules/`: Core logic modules (to be implemented).
- `main.py`: Entry point for running the simulation.

## Features
- Graph-based city modeling
- Real-time lane traffic analysis
- Dynamic signal timing
- Emergency vehicle override
- Multi-intersection synchronization
- Signal state rollback
- Historical data logging

## Addressing Common Drawbacks in Emergency Vehicle Optimization Simulations

This project tackles several common limitations found in existing emergency vehicle optimization tools:

### 1. Static Traffic Conditions
**Drawback:** Many simulators assume traffic is static or only changes at fixed intervals, which doesn’t reflect real-world, dynamic congestion.
**Solution:** This simulation updates traffic state on every tick, allowing for dynamic and realistic congestion modeling. The backend can be extended to accept live data feeds or simulate random incidents.

### 2. No Visualization of Congestion
**Drawback:** Users can’t easily see where congestion is happening or how it affects emergency routes.
**Solution:** The frontend visualizes congestion on the map using color-coded markers and badges, showing the number and type of vehicles at each intersection. Congestion cues update dynamically with each simulation tick.

### 3. Lack of User Interaction
**Drawback:** Some tools don’t let users interactively test different scenarios or control the simulation.
**Solution:** The UI provides controls for stepping through the simulation, resetting, and toggling dark mode. Users can select start/end points for emergency vehicles and see the computed path.

### 4. No Feedback on Emergency Vehicle Progress
**Drawback:** It’s hard to see how quickly or efficiently the emergency vehicle is moving through the network.
**Solution:** The frontend animates the emergency vehicle along the computed path and displays stats such as total distance, estimated time, and current position.

### 5. No Scenario Reset or Replay
**Drawback:** Users can’t easily reset or replay scenarios to compare different strategies.
**Solution:** A “Reset” button restarts the simulation from the initial state, enabling easy scenario comparison.

## Requirements
- Python 3.8+
- (Dependencies to be added in `requirements.txt`) 