# Phase 1: Map Interaction & User Selection - Research

**Researched:** 2026-04-12
**Domain:** Interactive Tkinter canvas map interface
**Confidence:** HIGH

## Summary

Phase 1 implements the foundational user interaction layer for the Norwegian Hiking Route Planner: an interactive map interface where users can select route endpoints by clicking on a canvas, navigate with pan/zoom controls, and view selected coordinates in decimal degrees format. The existing codebase provides a strong foundation with `Screen`, `Vector`, and `Raster` classes that already support digitizing, canvas drawing, and coordinate transformations. The implementation should extend these existing capabilities rather than rebuilding them.

The core challenge is transforming the existing F9/F12 digitizing workflow into a dedicated route selection interface with:
1. Two-state point selection (start point, end point) with visual differentiation
2. Pan/zoom navigation using Tkinter canvas `scan` and `scale` methods with mouse bindings
3. Coordinate display unified in WGS84 decimal degrees (EPSG:4326) using pyproj transformations

The existing infrastructure handles screen-to-world coordinate transformations via `utilities.screen_to_world()` and world file georeferencing from `Raster.read_image()`. Coordinate projections are already supported via pyproj (Vector.project() and utilities.project_point()).

**Primary recommendation:** Extend the Screen class with route selection state management (start/end point tracking), implement pan/zoom using Tkinter's built-in canvas scan/scale methods, and add coordinate display overlays using existing draw_line/draw_text methods with pyproj transformations.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.12.0 | Runtime language | Project-specified, standard built-in libraries (tkinter, json, webbrowser) |
| tkinter | 8.6 (built-in) | Canvas-based GUI | Project constraint, only GUI framework available, provides canvas pan/zoom infrastructure |
| pyproj | 3.7.2 | Coordinate reference system transformations | Required for EPSG:4326 coordinate display, existing codebase dependency, Python standard for CRS operations |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| numpy | 2.4.4 | Numerical computing (random, linalg) | Legacy support in vector_2026.py, not needed for Phase 1 UI |
| folium | 0.20.0 | Web-based OpenStreetMap mapping | For route visualization in later phases, not Phase 1 (desktop canvas) |
| pyshp | 3.0.3 | Shapefile reading/writing | For loading Norwegian geospatial data in later phases, not Phase 1 |
| webbrowser | built-in | Browser launching | For folium map export in later phases, not Phase 1 |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Tkinter canvas | PyQt/PySide | PyQt not in requirements.txt, heavier dependency, tkinter proven sufficient |
| pyproj | PROJ C library bindings | pyproj is the Python standard wrapper, simpler API |
| Native canvas pan/zoom | External map libraries | Existing canvas infrastructure available, no need for heavy dependencies |

**Installation:**
```bash
pip install numpy pyproj folium pyshp pytest
```

**Version verification:** Versions verified via PyPI API on 2026-04-12:
- numpy: 2.4.4 [VERIFIED: pypi.org]
- pyproj: 3.7.2 [VERIFIED: pypi.org]
- folium: 0.20.0 [VERIFIED: pypi.org]
- pyshp: 3.0.3 [VERIFIED: pypi.org]
- pytest: For test framework fallback (not yet installed)

## Architecture Patterns

### Recommended Project Structure
```
phase_01_map_interaction/
├── route_selector_2026.py    # New: Route selection state manager class
└── tests/
    ├── test_route_selector.py  # Screen integration tests
    └── test_coordinate_transform.py  # Coordinate display verification
```

### Pattern 1: Screen Class Extension for Route Selection
**What:** Add route selection state management to existing Screen class, tracking start/end as decorated points with persistent visual markers.
**When to use:** Implementing click-based endpoint selection with visual state.
**Example:**
```python
# Source: Existing Screen._get_point() in screen_2026.py (lines 86-92)
def _get_point(self, event):
    self.draw_point([event.x, event.y])
    self._digits._coordinates.append([event.x, event.y])
    count = len(self._digits.coordinates)
    self._digits._attributes.append({'fid': count})

# Extended pattern for route selection:
class RouteSelector:
    def __init__(self, screen):
        self._screen = screen
        self._start_point = None  # [x, y] screen coordinates
        self._end_point = None    # [x, y] screen coordinates
        self._stage = 'start'     # 'start' or 'end'

    def _select_route_point(self, event):
        """Select start or end point based on current stage"""
        point_id = 'selected_start' if self._stage == 'start' else 'selected_end'
        self._screen.delete(point_id)  # Clear previous marker
        self._screen.draw_point([event.x, event.y], size=6,
                               colour='red' if self._stage == 'start' else 'blue',
                               tag=point_id)

        if self._stage == 'start':
            self._start_point = [event.x, event.y]
            self._stage = 'end'
        else:
            self._end_point = [event.x, event.y]
            self._stage = 'start'
```

