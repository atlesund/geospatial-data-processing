# Features — Hiking Route Planning

## Table Stakes (Must Have for v1)

### Map Interaction
- Map-based point selection — Click to select start/end coordinates on interactive map
- Coordinate display — Show selected coordinates in both decimal degrees and UTM
- Pan/zoom navigation — Standard map controls for area selection

### Route Configuration
- Max elevation gain constraint — User can specify acceptable total elevation gain
- Scenic preference weight — Toggle or slider for scenic route preference
- Distance priority option — Optional preference for shortest path
- Route preset profiles — Quick selection (e.g., "Easy hiker", "Fast and flat", "Scenic wanderer")

### Route Computation
- Terrain-based routing — Use digital elevation models for cost calculation
- Hydrography awareness — Apply penalties for water body crossings
- Hybrid network routing — Combine trails, OSM paths, and terrain-based routing

### Visualization
- Route display on map — Visual representation of computed route
- Elevation profile — Chart showing elevation along route with total gain/loss
- Route statistics — Total distance, elevation gain/loss, estimated time
- Multi-option preview — Show 2-3 route alternatives with different trade-offs

### Export
- GPX file export — Standard GPX format for GPS navigation devices
- Route images — Export map with route overlay as image

### Offline Support
- Data download manager — Download terrain and mapping data for regions
- Cache management — View and manage downloaded offline data
- Offline mode indicator — Clear display of offline status vs. online

## Differentiators (Competitive Advantages)

### Norway-Specific
- Kartverket DTM50 integration — Official Norwegian terrain data
- GEONORGE data access — Norwegian geospatial data portal
- UTM zone handling — Proper handling of Norway's multiple UTM zones
- DNT trail integration — Norwegian Trekking Association trails where available

### Scenic Routing
- Water proximity preference — Routes near lakes, fjords, rivers get scenic bonus
- Named feature targeting — Routes through or near named scenic spots
- Terrain type weighting — Preferences for forests, alpine areas, coastlines
- Viewshed analysis — Routes maximizing scenic visibility

### Hybrid Network
- Trail-first routing — Prioritize existing hiking trails
- OSM integration — Fall back to OpenStreetMap paths/roads
- Terrain backup — Generate route off-trail when networks incomplete
- Configurable preference — User weighting of trail vs. off-trail

### Fully Offline
- No API calls after download — Complete offline operation
- Efficient caching — Compression and indexing of terrain data
- Regional downloads — Download by predefined Norway regions

## Anti-Features (Deliberately NOT Build)

- Real-time weather — Complex, data source dependencies, out of v1 scope
- Social features (sharing, reviews) — Beyond route generation, web service needed
- Mobile app — Desktop-only (Tkinter) for v1, mobile is separate platform
- Live GPS tracking — Route planning and generation only, not navigation tool
- Route analytics/history — Single-use route generation, no user accounts
- Real-time collaboration — Not a multi-user application

## Feature Dependencies

- Elevation profile depends on: Terrain data (DEM) + Route polyline
- Route visualization depends on: Map display + Route generation
- GPX export depends on: Route geometry + Elevation data
- Offline mode depends on: Cache manager + Data download
- Scenic routing depends on: Named features + Water bodies + Terrain types
- Route alternatives depends on: Multi-path search algorithm

## Norwegian Context

### Kartverket-Specific
- DTM50 (50m resolution) terrain data
- N50/N10 topographic maps
- Projected coordinate systems (UTM 32-35N)
- Hydrography data (lakes, rivers)

### GEONORGE-Specific
- Norwegian geospatial data portal
- Administrative boundary data
- Protected area information (nature reserves)
- Land use classification

### Terrain Type Relevance
- Alpine terrain (above treeline) — unique Norwegian feature
- Fjord/coastal areas — water-based routing considerations
- Forest regions — trail networks vs. terrain routing
- Plateau/mountain areas — elevation profile importance

### Seasonal Considerations
- Winter routing — Not in v1 (requires snow data, avalanche risk)
- DNT trail closures — Seasonal snow/melting conditions
- Tide-affected areas — Coastal trail accessibility

## Complexity Notes

- Map-based point selection — Simple (extend existing Screen class)
- Coordinate display — Simple (existing coordinate transforms)
- Route configuration dialogs — Medium (new UI components, validation)
- Terrain data download — Medium (API integration, large files, caching)
- Cache manager — Medium (storage, invalidation, UX)
- OSM data extraction — Medium (osmnx library, Norwegian OSM specifics)
- Routing network construction — Complex (multiple sources, graph building)
- Cost surface computation — Complex (DEM processing, multi-factor weights)
- Path finding algorithm — Complex (A* on weighted graph, heuristics)
- Elevation profile — Medium (DEM sampling, matplotlib integration)
- Route visualization — Simple (extend existing visualization)
- GPX export — Simple (gpxpy library)
- Scenic feature detection — Complex (spatial queries, proximity analysis)
- Water body handling — Medium (hydrography extraction, crossing detection)

---
*Research completed: 2026-04-12*