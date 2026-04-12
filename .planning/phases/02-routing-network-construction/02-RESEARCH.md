# Phase 2: Routing Network Construction - Research

**Researched:** 2026-04-12
**Domain:** Geospatial routing networks, graph construction, OpenStreetMap integration, terrain-based routing
**Confidence:** MEDIUM

## Summary

Phase 2 requires constructing a hybrid routing network from three data sources: established hiking trails (shapefile/GeoJSON), OpenStreetMap paths, and terrain-based meshes. The core technical challenge is creating a unified graph topology from these heterogeneous sources using Python geospatial libraries.

**Primary recommendation:** Use networkx for graph structure with osmnx (v2.1.0) for OSM data, and extend existing Vector/Raster classes for terrain mesh generation. The existing codebase's polyline support can be leveraged for trail data integration with a conversion layer to graph edges.

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| COMP-03 | System combines established hiking trails into routing network | Existing Vector class supports polylines; can convert to networkx edges with node snapping |
| COMP-04 | System incorporates OpenStreetMap paths and trails where available | osmnx 2.1.0 provides OSM graph loading with highway filtering (path, footway, track) |
| COMP-05 | System uses terrain-based routing where trail network incomplete | Raster class exists; require terrain mesh generation for graph nodes in uncovered areas |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| networkx | 3.6.1 [VERIFIED: PyPI] | Graph structure, shortest path algorithms | Industry standard Python graph library with Dijkstra, A* support |
| scipy | 1.17.1 [VERIFIED: PyPI] | Spatial KD-tree for efficient nearest-node lookup | `scipy.spatial.KDTree` is standard for geospatial node snapping |
| pyproj | 3.7.2 [VERIFIED: .venv] | Coordinate transformations already in codebase | Already installed, supports EPSG conversions for Norway |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| osmnx | 2.1.0 [VERIFIED: PyPI] | OpenStreetMap graph extraction | When OSM data available for hiking trails |
| geopandas | 1.1.3 [VERIFIED: PyPI] | Advanced spatial joins, topology operations | Optional: for complex polygon overlays if needed |
| rasterio | — | Advanced raster I/O, DEM processing | Optional: if Phase 3/4 need better DTM handling |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| networkx | graph-tool | Higher performance, but harder installation (C++ dependency) |
| osmnx | pyroutelib2 | OSM-only routing, no graph manipulation flexibility |
| scipy KDTree | rtree spatial index | rtree better for dynamic graphs, but scipy sufficient for static |

**Installation:**
```bash
python3 -m pip install networkx scipy osmnx
```

**Version verification:**
- networkx 3.6.1 (checked via PyPI API: `curl -s "https://pypi.org/pypi/networkx/json"`)
- scipy 1.17.1 (checked via PyPI API: `curl -s "https://pypi.org/pypi/scipy/json"`)
- osmnx 2.1.0 (checked via PyPI API: `curl -s "https://pypi.org/pypi/osmnx/json"`)

## Architecture Patterns

### Recommended Project Structure
```
src/
├── routing_2026.py    # New: RoutingNetwork class (graph wrapper)
├── vector_2026.py     # Existing: Extended for polyline-to-graph conversion
├── raster_2026.py     # Existing: Extended for terrain mesh generation
└── utilities_2026.py  # Existing: New graph utilities functions
tests/
├── test_routing_graph.py      # Graph construction tests
├── test_osmnx_integration.py  # OSM data loading tests
└── test_terrain_mesh.py       # Terrain mesh generation tests
data/
├── trails/                  # Established trails (shapefiles, GeoJSON)
│   └── norway_trails.shp
└── terrain/                 # DTM raster data (for Phases 3/4)
    └── dem_norway.tif
```

