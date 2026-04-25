---
wave: 1
depends_on: []
files_modified:
  - routing_2026.py
autonomous: false
---

# Phase 08: Fix OSM API Timeout for Water Feature Queries - PLAN

## Overview

Fix the bug where OSM API queries for water features fail when `enable_water_queries=True` because the query area (full raster extent up to 182km × 108km) exceeds OSM overpass API timeout limits. Implement automatic bbox splitting into manageable chunks to enable successful queries over full raster areas.

## Root Cause

From debug investigation (`.planning/debug/water-query-bbox-issue.md`):
- `bbox_local` is calculated from ALL mesh node coordinates (lines 466-469 in routing_2026.py)
- Full Kartverket dtm50 raster extent: 182.6km × 108.9km (1.61 sq degrees)
- This area causes OSM API timeouts (30-180 second limits)
- The optional `bbox` parameter exists but is ignored for water queries

## Solution Strategy

Per CONTEXT.md decisions D-01 through D-06:
- **D-01**: Use fixed 2x2 grid splitting (4 tiles)
- **D-02**: Query each tile sequentially using existing `load_water_features`
- **D-03**: Merge all tile results into single GeoDataFrames
- **D-04**: Fail entire query if any tile times out (prefer consistency)
- **D-05**: Create new `load_water_features_tiled` function (maintain backward compatibility)
- **D-06**: Query full water features for entire raster area (no subset fallback)

## Plans

### Plan 08-01: Create bbox splitting utility function
**File:** `08-01-PLAN.md`

Create `split_bbox(bbox, grid_size=(2,2))` function that splits a bounding box into rectangular grid tiles. This is the foundational utility for tiled querying.

**Key deliverables:**
- `split_bbox` function in routing_2026.py (line ~279)
- Returns list of 4 bbox tuples for 2x2 grid (NW, NE, SW, SE quadrants)
- Tile dimensions calculated as `(east - west) / cols` and `(north - south) / rows`

### Plan 08-02: Create tiled water feature loader
**File:** `08-02-PLAN.md`

Create `load_water_features_tiled(bbox, target_epsg, grid_size=(2,2), timeout=30)` function that queries each tile separately and merges results.

**Key deliverables:**
- `load_water_features_tiled` function in routing_2026.py (line ~335)
- Calls `split_bbox` to generate 2x2 grid tiles
- Queries each tile using existing `load_water_features`
- Prints progress for each tile ("Querying tile 1/4...")
- Returns (None, None) if any tile query fails (D-04)
- Merges all tile results using `gpd.pd.concat()` with `ignore_index=True`

### Plan 08-03: Integrate tiled loader into terrain mesh generation
**File:** `08-03-PLAN.md`

Update `terrain_mesh_from_raster` to use `load_water_features_tiled` instead of `load_water_features`. Simple 3-line change:

**Code changes:**
- Line 473: Update print message to mention "tiled approach (2x2 grid)"
- Line 484: Change `load_water_features` to `load_water_features_tiled`
- Line 487: Update error message to mention "Tiled water feature query"

### Plan 08-04: Test and validate tiled implementation
**File:** `08-04-PLAN.md`

Execute `test_water_query_debug.py` to verify the fix works correctly.

**Validation criteria:**
- No timeout errors with `enable_water_queries=True`
- Console shows tiled query messages ("Querying tile 1/4..." through "4/4...")
- Water feature counts displayed ("Query complete: X lakes, Y rivers found")
- Both tests complete successfully (baseline and water queries enabled)

## Execution Wave

Wave 1: Sequential execution
- 08-04 depends on 08-03 (integration)
- 08-03 depends on 08-02 (tiled loader)
- 08-02 depends on 08-01 (split_bbox utility)

Execute in order: 08-01 → 08-02 → 08-03 → 08-04

## Verification Criteria

### Must Haves (Goal-Backward)
- [ ] Water queries succeed for full raster areas (182km × 108km) without timeout
- [ ] All water features in the raster area are queried (no subset/fallback per D-06)
- [ ] Tiled approach uses 2x2 grid as specified in CONTEXT.md
- [ ] Error handling maintains consistency (fail entire query if any tile fails)

### Code Quality
- [ ] `split_bbox` function splits bbox into correct tile count and dimensions
- [ ] `load_water_features_tiled` merges results using pandas concat with ignore_index
- [ ] Progress messages show tile iteration (1/4, 2/4, 3/4, 4/4)
- [ ] Backward compatibility maintained (existing `load_water_features` unchanged)

### Testing
- [ ] `test_water_query_debug.py` runs successfully with `enable_water_queries=True`
- [ ] Console output confirms tiled queries executed
- [ ] Water feature counts displayed in console output
- [ ] Network generated with water-aware edge weights

### Integration
- [ ] `terrain_mesh_from_raster` uses tiled loader when `enable_water_queries=True`
- [ ] Water query results passed to `detect_water_crossing` for edge penalty calculation
- [ ] Combined terrain × water multiplicative penalty calculation works per Phase 4 D-06

## Success Criteria

**The phase is complete when:**
1. Running `test_water_query_debug.py` with `enable_water_queries=True` completes without timeout
2. Console output shows 4 tile queries and merged water feature counts
3. Water features are loaded for full raster area (not limited subset)
4. Backward compatibility maintained (existing code using `load_water_features` still works)

**Verification method:**
```bash
python test_water_query_debug.py
```

Expected success indicators:
- "Querying water features using tiled approach (2x2 grid)..." message
- "Querying tile 1/4...", "2/4...", "3/4...", "4/4..." messages
- "Query complete: X lakes, Y rivers found" message with counts > 0
- "Success! Network created with N nodes and M edges" for both tests

## Files Modified

- **routing_2026.py** (388 lines total, ~30 lines added)
  - Line ~279: Add `split_bbox` function
  - Line ~335: Add `load_water_features_tiled` function
  - Line 473: Update print message
  - Line 484: Replace `load_water_features` with `load_water_features_tiled`
  - Line 487: Update error message

- **test_water_query_debug.py** (no changes - used for validation only)

## Risk Mitigation

### Risk: OSM API still times out on individual tiles
**Mitigation:** Tiles are 1/4 the size of full bbox (45.6km × 27.2km). If still too large, can increase grid_size to (3,3) or (4,4) in future iteration. D-01 specifies (2,2) with option to tune.

### Risk: Duplicate features at tile boundaries
**Mitigation:** Current implementation includes duplicates. Parcel features don't span multiple tiles in practice. Can add deduplication in future using `dissolve()` or nearest-neighbor matching if needed.

### Risk: Performance degradation from 4x API calls
**Mitigation:** Parallel querying not implemented per D-02 (sequential). Accepts 4x slower for correctness. Can add threading in future if needed.

## Next Steps After Phase 08

This phase fixes the immediate bug preventing water queries from working. Phase 8 is now positioned to successfully implement terrain mesh generation with water-aware routing for full raster areas.