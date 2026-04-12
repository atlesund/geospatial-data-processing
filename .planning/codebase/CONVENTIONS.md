# Coding Conventions

**Analysis Date:** 2026-04-12

## Naming Patterns

**Files:**
- Libraries: `{name}_2026.py` (e.g., `utilities_2026.py`, `vector_2026.py`, `raster_2026.py`, `screen_2026.py`)
- Main entry: `geo_2026.py` (aggregates all modules)
- Tests: `test_{name}.py` (e.g., `test_1_A1.py`, `test_1B.py`)
- Examples: `example_{description}.py` (e.g., `example_01_vector.py`, `example_103_attributes.py`)
- Exercises: `exercise_{name}.py` or `lab_{name}.py`

**Functions:**
- Lowercase with underscores: `random_points`, `read_geojson`, `bounding_box`
- Internal methods protected with leading underscore: `_start_digit_points`, `_get_point`, `_stop_digit_points`

**Variables:**
- Lowercase with underscores: `x_min`, `y_max`, `record_count`, `field_name`
- Private attributes protected with leading underscore: `_coordinates`, `_attributes`, `_epsg`, `_geometry`

**Types (Classes):**
- PascalCase: `Vector`, `Raster`, `Screen`

## Code Style

**Formatting:**
- No formal formatting tool detected (no `.prettierrc`, no `black`, no `autopep8` config)
- Manual formatting by developers

**Linting:**
- No formal linting tool detected (no `.pylintrc`, no `flake8`, no `ruff` config)

**Indentation:**
- 4 spaces (standard Python)

**Line length:**
- No strict limit observed (some lines exceed 80 characters)

## Import Organization

**Order:**
1. Standard library (`import os`, `import sys`)
2. Third-party libraries (`import tkinter`, `import pyproj`, `from numpy import random`)
3. Local modules (`import utilities_2026 as utilities`, `from vector_2026 import Vector`)

**Common pattern:**
```python
import geo_2026 as geo

dataset = geo.Vector()
```

**Module aliases:**
- `import utilities_2026 as utilities` (standard alias)

## Error Handling

**Patterns:**
- Bare `except:` clauses used extensively (not recommended)
- Warning GUI dialog: `utilities.warning('message')`
- Return values: functions that may fail return `None` on error

**Example patterns:**
```python
try:
    # operation
except:
    result = None

if result is None:
    utilities.warning('Error message')
    return
```

**Validation:**
- `validate()` function in `/Users/dev/Code/School/geospatial-data-processing/utilities_2026.py` parses expressions safely
- Blocks dangerous keywords (e.g., `os`)

**eval/exec usage:**
- Used with validation in `Vector.select()` and `Vector.calculate()`
- Considered dangerous but protected by `validate()` function

## Logging

**Framework:** `print()` statements and GUI dialogs

**Patterns:**
- `print()` for debugging output
- `utilities.warning()` for user-facing warnings (tkinter message box)
- Debug comments with `#REMOVE` or inline explanations

**Example:**
```python
print('Start digitising mode...')
print(screen._points)

# Debug statements with REMOVE marker:
print(f'WORLD FILE SET IN READ_IMAGE (F5): {self._world_file}') #REMOVE
```

## Comments

**When to Comment:**
- Inline explanations of complex logic
- TODO markers for future work
- Section headers (e.g., `# System methods`, `# Properties`, `# User methods`)
- Removal markers for debug code (`#REMOVE`)

**JSDoc/TSDoc:**
- Not applicable (Python codebase)
- Docstrings use triple quotes at function/class level

**Docstring pattern:**
```python
def random_points(self, n, x_min, y_min, x_max, y_max):
    """
    Docstring for random_points

    :param self: Description
    :param n: number of radom points
    :params x_min, y_min, x_max, y_max: bounding box
    """
```

**TODO pattern:**
```python
# TODO: check that the EPSG code is valid (return None)
# TODO: Create projection
# TODO: Store control coordinates
```

## Function Design

**Size:**
- No strict size limits
- Utility functions: 10-50 lines
- Class methods: 10-80 lines
- Largest function: `read_shapefile_points()` (`~100 lines`)

**Parameters:**
- Explicit parameters with defaults
- Pattern: `(required_params, optional_params=None)`
- Common optional: `filename=None`, `encoding='utf-8'`, `separator=','`

**Default values:**
- `filename=None` (triggers file dialog if not provided)
- `multi=False` (for handling Multi geometry types)
- `encoding='utf-8'` for file reading

**Return Values:**
- Single values or lists/arrays
- Error cases return `None`
- Complex operations return dictionaries with status and data:
```python
report = {
    'status': False,
    'message': '',
    'coordinates': [],
    'attributes': [],
    'epsg': 'None'
}
```

## Module Design

**Exports:**
- Main entry point: `/Users/dev/Code/School/geospatial-data-processing/geo_2026.py`
- Imports all classes: `Vector`, `Raster`, `Screen`
- Imports utilities: `import utilities_2026 as utilities`

**Barrel Files:**
- `geo_2026.py` acts as aggregating module

**Module structure:**
```
geo_2026.py        (main entry, imports everything)
├── vector_2026.py (Vector class)
├── raster_2026.py (Raster class)
├── screen_2026.py (Screen class)
├── utilities_2026.py (helper functions)
└── tests/         (test files)
```

**Class design:**
- Three main classes: `Vector`, `Raster`, `Screen`
- Properties use `@property` decorator with explicit get/set methods
- Protected methods prefixed with `_` for internal use

**Property pattern:**
```python
def _get_epsg(self):
    return self._epsg

def _set_epsg(self, epsg_code):
    self._epsg = epsg_code

epsg = property(fget=_get_epsg, fset=_set_epsg)
```

---

*Convention analysis: 2026-04-12*