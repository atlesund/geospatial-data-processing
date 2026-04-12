# Architecture

**Analysis Date:** 2026-04-12

## Pattern Overview

**Overall:** Object-oriented modular library with utility functions

**Key Characteristics:**
- Domain-driven design with core classes representing geospatial data types
- Separation of concerns between data models, utilities, and presentation
- Event-driven GUI architecture using Tkinter
- Pluggable I/O for multiple geospatial formats (GeoJSON, Shapefile, CSV)
- Coordinate reference system transformation support via pyproj

## Layers

**Data Model Layer:**
- Purpose: Core abstractions for vector and raster geospatial data
- Location: `/Users/dev/Code/School/geospatial-data-processing/vector_2026.py`, `/Users/dev/Code/School/geospatial-data-processing/raster_2026.py`
- Contains: Vector class, Raster class
- Depends on: utilities_2026, external libraries (pyproj, shapefile)
- Used by: Screen, examples, exercises, tests

**Utilities Layer:**
- Purpose: Shared functions for I/O, transformations, calculations, validation
- Location: `/Users/dev/Code/School/geospatial-data-processing/utilities_2026.py`
- Contains: File I/O, coordinate transformations, spatial operations, user dialogs, GeoJSON/Shapefile parsing
- Depends on: Standard library (json, os, ast), pyproj, folium, shapefile, tkinter
- Used by: Vector, Raster, Screen

**Presentation Layer:**
- Purpose: Interactive GUI for data visualization and digitizing
- Location: `/Users/dev/Code/School/geospatial-data-processing/screen_2026.py`
- Contains: Screen class with canvas drawing, event bindings, digitizing tools
- Depends on: tkinter, Vector, Raster, utilities_2026
- Used by: examples requiring interactive display

**Integration Layer:**
- Purpose: Library exports and module organization
- Location: `/Users/dev/Code/School/geospatial-data-processing/geo_2026.py`
- Contains: Import statements for main classes, utilities alias
- Depends on: vector_2026, raster_2026, screen_2026, utilities_2026
- Used by: All examples, exercises, tests

## Data Flow

**Reading Data:**

1. User calls read method on Vector instance (`read_geojson()`, `read_shapefile()`, `read_csv()`)
2. Method delegates to utilities layer (`read_geojson_points()`, `read_shapefile_points()`, `read_csv_points()`)
3. Utilities layer parses file format, extracts coordinates and attributes
4. Vector instance updates internal state (`_coordinates`, `_attributes`, `_epsg`, `_source`, `_format`)

**Processing Data:**

1. User calls operation on Vector instance (`select()`, `calculate()`, `project()`, `bounding_box()`)
2. Method validates input (via utilities layer if needed)
3. Operation modifies in-memory data
4. For projections: uses pyproj Transformer to convert coordinates between EPSG codes
5. For selections: uses `eval()` on validated expressions (security concern)

**Displaying Data (GUI):**

1. User creates Screen instance with dimensions and background
2. Screen instantiates internal Vector and Raster datasets for points, polylines, polygons, image
3. User binds event handlers (keyboard/mouse) via `keyboard_bind()` or `mouse_bind()`
4. Tkinter event loop runs via `loop()` method
5. Callback functions invoke drawing methods (`draw_point()`, `draw_polyline()`, `draw_polygon()`)
6. Drawing methods render to tkinter canvas with tags for deletion

**Digitizing Flow:**

1. User presses F9 to start digitizing mode
2. Screen binds left-click to `_get_point()` callback
3. Each click stores screen coordinate in `_digits` Vector instance
4. User presses F12 to export digitized points to GeoJSON
5. Method transforms screen coordinates to world coordinates using world file (`utilities.screen_to_world()`)
6. Coordinates projected to EPSG:4326 if needed
7. GeoJSON written via `utilities.write_geojson_points()`

**State Management:**
- Vector/Raster instances hold mutable state in private attributes with underscore prefix
- Selection sets maintained in `_selection` indices list
- EPSG codes tracked per dataset for coordinate transformations
- No database persistence - all data in-memory

## Key Abstractions

**Vector:**
- Purpose: Represents vector geospatial data (POINT, POLYLINE, POLYGON)
- Examples: `/Users/dev/Code/School/geospatial-data-processing/examples/example_102_random_points.py`, `/Users/dev/Code/School/geospatial-data-processing/examples/example_105_folium.py`
- Pattern: Data container with geometry-specific operations, properties for controlled attribute access

**Raster:**
- Purpose: Represents raster imagery with georeferencing
- Examples: `/Users/dev/Code/School/geospatial-data-processing/examples/example_301_raster_class.py`
- Pattern: Simple wrapper around tkinter.PhotoImage with world file metadata

**Screen:**
- Purpose: Interactive display surface for geospatial visualization
- Examples: `/Users/dev/Code/School/geospatial-data-processing/examples/example_104_gui.py`, `/Users/dev/Code/School/geospatial-data-processing/examples/example_302_raster_gui.py`
- Pattern: Facade over tkinter Canvas with dataset management and event binding

**Coordinate Reference System:**
- Purpose: Transform between different EPSG projections
- Examples: `/Users/dev/Code/School/geospatial-data-processing/examples/example_110_map_projections.py`, `/Users/dev/Code/School/geospatial-data-processing/examples/example_111_project_to_osm.py`
- Pattern: pyproj Transformer instances used for point-by-point transformation

## Entry Points

**Library Usage:**
- Location: `/Users/dev/Code/School/geospatial-data-processing/geo_2026.py`
- Triggers: `import geo_2026 as geo` from examples/exercises/tests
- Responsibilities: Exports Vector, Raster, Screen classes and utilities module

**Interactive Scripts:**
- Location: Examples in `/Users/dev/Code/School/geospatial-data-processing/examples/`
- Triggers: Direct execution via `python -m examples.example_NNN`
- Responsibilities: Demonstrate library features with data processing and visualization

**Tests:**
- Location: `/Users/dev/Code/School/geospatial-data-processing/tests/`
- Triggers: Execution via test runner
- Responsibilities: Verify library functionality

## Error Handling

**Strategy:** Partial validation with warning dialogs

**Patterns:**
- User input validation via `utilities.validate()` - parses expression AST to block dangerous modules
- File I/o errors caught with try-except, return None or status dictionaries
- Warnings displayed via `tkinter.messagebox.showwarning()`
- Returns early from methods on error conditions
- Silent failures in some corner cases (e.g., shapefile geometry type mismatch)

## Cross-Cutting Concerns

**Logging:** Print statements to stdout (no logging framework)

**Validation:** AST-based expression parsing in `utilities.validate()`, field existence checks in Vector.select() and Vector.calculate()

**Authentication:** None - standalone library with no network services

**Coordinate Systems:** EPSG codes tracked per Vector/Raster instance, pyproj used for transformations

**File Formats:** Supported via format-specific utility functions (read_geojson_points, read_shapefile_points, read_csv_points)

---

*Architecture analysis: 2026-04-12*