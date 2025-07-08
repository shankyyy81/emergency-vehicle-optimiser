class Intersection:
    """
    Represents a traffic intersection (node in the city graph).
    Attributes:
        id (str): Unique identifier for the intersection.
        lanes (list): List of Lane objects connected to this intersection.
        signal_state (SignalState): Current signal state at the intersection.
    """
    def __init__(self, id):
        self.id = id
        self.lanes = []  # List of Lane objects
        self.signal_state = None

    def to_dict(self):
        return {
            'id': self.id,
            'lanes': [lane.to_dict() for lane in self.lanes],
            'signal_state': self.signal_state.to_dict() if self.signal_state else None
        } 