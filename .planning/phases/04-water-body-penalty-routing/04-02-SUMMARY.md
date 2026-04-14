---
phase: 04-water-body-penalty-routing
plan: 02
status: completed
started: 2026-04-14
completed: 2026-04-14
summary_author: atlesund
---

# Plan 04-02: Water Crossing Detection

## What Was Built

**detect_water_crossing() function** — Detects water body crossings for terrain edges using geometry checks: point-in-polygon for lakes, line-intersection for rivers, with fjord classification via OSM name tag matching.

## Implementation

### Function Location
- File: `routing_2026.py` (lines 326-385)
- Signature: `detect_water_crossing(edge_start, edge_end, lakes_gdf, rivers_gdf, lake_penalty=10.0, river_penalty=5.0, fjord_penalty=50.0)`

### Key Features

1. **Lake detection (point-in-polygon):**
   - Calculates edge midpoint
   - Checks if midpoint is within lake polygon
   - Returns `('lake', 10.0)` penalty factor

2. **Fjord classification:**
   - Checks if `'fjord'` in lake name (case-insensitive)
   - Returns `('fjord', 50.0)` higher penalty factor

3. **River detection (line-intersection):**
   - Creates linestring from edge endpoints
   - Checks intersection with river linestring
   - Returns `('river', 5.0)` penalty factor

4. **Graceful fallback:**
   - Returns `(None, 1.0)` when both GeoDataFrames are None
   - Returns `(None, 1.0)` when no crossing detected

## Tests

### Test Coverage
- File: `tests/test_04_02_water_detection.py`
- Status: 6 passed
- Tests:
  - `test_lake_crossing_detection` ✓ — point-in-polygon detection
  - `test_fjord_classification` ✓ — name-based classification
  - `test_river_crossing_detection` ✓ — line-intersection detection
  - `test_no_crossing` ✓ — non-water edge handling
  - `test_no_water_data` ✓ — None input fallback
  - `test_edge_touching_lake_boundary` ✓ — boundary behavior

### Test Strategy
- Independent of Plan 01: tests create synthetic GeoDataFrames using shapely directly
- No imports from `load_water_features()` — enables safe parallel execution
- Uses pytest fixtures for mock data creation

## Notable Deviations

None — implementation matches plan specification.

## Decision Followed

Implemented per Phase 04 locked decisions:
- D-03: Multiplicative penalties (penalty factor calculated, multiplication handled in Plan 03)
- D-04: Point-in-polygon for lakes (using shapely Point.within())
- D-05: OSM tag classification for fjords (name substring matching)

## Lineage

- Based on: `.planning/phases/04-water-body-penalty-routing/04-RESEARCH.md` (lines 122-166)
- Pattern: Water Crossing Detection per Phase 4 research

## Next Steps

Wave 2 (Plan 04-03) will integrate detection with water query for combined terrain × water penalty calculation in terrain mesh edge creation.