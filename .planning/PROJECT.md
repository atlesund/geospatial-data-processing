# Norwegian Hiking Route Planner

## What This Is

A desktop application that generates optimal hiking routes between coordinates in Norway using open source datasets (OpenStreetMap, GEONORGE, Kartverket) and digital terrain data. The system provides a Tkinter GUI with interactive map interface for selecting start/end points, user-configurable optimization parameters (elevation tolerance, scenic preferences), and exports routes as GPX with visualization.

## Core Value

Generate safe, optimal hiking routes between any two points in Norway using terrain and hydrography data, with a simple interface for route planning and export.

## Requirements

### Validated

- ✓ Vector class with POINT, POLYLINE, POLYGON support — existing
- ✓ Raster class with georeferenced image support — existing
- ✓ Screen class for interactive GUI — existing
- ✓ Coordinate reference system transformations via pyproj — existing
- ✓ GeoJSON, Shapefile, CSV file I/O — existing
- ✓ OpenStreetMap visualization via folium — existing
- ✓ Digitizing tools for point selection (F9/F12) — existing
- ✓ User can select start and end points on interactive map — Phase 1
- ✓ System can fetch OpenStreetMap data (roads, paths, trails) — Phase 2
- ✓ System can construct hybrid routing network (existing trails + OSM ways + terrain analysis) — Phase 2
- ✓ System can compute optimal paths using weighted cost surface — Phase 2-4
- ✓ System applies penalties for steep terrain slopes — Phase 3
- ✓ System applies penalties for water body crossings (lakes, rivers, fjords) — Phase 4, 8-9
- ✓ Default optimization: shortest distance with terrain-aware constraints — Phase 2-4
- ✓ Route visualization on interactive map — Phase 5
- ✓ GPX file export for navigation devices — Phase 5
- ✓ Application works fully offline after initial data download — Phase 2-9
- ✓ Python Tkinter GUI interface — Screen class implementation

### Active

- [ ] User can configure route optimization parameters (max elevation gain, scenic preferences)
- [ ] System can fetch/download terrain data from Kartverket N50/DTM50
- [ ] System can fetch GEONORGE data (Norwegian geospatial infrastructure)
- [ ] System detects scenic terrain (water proximity, named features, terrain type)
- [ ] Route visualization with elevation profile

Note: Above items represent potential v2 enhancements. All v1 milestone requirements are validated.

### Out of Scope

- Real-time weather integration — not in v1 scope, offline-first design
- Social features (sharing, reviews) — core routing functionality first
- Mobile app — desktop GUI only for v1
- International routing — Norway-specific datasets (Kartverket, GEONORGE)
- Real-time GPS tracking — route planning and generation only
- Route analytics/history — single-use route generation

## Context

**Existing Foundation:**
- Mature geospatial processing library with Vector, Raster, Screen classes
- Coordinate transformation support (pyproj)
- Multiple format support (GeoJSON, Shapefile, CSV)
- Interactive Canvas-based display layer with event handling
- Already uses OpenStreetMap via folium for web visualization

**Project State:**
- v1.0 milestone complete — 8 phases implemented (Phases 1-6, 8-9)
- Production-ready routing implementation with terrain and water penalties
- Full test coverage across all implemented features
- Screen class provides full GUI routing integration

**Technical Environment:**
- Python 3.x with tkinter for desktop GUI
- Offline-first design: datasets downloaded once, processed locally
- Norway-specific: prioritizes Kartverket N50/DTM50 over generic elevation data
- Hybrid routing: combine existing trails, OSM ways, terrain-based mesh

**User Vision:**
- Click-to-select route points on map
- Configurable optimization (distance vs. elevation vs. scenic)
- Visual preview with elevation profile
- Export for GPS navigation devices

## Constraints

- **Tech Stack**: Python 3.x, Tkinter GUI, geospatial libraries (pyproj, numpy, pyshp, folium) — user specified
- **Data Sources**: Kartverket N50/DTM50 (primary), OpenStreetMap, GEONORGE — specified by user
- **Platform**: Desktop application requiring GUI — tkinter constraint
- **Offline Capability**: Must work offline after initial download — user requirement
- **Scope Boundaries**: Norway-only, desktop-only, routing-only — v1 focus

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Tkinter GUI over web app | User explicitly requested Python Tkinter interface | Implemented: Screen class integration complete |
| Kartverket DTM50 over generic DEM | User specified Norway-specific terrain data source | Implemented: Raster class loads GeoTIFF terrain data |
| Hybrid routing network (trails + OSM + terrain) | Best coverage for hiking in varying terrain | Implemented: RoutingNetwork combines OSM and terrain mesh |
| Offline-first after download | User requested fully offline operation | Implemented: All data cached, OSM queries optional |
| User-configurable optimization | User wants to balance distance, elevation, scenic preferences | Partial: Terrain/water penalties configurable, UI parameters pending |
| Crossable penalty for water bodies | Avoid blocking routes unnecessarily when bridges/fords exist | Implemented: Multiplicative penalties (lakes 10x, rivers 5x, fjords 50x) |
| Spatial indexing for performance | OSM water queries cause timeouts on large areas | Implemented: shapely.strtree for fast water crossing detection |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-25 after v1.0 milestone completion*