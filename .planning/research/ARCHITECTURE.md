# Architecture — Hiking Route Planner Integration

## New Components

### Route Data Model

**Class**: `Route`
- **Purpose**: Represents a hiking route with geometry, elevation profile, and route-specific attributes
- **Extends/uses**: Inherits from `Vector` (POLYLINE) or composes a Vector instance
- **Key methods**:
  - `compute_elevation_profile(dem)` — Sample polyline against terrain DEM
  - `calculate_stats()` — Total distance, elevation gain/loss, max elevation
  - `export_gpx(filepath)` — Generate GPX format file
  - `get_altitudes_at_intervals(interval_meters)` — For profile plotting
- **Properties**:
  - `elevation_profile` — List of (distance, elevation) tuples along route
  - `total_distance` — Computed route length in meters
  - `elevation_gain`, `elevation_loss` — Cumulative elevation changes
  - `max_elevation`, `min_elevation` — Extremal elevations along route
  - `scenic_score` — Computed scenic quality metric
  - `difficulty_class` — Derived from gain/distance ratio

### Terrain Manager

**Class**: `TerrainManager`
- **Purpose**: Fetch, cache, and provide access to terrain elevation data
- **Extends/uses**: Integrates with existing `Raster` class for display
- **Key methods**:
  - `download_region(bbox, dem_type='DTM50')` — Fetch from Kartverket by bounding box
  - `get_elevation(lat, lon)` — Sample elevation at coordinate point
  - `get_elevation_along_path(coords)` — Sample elevation along polyline
  - `tile_manager` — Internal: handle tile-based loading (for large DEMs)
  - `merge_tiles(bbox)` — Combine multiple tiles into continuous raster
  - `is_cached(bbox)` — Check if terrain data already available offline
- **Integration point**: Loads terrain as `Raster` objects with georeferencing; uses `utilities_2026.screen_to_world()` for coordinate transforms

### Routing Network Builder

**Class**: `RoutingNetworkBuilder`
- **Purpose**: Construct weighted graph from multiple data sources for path finding
- **Extends/uses**: Creates NetworkX DiGraph; builds from OSM data and terrain
- **Key methods**:
  - `build_from_osm(bbox)` — Extract trails/paths from OpenStreetMap via osmnx
  - `add_terrain_edges(dem, resolution=50)` — Add terrain-based edges where trails don't exist
  - `apply_elevation_weights(dem, max_gain)` — Compute edge costs from terrain
  - `apply_scenic_weights(water, named_features)` — Boost scenic routes
  - `apply_water_penalties(hydrography)` — Penalize water crossings
  - `get_graph()` — Return NetworkX DiGraph for path finder
- **Data sources**: Kartverket (hydrography), OSM (trails/paths/roads), terrain DEM (elevation)

### Cost Surface Engine

**Class**: `CostSurfaceEngine`
- **Purpose**: Compute weighted cost surface for terrain-based routing
- **Extends/uses**: Uses DEM data via TerrainManager; outputs to RoutingNetworkBuilder
- **Key methods**:
  - `compute_slope(dem)` — Derive slope from elevation gradients
  - `compute_distance_weight()` — Base cost = Euclidean distance
  - `apply_elevation_cost(slope, max_gain)` — Add cost for steepness
  - `apply_scenic_cost(water_proximity, features)` — Discount for scenic locations
  - `apply_water_crossing_cost(hydrography, bridges)` — Penalty for crossings
  - `get_cost_graph()` — Return weighted graph for path finding
- **Dependencies**: Elevation DEM (TerrainManager), hydrography data, scenic features database

### Path Finder

**Class**: `PathFinder`
- **Purpose**: Find optimal paths on weighted routing graph
- **Extends/uses**: Uses NetworkX graph from RoutingNetworkBuilder
- **Key methods**:
  - `find_path(start, end, optimize='distance')` — Main path finding interface
  - `find_alternatives(start, end, n=3)` — Multiple route options
  - `_astar(graph, start, end)` — A* algorithm implementation
  - `_suggest_from_names(graph, start_name, end_name)` — Resolve named locations
  - `score_route(route)` — Evaluate route quality (distance/elevation/scenic)
- **Algorithm choices**: A* for single best path; path scoring for alternatives; NetworkX `shortest_path` for baseline comparison

### Offline Cache Manager

