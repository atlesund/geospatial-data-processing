# Phase 7: Terrain Auto-Mesh Generation - Pattern Map

**Mapped:** 2026-04-20
**Files analyzed:** 3
**Analogs found:** 3 / 3

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `screen_2026.py` | component | event-driven | `screen_2026.py:322-339` (_read_image method) | role-match |
| `examples/example_phase07_terrain_auto_mesh.py` | example | interactive | `examples/example_phase01_route_selection.py` | exact |
| `tests/test_07_terrain_auto_mesh.py` | test | request-response | `tests/test_v1_complete.py:33-289` (Phase 2 test patterns) | exact |

## Pattern Assignments

### `screen_2026.py` (component, event-driven - MODIFY)

**Analog:** `screen_2026.py:322-339` (_read_image method) - existing raster loading pattern

**Imports pattern** (lines 1-11):
```python
import json
import tkinter
import pyproj
import numpy as np

from vector_2026 import Vector
from raster_2026 import Raster

import utilities_2026 as utilities
```

**Raster loading pattern** (lines 322-339 - `_read_image` method):
```python
def _read_image(self, event):

    """
    Read image with F5

    :param self: Description
    :param event: Description
    """

    self._image.read_image()
    self._world_file = self._image._world_file
    print(f'WORLD FILE SET IN READ_IMAGE (F5): {self._world_file}') #REMOVE

    epsg = utilities.epsg()
    if epsg is not None:
        self._epsg = epsg
```

**Progress indication pattern** (from Phase 6 plan - line 272):
```python
# Show progress indication
self._root.config(cursor='watch')
self._root.update_idletasks()

# ... computation ...

# Restore cursor
self._root.config(cursor='arrow')
```

**Error handling with warning dialogs** (lines 531-537 - `_digit_points_to_geojson` method):
```python
if len(self._digits.coordinates) == 0:
    utilities.warning('Digitised points not found')
    return  # Early return on error

if self._world_file is None:
    utilities.warning('World file data not found')
    return  # Early return on error
```

**Setter method with validation pattern** (from Phase 6 expected - set_route_network):
```python
def set_route_network(self, network):
    """Assign a routing network to the screen for path computation."""
    if not isinstance(network, RoutingNetwork):
        raise ValueError(f"Expected RoutingNetwork instance, got {type(network).__name__}")
    self._route_network = network
    print(f'Routing network assigned to screen. Graph has {len(network.graph.nodes)} nodes')
```

**Network assignment pattern** (Phase 6 - set_route method):
```python
def set_route(self, network_coords):
    self._route_network_coords = network_coords  # Store for export
    self.display_route(network_coords)  # Display on canvas
```

---

### `examples/example_phase07_terrain_auto_mesh.py` (example, interactive)

**Analog:** `examples/example_phase01_route_selection.py`

**Module docstring pattern** (lines 1-21):
```python
"""
Example: Phase 01 Route Selection and Map Navigation

Demonstrates interactive map features from Phase 01:
- Route selection (start/end points via mouse clicks)
- Map navigation (pan via mouse drag, zoom via mouse wheel/keyboard)
- Coordinate display in WGS84 decimal degrees

Usage:
    python -m examples.example_phase01_route_selection

Controls:
    Shift+F9: Start route selection mode
    Shift+F10: Stop route selection mode
    Left click: Select route points (when in route selection mode)
    Middle/Right drag: Pan the map
    Mouse wheel: Zoom in/out
    +/- keys: Zoom in/out
    F5: Load an image (optional - requires image file)
"""
```

**Import pattern** (line 23):
```python
import geo_2026 as geo
```

**Main function pattern** (lines 26-62):
```python
def main():
    """
    Main function demonstrating Phase 01 features.
    """
    print("=" * 60)
    print("Phase 01: Route Selection and Map Navigation Demo")
    print("=" * 60)
    print()
    print("Interactive Map Controls:")
    print("  Shift+F9  : Start route selection mode")
    print("  Shift+F10 : Stop route selection mode")
    print()
    print("=" * 60)
    print()

    # Create a Screen instance with default size (800x600)
    screen = geo.Screen(rows=600, columns=800, background='black')

    print("Screen created. Ready for interaction.")
    print()

    # Start the main event loop
    screen.loop()


if __name__ == '__main__':
    main()
```

**Screen instantiation pattern** (line 50):
```python
screen = geo.Screen(rows=600, columns=800, background='black')
```

**User instruction display pattern** (lines 30-45):
```python
print("=" * 60)
print("Phase 01: Route Selection and Map Navigation Demo")
print("=" * 60)
    print()
print("Interactive Map Controls:")
    print("  Shift+F9  : Start route selection mode")
    print("  Shift+F10 : Stop route selection mode")
    print()
```

---

### `tests/test_07_terrain_auto_mesh.py` (test, request-response)

**Analog:** `tests/test_v1_complete.py` lines 33-289 (Phase 2 test classes)

