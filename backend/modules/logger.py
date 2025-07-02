class Logger:
    """
    Logs historical signal states and supports rollback using a stack per intersection.
    """
    def __init__(self, intersections):
        self.intersections = intersections  # id -> Intersection
        self.state_stacks = {iid: [] for iid in intersections}

    def log_state(self, intersection_id, signal_state):
        self.state_stacks[intersection_id].append(signal_state)

    def rollback(self, intersection_id):
        if self.state_stacks[intersection_id]:
            return self.state_stacks[intersection_id].pop()
        return None 