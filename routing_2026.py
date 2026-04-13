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
import math
import geopandas as gpd
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


def calculate_terrain_weight(elev1, elev2, edge_length,
                            threshold_degrees=20.0, slope_multiplier=0.2):
    """
    Calculate terrain-aware edge weight with slope-based penalties.

    Implements terrain routing per locked decisions D-01 through D-06:
    - D-01/D-02: Slope = atan(elevation_diff / edge_length), converted to degrees
    - D-03/D-04: 20° threshold - penalty only applies when slope > 20°
    - D-05: Linear scaling: penalty_factor = 1.0 + k*(slope - threshold)
    - D-06: Multiplicative weight: final_weight = edge_length × penalty_factor

    Args:
        elev1: Elevation at first node (meters)
        elev2: Elevation at second node (meters)
        edge_length: Horizontal distance between nodes (meters)
        threshold_degrees: Slope threshold for penalty application (default: 20.0)
        slope_multiplier: Linear scaling factor (default: 0.2)

    Returns:
        Tuple (weight, slope_degrees, penalty_factor):
        - weight: Final edge weight (edge_length × penalty_factor)
        - slope_degrees: Calculated slope angle in degrees
        - penalty_factor: Applied penalty (1.0 to 100.0)

    Raises:
        ValueError: If edge_length <= 0 or elevation values are invalid
    """
    # Guard clause: edge_length == 0 (T-3-05)
    if edge_length == 0:
        return (0.0, 0.0, 1.0)

    # Validate edge_length > 0 (T-3-08)
    if edge_length < 0:
        raise ValueError("edge_length must be positive")

    # Validate elevation values are finite (T-3-06)
    if not (math.isfinite(elev1) and math.isfinite(elev2)):
        raise ValueError("elevation values must be finite numbers")

    # Calculate elevation difference (D-01)
    elevation_diff = abs(elev2 - elev1)

    # Calculate slope angle in degrees (D-02)
    slope_radians = math.atan(elevation_diff / edge_length)
    slope_degrees = math.degrees(slope_radians)

    # Apply penalty if slope exceeds threshold (D-03/D-04)
    if slope_degrees <= threshold_degrees:
        penalty_factor = 1.0
    else:
        # Linear scaling formula (D-05)
        penalty_factor = 1.0 + slope_multiplier * (slope_degrees - threshold_degrees)

        # Clamp penalty factor to max 100 to prevent DoS (T-3-07)
        penalty_factor = min(100.0, penalty_factor)

    # Multiplicative weight calculation (D-06)
    weight = edge_length * penalty_factor

    return (weight, slope_degrees, penalty_factor)


