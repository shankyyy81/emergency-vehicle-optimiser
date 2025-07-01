class SignalState:
    """
    Represents the state of a traffic signal at an intersection.
    Attributes:
        green_lanes (list): List of lane IDs currently having green signal.
        red_lanes (list): List of lane IDs currently having red signal.
        duration (int): Duration of the current signal state in seconds.
        timestamp (float): Time when the state was set (for rollback/logging).
    """
    def __init__(self, green_lanes, red_lanes, duration, timestamp):
        self.green_lanes = green_lanes
        self.red_lanes = red_lanes
        self.duration = duration
        self.timestamp = timestamp 