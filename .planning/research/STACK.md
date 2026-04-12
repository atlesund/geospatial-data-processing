# Stack Recommendations — Norwegian Hiking Route Planner

**Researched:** 2026-04-12
**Overall confidence:** MEDIUM (Web search functionality was limited, recommendations based on established geospatial industry standards)

## Terrain Data Access

**Recommended**: `requests` + URL-based API access to Kartverket
- **Rationale**: Kartverket provides WMS/WCS services and direct download URLs for N50 DTM50. No official Python SDK exists, so HTTP requests are standard. Use `requests` for API calls and file downloads.
- **Usage**: 
  ```python
  import requests
  
  # Download DTM50 data via Kartverket API
  url = "https://wms.geonorge.no/kartverket/geowebcache/service/wms"
  params = {
      'service': 'WMS',
      'request': 'GetMap',
      'layers': 'dtm50',
      'format': 'image/tiff',
      'bbox': ...,
      'crs': 'EPSG:4326'
  }
  response = requests.get(url, params=params)
  ```
- **Confidence**: MEDIUM
  - Based on standard WMS/WCS access patterns
  - Official Kartverket documentation couldn't be verified due to search limitations

**Alternatives**:
- `GDAL` command-line tools wrapped in Python subprocess
- `owslib` library for OGC WMS/WCS services

## OSM Data Extraction

**Recommended**: `osmnx` 1.x
- **Rationale**: Industry-standard library for extracting OpenStreetMap data and building routing networks. Includes filters for path types (foot paths, hiking routes, steps, etc.) and automatic network topology construction. Integrates with NetworkX for routing.
- **Usage**:
  ```python
  import osmnx as ox
  
  # Extract hiking-specific graph
  G = ox.graph_from_place(
      "Norway",
      network_type='walk',
      custom_filter='["highway"~"path|footway|track"]'
  )
  
  # Extract specific hiking trails by tags
  trails = ox.geometries_from_place(
      "Norway",
      tags={'highway': ['path', 'footway', 'track']}
  )
  ```
- **Confidence**: HIGH
  - osmnx is well-established, actively maintained (2024+ releases)
  - Standard tool for OSM-based routing in Python research community

**Alternatives**:
- `overpy` for Overpass API queries (lower level)
- `pyosmium` for reading OSM PBF files (for bulk import)
- Direct Overpass API HTTP requests (for custom queries)

## Path Finding / Routing

**Recommended**: `networkx` (extends existing numpy dependency) with custom weight functions
- **Rationale**: Already using numpy in the project, so networkx maintains consistency. NetworkX provides A* and Dijkstra implementations out of the box with support for custom edge weights. Build routing as a weighted graph where edges get costs from terrain difficulty (elevation change, slope, surface type).
- **Usage**:
  ```python
  import networkx as nx
  import osmnx as ox
  
  # Convert OSM graph to NetworkX
  G_multigraph = ox.graph_to_gdfs(G)
  G = nx.DiGraph()
  
  # Add edges with custom weights from terrain
  for _, edge in edge_df.iterrows():
      elevation_diff = sample_elevation_at_coords(edge.geometry)
      slope = calculate_slope(elevation_diff, edge.length)
      cost = base_cost + slope_factor * slope
      
      G.add_edge(u, v, weight=cost, length=edge.length)
  
  # Find path between two points
  path = nx.astar_path(G, origin_node, dest_node, weight='weight')
  ```
- **Confidence**: HIGH
  - NetworkX is mature, well-documented (GitHub repo active)
  - Custom weight functions are standard use case
  - Integrating with existing numpy/pyproj stack is straightforward

**Alternatives**:
- `osmnx.routing` built-in routing (simpler but less customizable for terrain costs)
- `networkit` (faster for very large graphs, but smaller ecosystem)

## DEM Processing

**Recommended**: `rasterio` 1.x + `rioxarray` wrapper
- **Rationale**: Rasterio provides the standard Python interface to GDAL for efficient georeferenced raster I/O. Rioxarray adds xarray integration for easier data analysis. Use rasterio to:
  - Read DTM50 geotiffs from Kartverket
  - Sample elevation at specific coordinates
  - Reproject between coordinate systems (EPSG transformations)
  - Compute slopes and aspect from elevation data
- **Usage**:
  ```python
  import rasterio
  from rasterio.warp import transform_geom
  import numpy as np
  
  # Load DEM
  with rasterio.open('dtm50.tif') as src:
      elevation = src.read(1)
      transform = src.transform
      crs = src.crs
      
      # Sample elevation at point (GPS coordinates)
      def sample_elevation(lon, lat):
          row, col = src.index(lon, lat)
          return elevation[row, col]
      
      # Compute slope from DEM
      dy, dx = np.gradient(elevation)
      slope = np.arctan(np.sqrt(dx**2 + dy**2))
  ```
