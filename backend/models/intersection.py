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