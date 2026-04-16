---
phase: 05-route-visualization-export
reviewed: 2026-04-16T00:00:00Z
depth: standard
files_reviewed: 2
files_reviewed_list:
  - screen_2026.py
  - tests/test_05_gpx_export.py
findings:
  critical: 0
  warning: 4
  info: 4
  total: 8
status: issues_found
---

# Phase 05: Code Review Report

**Reviewed:** 2026-04-16
**Depth:** standard
**Files Reviewed:** 2
**Status:** issues_found

## Summary

Reviewed two files for Phase 5 route visualization and export: `screen_2026.py` (main Screen class with GPX export) and `test_05_gpx_export.py` (export compatibility tests). The code implements GPX 1.1 export with WGS84 coordinate transformation, file dialog integration, and fallback behavior for image loading.

Overall implementation is solid with proper error handling in critical paths. No security vulnerabilities or critical bugs found. Most issues are code quality concerns (debug artifacts, bare except blocks) and one test logic error.

## Warnings

### WR-01: Unchecked tuple unpacking may cause export failure

**File:** `screen_2026.py:486`
**Issue:** GPX export unpacks coordinates without validating tuple structure. If any coordinate in `_route_network_coords` is not a 2-element tuple, the entire export fails with an unclear error.

```python
for (x, y) in self._route_network_coords:
    lon, lat = transformer.transform(x, y)
```

**Fix:** Add try-except around individual coordinate transformations to handle malformed data gracefully:

```python
track_points = []
for coord in self._route_network_coords:
    try:
        x, y = coord  # Validate unpacking
        lon, lat = transformer.transform(x, y)
        track_points.append(f'      <trkpt lat="{lat:.6f}" lon="{lon:.6f}"></trkpt>')
    except (ValueError, TypeError, Exception) as e:
        print(f'Warning: Skipping invalid coordinate {coord}: {e}')
        continue
```

### WR-02: Bare except clause masks transformation errors

**File:** `screen_2026.py:300`
**Issue:** Catching all exceptions without logging makes debugging coordinate transformation failures difficult. Corrupted data or edge cases will fail silently.

```python
try:
    lon, lat = transformer.transform(*world_point)
    return [lon, lat]
except Exception:
    return world_point  # Fallback if transformation fails
```

**Fix:** Log the exception for debugging:

```python
try:
    lon, lat = transformer.transform(*world_point)
    return [lon, lat]
except Exception as e:
    print(f'Warning: Coordinate transformation failed: {e}')
    return world_point  # Fallback if transformation fails
```

### WR-03: Fallback behavior bypasses file dialog in export

**File:** `screen_2026.py:462-466`
**Issue:** When no route exists, `export_gpx()` falls back to `_read_image()` without user confirmation. The F5 key shows file dialog for export but cancels it behind the scenes when no route is present, which may confuse users expecting to always get a file dialog.

```python
if not self._route_network_coords:
    # No route available, fall back to image load (existing F5 behavior)
    print('No route computed. Loading image instead.')
    self._read_image(event)
    return
```

**Fix:** Add user notification or check if image loading was the intended action:

```python
if not self._route_network_coords:
    # No route available, fall back to image load (existing F5 behavior)
    message = 'No route computed. Loading image instead.'
    print(message)
    utilities.warning(message)  # Show GUI notification to user
    self._read_image(event)
    return
```

### WR-04: Test assertion uses incorrect mock attribute

**File:** `tests/test_05_gpx_export.py:268`
**Issue:** The test checks `screen.export_gpx.called == False`, but `export_gpx` is a regular method, not a mock object with a `.called` attribute. This assertion will always evaluate to `False` (not defined) and not properly verify behavior.

```python
assert len(gpx_files) == 0 or screen.export_gpx.called == False
```

**Fix:** Remove the incorrect mock check or properly mock the method:

```python
# Option 1: Simply check no files were created
assert len(gpx_files) == 0

# Option 2: If tracking calls is needed, properly mock the method
with patch.object(screen, 'export_gpx') as mock_export:
    mock_export.side_effect = lambda event: None  # Call original
    screen.export_gpx()
    assert mock_export.called
```

## Info

### IN-01: Debug artifact remaining in production code

**File:** `screen_2026.py:333`
**Issue:** Debug print statement marked with `#REMOVE` comment was not cleaned up. This clutters console output and should be removed before release.

```python
print(f'WORLD FILE SET IN READ_IMAGE (F5): {self._world_file}') #REMOVE
```

**Fix:** Remove the debug print statement entirely.

### IN-02: Variable shadowing in nested loop

**File:** `screen_2026.py:669`
**Issue:** In `draw_polygon()`, the inner loop shadows the outer loop variable `part`, making the code confusing and potentially buggy if the outer variable is used later.

```python
if vertices is True:
    for part in polygon:
        for part in part[1:]:  # Shadows outer 'part' variable
            self.draw_point(point=part, colour=colour, tag=tag)
```

**Fix:** Use different variable names:

```python
if vertices is True:
    for polygon_part in polygon:
        for vertex in polygon_part[1:]:
            self.draw_point(point=vertex, colour=colour, tag=tag)
```

### IN-03: Comment/parameter order mismatch

**File:** `screen_2026.py:275-279`
**Issue:** The function comment lists parameters in wrong order (documentation shows `screen_point` first, `self` second), contradicting Python convention where `self` is always first.

```python
:param self: Instance of the class
:param screen_point: [x, y] screen coordinates
```

**Fix:** Reorder to follow Python documentation conventions:

```python
:param screen_point: [x, y] screen coordinates
:return: [lon, lat] in decimal degrees, or None if world file not set
```

### IN-04: Inconsistent function docstring parameter naming

**File:** `screen_2026.py:303-310`
**Issue:** The function signature uses `point` but docstring uses `screen_point`, creating confusion about the parameter name.

```python
def _update_coordinate_display(self, point, label):
    """
    Display decimal degree coordinates for a selected point.

    :param screen_point: [x, y] screen coordinates  <-- Should be 'point'
    :param label: Label for the point ('Start' or 'End')
    """
```

**Fix:** Update docstring to match function signature:

```python
:param point: [x, y] screen coordinates
:param label: Label for the point ('Start' or 'End')
```

---

_Reviewed: 2026-04-16_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_