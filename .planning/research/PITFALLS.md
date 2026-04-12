# Pitfalls — Norwegian Hiking Route Planning

**Domain:** Geospatial routing with terrain analysis in Norway
**Researched:** 2026-04-12
**Overall Confidence:** MEDIUM (Limited current documentation access, based on codebase analysis and domain knowledge)

## Critical Pitfalls (Blockers or Major Rework)

### Coordinate System Zone Crossing
**Problem:** Norway spans four UTM zones (32-35N), with significant distortion and potential for inaccurate routing when transforming coordinates between zones. Routes crossing zone boundaries can appear discontinuous or create misleading distance calculations.

**Warning Signs:**
- Route calculations show unexpected jumps in distance or direction
- Coordinates fall near zone boundaries (longitude ~3°, 6°, 9°, 12° E)
- EPSG transformation warnings in logs
- Visual gaps in route visualization between overlapping zones

**Prevention:**
- Store all coordinate data in WGS84 (EPSG:4326) as master format
- Use geographic coordinates (lat/lon) for distance calculations (haversine)
- Apply UTM projections only for display and terrain analysis purposes
- Implement zone-aware routing: detect zone crossings and handle transformations explicitly
- Use pyproj's area_of_use metadata to validate coordinate validity per zone

**Phase to Address:** Phase 1 (Foundational infrastructure)

**Source:** Confirmed by existing codebase analysis - `vector_2026.py` lines 486-526 show basic projection support but lack zone boundary handling

### DEM Memory Exhaustion
**Problem:** Loading entire Digital Terrain Models (DTM50/DTM10) for large areas (e.g., entire Norway or multi-municipality hikes) can cause Python memory exhaustion (typically 2-4GB limit per process). DTM50 for Norway is ~50GB uncompressed; attempting to load as numpy arrays will cause crashes.

**Warning Signs:**
- MemoryError or "killed: 9" process termination
- Performance degradation with larger route areas
- System swap usage spikes during route computation
- Loading times increase dramatically with area size

**Prevention:**
- Implement tile-based DEM processing: load only the bounding box area needed for route
- Use streaming DEM readers (e.g., rasterio) instead of loading entire files
- Cache frequently-accessed tiles in LRU cache (size-limited)
- Process DEM in chunks for cost surface computation
- Coordinate tile boundaries with route bounding box
- Implement fallback to lower resolution (DTM50) for large areas, DTM10 for small areas

**Phase to Address:** Phase 2 (Data handling infrastructure)

**Source:** Codebase analysis shows `raster_2026.py` uses tkinter.PhotoImage for raster handling, not suitable for large DEM processing

### Cost Surface Resolution Mismatch
**Problem:** Using DEM resolution directly for routing cost surfaces creates computational explosion. A 10m DEM for a 50km^2 area = 500,000 cells; 8-neighbor connectivity = ~4,000,000 graph edges. A* search becomes impractically slow.

**Warning Signs:**
- Route calculation times >10 seconds for moderate areas
- CPU usage hits 100% without completion
- Memory usage spikes during pathfinding
- Performance acceptable on test data (10km^2) but times out on real hikes (100km^2+)

**Prevention:**
- Resample cost surfaces before routing: match resolution to pathfinding needs (20-50m typical for hiking)
- Implement hierarchical routing: coarse resolution first, refine near optimal path
- Use directed graph pruning based on terrain constraints (max slope, water barriers)
- Limit search space with bounding box expansion from straight-line path
- Pre-compute traversal costs per cell (elevation change + slope + surface type)

**Phase to Address:** Phase 2-3 (Routing algorithm implementation)

**Source:** Project requirements mention terrain-based routing; codebase has no routing implementation yet

## Norway-Specific Gotchas

### UTM Zone Boundaries
**Issue:** Norway's longitudinal span (4°E to 31°E) causes 4 UTM zone boundaries. Each 6° wide zone has its own central meridian; points near boundaries (within ~200km) exhibit significant projection distortion.

