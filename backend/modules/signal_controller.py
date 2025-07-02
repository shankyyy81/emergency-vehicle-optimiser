import heapq
import time
from collections import deque
from models.signal_state import SignalState

class SlidingWindow:
    """
    Maintains a sliding window of vehicle counts for a lane.
    """
    def __init__(self, window_size):
        self.window = deque(maxlen=window_size)

    def add(self, count):
        self.window.append(count)

    def average(self):
        return sum(self.window) / len(self.window) if self.window else 0

class SignalController:
    """
    Manages signal timings based on lane traffic density using a max-heap (priority queue).
    Updates signal cycles in real time.
    """
    def __init__(self, intersections, min_green=10, max_green=60, window_size=6):
        self.intersections = intersections  # id -> Intersection
        self.min_green = min_green
        self.max_green = max_green
        self.window_size = window_size  # e.g., 6 ticks = 1 minute if tick=10s
        # For each lane, maintain a sliding window of densities
        self.lane_windows = {}  # lane_id -> SlidingWindow
        self._init_lane_windows()

    def _init_lane_windows(self):
        for intersection in self.intersections.values():
            for lane in intersection.lanes:
                self.lane_windows[lane.id] = SlidingWindow(self.window_size)

    def update_lane_density(self):
        # Call this every tick to update sliding window for each lane
        for intersection in self.intersections.values():
            for lane in intersection.lanes:
                self.lane_windows[lane.id].add(lane.traffic_density)

    def compute_signal_schedule(self, intersection_id):
        intersection = self.intersections[intersection_id]
        heap = []
        for lane in intersection.lanes:
            avg_density = self.lane_windows[lane.id].average()
            # Use negative for max-heap
            heapq.heappush(heap, (-avg_density, lane.id))
        # Allocate green durations
        green_lanes = []
        red_lanes = []
        total_lanes = len(intersection.lanes)
        # Give green to top 1 or 2 lanes (can be adjusted)
        for _ in range(min(2, total_lanes)):
            if heap:
                _, lane_id = heapq.heappop(heap)
                green_lanes.append(lane_id)
        # The rest get red
        while heap:
            _, lane_id = heapq.heappop(heap)
            red_lanes.append(lane_id)
        # Duration proportional to max avg density, within bounds
        max_density = max([self.lane_windows[lid].average() for lid in green_lanes], default=1)
        duration = int(self.min_green + (self.max_green - self.min_green) * min(max_density / 10, 1))
        # Set signal state
        state = SignalState(green_lanes, red_lanes, duration, time.time())
        intersection.signal_state = state
        return state

    def tick(self):
        self.update_lane_density()
        for intersection_id in self.intersections:
            self.compute_signal_schedule(intersection_id) 