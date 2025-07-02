import random
import time
from models.vehicle import Vehicle
from models.lane import Lane
from modules.graph_manager import GraphManager

class SimulationRunner:
    """
    Simulates vehicle generation and movement through the city graph.
    Updates lane densities and supports emergency vehicle generation.
    """
    def __init__(self, graph_manager, vehicle_rate=5, emergency_rate=0.1):
        self.graph_manager = graph_manager
        self.vehicle_rate = vehicle_rate  # vehicles per tick
        self.emergency_rate = emergency_rate  # probability of emergency vehicle
        self.vehicle_id_counter = 0
        self.vehicles = {}  # vehicle_id -> Vehicle
        self.active_lanes = self._get_all_lanes()

    def _get_all_lanes(self):
        # For simplicity, each intersection has 4 lanes (N, S, E, W)
        directions = ['N', 'S', 'E', 'W']
        lanes = []
        for intersection in self.graph_manager.intersections.values():
            for d in directions:
                lane_id = f"{intersection.id}_{d}"
                lane = Lane(lane_id, d)
                intersection.lanes.append(lane)
                lanes.append(lane)
        return lanes

    def generate_vehicle(self):
        vehicle_type = random.choices(['car', 'bus', 'ambulance'], weights=[0.85, 0.1, 0.05])[0]
        is_emergency = vehicle_type == 'ambulance' and random.random() < self.emergency_rate
        vehicle_id = f"V{self.vehicle_id_counter}"
        self.vehicle_id_counter += 1
        vehicle = Vehicle(vehicle_id, vehicle_type, is_emergency)
        self.vehicles[vehicle_id] = vehicle
        # Assign to a random lane
        lane = random.choice(self.active_lanes)
        lane.vehicles.append(vehicle)
        lane.traffic_density += 1
        return vehicle, lane

    def move_vehicles(self):
        # For now, just randomly move vehicles to another lane or remove them
        for lane in self.active_lanes:
            if lane.vehicles:
                # 50% chance a vehicle leaves the lane (reaches destination)
                if random.random() < 0.5:
                    vehicle = lane.vehicles.pop(0)
                    lane.traffic_density -= 1
                    del self.vehicles[vehicle.id]
                # 30% chance a vehicle moves to another lane
                elif random.random() < 0.3:
                    vehicle = lane.vehicles.pop(0)
                    lane.traffic_density -= 1
                    new_lane = random.choice(self.active_lanes)
                    new_lane.vehicles.append(vehicle)
                    new_lane.traffic_density += 1

    def tick(self):
        # Simulate one time step
        for _ in range(self.vehicle_rate):
            self.generate_vehicle()
        self.move_vehicles()

    def run(self, ticks=10, delay=1):
        for _ in range(ticks):
            self.tick()
            print(f"Tick complete. Active vehicles: {len(self.vehicles)}")
            time.sleep(delay) 