# Phase 5: Route Visualization & Export - Research

**Research Date:** 2026-04-16
**Status:** Complete - Ready for planning

## Overview

Phase 5 adds route visualization to the tkinter Screen class and GPX file export functionality. This phase integrates route display with the existing desktop interface and provides GPS-compatible output for outdoor navigation devices.

## Technical Context

### Existing Infrastructure

**Screen Class (`screen_2026.py`)**
- Canvas-based tkinter visualization with coordinate transformations
- `draw_polyline()` method (line 459-470): Draws polylines on canvas with configurable width, color, and tag
- `draw_point()` method (line 434-456): Draws point markers with size, color, and tag
- `delete()` method (line 425-432): Removes canvas elements by tag for route clearing
- `keyboard_bind()` method (line 402-410): Binds keyboard shortcuts to functions
- F5 key currently bound to `_read_image()` for raster loading - needs rebinding or conflict resolution

**RoutingNetwork Class (`routing_2026.py`)**
- `shortest_path()` method (line 77-93): Returns list of node IDs forming the path
- `node_coords` attribute: Dict mapping node_id -> (x, y) coordinates in network EPSG
- `epsg` property: Tracks coordinate reference system (e.g., 25832 for UTM 32V)

**Coordinate Transformations**
- `screen_2026.py:265-293`: `screen_to_decimal_degrees()` transforms from screen -> world -> WGS84 using pyproj
- pyproj available in project for EPSG transformations
- Route coordinates may be in routing network EPSG (e.g., 25832), must transform to EPSG:4326 for GPX

### Key Locked Decisions from CONTEXT.md

**D-01:** Use tkinter Screen class - routes drawn via `Screen.draw_polyline()` on canvas
**D-02:** Bright distinctive color (red/yellow/orange) - high contrast against map
**D-03:** Medium line width (3-4 pixels) - visible without obscuring details
**D-04:** Simple styling - no additional markers or patterns
**D-05:** Auto-show route after routing completes
**D-06:** Clear old routes before computing/displaying new route
**D-07:** Track-only GPX format with `<trk><trkseg><trkpt>` structure
**D-08:** F5 keyboard shortcut for export
**D-09:** Standard file save dialog (tkinter.filedialog.asksaveasfilename)

## Implementation Requirements

### 1. Route Visualization (VIZ-01)

**What needs to happen:**
1. Route computation returns node IDs from `RoutingNetwork.shortest_path()`
2. Look up coordinates for each node ID via `RoutingNetwork.node_coords`
3. Transform coordinates from network EPSG to screen coordinates using world file
4. Call `Screen.draw_polyline()` with distinctive color and 3-4px width
5. Tag the route for clearing before new routes (D-06)

**Coordinate Transformation Flow:**
- Route nodes: network EPSG coordinates (e.g., UTM 32V: 25832)
- To screen: Use `Screen.world_to_screen()` inverse of `screen_to_decimal_degrees()` pattern
- Screen coordinates: Canvas pixel coordinates for `draw_polyline()`

**Integration Point:**
- Need to know where route computation happens - likely triggered after user selects start/end points
- May need to add route state to Screen class (similar to `_start_point`, `_end_point`)
- Route clearing: `Screen.delete('route_tag')` before drawing new route

### 2. GPX Export (EXP-01)

**GPX 1.1 Format Requirements:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="Norwegian Hiking Route Planner" xmlns="http://www.topografix.com/GPX/1/1">
  <trk>
    <name>Route</name>
    <trkseg>
      <trkpt lat="60.000000" lon="5.000000"></trkpt>
      <trkpt lat="60.000100" lon="5.000100"></trkpt>
      ...
    </trkseg>
  </trk>
