# Roadmap: Norwegian Hiking Route Planner

## Overview

Build hiking route planning capabilities into an existing geospatial codebase by enabling map interaction, integrating Norwegian terrain and trail data, computing optimal terrain-aware routes, and delivering results through visualization and GPX export. The implementation starts with frontend interaction, establishes routing networks, applies terrain-based cost functions for steep terrain and water obstacles, and culminates in user-facing visualization and export. v1 is scoped to UTM 32V (southern Norway) only.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Map Interaction & User Selection** - Enable point selection, map navigation, and coordinate display
- [x] **Phase 2: Routing Network Construction** - Build hybrid network from trails, OSM, and terrain
- [x] **Phase 3: Steep Terrain Penalty Routing** - Apply fixed steep terrain penalties for realistic hiking routes
- [x] **Phase 4: Water Body Penalty Routing** - Apply water crossing penalties in route computation
- [x] **Phase 5: Route Visualization & Export** - Display routes and enable GPX export for GPS devices
- [x] **Phase 6: GUI Routing Integration** - Connect point selection with routing computation
- [x] **Phase 8: Fix OSM API integration for querying water features and hiking trails within area given by TIF file** - Enable tiled water feature queries
- [x] **Phase 9: Optimize water crossing detection with spatial indexing** (verified 2026-04-25) - Enable fast water crossing detection for large datasets

## Phase Details

### Phase 1: Map Interaction & User Selection
**Goal**: Users can select route endpoints through interactive map interface
**Depends on**: Nothing (first phase)
**Requirements**: MAP-01, MAP-02, MAP-03, MAP-04, MAP-05
**Success Criteria** (what must be TRUE):
  1. User can click on map to select start point and see it visually marked
  2. User can click on map to select end point and see it visually marked
  3. User can pan the map to navigate to different geographic areas
  4. User can zoom in/out to adjust map scale for different levels of detail
  5. User can see selected coordinates displayed in decimal degrees format
**Plans**: 3
**UI hint**: yes

Plans:
- [x] 01-01: Set up test infrastructure with pytest framework and test fixtures
- [x] 01-02: Extend Screen class to support click-based point digitizing with visual markers
- [x] 01-03: Implement map pan and zoom controls with coordinate display in decimal degrees

### Phase 2: Routing Network Construction
**Goal**: System constructs a complete routing network from established trails, OpenStreetMap data, and terrain-based meshes
**Depends on**: Phase 1
**Requirements**: COMP-03, COMP-04, COMP-05
**Success Criteria** (what must be TRUE):
  1. System integrates established hiking trails into routing graph
  2. System incorporates OpenStreetMap paths and trails where available
  3. System uses terrain-based routing in areas where trail network is incomplete
**Plans**: 4

Plans:
- [x] 02-01: Install dependencies and create test fixtures
- [x] 02-02: Build network topology combining established trails and OSM ways
- [x] 02-03: OSM data integration for hiking trail extraction
- [x] 02-04: Add terrain mesh generation for areas lacking trail data

### Phase 3: Steep Terrain Penalty Routing
**Goal**: System applies fixed steep terrain penalties to ensure realistic hiking routes
**Depends on**: Phase 2
**Requirements**: COMP-02
**Success Criteria** (what must be TRUE):
  1. System applies fixed penalties for steep terrain in route computation
  2. System routes avoid unrealistic vertical climbs when alternatives exist
  3. System produces routes that follow natural hiking gradients where possible
**Plans**: 4

Plans:
- [x] 03-01: Enable raster elevation data access with Pillow (PIL) library
- [x] 03-02: Implement terrain weight calculation with slope-based penalties
- [x] 03-03: Integrate terrain weights into terrain mesh generation
- [x] 03-04: Validate terrain-aware routing through integration testing

### Phase 4: Water Body Penalty Routing
**Goal**: System computes optimal routes by applying penalties for water body crossings
**Depends on**: Phase 3
**Requirements**: COMP-01
**Success Criteria** (what must be TRUE):
  1. System applies penalties for water body crossings (lakes, rivers, fjords) in route computation
  2. System computes routes that minimize water crossings while finding optimal paths
  3. System produces routes that cross water only when necessary with appropriate detours
**Plans**: 4

Plans:
- [x] 04-01: Integrate osmnx API to query OpenStreetMap water features (lakes, rivers, fjords)
- [x] 04-02: Implement water crossing detection via point-in-polygon and line-intersection checks
- [x] 04-03: Add combined terrain × water multiplicative penalty calculation in mesh generation
- [x] 04-04: Validate water-aware routing through integration testing

