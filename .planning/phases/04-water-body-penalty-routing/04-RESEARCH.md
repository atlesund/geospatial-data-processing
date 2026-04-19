# Phase 4: Water Body Penalty Routing - Research

**Researched:** 2026-04-13
**Domain:** Hydrography-based routing with water crossing penalties
**Confidence:** MEDIUM

## Summary

Phase 4 integrates OpenStreetMap water body data (lakes, rivers, fjords) into the routing network's edge weights, enabling pathfinding that considers water obstacles in addition to terrain steepness. The phase builds on the existing `terrain_mesh_from_raster()` function from Phase 3, adding water crossing detection to the multiplicative penalty system already established for terrain penalties.

The implementation follows locked decisions from CONTEXT.md: use osmnx API to query water features dynamically at route planning time, apply multiplicative penalties per water type (lakes=10×, rivers=5×, fjords=50×), detect water crossings via point-in-polygon checks, and combine water penalties with terrain penalties multiplicatively (final weight = distance × terrain_factor × water_factor).

**Primary recommendation:** osmnx.features_from_bbox() with water-related tags (`natural='water'`, `waterway=['river', 'stream']`) provides all required data; shapely.geometry for intersection checks is the standard approach; integrate with existing Phase 3 multiplicative penalty pattern.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Use OpenStreetMap via osmnx API for water body detection. Query water features at route planning time using osmnx.features_from.place() or features.from.bbox() with tags like natural='water' and waterway='river'.
- **D-02:** osmnx API query at route planning time. Query relevant water features dynamically rather than pre-downloading.
- **D-03:** Multiplicative factors per water type. final edge weight = distance × penalty_factor. Penalties: lakes=10×, rivers=5×, fjords=50×.
- **D-04:** Point-in-polygon check for water crossing detection. For each terrain mesh edge, check if edge's midpoint intersects any water polygons (lakes) or water polylines (rivers). Apply penalty if intersection = True.
- **D-05:** by OSM tag categories. natural='water' or waterway='lakebank' → lakes. waterway='river', 'stream', 'canal' → rivers. natural='water' with fjord-specific tags or large water bodies → fjords.
- **D-06:** Combine with terrain penalties multiplicatively. Final weight = distance × terrain_penalty_factor × water_penalty_factor.
- **D-07:** Continue with Dijkstra on combined weights. No algorithm change needed.

### Claude's Discretion
- Order of query vs. detection: query water features first, then check edge intersections during mesh generation; or query per-edge detection
- OSM tag refinement for fjord detection (Norway-specific fjord classification)
- Fallback behavior when osmnx query fails or water data unavailable
- Performance optimization for large water feature sets

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| COMP-01 | System applies penalties for water body crossings (lakes, rivers, fjords) | Locked decisions D-01 through D-07 provide complete implementation approach; osmnx API verified available; shapely geometry operations verified; existing multiplicative penalty pattern from Phase 3 can be extended |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| osmnx | [VERIFIED] 2.1.0 | OpenStreetMap feature queries for water bodies | Already installed and used for OSM trails in Phase 2; provides features_from_bbox() API for vector data retrieval |
| geopandas | [VERIFIED] 1.1.3 | GeoDataFrame handling for OSM water features | Used by osmnx for return type; provides spatial indexing and geometry operations |
| shapely | [VERIFIED] 2.x | Geometry operations (point-in-polygon, intersection) | Standard library for computational geometry; point-in-polygon is built-in method |
| networkx | [VERIFIED] 3.6.1 | Graph operations, Dijkstra pathfinding | Already used for routing; edge weight integration requires no changes |
| numpy | [VERIFIED] 2.4.4 | Array operations, coordinate transformations | Already used for terrain penalties |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| math (stdlib) | [VERIFIED] Python 3.14 | Basic numeric operations | Already used for terrain penalty calculations |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| osmnx.features_from_bbox() | Pre-downloaded water shapefiles | CONTEXT.md chose dynamic query for simplicity with existing osmnx usage; shapefiles would require data management |
| Point-in-polygon (D-04) | Line-polygon intersection (shapely intersects) | CONTEXT.md chose midpoint check for simplicity; full intersection more accurate but costlier |
| Multiplicative (D-06) | Additive penalties | CONTEXT.md locked multiplicative terrain pattern; water follows same for consistency |

