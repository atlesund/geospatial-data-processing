# Phase 6: GUI Routing Integration - Context

**Gathered:** 2026-04-16
**Status:** Ready for planning

## Phase Boundary

Connect point selection to routing computation. When user selects start and end points through the GUI (Shift-F9/F10), the system computes the optimal route using the routing network and displays it. The integration layer bridges the frontend point selection from Phase 1 with the routing algorithms from Phases 2-4 and the visualization from Phase 5.

## Implementation Decisions

### Routing Trigger Timing
- **D-01:** Auto-trigger after end point selection. Compute route immediately when user selects the end point (the second click in the start → end sequence). No manual key press required — routing begins as soon as both points are available.

### Coordinate Mapping Flow
- **D-02:** Screen → World → Network EPSG. Use the Screen's existing world file transformation (utilities.screen_to_world()) to convert pixel coordinates to world coordinates, then project to the routing network's EPSG (typically UTM 32V). This leverages existing coordinate transformation infrastructure.

### Node Snapping Strategy
- **D-03:** Snap to nearest graph node. Use RoutingNetwork.find_nearest_node() on the transformed coordinates in network EPSG to find the nearest existing graph node. Simple, avoids creating orphaned nodes, and ensures routes connect to the traversable network.

### Error Communication
- **D-04:** Message dialog for all error types. Use tkinter.messagebox.showwarning() or showinfo() to display ALL routing errors to the user — no path found, missing network data, coordinate system mismatch, transformation failures. Consistent, noticeable error handling that requires user acknowledgment.

### Claude's Discretion
- Progress indication during route computation for longer routes (loading cursor, status text)
- Initial validation of routing network availability before mapping starts
- Coordinate system validation when screen EPSG differs from network EPSG

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Dependencies
- `.planning/phases/01-map-interaction-user-selection/01-CONTEXT.md` — Shift-F9/F10 point selection, coordinate display
- `.planning/phases/02-routing-network-construction/02-CONTEXT.md` — RoutingNetwork structure, find_nearest_node() usage
- `.planning/phases/03-steep-terrain-penalty-routing/03-CONTEXT.md` — Terrain penalty integration
- `.planning/phases/04-water-body-penalty-routing/04-CONTEXT.md` — Water penalty integration
- `.planning/phases/05-route-visualization-export/05-CONTEXT.md` — Route display via draw_polyline(), F5 export

### Screen Class API
- `screen_2026.py:24-28` — _start_point, _end_point, _route_stage attributes (current point selection state)
- `screen_2026.py:137-169` — _select_route_point() method (handles start and end selection)
- `screen_2026.py:171-181` — _start_route_selection() method (Shift-F9 binding)
- `screen_2026.py:183-193` — _stop_route_selection() method (Shift-F10 binding)

### RoutingNetwork API
- `routing_2026.py:77-92` — shortest_path() method for path computation
- `routing_2026.py:95-135` — find_nearest_node() method for snapping clicked points to graph nodes
- `routing_2026.py:20-41` — RoutingNetwork.__init__() structure (graph, node_coords, epsg)

### Coordinate Transformations
- `utilities_2026.py` — screen_to_world() function (convert pixel to world using world file)
- `utilities_2026.py` — world_to_screen() function (convert world to pixel for route display)
- `vector_2026.py` — project() method for EPSG transformations (if network needs conversion)

### Route Visualization Integration
- `screen_2026.py:26-35` — _current_route and _route_network_coords storage attributes (where route data goes)
- `screen_2026.py:451-499` — export_gpx() method for F5 export (reads _route_network_coords)
- `screen_2026.py` — draw_polyline() method signature

### Error Handling Patterns
- `utilities_2026.py:utilities.warning()` function for tkinter message dialogs
- .planning/codebase/CONVENTIONS.md — Error handling patterns (try-except with None returns)

No external specs — requirements fully captured in decisions above

## Existing Code Insights

### Reusable Assets
- `Screen._start_point`, `Screen._end_point` — Store selected point coordinates (set by Shift-F9/F10)
- `Screen._route_stage` — Tracks selection state ('start' → 'end' → reset for next pair)
- `RoutingNetwork.find_nearest_node()` — KDTree-based snapping to graph nodes O(log n)
- `RoutingNetwork.shortest_path()` — Dijkstra algorithm returns node ID list
- `utilities.screen_to_world()` — Pixel to world coordinate conversion using world file
- `utilities.warning()` — Show error dialog to user
- `Screen.draw_polyline()` — Visualize computed route
- `Screen._route_network_coords` — Store network EPSG coordinates for GPX export

### Established Patterns
- Two-stage point selection: first click = start (red marker), second click = end (blue marker)
- Stage toggling in _route_stage variable ('start' → 'end' → 'start' for reset)
- Keyboard shortcuts for screen interaction (F9, F10, F5 established patterns)
- Message dialogs via utilities.warning() for user-facing errors
- Coordinate transformations via utility functions and pyproj when needed

### Integration Points
- **Point selection → Routing:** In _select_route_point() after end point is selected (when _route_stage switches from 'end' to 'start'), trigger route computation
- **Screen coords → Network coords:** Click coordinates (pixel) → screen_to_world() → project to network EPSG → find_nearest_node()
- **Routing computation:** RoutingNetwork.shortest_path(start_node, end_node) returns node ID list
- **Path to coordinates:** Map node IDs → RoutingNetwork.node_coords[node_id] for (x, y) tuples
- **Coordinates to display:** World coordinates → world_to_screen() → Screen.draw_polyline()
- **Coordinates to export:** Store network EPSG coordinates in _route_network_coords for F5 export
- **Error feedback:** On routing failure, call utilities.warning() with clear explanation message

### Routing Integration envisioned workflow:
1. User presses Shift-F9 → route_stage = 'start', wait for clicks
2. User clicks → _start_point set, red marker drawn, route_stage = 'end'
3. User clicks → _end_point set, blue marker drawn, route_stage = 'start' (ready for next pair)
4. **NEW IN PHASE 6:** When end point selected, auto-trigger routing:
   a. Transform both screen coords to world coords via screen_to_world()
   b. Project both to network EPSG if needed
   c. Call RoutingNetwork.find_nearest_node() for each point
   d. Call RoutingNetwork.shortest_path() with node IDs
   e. Map node ID path back to coordinates via node_coords
   f. Store _route_network_coords for GPX export
   g. Convert to screen coords via world_to_screen()
   h. Call Screen.draw_polyline() with route styling
   i. On any error: utilities.warning(error_message)

## Specific Ideas

- Auto-trigger at end point selection keeps workflow simple — user clicks twice and gets immediate route feedback
- Using world file transformations (screen_to_world / world_to_screen) leverages existing Screen infrastructure
- Snapping to nearest node ensures routes connect to the traversable network rather than creating unrealistic isolated points
- Message dialogs for all errors create consistent, noticeable feedback — won't be in the console where users might miss it
- Integration at the end of the two-stage selection cycle (_route_stage transitioning from 'end' to 'start') is the natural place to trigger computation

## Deferred Ideas

None — discussion stayed within phase scope

---

*Phase: 06-gui-routing-integration-connect-point-selection-with-routing*
*Context gathered: 2026-04-16*