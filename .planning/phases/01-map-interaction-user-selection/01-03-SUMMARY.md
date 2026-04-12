---
phase: 01-map-interaction-user-selection
plan: 03
status: completed
nice: "03"
---

# Plan 03: Map Navigation (Pan and Zoom)

## Summary

Successfully implemented map navigation (pan via mouse drag, zoom via mouse wheel and keyboard shortcuts) with real-time WGS84 decimal degree coordinate display for selected route points. Cross-platform mouse wheel support ensures compatibility across Windows, macOS, and Linux.

## What Was Built

### 1. Pan Methods (Task 1)
- Created `_start_pan(self, event)` method:
  - Calls `self._canvas.scan_mark(event.x, event.y)` to mark initial position
- Created `_do_pan(self, event)` method:
  - Calls `self._canvas.scan_dragto(event.x, event.y, gain=1)` for continuous panning
  - Redisplays coordinate labels after pan operation

### 2. Zoom Methods (Task 2)
- Created `_zoom_in(self, event)` method:
  - Converts screen coordinates using `canvasx()` and `canvasy()`
  - Applies 10% scale factor (1.1) around cursor position
  - Redisplays coordinate labels after zoom
- Created `_zoom_out(self, event)` method:
  - Same coordinate conversion as zoom_in
  - Applies 10% out scale factor (0.9) around cursor position
  - Redisplays coordinate labels after zoom

### 3. Cross-Platform Mouse Wheel Handler (Task 3)
- Created `_handle_mouse_wheel(self, event)` method:
  - Windows/macOS: Uses `event.delta` (positive = zoom in, negative = zoom out)
  - Linux: Uses `event.num` (4 = scroll up/zoom in, 5 = scroll down/zoom out)
  - Routes to appropriate zoom method based on direction

### 4. Coordinate Transformation (Task 4)
- Created `screen_to_decimal_degrees(self, screen_point)` method:
  - Validates `self._world_file` exists
  - Calls `utilities.screen_to_world()` for affine transformation
  - Skips EPSG transformation if already 4326 or None
  - Uses `pyproj.Transformer` for EPSG → 4326 conversion
  - Returns `[lon, lat]` in decimal degrees format
- Added `import pyproj` at top of file

### 5. Coordinate Display Update (Task 5)
- Created `_update_coordinate_display(self, point, label)` method:
  - Calls `screen_to_decimal_degrees()` for coordinate conversion
  - Returns early if world file not set
  - Deletes previous 'coord_display' tag
  - Formats message as "Label: Lat X.XXXXXX, Lon X.XXXXXX"
  - Draws text with 'coord_display' tag
- Modified `_select_route_point()` to call `_update_coordinate_display()` after each point selection
- Modified `_do_pan()` to redisplay coordinates for start/end points after pan
- Modified `_zoom_in()` and `_zoom_out()` to redisplay coordinates after zoom

### 6. Pan and Zoom Bindings (Task 6)
- Added pan bindings:
  - `<Button-2>` → `_start_pan` (middle mouse button)
  - `<B2-Motion>` → `_do_pan` (middle mouse drag)
  - `<Button-3>` → `_start_pan` (right mouse button alternative)
  - `<B3-Motion>` → `_do_pan` (right mouse drag alternative)
- Added mouse wheel bindings:
  - `<MouseWheel>` → `_handle_mouse_wheel` (Windows/macOS)
  - `<Button-4>` → `_handle_mouse_wheel` (Linux scroll up)
  - `<Button-5>` → `_handle_mouse_wheel` (Linux scroll down)
- Added zoom keyboard shortcuts:
  - `<plus>` → `_zoom_in` (keyboard +)
  - `<equal>` → `_zoom_in` (unshifted + on most keyboards)
  - `<minus>` → `_zoom_out` (keyboard -)

