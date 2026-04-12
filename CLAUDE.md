<!-- GSD:project-start source:PROJECT.md -->
## Project

**Norwegian Hiking Route Planner**

A desktop application that generates optimal hiking routes between coordinates in Norway using open source datasets (OpenStreetMap, GEONORGE, Kartverket) and digital terrain data. The system provides a Tkinter GUI with interactive map interface for selecting start/end points, user-configurable optimization parameters (elevation tolerance, scenic preferences), and exports routes as GPX with visualization.

**Core Value:** Generate safe, optimal hiking routes between any two points in Norway using terrain and hydrography data, with a simple interface for route planning and export.

### Constraints

- **Tech Stack**: Python 3.x, Tkinter GUI, geospatial libraries (pyproj, numpy, pyshp, folium) — user specified
- **Data Sources**: Kartverket N50/DTM50 (primary), OpenStreetMap, GEONORGE — specified by user
- **Platform**: Desktop application requiring GUI — tkinter constraint
- **Offline Capability**: Must work offline after initial download — user requirement
- **Scope Boundaries**: Norway-only, desktop-only, routing-only — v1 focus
<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->
## Technology Stack

## Languages
- Python - All code is Python-based
## Runtime
- Python 3.x
- pip (implied)
- Lockfile: Not present
## Frameworks
- tkinter - Built-in Python GUI framework for desktop applications
- numpy - Numerical computing (random, linalg modules)
- pyproj - Coordinate reference system transformations
- pyshp - Shapefile reading/writing (imported as `shapefile`)
- folium - Interactive web mapping with OpenStreetMap
## Key Dependencies
- pyproj - Core requirement for all coordinate system transformations (EPSG code handling, CRS projections)
- numpy - Used for random point generation and linear algebra operations in `vector_2026.py`
- pyshp - Required for Shapefile format support
- folium - Required for OpenStreetMap visualization
## Configuration
- No environment variables required
- Configuration via function parameters and user dialogs
- No build system - runs as Python modules
## Platform Requirements
- Python 3.x with standard library (tkinter, json, os, random, math, ast, webbrowser)
- pip package installation (pyproj, numpy, pyshp, folium)
- Desktop environment (tkinter requires graphical interface)
- Web browser (for folium map output)
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

## Naming Patterns
- Libraries: `{name}_2026.py` (e.g., `utilities_2026.py`, `vector_2026.py`, `raster_2026.py`, `screen_2026.py`)
- Main entry: `geo_2026.py` (aggregates all modules)
- Tests: `test_{name}.py` (e.g., `test_1_A1.py`, `test_1B.py`)
- Examples: `example_{description}.py` (e.g., `example_01_vector.py`, `example_103_attributes.py`)
- Exercises: `exercise_{name}.py` or `lab_{name}.py`
- Lowercase with underscores: `random_points`, `read_geojson`, `bounding_box`
- Internal methods protected with leading underscore: `_start_digit_points`, `_get_point`, `_stop_digit_points`
- Lowercase with underscores: `x_min`, `y_max`, `record_count`, `field_name`
- Private attributes protected with leading underscore: `_coordinates`, `_attributes`, `_epsg`, `_geometry`
- PascalCase: `Vector`, `Raster`, `Screen`
## Code Style
- No formal formatting tool detected (no `.prettierrc`, no `black`, no `autopep8` config)
- Manual formatting by developers
- No formal linting tool detected (no `.pylintrc`, no `flake8`, no `ruff` config)
- 4 spaces (standard Python)
- No strict limit observed (some lines exceed 80 characters)
## Import Organization
- `import utilities_2026 as utilities` (standard alias)
## Error Handling
- Bare `except:` clauses used extensively (not recommended)
- Warning GUI dialog: `utilities.warning('message')`
- Return values: functions that may fail return `None` on error
- `validate()` function in `/Users/dev/Code/School/geospatial-data-processing/utilities_2026.py` parses expressions safely
- Blocks dangerous keywords (e.g., `os`)
- Used with validation in `Vector.select()` and `Vector.calculate()`
- Considered dangerous but protected by `validate()` function
## Logging
- `print()` for debugging output
- `utilities.warning()` for user-facing warnings (tkinter message box)
- Debug comments with `#REMOVE` or inline explanations
## Comments
- Inline explanations of complex logic
- TODO markers for future work
- Section headers (e.g., `# System methods`, `# Properties`, `# User methods`)
- Removal markers for debug code (`#REMOVE`)
- Not applicable (Python codebase)
- Docstrings use triple quotes at function/class level
## Function Design
- No strict size limits
- Utility functions: 10-50 lines
- Class methods: 10-80 lines
- Largest function: `read_shapefile_points()` (`~100 lines`)
- Explicit parameters with defaults
- Pattern: `(required_params, optional_params=None)`
- Common optional: `filename=None`, `encoding='utf-8'`, `separator=','`
- `filename=None` (triggers file dialog if not provided)
- `multi=False` (for handling Multi geometry types)
- `encoding='utf-8'` for file reading
- Single values or lists/arrays
- Error cases return `None`
- Complex operations return dictionaries with status and data:
## Module Design
- Main entry point: `/Users/dev/Code/School/geospatial-data-processing/geo_2026.py`
- Imports all classes: `Vector`, `Raster`, `Screen`
- Imports utilities: `import utilities_2026 as utilities`
- `geo_2026.py` acts as aggregating module
- Three main classes: `Vector`, `Raster`, `Screen`
- Properties use `@property` decorator with explicit get/set methods
- Protected methods prefixed with `_` for internal use
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