**Mitigation:**
- Use geographic coordinates (WGS84) for all persistent storage and route calculations
- For terrain analysis, project to appropriate UTM zone per region (not per query)
- Implement zone detection: given lat/lon, determine if within 3° of zone boundary
- For routes crossing zones: solve per zone, stitch results at boundary
- Document in UI: "Routes crossing UTM zones may have minor discontinuities"

### Kartverket API Limitations
**Issue:** Kartverket (Norwegian Mapping Authority) APIs for downloading DTM data have rate limits, chunk size restrictions, and may require Norwegian metadata or authentication. Not designed for bulk programmatic access.

**Mitigation:**
- Implement download with retry-backoff (exponential backoff for rate limits)
- Store downloaded DEMs locally in cache directory with version tracking
- Design for offline-first: initial download may take hours, but subsequent use is local
- Include manual file option: user can preload Kartverket data from official download portal
- Document data sources and license requirements in UI
- Cache invalidation strategy: track Kartverket data version via file timestamps

**Sources:**
- Kartverket data download portal provides bulk download options
- GEO-NORGE infrastructure may offer alternative access patterns

### Seasonal Trail Closures
**Issue:** Many Norwegian trails close seasonally (mid-September to mid-June) due to snow, avalanche danger, or wildlife protection. Routes valid in summer may be impassable or dangerous in winter.

**Mitigation:**
- V1 Scope: Rain routes for "optimal conditions" (summer hiking season)
- Include disclaimer in UI: "Routes assume non-winter conditions"
- Store OSM seasonal tags (seasonal=*, access=seasonal=*) in route metadata
- Optional: user can enter date; system flags potential seasonal issues
- Future enhancement: integrate weather data for real-time conditions

### Alpine Terrain Complexity
**Issue:** Norwegian mountain terrain (fjords, steep ridges, glaciers) creates routing challenges impossible to solve purely with DEM elevation data. Glaciers require ice knowledge; steep cliffs may be impassable; snow conditions change daily.

**Mitigation:**
- Set maximum slope thresholds (~50% for hiking, ~30% for family routes)
- Identify glaciers from available layers (apply high penalty or require user acknowledgment)
- Use OSM surface tags (rock, scree, paved, dirt) for cost surface weighting
- Include "technical difficulty" rating in route output
- V1 Limitation: Cannot automate glacier/complex terrain safety; requires user validation

**Sources:**
- Norwegian Trekking Association (DNT) trail classification system
- Standard hiking difficulty grading (T1-T5 or Easy-Expert)

## Common Implementation Mistakes

### DEM Processing
**Mistake:** Loading entire DEM files into memory as numpy arrays for route computation.

**Better Approach:**
```python
# BAD: Loads entire DEM (GBs of memory)
dem = np.fromfile('dtm50.bin')  # Crashes on large areas

# GOOD: Loads only necessary tiles
import rasterio
from rasterio.windows import from_bounds

with rasterio.open('dtm50.tif') as src:
    window = from_bounds(min_x, min_y, max_x, max_y, src.transform)
    dem_tile = src.read(1, window=window)  # Only bbox area
```

**Why:** Enables routing for large areas without memory exhaustion.

### OSM Data Extraction
**Mistake:** Using Overpass API queries without bounding box limits, causing timeouts on large Norway-wide requests.

**Better Approach:**
```python
# BAD: Entire Norway path network
query = 'way["highway"~"path|track"];'

# GOOD: Bounded query with timeout
query = f'''
way["highway"~"path|track,yes,primary,secondary"]({south},{west},{north},{east});
out;
'''
```

**Why:** Each query completes quickly (<5s); can tile for larger areas.

**Mistake:** Not caching OSM data between routes.

**Better Approach:** Store OSM network locally in GeoJSON/app format, only fetch new on user request or time-based refresh (monthly).

