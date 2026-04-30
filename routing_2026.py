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
import pyproj
from shapely.geometry import Point, LineString
from shapely.strtree import STRtree


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

    def find_nearest_node(self, x, y):
        """
        Find the nearest node to a given coordinate using scipy KDTree.


        Args:
            x: X coordinate of query point
            y: Y coordinate of query point
            k: Number of nearest nodes to find (default: 1)
        """
        node_ids = list(self.node_coords.keys())
        # Convert node_coords values to numpy array for KDTree
        coords_array = np.array(list(self.node_coords.values()))
        # Create KDTree for efficient nearest neighbor search
        tree = scipy.spatial.KDTree(coords_array)
        # Query k nearest neighbors to [x, y]
        distance, index = tree.query([x, y])
        # Get node_ids for all k nearest neighbors
        return (node_ids[index], float(distance))

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


def calculate_terrain_weight(elev1, elev2, edge_length,
                             threshold_degrees=10.0, slope_multiplier=1.0):
    """
    Calculate terrain-aware edge weight with slope-based penalties.

    Args:
        elev1: Elevation at first node (meters)
        elev2: Elevation at second node (meters)
        edge_length: Horizontal distance between nodes (meters)
        threshold_degrees: Slope threshold for penalty application (default: 10.0)
        slope_multiplier: Linear scaling factor (default: 1.0)

    Returns:
        Tuple (weight, slope_degrees, penalty_factor):
        - weight: Final edge weight (edge_length x penalty_factor)
        - slope_degrees: Calculated slope angle in degrees
        - penalty_factor: Applied penalty (1.0 to 100.0)

    """
    if not (math.isfinite(elev1) and math.isfinite(elev2)):
        return (edge_length, 0.0, 1.0)

    elevation_diff = abs(elev2 - elev1)
    slope_radians = math.atan(elevation_diff / edge_length)
    slope_degrees = math.degrees(slope_radians)

    # Apply penalty if slope exceeds threshold
    if slope_degrees <= threshold_degrees:
        penalty_factor = 1.0
    else:
        # Linear scaling formula
        penalty_factor = 1.0 + slope_multiplier * (slope_degrees - threshold_degrees)
        penalty_factor = min(100.0, penalty_factor)

    # Multiplicative weight calculation
    weight = edge_length * penalty_factor

    return (weight, slope_degrees, penalty_factor)


def split_bbox(bbox, grid_size=(2,2)):
    """
    Split bounding box into rectangular grid tiles.

    Splits a large bounding box into smaller tiles to avoid OSM API
    timeout limits when querying over large areas. Used by tiled
    water feature queries.

    Args:
        bbox: Tuple (west, south, east, north) in EPSG:4326 (lat/lon)
        grid_size: Tuple (rows, cols) for grid dimensions. Default (2,2)
                   creates 4 tiles (NW, NE, SW, SE quadrants).

    Returns:
        List of bbox tuples (west, south, east, north) for each tile,
        ordered top-left to bottom-right (row-major order).

    Example:
        For bbox (7.0, 60.0, 9.0, 61.0) with grid_size=(2,2):
        Returns [(7.0, 60.5, 8.0, 61.0),   # NW tile
                (8.0, 60.5, 9.0, 61.0),   # NE tile
                (7.0, 60.0, 8.0, 60.5),   # SW tile
                (8.0, 60.0, 9.0, 60.5)]   # SE tile
    """
    west, south, east, north = bbox
    rows, cols = grid_size

    # Validate grid_size to prevent division by zero
    if rows <= 0 or cols <= 0:
        raise ValueError(f"grid_size must have positive values, got ({rows}, {cols})")

    tile_width = (east - west) / cols
    tile_height = (north - south) / rows

    tiles = []
    for row in range(rows):
        for col in range(cols):
            tile_west = west + col * tile_width
            tile_east = west + (col + 1) * tile_width
            tile_south = south + (rows - 1 - row) * tile_height
            tile_north = south + (rows - row) * tile_height
            tiles.append((tile_west, tile_south, tile_east, tile_north))

    return tiles