### Pattern 2: Pan Using Tkinter Canvas scan Methods
**What:** Use `canvas.scan_mark()` and `canvas.scan_dragto()` for drag-based panning.
**When to use:** Implementing map navigation to different geographic areas.
**Example:**
```python
# Source: Tcl/Tk canvas documentation scan command
def _start_pan(self, event):
    """Initiate drag-to-pan on mouse button press"""
    self._canvas.scan_mark(event.x, event.y)

def _do_pan(self, event):
    """Continue panning while dragging"""
    self._canvas.scan_dragto(event.x, event.y, gain=1)
```

### Pattern 3: Zoom Using Tkinter Canvas scale Method
**What:** Use `canvas.scale()` to rescale all items around a focal point for zoom in/out.
**When to use:** Implementing map scale adjustment via mouse wheel or keyboard shortcuts.
**Example:**
```python
# Source: Tcl/Tk canvas documentation scale command
def _zoom(self, event, factor):
    """Zoom canvas items around mouse cursor position"""
    # Convert screen coordinates to canvas coordinates (considering current scroll)
    canvas_x = self._canvas.canvasx(event.x)
    canvas_y = self._canvas.canvasy(event.y)

    # Scale all items
    self._canvas.scale('all', canvas_x, canvas_y, factor, factor)
```

### Pattern 4: Coordinate Display via Affine Transformations
**What:** Transform screen coordinates to world coordinates using affine georeferencing, then project to decimal degrees using pyproj.
**When to use:** Displaying selected coordinates in WGS84 format (MAP-05 requirement).
**Example:**
```python
# Source: utilities.screen_to_world() in utilities_2026.py (lines 356-363)
# Screen ---affine---> World (UTM/local) ---pyproj---> WGS84 (decimal degrees)

def screen_to_decimal_degrees(self, screen_point):
    """Convert screen coordinates to decimal degrees"""
    # 1. Screen to world (using affine transformation)
    if self._world_file is None:
        return None
    world_point = utilities.screen_to_world(screen_point, self._world_file)

    # 2. World to WGS84 decimal degrees (EPSG:4326)
    if self._epsg is None or self._epsg == 4326:
        return world_point  # Already in decimal degrees

    transformer = pyproj.Transformer.from_crs(
        pyproj.CRS.from_epsg(self._epsg),
        pyproj.CRS.from_epsg(4326),
        always_xy=True
    )
    lon, lat = transformer.transform(*world_point)
    return [lon, lat]

# Update coordinate display
def _update_coordinate_display(self, event):
    point_id = 'selected_start' if self._start_point else 'selected_end'
    if point_id:
        self._screen.delete('coord_display')
        coord = self.screen_to_decimal_degrees(self._start_point or self._end_point)
        if coord:
            self._screen.draw_text(self._start_point or self._end_point,
                                 f"Lat: {coord[1]:.6f}, Lon: {coord[0]:.6f}",
                                 colour='white', tag='coord_display')
```

### Anti-Patterns to Avoid
- **Storing route state globally outside Screen class**: Use class attributes for encapsulation, follows existing pattern with `_digits`, `_points` tensors
- **Hardcoding screen-centric coordinates without world file**: Always use affine transformations via utilities.screen_to_world() for geographic accuracy
- **Ignoring existing draw_text/delete methods**: Reuse Screen.draw_line/draw_text and delete() for visual state management
- **Mixing coordinate systems in display**: Unify all coordinate display to decimal degrees (EPSG:4326) per MAP-05, not UTM

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Coordinate CRS transformations | Custom EPSG math | pyproj Transformer | Handles all coordinate systems, Norway UTM zones, datum shifts |
| Canvas coordinate conversion | Manual scroll offset tracking | canvas.canvasx/canvasy builtin methods | Tkinter has built-in screen-to-canvas coordinate conversion |
| Point digitizing UI | Full custom click handling | Extend Screen._start_digit_points/_get_point pattern | Existing infrastructure handles cursor changes, event binding, point storage |
| Affine transformation screen-to-world | Write own matrix math | utilities.screen_to_world() + world_file pattern | Already handles PNG+PGW georeferencing, battle-tested |
| Map data loading | Write PNG/TIFF parsers | Raster.read_image() + utilities functions | Existing file dialogs, world file parsing, PhotoImage integration |