- **Confidence**: HIGH
  - Rasterio is the industry standard for Python raster I/O
  - Active development, extensive documentation
  - Compatible with geospatial CRS handling via pyproj (already in use)

**Alternatives**:
- `GDAL` Python bindings (`osgeo.gdal`) -- more powerful but more complex API
- `xarray` with `rioxarray` directly (for array-based workflows)

## Offline Storage

**Recommended**: `GeoPackage` via `fiona` or `geopandas`
- **Rationale**: GeoPackage is the modern,开放的标准 for storing both vector and raster geospatial data in a single SQLite file. It's:
  - Readable by QGIS, ArcGIS, and most GIS tools
  - Supports raster tiles (can store downloaded DTM50 chunks)
  - Supports vector data (OSM trails, GPX routes)
  - Single-file solution for offline use
  - No separate database setup required
- **Usage**:
  ```python
  import fiona
  
  # Write vector data to GeoPackage
  schema = {
      'geometry': 'LineString',
      'properties': {'name': 'str', 'length': 'float'}
  }
  
  with fiona.open(
      'hiking_routes.gpkg',
      'w',
      driver='GPKG',
      schema=schema,
      crs='EPSG:4326'
  ) as dst:
      dst.write(feature)
  
  # Raster can be stored using GDAL's GeoPackage driver
  ```
- **Confidence**: HIGH
  - GeoPackage is OGC standard, officially recommended
  - Fiona and GDAL have full support
  - Industry best practice for offline geospatial storage

**Alternatives**:
- `Spatialite` (SQLite with spatial extensions) — good for query-heavy use cases
- Flat files (GeoJSON + GeoTIFF) — simpler but no single-file access

## Elevation Profile

**Recommended**: Custom implementation using rasterio sampling
- **Rationale**: No dedicated library needed. Elevation profiles are straightforward to compute by:
  1. Sampling the DEM at regular intervals along the route geometry
  2. Computing cumulative distance
  3. Plotting using matplotlib (already common in scientific Python)
- **Usage**:
  ```python
  import numpy as np
  import matplotlib.pyplot as plt
  from shapely.geometry import LineString
  import rasterio
  
  def compute_elevation_profile(route_line, dem_path, num_samples=100):
      """Return (distances_m, elevations_m) arrays"""
      with rasterio.open(dem_path) as src:
          # Sample at regular intervals
          coords = [route_line.interpolate(d/max_d, normalized=True).coords[0]
                   for d in np.linspace(0, max_d, num_samples)]
          
          elevations = [sample_dem_at_point(coord, src) for coord in coords]
      
      # Compute cumulative distances
      distances = np.linspace(0, route_line.length, num_samples)
      
      return distances, np.array(elevations)
  ```
- **Confidence**: HIGH
  - This is standard pattern, not a domain where specialized libraries exist
  - Integrates directly with rasterio from DEMProcessing

**Alternatives**:
- None significant — custom implementation is standard approach

## GPX Export

**Recommended**: `gpxpy` 1.x
- **Rationale**: gpxpy is the most widely used Python library for reading and writing GPX files. It:
  - Supports all GPX required elements (tracks, routes, waypoints)
  - Properly handles elevation, time, and metadata
  - Has simple API for writing track segments
  - Lightweight, no heavy dependencies
- **Usage**:
  ```python
  import gpxpy
  from gpxpy.gpx import GPXTrack, GPXTrackSegment, GPXTrackPoint
  
  gpx = gpxpy.gpx.GPX()
  
  track = GPXTrack()
  gpx.tracks.append(track)
  
  segment = GPXTrackSegment()
  track.segments.append(segment)
  
  # Add points from route
  for coord, elevation in zip(route_coords, elevations):
      point = GPXTrackPoint(latitude=coord[1], longitude=coord[0], elevation=elevation)
      segment.points.append(point)
  
  # Write to file
  with open('route.gpx', 'w') as f:
      f.write(gpx.to_xml())
  ```
- **Confidence**: MEDIUM
  - gpxpy is established but maintenance has slowed (last release ~2022)
  - Still works well for basic GPX writing
  - No widely used alternative exists

**Alternatives**:
- Custom XML generation (GPX is simple XML format)
- `gpxkml` (less common)

## Scenic Feature Detection

