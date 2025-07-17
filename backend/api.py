from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from modules.graph_manager import GraphManager
from modules.simulation_runner import SimulationRunner
from modules.signal_controller import SignalController
from modules.emergency_handler import EmergencyHandler
from modules.logger import Logger
from fastapi import Query
from fastapi import Request

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph_manager = GraphManager()
intersections = graph_manager.intersections
sim_runner = SimulationRunner(graph_manager, vehicle_rate=200, emergency_rate=0.1)
signal_controller = SignalController(intersections, min_green=10, max_green=60, window_size=6)
logger = Logger(intersections)
emergency_handler = EmergencyHandler(intersections, signal_controller)
topo_order = graph_manager.topological_sort()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/state")
def get_state():
    return {
        'intersections': {iid: intersection.to_dict() for iid, intersection in intersections.items()},
        'vehicles': [v.to_dict() for v in sim_runner.vehicles.values()]
    }

@app.get("/history/{intersection_id}")
def get_history(intersection_id: str):
    return logger.to_json(intersection_id)

@app.get("/shortest_path")
def shortest_path(from_id: str = Query(..., alias="from"), to_id: str = Query(..., alias="to")):
    # Use dynamic weights based on current simulation state
    path, total_distance, total_penalty = graph_manager.shortest_path_dynamic(from_id, to_id, intersections)
    # Use realistic speed for emergency vehicles (e.g., 30 km/h)
    avg_speed_kmh = 30
    if not path or len(path) < 2:
        return {"path": path, "total_distance_km": 0, "estimated_time_min": 0}
    # Estimated time = travel time + penalties
    travel_time = (total_distance / avg_speed_kmh) * 60  # in minutes
    estimated_time = travel_time + total_penalty
    return {
        "path": path,
        "total_distance_km": round(total_distance, 2),
        "estimated_time_min": round(estimated_time, 2)
    }

@app.post("/tick")
def tick():
    sim_runner.tick()
    signal_controller.update_lane_density()
    signal_controller.synchronize_signals(topo_order)
    emergency_handler.handle_emergencies()
    for iid, intersection in intersections.items():
        logger.log_state(iid, intersection.signal_state)
    logger.next_tick()
    return {"status": "tick complete"}

@app.post("/reset")
def reset():
    global graph_manager, intersections, sim_runner, signal_controller, logger, emergency_handler, topo_order
    graph_manager = GraphManager()
    intersections = graph_manager.intersections
    sim_runner = SimulationRunner(graph_manager, vehicle_rate=200, emergency_rate=0.1)
    signal_controller = SignalController(intersections, min_green=10, max_green=60, window_size=6)
    logger = Logger(intersections)
    emergency_handler = EmergencyHandler(intersections, signal_controller)
    topo_order = graph_manager.topological_sort()
    return {"status": "reset complete"}

@app.post("/update_traffic")
async def update_traffic(request: Request):
    data = await request.json()
    # Expecting: {"intersection_id": str, "direction": str, "congestion": int, "incident": str, "incident_duration": int}
    intersection_id = data.get("intersection_id")
    direction = data.get("direction")
    congestion = data.get("congestion")
    incident = data.get("incident")
    incident_duration = data.get("incident_duration")
    if intersection_id and direction:
        sim_runner.update_lane_from_traffic(intersection_id, direction, congestion, incident, incident_duration)
        return {"status": "success", "updated": {"intersection_id": intersection_id, "direction": direction, "congestion": congestion, "incident": incident, "incident_duration": incident_duration}}
    return {"status": "error", "message": "intersection_id and direction required"} 