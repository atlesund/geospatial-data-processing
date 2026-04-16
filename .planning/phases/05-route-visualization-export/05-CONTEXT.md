# Phase 5: Route Visualization & Export - Context

**Gathered:** 2026-04-16
**Status:** Ready for planning

## Phase Boundary

Display computed routes on the tkinter map interface and enable GPX file export for GPS navigation devices. The phase adds route visualization capabilities to the existing Screen class using the project's in-app canvas drawing approach, not browser-based folium HTML maps.

## Implementation Decisions

### Visualization Framework
- **D-01:** Tkinter window approach (Screen class), not folium HTML. Routes drawn directly in the desktop window using screen.draw_polyline() on the canvas. Integrates with existing Phase 1 map interaction and start/end point selection.

### Route Visual Style
- **D-02:** Bright distinctive color for the route. Use red, yellow, or orange - high contrast against the map for easy visibility. Common pattern in hiking applications.
- **D-03:** Medium line width (3-4 pixels). Clearly visible without obscuring map details. Matches Screen.draw_polyline() default of 3 pixels for consistency.
- **D-04:** Keep styling simple - no additional markers, patterns, or variations. Just color and width. Clean, straightforward route presentation.

### Visualization Behavior
- **D-05:** Auto-show route immediately after routing completes in the tkinter window. No user action required to see the result.
- **D-06:** Clear old routes before computing new route, then display. Replaces previous route - only the most recent route is visible. Clean slate each time routing is triggered.

### GPX Export Format
- **D-07:** Track-only GPX format. Export with <trk> element containing just the route coordinates. Minimal format compatible with most GPS navigation devices. No waypoints or route metadata.

### Export UI Flow
- **D-08:** Keyboard shortcut trigger. F5 function key to export GPX file. Follows existing F9 (start digitizing) and F12 (end digitizing) pattern for screen interaction.
- **D-09:** Standard file save dialog for export. User chooses location and filename when F5 is pressed. Uses tkinter.filedialog.asksaveasfilename() for consistency with existing file dialogs.

### Claude's Discretion
- Specific bright color selection (red vs yellow vs orange)
- Whether to add a visual indicator when export succeeds/displays a success message to user
- Error handling for export failures (file write errors, no route computed yet)
- Coordinate system transformation for GPX export (route coordinates in network EPSG may need conversion to WGS84)
- GPX track name generation (auto-generated vs fixed name vs prompt user)

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` — VIZ-01: System displays computed route polyline on interactive map with distinct visualization
- `.planning/REQUIREMENTS.md` — EXP-01: User can export route as GPX file for GPS navigation device use

### Code Conventions
- `.planning/codebase/CONVENTIONS.md` — Naming patterns, module structure, function design
- `.planning/codebase/ARCHITECTURE.md` — Screen class as presentation layer, event-driven GUI architecture

### Screen Drawing Methods
- `screen_2026.py:459-470` — draw_polyline() method for rendering route on canvas with width, color, and vertices parameters
- `screen_2026.py:434-456` — draw_point() method for rendering markers (if needed for start/end points)
- `screen_2026.py` — keyboard_bind() method for attaching F5 key handler for export

### Routing Network Integration
- `routing_2026.py:77-92` — shortest_path() returns list of node IDs forming the path
- `routing_2026.py` — node_coords dictionary mapping node IDs to (x, y) coordinate tuples in network EPSG

### Prior Phase Context
- `.planning/phases/01-map-interaction-user-selection/01-CONTEXT.md` — Screen canvas drawing patterns, coordinate display behavior
- `.planning/phases/02-routing-network-construction/02-CONTEXT.md` — RoutingNetwork structure, node coordinate storage format
- `.planning/phases/03-steep-terrain-penalty-routing/03-CONTEXT.md` — Terrain-based weight context
- `.planning/phases/04-water-body-penalty-routing/04-CONTEXT.md` — Water penalty context, combined weight calculation

### GPX Standard
- GPX 1.1 schema: <trk><trkseg><trkpt lat="..." lon="..."> structure
- GPX requires WGS84 coordinates (EPSG:4326) - route coordinates may need transformation
- Standard GPX namespace and XML header required for compatibility

No external specs — requirements fully captured in decisions above

## Existing Code Insights

### Reusable Assets
- `Screen.draw_polyline()` method: Already supports color, width parameters. Route visualization can call this directly with chosen styling.
- `Screen.draw_point()` method: If needed to add start/end markers alongside route. User chose simple styling, but point markers available if reconsidered.
- `Screen.keyboard_bind()` method: Used in Phase 1 for F9/F12 digitizing. Pattern for binding F5 export handler.
- RoutingNetwork.shortest_path(): Returns node ID list. Need to look up coordinates via RoutingNetwork.node_coords.
- RoutingNetwork.epsg property: Tracks network coordinate system. May need transformation to WGS84 for GPX export.

### Established Patterns
- Keyboard shortcuts for user-triggered actions (F9 start digitizing, F12 end digitizing). F5 export follows same pattern.
- Canvas drawing with tags: existing draw methods support tag parameter for deletion. Route can be tagged for clearing before new route (D-06).
- File dialogs via utilities file I/O functions: pattern for asking user for save location.
- Coordinate transformations: pyproj available (used in vector_2026.py). GPX export may transform from network EPSG to WGS84.

### Integration Points
- Route computation flow: RoutingNetwork.shortest_path() returns node IDs → look up coordinates in RoutingNetwork.node_coords → convert to screen coordinates → Screen.draw_polyline()
- Route clearing: Use Screen.delete() with route tag before displaying new route
- Export flow: F5 trigger → check if route exists → transform coordinates to WGS84 if needed → write GPX file via file dialog
- Coordinate system management: Route coordinates may be in routing network's EPSG (e.g., UTM 32V). GPX requires EPSG:4326. Use pyproj Transformer for per-point conversion.

## Specific Ideas

- User chose tkinter window over folium HTML - keeps everything in a single desktop application interface, no browser switching needed.
- Bright distinctive color (red/yellow/orange) - high contrast is critical for outdoor maps where users need to quickly identify their planned route.
- Medium line width (3-4px) - balances visibility with not obscuring underlying trail/road data.
- Auto-show route - eliminates extra clicks, user gets immediate feedback after routing computation.
- Clear and recalc - prevents visual clutter, always shows only the current route being planned.
- F5 for export - follows common convention (file save) and pairs with F9/F12 as screen interaction shortcuts.
- Track-only GPX - minimal format maximizes compatibility across GPS devices from different manufacturers.

## Deferred Ideas

None — discussion stayed within phase scope

---

*Phase: 05-route-visualization-export*
*Context gathered: 2026-04-16*