def load_water_features(bbox, target_epsg, timeout=30):
    """
    Query and project water features for water penalty routing.

    Implements per:
    - Query OpenStreetMap water features via osmnx.features_from_bbox()
    - Query at route planning time (dynamic, not pre-download)
    - Separate queries for lakes (polygons) and rivers (linestrings)
    - Project from EPSG:4326 to target CRS for intersection with terrain mesh

    Args:
        bbox: Tuple (west, south, east, north) in EPSG:4326 (lat/lon)
        target_epsg: Target EPSG code (e.g., 25832 for UTM 32V)
        timeout: HTTP request timeout in seconds for osmnx Overpass API calls.
                 If timeout is exceeded, the function returns (None, None) allowing
                 routing to continue without water penalties. Default: 30 seconds.
                 Note: This is per-request timeout (lakes and rivers queried separately).

    Returns:
        Tuple (lakes_gdf, rivers_gdf) - GeoDataFrames projected to target CRS
        Returns (None, None) on network timeout or error with warning logged
    """
    west, south, east, north = bbox

    # Validate bbox format
    assert west < east, f"bbox west ({west}) must be less than east ({east})"
    assert south < north, f"bbox south ({south}) must be less than north ({north})"

    try:
        # Configure timeout for osmnx API requests (global setting in osmnx 2.1.0)
        ox.settings.requests_timeout = timeout

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


def load_water_features_tiled(bbox, target_epsg, grid_size=(2,2), timeout=30):
    """
    Query and project water features in multiple tiles to avoid OSM API timeouts.

    Splits large bounding box into grid tiles, queries each tile separately,
    and merges results. Uses 2x2 grid by default (4 tiles).

    Args:
        bbox: Tuple (west, south, east, north) in EPSG:4326 (lat/lon)
        target_epsg: Target EPSG code (e.g., 25832 for UTM 32V)
        grid_size: Tuple (rows, cols) for grid dimensions. Default (2,2)
        timeout: HTTP request timeout per tile in seconds

    Returns:
        Tuple (lakes_gdf, rivers_gdf) - Merged GeoDataFrames projected to target CRS
        Returns (None, None) if any tile query fails (timeout or error)
    """
    tiles = split_bbox(bbox, grid_size)
    total_tiles = len(tiles)

    all_lakes = []
    all_rivers = []

    for i, tile_bbox in enumerate(tiles, start=1):
        print(f"Querying water features for tile {i}/{total_tiles}...")

        lakes_gdf, rivers_gdf = load_water_features(tile_bbox, target_epsg, timeout)

        if lakes_gdf is None or rivers_gdf is None:
            print(f"Warning: Tile {i} query failed, aborting entire query")
            return (None, None)

        # Collect results for merging
        if len(lakes_gdf) > 0:
            all_lakes.append(lakes_gdf)
        if len(rivers_gdf) > 0:
            all_rivers.append(rivers_gdf)

    # Merge all tile results
    if all_lakes:
        merged_lakes = gpd.pd.concat(all_lakes, ignore_index=True)
    else:
        merged_lakes = gpd.GeoDataFrame()

    if all_rivers:
        merged_rivers = gpd.pd.concat(all_rivers, ignore_index=True)
    else:
        merged_rivers = gpd.GeoDataFrame()

    print(f"Query complete: {len(merged_lakes)} lakes, {len(merged_rivers)} rivers found")

    return (merged_lakes, merged_rivers)


def build_spatial_indexes(lakes_gdf, rivers_gdf):
    """
    Build spatial indexes for lakes and rivers using shapely.strtree.STRtree.
    """
    if lakes_gdf is not None and len(lakes_gdf) > 0:
        lake_tree = STRtree(lakes_gdf.geometry.values)
    else:
        lake_tree = None
        lakes_gdf = None

    if rivers_gdf is not None and len(rivers_gdf) > 0:
        river_tree = STRtree(rivers_gdf.geometry.values)
    else:
        river_tree = None
        rivers_gdf = None

    return (lake_tree, lakes_gdf, river_tree, rivers_gdf)


