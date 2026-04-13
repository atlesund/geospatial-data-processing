"""
Routing network module for geospatial pathfinding.

Provides RoutingNetwork class wrapper around networkx.Graph with
geospatial methods for node snapping, shortest path computation,
and coordinate system tracking.
"""

import networkx as nx
import scipy.spatial
import numpy as np
import osmnx as ox
from vector_2026 import Vector
from raster_2026 import Raster


class RoutingNetwork:
    """
    Wrapper around networkx.Graph for geospatial routing.

    Stores node coordinates as (x, y) tuples in node_coords dict,
    edge weights in edge data for pathfinding, and EPSG code for
    coordinate reference system tracking.
    """

    def __init__(self):
        """
        Initialize empty routing network.

        Creates:
            - self.graph: Empty networkx.Graph instance
            - self.node_coords: Empty dict mapping node_id -> (x, y)
            - self._epsg: None (unspecified coordinate system)
        """
        self.graph = nx.Graph()
        self.node_coords = {}  # node_id -> (x, y)
        self._epsg = None  # EPSG code for coordinate system

    def add_node(self, node_id, x, y):
        """
        Add a georeferenced node to the network.

        Args:
            node_id: Unique identifier for the node (can be any hashable type)
            x: X coordinate in the network's EPSG coordinate system
            y: Y coordinate in the network's EPSG coordinate system

        Returns:
            None
        """
        # Add node to the graph
        self.graph.add_node(node_id)

        # Store coordinates in node_coords dict
        self.node_coords[node_id] = (x, y)

    def add_edge(self, u, v, weight, **attrs):
        """
        Add a weighted bidirectional edge between two nodes.

        Args:
            u: Source node ID
            v: Target node ID
            weight: Edge weight (typically distance in meters)
            **attrs: Additional edge attributes (e.g., length, trail_id)

        Returns:
            None
        """
        # Add edge with weight and additional attributes
        # NetworkX Graph is undirected, so edge (u,v) = edge (v,u)
        self.graph.add_edge(u, v, weight=weight, **attrs)

    def shortest_path(self, source, target):
        """
        Compute shortest path between two nodes using Dijkstra algorithm.

        Args:
            source: Starting node ID
            target: Ending node ID

        Returns:
            List of node IDs forming the path from source to target.

        Raises:
            networkx.exception.NetworkXNoPath: If no path exists between nodes
        """
        # Use Dijkstra algorithm with 'weight' attribute
        path = nx.dijkstra_path(self.graph, source, target, weight='weight')
        return path

    def find_nearest_node(self, x, y, k=1):
        """
        Find k nearest nodes to a given point using scipy KDTree.

        Args:
            x: X coordinate of query point
            y: Y coordinate of query point
            k: Number of nearest nodes to find (default: 1)

        Returns:
            Tuple (node_id, distance) for the nearest node.
            If graph is empty with no nodes, returns (None, float('inf'))
        """
        # Handle empty graph case
        if len(self.node_coords) == 0:
            return (None, float('inf'))

        # Convert node_coords values to numpy array for KDTree
        coords_array = np.array(list(self.node_coords.values()))

        # Create KDTree for efficient nearest neighbor search
        tree = scipy.spatial.KDTree(coords_array)

        # Query k nearest neighbors to [x, y]
        distances, indices = tree.query([x, y], k=k)

        # When k=1, scipy returns scalars; when k>1, returns arrays
        # Handle both cases by converting to list
        if k == 1:
            indices = [indices] if not isinstance(indices, (list, np.ndarray)) else indices
            distances = [distances] if not isinstance(distances, (list, np.ndarray)) else distances

        # Get node_id for nearest neighbor (index 0)
        node_id = list(self.node_coords.keys())[indices[0]]
        distance = distances[0]

        return (node_id, distance)

    def _get_epsg(self):
        """
        Get the EPSG code for the coordinate reference system.

        Returns:
            None if unspecified, or integer EPSG code (e.g., 25832 for UTM 32V)
        """
        return self._epsg

    def _set_epsg(self, epsg_code):
        """
        Set the EPSG code with validation.

        Args:
            epsg_code: None (unspecified) or integer EPSG code

        Raises:
            ValueError: If epsg_code is not None or not an integer
        """
        if epsg_code is not None and not isinstance(epsg_code, int):
            raise ValueError(f"EPSG code must be None or int, got {type(epsg_code)}")
        self._epsg = epsg_code

    epsg = property(fget=_get_epsg, fset=_set_epsg)


def load_osmnx_trails(bbox, epsg=25832):
    """
    Load hiking trails from OpenStreetMap within bounding box.

    Extracts hiking trails (path, footway, track, steps) from OpenStreetMap
    using osmnx library, projects to metric coordinate system, and returns
    as RoutingNetwork instance.

    Args:
        bbox: Tuple (south, west, north, east) in decimal degrees (lat, lon)
        epsg: Target EPSG for metric coordinate system (UTM 32V = 25832)

    Returns:
        RoutingNetwork with OSM trails as graph

    OSM highway types for hiking:
        - 'path'           # Generic path
        - 'footway'        # Pedestrian path
        - 'track'          # Agricultural/forestry road
        - 'steps'          # Stairs
    """
    # Create osmnx graph filtered for hiking trails
    # bbox input format: (south, west, north, east)
    # osmnx expects: (west, south, east, north)
    custom_filter = '["highway"~"path|footway|track|steps"]'
    G_osm = ox.graph_from_bbox(
        (bbox[1], bbox[0], bbox[3], bbox[2]),  # west, south, east, north
        network_type='walk',
        custom_filter=custom_filter
    )

    # Project to metric coordinate system
    G_osm = ox.project_graph(G_osm, to_crs=f"EPSG:{epsg}")

    # Convert to RoutingNetwork wrapper
    routing_net = RoutingNetwork()
    routing_net.epsg = epsg

    # Extract nodes with coordinates
    for node_id, node_data in G_osm.nodes(data=True):
        x = node_data['x']
        y = node_data['y']
        routing_net.add_node(node_id, x, y)

    # Extract edges with weights
    for u, v, edge_data in G_osm.edges(data=True):
        weight = edge_data.get('length', 1.0)  # OSM provides length
        routing_net.add_edge(u, v, weight,
                           length=weight,
                           source='osm')

    return routing_net