**Why:** Avoids repeated API calls, improves offline capability.

### Path Finding on Cost Surfaces
**Mistake:** Using undirected 8-neighbor connectivity for all terrain, allowing routes downstream on steep slopes that are dangerous or impossible.

**Better Approach:**
```python
# BAD: Always 8 neighbors, all directions
neighbors = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]

# GOOD: Direction-dependent costs based on slope
def traversal_cost(cell_from, cell_to):
    slope = calculate_slope(cell_from, cell_to)
    # Uphill high cost, high penalty for extreme slopes
    if slope > MAX_SLOPE:
        return float('inf')  # Impassable
    elif slope > 0:  # Uphill
        return BASE_COST * (1 + slope * SLOPE_FACTOR)
    else:  # Downhill
        return BASE_COST * (1 - min(slope, -0.1) * 0.5)
```

**Why:** Prevents dangerous routes up cliffs; rewards reasonable ascents/descents.

**Mistake:** Not accounting for water bodies as barriers.

**Better Approach:**
- Load water polygon layers (from Kartverket or OSM)
- Rasterize water to cost surface: assign high penalty (100x normal) or impassable
- For known bridges/fords (OSM tags): create low-cost crossing cells
- User preference: "Avoid water crossings" vs. "Allow with bridges/fords"

### Offline Cache Management
**Mistake:** No cache invalidation strategy - stale DEM data used indefinitely.

**Better Approach:**
```python
class TerrainCache:
    def __init__(self, cache_dir):
        self.cache_dir = cache_dir
        self.version_file = os.path.join(cache_dir, 'version.json')

    def is_version_valid(self, dataset_id):
        """Check if cached data matches current version"""
        if not os.path.exists(self.version_file):
            return False
        with open(self.version_file) as f:
            cached = json.load(f)
        # Compare Kartverket data version or timestamp
        return cached.get(dataset_id) == self.get_source_version(dataset_id)

    def download_and_cache(self, dataset_id, bbox):
        """Download new version, update cache"""
        dem_data = self.download_from_api(dataset_id, bbox)
        self.save_to_cache(dataset_id, dem_data)
        self.update_version_file(dataset_id, self.get_source_version(dataset_id))
```

**Why:** Users get corrected terrain when Kartverket updates errors.

**Mistake:** No storage limits - cache grows indefinitely.

**Better Approach:** Implement LRU cache with size limit (e.g., 10GB), or explicit cache management UI for users to clear old areas.

## Performance Bottlenecks

### DEM Reading
**Problem:** Reading DEM tiles from disk is I/O-bound; synchronous file reads block route computation.

**Profiling:**
```python
import cProfile

def test_dem_loading():
    with rasterio.open('dtm50.tif') as src:
        for i in range(100):
            window = from_bounds(*bbox, src.transform)
            data = src.read(1, window=window)

cProfile.run('test_dem_loading()', 'dem_profile.stat')
# Check time in rasterio.read operations
```

**Optimization:**
- Use memory-mapped DEMs (rasterio MemoryFile)
- Pre-load frequently-used tiles into RAM cache
- Parallelize tile loads for multi-threaded route search
- Use compressed formats (e.g., GeoTIFF with LZW compression)

### Cost Surface Computation
**Problem:** Computing slope, aspect, and traversal costs for each cell involves multiple passes over DEM (expensive for 1M+ cells).

**Profiling:**
```python
import time

def test_cost_computation(dem_data):
    start = time.time()
    cost_surface = compute_traversal_costs(dem_data)  # Your function
    elapsed = time.time() - start
    print(f"Cost surface: {elapsed:.2f}s for {dem_data.size} cells")
    # Should be <1s for 1M cells
```

**Optimization:**
- Vectorized numpy operations (not Python loops)
- Combine slope+aspect+slope calculations in single pass
- Use lookup tables for discrete costs (surface type categories)
- Pre-compute and cache cost surfaces for popular areas

