# Codebase Structure

**Analysis Date:** 2026-04-12

## Directory Layout

```
geospatial-data-processing/
├── data/                   # Test datasets
├── docs/                   # Documentation
├── examples/               # Example scripts demonstrating library usage
├── exercises/              # Lab exercises for students
├── tests/                  # Unit tests
├── .planning/              # Planning documents (GSD framework)
├── geo_2026.py             # Library entry point
├── vector_2026.py          # Vector data class
├── raster_2026.py          # Raster data class
├── screen_2026.py          # GUI display class
├── utilities_2026.py       # Utility functions
├── utilities_07_validate.py # Empty placeholder
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
└── .gitignore              # Git ignore rules
```

## Directory Purposes

**data/:**
- Purpose: Contains sample geospatial datasets for testing and examples
- Contains: CSV files, GeoJSON files, shapefile components
- Key files: `polylines.csv`

**docs/:**
- Purpose: Reference documentation and guides
- Contains: Markdown documentation files
- Key files: `geo_2026_reference.md`

**examples/:**
- Purpose: Demonstrative scripts showing library features and usage patterns
- Contains: Python scripts (`example_NNN_*.py` pattern)
- Key files: `example_01_vector.py`, `example_105_folium.py`, `example_201_digit.py`, `example_309_affine_transformation.py`

**exercises/:**
- Purpose: Student lab exercises and assignments
- Contains: Python scripts for extended practice
- Key files: `exercise_01.py`, `exercise_2a.py`, `lab_2a.py`

**tests/:**
- Purpose: Unit tests for library functionality
- Contains: Python test scripts
- Key files: `test_1_A1.py`, `test_1_A2.py`, `test_1_A3.py`, `test_1B.py`

**.planning/:**
- Purpose: GSD framework planning documents (not part of the library)
- Contains: Generated architecture and structure analysis
- Key files: `ARCHITECTURE.md`, `STRUCTURE.md`

## Key File Locations

**Entry Points:**
- `/Users/dev/Code/School/geospatial-data-processing/geo_2026.py`: Library exports (imports Vector, Raster, Screen, utilities)

**Configuration:**
- `/Users/dev/Code/School/geospatial-data-processing/requirements.txt`: Python package dependencies
- `/Users/dev/Code/School/geospatial-data-processing/.gitignore`: Git ignore patterns

**Core Logic:**
- `/Users/dev/Code/School/geospatial-data-processing/vector_2026.py`: Vector geospatial data class (192 lines)
- `/Users/dev/Code/School/geospatial-data-processing/raster_2026.py`: Raster geospatial data class (57 lines)
- `/Users/dev/Code/School/geospatial-data-processing/screen_2026.py`: GUI display class (296 lines)
- `/Users/dev/Code/School/geospatial-data-processing/utilities_2026.py`: Utility functions (857 lines)

**Testing:**
- `/Users/dev/Code/School/geospatial-data-processing/tests/`: Test scripts for library verification

**Examples/Demonstration:**
- `/Users/dev/Code/School/geospatial-data-processing/examples/`: Usage examples and feature demonstrations
- `/Users/dev/Code/School/geospatial-data-processing/exercises/`: Lab exercises

## Naming Conventions

**Files:**
- Core modules: `{domain}_2026.py` pattern (e.g., `vector_2026.py`, `raster_2026.py`)
- Examples: `example_{number}_{topic}.py` pattern (e.g., `example_102_random_points.py`)
- Tests: `test_{number}_{part}.py` pattern (e.g., `test_1_A1.py`)
- Exercises: `exercise_{number}.py` or `lab_{number}.py` pattern

**Directories:**
- Lowercase names: `data`, `docs`, `examples`, `exercises`, `tests`

**Python Classes:**
- PascalCase: `Vector`, `Raster`, `Screen`

**Python Methods:**
- snake_case: `random_points()`, `read_geojson()`, `screen_to_world()`
- Protected methods: underscore prefix: `_read_image()`, `_get_point()`

**Python Variables:**
- Private attributes: underscore prefix: `_coordinates`, `_attributes`, `_epsg`
- Public properties: no underscore: `coordinates`, `attributes`, `epsg`

## Where to Add New Code

**New Geospatial Operations:**
- Primary code: `/Users/dev/Code/School/geospatial-data-processing/utilities_2026.py` (for pure functions)
- Method additions: `/Users/dev/Code/School/geospatial-data-processing/vector_2026.py` (for Vector class methods)
- Tests: `/Users/dev/Code/School/geospatial-data-processing/tests/`

**New File Format Support:**
- Implementation: `/Users/dev/Code/School/geospatial-data-processing/utilities_2026.py` (read/write functions)
- Vector/Raster integration: `/Users/dev/Code/School/geospatial-data-processing/vector_2026.py` or `/Users/dev/Code/School/geospatial-data-processing/raster_2026.py` (wrapper methods)

**New GUI Features:**
- Implementation: `/Users/dev/Code/School/geospatial-data-processing/screen_2026.py` (Screen class methods)
- Examples: `/Users/dev/Code/School/geospatial-data-processing/examples/` (demonstration scripts)

**New Component/Module:**
- Implementation: `{module_name}_2026.py` in root directory
- Export: Add import to `/Users/dev/Code/School/geospatial-data-processing/geo_2026.py`

**Utilities:**
- Shared helpers: `/Users/dev/Code/School/geospatial-data-processing/utilities_2026.py` (existing utilities module)

**Documentation:**
- Reference docs: `/Users/dev/Code/School/geospatial-data-processing/docs/`

## Special Directories

**data/:**
- Purpose: Sample datasets for testing and demonstration
- Generated: No
- Committed: Yes

**.planning/:**
- Purpose: GSD framework planning documents
- Generated: Yes (by GSD commands)
- Committed: Yes

**__pycache__/ (not visible):**
- Purpose: Python bytecode cache
- Generated: Yes (by Python interpreter)
- Committed: No (.gitignore excludes it)

---

*Structure analysis: 2026-04-12*