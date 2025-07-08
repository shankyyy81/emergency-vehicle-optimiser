from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from modules.graph_manager import GraphManager
from modules.simulation_runner import SimulationRunner
from modules.signal_controller import SignalController
from modules.emergency_handler import EmergencyHandler
from modules.logger import Logger
from fastapi import Query

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
sim_runner = SimulationRunner(graph_manager, vehicle_rate=10, emergency_rate=0.2)
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
    path, total_distance = graph_manager.shortest_path(from_id, to_id)
    # For now, estimate time as 1 unit distance = 1 minute
    estimated_time = total_distance  # You can enhance this with signal/wait logic later
    return {
        "path": path,
        "total_distance": total_distance,
        "estimated_time_min": estimated_time
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
    sim_runner = SimulationRunner(graph_manager, vehicle_rate=10, emergency_rate=0.2)
    signal_controller = SignalController(intersections, min_green=10, max_green=60, window_size=6)
    logger = Logger(intersections)
    emergency_handler = EmergencyHandler(intersections, signal_controller)
    topo_order = graph_manager.topological_sort()
    return {"status": "reset complete"} 