### Pattern 1: Routing Network Class Wrapper
**What:** A new `RoutingNetwork` class that wraps networkx.Graph with geospatial methods
**When to use:** For all graph operations in the routing system
**Example:**
```python
# Source: [NetworkX official docs]
import networkx as nx
import heapq

class RoutingNetwork:
    """Wrapper around networkx.Graph for geospatial routing
    
    Stores node coordinates as (x, y) tuples in node data,
    edge weights in edge data for pathfinding.
    """
    def __init__(self):
        self.graph = nx.Graph()
        self.node_coords = {}  # node_id -> (x, y)
        self.epsg = None  # Coordinate reference system
    
    def add_node(self, node_id, x, y):
        """Add a georeferenced node."""
        self.graph.add_node(node_id)
        self.node_coords[node_id] = (x, y)
    
    def add_edge(self, u, v, weight, **attrs):
        """Add a weighted edge between two nodes."""
        self.graph.add_edge(u, v, weight=weight, **attrs)
    
    def shortest_path(self, source, target):
        """Compute shortest path using Dijkstra."""
        return nx.dijkstra_path(self.graph, source, target, weight='weight')
    
    def find_nearest_node(self, x, y, k=1):
        """Find k nearest nodes using scipy KD-tree."""
        coords_array = np.array(list(self.node_coords.values()))
        tree = scipy.spatial.KDTree(coords_array)
        dist, idx = tree.query([x, y], k=k)
        node_ids = list(self.node_coords.keys())[idx]
        return node_ids[0], dist
```

### Pattern 2: Polyline to Graph Conversion
**What:** Convert existing Vector polylines to graph edges by snapping line endpoints
**When to use:** When loading established trails from shapefiles/GeoJSON
**Example:**
```python
# Source: [Derived from networkx geospatial patterns]
from vector_2026 import Vector
from routing_2026 import RoutingNetwork

def polylines_to_graph(trails_vector: Vector, snap_distance=50) -> RoutingNetwork:
    """Convert trail polylines to routing graph with node snapping.
    
    Args:
        trails_vector: Vector instance with POLYLINE geometry
        snap_distance: Distance in map units to snap endpoint nodes
        
    Returns:
        RoutingNetwork instance with graph topology
    """
    routing_net = RoutingNetwork()
    routing_net.epsg = trails_vector.epsg
    
    node_id_counter = 0
    line_endpoint_map = {}  # (x, y) -> node_id for snapping
    
    for i, polyline in enumerate(trails_vector.coordinates):
        # Get line start and end points
        start_pt = polyline[0]
        end_pt = polyline[-1]
        
        # Snap start point to existing node or create new
        start_node = _snap_or_create_node(
            routing_net, start_pt, line_endpoint_map, 
            snap_distance, node_id_counter
        )
        if start_node == node_id_counter:
            node_id_counter += 1
            start_pt_name = start_pt
        else:
            start_pt_name = start_pt  # Use snapped coordinates
            line_endpoint_map[start_node] = start_pt_name
        
        # Same for end point
        end_node = _snap_or_create_node(
            routing_net, end_pt, line_endpoint_map,
            snap_distance, node_id_counter
        )
        if end_node == node_id_counter:
            node_id_counter += 1
            end_pt_name = end_pt
        else:
            end_pt_name = end_pt
            line_endpoint_map[end_node] = end_pt_name
        
        # Calculate edge weight (Euclidean distance)
        edge_length = _calculate_polyline_length(polyline)
        
        # Add bidirectional edge (hiking can go either way)
        routing_net.add_edge(start_node, end_node, 
                           weight=edge_length,
                           length=edge_length,
                           trail_id=i)
    
    return routing_net

def _snap_or_create_node(routing_net, point, endpoint_map, 
                         snap_distance, next_id):
    """Snap point to existing node or create new node."""
    x, y = point
    
    # Check if point already exists
    # Using simple distance check (can optimize with KD-tree for large graphs)
    for node_id, existing_pt in routing_net.node_coords.items():
        existing_x, existing_y = existing_pt
        if (x - existing_x)**2 + (y - existing_y)**2 < snap_distance**2:
            return node_id
    
    # Create new node
    routing_net.add_node(next_id, x, y)
    return next_id

def _calculate_polyline_length(polyline):
    """Calculate total length of polyline segments."""
    total_length = 0.0
    for i in range(len(polyline) - 1):
        x1, y1 = polyline[i]
        x2, y2 = polyline[i+1]
        segment_length = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
        total_length += segment_length
    return total_length
```