### Phase 5: Route Visualization & Export
**Goal**: Users can view computed routes and export them for GPS navigation device use
**Depends on**: Phase 4
**Requirements**: VIZ-01, EXP-01
**Success Criteria** (what must be TRUE):
  1. System displays computed route polyline on interactive map with distinct, clear visualization
  2. User can export route as GPX file that loads successfully in GPS navigation device
  3. GPX file contains all required waypoint and track information for navigation
**Plans**: 4
**UI hint**: yes

Plans:
- [x] 05-01: Extend Screen drawing methods to display route polylines with distinct styling
- [x] 05-02: Implement GPX file export from route polyline data
- [x] 05-03: Add route visualization controls (show/hide, color/style options)
- [x] 05-04: Validate GPX export compatibility with common GPS devices

### Phase 6: GUI Routing Integration - Connect point selection with routing computation

**Goal:** Routes automatically compute when user selects start and end points through GUI
**Requirements:** D-01, D-02, D-03, D-04 (from CONTEXT.md)
**Depends on:** Phase 5
**Success Criteria** (what must be TRUE):
  1. User selects start point via Shift-F9 + click
  2. User selects end point via click (second click)
  3. Route automatically computes after second click (no manual trigger needed)
  4. System transforms screen coordinates through world → network EPSG
  5. System snaps clicked points to nearest graph nodes
  6. System computes shortest path and displays route on map
  7. All errors show user-friendly message dialogs

**Plans**: 4

Plans:
- [x] 06-00: Create test infrastructure with fixtures and comprehensive test coverage
- [x] 06-01: Add network assignment capability to Screen class (set_route_network method)
- [x] 06-02: Implement core routing computation method (_compute_and_display_route)
- [x] 06-03: Wire auto-trigger into point selection and create integration example

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6 → 8 → 9

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Map Interaction & User Selection | 3/3 | Complete | 2026-04-12 |
| 2. Routing Network Construction | 4/4 | Complete | 2026-04-13 |
| 3. Steep Terrain Penalty Routing | 4/4 | Complete | 2026-04-13 |
| 4. Water Body Penalty Routing | 4/4 | Complete | 2026-04-14 |
| 5. Route Visualization & Export | 4/4 | Complete | 2026-04-16 |
| 6. GUI Routing Integration | 4/4 | Complete    | 2026-04-20 |
| 8. Fix OSM API integration for querying water features | 4/4 | Complete    | 2026-04-24 |
| 9. Optimize water crossing detection with spatial indexing | 4/4 | Complete    | 2026-04-25 |

### Phase 8: Fix OSM API integration for querying water features and hiking trails within area given by TIF file

**Goal:** Enable successful OSM water feature queries for large raster areas by implementing tiled queries that avoid API timeout limits
**Requirements:** D-06 (full water feature coverage)
**Depends on:** Phase 4
**Success Criteria** (what must be TRUE):
  1. Water feature queries complete without OSM API timeout for full raster areas (up to 182km × 108km)
  2. Tiled queries split large bounding boxes into 2x2 grid tiles
  3. All tile results are merged into single GeoDataFrames for lakes and rivers
  4. Failed tiles cause entire query to fail (consistency over partial results)
**Plans**: 4/4 plans complete

Plans:
- [x] 08-01: Create split_bbox utility function that divides large bounding boxes into a 2x2 grid
- [x] 08-02: Create load_water_features_tiled function that queries tiles and merges results
- [x] 08-03: Update terrain_mesh_from_raster to use load_water_features_tiled
- [x] 08-04: Test and validate tiled water query implementation

### Phase 9: Optimize water crossing detection with spatial indexing

**Goal:** Enable fast water crossing detection for large numbers of water features without performance degradation
**Requirements:** COMP-01 (water penalty routing)
**Depends on:** Phase 8
**Success Criteria** (what must be TRUE):
  1. Water crossing detection uses spatial indexing (O(n log m) instead of O(n×m))
  2. Detection completes in reasonable time for full raster areas (30k+ lakes, 20k+ rivers)
  3. Results are functionally identical to naive iteration (same penalties applied)
  4. Detection works with both lakes (point-in-polygon) and rivers (line-intersection)
**Plans**: 4

Plans:
- [x] 09-01: Build spatial indexes for lakes and rivers using shapely.strtree.STRtree
- [x] 09-02: Update detect_water_crossing to use spatial indexes instead of naive iteration
- [x] 09-03: Integrate spatial index building into terrain mesh generation workflow
- [x] 09-04: Test and validate indexed detection produces same results as naive version