### 7. Integration Tests (Task 7)
- Created `tests/test_navigation_and_display.py` with 15 test functions:
  - `test_screen_to_decimal_degrees` - verifies transformation
  - `test_screen_to_decimal_degrees_no_world_file` - validates None return
  - `test_coordinate_display` - verifies canvas text display
  - `test_coordinate_display_no_world_file` - validates early return
  - `test_pan_start` - tests canvas scan_mark
  - `test_pan_drag` - tests canvas scan_dragto
  - `test_zoom_in` - tests canvas scale operation
  - `test_zoom_out` - tests canvas scale with 0.9 factor
  - `test_mouse_wheel_handler_windows_mac` - tests delta property
  - `test_mouse_wheel_handler_linux` - tests event.num = 4
  - `test_mouse_wheel_handler_linux_scroll_down` - tests event.num = 5
  - `test_coordinate_display_persistence_after_pan` - validates redisplay
  - `test_coordinate_display_persistence_after_zoom` - validates redisplay
  - `test_coordinate_format` - validates decimal degree format
  - `test_both_points_display_after_navigation` - validates both labels
- All 15 tests pass with pytest

## Files Modified

- `screen_2026.py`:
  - Line 3: Added `import pyproj`
  - Lines 76-96: Added pan and zoom bindings in `__init__`
  - Lines 171-296: Added navigation and coordinate display methods
  - Lines 130, 142: Added `_update_coordinate_display()` calls in `_select_route_point()`

- `tests/test_navigation_and_display.py` (new):
  - 213 lines of integration tests for navigation and coordinate display

## Test Results

```
test_screen_to_decimal_degrees PASS
test_screen_to_decimal_degrees_no_world_file PASS
test_coordinate_display PASS
test_coordinate_display_no_world_file PASS
test_pan_start PASS
test_pan_drag PASS
test_zoom_in PASS
test_zoom_out PASS
test_mouse_wheel_handler_windows_mac PASS
test_mouse_wheel_handler_linux PASS
test_mouse_wheel_handler_linux_scroll_down PASS
test_coordinate_display_persistence_after_pan PASS
test_coordinate_display_persistence_after_zoom PASS
test_coordinate_format PASS
test_both_points_display_after_navigation PASS

============================== 15 passed in 0.50s ==============================
```

## Threat Mitigations Addressed

- **T-01-07 (Tampering)**: Mouse coordinates used directly in canvas operations. This is acceptable for early development; bound checks could be added for production.

- **T-01-08 (DoS)**: Zoom factor is fixed at 1.1/0.9 per operation. Unbounded zoom could occur with repeated operations; future enhancement could add zoom limits.

- **T-01-09 (Information Disclosure)**: Affine transformation parameters are accessed via existing `utilities.screen_to_world()` which is already public.

- **T-01-10 (Tampering)**: Coordinate display formats any coordinates returned from transformation. Range validation (lat: -90..90, lon: -180..180) could be added for production.

## Key Links Verified

- ✓ `_handle_mouse_wheel()` → `_zoom_in()`/`_zoom_out()` via delta/num detection
- ✓ `screen_to_decimal_degrees()` → `draw_text()` via `_update_coordinate_display()`
- ✓ Platform-specific mouse wheel handlers tested for Windows/macOS/Linux
- ✓ Coordinate display persistence verified after pan and zoom operations

## Dependencies Satisfied

- **MAP-03**: User can pan map with middle/right mouse drag
- **MAP-04**: User can zoom with mouse wheel and keyboard shortcuts (+/-)
- **MAP-05**: Selected points display coordinates in decimal degrees format (6 decimal places)

## Commits

1. `feat(screen): add map navigation and coordinate display` - implements tasks 1-6
2. `test(01-03): add integration tests for navigation and coordinate display` - implements task 7
3. `docs(01-03): Create plan execution summary` (this file)

## Notable Deviations

None. Implementation followed plan specifications exactly. All acceptance criteria met.

## Phase Completion Status

All three plans in Phase 01 completed successfully:
- ✓ Plan 01-01: Test Infrastructure (pytest framework, fixtures, test data)
- ✓ Plan 01-02: Route Selection State Management (start/end point selection, visual markers)
- ✓ Plan 03-03: Map Navigation and Coordinate Display (pan/zoom, decimal degree display)

Total tests: 21 (6 from plan 01-02, 15 from plan 01-03) — all passing.