def load_water_features(bbox, target_epsg, timeout=30):
    """
    Query and project water features for water penalty routing.

    Implements per D-01/D-02:
    - Query OpenStreetMap water features via osmnx.features_from_bbox()
    - Query at route planning time (dynamic, not pre-download)
    - Separate queries for lakes (polygons) and rivers (linestrings)
    - Project from EPSG:4326 to target CRS for intersection with terrain mesh

    Args:
        bbox: Tuple (west, south, east, north) in EPSG:4326 (lat/lon)
        target_epsg: Target EPSG code (e.g., 25832 for UTM 32V)
        timeout: Timeout for osmnx query in seconds (default: 30)

    Returns:
        Tuple (lakes_gdf, rivers_gdf) - GeoDataFrames projected to target CRS
        Returns (None, None) on network failure with warning logged
    """
    west, south, east, north = bbox

    # Validate bbox format
    assert west < east, f"bbox west ({west}) must be less than east ({east})"
    assert south < north, f"bbox south ({south}) must be less than north ({north})"

    try:
        # Query lakes with tags: {'natural': 'water'}
        lakes = ox.features_from_bbox(
            (west, south, east, north),
            tags={'natural': 'water'}
        )

        # Query rivers with tags: {'waterway': ['river', 'stream', 'canal']}
        rivers = ox.features_from_bbox(
            (west, south, east, north),
            tags={'waterway': ['river', 'stream', 'canal']}
        )

        # Project to target CRS
        lakes_gdf = lakes.to_crs(f"EPSG:{target_epsg}")
        rivers_gdf = rivers.to_crs(f"EPSG:{target_epsg}")

        return (lakes_gdf, rivers_gdf)

    except Exception as e:
        # Graceful fallback on network failure
        print(f"Warning: Failed to query water features: {e}")
        print("Continuing without water penalty mode")
        return (None, None)


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

    # Track node elevations for slope calculation per D-01/D-02
    node_elevations = {}  # node_id -> elevation in meters

    # Get raster extent and pixel size from world file
    world_file = raster._world_file
    pixel_width = world_file[0]
    pixel_height = world_file[3]  # Negative

    # Calculate pixel spacing for mesh nodes
    pixel_spacing = mesh_spacing / abs(pixel_width)

    # Generate grid of nodes
    node_id_counter = 0
    rows, cols = raster.shape

    # Calculate number of nodes per row
    nodes_per_row = 0
    for col in range(0, cols, int(pixel_spacing)):
        nodes_per_row += 1

    for row in range(0, rows, int(pixel_spacing)):
        col_index = 0
        for col in range(0, cols, int(pixel_spacing)):
            # Convert pixel to world coordinates using world file
            x = world_file[4] + col * pixel_width + row * world_file[1]
            y = world_file[5] + row * pixel_height + col * world_file[2]

            # Retrieve elevation for slope calculation
            world_x = x
            world_y = y
            elevation = raster.get_elevation_at(world_x, world_y)
            node_elevations[node_id_counter] = elevation

            # Add node to routing network
            routing_net.add_node(node_id_counter, x, y)

            # Connect to left neighbor (same row, previous column) with terrain penalties
            if col_index > 0:
                left_id = node_id_counter - 1
                elev1 = node_elevations[node_id_counter]
                elev2 = node_elevations[left_id]

                # Calculate terrain-aware weight per D-01/D-02/D-03/D-04/D-05/D-06
                if elev1 is not None and elev2 is not None:
                    terrain_weight, slope, penalty = calculate_terrain_weight(
                        elev1, elev2, mesh_spacing
                    )
                else:
                    # Fallback to uniform weight if elevation unavailable
                    terrain_weight = mesh_spacing
                    slope = 0.0
                    penalty = 1.0

                routing_net.add_edge(node_id_counter, left_id, terrain_weight,
                                   length=mesh_spacing,
                                   slope_angle=slope,
                                   penalty_factor=penalty,
                                   source='terrain')

            # Connect to top neighbor (previous row, same column) with terrain penalties
            if row > 0:
                top_id = node_id_counter - nodes_per_row
                elev1 = node_elevations[node_id_counter]
                elev2 = node_elevations[top_id]

                # Calculate terrain-aware weight per D-01/D-02/D-03/D-04/D-05/D-06
                if elev1 is not None and elev2 is not None:
                    terrain_weight, slope, penalty = calculate_terrain_weight(
                        elev1, elev2, mesh_spacing
                    )
                else:
                    # Fallback to uniform weight if elevation unavailable
                    terrain_weight = mesh_spacing
                    slope = 0.0
                    penalty = 1.0

                routing_net.add_edge(node_id_counter, top_id, terrain_weight,
                                   length=mesh_spacing,
                                   slope_angle=slope,
                                   penalty_factor=penalty,
                                   source='terrain')

            node_id_counter += 1
            col_index += 1

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


def merge_networks(networks, prefix_mapping=None):
    """
    Merge multiple routing networks into unified graph.

    Args:
        networks: List of RoutingNetwork instances to merge
        prefix_mapping: Optional list of prefixes for node IDs.
                       If None, uses ['trail_', 'osm_', 'mesh_', ...]

    Returns:
        Unified RoutingNetwork with all merged nodes and edges

    Note: All networks must have the same EPSG code for valid merge.
          Raises ValueError if EPSG codes differ.
    """
    if not networks:
        return None

    # Validate EPSG codes match
    epsg_values = set(net.epsg for net in networks if net.epsg is not None)
    if len(epsg_values) > 1:
        raise ValueError(f"Cannot merge networks with different EPSG codes: {epsg_values}")

    # Generate prefixes if not provided
    if prefix_mapping is None:
        prefix_mapping = [f'n{i}_' for i in range(len(networks))]

    # Create merged network
    merged_net = RoutingNetwork()
    if len(networks) > 0 and networks[0].epsg is not None:
        merged_net.epsg = networks[0].epsg

    # Merge all networks
    for network, prefix in zip(networks, prefix_mapping):
        # Add nodes with prefixed IDs
        for node_id, coord in network.node_coords.items():
            prefixed_id = f"{prefix}{node_id}"
            merged_net.add_node(prefixed_id, coord[0], coord[1])

        # Add edges with prefixed node IDs
        for u, v, data in network.graph.edges(data=True):
            prefixed_u = f"{prefix}{u}"
            prefixed_v = f"{prefix}{v}"
            weight = data.get('weight', 1.0)
            attrs = {k: v for k, v in data.items() if k != 'weight'}
            merged_net.add_edge(prefixed_u, prefixed_v, weight, **attrs)

    return merged_net