**Example:**
```python
# BAD: Python loop (slow)
cost = np.zeros_like(dem)
for i in range(dem.shape[0]):
    for j in range(dem.shape[1]):
        cost[i,j] = calculate_slope(dem[i,j], dem[i+1,j], dem[i,j+1])

# GOOD: Vectorized numpy fast
dy, dx = np.gradient(dem)
slope = np.arctan(np.sqrt(dx**2 + dy**2))
cost = BASE_COST * (1 + slope * SLOPE_FACTOR)
```

### Graph Search
**Problem:** A* pathfinding on large raster graphs explores millions of nodes before finding optimal path.

**Profiling:**
```python
def test_astar_performance(start, goal, cost_surf):
    start_time = time.time()
    path = a_star_search(cost_surf, start, goal)
    elapsed = time.time() - start_time
    nodes_explored = len(closed_set)
    print(f"A*: {elapsed:.2f}s, {nodes_explored} nodes")
```

**Optimization:**
- Heuristic function: use straight-line Euclidean distance (admissible)
- Bounding box: limit search to expanded corridor around straight line
- Hierarchical A*: coarse resolution first, refine narrow band
- Beam search: prune to top K candidates per iteration (approximate but fast)

**Milestone:** Aim for <5 seconds for 100km^2 routes, <30s for 500km^2 routes.

## Safety Considerations

### Risk: Avalanche Zones
**Detection:** Identify high slopes (>30°) on north/northeast-facing slopes in winter months from DEM aspect+slope.

**Prevention:**
- Apply high penalty (>100x) to cells with slope >30° and aspect in [300°, 60°] (N/NE)
- Include warning in route output: "Route passes through potential avalanche terrain"
- Validate against known avalanche paths if available

**Limitation:** V1 cannot automate avalanche risk assessment. Relies on slope thresholds and warns user.

### Risk: Steep Ascents
**Detection:** Compute cumulative elevation gain and maximum slope angle.

**Prevention:**
- User-configurable max total gain (e.g., 500m, 1000m)
- Max slope threshold applies per segment
- Provide alternative route if exceeded: "Route exceeds your max elevation gain setting"

**Limitation:** Can detect steep segments, cannot assess technical climbing difficulty.

### Risk: Tide-Affected Water Crossings
**Detection:** Identify coastal paths that cross narrow fjord inlets (<500m width) from coastline polygons.

**Prevention:**
- Store crossing location in route metadata
- Include warning: "Check local tide conditions before crossing"
- Mark on map with safety icon

**Limitation:** V1 cannot integrate tide tables; user must check externally.

### Risk: Unbridged River Crossings
**Detection:** Water polygon intersections without OSM bridge tags.

**Prevention:**
- Auto-mark as "unbridged crossing - check season/current"
- Require user acknowledgement before generating route with unknown crossings
- Prefer routed paths around water bodies

**Limitation:** Cannot detect river depth, width, or current conditions.

## Testing Strategy

### Test Category: Route Accuracy Against Known Paths
**Test Data Sources:**
- Norwegian Trekking Association (DNT) GPX routes for popular hikes (Preikestolen, Trolltunga, Besseggen)
- OpenStreetMap "route=hiking" relations with validation dates
- User-contributed test routes (community feedback loop)

**Validation Methods:**
```python
def compare_routes(generated_path, reference_gpx):
    """Compute similarity metrics"""
    # 1. Hausdorff distance: maximum deviation
    hausdorff = max_hausdorff_distance(generated_path, reference_gpx)

    # 2. Average distance from reference path
    mean_dev = mean_distance(generated_path, reference_gpx)

    # 3. Length ratio (should be 1.0-1.5 due to optimization preferences)
    length_rat = length(generated_path) / length(reference_gpx)

    # 4. Elevation profile comparison (if available)
    max_gain_diff = abs(max_gain(generated) - max_gain(reference))

    print(f"Hausdorff: {hausdorff:.0f}m, Mean deviation: {mean_dev:.0f}m")
    print(f"Length ratio: {length_rat:.2f}, Elevation gain diff: {max_gain_diff:.0f}m")

    # Pass criteria: Hausdorff <500m, mean deviation <100m, length ratio 0.8-1.3
    assert hausdorff < 500, "Route too far from known path"
```

