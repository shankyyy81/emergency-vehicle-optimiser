from collections import deque

class Logger:
    """
    Logs historical signal states and supports rollback using a stack per intersection.
    Also stores historical traffic and signal data for pattern detection.
    """
    def __init__(self, intersections, history_limit=1000):
        self.intersections = intersections  # id -> Intersection
        self.state_stacks = {iid: [] for iid in intersections}
        self.history = {iid: deque(maxlen=history_limit) for iid in intersections}  # intersection_id -> deque of (tick, signal_state, lane_densities)
        self.tick_counter = 0

    def log_state(self, intersection_id, signal_state):
        self.state_stacks[intersection_id].append(signal_state)
        # Log lane densities as well
        intersection = self.intersections[intersection_id]
        lane_densities = {lane.id: lane.traffic_density for lane in intersection.lanes}
        self.history[intersection_id].append((self.tick_counter, signal_state, lane_densities))

    def next_tick(self):
        self.tick_counter += 1

    def rollback(self, intersection_id):
        if self.state_stacks[intersection_id]:
            return self.state_stacks[intersection_id].pop()
        return None

    def get_peak_congestion(self, intersection_id):
        # Returns the tick and lane with max density
        max_density = -1
        peak_tick = None
        peak_lane = None
        for tick, _, lane_densities in self.history[intersection_id]:
            for lane_id, density in lane_densities.items():
                if density > max_density:
                    max_density = density
                    peak_tick = tick
                    peak_lane = lane_id
        return peak_tick, peak_lane, max_density

    def get_average_wait_time(self, intersection_id):
        # Estimate: average green duration per lane
        total_duration = 0
        count = 0
        for _, signal_state, _ in self.history[intersection_id]:
            total_duration += signal_state.duration
            count += 1
        return total_duration / count if count else 0

    def get_lane_history(self, intersection_id, lane_id):
        # Returns a list of (tick, density) for a given lane
        return [(tick, lane_densities[lane_id]) for tick, _, lane_densities in self.history[intersection_id] if lane_id in lane_densities] 