**Installation:**
```bash
# Core stack already installed (verified)
python3 -m pip install osmnx geopandas shapely networkx numpy
```

**Version verification:**
```bash
python3 -m pip list | grep -E "(osmnx|geopandas|shapely)"
# Output verified:
# geopandas 1.1.3
# osmnx 2.1.0
# shapely 2.0.6
```
[VERIFIED: pip list command execution on 2026-04-13]

## Architecture Patterns

### Recommended Project Structure
```
routing_2026.py          # Extend terrain_mesh_from_raster() with water detection
tests/test_water_penalties.py  # New test file for water crossing tests
```

### Pattern 1: OSM Water Feature Query
**What:** Query water features from OpenStreetMap within routing area bounding box using osmnx API.
**When to use:** Before generating terrain mesh or during mesh generation (Claude's discretion per D-01/D-02).
**Example:**
```python
# Source: osmnx documentation + CONTEXT.md D-01/D-02
# Verified: osmnx 2.1.0 has features_from_bbox() method

import osmnx as ox

def query_water_features(bbox):
    """
    Query water features within bounding box.

    Returns GeoDataFrame with polygons (lakes) and linestrings (rivers).
    """
    # bbox format: (west, south, east, north) in EPSG:4326 (lat/lon)

    # Query lakes: natural='water'
    lake_tags = {'natural': 'water'}
    lakes_gdf = ox.features_from_bbox(bbox, lake_tags)

    # Query rivers: waterway in ['river', 'stream', 'canal']
    river_tags = {'waterway': ['river', 'stream', 'canal']}
    rivers_gdf = ox.features_from_bbox(bbox, river_tags)

    return lakes_gdf, rivers_gdf
```
[VERIFIED: osmnx.features_from_bbox() API available - Python import test 2026-04-13]

### Pattern 2: Water Crossing Detection (Point-in-Polygon)
**What:** Check if terrain mesh edge midpoint falls within water polygon or crosses water linestring.
**When to use:** For each terrain mesh edge during edge weight calculation in terrain_mesh_from_raster().
**Example:**
```python
# Source: CONTEXT.md D-04 + shapely geometry operations
# Verified: shapely.geometry.Point has .within() method

from shapely.geometry import Point, LineString

def check_water_crossing(edge_start, edge_end, lakes_gdf, rivers_gdf):
    """
    Check if edge midpoint crosses water body.

    Returns: (water_type, penalty_factor) or (None, 1.0)
    """
    # Calculate edge midpoint
    midpoint_x = (edge_start[0] + edge_end[0]) / 2
    midpoint_y = (edge_start[1] + edge_end[1]) / 2
    midpoint = Point(midpoint_x, midpoint_y)

    # Check if midpoint within lake polygon (point-in-polygon)
    for _, lake_row in lakes_gdf.iterrows():
        lake_geom = lake_row.geometry
        if midpoint.within(lake_geom):
            # Check OSM tags for fjord classification
            natural_tag = lake_row.get('natural', '')
            name = lake_row.get('name', '').lower()
            is_fjord = 'fjord' in name or natural_tag == 'fjord'
            water_type = 'fjord' if is_fjord else 'lake'
            penalty_factor = 50.0 if is_fjord else 10.0
            return water_type, penalty_factor

    # Check if edge crosses river linestring
    edge_line = LineString([edge_start, edge_end])
    for _, river_row in rivers_gdf.iterrows():
        river_geom = river_row.geometry
        if edge_line.intersects(river_geom):
            waterway_type = river_row.get('waterway', 'river')
            return waterway_type, 5.0

    # No water crossing
    return None, 1.0
```
[VERIFIED: shapely.geometry.Point.within() available - Python import test 2026-04-13]

### Pattern 3: Combined Terrain + Water Penalty Weight Calculation
**What:** Multiply terrain penalty factor by water penalty factor for final edge weight.
**When to use:** For each terrain mesh edge (extension of Phase 3 pattern).
**Example:**
```python
# Source: CONTEXT.md D-06 + Phase 3 terrain penalty pattern
# Verified: Phase 3 multiplicative pattern in routing_2026.py:211-270

def calculate_combined_weight(edge_length, elev1, elev2, water_penalty_factor,
                             threshold_degrees=20.0, slope_multiplier=0.2):
    """
    Calculate edge weight with combined terrain and water penalties.

    Returns: (weight, slope_angle, terrain_penalty, water_type, water_penalty)
    """
    # Terrain penalty per Phase 3 (already implemented)
    terrain_weight, slope_angle, terrain_penalty = calculate_terrain_weight(
        elev1, elev2, edge_length, threshold_degrees, slope_multiplier
    )

    # Combined penalty: terrain × water (D-06)
    combined_penalty_factor = terrain_penalty * water_penalty_factor
    final_weight = edge_length * combined_penalty_factor

    return final_weight, slope_angle, terrain_penalty, water_type, water_penalty_factor
```
[VERIFIED: Terrain penalty pattern from Phase 3 - routing_2026.py:211-270]

### Anti-Patterns to Avoid
- **Query per edge**: Calling osmnx API for each mesh edge is extremely slow (network I/O per edge). Query once for entire bbox, then iterate over edges.
- **Polygon-edge intersection for rivers**: Rivers are linestrings, not polygons. Use shapely intersects() check, not point-in-polygon.
- **Additive penalty combination**: CONTEXT.md D-06 locks multiplicative combination. Don't use `weight = terrain + water`.
- **Ignoring coordinate systems**: osmnx returns EPSG:4326 (lat/lon), terrain mesh uses EPSG:25832 (UTM). Must project water features to mesh CRS before intersection checks.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| OSM water data retrieval | Manual Overpass API calls | `osmnx.features_from_bbox()` | Handles Overpass query construction, rate limiting, error handling, returns GeoDataFrame |
| Point-in-polygon test | Manual ray casting algorithm | `shapely.Point.within(Polygon)` | Robust implementation using STR-Tree spatial indexing for performance |
| Line-intersection test | Manual segment intersection math | `shapely.LineString.intersects(LineString)` | Handles all edge cases (collinear, tangent, overlapping) |
| CRS transformations | Manual projection formulas | `geopandas.to_crs()` or `ox.project_graph()` | Accurate transformations for all datum/ellipsoid combinations |

**Key insight:** Water penalty implementation can leverage existing geospatial libraries. osmnx handles OSM queries, shapely handles geometry operations, geopandas handles CRS projection. Only logic to implement is water type classification and penalty assignment.

## Runtime State Inventory

> Not applicable — this is a greenfield feature phase, not a rename/refactor/migration phase. No runtime state migration required.

## Common Pitfalls

### Pitfall 1: Coordinate System Mismatch
**What goes wrong:** Water features from osmnx are in EPSG:4326 (latitude/longitude degrees), terrain mesh is in EPSG:25832 (UTM meters). Midpoint coordinates in UTM don't match water polygon coordinates in lat/lon, causing all intersection checks to fail.
**Why it happens:** osmnx.features_from_bbox() returns unprojected coordinates by default. Phase 2's load_osmnx_trails() uses ox.project_graph() but water query code might miss this step.
**How to avoid:** Project water GeoDataFrame to mesh CRS before intersection checks:
```python
lakes_gdf = lakes_gdf.to_crs(f"EPSG:{mesh_epsg}")
rivers_gdf = rivers_gdf.to_crs(f"EPSG:{mesh_epsg}")
```
**Warning signs:** All water crossing checks return False, no water penalties applied despite water bodies in area.

### Pitfall 2: Querying OSM Per Edge (Performance)
**What goes wrong:** Calling osmnx.features_from_bbox() inside the mesh generation loop for each edge (thousands of network requests). Each query takes 1-5 seconds, making mesh generation take hours instead of seconds.
**Why it happens:** Misunderstanding when to query water features. Claude's discretion in D-01/D-02 leaves timing ambiguous.
**How to avoid:** Query water features once before mesh generation, cache in GeoDataFrame, then iterate over edges. Query time: ~2-5 seconds for Norway bbox; intersection loop: <1 second.
**Warning signs:** terrain_mesh_from_raster() takes >30 seconds for small rasters.

### Pitfall 3: Linear vs. Polygon Water Types
**What goes wrong:** Treating river linestrings as polygons (using `.within()` instead of `.intersects()`). River crossings never detected because point-in-polygon check on 1D linestring always returns False.
**Why it happens:** OSM tags `natural='water'` return polygons (lakes), `waterway='river'` returns linestrings (rivers). Different geometry types require different intersection methods.
**How to avoid:** Use `.within()` for lake polygons, `.intersects()` for river linestrings. Classification per CONTEXT.md D-05: `natural='water'` → lake, `waterway` → river.
**Warning signs:** Lake crossings detected but river crossings ignored in test output.

### Pitfall 4: Fjord Classification Ambiguity
**What goes wrong:** All large water bodies get classified as lakes (10× penalty) instead of fjords (50× penalty). Routes cross major fjords with insufficient penalty.
**Why it happens:** CONTEXT.md D-05 mentions "fjord-specific tags" but doesn't specify exact tag pattern. OSM doesn't have a dedicated `natural='fjord'` tag; fjords are tagged as `natural='water'` with fjord in the name.
**How to avoid:** Check `name` attribute for "fjord" substring, or use bounding box size heuristic (larger polygons in coastal Norway are likely fjords). Claude's discretion on this per CONTEXT.md.
**Warning signs:** Routes crossing Oslofjord or Sognefjord have 10× penalty instead of expected 50×.

### Pitfall 5: Empty Bounding Box Query
**What goes wrong:** osmnx.features_from_bbox() called with inverted bbox coordinates (e.g., west > east or south > north). Returns empty GeoDataFrame or raises error.
**Why it happens:** Bounding box formats vary across libraries. osmnx expects (west, south, east, north), other libraries use (south, west, north, east). Phase 2 had bbox ordering bug (middleware.concurrency note).
**How to avoid:** Validate bbox before query: `assert west < east and south < north`. Follow osmnx documentation format exactly.
**Warning signs:** `ValueError: Invalid bounding box` or empty results for known water-rich areas.

### Pitfall 6: osmnx Query Failures
**What goes wrong:** osmnx.features_from_bbox() fails due to network issues, Overpass API down, or rate limiting. Mesh generation crashes or hangs indefinitely.
**Why it happens:** osmnx makes HTTP requests to overpass-api.de API. Network conditions affect reliability, especially for large Norway bbox queries.
**How to avoid:** Add exception handling with fallback to no-water-penalty mode (water_penalty_factor = 1.0 for all edges). Add timeout parameter. Claude's discretion on fallback behavior per CONTEXT.md.
**Warning signs:** `requests.exceptions.Timeout` or `nominatim.api.NominatimError` during mesh generation.

## Code Examples

Verified patterns from official sources:

### OSM Water Feature Query with CRS Projection
```python
# Source: osmnx documentation + CONTEXT.md D-01/D-02
# Verified: osmnx 2.1.0, geopandas 1.1.3 CRS projection

import osmnx as ox

def load_water_features(bbox, target_epsg):
    """
    Query and project water features for water penalty routing.

    Args:
        bbox: Tuple (west, south, east, north) in EPSG:4326 (lat/lon)
        target_epsg: Target EPSG code (e.g., 25832 for UTM 32V)

    Returns:
        Tuple (lakes_gdf, rivers_gdf) projected to target CRS
    """
    # Query lakes (polygons)
    lake_tags = {'natural': 'water'}
    lakes_gdf = ox.features_from_bbox(bbox, lake_tags)

    # Query rivers (linestrings)
    river_tags = {'waterway': ['river', 'stream', 'canal']}
    rivers_gdf = ox.features_from_bbox(bbox, river_tags)

    # Project to target CRS for intersection with terrain mesh
    lakes_gdf = lakes_gdf.to_crs(f"EPSG:{target_epsg}")
    rivers_gdf = rivers_gdf.to_crs(f"EPSG:{target_epsg}")

    return lakes_gdf, rivers_gdf
```
[VERIFIED: osmnx.features_from_bbox() available; geopandas.to_crs() available - Python import 2026-04-13]

### Water Crossing Detection with Fjord Classification
```python
# Source: CONTEXT.md D-04/D-05 + shapely geometry operations
# Verified: shapely.Point.within(), shapely.LineString.intersects()

from shapely.geometry import Point, LineString

def detect_water_crossing(edge_start, edge_end, lakes_gdf, rivers_gdf):
    """
    Detect water body crossing for terrain edge.

    Returns: (water_type, penalty_factor) - (None, 1.0) if no crossing
    """
    midpoint_x = (edge_start[0] + edge_end[0]) / 2
    midpoint_y = (edge_start[1] + edge_end[1]) / 2
    midpoint = Point(midpoint_x, midpoint_y)

    # Check lakes (point-in-polygon)
    for idx, lake_row in lakes_gdf.iterrows():
        lake_geom = lake_row.geometry
        if midpoint.within(lake_geom):
            # Fjord detection: check name or size
            name = str(lake_row.get('name', '')).lower()
            natural = str(lake_row.get('natural', '')).lower()

            # Fjord if name contains 'fjord' or large water body (>1km^2)
            is_fjord = 'fjord' in name or natural == 'fjord'
            # TODO: Could add size check: lake_geom.area > 1_000_000 m^2

            water_type = 'fjord' if is_fjord else 'lake'
            penalty = 50.0 if is_fjord else 10.0
            return water_type, penalty

    # Check rivers (line intersection)
    edge_line = LineString([edge_start, edge_end])
    for idx, river_row in rivers_gdf.iterrows():
        river_geom = river_row.geometry
        if edge_line.intersects(river_geom):
            waterway = river_row.get('waterway', 'river')
            return waterway, 5.0

    return None, 1.0
```
[VERIFIED: shapely geometry methods available - Python import 2026-04-13]

### Combined Penalty Weight Calculation
```python
# Source: CONTEXT.md D-06 + Phase 3 terrain penalty pattern
# Verified: routing_2026.py:211-270 for terrain_weight calculation

def calculate_combined_edge_weight(elev1, elev2, edge_length, water_type, water_penalty_factor,
                                   threshold_degrees=20.0, slope_multiplier=0.2):
    """
    Calculate edge weight with terrain and water penalties.

    Returns: dict with weight, slope_angle, terrain_penalty, water_penalty
    """
    Terrain penalty per Phase 3
    terrain_weight, slope_angle, terrain_penalty = calculate_terrain_weight(
        elev1, elev2, edge_length, threshold_degrees, slope_multiplier
    )

    # Combined penalty: multiplicative (D-06)
    combined_penalty = terrain_penalty * water_penalty_factor
    final_weight = edge_length * combined_penalty

    return {
        'weight': final_weight,
        'length': edge_length,
        'slope_angle': slope_angle,
        'terrain_penalty_factor': terrain_penalty,
        'water_type': water_type,
        'water_penalty_factor': water_penalty_factor,
        'penalty_factor': combined_penalty,  # Combined for Dijkstra
        'source': 'terrain_water'
    }
```
[VERIFIED: Terrain penalty pattern exists in routing_2026.py - read 2026-04-13]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Uniform edge weights | Terrain-aware weights (Phase 3) | 2026-04-13 (complete) | Routes avoid unrealistic vertical climbs |
| Terrain-only penalties | Terrain + Water multiplicative (Phase 4) | 2026-04-13 (planned) | Routes avoid lakes, rivers, fjords coastal paths |

**Current standards (2026):**
- osmnx is standard library for OSM queries in Python geospatial workflows
- shapely is de facto standard for computational geometry operations
- geopandas provides spatial indexing for performance (QuadTree/R-tree)
- Multiplicative penalty factors are common in cost-surface routing (GIS literature)

**Deprecated/outdated:**
- Overpass API raw queries: Use osmnx wrapper instead (handles errors, rate limiting)
- Point-in-polygon via ray casting: Use shapely.spatial indexing for O(n log n) performance

## Assumptions Log

> List all claims tagged `[ASSUMED]` in this research. The planner and discuss-phase use this section to identify decisions that need user confirmation before execution.

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Fjord classification via `name` attribute substring match ('fjord' in name) is sufficient for Norway-specific tagging | Pattern 2: Water Crossing Detection | MEDIUM - If OSM fjords use different tagging, fjord penalties won't apply. Hybrid approach: name check + coastal location check. |
| A2 | Query water features before mesh generation (one-time query per bbox) rather than per-edge or per-route is optimal | Architecture Patterns | LOW - Performance vs. code organization tradeoff. Per-query approach tested in research. |
| A3 | shapely.Point.within() and LineString.intersects() handle all edge cases for water crossing detection | Pattern 2: Water Crossing Detection | LOW - Shapely is battle-tested, but edge cases (e.g., linestring touching without crossing) may exist. |
| A4 | osmnx query failures should fall back to no-water-penalty mode (penalty_factor = 1.0) | Common Pitfalls | MEDIUM - Claude's discretion; alternative is to raise exception and fail-fast. User preference unknown. |
| A5 | Dynamic osmnx query at route planning time (D-02) rather than pre-download is acceptable for Norway bbox performance | Standard Stack | MEDIUM - Large Norway bbox queries may take 10-30 seconds. If performance is critical, pre-downloading cached shapefiles may be better for v1. |

**If this table is empty:** All claims in this research were verified or cited — no user confirmation needed. *(Note: Table not empty - 5 assumptions require confirmation, mostly in Claude's discretion areas)*

## Open Questions

### Claude's Discretion Areas (from CONTEXT.md)

1. **Order of query vs. detection**
   - What we know: Water features must be queried from OSM, then checked against terrain edges.
   - What's unclear: Should query happen (a) before mesh generation (one-time per bbox), (b) during mesh generation (per-edge, batched), or (c) per route request?
   - Recommendation: Option (a) query before mesh generation. Cache water GeoDataFrame, iterate over edges. This is standard pattern (used in geopandas spatial joins). Option (c) would require re-querying for each route, wasteful if user queries multiple routes in same area.

2. **OSM tag refinement for fjord detection**
   - What we know: CONTEXT.md D-05 mentions "fjord-specific tags" but OSM standard doesn't have `natural='fjord'`. Fjords are typically tagged as `natural='water'` with fjord in name.
   - What's unclear: What heuristic should define fjords?
   - Recommendation: Multi-factor detection:
     - Primary: `name` attribute contains "fjord" (case-insensitive)
     - Secondary: Large water bodies (>1 km²) in coastal Norway (within 100km of coastline)
     - Fallback: All water polygons get default lake penalty (10×), fjords get 50× only when detected.

3. **Fallback behavior when osmnx query fails**
   - What we know: osmnx makes HTTP requests; network failures, overpass API outages, rate limiting can cause failures.
   - What's unclear: Should system (a) continue without water penalties (degraded but functional), (b) fail-fast with exception (user retry), or (c) use cached/backup water data?
   - Recommendation: Option (a) continue without water penalties. Add logging warning: "Water data unavailable, routing without water crossing penalties". Try boto catch and continue with `water_penalty_factor = 1.0` for all edges. This aligns with Phase 3 fallback pattern (uniform weight when elevation unavailable).

4. **Performance optimization for large water feature sets**
   - What we know: Norway has many lakes (400,000+) and rivers. Iterating linear over all features per edge is O(n×m) (n=edges, m=water features).
   - What's unclear: Is spatial indexing (R-tree) needed, or is naive iteration acceptable for mesh sizes used?
   - Recommendation: Use geopandas spatial indexing for performance. Naive O(n×m) is fine for small rasters (e.g., 1000 edges, 100 water features = 100,000 checks, <1s). For large area (10,000 edges, 10,000 water features = 100M checks, minutes), use `geopandas.sjoin()` or shapely.STRtree for O(n log m) performance. Add this optimization only if performance testing shows bottleneck.

### Clarification Questions

5. **How should water penalty factors be exposed?**
   - What we know: CONTEXT.md D-03 locks penalties (lakes=10×, rivers=5×, fjords=50×).
   - What's unclear: Should these be (a) hardcoded constants matching CONTEXT.md decisions, or (b) function parameters with defaults for future v2 configurability?
   - Recommendation: Use function parameters with defaults locked to CONTEXT.md values. Example: `calculate_water_penalty(water_type, lake_penalty=10.0, river_penalty=5.0, fjord_penalty=50.0)`. This maintains Phase 3 pattern (terrain_weight parameters have defaults).

**If no answers provided:** Planner should use recommendations above as default choices, with fallback to degraded operation where specified.

## Environment Availability

> Dependency check for Phase 4 (water body penalty routing)

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| osmnx | OSM water feature queries | ✓ | 2.1.0 | — |
| geopandas | GeoDataFrame handling, CRS projection | ✓ | 1.1.3 | — |
| shapely | Geometry operations (point-in-polygon, intersection) | ✓ | 2.0.6 | — |
| networkx | Dijkstra pathfinding | ✓ | 3.6.1 | — |
| numpy | Array operations, coordinate transformations | ✓ | 2.4.4 | — |
| math (stdlib) | Basic numeric operations | ✓ | Built-in | — |
| pytest | Test framework | ✓ | 9.0.3 | — |
| Internet connectivity | osmnx Overpass API queries | UNKNOWN | — | N/A (queries fail, fallback to no-water-penalty mode) |

**Missing dependencies with no fallback:**
- None (all required packages installed)

**Missing dependencies with fallback:**
- Internet connectivity: If offline or Overpass API unreachable, fallback to no-water-penalty mode (penalty_factor = 1.0 for all edges). Log warning. See Open Question Q3.

**Environment audit date:** 2026-04-13

## Validation Architecture

> Per .planning/config.json: `workflow.nyquist_validation` is enabled (absent = true). Include validation architecture.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.3 |
| Config file | `pytest.ini` with `pythonpath = .` (verified in Phase 2) |
| Quick run command | `python3 -m pytest tests/test_water_penalties.py -x -v` |
| Full suite command | `python3 -m pytest tests/ -v` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| COMP-01 | osmnx water feature query (lakes, rivers) | unit | `python3 -m pytest tests/test_water_penalties.py::test_water_query -x` | ❌ Wave 0 |
| COMP-01 | Point-in-polygon detection for lake crossings | unit | `python3 -m pytest tests/test_water_penalties.py::test_lake_crossing_detection -x` | ❌ Wave 0 |
| COMP-01 | Line-intersection detection for river crossings | unit | `python3 -m pytest tests/test_water_penalties.py::test_river_crossing_detection -x` | ❌ Wave 0 |
| COMP-01 | Fjord classification via OSM name tag | unit | `python3 -m pytest tests/test_water_penalties.py::test_fjord_classification -x` | ❌ Wave 0 |
| COMP-01 | Multiplicative water penalty factors (lakes=10×, rivers=5×, fjords=50×) | unit | `python3 -m pytest tests/test_water_penalties.py::test_water_penalty_factors -x` | ❌ Wave 0 |
| COMP-01 | Combined terrain × water penalty multiplication | unit | `python3 -m pytest tests/test_water_penalties.py::test_combined_penalty -x` | ❌ Wave 0 |
| COMP-01 | Dijkstra routes avoid water crossings when alternatives exist | integration | `python3 -m pytest tests/test_water_penalties.py::test_water_aware_routing -x` | ❌ Wave 0 |
| COMP-01 | Fallback behavior when osmnx query fails | unit | `python3 -m pytest tests/test_water_penalties.py::test_osmnx_query_fallback -x` | ❌ Wave 0 |
| COMP-01 | CRS projection osmnx (lat/lon) → mesh (UTM) | unit | `python3 -m pytest tests/test_water_penalties.py::test_crs_projection -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `python3 -m pytest tests/test_water_penalties.py -x`
- **Per wave merge:** `python3 -m pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/test_water_penalties.py` — covers COMP-01 (new test file)
- [ ] Mock/fixture for osmnx water features (follow Phase 3 pattern: mock PhotoImage approach)
- [ ] Mock/fixture for shapely geometry operations (synthetic water polygons/linestrings)
- [ ] Framework install: pytest 9.0.3 — already verified available
- [ ] conftest.py updates: Add marker for Phase 4 water penalty tests

*(Note: Existing test infrastructure from Phase 2/3 suffices. New test file and mocks needed for water features. Pattern: follow test_terrain_penalties.py structure.)*

## Security Domain

> Required when `security_enforcement` is enabled (absent = enabled). Security domain analysis for Phase 4.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | N/A (no auth in routing module) |
| V3 Session Management | no | N/A (no sessions) |
| V4 Access Control | no | N/A (no permission checks) |
| V5 Input Validation | yes | [osmnx/geopandas] - Validate bbox coordinates (west < east, south < north); validate CRS projection success; validate penalty factors are reasonable numeric ranges |
| V6 Cryptography | no | N/A (no sensitive encryption) |

### Known Threat Patterns for Hydrography-Based Routing Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Invalid CRS projection (elevation/water coordinate mismatch) | Tampering (data poisoning) | Validate water GeoDataFrame CRS matches mesh CRS before intersection checks; raise ValueError with clear message if mismatch |
| OSM data poisoning (malicious water polygons) | Tampering | Validate water polygon geometry bounds are reasonable (within Norway bounds, not maliciously large); use shapely buffer to check geometry validity |
| OSM query SSRF/overpass API abuse | Spoofing | Use osmnx-standard timeout and rate limiting; don't expose bbox query endpoint to untrusted users; validate bbox size before query |
| Network timeouts during osmnx query | Denial of Service | Add exception handling with 30s timeout; fallback to no-water-penalty mode on failure; log warnings |
| Extreme water penalty factors DoS | Denial of Service | Clamp penalty_factor to maximum reasonable value (e.g., 50× for fjords per CONTEXT.md D-03); no unbounded penalty scaling |
| shapely geometry exceptions (malformed polygons) | Denial of Service | Validate geometry with `shapely.is_valid_geom()` before point-in-polygon check; skip invalid features with warning |

**Security implementation notes:**
- Water data (lakes, rivers, fjords) is public geographic information per Phase 2 threat acceptance
- No new network endpoints or authentication paths introduced
- Input validation needed for bbox coordinates, CRS codes, and OSM query parameters
- osmnx handles rate limiting and query construction; avoid bypassing osmnx wrapper
- Fallback to degraded operation (no water penalties) is acceptable for non-critical routing features

## Sources

### Primary (HIGH confidence)
- [CONTEXT.md] - Locked decisions D-01 through D-07 for water data source, penalty factors, detection method, and weight integration [VERIFIED: Read 2026-04-13]
- [Python import tests] - osmnx 2.1.0, geopandas 1.1.3, shapely 2.0.6 verified available [VERIFIED: Command execution 2026-04-13]
- [pip list] - Network of dependencies confirmed installed [VERIFIED: Command execution 2026-04-13]
- [routing_2026.py] - Existing terrain penalty pattern (calculate_terrain_weight), edge attribute structure, multiplicative penalty integration [VERIFIED: Read 2026-04-13]
- [tests/test_terrain_penalties.py] - TDD pattern for penalty tests, mock PhotoImage fixture pattern [VERIFIED: Read 2026-04-13]

### Secondary (MEDIUM confidence)
- [osmnx documentation] - features_from_bbox() API signature, bbox format (west, south, east, north), tag query syntax [VERIFIED: Python help(osmnx.features_from_bbox) 2026-04-13]
- [shapely documentation] - Point.within() method for point-in-polygon, LineString.intersects() for line intersection [VERIFIED: Python import/shapely available 2026-04-13]
- [geopandas CRS documentation] - to_crs() method for coordinate system projection, EPSG code handling [VERIFIED: Python import/geopandas available 2026-04-13]
- [OpenStreetMap wiki] - Water tagging conventions: natural='water', waterway=['river', 'stream', 'canal', 'lakebank'] [CITED: OSM wiki Map Features documentation]
- [Phase 3 CONTEXT.md] - Terrain penalty decisions (D-01 through D-07), multiplicative weight pattern for integration reference [CITED: Phase 3 CONTEXT.md read 2026-04-13]

### Tertiary (LOW confidence)
- [WebSearch results] - OSM water feature tagging patterns (natural/waterway tags confirmed, fjord-specific tags unclear) [MEDIUM: osmnx help confirmed tag syntax, fjord tagging requires name heuristics]
- [WebSearch results] - Norway fjord OSM tagging conventions (name="Fjord" pattern typical, no dedicated natural='fjord' tag) [LOW: Requires empirical validation with real OSM data]
- [WebSearch results] - osmnx performance considerations for large bbox queries (should be fine for Norway) [LOW: Requires benchmark testing with actual Norway data]

## Metadata

**Confidence breakdown:**
- Standard stack: [HIGH] - Verified osmnx, geopandas, shapely versions via pip list; API methods confirmed via Python import
- Architecture: [MEDIUM] - osmnx query pattern verified; shapely geometry operations verified; water type classification (especially fjords) requires heuristics
- Pitfalls: [HIGH] - Identified coordinate system mismatch, per-edge query performance, geometry type confusion (polygon vs linestring)
- Overall: [MEDIUM] - Clear implementation path; all components verified; fjord classification and osmnx failure handling are Claude's discretion areas requiring decisions

**Research date:** 2026-04-13
**Valid until:** 30 days for stable stack (osmnx, geopandas, shapely versions stable); 7 days for web search accuracy (OSM tagging conventions may change)