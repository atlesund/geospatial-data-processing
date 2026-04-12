# Testing Patterns

**Analysis Date:** 2026-04-12

## Test Framework

**Runner:**
- No formal test framework detected (pytest, unittest, nose not configured)
- No test configuration file (no `pytest.ini`, `setup.cfg`, `pyproject.toml` with pytest config)
- Tests are manual scripts that import modules and print results

**Assertion Library:**
- Uses Python's built-in `print()` for verification

**Run Commands:**
```bash
# Run test manually
python tests/test_1_A1.py

# Run all tests (manual, no command provided)
for f in tests/test_*.py; do python "$f"; done
```

**Coverage:**
- No coverage tool detected (no pytest-cov, coverage.py)

## Test File Organization

**Location:**
- Separate directory: `/Users/dev/Code/School/geospatial-data-processing/tests/`

**Naming:**
- Pattern: `test_{chapter}_{variant}.py` (e.g., `test_1_A1.py`, `test_1B.py`)
- Variants: A1, A2, A3, B (suggests lab/session structure)

**Structure:**
```
tests/
├── test_1_A1.py       # Basic module test
├── test_1_A2.py       # Polygon reading test
├── test_1_A3.py       # Multi-geometry test
└── test_1B.py         # Import access test
```

## Test Structure

**Suite Organization:**
Tests are simple scripts, not formal test suites:

```python
# Example from test_1_A1.py
import geo_2026 as geo

counts = geo.utilities.describe_geojson()
print(counts)
```

```python
# Example from test_1_A2.py
import geo_2026 as geo

dataset = geo.Vector(geometry='POLYGON')
dataset.read_geojson()
print(dataset)
```

```python
# Example from test_1_A3.py
import geo_2026 as geo

dataset = geo.Vector(geometry='POLYGON')
dataset.read_geojson(multi=True)
print(dataset)
```

```python
# Example from test_1B.py
from vector_2026 import Vector
from raster_2026 import Raster
from screen_2026 import Screen

import utilities_2026 as utilities
```

**Patterns:**
- Setup: Import geo_2026 module
- Test: Call function and print result
- Teardown: None (no cleanup)
- Assertion: Visual inspection of printed output

**What each test covers:**
- `test_1_A1.py`: Tests `describe_geojson()` utility function
- `test_1_A2.py`: Tests reading GeoJSON with Polygon geometry
- `test_1_A3.py`: Tests reading MultiPolygon geometry (multi=True parameter)
- `test_1B.py`: Verifies module imports (no actual test logic, just imports)

## Mocking

**Framework:** None (pytest-mock, unittest.mock not used)

**Patterns:**
- No mocking observed
- Tests use real file dialogs via `utilities.input_file()`
- Requires manual file selection during test execution

**What to Mock:**
- Not applicable - no formal mocking framework

**What NOT to Mock:**
- No guidelines available (no tests with mocks existing)

## Fixtures and Factories

**Test Data:**
- No fixture system detected
- Test data located in: `/Users/dev/Code/School/geospatial-data-processing/data/`

**Location:**
- `/Users/dev/Code/School/geospatial-data-processing/data/` directory exists but contents not analyzed

**Pattern:**
- Tests require manual file selection via GUI dialogs
- No programmatic test data generation

## Coverage

**Requirements:** None (no coverage enforcement)

**View Coverage:**
- No coverage report available
- No coverage measurement tools configured

**Coverage status:**
- No automated coverage tracking
- Manual verification only

## Test Types

**Unit Tests:**
- Limited implementation
- Existing tests are more like integration tests (import modules, call methods, print results)
- Test files exercise single functions from utilities_2026.py

**Integration Tests:**
- Primary testing approach
- Tests interactions between geo_2026 and its components
- Tests file I/O operations (read_geojson, read_shapefile, etc.)

**E2E Tests:**
- Not used
- No automated end-to-end testing framework

## Common Patterns

**Loading GeoJSON data:**
```python
import geo_2026 as geo

dataset = geo.Vector(geometry='POINT')
dataset.read_geojson()
print(dataset)
```

**Reading Multi-geometry types:**
```python
import geo_2026 as geo

dataset = geo.Vector(geometry='POLYGON')
dataset.read_geojson(multi=True)
print(dataset)
```

**Using utility functions:**
```python
import geo_2026 as geo

counts = geo.utilities.describe_geojson()
print(counts)
```

**Direct module imports:**
```python
from vector_2026 import Vector
from raster_2026 import Raster
from screen_2026 import Screen

import utilities_2026 as utilities
```

**Pattern limitations:**
- Tests require interactive GUI dialogs (file selection)
- No assertions, only print statements
- No setup/teardown logic
- No test isolation (no fixtures or test-specific data)

**Example-based testing:**
Examples in `/Users/dev/Code/School/geospatial-data-processing/examples/` serve as documentation and informal tests:

- `example_01_vector.py`: Basic Vector class usage
- `example_102_random_points.py`: Generate random points
- `example_103_attributes.py`: Add and manipulate attributes
- `example_104_gui.py`: GUI binding patterns
- `example_105_folium.py`: OSM map visualization
- `example_110_map_projections.py`: Coordinate projections
- `example_111_project_to_osm.py`: Projection to OSM
- And more...

---

*Testing analysis: 2026-04-12*