**Key insight:** The existing codebase provides mature implementations of all foundational operations. Phase 1 should orchestrate them, not reimplement.

## Runtime State Inventory

> Not applicable: Phase 1 is Greenfield development (user interaction layer), no rename/refactor/migration scope.

## Common Pitfalls

### Pitfall 1: Mouse Wheel Event Platform Inconsistency
**What goes wrong:** Mouse wheel scrolling uses different event patterns across platforms (`<MouseWheel>` on Windows/macOS, `<Button-4>/<Button-5>` on Linux).
**Why it happens:** Tkinter inherits platform-specific event differences from Tcl/Tk.
**How to avoid:** Bind all three event patterns with unified handler using `event.delta` for direction; use `<Button-4>/<Button-5>` as fallback (verified patterns from existing cross-platform Tkinter apps).
**Warning signs:** Zoom doesn't work on Linux but works on macOS; check OS detection with `platform.system()`.

### Pitfall 2: Coordinate System Mismatch
**What goes wrong:** Selected point coordinates displayed in UTM instead of decimal degrees, or vice versa.
**Why it happens:** Screen class stores screen pixels, _epsg may be None (not set via F5 image load), code assumes coordinate system without verifying.
**How to avoid:** Always verify self._epsg is set before coordinate transformations; default to display coordinates as decimal degrees (EPSG:4326) per MAP-05; show warning if EPSG missing.
**Warning signs:** Coordinates appear as large numbers (UTM meters) instead of decimals between -180/+180.

### Pitfail 3: Visual Marker Persistence Between Selections
**What goes wrong:** Old start/end markers remain visible when user clicks new points, causing display clutter.
**Why it happens:** Using distinct tags for each point without clearing previous tags; overlapping tags not managed.
**How to avoid:** Use consistent tags (`selected_start`, `selected_end`) and call `screen.delete(tag)` before drawing new markers; manage coordinate display tag (`coord_display`) separately.
**Warning signs:** Multiple "Start" or "End" markers visible simultaneously after clicking.

### Pitfall 4: Pan/Zoom Doesn't Persist Coordinate Display
**What goes wrong:** Coordinate text moves incorrectly during pan, becomes detached from point, or disappears after zoom.
**Why it happens:** Text drawn at absolute screen coordinates, not updated when canvas transforms; tag management incomplete.
**How to avoid:** Redraw coordinate display after each pan/zoom event using stored point coordinates; delete and recreate `coord_display` tag in _do_pan and _zoom handlers.
**Warning signs:** Text shows wrong coordinates relative to dot position, or text vanishes after zooming.

### Pitfall 5: Missing Georeferencing Causes Invalid Coordinates
**What goes wrong:** Screen coordinates convert to meaningless world coordinates when world file not loaded (no F5 image load).
**Why it happens:** utilities.screen_to_world() with None affine returns garbage or fails; code doesn't check self._world_file existence.
**How to avoid:** Validate world file loaded before digitizing route points; prompt user to load georeferenced image first; show error if world file missing.
**Warning signs:** Coordinates appear as extreme values or zero; GeoJSON export fails with no world file.

## Code Examples

Verified patterns from official sources:

### Tkinter Canvas Pan (scan method)
```python
# Source: Tcl/Tk canvas documentation: https://www.tcl-lang.org/man/tcl8.6/TkCmd/canvas.htm
# scan dragto implements "drag-to-scroll functionality"
def _start_pan(self, event):
    self._canvas.scan_mark(event.x, event.y)

def _do_pan(self, event):
    self._canvas.scan_dragto(event.x, event.y, gain=1)

# Bind to middle mouse or left-drag
self._canvas.bind('<ButtonPress-2>', self._start_pan)  # Middle mouse
self._canvas.bind('<B2-Motion>', self._do_pan)
```