## Pattern Overview
- Domain-driven design with core classes representing geospatial data types
- Separation of concerns between data models, utilities, and presentation
- Event-driven GUI architecture using Tkinter
- Pluggable I/O for multiple geospatial formats (GeoJSON, Shapefile, CSV)
- Coordinate reference system transformation support via pyproj
## Layers
- Purpose: Core abstractions for vector and raster geospatial data
- Location: `/Users/dev/Code/School/geospatial-data-processing/vector_2026.py`, `/Users/dev/Code/School/geospatial-data-processing/raster_2026.py`
- Contains: Vector class, Raster class
- Depends on: utilities_2026, external libraries (pyproj, shapefile)
- Used by: Screen, examples, exercises, tests
- Purpose: Shared functions for I/O, transformations, calculations, validation
- Location: `/Users/dev/Code/School/geospatial-data-processing/utilities_2026.py`
- Contains: File I/O, coordinate transformations, spatial operations, user dialogs, GeoJSON/Shapefile parsing
- Depends on: Standard library (json, os, ast), pyproj, folium, shapefile, tkinter
- Used by: Vector, Raster, Screen
- Purpose: Interactive GUI for data visualization and digitizing
- Location: `/Users/dev/Code/School/geospatial-data-processing/screen_2026.py`
- Contains: Screen class with canvas drawing, event bindings, digitizing tools
- Depends on: tkinter, Vector, Raster, utilities_2026
- Used by: examples requiring interactive display
- Purpose: Library exports and module organization
- Location: `/Users/dev/Code/School/geospatial-data-processing/geo_2026.py`
- Contains: Import statements for main classes, utilities alias
- Depends on: vector_2026, raster_2026, screen_2026, utilities_2026
- Used by: All examples, exercises, tests
## Data Flow
- Vector/Raster instances hold mutable state in private attributes with underscore prefix
- Selection sets maintained in `_selection` indices list
- EPSG codes tracked per dataset for coordinate transformations
- No database persistence - all data in-memory
## Key Abstractions
- Purpose: Represents vector geospatial data (POINT, POLYLINE, POLYGON)
- Examples: `/Users/dev/Code/School/geospatial-data-processing/examples/example_102_random_points.py`, `/Users/dev/Code/School/geospatial-data-processing/examples/example_105_folium.py`
- Pattern: Data container with geometry-specific operations, properties for controlled attribute access
- Purpose: Represents raster imagery with georeferencing
- Examples: `/Users/dev/Code/School/geospatial-data-processing/examples/example_301_raster_class.py`
- Pattern: Simple wrapper around tkinter.PhotoImage with world file metadata
- Purpose: Interactive display surface for geospatial visualization
- Examples: `/Users/dev/Code/School/geospatial-data-processing/examples/example_104_gui.py`, `/Users/dev/Code/School/geospatial-data-processing/examples/example_302_raster_gui.py`
- Pattern: Facade over tkinter Canvas with dataset management and event binding
- Purpose: Transform between different EPSG projections
- Examples: `/Users/dev/Code/School/geospatial-data-processing/examples/example_110_map_projections.py`, `/Users/dev/Code/School/geospatial-data-processing/examples/example_111_project_to_osm.py`
- Pattern: pyproj Transformer instances used for point-by-point transformation
## Entry Points
- Location: `/Users/dev/Code/School/geospatial-data-processing/geo_2026.py`
- Triggers: `import geo_2026 as geo` from examples/exercises/tests
- Responsibilities: Exports Vector, Raster, Screen classes and utilities module
- Location: Examples in `/Users/dev/Code/School/geospatial-data-processing/examples/`
- Triggers: Direct execution via `python -m examples.example_NNN`
- Responsibilities: Demonstrate library features with data processing and visualization
- Location: `/Users/dev/Code/School/geospatial-data-processing/tests/`
- Triggers: Execution via test runner
- Responsibilities: Verify library functionality
## Error Handling
- User input validation via `utilities.validate()` - parses expression AST to block dangerous modules
- File I/o errors caught with try-except, return None or status dictionaries
- Warnings displayed via `tkinter.messagebox.showwarning()`
- Returns early from methods on error conditions
- Silent failures in some corner cases (e.g., shapefile geometry type mismatch)
## Cross-Cutting Concerns
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, or `.github/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
