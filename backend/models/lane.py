class Lane:
    """
    Represents a lane within a road or intersection.
    Attributes:
        id (str): Unique identifier for the lane.
        direction (str): Direction of the lane (e.g., 'N', 'S', 'E', 'W').
        vehicles (list): List of Vehicle objects currently in the lane.
        traffic_density (int): Number of vehicles in the lane (for simulation).
    """
    def __init__(self, id, direction):
        self.id = id
        self.direction = direction
        self.vehicles = []  # List of Vehicle objects
        self.traffic_density = 0

    def to_dict(self):
        return {
            'id': self.id,
            'direction': self.direction,
            'vehicles': [v.to_dict() for v in self.vehicles],
            'traffic_density': self.traffic_density
        } 