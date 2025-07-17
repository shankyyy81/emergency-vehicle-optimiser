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
    def __init__(self, graph_manager, vehicle_rate=30, emergency_rate=0.2):
        self.graph_manager = graph_manager
        self.vehicle_rate = vehicle_rate  # vehicles per tick (increased for Chennai)
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
        # Increase chance of bus and emergency vehicles for realism
        vehicle_type = random.choices(['car', 'bus', 'ambulance'], weights=[0.7, 0.2, 0.1])[0]
        is_emergency = vehicle_type == 'ambulance' and random.random() < self.emergency_rate
        vehicle_id = f"V{self.vehicle_id_counter}"
        self.vehicle_id_counter += 1
        vehicle = Vehicle(vehicle_id, vehicle_type, is_emergency)
        self.vehicles[vehicle_id] = vehicle
        # Assign to a random lane, but bias toward already busy lanes
        busy_lanes = [lane for lane in self.active_lanes if lane.traffic_density > 5]
        if busy_lanes and random.random() < 0.5:
            lane = random.choice(busy_lanes)
        else:
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
        self.simulate_random_incidents()
        self.update_incident_durations()

    def simulate_random_incidents(self, probability=0.08):
        # 8% chance per tick to create a random incident on a random lane
        if random.random() < probability:
            lane = random.choice(self.active_lanes)
            if lane.incident is None:
                lane.incident = random.choice(['accident', 'block'])
                lane.incident_duration = random.randint(2, 5)

    def update_incident_durations(self):
        for lane in self.active_lanes:
            if lane.incident:
                lane.incident_duration -= 1
                if lane.incident_duration <= 0:
                    lane.incident = None
                    lane.incident_duration = 0

    def update_lane_from_traffic(self, intersection_id, direction, congestion=None, incident=None, incident_duration=None):
        # Find the lane by intersection and direction
        lane_id = f"{intersection_id}_{direction}"
        lane = next((l for l in self.active_lanes if l.id == lane_id), None)
        if lane:
            if congestion is not None:
                lane.traffic_density = congestion
            if incident:
                lane.incident = incident
                lane.incident_duration = incident_duration or 3

    def run(self, ticks=10, delay=1):
        for _ in range(ticks):
            self.tick()
            print(f"Tick complete. Active vehicles: {len(self.vehicles)}")
            time.sleep(delay) 