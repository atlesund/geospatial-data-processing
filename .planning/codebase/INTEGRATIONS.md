# External Integrations

**Analysis Date:** 2026-04-12

## APIs & External Services

**Mapping Platforms:**
- OpenStreetMap (OSM) - Base map for geospatial visualization
  - Library: folium (`utilities_2026.py`)
  - Usage: Creates interactive HTML maps that open in default web browser
  - CRS requirement: EPSG:4326 or EPSG:4258 (geographic coordinates)
  - Functions: `create_osm_point_layer()`, `show_osm_map()`

**Web Browser Integration:**
- Default system web browser - Opens generated OSM maps
  - Library: webbrowser (Python standard library)
  - Usage: `webbrowser.open()` for displaying HTML map files
  - Location: `utilities_2026.py:253`

## Data Storage

**File-Based Storage:**
- Local filesystem only - No databases or cloud storage
- Supported formats: CSV, GeoJSON, Shapefile (.shp), PNG (raster images)
- World files (.pgw, etc.) - For georeferencing raster images
- File dialogs via tkinter.filedialog

**Coordinate Reference Systems:**
- pyproj.CRS - Handles EPSG coordinate system definitions
  - Supports transformation between any EPSG-coded CRS
  - Includes WKT (Well-Known Text) parsing from .prj files
  - Functions: `pyproj.CRS.from_epsg()`, `pyproj.CRS.from_wkt()`

## Authentication & Identity

**None**

## Monitoring & Observability

**Error Tracking:**
- None - Uses tkinter.messagebox for user-facing warnings

**Logs:**
- Console print statements for debugging
- No structured logging

## CI/CD & Deployment

**Hosting:**
- None - Desktop-only application

**CI Pipeline:**
- None detected

## Environment Configuration

**Required env vars:**
- None - Configuration via runtime parameters

**Secrets location:**
- Not applicable - No external services requiring authentication

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

## Third-Party Library Integrations

**pyproj:**
- Coordinate system transformations in `vector_2026.py` and `utilities_2026.py`
- Functions used: `Transformer.from_crs()`, `CRS.from_epsg()`, `CRS.from_wkt()`
- Key method: `projection.transform()` for point coordinate conversion

**pyshp (shapefile):**
- Shapefile reading in `utilities_2026.py`
- Functions used: `shapefile.Reader()`, `shapeRecords()`, shape parsing
- Handles binary Shapefile format with associated .dbf and .prj files

**folium:**
- Map creation in `utilities_2026.py`
- Functions used: `folium.Map()`, `folium.FeatureGroup()`, `folium.CircleMarker()`, `folium.Popup()`
- Exports to self-contained HTML files

**tkinter:**
- GUI framework - Not a service but integration with desktop environment
- Modules: `tkinter.Canvas`, `tkinter.Tk`, `tkinter.filedialog`, `tkinter.messagebox`, `tkinter.simpledialog`
- Used for all dialog boxes, file selection, and canvas drawing

---

*Integration audit: 2026-04-12*