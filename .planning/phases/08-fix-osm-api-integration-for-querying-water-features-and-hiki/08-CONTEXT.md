# Phase 08: Fix OSM API integration for querying water features - Context

**Gathered:** 2026-04-24
**Status:** Ready for planning

## Phase Boundary

Fix the bug where OSM API queries for water features fail or timeout when `enable_water_queries=True` because the query area is too large. The `terrain_mesh_from_raster` function calculates bbox from the full raster extent (up to 182km × 108km for Kartverket tiles), which exceeds OSM overpass API timeout limits (180 seconds).

**Root cause:** `bbox_local` is calculated from ALL node coordinates (lines 466-469 in routing_2026.py), not from the optional `bbox` parameter (which is currently ignored).

**Goal:** Enable successful water feature queries for entire raster areas by implementing automatic bbox splitting into manageable chunks, merging results, and processing failures appropriately.

## Implementation Decisions

### Bbox Splitting Strategy
- **D-01:** Use fixed grid splitting with 2x2 grid (4 tiles) — simple, predictable, easy to debug
- **D-02:** Query each tile sequentially using existing `load_water_features` function
- **D-03:** Combine all tile results into single merged GeoDataFrame for lakes and rivers separately

### Failure Handling
- **D-04:** Fail entire query if any single chunk times out — prefer consistency over partial results

### Function Placement
- **D-05:** Create new tiled function `load_water_features_tiled(bbox, target_epsg, grid_size=(2,2))` — maintains backward compatibility by keeping existing `load_water_features` unchanged

### Coverage Requirement
- **D-06:** Must query full water features for entire raster area — not fallback to subset or greater bbox

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Debug Context
- `.planning/debug/water-query-bbox-issue.md` — Full investigation of the OSM timeout issue with bbox size analysis
- `test_water_query_debug.py` — Test script demonstrating the problem with full raster queries

### Source Code
- `routing_2026.py:399-576` — `terrain_mesh_from_raster` function (water query logic at lines 466-491)
- `routing_2026.py:280-335` — `load_water_features` function (current OSM query implementation)
- `routing_2026.py:337-397` — `detect_water_crossing` function (consumes water query results)

### Project Context
- `.planning/ROADMAP.md` — Phase 8 definition and dependencies
- `.planning/REQUIREMENTS.md` — COMP-01: water body crossing penalties
- `.planning/codebase/INTEGRATIONS.md` — OpenStreetMap (OSM) integration details

## Existing Code Insights

### Reusable Assets
- `load_water_features(bbox, target_epsg, timeout=30)` — Existing OSM query function (lines 280-335)
- Uses `osmnx.features_from_bbox()` for queries
- Returns tuple (lakes_gdf, rivers_gdf) as GeoDataFrames projected to target CRS
- Has 180-second timeout via `ox.settings.requests_timeout` setting
- Returns (None, None) on failure with warning message

### Established Patterns
- CRS conversion using `pyproj.Transformer.from_crs()` (line 478)
- Bbox format: (west, south, east, north) in EPSG:4326 for osmnx queries
- Error handling with try-except returning None and printing warning
- Project to target CRS after query: `.to_crs(f"EPSG:{target_epsg}")`

### Integration Points
- `terrain_mesh_from_raster` calls `load_water_features` at line 484
- Water query results passed to `detect_water_crossing` for edge penalty calculation
- Lakes and rivers handled separately (different geometry types, different penalties)

## Specific Ideas

- 2x2 grid means: split bbox into four quadrants (NW, NE, SW, SE)
- Tile splitting logic needs to work in both EPSG:4326 (for OSM queries) and local CRS
- Progress logging helpful during multi-tile queries (e.g., "Querying tile 1/4...")
- Tile size calculation: tile_width = (east - west) / 2, tile_height = (north - south) / 2

## Deferred Ideas

None — discussion stayed within phase scope.

---

*Phase: 08-fix-osm-api-integration-for-querying-water-features*
*Context gathered: 2026-04-24*