**Recommended**: Custom implementation using rasterio + spatial queries
- **Rationale**: "Scenic" is subjective, but implementable proxies include:
  - **Water proximity**: Query nearby lakes/rivers from OSM water features, or use National Land Cover datasets
  - **Mountain views**: Compute horizon from DEM ray-tracing (when elevation gain > threshold)
  - **Valleys**: Detect low-elevation corridors surrounded by higher terrain
  - **Shoreline**: Check distance to coastline using OSM coastline features
  
  Build as analysis functions that compute scenic scores along route candidates.
- **Usage**:
  ```python
  from shapely.geometry import Point
  
  def compute_scenic_score(point, water_features, dem):
      # Water proximity (0-1)
      water_dist = min(point.distance(w.geometry) for w in water_features)
      water_score = 1 / (1 + water_dist / 1000)  # Normalized
      
      # Elevation prominence (how high above surrounding terrain)
      elevation = sample_elevation(point, dem)
      local_avg = compute_local_avg_elevation(point, dem, radius=1000)
      prominence_score = max(0, (elevation - local_avg) / 500)
      
      # Combined score
      return 0.6 * water_score + 0.4 * prominence_score
  ```
- **Confidence**: MEDIUM
  - This is a research/machine learning problem, not a solved tool domain
  - Approaches are application-specific
  - Implementation based on standard geospatial analysis techniques

**Alternatives**:
- Pre-computed scenic scores from external datasets (if available for Norway)

## Integration with Existing Stack

The following must integrate with existing codebase:

### Coordinate Transforms
- **Existing**: `pyproj` for EPSG transformations
- **New req**: All new components must work with pyproj CRS objects
- **Integration**: Pass `epsg` codes between Vector, Raster, and new classes. Use pyproj transformers in terrain sampling and route calculations.

### Vector Class
- **Existing**: GPS coordinates and route polylines
- **New req**: Route polylines from pathfinding must be Vector(POLYLINE) objects
- **Integration**: Convert osmnx/networkx route edge sequences to Vector coordinate lists. Store route metadata as attributes (elevation gain, scenic score, estimated time).

### Raster Class
- **Existing**: Georeferenced images for display
- **New req**: DTM50 terrain data for routing costs
- **Integration**: Extend Raster to support geotiff loading via rasterio. Store DEM as `Raster` with `epsg: 4326` or EPSG:32632-32636 (UTM zones). The `_photoimage` can remain for visual display, but add method to access underlying rasterio dataset for computation.

### Screen Class
- **Existing**: Tkinter canvas for digitizing and display
- **New req**: Visualizing routes, elevation profiles, terrain backgrounds
- **Integration**: 
  - Use existing `draw_polyline()` for route display
  - Add elevation profile plotting to canvas (using matplotlib backend)
  - Load terrain as raster background with `read_image()` → `draw_image()` flow
  - Preserve F5/F9/F10/F12 workflow for route digitizing

### Data Flow Integration
```
User selects start/end points (Screen digitizing)
    ↓
Start/end to Vector coordinates (screen_to_world)
    ↓
OSM graph extraction (osmnx) → NetworkX graph
    ↓
Edge costs from DEM (rasterio sampling)
    ↓
Path finding (NetworkX A*)
    ↓
Route to Vector(POLYLINE)
    ↓
Elevation profile (custom)
    ↓
Display on Screen + GPX export (gpxpy)
```

## What NOT to Use

- **PostGIS** — Overkill for local offline use, introduces database complexity. Use GeoPackage instead.
- **Routing engines (OSRM, GraphHopper)** — Require server infrastructure. NetworkX works completely offline.
- **ArcGIS/ArcGIS API for Python** — Proprietary, expensive, conflicts with open-source ecosystem. Use GDAL ecosystem.
- **Google Maps API** — Not free for hiking routes, doesn't provide terrain data. Use OpenStreetMap.
- **RTree** — NetworkX has built-in spatial indexing, RTree adds complexity without clear benefit.
- **pandana** — Specialized for urban accessibility, not terrain-based routing.
- **geopandas** (for most operations) — Heavy dependency, overkill if not doing spatial joins/aggregations. Use shapely + rasterio for individual operations.

## Dependencies Summary

**Add to requirements.txt:**
```
osmnx>=1.9.0
networkx>=3.0
rasterio>=1.3.0
rioxarray>=0.15.0
gpxpy>=1.5.0
fiona>=1.9.0
shapely>=2.0.0
```

**Already in use (domain-confirmed):**
```
pyproj
numpy
folium
pyshp
tkinter
```

*Research completed: 2026-04-12*