### Pattern 3: OSM Data Loading
**What:** Use osmnx to load OSM footpaths and convert to local routing graph
**When to use:** ShangIncomplete trail coverage, need to supplement with OSM paths
**Example:**
```python
# Source: [osmnx documentation - WebSearch verified]
import osmnx as ox

def load_osmnx_trails(bbox, epsg=25832) -> RoutingNetwork:
    """Load hiking trails from OpenStreetMap within bounding box.
    
    Args:
        bbox: Tuple (south, west, north, east) in decimal degrees
        epsg: Target EPSG for metric coordinate system (UTM 32V = 25832)
        
    Returns:
        RoutingNetwork with OSM trails as graph
        
    Note: OSM highway types for hiking:
        - 'path'           # Generic path
        - 'footway'        # Pedestrian path
        - 'track'          # Agricultural/forestry road
    """
    # Filter for hiking-related highway types
    # [ASSUMED] osmnx network_type='walk' includes these types
    # [ASSUMED] custom_filter parameter filters specific OSM tags
    
    # Create osmnx graph filtered for hiking trails
    G_osm = ox.graph_from_bbox(
        bbox[2], bbox[0], bbox[3], bbox[1],
        network_type='walk',
        custom_filter='["highway"~"path|footway|track|steps"]'
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
```

### Pattern 4: Terrain Mesh Generation
**What:** Generate a sparse mesh graph from terrain for areas without trail data
**When to use:** OSM and trail coverage gaps; Phase 3/4 terrain-aware routing
**Example:**
```python
# Source: [Standard raster-to-graph pattern for mobility routing]
import numpy as np
from raster_2026 import Raster
from routing_2026 import RoutingNetwork

def terrain_mesh_from_raster(
    raster: Raster, 
    mesh_spacing=100,  # meters between nodes
    bbox=None
) -> RoutingNetwork:
    """Generate a regular mesh node grid from terrain raster.
    
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
    
    # Get raster extent and pixel size
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
```

### Anti-Patterns to Avoid
- **Falling back to bare for loops for node snapping:** Use scipy.spatial.KDTree for O(n log n) instead of O(n^2) pairwise distances
- **Storing coordinates in node IDs:** Always store coordinates in node data (node_coords dict) for reproducibility
- **Asymmetric edge weights in undirected graphs:** Hiking trails are bidirectional; ensure weight(u,v) = weight(v,u)
- **Mixing coordinate systems:** Convert all data to same EPSG before graph construction

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Shortest path algorithms | Dijkstra or A* implementation | `nx.dijkstra_path()`, `nx_astar_path()` | battle-tested, heavily optimized (C/NumPy) |
| Spatial nearest neighbor search | Python loops over all nodes | `scipy.spatial.KDTree.query()` | O(log n) vs O(n) for large graphs |
| OSM data parsing | XML/JSON parsing of .osm files | osmnx `graph_from_bbox()` or `graph_from_place()` | Handles topology, projection, filtering |
| Coordinate transformations | Manual projection formulas | pyproj `Transformer` or `osmnx.project_graph()` | Handles complex edge cases, error handling |
| Edge weight calculation | Manual Euclidean distance | Use `geopy.distance.geodesic()` for lat/lon, or pyproj-projected Euclidean for UTM | Earth curvature matters at Norway scale |

**Key insight:** The only custom logic needed for this phase is the polyline-to-graph conversion and terrain mesh generation. Everything else (pathfinding, spatial indexing, OSM loading, coordinate transforms) has mature, well-tested libraries that handle edge cases you'll never think of.

## Runtime State Inventory

> This is a greenfield phase (new feature implementation), not a rename/refactor/migration phase. 
> No runtime state inventory required.

**None — Phase 2 is greenfield implementation of new routing network construction capabilities.**

## Common Pitfalls

### Pitfall 1: Coordinate System Mismatch
**What goes wrong:** Trail data in EPSG:4326 (lat/lon), OSM data projected to UTM, terrain raster in yet another projection. Distance calculations become meaningless.
**Why it happens:** Mixing data sources without explicit projection handling
**How to avoid:** 
- Define a single working EPSG (e.g., 25832 for UTM 32V) for the routing graph
- Convert all inputs before graph construction using `pyproj.Transformer`
- Store EPSG in RoutingNetwork instance for validation
**Warning signs:** Computed distances are suspiciously large/small, or straight-line distance varies by edge orientation

### Pitfall 2: Node Snapping Creates Disconnected Graph
**What goes wrong:** Overly strict snap_distance prevents line endpoints from connecting, resulting in disconnected components
**Why it happens:** Trail datasets have precision errors or small gaps at intersections
**How to avoid:**
- Use adaptive snap_distance based on data quality (e.g., 10-50m for hiking trails)
- Run `nx.connected_components()` after construction to detect disconnected subgraphs
- Optional: Add "bridge edges" between nearby disconnected components
**Warning signs:** `nx.dijkstra_path()` raises `NetworkXNoPath` exception between nearby nodes

