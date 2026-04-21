# Phase 7: Terrain Auto-Mesh Generation - Context

**Gathered:** 2026-04-20
**Status:** Ready for planning

## Phase Boundary

Automatically generate routing networks from loaded terrain data, removing manual network creation step from user workflow. When user loads a GeoTIFF terrain file via F5, the system should automatically create a routing mesh using the existing terrain_mesh_from_raster() function and assign it to the screen for immediate route computation.

## Implementation Decisions

### Trigger Location
- **D-01:** Auto-generate network in Screen.load_raster(). Modify the existing F5 binding method to call terrain_mesh_from_raster() after raster.read_image() completes. This is the most straightforward integration point.

### Mesh Spacing
- **D-02:** Fixed 200m spacing for v1. Performance tradeoff - 200m spacing balances node count (~250K nodes for 100km tile) with route quality. Not configurable in v1; defer spacing UI to v2.

### Progress Indication
- **D-03:** Cursor change + console output. Use cursor='watch' during mesh generation (30-60 seconds per DTM50 tile), print tick messages to console for visibility. Keep simple - no progress bar in v1.

### Error Handling
- **D-04:** Warning dialogs for all failures. Wrap mesh generation in try-except, use utilities.warning() for exceptions, validate non-empty network before assignment. Failures should not crash the application.

### Network Validation
- **D-05:** Validate network non-emptiness before assignment. Check len(network.graph.nodes) > 0, warn user if mesh generation produced empty network, don't assign empty values.

### Hot Reload Support
- **D-06:** Network replacement on re-load. Each F5 replaces both terrain and network, enabling hot-reload workflow for testing tile changes without restart.

### Claude's Discretion
- None - all major decisions specified above

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Dependencies
- `.planning/phases/02-routing-network-construction/02-CONTEXT.md` — RoutingNetwork structure, terrain_mesh_from_raster() function
- `.planning/phases/03-steep-terrain-penalty-routing/03-CONTEXT.md` — Terrain penalty integration
- `.planning/phases/04-water-body-penalty-routing/04-CONTEXT.md` — Water penalty integration
- `.planning/phases/05-route-visualization-export/05-CONTEXT.md` — set_route_network() method
- `.planning/phases/06-gui-routing-integration-connect-point-selection-with-routing/06-CONTEXT.md` — GUI routing expects pre-existing network

### Function Signatures
- `routing_2026.py:393` — terrain_mesh_from_raster(raster, mesh_spacing=100, bbox=None) → RoutingNetwork
- `screen_2026.py` — set_route_network(network) method (from Phase 6 plans)
- `utilities_2026.py:37-39` — warning(message, title='Warning') for error dialogs

### Pattern References
- `.planning/phases/07-terrain-auto-mesh-generation/07-PATTERNS.md` — Code patterns for auto-trigger, progress indication, error handling

### Integration Points
- Screen._read_image() → after raster.read_image() call, add mesh generation
- terrain_mesh_from_raster() → uses raster._elevation_grid, raster._epsg, raster._world_file
- set_route_network() → assigns result to self._route_network

No external specs — requirements fully captured in decisions above

## Specific Ideas

- Modify screen_2026.py _read_image() method (F5 binding) - insert ~30 lines after raster.load()
- Import terrain_mesh_from_raster at module level if not already present
- Fixed mesh_spacing=200 parameter for v1 (not exposed to user)
- Cursor progress indication matches Phase 6 pattern for consistency
- Warning dialogs use existing utilities.warning() function
- Empty network check prevents Phase 6 routing crashes

## Deferred Ideas

- Mesh spacing UI control/slider (v2 feature)
- Progress bar during mesh generation (v2 feature)
- Cancellation of in-progress mesh generation (v2 feature)
- Mesh configuration dialog (spacing, water penalty toggle, etc.)

---

*Phase: 07-terrain-auto-mesh-generation*
*Context gathered: 2026-04-20*