def terrain_mesh_from_raster(raster, mesh_spacing=100, bbox=None):
    """
    Generate a regular mesh node grid from terrain raster.

    For Phase 2: Creates placeholder mesh structure.
    Phase 3: Will add terrain-based edge weights.
    Phase 4: Will add water body penalties.

    Args:
        raster: Raster instance with DTM data
        mesh_spacing: Distance between mesh nodes (meters in projection)
        bbox: Optional bounding box (x_min, y_min, x_max, y_max)

    Returns:
        RoutingNetwork with regular mesh topology
    """
    routing_net = RoutingNetwork()
    routing_net.epsg = raster.epsg

    # Get raster extent and pixel size from world file
    world_file = raster._world_file
    pixel_width = world_file[0]
    pixel_height = world_file[3]  # Negative

    # Calculate pixel spacing for mesh nodes
    pixel_spacing = mesh_spacing / abs(pixel_width)

    # Generate grid of nodes
    node_id_counter = 0
    rows, cols = raster.shape

    for row in range(0, rows, int(pixel_spacing)):
        for col in range(0, cols, int(pixel_spacing)):
            # Convert pixel to world coordinates using world file
            x = world_file[4] + col * pixel_width + row * world_file[1]
            y = world_file[5] + row * pixel_height + col * world_file[2]

            # Add node to routing network
            routing_net.add_node(node_id_counter, x, y)

            # Connect to left neighbor
            if col > 0:
                left_id = node_id_counter - int(pixel_spacing)
                edge_weight = mesh_spacing
                routing_net.add_edge(node_id_counter, left_id, edge_weight,
                                   length=edge_weight,
                                   source='terrain')

            # Connect to top neighbor
            if row > 0:
                top_id = node_id_counter - int(cols / pixel_spacing)
                edge_weight = mesh_spacing
                routing_net.add_edge(node_id_counter, top_id, edge_weight,
                                   length=edge_weight,
                                   source='terrain')

            node_id_counter += 1

    return routing_net

def polylines_to_graph(trails_vector, snap_distance=50):
    """
    Convert trail polylines to routing graph with node snapping.

    Args:
        trails_vector: Vector instance with POLYLINE geometry
        snap_distance: Distance in map units to snap endpoint nodes

    Returns:
        RoutingNetwork instance with graph topology
    """
    routing_net = RoutingNetwork()
    routing_net.epsg = trails_vector.epsg

    node_id_counter = 0

    for i, polyline in enumerate(trails_vector.coordinates):
        # Get line start and end points
        start_pt = polyline[0]
        end_pt = polyline[-1]

        # Snap start point using KDTree for efficiency
        start_node = _snap_or_create_node(routing_net, start_pt, snap_distance, node_id_counter)
        if start_node == node_id_counter:
            node_id_counter += 1

        # Snap end point using KDTree
        end_node = _snap_or_create_node(routing_net, end_pt, snap_distance, node_id_counter)
        if end_node == node_id_counter:
            node_id_counter += 1

        # Calculate edge weight (Euclidean distance)
        edge_length = _calculate_polyline_length(polyline)

        # Add bidirectional edge (hiking can go either way)
        routing_net.add_edge(start_node, end_node,
                           weight=edge_length,
                           length=edge_length,
                           trail_id=i)

    return routing_net


def _snap_or_create_node(routing_net, point, snap_distance, next_id):
    """
    Snap point to existing node using KDTree or create new node.

    Args:
        routing_net: RoutingNetwork instance
        point: (x, y) tuple representing point location
        snap_distance: Maximum distance to snap to existing node
        next_id: Node ID to use if creating new node

    Returns:
        Node ID (either existing snapped node or newly created node)
    """
    x, y = point

    if not routing_net.node_coords:
        # Empty graph, create first node
        routing_net.add_node(next_id, x, y)
        return next_id

    # Use KDTree for efficient nearest neighbor search
    coords_array = np.array(list(routing_net.node_coords.values()))
    tree = scipy.spatial.KDTree(coords_array)
    dist, idx = tree.query([x, y], k=1)

    if dist < snap_distance:
        # Within snap distance, use existing node
        node_ids = list(routing_net.node_coords.keys())
        return node_ids[idx]

    # Outside snap distance, create new node
    routing_net.add_node(next_id, x, y)
    return next_id


def _calculate_polyline_length(polyline):
    """
    Calculate total length of polyline segments using Euclidean distance.

    Args:
        polyline: List of (x, y) coordinate tuples

    Returns:
        Total length of all segments
    """
    total_length = 0.0
    for i in range(len(polyline) - 1):
        x1, y1 = polyline[i]
        x2, y2 = polyline[i + 1]
        segment_length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        total_length += segment_length
    return total_length
