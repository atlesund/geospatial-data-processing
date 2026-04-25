---
slug: water-query-bbox-issue
status: investigating
trigger: Debug phase 4 water query issue - figure out why enabling water queries doesn't work when calling terrain_mesh_from_raster with .tif files. Are files too big? Wrong syntax? Wrong bbox sent to load_water_features?
created: 2026-04-22T16:00:00Z
updated: 2026-04-22T16:30:00Z
---

# Water Query BBox Issue Debug Session

## Symptoms
- **Expected behavior**: Water features should load from OpenStreetMap when `enable_water_queries=True` in `terrain_mesh_from_raster`
- **Actual behavior**: Water queries produce excessively large bbox area causing potential OSM API timeouts or failures
- **Error messages**: No explicit error reported, but the bbox size is problematic
- **Timeline**: Never verified - water queries have always been disabled in tests (`enable_water_queries=False`)
- **Reproduction**: Call `terrain_mesh_from_raster(raster, mesh_spacing=100, enable_water_queries=True)` with .tif files from /data/terrain/

## Questions to Answer
1. Are the .tif files too big (15MB each) causing issues?
2. Is there wrong syntax in the water query code?
3. Is the correct bbox being sent to `load_water_features`?
4. Does the CRS conversion from local EPSG to EPSG:4326 work correctly?

## Current Focus
- **Hypothesis**: The .tif files cover too large an area for efficient OSM queries (182.6km x 108.9km = 1.61 sq degrees), causing timeouts or excessive data retrieval
- **Test**: Verify OSM query behavior with the full bbox and test with a smaller bbox
- **Expecting**: Full bbox query will timeout or return excessive data; smaller bbox should work
- **Next action**: Add bbox size limit and/or use the optional `bbox` parameter to `terrain_mesh_from_raster` to restrict queries to smaller areas

## Evidence
- timestamp: 2026-04-22T16:15:00Z
  - Finding: GeoTIFF files are 2002x2002 pixels at 50m resolution in EPSG:25833 (UTM Zone 33N)
  - Shape: (2002, 2002), Bounds: (99950.0, 6699950.0, 200050.0, 6800050.0)
  - File size: 15MB each, not the issue
  - Files: 6701_50m_33.tif and 6801_50m_33.tif

- timestamp: 2026-04-22T16:20:00Z
  - Finding: CRS conversion from EPSG:25833 to EPSG:4326 produces bbox: (7.765917, 60.238587, 9.410887, 61.219283)
  - BBox size: 1.644970 degrees x 0.980696 degrees = 1.61 sq degrees
  - Equivalent physical size: approx 182.6km x 108.9km
  - Conversion is syntactically correct

- timestamp: 2026-04-22T16:25:00Z
  - Finding: OSM settings show 180 second timeout with cache enabled by default
  - This full bbox area is too large for typical OSM API queries
  - osmnx.features_from_bbox() may timeout or return excessive data

- timestamp: 2026-04-22T16:28:00Z
  - Finding: Code review shows `terrain_mesh_from_raster` accepts optional `bbox` parameter
  - The bbox is calculated from the full raster extent (lines 466-469 in routing_2026.py)
  - The function signature allows passing a smaller bbox: `bbox: Optional bounding box (x_min, y_min, x_max, y_max)`
  - This bbox is used but could be overridden/limited

- timestamp: 2026-04-22T16:30:00Z
  - Finding: The bbox parameter exists but is passed to mesh creation without affecting the water query bbox
  - Water queries use bbox_local calculated from ALL node coordinates (lines 466-469)
  - The optional bbox parameter is documented but not used for water query area restriction

## Eliminated
- timestamp: 2026-04-22T16:15:00Z
  - hypothesis: .tif files are too big causing memory issues
  - evidence: Files are 15MB, reasonable size for GeoTIFF. The issue is query area, not file size.

- timestamp: 2026-04-22T16:20:00Z
  - hypothesis: Syntax error in bbox conversion code
  - evidence: CRS conversion code works correctly, produces valid EPSG:4326 coordinates

- timestamp: 2026-04-22T16:25:00Z
  - hypothesis: Wrong bbox sent to load_water_features
  - evidence: Bbox is correct format but covers too large area (182.6km x 108.9km)

## Resolution
- **Root cause**: The water query bbox covers the full raster extent (182.6km x 108.9km for Kartverket dtm50 tiles), which is too large for practical OSM queries. While the code is syntactically correct, querying OSM for water features over this entire area will likely timeout or return excessive data.

- **Fix**:
  1. When `enable_water_queries=True`, the bbox parameter to `terrain_mesh_from_raster` should be used to limit water queries to a smaller area
  2. Or add a bbox size limit/splitting logic to query OSM in smaller chunks
  3. The current bbox parameter exists but is not used for water query area restriction

- **Verification**: Test with a limited bbox (e.g., 10km x 10km area) to verify water queries work at smaller scale

- **Files changed**: routing_2026.py (lines 466-484  - bbox calculation and water query section)

## Recommendations
1. **Short term**: Use the optional `bbox` parameter when calling `terrain_mesh_from_raster` to limit queries for testing:
   ```python
   # Smaller bbox example (10km x 10km area in Bergen)
   bbox = (100000, 6700000, 110000, 6710000)
   routing_net = terrain_mesh_from_raster(raster, mesh_spacing=100, bbox=bbox, enable_water_queries=True)
   ```

2. **Long term**: Modify `terrain_mesh_from_raster` to use the bbox parameter to limit water queries, not just mesh generation