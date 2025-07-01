class Road:
    """
    Represents a road (edge in the city graph).
    Attributes:
        id (str): Unique identifier for the road.
        from_intersection (str): ID of the starting intersection.
        to_intersection (str): ID of the ending intersection.
        lanes (list): List of Lane objects on this road.
        weight (float): Traffic weight (e.g., congestion, length).
        is_one_way (bool): Directional property of the road.
    """
    def __init__(self, id, from_intersection, to_intersection, is_one_way=True, weight=1.0):
        self.id = id
        self.from_intersection = from_intersection
        self.to_intersection = to_intersection
        self.lanes = []  # List of Lane objects
        self.weight = weight
        self.is_one_way = is_one_way 