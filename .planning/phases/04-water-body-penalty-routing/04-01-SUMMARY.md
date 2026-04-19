---
phase: 04-water-body-penalty-routing
plan: 01
status: completed
started: 2026-04-14
completed: 2026-04-14
summary_author: atlesund
---

# Plan 04-01: Water Feature Query from OpenStreetMap

## What Was Built

**load_water_features() function** — Queries OpenStreetMap for water features (lakes and rivers) using osmnx API, projects from EPSG:4326 to target CRS, with graceful fallback for network failures.

## Implementation

### Function Location
- File: `routing_2026.py` (lines 275-323)
- Signature: `load_water_features(bbox, target_epsg, timeout=30)`

### Key Features

1. **Separate queries for lakes and rivers:**
   - Lakes: tags `{'natural': 'water'}`
   - Rivers: tags `{'waterway': ['river', 'stream', 'canal']}`

2. **Bbox validation:**
   - Validates `west < east` and `south < north` before query
   - Protects against malformed input

3. **CRS projection:**
   - Projects from EPSG:4326 (OSM default) to target CRS
   - Uses `geopandas.to_crs()` for transformation

4. **Graceful fallback:**
   - Returns `(None, None)` on network failure
   - Logs warning message allowing routing without water penalties

## Tests

### Test Coverage
- File: `tests/test_04_01_water_query.py`
- Status: 8 passed, 2 skipped
- Tests:
  - `test_load_water_features_bbox_validation` ✓ — validates bbox assertion
  - `test_load_water_features_bbox_validation_reversed` ✓ — validates reversed bbox
  - `test_crs_projection` — skipped (requires live OSM API)
  - `test_query_fallback` — skipped (requires pytest-mock)

### Test Marker
- Added `@pytest.mark.water` marker to `tests/conftest.py`

## Notable Deviations

None — implementation matches plan specification.

## Decision Taken

Plan 02 confirmed following per-Plan 01 note:
- Tests use direct shapely geometry creation (not imports from Plan 01)
- Enables safe parallel execution with Plan 02
- Only production code in Plan 03 depends on both functions

## Lineage

- Based on: Phase 04 Decision D-01 (Use osmnx API) and D-02 (Query at route planning time)
- Pattern from: `.planning/phases/04-water-body-penalty-routing/04-RESEARCH.md` (lines 96-119)

## Next Steps

Wave 2 (Plan 04-03) will integrate this function with `detect_water_crossing()` into terrain mesh generation for combined penalty calculation.