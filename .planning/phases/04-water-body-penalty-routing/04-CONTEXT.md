# Phase 4: Water Body Penalty Routing - Context

**Gathered:** 2026-04-13
**Status:** Ready for planning

## Phase Boundary

Apply water crossing penalties to route computation. Routes should avoid lakes, rivers, and fjords when possible, preferring land-based detours. The phase integrates hydrography data into the routing network's edge weights, enabling pathfinding that considers water obstacles in addition to terrain steepness.

## Implementation Decisions

### Water Data Source
- **D-01:** Use OpenStreetMap via osmnx API for water body detection. Query water features at route planning time using osmnx.features.from.place() or features.from.bbox() with tags like natural='water' and waterway='river'. leverages existing osmnx dependency already used for OSM trail integration in Phase 2.

### Data Access Strategy
- **D-02:** osmnx API query at route planning time. Query relevant water features dynamically rather than pre-downloading. Works for on-demand routes within Norway boundaries.

### Penalty Function
- **D-03:** Multiplicative factors per water type (consistent with Phase 3 terrain penalties). Final edge weight = distance × penalty_factor. Penalities: lakes=10×, rivers=5×, fjords=50×. Strongly prefers land routes while allowing water crossings as last resort.

### Edge Detection Method
- **D-04:** Point-in-polygon check for water crossing detection. For each terrain mesh edge, check if the edge's midpoint intersects any water polygons (lakes) or crosses water polylines (rivers). Apply penalty if intersection = True.

### Water Type Classification
- **D-05:** by OSM tag categories. natural='water' or waterway='lakebank' → lakes. waterway='river', 'stream', 'canal' → rivers. natural='water' with fjord-specific tags or large water bodies → fjords.

### Weight Integration
- **D-06:** Combine with terrain penalties multiplicatively. Final weight = distance × terrain_penalty_factor × water_penalty_factor. Edge gets penalty_factor = terrain_penalty × water_penalty, with default 1.0 for neither applies to both. If both terrain and water penalties apply, penalty_factor = terrain_penalty × water_penalty (e.g., 4.0 terrain × 10.0 water = 40.0 total).

### Pathfinding Algorithm
- **D-07:** Continue with Dijkstra on combined weights. No algorithm change needed. Dijkstra with multiplicative terrain and water penalties provides sufficient performance.

### Claude's Discretion
- Order of query vs. detection: query water features first, then check edge intersections during mesh generation; or query per-edge detection
- OSM tag refinement for fjord detection (Norway-specific fjord classification)
- Fallback behavior when osmnx query fails or water data unavailable
- Performance optimization for large water feature sets

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` — COMP-01: System applies penalties for water body crossings (lakes, rivers, fjords)

### Routing Network
- `routing_2026.py` — RoutingNetwork class with graph structure and Dijkstra pathfinding
- `routing_2026.py:74-91` — shortest_path() uses nx.dijkstra_path with 'weight' attribute
- `routing_2026.py:260-380` — terrain_mesh_from_raster() generates mesh with terrain weights; Phase 4 will add water penalty detection

### Code Conventions
- `.planning/codebase/CONVENTIONS.md` — Naming patterns, class design, property setters
- `.planning/codebase/ARCHITECTURE.md` — RoutingNetwork composition pattern

### Phase 3 Terrain Penalties (Context)
- `.planning/phases/03-steep-terrain-penalty-routing/03-CONTEXT.md` — Terrain penalty decisions to combine: multip Final = distance × terrain_factor × water_factor
- `.planning/phases/03-steep-terrain-penalty-routing/03-03-SUMMARY.md` — Edge attribute structure pattern: weight, length, slope_angle, penalty_factor, source

### OSM Data Access
- osmnx package already imported in routing_2026.py for OSM trail integration (Phase 2)
- osmnx.features_from_bbox() and osmnx.features_from_place() methods for vector data retrieval

### Water Data Sources (Norway)
- OpenStreetMap water feature tags: natural='water', waterway='river'|'stream'|'lakebank'
- Norway-specific fjord tags: natural='water' + fjord naming or fjord-specific mapping conventions
- Norwegian water body context: many fjords, lakes, and rivers avoid unnecessary crossings

No external specs — requirements fully captured in decisions above

## Existing Code Insights

### Reusable Assets
- `RoutingNetwork` class: Already has graph structure, edge weight system, Dijkstra pathfinding. Need to add detection for water crossings.
- `terrain_mesh_from_raster()` function: Generates mesh with terrain penalties. Phase 4 will add water detection and combine penalties multiplicatively.
- osmnx import: Already in routing_2026.py for OSM trail data. Reuse for water feature queries.

### Established Patterns
- Multiplicative penalty factors from Phase 3: penalty_factor = 1.0 + 0.2 × (slope - 20°) for terrain. Apply similar pattern for water.
- Edge attribute structure: edges store weight, length, penalty_factor, source. Add water_penalty_factor or combine into existing penalty_factor.
- Fallback handling: Phase 3 returns uniform weight when elevation unavailable. Apply similar pattern for water data failures.

### Integration Points
- `terrain_mesh_from_raster()` function: Phase 3 adds edge with terrain_weight. Phase 4 will check water crossing before/after terrain calculation and multiply penalties.
- Edge attributes: existing edges have weight, length, slope_angle, penalty_factor, source. Add water_type and water_penalty_factor for traceability.
- Combined penalty flow: For each edge, calculate terrain_penalty, check water crossing → water_penalty, final penalty = terrain_penalty × water_penalty.

## Specific Ideas

- Norway has many fjords, lakes, rivers. Aggressive penalties (lakes=10, rivers=5, fjords=50) reflect water crossings as last resort.
- Point-in-polygon is simpler than full shapely intersection. Check edge midpoint against water polygons. Good balance of accuracy vs. complexity.
- Combining terrain and water penalties multiplicatively: steep slopes + water crossing = extremely high cost, router avoids both.
- osmnx API query at route planning time vs. pre-download. Chosen query approach for simplicity with existing osmnx usage.

## Deferred Ideas

None — discussion stayed within phase scope

---

*Phase: 04-water-body-penalty-routing*
*Context gathered: 2026-04-13*