**Class**: `OfflineCacheManager`
- **Purpose**: Manage offline data storage (terrain, OSM, metadata)
- **Extends/uses**: Stands alone; integrates with TerrainManager and RoutingNetworkBuilder
- **Key methods**:
  - `download_all_for_region(bbox)` — Orchestrate all data downloads
  - `get_cache_size()` — Return total storage usage
  - `clear_cache(bbox)` — Delete cached data for region
  - `list_cached_regions()` — Return available cache regions
  - `is_download_complete(bbox)` — Check if all data cached
  - `invalidate_bounding_data()` — Handle data updates
- **Data stored**:GeoPackage files for OSM networks, GeoTIFF for DEM tiles, metadata JSON

### Route Composer (Orchestrator)

**Class**: `RouteComposer`
- **Purpose**: Coordinate route computation pipeline from user input to GPX export
- **Extends/uses**: Glues together TerrainManager, RoutingNetworkBuilder, CostSurfaceEngine, PathFinder
- **Key methods**:
  - `compute_route(start_coord, end_coord, config)` — Main entry point
  - `configure(params)` — Set route preferences (max elevation, scenic weight, etc.)
  - `get_alternatives()` — Return multiple route options
  - `export_route(route_index, format='gpx')` — Export computed route
- **Pipeline stages**:
  1. User input (coordinates) → RouteComposer
  2. Fetch terrain data → TerrainManager (from cache or download)
  3. Extract OSM data → RoutingNetworkBuilder
  4. Build routing graph → RoutingNetworkBuilder + CostSurfaceEngine
  5. Find optimal paths → PathFinder
  6. Generate routes → Route objects with elevation profiles
  7. Export → GPX files

## Existing Component Extensions

### Vector class

**Additions**:
- **New methods**:
  - `sample_elevation(dem, interval_meters=25)` — Return elevation profile along polyline
  - `calculate_distance()` — Return length in meters (may exist, verify)
- **Attributes**:
  - `_epsg` already exists (for coordinate transforms)
  - Add `_elevation_profile` as optional property
- **Backward compatible**: Yes — new methods are additive; route-specific attributes stored separately in Route class

### Screen class

**Additions**:
- **New methods**:
  - `click_to_coordinate(event)` — Convert canvas click to lat/lon (extend F9 digitizing)
  - `draw_route(route, color='blue', width=2)` — Render route polylines on map
  - `draw_elevation_profile(route, x, y, width, height)` — Embed matplotlib figure
  - `show_route_stats(route)` — Display distance/elevation in GUI
- **UI components**:
  - Route configuration dialog (max elevation, scenic slider)
  - Cache manager dialog (download regions, view storage)
  - Route alternatives selector (dropdown/list for choosing option)
  - Export dialog (GPX file path, format options)
- **Event handlers**:
  - Route selection click (choose start/end points)
  - Hover over route alternatives (preview)
  - Right-click context menu (download area, clear cache)
- **Backward compatible**: Yes — all additions are new UI/methods; existing event bindings preserved

### Utilities module (`utilities_2026.py`)

**New functions**:
- **Coordinate transforms**:
  - `safe_zone_transform(lat, lon, from_epsg, to_epsg)` — Handle Norway UTM zones
  - `get_utm_zone(lat, lon)` — Return UTM zone number for coordinate
  - `project_to_local(lat, lon)` — Use appropriate UTM zone for Norway location
- **Elevation operations**:
  - `sample_raster_at_coord(raster, lat, lon)` — Get elevation at point
  - `resample_raster_along_line(raster, coords)` — Extract profile along polyline
- **File I/O**:
  - `write_route_to_gpx(route, filepath)` — GPX file generation
  - `read_route_from_gpx(filepath)` — Load GPX route (potential future feature)

## Data Flow