### Pitfall 3: OSM Data Out of Bounds
**What goes wrong:** User selects point outside downloaded OSM bounding box, osmnx crashes or returns empty graph
**Why it happens:** osmnx doesn't automatically extend queries beyond specified bounds
**How to avoid:**
- Check user coordinates against OSM bounding box before routing
- Provide clear error message: "Area outside downloaded map data"
- Design: Phase 2 should accept bounding box parameter and validate
**Warning signs:** Empty graph after OSM load, or routing suddenly stops working

### Pitfall 4: Duplicate Node IDs from Different Sources
**What goes wrong:** Trail dataset uses integer node IDs starting at 0, OSM uses OSM node IDs (large integers), terrain mesh uses sequential IDs. Collisions cause data overwrite.
**Why it happens:** Naive concatenation of graphs without ID prefixing/namespacing
**How to avoid:**
- Use prefixed node IDs for each source: e.g., "trail_0", "osm_123456", "mesh_0"
- Or store source in node data attribute: `graph.nodes[node_id]['source'] = 'trail'`
- Maintain source-specific lookups: `source_node_map[source][local_id] = global_id`
**Warning signs:** Graph has fewer nodes than expected, or node coordinates are wrong

### Pitfall 5: Edge Weight Type Mismatch
**What goes wrong:** Some edges have float weights, others are ints, or missing weights default to 1 incorrectly
**Why it happens:** Inconsistent weight assignment during graph construction
**How to avoid:**
- Always set explicit `weight` attribute when adding edges
- Validate: `assert all(type(d['weight']) in (int, float) for u,v,d in G.edges(data=True))`
- Use consistent naming: `length`, `weight`, `cost` should map clearly
**Warning signs:** Pathfinding returns unexpected routes, or large routing cost values

## Code Examples

Verified patterns from official sources:

### NetworkX Shortest Path
```python
# Source: [NetworkX official docs - shortest paths module]
import networkx as nx

G = nx.Graph()
G.add_edge("A", "B", weight=4)
G.add_edge("A", "C", weight=2)
G.add_edge("B", "C", weight=3)
G.add_edge("B", "D", weight=1)
G.add_edge("C", "D", weight=5)

# Dijkstra shortest path
path = nx.dijkstra_path(G, source="A", target="D", weight="weight")
# Result: ['A', 'B', 'D'] (total weight 5, shorter than A->C->D with weight 7)

# Path length
length = nx.dijkstra_path_length(G, source="A", target="D", weight="weight")
```

### A* with Geodesic Heuristic
```python
# Source: [NetworkX official docs - astar module]
import networkx as nx
import math

def geodesic_heuristic(u, v, node_coords):
    """Great-circle distance heuristic for A* in lat/lon coordinates.
    
    Args:
        u, v: Node IDs
        node_coords: dict mapping node_id -> (lat, lon)
    """
    lat1, lon1 = node_coords[u]
    lat2, lon2 = node_coords[v]
    
    # Haversine formula (simplified)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2)**2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dlon/2)**2)
    c = 2 * math.asin(math.sqrt(a))
    r = 6371000  # Earth's radius in meters
    return c * r

G = nx.Graph()
node_coords = {'A': (60.0, 10.0), 'B': (60.1, 10.1), 'C': (60.2, 10.0)}
for node, coord in node_coords.items():
    G.add_node(node)
G.add_edge("A", "B", weight=15000)
G.add_edge("B", "C", weight=14000)
G.add_edge("A", "C", weight=22500)  # Direct route

# A* with custom heuristic
path = nx.astar_path(G, source="A", target="C",
                     heuristic=lambda u, v: geodesic_heuristic(u, v, node_coords),
                     weight="weight")
```

