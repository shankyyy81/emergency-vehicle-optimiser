class Vehicle:
    """
    Represents a vehicle in the simulation.
    Attributes:
        id (str): Unique identifier for the vehicle.
        type (str): Type of vehicle (e.g., 'car', 'bus', 'ambulance').
        is_emergency (bool): Whether the vehicle is an emergency vehicle.
    """
    def __init__(self, id, type, is_emergency=False):
        self.id = id
        self.type = type
        self.is_emergency = is_emergency

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'is_emergency': self.is_emergency
        } 