def detect_water_crossing(edge_start, edge_end, lake_tree, river_tree,
                         lakes_gdf=None, rivers_gdf=None,
                         lake_penalty=30.0, river_penalty=15.0, fjord_penalty=10000.0):
    """
    Detect water body crossing for terrain edge using spatial index queries.

    Args:
        edge_start: Tuple (x, y) of edge start point in mesh CRS
        edge_end: Tuple (x, y) of edge end point in mesh CRS
        lake_tree: STRtree spatial index for lake polygons (from build_spatial_indexes)
        river_tree: STRtree spatial index for river linestrings (from build_spatial_indexes)
        lakes_gdf: GeoDataFrame of lake polygons (optional, for fjord name lookup only)
        rivers_gdf: GeoDataFrame of river linestrings (optional, reserved for future use)
        lake_penalty: Penalty factor for lake crossings (default: 30.0)
        river_penalty: Penalty factor for river crossings (default: 15.0)
        fjord_penalty: Penalty factor for fjord crossings (default: 150.0)

    Returns:
        Tuple (water_type, penalty_factor) - (None, 1.0) if no crossing
        water_type: String ('lake', 'fjord', 'river', or None)
        penalty_factor: Float (30.0 for lakes, 150.0 for fjords, 15.0 for rivers, 1.0 for none)

    """
    if lake_tree is None and river_tree is None:
        return (None, 1.0)

    x1, y1 = edge_start
    x2, y2 = edge_end

    midpoint = Point(((x1 + x2) / 2, (y1 + y2) / 2))

# Check lakes using spatial index (O(log m) instead of O(m))
    if lake_tree is not None and lakes_gdf is not None:
        lake_geometries = lakes_gdf.geometry.values
        nearby_indices = lake_tree.query(midpoint)
        for idx in nearby_indices:
            lake_geom = lake_geometries[idx]
            if midpoint.within(lake_geom):
                row = lakes_gdf.iloc[idx]
                name = row['name'] if 'name' in lakes_gdf.columns else ''
                if name and 'fjord' in str(name).lower():
                    return ('fjord', fjord_penalty)
                return ('lake', lake_penalty)

    if river_tree is not None and rivers_gdf is not None:
        river_geometries = rivers_gdf.geometry.values
        edge_line = LineString([edge_start, edge_end])
        nearby_indices = river_tree.query(edge_line)
        for idx in nearby_indices:
            river_geom = river_geometries[idx]
            # Check for line-intersection
            if edge_line.intersects(river_geom):
                return ('river', river_penalty)

    # No water crossing detected
    return (None, 1.0)


