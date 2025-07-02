from modules.graph_manager import GraphManager
from modules.simulation_runner import SimulationRunner
from modules.signal_controller import SignalController
from modules.emergency_handler import EmergencyHandler
from modules.logger import Logger

if __name__ == "__main__":
    # Initialize city graph
    graph_manager = GraphManager()
    intersections = graph_manager.intersections

    # Initialize modules
    sim_runner = SimulationRunner(graph_manager, vehicle_rate=10, emergency_rate=0.2)
    signal_controller = SignalController(intersections, min_green=10, max_green=60, window_size=6)
    logger = Logger(intersections)
    emergency_handler = EmergencyHandler(intersections, signal_controller)

    # Run simulation for 10 ticks
    for tick in range(10):
        print(f"\n--- Tick {tick+1} ---")
        sim_runner.tick()
        signal_controller.tick()
        emergency_handler.handle_emergencies()
        # Log signal states
        for iid, intersection in intersections.items():
            logger.log_state(iid, intersection.signal_state)
            state = intersection.signal_state
            print(f"Intersection {iid}: Green {state.green_lanes}, Red {state.red_lanes}, Duration {state.duration}s")
        print(f"Active vehicles: {len(sim_runner.vehicles)}")
        logger.next_tick()

    # Demo: Print peak congestion and average wait time for a few intersections
    print("\n--- Historical Data Analysis ---")
    for iid in list(intersections.keys())[:3]:  # Show for first 3 intersections
        peak_tick, peak_lane, max_density = logger.get_peak_congestion(iid)
        avg_wait = logger.get_average_wait_time(iid)
        print(f"Intersection {iid}: Peak congestion at tick {peak_tick} on lane {peak_lane} (density {max_density}), Avg. wait time: {avg_wait:.2f}s") 