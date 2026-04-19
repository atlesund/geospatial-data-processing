# User Process: Terrain-Based Routing

**Purpose:** Complete end-to-end flow for terrain-aware hiking route planning in Norway

---

## Overview

Users download Norwegian terrain data (DTM50) as GeoTIFF files, load them into the application, select start/end points on the map, and receive optimized hiking routes that avoid steep terrain and water hazards.

---

## Complete Process Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: DOWNLOAD TERRAIN DATA                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ • Visit: https://kartverket.no/download/                                     │
│ • Select: Digital Terrengmodell (DTM50)                                      │
│ • Choose area of Norway (e.g., Bergen, Oslo)                                  │
│ • Download file format: GeoTIFF (.tif)                                        │
│ • File naming: {tilename}_50m_{zone}.tif (e.g., bergen_50m_33.tif)            │
│                                                                              │
│ NOTE: Use GeoTIFF format - has embedded georeferencing (no separate files)   │
│       Files are ~200MB per 100km x 100km tile (50m resolution)              │
└─────────────────────────────────────────────────────────────────────────────┘
                                     ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 2: STORE TERRAIN FILES                                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ • Place files in project directory:                                           │
│   - /path/to/project/bergen_50m_33.tif                                        │
│   - Or create data folder: project/data/terrain/*.tif                        │
│                                                                              │
│ NOTE: No manual mapping needed - GeoTIFF files contain embedded              │
│       coordinate metadata (EPSG code, bounds, affine transform)            │
└─────────────────────────────────────────────────────────────────────────────┘
                                     ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 3: LOAD TERRAIN DATA                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ • In application, press F5 (or choose File → Open)                            │
│ • Select the .tif file                                                       │
│ • System automatically:                                                         │
│   ✓ Extracts EPSG code from file metadata (e.g., 25833 = UTM 33V)           │
│   ✓ Reads bounding box coordinates                                          │
│   ✓ Reads affine transform matrix for pixel ↔ world mapping                │
│   ✓ Loads elevation data as numpy array                                      │
│   ✓ Converts to grayscale visualization for display                          │
│                                                                              │
│ Console output shows:                                                          │
│   Loaded GeoTIFF: bergen_50m_33.tif                                          │
│     EPSG: 25833                                                                │
│     Bounds: 99950, 6800050 to 200050, 6699950                                │
│     Resolution: 50m x 50m per pixel                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                     ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 4: GENERATE ROUTING NETWORK                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│ • Application calls: terrain_mesh_from_raster(raster, mesh_spacing=100)      │
│                                                                              │
│ Process:                                                                      │
│ 1. Create grid of nodes every 100m across the terrain tile                    │
│ 2. For each node, retrieve elevation: raster.get_elevation_at(x, y)        │
│ 3. Connect adjacent nodes with edges (horizontal + vertical)                  │
│ 4. For each edge, calculate:                                                   │
│    • Slope angle = atan(elevation_diff / edge_length)                         │
│    • If slope > 20°, apply penalty: penalty_factor = 1.0 + 0.2*(slope-20)    │
│    • Final weight = edge_length × penalty_factor                              │
│    • 20° = flat (1×), 25° = 2×, 35° = 4×, 45° = 6×, 60° = 10× cost         │
│ 5. Query OpenStreetMap for water features (lakes, rivers, fjords)           │
│ 6. Apply water crossing penalty to edges that cross water:                    │
│    • Lakes = 10× penalty                                                       │
│    • Rivers = 5× penalty                                                        │
│    • Fjords = 50× penalty                                                    │
│ 7. Combine penalties: final_penalty = terrain × water                         │
│                                                                              │
│ Output: RoutingNetwork with graph of nodes and weighted edges                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                     ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 5: USER SELECTS ROUTE POINTS                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ • User presses Shift+F9 to start route selection mode                          │
│ • First click: Sets start point (displayed as red marker)                     │
│   └─> Screen coordinates captured: [100, 200] (pixels)                      │
│ • Second click: Sets end point (displayed as blue marker)                    │
│   └─> Screen coordinates captured: [350, 450] (pixels)                      │
│                                                                              │
│ NO user declaration of tile location needed - auto-detected from file!      │
└─────────────────────────────────────────────────────────────────────────────┘
                                     ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 6: COORDINATE TRANSFORMATION (AUTOMATIC)                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ When end point is selected, routing auto-triggers:                            │
│                                                                              │
│ For start point [100, 200] and end point [350, 450]:                         │
│                                                                              │
│ 1. Screen → World coordinates:                                                │
│    Using world file affine transform:                                         │
│    start_world = utilities.screen_to_world([100, 200], affine)              │
│    → (149950, 6720050) in UTM 33V coordinates                                │
│    end_world = utilities.screen_to_world([350, 450], affine)                │
│    → (167450, 6652750) in UTM 33V coordinates                                │
│                                                                              │
│ 2. World → Network coordinates (if EPSG differs):                              │
│    Using pyproj transformer:                                                   │
│    If Screen EPSG (25833) != Network EPSG (e.g., 25832 for UTM 32V):       │
│    transformer = pyproj.Transformer.from_crs(25833, 25832, always_xy=True)   │
│    start_network = transformer.transform(149950, 6720050)                      │
│    └─> Start point in network coordinate system                               │
│                                                                              │
│ NOTE: All transforms use accurate cartographic projections,                │
│       not simple offsets. Handles all Norwegian UTM zones automatically.    │
└─────────────────────────────────────────────────────────────────────────────┘
                                     ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 7: NODE SNAPPING TO ROUTING GRAPH                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│ • Query coordinates are snapped to nearest graph nodes:                       │
│                                                                              │
│ start_node_id = RoutingNetwork.find_nearest_node(start_network_x,       │
│                                                        start_network_y)   │
│   → Uses KDTree spatial index for O(log n) lookup                           │
│   → Returns: (node_id_42, distance_from_actual_click = 3.2m)              │
│                                                                              │
│ end_node_id = RoutingNetwork.find_nearest_node(end_network_x,           │
│                                                      end_network_y)       │
│   → Returns: (node_id_157, distance_from_actual_click = 4.1m)             │
│                                                                              │
│ WHY: User clicks anywhere, routes must follow traversable network           │
└─────────────────────────────────────────────────────────────────────────────┘
                                     ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 8: COMPUTE OPTIMAL ROUTE                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ • Run Dijkstra's algorithm on weighted graph:                                  │
│                                                                              │
│ path = RoutingNetwork.shortest_path(source=node_42, target=node_157)    │
│                                                                              │
│ Algorithm considers:                                                           │
│ • Edge length in meters                                                      │
│ • Slope penalty (steeper = higher cost)                                        │
│ • Water crossing penalty (lakes = 10×, fjords = 50×)                          │
│                                                                              │
│ Result: [node_42, node_61, node_88, ..., node_157]                           │
│        (~100-500 nodes depending on terrain complexity)                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                     ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 9: COORDINATE MAPPING BACK TO DISPLAY                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. Extract coordinates from each node in path:                                │
│    For node_id in path:                                                       │
│      coord = RoutingNetwork.node_coords[node_id]                              │
│      → Stores in route_network_coords for GPX export                        │
│                                                                              │
│ 2. Transform network → screen coordinates:                                    │
│    screen_point = Screen.world_to_screen(coord)                              │
│    → Applies inverse of affine transform                                     │
│                                                                              │
│ 3. Store screen coordinates for display:                                      │
│    route_screen_coords = [[150, 210], [180, 230], ..., [355, 455]]           │
└─────────────────────────────────────────────────────────────────────────────┘
                                     ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 10: DISPLAY ROUTE ON MAP                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ • Clear previous routes: Screen.delete('route')                             │
│ • Draw new route as orange polyline:                                          │
│   Screen.draw_polyline(                                                       │
│     polyline=route_screen_coords,                                            │
│     width=4,                                                                  │
│     colour='orange',                                                           │
│     tag='route'                                                               │
│   )                                                                           │
│                                                                              │
│ User sees:                                                                     │
│ • Orange line connecting start (red) and end (blue) points                     │
│ • Route follows natural paths, avoids climbing steep mountains directly      │
│ • Pink optional: Export as GPX (F5) for GPS navigation device                │
└─────────────────────────────────────────────────────────────────────────────┘
                                     ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 11: EXPORT ROUTE (OPTIONAL)                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ • User presses F5 to export                                                   │
│ • GPX file generated with:                                                     │
│   - <trk><trkseg> containing all route waypoints                             │
│   - WGS84 coordinates (converted from UTM 33V/32V)                            │
│   - Elevation data at each point                                             │
│ • File ready for upload to GPS device or hiking app (Garmin, Komoot, etc.)   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Key Advantages of This Process

### 1. **No Manual Georeferencing Required**
- GeoTIFF files contain all metadata automatically
- System knows tile location, CRS, and scale instantly

### 2. **No User Declaration of Tile Location**
- File name doesn't affect coverage
- Bounding box extracted from file metadata
- Users don't need to know UTM zones or coordinate systems

### 3. **Accurate Coordinate Transformations**
- Uses proper cartographic projections (pyproj)
- Handles all Norwegian UTM zones automatically
- Supports seamless tile stitching (different zones, different scales)

### 4. **Smart Route Optimization**
- Terrain-aware: Penalizes steep climbs (>20°)
- Water-aware: Avoids lakes, rivers, fjords
- Realistic hiking paths based on actual topography

---

## Common Questions

### Q: What happens if I download tiles from different UTM zones?

**A:** The system handles this automatically. Each GeoTIFF file has its own EPSG code (e.g., 25832, 25833, 25834, 25835, 25836). The routing network can work within a single zone without issues. For cross-zone routing, tiles would need to be reprojected to a common zone first.

### Q: Can I see a preview of which area of Norway the tile covers?

**A:** Yes! When you load a .tif file, the console output shows the bounds in UTM coordinates. For better visualization, we could add a preview map overlay showing the tile location on a base map of Norway.

### Q: What if the terrain data has gaps or invalid values?

**A:** The system handles this gracefully:
- Nodata values are replaced with NaN
- Edges with NaN elevation fall back to uniform weights
- Affected areas still routeable, just without terrain penalties

### Q: How large can the route area be?

**A:** One DTM50 tile covers 100km × 100km. For larger areas:
- Download adjacent tiles
- They can be merged into a single network
- Or process per-tile and stitch results

---

## Data Source: Kartverket DTM50

**Provider:** Norwegian Mapping Authority (Kartverket)
**Dataset:** Digital Terrain Model 50m (DTM50)
**Coverage:** All of Norway
**Resolution:** 50 meters per pixel
**Accuracy:** Comparable to actual topography
**Download:** https://kartverket.no/download/

**File Format:**
- GeoTIFF with embedded georeferencing
- Metadata includes EPSG code, bounds, affine transform
- No separate world files needed

**Coordinate Systems by Zone:**
- UTM Zone 32V (southern/eastern): EPSG:25832
- UTM Zone 33V (western/central): EPSG:25833
- UTM Zone 34V (northern central): EPSG:25834
- UTM Zone 35V (northern): EPSG:25835
- UTM Zone 36V (far north): EPSG:25836

---

## Example: Full Workflow

```bash
# 1. User downloads Bergen terrain
Downloaded: bergen_50m_33.tif (from Kartverket Design 6701)
Placed in: ~/projects/geospatial-data-processing/data/terrain/

# 2. Launch application
python example_phase06_gui_routing.py

# 3. Load terrain (F5)
Loaded GeoTIFF: data/terrain/bergen_50m_33.tif
  EPSG: 25833  (UTM Zone 33V)
  Bounds: 99950, 6800050 to 200050, 6699950
  Resolution: 50m x 50m per pixel

# 4. Create routing network (automatic with .tif load)
Generating terrain mesh...
Network created: 1000 nodes, 1958 edges, EPSG: 25833
Network assigned to screen.

# 5. User selects start point (Shift+F9)
Click screen at [400, 300] → snapped to node_42
Start point selected: [400, 300]

# 6. User selects end point (second click)
Click screen at [600, 450] → snapped to node_157
End point selected: [600, 450]

# 7. Route computation (auto-trigger)
Route computed: 47 vertices, 2.1m from start node, 3.8m from end node
Total distance: 12.3 km
Elevation gain: 450 m
Steep segments: 3 (avoided via detours)
Water crossings: 1 (bridge/penalty applied)

# 8. Route displayed
Orange polyline shows optimized path from start to end

# 9. Export GPX (F5)
GPX exported: bergen_hike_2026-04-19.gpx
Ready for GPS device upload
```

---

## Files Involved

| File | Purpose | Key Functionality |
|------|---------|-------------------|
| `raster_2026.py` | Terrain data loading | `read_image()`, `get_elevation_at()`, `_read_geotiff()` |
| `routing_2026.py` | Routing network | `terrain_mesh_from_raster()`, `calculate_terrain_weight()` |
| `screen_2026.py` | GUI & display | `_compute_and_display_route()`, `world_to_screen()` |
| `utilities_2026.py` | Coordinate transforms | `screen_to_world()`, `warning()` |

---

## Phase Implementation Status

| Phase | Status | Implemented By |
|-------|--------|----------------|
| Phase 1: Map Interaction | ✅ Complete | Shift+F9/F10 point selection |
| Phase 2: Routing Network | ✅ Complete | Grid + OSM trail integration |
| Phase 3: Steep Terrain Penalty | ✅ Complete | >20° slope penalties |
| Phase 4: Water Body Penalty | ✅ Complete | Lake/river/fjord penalties |
| Phase 5: Route Visualization | ✅ Complete | Orange polyline + GPX export |
| Phase 6: GUI Integration | ✅ Complete | Auto-trigger routing |

**GeoTIFF Support:** ✅ Now implemented (via current update)

---

*Document created: 2026-04-19*
*Process updated: GeoTIFF loading with rasterio*