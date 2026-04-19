---
phase: 04-water-body-penalty-routing
reviewed: 2026-04-14T00:00:00Z
depth: standard
files_reviewed: 1
files_reviewed_list:
  - routing_2026.py
findings:
  critical: 0
  warning: 3
  info: 3
  total: 6
status: issues_found
---

# Phase 04: Code Review Report

**Reviewed:** 2026-04-14T00:00:00Z
**Depth:** standard
**Files Reviewed:** 1
**Status:** issues_found

## Summary

Reviewed `routing_2026.py`, a new geospatial routing module that provides terrain-aware pathfinding with water body penalties. The module implements a `RoutingNetwork` class wrapper around networkx.Graph, functions for loading OpenStreetMap trails, terrain weight calculations using slope-based penalties, water feature detection and penalties, and mesh generation from raster elevation data.

Overall, the code is well-documented with comprehensive docstrings and follows project conventions. The implementation correctly handles offline capability requirements with graceful fallback behavior when network queries fail. However, there are several areas that warrant attention before integration.

## Critical Issues

None found.

## Warnings

### WR-01: Zero-weight edges in Dijkstra's algorithm

**File:** `routing_2026.py:241-242`
**Issue:** The `calculate_terrain_weight()` function returns weight=0.0 when edge_length == 0. While this is likely intentional for handling coincident points, zero-weight edges in routing graphs can cause unexpected behavior with Dijkstra's algorithm (preferentially choosing zero-length paths, potential issues with path uniqueness).

**Fix:**
Consider returning a small minimum weight or documenting why zero is acceptable:
```python
# Guard clause: edge_length == 0 (T-3-05)
if edge_length == 0:
    # Return small minimum weight to avoid zero-weight edge routing issues
    # while still preferring coincident points
    return (0.001, 0.0, 1.0)
```

### WR-02: Mock assert statements in user-facing function

**File:** `routing_2026.py:297-298`
**Issue:** The `load_water_features()` function uses assert statements to validate bounding box coordinates. Assertions are meant for programmer errors (invariants that should never be violated), not user input validation. Assertions can be disabled with Python's `-O` flag, which would skip this validation in production.

**Fix:**
Replace assertions with explicit exception handling:
```python
# Validate bbox format
if not west < east:
    raise ValueError(f"bbox west ({west}) must be less than east ({east})")
if not south < north:
    raise ValueError(f"bbox south ({south}) must be less than north ({north})")
```

### WR-03: Integer truncation in mesh spacing calculation

**File:** `routing_2026.py:416, 425, 429`
**Issue:** After calculating `pixel_spacing = mesh_spacing / abs(pixel_width)`, the code uses `int(pixel_spacing)` in range() calls. This truncates the pixel spacing to an integer, which means actual mesh spacing may differ from the requested `mesh_spacing` parameter. For example, if `mesh_spacing=100m` and `pixel_width=15m`, then `pixel_spacing=6.666` but `int(pixel_spacing)=6`, resulting in actual spacing of 90m instead of 100m.

**Fix:**
Consider either:
1. Keep using integer spacing but document the truncation behavior
2. Round to nearest integer: `int(round(pixel_spacing))`
3. Allow float spacing and adjust loop logic accordingly (more complex)

```python
# Option 2: Round to nearest integer
pixel_spacing_int = int(round(mesh_spacing / abs(pixel_width)))
if pixel_spacing_int < 1:
    pixel_spacing_int = 1  # Ensure at least 1 pixel spacing
```

## Info

### IN-01: Unhandled variable shadowing

**File:** `routing_2026.py:478-487`
**Issue:** The variable `terrain_weight` returned from `calculate_terrain_weight()` is immediately overwritten on line 485 (`terrain_weight = mesh_spacing`) in the None elevation fallback case. While the return value isn't used subsequently, this shadowing breaks the semantic expectation that `terrain_weight` represents the calculated terrain weight.

**Fix:**
Use a different variable name for the fallback value:
```python
if elev1 is not None and elev2 is not None:
    terrain_weight, slope, terrain_penalty = calculate_terrain_weight(
        elev1, elev2, mesh_spacing
    )
else:
    # Fallback to uniform weight if elevation unavailable
    terrain_weight = mesh_spacing
    slope = 0.0
    terrain_penalty = 1.0
```

### IN-02: Broad exception handling in network operations

**File:** `routing_2026.py:319-323, 462-465`
**Issue:** Both `load_water_features()` and `terrain_mesh_from_raster()` use bare `except Exception` clauses without specifying expected exception types. While this is acceptable for graceful fallback to offline mode, specific exception types would be better for debugging and error logging.

**Fix:**
Catch specific exceptions and log appropriately:
```python
# Example for load_water_features
except (ox.errors.OverpassAPIError, ConnectionError, TimeoutError) as e:
    # Graceful fallback on network failure
    print(f"Warning: Failed to query water features: {e}")
    print("Continuing without water penalty mode")
    return (None, None)
except Exception as e:
    # Log unexpected errors
    print(f"Error: Unexpected exception querying water features: {e}")
    return (None, None)
```

### IN-03: Missing input validation in user-facing function

**File:** `routing_2026.py:551-552`
**Issue:** The `polylines_to_graph()` function doesn't validate that `trails_vector` is not None or that it contains POLYLINE geometry. If invalid input is passed, it will raise an AttributeError when accessing `trails_vector.coordinates`.

**Fix:**
Add input validation:
```python
def polylines_to_graph(trails_vector, snap_distance=50):
    """
    Convert trail polylines to routing graph with node snapping.
    
    Args:
        trails_vector: Vector instance with POLYLINE geometry
        snap_distance: Distance in map units to snap endpoint nodes
    
    Returns:
        RoutingNetwork instance with graph topology
    """
    if trails_vector is None:
        raise ValueError("trails_vector cannot be None")
    if not hasattr(trails_vector, 'coordinates'):
        raise ValueError("trails_vector must have coordinates attribute")
    
    # Rest of function
```

---

_Reviewed: 2026-04-14T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_