# Phase 1 Tests

Test suite for Phase 01: Map Interaction and User Selection.

## Directory Structure

```
tests/
├── conftest.py          # Pytest fixtures and configuration
├── README.md            # This file
└── data/                # Test data directory
    ├── .gitkeep         # Ensures directory is tracked
    └── test_world.pgw   # Mock world file for UTM 32V testing
```

## Available Fixtures

### `screen()`
Creates a Screen instance with default dimensions (800x600 pixels).

```python
def test_with_screen(screen):
    """Test using default screen fixture."""
    assert screen._columns == 800
    assert screen._rows == 600
```

### `screen_with_world_file(mock_world_file, mock_epsg)`
Creates a Screen instance with mock world file and EPSG code set for UTM 32V coordinate transformations.

```python
def test_with_georeferenced_screen(screen_with_world_file):
    """Test using georeferenced screen fixture."""
    assert screen_with_world_file._world_file[4] == 450000.0  # top_left_x
    assert screen_with_world_file._epsg == 4326
```

### `mock_world_file()`
Returns affine transformation tuple for UTM 32V:
- `[pixel_width, rotation_x, rotation_y, pixel_height, top_left_x, top_left_y]`
- Values: `[12.0, 0.0, 0.0, -12.0, 450000.0, 6500000.0]`

### `mock_epsg()`
Returns EPSG code 4326 (WGS84 decimal degrees) for coordinate system testing.

## Test Markers

Use pytest markers to categorize tests:

```python
@pytest.mark.screen
def test_screen_functionality(screen):
    pass

@pytest.mark.navigation
def test_navigation_operations():
    pass

@pytest.mark.coord_display
def test_coordinate_display():
    pass

@pytest.mark.route_selection
def test_route_point_selection():
    pass
```

## Running Tests

Run all Phase 1 tests:
```bash
pytest .planning/phases/01-map-interaction-user-selection/tests/
```

Run tests by marker:
```bash
pytest -m screen .planning/phases/01-map-interaction-user-selection/tests/
pytest -m navigation .planning/phases/01-map-interaction-user-selection/tests/
```

List available fixtures:
```bash
pytest .planning/phases/01-map-interaction-user-selection/tests/ --fixtures
```

## Test Data

### test_world.pgw
World file representing UTM 32V (northern Norway) coordinate system:
- Pixel size: 12m x 12m
- Top-left coordinate: 450000m E, 6500000m N
- Y-axis: negative (image rows increase northward with pixel height = -12.0)

## Notes

- Fixtures handle tkinter window cleanup automatically
- Screen instances are created fresh for each test using fixtures
- Coordinate transformations use mock data to test logic without external dependencies
- Test data is minimal and self-contained for reliability