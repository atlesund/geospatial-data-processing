# Research Summary: Norwegian Hiking Route Planner Stack

**Domain:** Geospatial routing application
**Researched:** 2026-04-12
**Overall confidence:** MEDIUM

## Executive Summary

The Norwegian hiking route planner builds on an existing Python geospatial library with Vector, Raster, and Screen classes for data management and tkinter-based visualization. The research identified a cohesive, open-source stack that integrates minimally with the current architecture while providing terrain-based routing capabilities.

The primary recommendations center on three core libraries:
1. **osmnx** for extracting OpenStreetMap hiking trail data and building routing networks
2. **networkx** (extending the existing numpy dependency) for path finding with terrain-based costs
3. **rasterio** for processing Kartverket DTM50 terrain data and computing elevation profiles

These choices maintain consistency with the existing ecosystem (pyproj coordinates, numpy operations) while adding minimal new dependencies. The stack supports offline operation through GeoPackage storage and follows industry standard patterns for geospatial data handling.

## Key Findings

**Stack Core:** `osmnx` + `networkx` + `rasterio` + `shapely` + `fiona` for terrain-based hiking routing with GPX export

**Architecture:** Extend existing Vector class to store routes, add Raster geotiff loading via rasterio, and use Screen's existing drawing methods for visualization. Route computation follows: User digitizes points → OSM graph extraction → DEM-sampled edge costs → NetworkX A* → route as Vector polyline.

**Critical integration points:** All new components must use pyproj for coordinate transforms, convert routes to Vector(POLYLINE) objects, and work with Raster's geotiff backend for terrain sampling. Screen's F5/F9/F10/F12 workflow handles digitizing and export.

## Implications for Roadmap

Based on research, suggested phase structure:

1. **Phase: Terrain Data Integration** - Addresses: Elevation profile computation
   - Add rasterio dependency and extend Raster class with geotiff loading
   - Implement elevation sampling from DEM data
   - Compute slope and aspect for terrain difficulty
   - Avoid: Trying to build routing without elevation costs

2. **Phase: OSM Data Extraction** - Addresses: Trail network construction
   - Add osmnx dependency and extract walking/hiking graphs
   - Filter for Norwegian paths, tracks, footways
   - Build network topology ready for routing
   - Avoid: Pre-filtering by historical data sources (OSM is comprehensive)

3. **Phase: Path Finding Engine** - Addresses: Terrain-based routing
   - Add networkx and implement A* with custom weights
   - Integrate DEM sampling for edge costs (slope, elevation gain)
   - Convert networkx paths to Vector polylines
   - Avoid: Using online routing services (offline capability matters)

4. **Phase: User Interface Integration** - Addresses: Route visualization and export
   - Integrate route display into existing Screen drawing methods
   - Implement elevation profile plotting on canvas
   - Add GPX export via gpxpy
   - Avoid: Major Screen refactoring (use existing digitizing workflow)

**Phase ordering rationale:**
- Terrain data must be processed before routing costs can be computed
- OSM graph needs to exist before path finding can run
- Routing results needed before UI and export functionality
- Each phase builds directly on previous capabilities

**Research flags for phases:**
- Phase 1 (Terrain): Standard rasterio patterns, low research risk
- Phase 2 (OSM): osmnx is mature, Norway-specific filters may need verification
- Phase 3 (Routing): Custom weight functions will need tuning based on hiking preferences
- Phase 4 (UI): Elevation profile plotting on Tkinter canvas needs matplotlib backend validation

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM | Recommendations based on industry standards; web search was limited so Kartverket-specific APIs need verification |
| Features | HIGH | OSM extraction and routing patterns are well-established in Python ecosystem |
| Architecture | MEDIUM | Integration paths identified but Screen elevation profile plotting needs technical validation |
| Pitfalls | MEDIUM | Identified key risks (CRS consistency, geotiff loading) but Norway-specific data issues may surface |

## Gaps to Address

- **Kartverket DTM50 access**: Need to verify exact download URLs, API authentication requirements, and coordinate reference systems for Norwegian data
- **Off-hiking trails**: Need to confirm what happens when route finding requires traversing non-OSM paths (open terrain) - may need custom off-network routing
- **Screen elevation profiles**: Matplotlib integration with Tkinter canvas needs prototype to verify performance
- **Norway-specific OSM tags**: Need to validate that osmnx filters correctly capture Norwegian trail classifications

*Research completed: 2026-04-12*