**Acceptable Deviation:** Routes within 100m average deviation of known paths; >500m maximum deviation indicates algorithm issues.

### Test Category: Coordinate Transformation Consistency
**Test Data:**
- Generator: create grid of points across Norway (lat 58-71°N, lon 4-31°E)
- Known coordinates from Kartverket reference stations

**Validation:**
- Transform WGS84 → UTM32N/33N/34N/35N → back to WGS84, check <0.1m error
- distances computed in projected vs geographic coordinate systems
- Zone boundary: ensure forward/backward transformation preserves coordinates within tolerance

### Test Category: Performance Benchmarks
**Test Scenarios:**
- Small hike (10km^2, DTM10): target <2 seconds
- Medium hike (100km^2, DTM50): target <5 seconds
- Large region (500km^2, DTM50): target <30 seconds
- Zone-crossing route (200km^2 across 2 UTM zones): target <10 seconds

**Profiling Tools:**
```python
import cProfile
import pstats
import tracemalloc

def profile_route_generation(start, end, bbox):
    # Memory profiling
    tracemalloc.start()
    path = generate_route(start, end, bbox)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"Memory usage: peak {peak / 1024 / 1024:.1f} MB")

    # CPU profiling
    profiler = cProfile.Profile()
    profiler.enable()
    path = generate_route(start, end, bbox)
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumtime').print_stats(10)  # Top 10 functions
```

**Pass Criteria:** Peak memory <500MB for all scenarios; top functions show no degenerate O(n²) patterns.

### Test Category: Data Quality Validation
**Test Data:**
- OSM Norway hiking network download
- Kartverket DTM50 sample tiles

**Validation:**
- Check for disconnected trail segments (graph connectivity)
- Verify DEM完整性 (no nodata values in route box)
- Validate water obstacle detection (known river crossings flagged)
- Seasonal tagging coverage (percentage of trails with seasonal info)

### Test Category: Edge Cases
**Test Scenarios:**
- Start/end points same (return simple path or single point)
- Unreachable points (on island with no bridges, in water) → handle gracefully
- Route box spanning multiple tiles (ensure continuity)
- Coordinate values at extreme ranges (Svalbard? Jan Mayen? Out of Norway?)

**Validation:**
```python
def test_edge_cases():
    # Same point
    assert generate_route((10.0, 60.0), (10.0, 60.0)) == [(10.0, 60.0)]

    # Out of Norway
    try:
        generate_route((0.0, 0.0), (0.0, 0.0))
    except ValueError as e:
        assert "out of bounds" in str(e)

    # Island with no bridges (should fail or flag)
    result = generate_route((5.5, 60.0), (5.5, 60.01))  # Small island
    assert result['status'] == 'no_path_found' or 'water_crossing' in result['warnings']
```

## Summary of Research Gaps

Based on this research, the following areas require phase-specific investigation:

1. **Kartverket API Documentation** (Phase 2): Need specific documentation on DTM download formats, rate limits, and available resolutions
2. **Performance Profiling** (Phase 2-3): Actual Python/DEM implementation will reveal real bottlenecks
3. **Norwegian Trail Validation Data** (Phase 4+): Source repository of validated GPX routes for testing
4. **Winter Routing Algorithms** (Future enhancement): Different routing parameters for snow conditions

The existing codebase provides strong foundations (Vector/Raster classes, pyproj integration) but lacks routing-specific components. The critical infrastructure (tile-based DEM loading, zone-safe coordinate handling) must be implemented in early phases to avoid costly refactoring.

---
*Research completed: 2026-04-12*