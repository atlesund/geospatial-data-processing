# Phase 7: Terrain Auto-Mesh Generation - Research

**Generated:** 2026-04-20
**Status:** Complete

---

## Objective

Research how to automatically trigger routing network generation from loaded terrain data, enabling seamless workflow where terrain file load directly produces routable network.

**Core Question:** What patterns exist for auto-triggering mesh generation after terrain load, and how to wire this into Screen/Raster classes?

---

## Domain Research: Terrain Processing Workflow

### Current State (Pre-Phase 7)

**Manual workflow (what happens now):**
```bash
# User loads terrain via F5
screen.load_raster() -> raster.read_image() -> GeoTIFF loaded

# Manual step (what Phase 7 should automate):
network = terrain_mesh_from_raster(raster, mesh_spacing=100)
screen.set_route_network(network)
```

**Problem:** User must manually create network in example code. Phase 6 GUI routing expects pre-existing network.

### Existing Integration Points

**Screen class:**
- `load_raster()` method (F5 binding) - loads raster, calls `raster.read_image()`
- `set_route_network(network)` method (Phase 6) - assigns network for routing
- `_route_network` attribute - stores RoutingNetwork instance

**Raster class:**
- `read_image()` method - handles GeoTIFF loading with rasterio
- `_read_geotiff()` method - extracts affine transform, EPSG, elevation grid
- Returns populated Raster instance with `_elevation_grid`, `_epsg`, `_world_file`

**Routing module:**
- `terrain_mesh_from_raster(raster, mesh_spacing=100)` - generates RoutingNetwork from raster
- Already handles CORS conversion, water features, slope penalties
- Returns complete RoutingNetwork instance ready for use

### Trigger Options

| Option | Location | Pros | Cons |
|--------|----------|------|------|
| **A: Modify Screen.load_raster()** | screen_2026.py, after raster loaded | Central location, clear auto-behavior, inherits raster epsg | Screen becomes responsible for mesh creation (mixed concerns) |
| **B: Add Raster.auto_mesh() callback** | raster_2026.py, after _read_geotiff() | Clean separation - raster owns its mesh generation | Requires wiring callback registration |
| **C: Add Screen._auto_generate_network()** | screen_2026.py, separate method from load_raster() | Explicit trigger, testable independently | Still requires call from somewhere |
| **D: Create AutoMesh wrapper class** | new module, e.g., auto_mesh_2026.py | Separates concerns, reusable across contexts | New file, added complexity |

**Recommended: Option A** - Modify `Screen.load_raster()` to auto-generate network after terrain load.
- Reasons:
  - Screen already has route network responsibility (set_route_network from Phase 6)
  - User expects F5 to "just work" for routing
  - Minimal code changes (add ~30 lines after F5 binding)
  - Follows existing Screen.load_* pattern

---

## Technical Implementation Research

### 1. Trigger Point in Screen.load_raster()

**Current code pattern:**
```python
def load_raster(self):
    self._raster = Raster()
    self._raster.read_image()
    # Raster now loaded
```

**Proposed addition:**
```python
def load_raster(self):
    self._raster = Raster()
    self._raster.read_image()

    # Phase 7: Auto-generate routing network from terrain
    routing_net = terrain_mesh_from_raster(
        self._raster,
        mesh_spacing=100  # Default, or make configurable
    )
    self.set_route_network(routing_net)
```

### 2. Progress Indication

**Problem:** terrain_mesh_from_raster() can take 30-60 seconds for 100km × 100km terrain tiles (DTM50).

**Research findings:**
- Tkinter supports progress bars via `tkinter.ttk.Progressbar`
- Cursor changes already used in Phase 6 (`config(cursor='watch')`)
- Status text updates via `title(f"{base_title} -- Computing mesh...")`

**Approach for Phase 7:**
- Use cursor 'watch' during mesh generation (minimal code change, consistent with Phase 6)
- Add progress ticks: print statements to console (visible while cursor is watch)
- Optional: Add Screen._progress callback parameter if we want to wire progress bar later