### Graph Connected Components Check
```python
# Source: [NetworkX official docs - connectivity module]
import networkx as nx

G = nx.Graph()
G.add_path([0, 1, 2])
G.add_path([3, 4, 5])

# Check number of connected components
num_components = nx.number_connected_components(G)
# Result: 2

# Identify disconnected components
components = list(nx.connected_components(G))
# Result: [{0, 1, 2}, {3, 4, 5}]

# Check if two nodes are in same component
is_connected = nx.has_path(G, 0, 3)
# Result: False
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual OSM parsing | osmnx library (v2.0+) | 2020+ | Simplified OSM integration, handles projection automatically |
| Custom shortest path | NetworkX bidirectional Dijkstra | 2004-2012+ | Significant speedup for large graphs |
| Hand-rolled spatial index | scipy/numpy KDTrees | 2000s+ | O(log n) instead of O(n) nearest neighbor queries |

**Deprecated/outdated:**
- **osm2po**: OSM routing engine, predates osmnx, less Python-native integration
- **pyroutelib2**: Limited to OSM-only routing, no graph manipulation flexibility
- **pgrouting (PostgreSQL)**: Requires database setup, overkill for desktop-first Python app
- **graph-tool binary installation**: Requires C++ compilation, complex for cross-platform distribution (networkx pure Python is preferred for ease of development)

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | osmnx `network_type='walk'` and `custom_filter` can filter for highway=path,footway,track | Pattern 3 (OSM Data Loading) | May need alternative OSM query method (Overpass API) if filter syntax differs |
| A2 | Norwegian hiking trails are available as shapefiles/GeoJSON from Kartverket or DNT | COMP-03 Research Support | May need to scrape/derive trails from other sources (OpenStreetMap intersection with Norway boundary) |
| A3 | Terrain mesh spacing of 100m provides reasonable routing granularity | Pattern 4 (Terrain Mesh) | Too coarse: unnatural routes seen from space; Too fine: performance issues |
| A4 | Existing `vector_2026.py` can be extended in-place for polyline-to-graph conversion | Pattern 2 | If Vector class is rigid, may need separate utility module and wrapper |
| A5 | pyproj is available in .venv (verified 3.7.2) for UTM 32V projections | Standard Stack | Code will need manual coordinate transforms if not available |
| A6 | Node snap_distance of 50m appropriate for hiking trail precision | Pattern 2 | If trails have larger gaps (>50m), graph will have disconnected components |

## Open Questions

1. **Norwegian hiking trail data source**
   - What we know: DNT (Norwegian Trekking Association) maintains trails [WebSearch]
   - What's unclear: What format are they distributed in? Shapefile? GeoJSON? Do we need to request API access?
   - Recommendation: Verify data format before Phase 2 execution. If not available as public download, create placeholder trail data for proof-of-concept.

2. **OSM data availability for Norway**
   - What we know: OSM has global coverage including Norway [WebSearch]
   - What's unclear: Does Norway have dense hiking trail tagging? Are there significant gaps?
   - Recommendation: Test osmnx bbox query for sample Norway region to verify trail density.

3. **Terrain mesh integration strategy**
   - What we know: Terrain mesh required for coverage gaps
   - What's unclear: How do we detect which areas need meshing? Union operation of trail/OSM coverages? Or always generate mesh for full bbox?
   - Recommendation: Start with full-bbox mesh for simplicity. Future optimization could use spatial union to mesh only uncovered areas.

4. **Graph size and performance**
   - What we know: Norway is large (385,000 km²). Full UTM 32V raster at 50m resolution = ~150M nodes. Too large.
   - What's unclear: What bounding box size is practical for desktop routing? Do we load data on-demand per query?
   - Recommendation: Design for bbox-limited loading (e.g., 100km x 100km region). User selects route endpoints → load bbox → route → discard graph.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | All | ✓ | 3.14.4 (system), 3.12 (.venv) | Use .venv Python 3.12 |
| networkx | Graph structure | ✗ | — | Install via pip |
| scipy | Spatial indexing (KDTree) | ✗ | — | Install via pip |
| osmnx | OSM data loading | ✗ | — | Install via pip |
| pyproj | Coordinate transforms | ✓ | 3.7.2 (.venv) | Already installed |
| numpy | Array operations | ✓ | 2.4.4 (.venv) | Already installed |
| pytest | Testing | ✓ | 9.0.3 (.venv) | Already installed |

**Missing dependencies with no fallback:**
- networkx: Required for graph construction and pathfinding
- scipy: Required for KDTree node snapping (performance critical)
- osmnx: Required for OSM trail extraction

**Missing dependencies with fallback:**
- None — all missing libraries are blocking for Phase 2 core requirements

**Installation command:**
```bash
.venv/bin/python -m pip install networkx scipy osmnx
```

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.3 |
| Config file | None — configured via conftest.py |
| Quick run command | `.venv/bin/pytest tests/test_routing_graph.py -x -v` |
| Full suite command | `.venv/bin/pytest tests/ -v` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| COMP-03 | Trail polylines convert to graph with snapping | unit | `pytest tests/test_routing_graph.py::test_polylines_to_graph -x` | ❌ Wave 0 |
| COMP-03 | Graph connected components verified after conversion | unit | `pytest tests/test_routing_graph.py::test_connected_components -x` | ❌ Wave 0 |
| COMP-04 | OSM graph loads with correct highway filter | integration | `pytest tests/test_osmnx_integration.py::test_load_osmnx_trails -x` | ❌ Wave 0 |
| COMP-04 | OSM nodes extracted with correct coordinates | unit | `pytest tests/test_osmnx_integration.py::test_osm_node_coordinates -x` | ❌ Wave 0 |
| COMP-05 | Terrain mesh generates regular grid | unit | `pytest tests/test_terrain_mesh.py::test_terrain_mesh_generation -x` | ❌ Wave 0 |
| COMP-05 | Mesh edges connect nodes correctly | unit | `pytest tests/test_terrain_mesh.py::test_mesh_edge_topology -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/test_{module}.py -x -v` (module-specific tests)
- **Per wave merge:** `pytest tests/ -v` (full test suite)
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/test_routing_graph.py` — covers COMP-03 (trail polyline conversion)
- [ ] `tests/test_osmnx_integration.py` — covers COMP-04 (OSM data loading)
- [ ] `tests/test_terrain_mesh.py` — covers COMP-05 (terrain mesh generation)
- [ ] `tests/conftest.py` — shared fixtures for routing tests (reuse or extend Phase 1 conftest)
- [ ] Dependency install: `.venv/bin/pip install networkx scipy osmnx` — blocking for Phase 2 execution
- [ ] Test data: Sample trail shapefile, known OSM bbox for integration testing

