# Phase 4: Water Body Penalty Routing - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-13
**Phase:** 04-water-body-penalty-routing
**Areas discussed:** Data source, Data access strategy, Penalty function, Edge detection method, Water type classification, Weight integration, Pathfinding algorithm

---

## Data Source

| Option | Description | Selected |
|--------|-------------|----------|
| OpenStreetMap (osmnx) | Use osmnx package to query water features from OpenStreetMap. Easier integration (already using osmnx for OSM trails), but requires online access or local OSM download. | ✓ |
| Kartverket N50 | Load Kartverket N50 hydrography shapefiles locally. Provides authoritative Norwegian water data, works offline after download, consistent with terrain data source. | |
| GEONORGE | Download hydrography vector data directly from GEONORGE Norwegian geospatial infrastructure. Provides up-to-date water features, but requires additional API integration. | |

**User's choice:** OpenStreetMap (osmnx)
**Notes:** Leverages existing osmnx dependency from Phase 2 OSM trail integration.

---

## Water Detection

| Option | Description | Selected |
|--------|-------------|----------|
| osmnx API query | Using osmnx.features_from_place() or features_from_bbox() with tags like natural='water' and waterway='river'. Query at route planning time to get relevant water features. | ✓ |
| Pre-download to vector | Pre-download OSM water features for the planning area into Polygon (lakes) and Polyline (rivers) geometries. Store in memory or local cache for offline access. | |

**User's choice:** osmnx API query
**Notes:** Query at route planning time rather than pre-download.

---

## Penalty Type

| Option | Description | Selected |
|--------|-------------|----------|
| Fixed per type | Static penalty per water type: lakes=low, rivers=medium, fjords=high. Simple, predictable, but doesn't consider crossing difficulty (width, depth). | |
| Multiplicative factors | Multiply edge weight by penalty factor (like terrain). Penalties: lakes=10×, rivers=5×, fjords=50×. Prefer land detours proportionally to water severity. | ✓ |

**User's choice:** Multiplicative factors
**Notes:** Consistent with Phase 3 terrain penalty approach.

---

## Penalty Values

| Option | Description | Selected |
|--------|-------------|----------|
| Conservative | Conservative: lakes=5×, rivers=3×, fjords=20×. Allows water crossings when detours are long. Best for areas where streams/fjords are unavoidable. | |
| Aggressive | Aggressive: lakes=10×, rivers=5×, fjords=50×. Strongly prefers land routes. Avoids water crossings except when no alternative exists. | ✓ |

**User's choice:** Aggressive
**Notes:** lakes=10×, rivers=5×, fjords=50× penalties chosen.

---

## Edge Detection

| Option | Description | Selected |
|--------|-------------|----------|
| Point-in-polygon check | For each terrain mesh edge, check if edge's midpoint intersects any water polygons (lakes) or crosses water polylines (rivers). Apply penalty if intersect = True. | ✓ |
| Shapely intersection | Use shapely intersection library to detect geometric intersections between routing edges and water features. More accurate than simple point tests. | |

**User's choice:** Point-in-polygon check
**Notes:** Simpler approach checking edge midpoint against water polygons/polylines.

---

## Claude's Discretion

Areas where user deferred to Claude:
- Order of query vs. detection: query water features first, then check edge intersections during mesh generation; or query per-edge detection
- OSM tag refinement for fjord detection (Norway-specific fjord classification)
- Fallback behavior when osmnx query fails or water data unavailable
- Performance optimization for large water feature sets

## Deferred Ideas

None — discussion stayed within phase scope