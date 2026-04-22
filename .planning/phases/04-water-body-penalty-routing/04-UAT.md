---
status: testing
phase: 04-water-body-penalty-routing
source:
  - 04-01-SUMMARY.md
  - 04-02-SUMMARY.md
  - 04-03-SUMMARY.md
  - 04-04-SUMMARY.md
started: 2026-04-22T12:05:00Z
updated: 2026-04-22T12:05:00Z
---

## Current Test

number: 1
name: Water Feature Query Functionality
expected: |
  The load_water_features() function exists in routing_2026.py and can query OpenStreetMap for water features when provided with a bounding box. The function should accept bbox coordinates (west, south, east, north), a target EPSG code, and an optional timeout parameter. When called with valid coordinates, it should return two GeoDataFrames (lakes, rivers) projected to the target CRS. If the network request times out or fails, the function should gracefully return (None, None) and print a warning message.
awaiting: user response

## Tests

### 1. Water Feature Query Functionality
expected: The load_water_features() function exists in routing_2026.py and can query OpenStreetMap for water features when provided with a bounding box. The function should accept bbox coordinates (west, south, east, north), a target EPSG code, and an optional timeout parameter. When called with valid coordinates, it should return two GeoDataFrames (lakes, rivers) projected to the target CRS. If the network request times out or fails, the function should gracefully return (None, None) and print a warning message.
result: pending

### 2. Water Crossing Detection
expected: The detect_water_crossing() function exists in routing_2026.py and can detect when terrain edges cross water features. For lakes, it should use point-in-polygon checks on edge midpoints. For rivers, it should use line-intersection checks. For fjords, it should classify them by checking if 'fjord' appears in the lake name. The function should return appropriate penalty factors: 10.0 for lakes, 50.0 for fjords, 5.0 for rivers, and 1.0 when no crossing is detected.
result: pending

### 3. Combined Terrain and Water Penalties
expected: The terrain_mesh_from_raster() function can generate routing networks with combined terrain and water penalties. Edge weights should be calculated as: final_weight = mesh_spacing × (terrain_penalty × water_penalty_factor). Edge attributes should include terrain_penalty_factor, water_type, water_penalty_factor, and source='terrain_water'. When water queries fail, the system should fall back to terrain-only routing (water_penalty_factor = 1.0).
result: pending

### 4. Route Avoids Water Bodies
expected: When routing between two points with a lake or river between them, the pathfinder should prefer land routes over water crossings. The Dijkstra algorithm should select edges with lower combined penalties, resulting in routes that detour around water bodies where possible.
result: pending

### 5. Fjord Crossing Behavior
expected: When routing requires crossing a fjord (detected via OSM name tag), the pathfinder can include the crossing but applies a higher penalty factor (50.0) compared to lakes (10.0) and rivers (5.0). The route should still cross fjords when necessary for connecting fjord-side locations.
result: pending

### 6. Multiplicative Penalty Combination
expected: Edge penalties combine multiplicatively: terrain_penalty × water_penalty_factor. This means steep terrain at a water crossing incurs extremely high costs (both penalties apply), while flat terrain near water has moderate costs.
result: pending

### 7. Integration Tests Pass
expected: All integration tests in tests/test_04_04_integration.py should pass. These tests validate the complete pipeline from water query → crossing detection → combined weights → Dijkstra pathfinding.
result: pending

### 8. Water Queries Disabled by Default for v1 Stability
expected: The enable_water_queries parameter in terrain_mesh_from_raster() defaults to False, preventing GUI freezing from synchronous network calls. The function signature should have enable_water_queries=False as the default value.
result: pending

## Summary

total: 8
passed: 0
issues: 0
pending: 8
skipped: 0

## Gaps

[none yet]