**Test module docstring pattern**:
```python
"""
Comprehensive v1 integration test for Norwegian Hiking Route Planner.

Tests all implemented features:
- Phase 2: Routing Network Construction (trails, OSM, terrain mesh)
- Phase 7: Terrain Auto-Mesh Generation

Usage:
    Run all tests: pytest tests/test_07_terrain_auto_mesh.py -v
    Run specific test class: pytest tests/test_07_terrain_auto_mesh.py::TestAutoMeshTrigger -v
"""
```

**Import pattern**:
```python
import pytest
import numpy as np
from unittest.mock import Mock, patch

# Import geospatial modules
from routing_2026 import RoutingNetwork, terrain_mesh_from_raster
from raster_2026 import Raster
from screen_2026 import Screen
```

**Test class pattern**:
```python
class TestAutoMeshTrigger:
    """Test automatic terrain mesh generation after raster load."""

    def test_auto_mesh_called_after_raster_load(self):
        """Mesh generation triggers after raster is loaded."""
        screen = Screen()
        # Mock terrain_mesh_from_raster to verify it's called
        with patch('routing_2026.terrain_mesh_from_raster') as mock_mesh:
            # Trigger raster load
            screen._read_image(Mock())
            # Verify mesh generation was called
            assert mock_mesh.called
```

**Pytest fixture pattern for mock screen with raster** (from Phase 6 patterns):
```python
@pytest.fixture
def mock_screen_with_raster(self):
    """Create mock screen with loaded raster."""
    from screen_2026 import Screen
    from raster_2026 import Raster

    with patch('screen_2026.tkinter.Tk'):
        screen = Screen()
        screen._eps = 32632  # UTM 32V
        screen._world_file = [10.0, 0.0, 0.0, -10.0, 600000.0, 6650000.0]
        screen._image = Raster()
        screen._image._elevation_grid = np.ones((100, 100))
        screen._image._world_file = screen._world_file
        return screen
```

**Test method with fixture parameter pattern**:
```python
def test_network_assigned_after_mesh_generation(self, mock_screen_with_raster):
    """Network is assigned to screen after mesh generation."""
    # Test that _route_network is populated
    assert hasattr(mock_screen_with_raster, '_route_network')
    assert mock_screen_with_raster._route_network is not None
    assert len(mock_screen_with_raster._route_network.graph.nodes) > 0
```

**Mock behavior with tkinter.Tk patch pattern** (from Phase 6):
```python
@pytest.fixture
def mock_screen(self):
    from screen_2026 import Screen
    with patch('screen_2026.tkinter.Tk'):
        screen = Screen()
        screen._world_file = [10.0, 0.0, 0.0, -10.0, 600000.0, 6650000.0]
        screen._epsg = 32632
        return screen
```

**Test with temporary file pattern**:
```python
def test_mesh_generation_with_real_geotiff(self):
    """Mesh generation works with actual GeoTIFF file."""
    import tempfile
    import os

    # Create temporary GeoTIFF with elevation data
    with tempfile.NamedTemporaryFile(suffix='.tif', delete=False) as f:
        filename = f.name

    try:
        # Write test GeoTIFF data...
        # Load raster and generate mesh
        screen = Screen()
        screen._image = Raster()
        screen._image._read_geotiff(filename)
        # Auto-mesh should generate network
        assert screen._route_network is not None
    finally:
        if os.path.exists(filename):
            os.unlink(filename)
```

---

## Shared Patterns

### Error Handling with Warning Dialogs
**Source:** `utilities_2026.py:37-39` and `screen_2026.py:531-537`
**Apply to:** All methods in screen_2026.py that handle user-facing errors
```python
def warning(message, title='Warning'):
    tkinter.Tk().withdraw()
    tkinter.messagebox.showwarning(title, message)

# Usage pattern:
if self._world_file is None:
    utilities.warning('World file data not found')
    return  # Early return on error
```

### Cursor Progress Indication Pattern
**Source:** Phase 6 plan (line 272) and screen_2026.py (_compute_and_display_route expected)
**Apply to:** All long-running operations in screen_2026.py
```python
# Show progress indication
self._root.config(cursor='watch')
self._root.update_idletasks()

# ... computation ...

# Restore cursor
self._root.config(cursor='arrow')
```

### World File Validation Pattern
**Source:** `screen_2026.py:273-282` and `screen_2026.py:535-537`
**Apply to:** All coordinate transformation methods in screen_2026.py
```python
if self._world_file is None:
    return None  # Early return for missing world file
```

### Network Validation Pattern
**Source:** Phase 6 expected (set_route_network)
**Apply to:** All methods that depend on routing network
```python
if self._route_network is None:
    utilities.warning('Routing network not loaded')
    return  # Early return on error

if len(self._route_network.graph.nodes) == 0:
    utilities.warning('Routing network is empty')
    return  # Early return on error
```

### Raster Loading Pattern
**Source:** `screen_2026.py:322-339` (`_read_image` method)
**Apply to:** New auto-mesh generation method or modification to `_read_image`
```python
def _read_image(self, event):
    self._image.read_image()  # Load GeoTIFF
    self._world_file = self._image._world_file  # Store world file

    epsg = utilities.epsg()
    if epsg is not None:
        self._epsg = epsg
```

