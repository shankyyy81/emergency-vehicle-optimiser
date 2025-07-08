from collections import deque, Counter

class TrafficAnalyzer:
    """
    Analyzes historical traffic data for pattern detection and prediction.
    Supports peak hour detection, bottleneck identification, and congestion prediction.
    """
    def __init__(self, logger):
        self.logger = logger  # Logger instance

    def detect_peak_hours(self, intersection_id, window=10):
        # Returns the tick(s) with highest average density in the last 'window' ticks
        history = self.logger.history[intersection_id]
        if not history:
            return []
        recent = list(history)[-window:]
        tick_density = [(tick, sum(lane_densities.values())) for tick, _, lane_densities in recent]
        if not tick_density:
            return []
        max_density = max(d for _, d in tick_density)
        return [tick for tick, d in tick_density if d == max_density]

    def detect_bottlenecks(self, intersection_id, threshold=10):
        # Returns lanes that frequently exceed the density threshold
        history = self.logger.history[intersection_id]
        lane_counts = Counter()
        for _, _, lane_densities in history:
            for lane_id, density in lane_densities.items():
                if density >= threshold:
                    lane_counts[lane_id] += 1
        # Return lanes with most frequent congestion
        if not lane_counts:
            return []
        max_count = max(lane_counts.values())
        return [lane for lane, count in lane_counts.items() if count == max_count]

    def predict_congestion(self, intersection_id):
        # Placeholder for future ML-based prediction
        # For now, just return the lane with highest average density
        history = self.logger.history[intersection_id]
        lane_totals = Counter()
        lane_counts = Counter()
        for _, _, lane_densities in history:
            for lane_id, density in lane_densities.items():
                lane_totals[lane_id] += density
                lane_counts[lane_id] += 1
        if not lane_totals:
            return None
        avg_density = {lane: lane_totals[lane]/lane_counts[lane] for lane in lane_totals}
        if not avg_density:
            return None
        return max(avg_density, key=lambda k: avg_density[k]) 