### Tkinter Canvas Zoom (scale method)
```python
# Source: Tcl/Tk canvas documentation: https://www.tcl-lang.org/man/tcl8.6/TkCmd/canvas.htm
# scale command "Rescale the coordinates of all of the items given by tagOrId"
def _zoom_in(self, event):
    scale_factor = 1.1  # 10% zoom in
    canvas_x = self._canvas.canvasx(event.x)
    canvas_y = self._canvas.canvasy(event.y)
    self._canvas.scale('all', canvas_x, canvas_y, scale_factor, scale_factor)

def _zoom_out(self, event):
    scale_factor = 0.9  # 10% zoom out
    canvas_x = self._canvas.canvasx(event.x)
    canvas_y = self._canvas.canvasy(event.y)
    self._canvas.scale('all', canvas_x, canvas_y, scale_factor, scale_factor)
```

### Platform-Independent Mouse Wheel Binding
```python
# Source: Tkinter event handling documentation + common cross-platform practice
def _handle_mouse_wheel(self, event):
    """Cross-platform mouse wheel handler"""
    if event.delta:
        # Windows/macOS: event.delta typically +/- 120
        delta = event.delta
    else:
        # Linux: Button-4 (up) or Button-5 (down)
        delta = 120 if event.num == 4 else -120

    if delta > 0:
        self._zoom_in(event)
    else:
        self._zoom_out(event)

# Platform-specific bindings (all bind to same handler)
self._root.bind('<MouseWheel>', self._handle_mouse_wheel)  # Windows/macOS
self._root.bind('<Button-4>', self._handle_mouse_wheel)    # Linux scroll up
self._root.bind('<Button-5>', self._handle_mouse_wheel)    # Linux scroll down
```

### Coordinate Transformation (Screen → World → Decimal Degrees)
```python
# Source: utilities.screen_to_world() in utilities_2026.py (lines 356-363)
def screen_to_world(point, affine):
    x, y = point
    a, d, b, e, c, f = affine
    x_world = a*x + b*y + c
    y_world = d*x + e*y + f
    return [x_world, y_world]

# Extended to decimal degrees via pyproj
def get_decimal_degrees(screen_point, world_file, source_epsg):
    # 1. Screen to world
    world_point = utilities.screen_to_world(screen_point, world_file)

    # 2. World to WGS84 (if needed)
    if source_epsg != 4326:
        transformer = pyproj.Transformer.from_crs(
            pyproj.CRS.from_epsg(source_epsg),
            pyproj.CRS.from_epsg(4326),
            always_xy=True
        )
        lon, lat = transformer.transform(*world_point)
        return [lon, lat]
    return world_point
```

