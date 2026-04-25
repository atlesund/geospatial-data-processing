---
gathered: 2026-04-24
status: Complete
---

# Phase 9: Water Crossing Detection Optimization - Research

## Problem Statement

The current `detect_water_crossing()` function in `routing_2026.py` (lines 441-500) uses naive iteration O(n×m):
- For each edge (~500,000): iterate through ALL lakes (~29,510) AND ALL rivers (~23,425)
- Total: ~26 billion geometry checks
- Result: System hang when water features are successfully retrieved (Phase 8 now retrieves all features)

## Solution: Spatial Indexing with shapely.strtree.STRtree

### Why Spatial Indexing Works

**Current (Naive):**
```
For each edge (500,000):
  For each lake (29,510): check if midpoint inside lake
  For each river (23,425): check if line intersects river
→ 26,000,000,000 checks
```

**With R-tree (STR - Sort-Tile-Recursive):**
```
Build R-tree index: O(m log m) once
For each edge (500,000):
  Query index → get nearby water features (typically 0-10)
  Check only those nearby features
→ 500,000 × ~5 = 2,500,000 checks
```

**Speedup:** ~10,000×

### shapely.strtree.STRtree API

```python
from shapely.strtree import STRtree

# 1. Build index (O(m log m), done once)
lake_geometries = lakes_gdf.geometry.values
river_geometries = rivers_gdf.geometry.values
lake_tree = STRtree(lake_geometries)
river_tree = STRtree(river_geometries)

# 2. Query index (O(log m + k) where k = results found)
nearby_lakes = lake_tree.query(point_or_line)
nearby_rivers = river_tree.query(line_string)

# 3. Check only nearby features
for lake in nearby_lakes:
    if point.within(lake):
        return lake_penalty
```

### Key Tech Details

**STRtree.query() behavior:**
- Returns all geometries that intersect the query geometry
- For point query: returns geometries containing the point (lakes)
- For line query: returns geometries intersecting the line (rivers)
- Result count depends on spatial proximity, not total dataset size

**Performance characteristics:**
- Build time: O(m log m) - done once before edge loop
- Query time: O(log m + k) where k = number of results
- Target: k is small (0-10) for realistic edge/water distribution

**Memory overhead:**
- Index stores the geometries and tree structure
- Roughly 2x memory of original geometries
- For 50k water features: manageable (few MB)

## Implementation Strategy

### Location: routing_2026.py

**Current function signature:**
```python
def detect_water_crossing(edge_start, edge_end, lakes_gdf, rivers_gdf,
                         lake_penalty=10.0, river_penalty=5.0, fjord_penalty=50.0):
```

**Approach 1: Build index inside detect_water_crossing (simple)**
- Build STRtree on first call, cache for subsequent calls
- Simple, single-function change
- Index built many times (once per edge in current usage pattern) - wasteful

**Approach 2: Build index outside, pass in (recommended)**
- Build index once in terrain_mesh_from_raster before edge loop
- Pass STRtree instances to detect_water_crossing
- Clean separation of concerns
- Most efficient

**Recommended: Approach 2**

### Code Changes Required

**1. Add index building in terrain_mesh_from_raster:**
```python
# After water query succeeds, build spatial indexes
if lakes_gdf is not None and len(lakes_gdf) > 0:
    from shapely.strtree import STRtree
    lake_tree = STRtree(lakes_gdf.geometry.values)
else:
    lake_tree = None

if rivers_gdf is not None and len(rivers_gdf) > 0:
    river_tree = STRtree(rivers_gdf.geometry.values)
else:
    river_tree = None
```

**2. Update detect_water_crossing signature and logic:**
```python
def detect_water_crossing(edge_start, edge_end, lake_tree, river_tree,
                         lake_penalty=10.0, river_penalty=5.0, fjord_penalty=50.0):
    # Calculate geometry
    midpoint = Point(((x1 + x2) / 2, (y1 + y2) / 2))
    edge_line = LineString([edge_start, edge_end])

    # Query lakes using index
    if lake_tree:
        nearby_lakes = lake_tree.query(midpoint)
        for lake in nearby_lakes:
            if midpoint.within(lake):
                return (lake_type, lake_penalty)

    # Query rivers using index
    if river_tree:
        nearby_rivers = river_tree.query(edge_line)
        for river in nearby_rivers:
            if edge_line.intersects(river):
                return (river, river_penalty)

    return (None, 1.0)
```

**3. Compatibility note:**
- STRtree is available in shapely 2.0+
- Project already imports shapely.geometry.Point, LineString
- No additional dependencies needed

## Validation Strategy

### Functional Equivalence Test

**Goal:** Prove indexed version produces identical results to naive version

**Method:**
1. Test with small dataset (100 lakes, 50 rivers, 1000 edges)
2. Run naive version, save all penalty results
3. Run indexed version, save all penalty results
4. Compare: must be identical

**Test approach:**
```python
# Simple test
for edge in test_edges:
    penalty_naive = detect_water_crossing_naive(...)
    penalty_indexed = detect_water_crossing_indexed(...)
    assert penalty_naive == penalty_indexed
```

### Performance Test

**Target:** Completes in <10 seconds for full raster dataset

**Profiling:**
```python
import time
start = time.time()
# Run with 500k edges, 30k lakes, 20k rivers
end = time.time()
print(f"Total time: {end - start}s")
```

**Success criteria:**
- Indexed version: <10s
- Naive version: would take hours/days (don't test)

## Known Pitfalls

1. **Empty GeoDataFrames:** Handle gracefully - STRtree with empty list raises ValueError
   - Check len() > 0 before building index
   - Pass None to detect_water_crossing if no water features

2. **Index cache invalidation:** If water features change between calls, must rebuild index
   - Current design: water features static during mesh generation
   - Safe to build once per terrain_mesh_from_raster call

3. **STRtree returns geometry only:** No attributes (like name for fjord classification)
   - GeoDataFrame is still needed for fjord name lookup
   - Use geometry to find index, then get row from GeoDataFrame

   **Workaround for fjord detection:**
   ```python
   # After finding nearby lake, get its attributes
   for idx, lake in enumerate(lake_geometries):
       if lake is matching_lake:
           name = lakes_gdf.iloc[idx]['name']
   ```

   **Better:** Use STRtree's return_indices parameter (if available) or map geometry back to DataFrame

4. **Performance cliff:** STRtree query is fast with nearby_pool_size < 50, degrades if index is bad
   - Default configuration should work for geographic data
   - If not, tune node_capacity parameter in STRtree constructor

## Alternative Approaches Considered

### Rtree (rtree package)
- Older library, ~deprecated in favor of shapely.strtree
- Requires pip install rtree + libspatialindex system dependency
- Reason: Not chosen - shapely.strtree is cleaner

### Geopandas spatial index sjoin
- Designed for dataset joins, not per-query lookups
- Would require restructuring data flow
- Reason: Not aligned with per-edge detection pattern

### Binary space partitioning (BSP)
- Great for static scenes with many queries
- Overkill for this use case
- Reason: STRtree is simpler and sufficient

## Dependencies

**Existing:**
- shapely (already imported in routing_2026.py)
- shapely.geometries.Point, LineString (already imported)

**New:**
- `from shapely.strtree import STRtree` (shapely 2.0+)

**Check:**
```bash
python -c "import shapely; print(shapely.__version__)"
# Must be 2.0.0 or higher
```

---

*Research: Complete - 2026-04-24*