**Recommendation:** Cursor change + console ticks only. Phase 7 should stay small; progress bar integration is Phase 8 material.

### 3. Error Handling Strategy

**Potential failures:**
1. GeoTIFF load fails (already handled by raster.read_image() with dialog)
2. terrain_mesh_from_raster() raises exception (water query failure, memory error)
3. Return value is None or empty network

**Research findings:**
- `utilities.warning()` already in use for error dialogs (Phase 6)
- terrain_mesh_from_raster() already has try-except for water feature queries
- NetworkX raises NetworkXNoPath for disconnected graphs (handled in Phase 6)

**Approach:**
```python
try:
    routing_net = terrain_mesh_from_raster(...
    self.set_route_network(routing_net)
    print(f"Mesh network created: {len(routing_net.graph.nodes)} nodes")
except Exception as e:
    utilities.warning(f"Failed to generate routing network: {e}")
    print(f"Error: {e}")
```

### 4. Parameter Handling

**Research question:** Should mesh_spacing be fixed (100m) or configurable?

**Findings:**
- terrain_mesh_from_raster() defaults to 100m spacing
- 100m = 10 nodes per km (100km tile = 1000 × 1000 = 1,000,000 nodes - too many!)
- 200m = 5 nodes per km (100km tile = 500 × 500 = 250,000 nodes - still heavy)
- Current test fixtures use 10-20m spacing for mock data

**Recommendation:**
- Fixed at 200m for v1 (performance vs detail tradeoff)
- Future v2: Add mesh_spacing parameter preference or slider UI
- Document decision clearly in Phase 7 context

### 5. Network Verification

**Problem:** What if mesh generation returns empty or malformed network?

**Research:**
- RoutingNetwork has .graph.nodes, .graph.edges for verification
- Empty network crashes Phase 6 routing (already validated in Phase 6)
- Should we verify before calling set_route_network()?

**Approach:**
```python
routing_net = terrain_mesh_from_raster(...

if len(routing_net.graph.nodes) == 0:
    utilities.warning("Network has no nodes — terrain may be invalid")
    # Don't assign empty network
else:
    self.set_route_network(routing_net)
```

---

## Dependency Analysis

### Phase 7 Provides to Phase 6

**From user-process.md Step 4 gap:**
- Phase 6 expects `screen._route_network` to be set
- Phase 7 sets this automatically via `screen.set_route_network()`
- Phase 6 can immediately route after point selection

**Dependency:**
```
Phase 7 → terrain_mesh_from_raster() → RoutingNetwork
Phase 7 → set_route_network() → stores in screen._route_network
Phase 6 → reads screen._route_network → computes shortest path
```

### Phase 7 Depends On

- Phase 2: RoutingNetwork class structure
- Phase 3: calculate_terrain_weight() function
- Phase 4: detect_water_crossing() function (optional fallback)
- Phase 5: set_route_network() method
- Existing: terrain_mesh_from_raster() implementation

### Execution Order

```
Phase 5: Adds set_route_network() to Screen ✓ (COMPLETE)
    ↓
Phase 7: Auto-generates network in load_raster() ← WE ARE HERE
    ↓
Phase 6: GUI routing uses auto-generated network
```

**Correct sequencing:** Phase 7 before Phase 6 execution.

---

## Code Patterns Research

### Existing Patterns to Follow

**1. Raster.load() → Raster object ready pattern:**
```python
# From example_302_raster_gui.py
raster = Raster()
raster.read_image()  # Populates _elevation_grid, _epsg, _world_file
```

**2. Cursor progress indication (Phase 6):**
```python
# From screen_2026.py _compute_and_display_route()
self._root.config(cursor='watch')
self._root.update_idletasks()
# ... computation ...
self._root.config(cursor='arrow')
```

**3. Error dialog pattern (Phase 6):**
```python
# From screen_2026.py
utilities.warning('Routing network not loaded. Load network data first.')
```

