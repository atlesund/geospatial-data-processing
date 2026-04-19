# Phase 3: Steep Terrain Penalty Routing - Context

**Gathered:** 2026-04-13
**Updated:** 2026-04-13
**Status:** Ready for planning

## Phase Boundary

Apply terrain-based penalties to route computation to avoid unrealistic vertical climbs and produce routes that follow natural hiking gradients where possible. The phase integrates Digital Terrain Model (DTM) data into the routing network's edge weights, enabling pathfinding that considers steepness in addition to distance.

## Implementation Decisions

### Slope Calculation
- **D-01:** Use slope = elevation_diff / raster_pixel_spacing. Compute slope directly from elevation differences between mesh nodes divided by the raster pixel spacing/raster resolution. This simplifies computation by avoiding 3x3 gradient windows and assumes uniform terrain between pixels.

- **D-02:** Slope calculation applies per mesh edge. For each edge in the terrain mesh, compute elevation difference between the two endpoint nodes, divide by the edge length (which matches mesh_spacing), convert to degrees: slope_angle = atan(elevation_diff / horizontal_distance).

### Steep Terrain Threshold
- **D-03:** Penalty applies when slope > 20 degrees. Below or equal to 20 degrees, no penalty. Above 20 degrees, penalty applied.

- **D-04:** 20 degrees chosen as aggressive threshold. Allows moderately steep terrain where beneficial while avoiding unrealistic vertical climbs.

### Penalty Function
- **D-05:** Linear scaling. Penalty_factor = 1.0 for slope ≤ 20°. For slope > 20°, penalty_factor = 1.0 + k × (slope - 20°) where k = 0.2 (slope multiplier). This creates smooth gradients with realistic hiking effort scaling:
  - 25° slope: penalty_factor = 2.0 (2× harder)
  - 35° slope: penalty_factor = 4.0 (4× harder)
  - 45° slope: penalty_factor = 6.0 (6× harder)

### Weight Integration
- **D-06:** Multiplicative. Final weight = distance × penalty_factor. Pairs well with continuous linear scaling. Penalty_factor applies per edge, not per whole route. Represents "times harder to hike" which is intuitive:
  - Flat terrain (≤20°): weight = distance × 1.0 = distance
  - Steep terrain (>20°): weight = distance × (1.0 + 0.2 × (slope - 20°))

### Pathfinding Algorithm
- **D-07:** Continue with Dijkstra on updated weights. No change to existing `shortest_path()` implementation. Dijkstra with multiplicative terrain weights provides sufficient performance and correctness for this scope.

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Terrain Processing
- `.planning/requirements.md` — COMP-02: System applies fixed penalties for steep terrain to ensure realistic hiking routes
- `.planning/codebase/CONVENTIONS.md` — Naming patterns, class design, property setters for EPSG code
- `.planning/codebase/ARCHITECTURE.md` — RoutingNetwork composition pattern, existing graph operations

### Routing Network
- `routing_2026.py:210-275` — `terrain_mesh_from_raster()` function creates placeholder mesh with uniform weights to be replaced with terrain-based weights
- `routing_2026.py:92-128` — `find_nearest_node()` uses KDTree for O(log n) node lookup
- `routing_2026.py:74-90` — `shortest_path()` uses nx.dijkstra_path with 'weight' attribute

### Terrain Data
- `raster_2026.py` — Raster class for reading DTM terrain data with world file georeferencing
- `raster_2026.py` — EPSG property pattern: _get_epsg, _set_epsg, property decorator

### Terrain Analysis Background
- Norway DTM50 data resolution: 50m pixel spacing → slope calculation uses 50m horizontal distance basis
- Typical hiking steepness thresholds: 10° (conservative), 15° (common), 20° (aggressive) → user chose 20°
- Linear scaling with k=0.2: penalty scales from 1.0 at 20° to 6.0 at 45° (extreme steepness)

No external specs — requirements fully captured in decisions above

## Existing Code Insights

### Reusable Assets
- `RoutingNetwork` class: Already has graph structure, node snapping (KDTree), EPSG tracking, and Dijkstra pathfinding. Need to add terrain-aware weight computation.
- `terrain_mesh_from_raster()` function: Generates regular mesh grid. Currently uses uniform `mesh_spacing` as weight. Phase 3 will compute slope-based weights from terrain elevation.
- `Raster` class: Loads DTM data with world file. Provides elevation values via world coordinate to pixel conversion.

### Established Patterns
- Composition pattern for RoutingNetwork (wraps nx.Graph instead of inheriting) — apply same pattern to new terrain weighting methods
- EPSG property with validation (raises ValueError on conflict) — maintain pattern for terrain-aware network
- Network priority: use scipy.spatial.KDTree for O(log n) spatial queries rather than O(n) scans

### Integration Points
- `terrain_mesh_from_raster()` function in `routing_2026.py`: Flow currently writes `edge_weight = mesh_spacing` for all edges. Phase 3 will replace with slope-based weight calculation using penalty_factor.
- Edge attribute structure: existing edges store `weight`, `length`, `source`. Phase 3 should add `slope_angle`, `penalty_factor` for traceability.
- Dijkstra shortest path expects 'weight' attribute — terrain penalties integrate by updating this attribute, not changing algorithm.
- Penalty applies per edge, not per whole route: each edge's weight = edge_length × penalty_factor

## Specific Ideas

- Norway山区 (mountainous terrain) has steep sections that realistically should be avoided or heavily penalized in hiking routes
- 20 degree threshold is aggressive but appropriate for Norway — hikers can handle moderate steepness but avoid unrealistic climbs
- Continuous linear scaling with k=0.0.2 provides smooth transitions:
  - 25° slopes cost 2× (reasonably challenging)
  - 35° slopes cost 4× (significantly harder)
  - 45° slopes cost 6× (extreme, should be avoided)
- Multiplicative scaling represents "times harder to hike" which aligns with realistic hiking behavior

## Deferred Ideas

None — discussion stayed within phase scope

---

*Phase: 03-steep-terrain-penalty-routing*
*Context gathered: 2026-04-13*
*Updated: 2026-04-13 (penalty function changed to continuous linear scaling)*