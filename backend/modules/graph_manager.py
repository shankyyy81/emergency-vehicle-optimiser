from models.intersection import Intersection
from models.road import Road
from math import radians, sin, cos, sqrt, atan2

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

    def add_intersection(self, intersection_id, coordinates=None):
        if intersection_id not in self.intersections:
            self.intersections[intersection_id] = Intersection(intersection_id, coordinates)
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

    def haversine(self, coord1, coord2):
        # Coordinates in (lat, lng)
        R = 6371  # Earth radius in km
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c

    def _initialize_chennai_graph(self):
        # List of intersections with coordinates
        coords = {
            'Koyambedu': (13.0700, 80.2110),
            'Anna Nagar': (13.0878, 80.2102),
            'Egmore': (13.0827, 80.2622),
            'T Nagar': (13.0336, 80.2305),
            'Guindy': (13.0067, 80.2206),
            'Adyar': (13.0064, 80.2570),
            'Saidapet': (13.0291, 80.2209),
            'Mylapore': (13.0339, 80.2698),
            'Nungambakkam': (13.0604, 80.2412),
            'Velachery': (12.9784, 80.2214),
            'Tambaram': (12.9246, 80.1272),
            'Perambur': (13.1132, 80.2337),
            'Ambattur': (13.1143, 80.1480),
            'Thiruvanmiyur': (12.9847, 80.2606),
            'Vadapalani': (13.0496, 80.2127),
            'Royapettah': (13.0524, 80.2616),
        }
        nodes = list(coords.keys())
        for node in nodes:
            self.add_intersection(node, coords[node])
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
            from_coord = coords[from_id]
            to_coord = coords[to_id]
            distance = self.haversine(from_coord, to_coord)
            self.add_road(road_id, from_id, to_id, is_one_way=False, weight=distance)

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

    def get_dynamic_weight_and_penalty(self, road, intersections):
        # Base distance in km
        base_distance = road.weight
        # Congestion penalty: sum densities of all lanes at from_intersection in the road's direction (0.5 min per vehicle)
        from_intersection = intersections[road.from_intersection]
        density_penalty = 0
        for lane in from_intersection.lanes:
            density_penalty += lane.traffic_density * 0.5  # 0.5 min per vehicle
        # Signal penalty: if signal is red for this road's direction, add wait time (in minutes)
        signal_penalty = 0
        signal_state = from_intersection.signal_state
        if signal_state and road.id not in signal_state.green_lanes:
            signal_penalty += (signal_state.duration / 2)  # average wait in seconds
            signal_penalty /= 60  # convert to minutes
        total_penalty = density_penalty + signal_penalty
        return base_distance, total_penalty

    def shortest_path_dynamic(self, start_id, end_id, intersections):
        import heapq
        queue = [(0, 0, start_id, [])]  # (base_distance_sum, penalty_sum, node, path)
        visited = set()
        while queue:
            (dist_sum, penalty_sum, node, path) = heapq.heappop(queue)
            if node in visited:
                continue
            path = path + [node]
            if node == end_id:
                return path, dist_sum, penalty_sum
            visited.add(node)
            for neighbor in self.adjacency.get(node, []):
                road = next((r for r in self.roads.values() if ((r.from_intersection == node and r.to_intersection == neighbor) or (not r.is_one_way and r.from_intersection == neighbor and r.to_intersection == node))), None)
                if road:
                    base_dist, penalty = self.get_dynamic_weight_and_penalty(road, intersections)
                    heapq.heappush(queue, (dist_sum + base_dist, penalty_sum + penalty, neighbor, path))
        return None, float('inf'), float('inf') 