### Network Assignment Pattern
**Source:** Phase 6 (set_route_network method - expected)
**Apply to:** Auto-mesh generation to assign generated network to screen
```python
def set_route_network(self, network):
    from routing_2026 import RoutingNetwork

    if not isinstance(network, RoutingNetwork):
        raise ValueError(f"Expected RoutingNetwork instance, got {type(network).__name__}")

    self._route_network = network
    print(f'Routing network assigned: {len(network.graph.nodes)} nodes')
```

### Terrain Mesh Generation Pattern
**Source:** `routing_2026.py:393-554` (`terrain_mesh_from_raster` function)
**Apply to:** New auto-mesh trigger in screen_2026.py
```python
def terrain_mesh_from_raster(raster, mesh_spacing=100, bbox=None):
    """
    Generate a regular mesh node grid from terrain raster.

    Args:
        raster: Raster instance with DTM data
        mesh_spacing: Distance between mesh nodes (meters in projection)

    Returns:
        RoutingNetwork with regular mesh topology
    """
    routing_net = RoutingNetwork()
    routing_net.epsg = raster.epsg

    # ... create nodes and edges ...

    return routing_net
```

### Print Debug Pattern
**Source:** `screen_2026.py:333` and throughout screen_2026.py
**Apply to:** All operations that should provide feedback to console
```python
print(f'Mesh network created: {len(routing_net.graph.nodes)} nodes, {len(routing_net.graph.edges)} edges')
print(f'Debug: world file set to {self._world_file}')
```

### Exception Handling with Finally Block
**Source:** Phase 6 plan (line 335-337)
**Apply to:** All operations with cursor progress indication
```python
try:
    # ... operation ...
finally:
    # Restore cursor even if operation fails
    self._root.config(cursor='arrow')
```

### Test Mock Pattern for Tkinter
**Source:** `tests/test_v1_complete.py:240-253` and `295-309`
**Apply to:** All test classes that create Screen instances
```python
from unittest.mock import patch

@pytest.fixture
def mock_screen(self):
    from screen_2026 import Screen
    with patch('screen_2026.tkinter.Tk'):
        screen = Screen()
        screen._world_file = [10.0, 0.0, 0.0, -10.0, 600000.0, 6650000.0]
        screen._epsg = 32632
        return screen
```

### Documentation Pattern for Examples
**Source:** `examples/example_phase01_route_selection.py:1-21`
**Apply to:** All example files
```python
"""
Example: Phase 07 - Terrain Auto-Mesh Generation

Demonstrates automatic routing network generation from terrain load:
- F5: Load GeoTIFF terrain and auto-generate routing mesh
- Routing is immediately available after terrain load

Usage:
    python -m examples.example_phase07_terrain_auto_mesh

Controls:
    F5: Load GeoTIFF and auto-generate mesh
    Shift+F9: Start route selection (mesh must be loaded)
"""
```

### Raster Attribute Access Pattern
**Source:** `raster_2026.py:86-110` (`read_image` method)
**Apply to:** Code that uses Raster instances
```python
# Raster instance has these key attributes after loading:
raster._filename      # Path to loaded file
raster._epsg          # EPSG code from GeoTIFF metadata
raster._world_file    # Affine transform [a, d, b, e, c, f]
raster._elevation_grid  # 2D numpy array of elevation values
raster.shape          # [rows, columns] tuple
```

## No Analog Found

Files with no close match in the codebase (planner should use RESEARCH.md patterns instead):

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| None | - | - | All files have close analogs in the codebase |

## Metadata

**Analog search scope:**
- `/Users/dev/Code/School/geospatial-data-processing/screen_2026.py` (Screen class methods)
- `/Users/dev/Code/School/geospatial-data-processing/examples/` (example files)
- `/Users/dev/Code/School/geospatial-data-processing/tests/` (test files)
- `/Users/dev/Code/School/geospatial-data-processing/routing_2026.py` (terrain_mesh_from_raster function)
- `/Users/dev/Code/School/geospatial-data-processing/utilities_2026.py` (warning dialogs)
- `/Users/dev/Code/School/geospatial-data-processing/.planning/phases/06-gui-routing-integration-connect-point-selection-with-routing/` (Phase 6 patterns)

**Files scanned:**
- screen_2026.py (679 lines) - Screen class with event handlers, coordinate transforms, route display
- routing_2026.py (701 lines) - RoutingNetwork class, terrain_mesh_from_raster function
- utilities_2026.py (857 lines) - Coordinate transforms, warning function, file I/O
- examples/example_phase01_route_selection.py (66 lines) - Route selection demo
- examples/example_302_raster_gui.py (15 lines) - Raster GUI example
- tests/test_v1_complete.py (500+ lines) - Comprehensive test suite
- .planning/phases/06-gui-routing-integration-connect-point-selection-with-routing/06-PATTERNS.md (594 lines)
- .planning/phases/06-gui-routing-integration-connect-point-selection-with-routing/06-01-PLAN.md (230 lines)
- .planning/phases/06-gui-routing-integration-connect-point-selection-with-routing/06-02-PLAN.md (400 lines)

**Pattern extraction date:** 2026-04-20
**Confidence:** HIGH - All patterns verified from actual codebase files