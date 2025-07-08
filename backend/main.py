from modules.graph_manager import GraphManager
from modules.simulation_runner import SimulationRunner
from modules.signal_controller import SignalController
from modules.emergency_handler import EmergencyHandler
from modules.logger import Logger
from modules.traffic_analyzer import TrafficAnalyzer

if __name__ == "__main__":
    # Initialize city graph
    graph_manager = GraphManager()
    intersections = graph_manager.intersections

    # Initialize modules
    sim_runner = SimulationRunner(graph_manager, vehicle_rate=10, emergency_rate=0.2)
    signal_controller = SignalController(intersections, min_green=10, max_green=60, window_size=6)
    logger = Logger(intersections)
    emergency_handler = EmergencyHandler(intersections, signal_controller)
    traffic_analyzer = TrafficAnalyzer(logger)

    # Get topological order for synchronization
    topo_order = graph_manager.topological_sort()

    # Run simulation for 10 ticks with advanced synchronization
    for tick in range(10):
        print(f"\n--- Tick {tick+1} ---")
        sim_runner.tick()
        signal_controller.update_lane_density()
        signal_controller.synchronize_signals(topo_order)
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

    # Demo: TrafficAnalyzer features for the first intersection
    first_iid = list(intersections.keys())[0]
    print(f"\n--- TrafficAnalyzer for Intersection {first_iid} ---")
    peak_hours = traffic_analyzer.detect_peak_hours(first_iid)
    bottlenecks = traffic_analyzer.detect_bottlenecks(first_iid)
    predicted = traffic_analyzer.predict_congestion(first_iid)
    print(f"Peak hours (ticks with highest density): {peak_hours}")
    print(f"Bottleneck lanes (most frequently congested): {bottlenecks}")
    print(f"Predicted most congested lane: {predicted}")

    # Demo: Dijkstra's shortest path between two intersections
    start, end = list(intersections.keys())[0], list(intersections.keys())[1]
    path, cost = graph_manager.shortest_path(start, end)
    print(f"\nShortest path from {start} to {end}: {path} (total weight: {cost})") 