```
[GUI: Screen.click_to_coordinate()]
         ↓
[RouteComposer.compute_route(start, end, config)]
         ↓
[TerrainManager.get_cached_or_download(bbox)]
         ├─→ [Cache check]
         ├─→ [Download from Kartverket if needed]
         └─→ [Return DEM Raster]
         ↓
[RoutingNetworkBuilder.build_network(bbox, dem)]
         ├─→ [OSM Fetcher: extract trails/paths]
         ├─→ [Terrain edges: generate from DEM]
         └─→ [NetworkX DiGraph created]
         ↓
[CostSurfaceEngine.compute_weights(graph, dem, config)]
         ├─→ [Elevation weights from slope]
         ├─→ [Scenic weights from features]
         └─→ [Water crossing penalties]
         ↓
[PathFinder.find_path(graph, start, end, config)]
         ├─→ [A* search for optimal route]
         ├─→ [Alternatives generation via path modifiers]
         └─→ [Return paths as coordinate lists]
         ↓
[Route objects creation]
         ├─→ [Route.from_coordinates(coords)]
         ├─→ [route.compute_elevation_profile(dem)]
         └─→ [route.calculate_stats()]
         ↓
[GUI: Screen.draw_route(route)]
         ├─→ [Visualize route polyline on map]
         ├─→ [Screen.draw_elevation_profile(route)]
         └─→ [Display stats: distance, gain, loss]
         ↓
[Export: route.export_gpx(filepath)]
         └─→ [GPX file generated]
```

## Build Order Implications

1. **Phase 1 - Foundation (Terrain & Cache)**:
   - Terrain Manager (Kartverket DTM download/loading)
   - Offline Cache Manager (storage, invalidation)
   - Extended Utilities (coordinate transforms, DEM sampling)
   - **BLOCKS**: All phases require terrain data access

2. **Phase 2 - Network (OSM & Routing)**:
   - Routing Network Builder (OSM extraction, terrain edges)
   - Path Finder (basic A* on distance-only graph)
   - Extended Screen (click-to-coordinate for input)
   - **BLOCKS**: Phase 3 (need graph before cost surface)

3. **Phase 3 - Cost Surface (Weights & Optimization)**:
   - Cost Surface Engine (elevation/scenic/water weights)
   - Path Finder enhancements (optimization mode support)
   - Route Composer (coordinate pipeline)
   - **BLOCKS**: Phase 4 (need weighted paths before routes)

4. **Phase 4 - Route Model (Output & Export)**:
   - Route class (elevation profile, stats, GPX export)
   - Route Composer integration (Route → GPX pipeline)
   - Extended Screen (route visualization)
   - **BLOCKS**: Phase 5 (need routes before full UI)

5. **Phase 5 - UI Polish (Configuration & Alternatives)**:
   - Configuration dialogs (max elevation, scenic preferences)
   - Route alternatives generation and UI
   - Cache manager UI (download regions, storage view)
   - Interactive elevation profile (point inspection)

## Integration Touch Points

- **Terrain Manager ↔ Raster class**:
  - Terrain Manager creates Raster objects for loaded DEMs
  - Raster's existing `_epsg` tracking used for coordinate transforms
  - Screen's raster drawing reused for terrain visualization

- **Routing Network Builder ↔ Vector class**:
  - OSM paths converted to Vector POLYLINE instances for storage/analysis
  - Existing Vector.select() used for filtering OSM features by type (path vs. road)

- **Route ↔ Vector class**:
  - Route composes a Vector POLYLINE for geometry
  - Route-specific properties (elevation profile, stats) stored separately
  - Route can be visualized using Screen.draw_polyline() (existing method)

- **Screen ↔ Route Composer**:
  - Screen's click events provide coordinates to RouteComposer
  - Screen's existing digitizing (F9/F12) patterns extended for start/end selection
  - Route display adds to existing drawing methods (points, polylines, polygons)

- **Offline Cache ↔ File I/O** (utilities_2026):
  - Existing GeoJSON/Shapefile/CSV read/write reused for cache metadata
  - Cache manager adds GeoTIFF and GeoPackage format handling

## Python Module Structure

```
geo_2026/                    # Entry point (existing)
├── vector_2026.py           # Existing — extend with elevation sampling
├── raster_2026.py           # Existing — use for DEM display
├── screen_2026.py           # Existing — extend with routing UI
├── utilities_2026.py        # Existing — extend with transforms, GPX
├── route.py                 # NEW — Route class, elevation profile
├── terrain.py               # NEW — Terrain Manager, cache integration
├── routing.py               # NEW — Network builder, Path Finder
├── cost.py                  # NEW — Cost Surface Engine
├── config.py                # NEW — Route configuration presets
└── cache.py                 # NEW — Offline Cache Manager

examples/                    # Existing — add route examples
├── example_501_terrain_download.py
├── example_502_osm_network.py
├── example_503_basic_route.py
├── example_504_elevation_profile.py
├── example_505_scenic_route.py
└── example_506_gpx_export.py
```

---
*Research completed: 2026-04-12*