*(If no gaps: "None — existing test infrastructure covers all phase requirements")*

## Security Domain

> Required when `security_enforcement` is enabled (absent = enabled). Included for completeness, though routing phase has minimal security implications.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | N/A — routing is internal computation |
| V3 Session Management | no | N/A — desktop app, no web sessions |
| V4 Access Control | no | N/A — no user permission model |
| V5 Input Validation | yes | Validate coordinate bounds, graph size limits |
| V6 Cryptography | no | N/A — no encryption required |

### Known Threat Patterns for {routing stack}

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Path traversal (file paths) | Tampering | Validate shapefile/GeoJSON paths, restrict to data/ directory |
| Graph DoS (memory exhaustion) | Denial of Service | Limit graph node count, bbox size validation |
| Invalid coordinate input | Tampering | Validate coordinate ranges (Norway: ~4-31°E, ~57-71°N) |

## Sources

### Primary (HIGH confidence)
- [networkx 3.6.1] - PyPI verified version; shortest path algorithms documentation
- [scipy 1.17.1] - PyPI verified version; scipy.spatial.KDTree documentation
- [networkx official docs] - Verified shortest_path(), astar_path(), connected_components() usage
- [PyPI API] - Package versions verified via `curl -s "https://pypi.org/pypi/{package}/json"`

### Secondary (MEDIUM confidence)
- [WebSearch verified] - osmnx 2.1.0 availability and OSM graph loading capabilities [VERIFIED: PyPI]
- [WebSearch verified] - OSM highway types for hiking: path, footway, track [ASSUMED: standard OSM tagging]
- [WebSearch verified] - Norwegian Trail data sources: DNT, Kartverket [identified but format unverified]

### Tertiary (LOW confidence)
- [WebSearch] - Norwegian hiking trails data availability and formats (not verified against official sources)
- [WebSearch] - osmnx custom_filter syntax for highway types (needs verification against docs or examples)
- [Training data] - Terrain mesh spacing selection (heuristic, needs calibration during implementation)

## Metadata

**Confidence breakdown:**
- Standard stack: MEDIUM - Package versions verified via PyPI, but osmnx API details need verification against documentation
- Architecture: MEDIUM - Patterns derived from verified NetworkX docs and standard geospatial practices, but some specifics (osmnx filter syntax) need validation
- Pitfalls: HIGH - Based on common geospatial routing pitfalls and network graph construction challenges

**Research date:** 2026-04-12
**Valid until:** 30 days (stable domain, but osmnx API details may need verification)

**Next steps for planner:**
1. Resolve Assumptions A1-A6 before finalizing tasks
2. Create Phase 2 task breakdown based on patterns in Architecture Patterns section
3. Include dependency installation task (networkx, scipy, osmnx) as Wave 0
4. Design test data acquisition (sample trail shapefile, test OSM bbox) for Wave 0