def terrain_mesh_from_raster(raster, mesh_spacing=100, enable_water_queries=False):
    """
    Generate a regular mesh node grid from terrain raster.

    Args:
        raster: Raster instance with DTM data
        mesh_spacing: Distance between mesh nodes (meters in projection)
        enable_water_queries: If False, skip water feature queries for testing/faster execution

    Returns:
        RoutingNetwork with regular mesh topology and water-aware edge weights
    """
    routing_net = RoutingNetwork()
    routing_net.epsg = raster.epsg

    # Track node elevations for slope calculation
    node_elevations = {}  # node_id -> elevation in meters

    # Get raster extent and pixel size from world file
    world_file = raster._world_file
    if world_file is None or len(world_file) < 6:
        raise ValueError("Raster has no valid world file")
    pixel_width = world_file[0]
    pixel_height = world_file[3]  # Negative

    # Validate pixel dimensions to prevent division by zero
    if pixel_width == 0:
        raise ValueError("World file pixel_width is zero (division by zero)")
    if pixel_height == 0:
        raise ValueError("World file pixel_height is zero (division by zero)")

    # Calculate pixel spacing for mesh nodes
    # Use math.ceil to ensure spacing doesn't become too small
    pixel_spacing = math.ceil(mesh_spacing / abs(pixel_width))

    # First pass: create all nodes without edges
    # This allows us to collect all node coordinates for water feature queries
    node_id_counter = 0
    rows, cols = raster.shape

    # Calculate number of nodes per row
    nodes_per_row = 0
    for col in range(0, cols, pixel_spacing):
        nodes_per_row += 1

    # First loop collect node coordinates and elevation data
    for row in range(0, rows, pixel_spacing):
        for col in range(0, cols, pixel_spacing):
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

            node_id_counter += 1

    # Extract bounding box for water feature query
    x_coords = [coord[0] for coord in routing_net.node_coords.values()]
    y_coords = [coord[1] for coord in routing_net.node_coords.values()]
    bbox_local = (min(x_coords), min(y_coords), max(x_coords), max(y_coords))

    # Query water features only if enabled
    if enable_water_queries:
        print("Water queries enabled, querying OSM water features using tiled approach (2x2 grid)...")
        # Convert bbox from local CRS to EPSG:4326 for osmnx query
        # Use pyproj transformer for CRS conversion
        try:
            transformer = pyproj.Transformer.from_crs(f"EPSG:{raster.epsg}", "EPSG:4326", always_xy=True)
            west, south = transformer.transform(bbox_local[0], bbox_local[1])
            east, north = transformer.transform(bbox_local[2], bbox_local[3])
            bbox_osm = (west, south, east, north)

            # Query water features using tiled approach to avoid API timeouts
            lakes_gdf, rivers_gdf = load_water_features_tiled(bbox_osm, raster.epsg)

            # Build spatial indexes for efficient water crossing detection
            # This reduces water penalty calculation from O(nxm) to O(n log m)
            lake_tree, lakes_gdf_idx, river_tree, rivers_gdf_idx = build_spatial_indexes(lakes_gdf, rivers_gdf)
        except pyproj.exceptions.CRSError as e:
            # CRS transformation error - more specific handling
            print(f"Warning: CRS transformation failed: {e}")
            print("Routing without water penalties due to coordinate system issues")
            lakes_gdf, rivers_gdf = None, None
            lake_tree, river_tree = None, None
            lakes_gdf_idx, rivers_gdf_idx = None, None
        except Exception as e:
            # Other errors (network timeout, OSM API error, etc.)
            print(f"Warning: Tiled water feature query failed ({type(e).__name__}: {e})")
            print("Routing without water penalties")
            lakes_gdf, rivers_gdf = None, None
            lake_tree, river_tree = None, None
            lakes_gdf_idx, rivers_gdf_idx = None, None
    else:
        print("Info: Water queries disabled, routing without water penalties")
        lakes_gdf, rivers_gdf = None, None
        lake_tree, river_tree = None, None
        lakes_gdf_idx, rivers_gdf_idx = None, None

    def add_mesh_edge(node_id, neighbor_id):
        elev1 = node_elevations[node_id]
        elev2 = node_elevations[neighbor_id]

        if elev1 is not None and elev2 is not None:
            terrain_weight, slope, terrain_penalty = calculate_terrain_weight(
                elev1, elev2, mesh_spacing
            )
        else:
            terrain_weight = mesh_spacing
            slope = 0.0
            terrain_penalty = 1.0

        edge_start = routing_net.node_coords[node_id]
        edge_end = routing_net.node_coords[neighbor_id]
        water_type, water_penalty_factor = detect_water_crossing(
            edge_start, edge_end, lake_tree, river_tree,
            lakes_gdf=lakes_gdf_idx, rivers_gdf=rivers_gdf_idx
        )

        final_weight = terrain_weight * water_penalty_factor
        combined_penalty = terrain_penalty * water_penalty_factor

        routing_net.add_edge(
            node_id, neighbor_id, final_weight,
            length=mesh_spacing,
            slope_angle=slope,
            terrain_penalty_factor=terrain_penalty,
            water_type=water_type,
            water_penalty_factor=water_penalty_factor,
            penalty_factor=combined_penalty,
            source='terrain_water'
        )

    # Second pass: create edges with terrain and water penalties
    node_id_counter = 0
    for row in range(0, rows, pixel_spacing):
        col_index = 0
        for col in range(0, cols, pixel_spacing):
            if col_index > 0:
                add_mesh_edge(node_id_counter, node_id_counter - 1)

            if row > 0:
                add_mesh_edge(node_id_counter, node_id_counter - nodes_per_row)

            node_id_counter += 1
            col_index += 1

    return routing_net
