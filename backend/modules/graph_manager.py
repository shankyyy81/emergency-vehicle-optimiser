from models.intersection import Intersection
from models.road import Road

class GraphManager:
    """
    Handles city map creation, intersection registration, and traffic weight updates.
    Maintains an adjacency list representation of the city graph.
    """
    def __init__(self):
        self.intersections = {}  # id -> Intersection
        self.roads = {}          # id -> Road
        self.adjacency = {}      # id -> set of neighbor ids
        self._initialize_chennai_graph()

    def add_intersection(self, intersection_id):
        if intersection_id not in self.intersections:
            self.intersections[intersection_id] = Intersection(intersection_id)
            self.adjacency[intersection_id] = set()

    def add_road(self, road_id, from_id, to_id, is_one_way=True, weight=1.0):
        road = Road(road_id, from_id, to_id, is_one_way, weight)
        self.roads[road_id] = road
        self.adjacency[from_id].add(to_id)
        if not is_one_way:
            self.adjacency[to_id].add(from_id)

    def update_road_weight(self, road_id, new_weight):
        if road_id in self.roads:
            self.roads[road_id].weight = new_weight

    def _initialize_chennai_graph(self):
        # List of intersections
        nodes = [
            'Koyambedu', 'Anna Nagar', 'Egmore', 'T Nagar', 'Guindy', 'Adyar', 'Saidapet',
            'Mylapore', 'Nungambakkam', 'Velachery', 'Tambaram', 'Perambur', 'Ambattur',
            'Thiruvanmiyur', 'Vadapalani', 'Royapettah'
        ]
        for node in nodes:
            self.add_intersection(node)
        # List of roads (edges)
        edges = [
            ('R1', 'Koyambedu', 'Anna Nagar'),
            ('R2', 'Koyambedu', 'Ambattur'),
            ('R3', 'Anna Nagar', 'Nungambakkam'),
            ('R4', 'Nungambakkam', 'Egmore'),
            ('R5', 'Egmore', 'Royapettah'),
            ('R6', 'Royapettah', 'Mylapore'),
            ('R7', 'Mylapore', 'Adyar'),
            ('R8', 'Adyar', 'Thiruvanmiyur'),
            ('R9', 'Thiruvanmiyur', 'Velachery'),
            ('R10', 'Velachery', 'Guindy'),
            ('R11', 'Guindy', 'Saidapet'),
            ('R12', 'Saidapet', 'T Nagar'),
            ('R13', 'T Nagar', 'Vadapalani'),
            ('R14', 'Vadapalani', 'Koyambedu'),
            ('R15', 'T Nagar', 'Mylapore'),
            ('R16', 'Tambaram', 'Velachery'),
            ('R17', 'Tambaram', 'Guindy'),
            ('R18', 'Perambur', 'Anna Nagar'),
            ('R19', 'Perambur', 'Egmore'),
            ('R20', 'Ambattur', 'Perambur'),
        ]
        for road_id, from_id, to_id in edges:
            self.add_road(road_id, from_id, to_id, is_one_way=False, weight=1.0)

    def topological_sort(self):
        # Kahn's algorithm for topological sorting
        in_degree = {node: 0 for node in self.intersections}
        for from_node, neighbors in self.adjacency.items():
            for to_node in neighbors:
                in_degree[to_node] += 1
        queue = [node for node, deg in in_degree.items() if deg == 0]
        sorted_order = []
        while queue:
            node = queue.pop(0)
            sorted_order.append(node)
            for neighbor in self.adjacency[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        if len(sorted_order) != len(self.intersections):
            # Cycle detected, fallback to arbitrary order
            return list(self.intersections.keys())
        return sorted_order 