**4. Print debug pattern (existing):**
```python
print(f"Loaded GeoTIFF: {filename}")
print(f"  EPSG: {epsg}")
print(f"  Bounds: {bounds}")
```

### New Pattern for Phase 7

**Auto-trigger with validation pattern:**
```python
def load_raster(self):
    """Load raster and auto-generate routing network (Phase 7)."""
    # Load terrain data
    self._raster = Raster()
    self._raster.read_image()

    # Auto-generate network from terrain
    try:
        routing_net = terrain_mesh_from_raster(
            self._raster,
            mesh_spacing=200  # v1 fixed: 200m spacing for performance
        )

        # Validate network before assignment
        if len(routing_net.graph.nodes) == 0:
            utilities.warning(
                "Mesh generation produced empty network. "
                "Terrain data may be invalid."
            )
        else:
            self.set_route_network(routing_net)
    except Exception as e:
        utilities.warning(f"Failed to generate mesh: {e}")
        print(f"Mesh generation error: {e}")
```

---

## Edge Cases

### 1. User loads non-terrain raster (PNG without elevation)

**Current behavior:** Raster._elevation_grid = NaN
**Phase 7 behavior:** terrain_mesh_from_raster() returns empty network → warning dialog
**User experience:** File loads, but no route capability, clear error message

### 2. Multiple raster loads

**Current behavior:** Each F5 replaces self._raster
**Phase 7 behavior:** Each F5 regenerates network (replaces self._route_network)
**User experience:** Hot-reload works - change .tif file, F5, new mesh ready

### 3. Very large terrain (memory error)

**Current behavior:** terrain_mesh_from_raster() may raise MemoryError
**Phase 7 behavior:** Catch exception, warn user, leave ._route_network = None
**User experience:** F5 fails gracefully, can load smaller tile

### 4. Network already exists

**Question:** Should we warn before replacing existing network?
**Decision:** No - F5 is "reload", replacement is expected behavior

---

## Testing Strategy Research

### Test Coverage Needs

1. **Auto-trigger verification:**
   - load_raster() calls terrain_mesh_from_raster()
   - Network assigned to screen._route_network
   - Network has expected EPSG from raster

2. **Error handling:**
   - Empty network triggers warning
   - Exception triggers warning
   - Network not assigned after failure

3. **Progress indication:**
   - Cursor changes during mesh generation
   - Console output shows progress

4. **Parameter passing:**
   - mesh_spacing=200 passed correctly
   - Raster instance passed correctly

### Test Fixtures Needed

```python
@pytest.fixture
def mock_geotiff_raster():
    """Mock Raster with GeoTIFF attributes."""
    raster = Raster()
    raster._elevation_grid = np.ones((100, 100))  # 100×100 mock terrain
    raster._epsg = 32632
    raster._world_file = [50.0, 0.0, 0.0, -50.0, 600000.0, 6650000.0]
    return raster

@pytest.fixture
def screen_with_raster():
    """Screen with loaded raster."""
    screen = Screen()
    screen._raster = mock_geotiff_raster()
    return screen
```

---

## Summary: Implementation Knowledge

**To Phase 7 Planner:**

Phase 7 requires:
1. Modify `Screen.load_raster()` after terrain load
2. Call `terrain_mesh_from_raster(raster, mesh_spacing=200)`
3. Assign result via `self.set_route_network(network)`
4. Wrap in try-except with utilities.warning() on failure
5. Validate non-empty network before assignment
6. Cursor progress indication during generation

**Key design decisions:**
- Fixed 200m mesh spacing for v1 (not configurable)
- Auto-trigger on every load (manual network load still possible via set_route_network())
- Fail gracefully on errors (warning dialog, no crash)
- Network replacement on re-load (hot-reload workflow)

**Phase 6 dependency:**
- Phase 6 plans already exist and expect `screen._route_network`
- Phase 7 provides this automatically
- Execute Phase 7 first, then Phase 6

---

*Research generated: 2026-04-20*
*Phase: 07-terrain-auto-mesh-generation*