</gpx>
```

**Coordinate Transformation for GPX:**
- Route coordinates: network EPSG (e.g., 25832)
- Transform to WGS84 (EPSG:4326) using pyproj: `Transformer.from_crs(from_epsg, 4326, always_xy=True)`
- WGS84 coordinates: (lon, lat) order for GPX `<trkpt lat="..." lon="...">`

**Export Flow:**
1. F5 keyboard trigger via `Screen.keyboard_bind('<F5>', export_handler)`
2. Check if route has been computed
3. Get route coordinates from where they're stored
4. Transform each coordinate to WGS84 using pyproj
5. Generate GPX XML structure
6. Show file save dialog: `tkinter.filedialog.asksaveasfilename(defaultextension=".gpx")`
7. Write GPX file with UTF-8 encoding

### 3. Route State Management

**Missing Pieces (requires investigation/planning):**
- Where is route computation triggered? (likely after Shift-F10 end point selection)
- Where are route results stored? (need to add route storage to Screen or main app)
- How to access current screen world file for coordinate transformation?

**Potential Storage Options:**
- Add `self._current_route = None` and `self._route_coordinates = []` to Screen class
- Store route as list of screen coordinates for immediate display
- Store route as list of network EPSG coordinates for GPX export

## Implementation Considerations

### F5 Key Conflict

**Current State:**
- F5 is bound to `_read_image()` for loading raster images (line 62)

**Options:**
1. Rebind F5 to export and add fallback: Shift-F5 for image read (Shift-F5 already exists)
2. Use different key for export (e.g., Ctrl-E, F6)
3. Add keyboard modal check: only trigger export if route computed, else read image

**Context from D-08:** User chose F5 specifically for export, implying intent to rebind or handle conflict.

### Coordinate System Handling

**Route Coordinates in Network EPSG:**
- Routing network typically in UTM zone (e.g., 25832 for Norway UTM 32V)
- Screen uses world file for transformation
- GPX requires WGS84 (EPSG:4326)

**Transformation Chain:**
1. Network EPSG → Screen coordinates: Use inverse of `Screen.screen_to_decimal_degrees()` pattern
2. Network EPSG → WGS84 for GPX: Use pyproj `Transformer.from_crs(network_epsg, 4326)`

### GPX Compatibility

**GPS Device Standards:**
- Most modern GPS devices accept GPX 1.1 schema
- Track-only format is widely compatible (no waypoints, minimal metadata)
- WGS84 coordinates are mandatory (EPSG:4326)

**Validation Plan (05-04):**
- Test GPX export with common devices: Garmin, Suunto, smartphone apps (Gaia GPS, AllTrails)
- Verify GPX file validates against GPX 1.1 schema
- Check coordinate precision (6 decimal places ≈ 0.1 meter accuracy)

## Implementation Patterns

### Route Display Pattern (from Screen class)
```python
# Drawing polylines on canvas
screen.draw_polyline(
    polyline=[[x1, y1], [x2, y2], ...],  # screen coordinates
    width=3,  # medium width per D-03
    colour='red',  # bright distinctive color per D-02
    tag='route'  # for clearing per D-06
)

# Clearing old routes
screen.delete('route')
```

### Keyboard Binding Pattern (from Screen class)
```python
# Bind keyboard shortcut
screen.keyboard_bind('<F5>', export_gpx_handler)

# Handler function with event parameter
def export_gpx_handler(event):
    # Implementation here
    pass
```

### GPX Export Pattern
```python
# Transform coordinates to WGS84
from pyproj import Transformer
transformer = Transformer.from_crs(network_epsg, 4326, always_xy=True)
for (x, y) in route_coords:
    lon, lat = transformer.transform(x, y)
    gpx_points.append(f'<trkpt lat="{lat:.6f}" lon="{lon:.6f}"></trkpt>')

# File save dialog
from tkinter import filedialog
filename = filedialog.asksaveasfilename(
    defaultextension=".gpx",
    filetypes=[("GPX files", "*.gpx"), ("All files", "*.*")]
)
```

## Dependencies

### Required Libraries (already in project)
- `tkinter`: Desktop GUI (Python standard library)
- `pyproj`: Coordinate transformations (already used in screen_2026.py)
- Standard library: `xml.etree.ElementTree` or simple f-string XML generation

### Integration Points
- `routing_2026.py`: RoutingNetwork API for route computation
- `screen_2026.py`: Canvas rendering and keyboard bindings
- `utilities_2026.py`: File I/O patterns (if needed for dialogs)

## Risks and Considerations

1. **F5 Key Conflict**: User chose F5 for export, but it's bound to image read. Needs careful handling.
2. **Coordinate Transformation**: Route coordinates may need transformation through two systems (network → screen, network → WGS84).
3. **Route State Storage**: Need to determine where route results are stored and accessed.
4. **GPX Schema Compliance**: Must ensure GPX output is valid XML with proper namespace.
5. **Testing GPS Compatibility**: Validation requires testing with actual GPS devices or simulators.

## Next Steps for Planning

1. **Determine trigger point**: Where is route computation triggered? Add handler there.
2. **Design route state**: Add route storage to Screen or app state module.
3. **Resolve F5 conflict**: Decide rebinding strategy per user's F5 choice.
4. **Plan coordinate transformations**: Network EPSG → screen coordinates, Network EPSG → WGS84.
5. **Structure GPX export**: Design XML generation with proper schema.
6. **Design validation approach**: How to test GPX compatibility for plan 05-04.

## Research Questions Answered

✓ How to display routes on tkinter canvas? → Use `Screen.draw_polyline()` with distinctive styling
✓ How to transform coordinates? → pyproj for EPSG transformations, world file for screen coordinates
✓ How to handle F5 key conflict? → Rebind or modal check - user chose F5 for export
✓ What GPX format to use? → Track-only GPX 1.1 with WGS84 coordinates
✓ How to export file? → tkinter.filedialog for save dialog, UTF-8 encoding
✓ What drawing primitives exist? → `draw_polyline()`, `draw_point()` with color, width, tag parameters
✓ How to clear old routes? → `Screen.delete()` with route tag
✓ What coordinate systems are involved? → Network EPSG (e.g., 25832), Screen coordinates, WGS84 (4326)

## RESEARCH COMPLETE

All research questions answered. Context, codebase patterns, and integration points identified. Ready for detailed planning.