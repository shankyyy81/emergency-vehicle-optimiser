from models.vehicle import Vehicle

class EmergencyHandler:
    """
    Detects and handles emergency vehicle routes with signal override.
    """
    def __init__(self, intersections, signal_controller):
        self.intersections = intersections  # id -> Intersection
        self.signal_controller = signal_controller

    def detect_emergency(self):
        # Scan all lanes for emergency vehicles
        emergencies = []
        for intersection in self.intersections.values():
            for lane in intersection.lanes:
                for vehicle in lane.vehicles:
                    if vehicle.is_emergency:
                        emergencies.append((intersection.id, lane.id, vehicle))
        return emergencies

    def override_signal(self, intersection_id, lane_id):
        # Force green for the lane with emergency vehicle
        intersection = self.intersections[intersection_id]
        prev_state = intersection.signal_state
        green_lanes = [lane_id]
        red_lanes = [l.id for l in intersection.lanes if l.id != lane_id]
        # Short green duration for emergency
        from time import time as now
        state = self.signal_controller.push_signal_state(intersection_id, green_lanes, red_lanes, duration=15, timestamp=now())
        return prev_state, state

    def handle_emergencies(self):
        emergencies = self.detect_emergency()
        for intersection_id, lane_id, vehicle in emergencies:
            self.override_signal(intersection_id, lane_id) 