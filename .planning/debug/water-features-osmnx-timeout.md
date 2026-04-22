---
slug: water-features-osmnx-timeout
status: fixed
trigger: Focus on Phase 4 water features loading. The error shows `features_from_bbox() got an unexpected keyword argument 'timeout'`. Find where this timeout parameter is being passed in the water query code and fix it.
created: 2026-04-22T13:29:00Z
updated: 2026-04-22T13:40:00Z
---

# Water Features OSMnx Timeout Bug Debug Session

## Symptoms
- **Expected behavior**: Water features should load from OpenStreetMap with Phase 4 water body penalties enabled
- **Actual behavior**: Query fails with `features_from_bbox() got an unexpected keyword argument 'timeout'`
- **Error message**: `features_from_bbox() got an unexpected keyword argument 'timeout'`
- **Timeline**: Never worked - this is a bug in the original implementation
- **Reproduction**: Load terrain data when `enable_water_queries=True` (Phase 4 water penalty mode)

## Console Output
```
Water queries enabled, querying OSM water features...
Warning: Failed to query water features: features_from_bbox() got an unexpected keyword argument 'timeout'
Continuing without water penalty mode
```

## Current Focus
- **Hypothesis**: The `timeout` parameter was removed from OSMnx's `features_from_bbox()` API in a recent version
- **Test**: Verify OSMnx API documentation for `features_from_bbox()` parameters
- **Expecting**: Find that `timeout` is not a valid parameter and needs to be removed or replaced with equivalent timeout handling
- **Next action**: Find the water query code calling `features_from_bbox(timeout=...)` and fix it

## Evidence
- timestamp: 2026-04-22T13:30:00Z
  - Finding: Located code in `/Users/dev/Code/School/geospatial-data-processing/routing_2026.py` lines 310-314 and 317-321
  - Code: `ox.features_from_bbox((west, south, east, north), tags={...}, timeout=timeout)`
  - Environment: osmnx version 2.1.0 installed

- timestamp: 2026-04-22T13:30:00Z
  - Finding: Checked osmnx API signature for `features_from_bbox()`
  - Signature: `(bbox: tuple[float, float, float, float], tags: dict[str, bool | str | list[str]]) -> gpd.GeoDataFrame`
  - Result: `timeout` parameter does not exist in osmnx 2.1.0 API

## Evidence
- timestamp: 2026-04-22T13:30:00Z
  - Finding: Located code in `/Users/dev/Code/School/geospatial-data-processing/routing_2026.py` lines 310-314 and 317-321
  - Code: `ox.features_from_bbox((west, south, east, north), tags={...}, timeout=timeout)`
  - Environment: osmnx version 2.1.0 installed

- timestamp: 2026-04-22T13:30:00Z
  - Finding: Checked osmnx API signature for `features_from_bbox()`
  - Signature: `(bbox: tuple[float, float, float, float], tags: dict[str, bool | str | list[str]]) -> gpd.GeoDataFrame`
  - Result: `timeout` parameter does not exist in osmnx 2.1.0 API

- timestamp: 2026-04-22T13:35:00Z
  - Finding: osmnx 2.1.0 uses `ox.settings.requests_timeout` for global timeout configuration
  - Current value: 180 seconds (default)
  - Result: Timeout must be set via `ox.settings.requests_timeout = timeout` before calling the API
  - Cache enabled: `ox.settings.use_cache = True` by default

## Eliminated
-

## Resolution
- **Root cause**: `features_from_bbox()` in osmnx 2.1.0 does not accept a `timeout` parameter as a function argument. Timeout is handled globally via `ox.settings.requests_timeout` (currently 180s default).
- **Fix**:
  1. Remove `timeout=timeout` parameter from both `ox.features_from_bbox()` calls (lines 313 and 320)
  2. Add `ox.settings.requests_timeout = timeout` before the API calls to configure the timeout
  3. Optionally keep existing caching behavior (already enabled by default)
- **Verification**: Run application with `enable_water_queries=True` and verify water features load successfully without hanging.
- **Files changed**: routing_2026.py (lines 308-321)