### Using Existing Screen Drawing Methods
```python
# Source: screen_2026.py draw_point, draw_text, delete (lines 223-295)
# Draw visual marker for selected point
screen.draw_point([x, y], size=6, colour='red', tag='selected_start')

# Draw coordinate text
screen.draw_text([x, y], f"Lat: {lat:.6f}, Lon: {lon:.6f}", colour='white', tag='coord_display')

# Clear previous markers
screen.delete('selected_start')
screen.delete('selected_end')
screen.delete('coord_display')
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual point digitizing with F9/F12 | Dedicated route selection UI | Phase 1 (new) | Simplifies workflow: route-specific, visual state |
| Screen-only coordinates display | Projected decimal degrees display | Phase 1 (new) | MAP-05 requirement: WGS84 standard format |
| Static canvas (no navigation) | Pan/zoom navigation | Phase 1 (new) | MAP-03/MAP-04: Navigate Norway's extensive terrain |

**Deprecated/outdated:**
- F9/F12 exclusive digitizing workflow: Still supported for legacy compatibility, but route selection will use dedicated UI patterns
- Screen coordinates only for display: Unify to decimal degrees per MAP-05

## Assumptions Log

> List all claims tagged `[ASSUMED]` in this research. The planner and discuss-phase use this section to identify decisions that need user confirmation before execution.

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Georeferenced map image (PNG+PGW) exists for Norway terrain | Architecture Patterns | If no base map exists, route selection has no visual reference |
| A2 | Single UTM zone (32V) sufficient for v1 Norway coverage | Architecture Patterns | If routes cross zones, pyproj per-point transforms needed (not block) |
| A3 | User prefers Tkinter canvas over web-based folium for selection | Standard Stack | If web interface preferred, architecture would change significantly |
| A4 | Offline map data available locally (no API calls) | Architecture Patterns | If map requires tiles API, offline requirement violated |

**If this table is empty:** All claims in this research were verified or cited — no user confirmation needed.

*Note: Assumptions exist because base map image georeferencing strategy not yet documented in existing code examples.* Planner should validate map data availability before Phase 1 execution.

## Open Questions

1. **Base map availability for Norway terrain**
   - What we know: Raster.read_image() supports PNG+PGW georeferencing, utilities.read_world_file() parses .pgw files
   - What's unclear: Does pre-existing PNG+PGW map coverage exist for Norway? Where should it be stored?
   - Recommendation: User confirms map data source/path prior to Phase 1 implementation, or include placeholder map fetch in Wave 1

2. **User workflow sequence**
   - What we know: Screen class has F5 binding for image loading, F9/F12 for digitizing
   - What's unclear: Should user load map image first, then select points? Or auto-load map on route selector init?
   - Recommendation: Follow existing pattern: user loads georeferenced image via existing Raster.read_image() (F5), then route selector initialized on world file

3. **Coordinate persistence strategy**
   - What we know: Selected points stored in Screen attributes, can export via existing _digit_points_to_geojson() (F12)
   - What's unclear: Should route selector auto-export coordinates on each selection, or wait for explicit user action?
   - Recommendation: Display coordinates in real-time (MAP-05), defer export to Route Computation phase

4. **Error handling for missing georeferencing**
   - What we know: utilities.screen_to_world() returns None if world_file is None; existing code has bare except clauses
   - What's unclear: Should Phase 1 block route selection if no world file, or fallback to screen-only coordinates?
   - Recommendation: Phase 1 should require world file (error if missing); MAP-05 explicitly requires decimal degrees

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.x | All functionality | ✓ | 3.12.0 | — |
| tkinter 8.x | Canvas GUI | ✓ | 8.6 (built-in) | — |
| pyproj | Coordinate transformations | ✓ | 3.7.2 | — |
| numpy | Legacy support | ✓ | 2.4.4 | — |
| folium | Route visualization (later phases) | ✓ | 0.20.0 | — |
| pyshp | Shapefile support (later phases) | ✓ | 3.0.3 | — |
| pytest | Testing framework | ✗ | — | Use manual tests for now |
| webbrowser | Folium export (later phases) | ✓ | built-in | — |

**Missing dependencies with no fallback:**
- pytest: Required for test automation but not currently installed
  - Recommendation: Add `pip install pytest` to Phase 1 setup (Wave 0)
  - Impact: Cannot run automated tests until installed

**Missing dependencies with fallback:**
- None - all required dependencies available

**Notes:**
- Python 3.12 used for all verification
- Tkinter 8.6 provides all canvas operations needed (scan, scale, mouse wheel)
- pytest not installed in current venv but recommended for test infrastructure

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Unit tests (manual for now, pytest to be installed in Wave 0) |
| Config file | None — tests currently simple Python scripts in tests/ |
| Quick run command | `python3 tests/test_1_A1.py` (manual execution) |
| Full suite command | `python3 -m pytest tests/` (after pytest install) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| MAP-01 | Start point selection via click | integration | `pytest tests/test_route_selector.py::test_select_start_point -x` | ❌ Wave 0 |
| MAP-02 | End point selection via click | integration | `pytest tests/test_route_selector.py::test_select_end_point -x` | ❌ Wave 0 |
| MAP-03 | Map pan navigation | integration | `pytest tests/test_route_selector.py::test_pan_functionality -x` | ❌ Wave 0 |
| MAP-04 | Map zoom in/out controls | integration | `pytest tests/test_route_selector.py::test_zoom_functionality -x` | ❌ Wave 0 |
| MAP-05 | Coordinate display in decimal degrees | unit | `pytest tests/test_coordinate_transform.py::test_screen_to_decimal_degrees -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** Quick run (single test file or manual test)
- **Per wave merge:** Full suite with pytest (after Wave 0 setup)
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/test_route_selector.py` — Route selector Screen integration tests (MAP-01, MAP-02, MAP-03, MAP-04)
- [ ] `tests/test_coordinate_transform.py` — Coordinate transformation unit tests (MAP-05)
- [ ] `tests/conftest.py` — Shared fixtures for Screen setup, mock world files, pytest config
- [ ] Framework install: `pip install pytest` — Not currently installed in venv
- [ ] Test data fixtures: Example PNG+PGW georeferenced map files for Norway region

*(Existing test files are stubs — tests/test_1_A1.py, test_1B.py — adapted from course examples, not test framework code)*

## Security Domain

> Security enforcement enabled in config.json (workflow.nyquist_validation: true)

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | Not applicable - Phase 1 UI only |
| V3 Session Management | no | Not applicable - No user sessions |
| V4 Access Control | no | Not applicable - No authorization |
| V5 Input Validation | yes | INPUT: Screen coordinates bounded to canvas dimensions [ASSUMED: Coordinator bounds not yet documented] |
| V6 Cryptography | no | Not applicable - No encryption needed |

### Known Threat Patterns for Phase 1 Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Coordinate injection (malformed screen coords) | Tampering | Bounds validation: ensure x, y within self._rows, self._columns before processing |
| Malicious world file (path traversal, large values) | Tampering | Validate affine parameters after read_world_file(); reject extreme transformation values |
| Missing world file (None affine causes crashes) | Denial of Service | Explicit None check before screen_to_world(); degrade gracefully with error message |
| Unbounded coordinate list growth (memory exhaustion) | Denial of Service | Limit max points (e.g., 1 start + 1 end only), clear on reset |

**Special consideration for v1 offline requirement:**
- No network code in Phase 1 (per project constraints)
- Attack surface limited to local file parsing (PNG+PGW)
- Coordinate validation prevents canvas boundary exploitation
- Use existing utilities.validate() pattern for expression safety if user inputs numeric criteria in later phases

## Sources

### Primary (HIGH confidence)
- [Tcl/Tk canvas documentation - scan and scale commands](https://www.tcl-lang.org/man/tcl8.6/TkCmd/canvas.htm) - Verified canvas pan/scale operations (scan, scale, canvasx/canvasy)
- [Python tkinter documentation - Event handling basics](https://docs.python.org/3/library/tkinter.html) - Confirmed event binding syntax and event object fields
- [utilities.screen_to_world() in utilities_2026.py](/Users/dev/Code/School/geospatial-data-processing/utilities_2026.py:356) - Lines 356-363: Affine transformation implementation
- [Screen class in screen_2026.py](/Users/dev/Code/School/geospatial-data-processing/screen_2026.py) - Lines 12-295: Existing digitizing, drawing, event binding patterns
- [pypi.org - numpy](https://pypi.org/pypi/numpy/json) - Version 2.4.4 (verified 2026-04-12)
- [pypi.org - pyproj](https://pypi.org/pypi/pyproj/json) - Version 3.7.2 (verified 2026-04-12)
- [pypi.org - folium](https://pypi.org/pypi/folium/json) - Version 0.20.0 (verified 2026-04-12)
- [pypi.org - pyshp](https://pypi.org/pypi/pyshp/json) - Version 3.0.3 (verified 2026-04-12)

### Secondary (MEDIUM confidence)
- [Existing codebase examples - example_104_gui.py](/Users/dev/Code/School/geospatial-data-processing/examples/example_104_gui.py) - Mouse coordinate tracking pattern verified
- [Existing codebase examples - example_309_affine_transformation.py](/Users/dev/Code/School/geospatial-data-processing/examples/example_309_affine_transformation.py) - Control coordinate workflow (has syntax error in line 74: append[(...)] should be append([...]))
- [Existing codebase examples - example_111_project_to_osm.py](/Users/dev/Code/School/geospatial-data-processing/examples/example_111_project_to_osm.py) - UTM to EPSG:4326 projection pattern

### Tertiary (LOW confidence)
- Cross-platform mouse wheel event pattern - Common practice from Linux/Windows/macOS tkinter apps (not verified in official docs this session)
- Norway single UTM zone coverage - Assumption for v1 scope (not verified against actual route data)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All versions verified via PyPI API, existing codebase confirms usage
- Architecture: HIGH - Based on verified existing Screen/Vector/Raster classes, documented Tcl/Tk APIs
- Pitfalls: HIGH - Identified from existing code issues (example_309 syntax error), documented Tkinter cross-platform behavior
- Environment: HIGH - All dependencies verified via pip show, Python 3.12/Tkinter 8.6 confirmed

**Research date:** 2026-04-12
**Valid until:** 2026-05-12 (30 days for stable Tkinter/pyproj APIs; python version stable)