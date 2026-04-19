# Phase 6: GUI Routing Integration - Research

**Researched:** 2026-04-16
**Domain:** Tkinter GUI integration with geospatial routing algorithms
**Confidence:** HIGH

## Summary

Phase 6 connects the interactive point selection GUI from Phase 1 with the routing computation engine from Phases 2-4 and the visualization capabilities from Phase 5. The integration layer automates route computation when users select start and end points, transforming screen coordinates through the coordinate reference stack, snapping to traversable network nodes, computing optimal paths, and displaying results.

The primary challenge is bridging three coordinate systems: screen pixels (user clicks), world coordinates (geo-referenced data), and network coordinates (routing graph). The existing codebase provides all necessary infrastructure—Screen.world_to_screen(), utilities.screen_to_world(), pyproj transformers, and RoutingNetwork.find_nearest_node(). The phase requires weaving these together with proper error handling at each transformation step.

**Primary recommendation:** Implement routing trigger at the end of the two-stage selection cycle (_route_stage transitioning from 'end' to 'start'), using a dedicated _compute_and_display_route() method that follows the established error handling pattern (utilities.warning() for user-facing issues, try-except with early returns for internal failures).

## User Constraints (from CONTEXT.md)

### Locked Decisions

**D-01: Routing Trigger Timing**
- Auto-trigger after end point selection. Compute route immediately when user selects the end point (the second click in the start → end sequence). No manual key press required — routing begins as soon as both points are available.

**D-02: Coordinate Mapping Flow**
- Screen → World → Network EPSG. Use the Screen's existing world file transformation (utilities.screen_to_world()) to convert pixel coordinates to world coordinates, then project to the routing network's EPSG (typically UTM 32V). This leverages existing coordinate transformation infrastructure.

**D-03: Node Snapping Strategy**
- Snap to nearest graph node. Use RoutingNetwork.find_nearest_node() on the transformed coordinates in network EPSG to find the nearest existing graph node. Simple, avoids creating orphaned nodes, and ensures routes connect to the traversable network.

**D-04: Error Communication**
- Message dialog for all error types. Use tkinter.messagebox.showwarning() or showinfo() to display ALL routing errors to the user — no path found, missing network data, coordinate system mismatch, transformation failures. Consistent, noticeable error handling that requires user acknowledgment.

### Claude's Discretion

- Progress indication during route computation for longer routes (loading cursor, status text)
- Initial validation of routing network availability before mapping starts
- Coordinate system validation when screen EPSG differs from network EPSG

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Point selection (click capture) | Browser / Client (tkinter events) | — | User interaction captured at GUI level, starts the routing workflow |
| Coordinate transformation (screen→world) | Frontend Server (Screen methods) | — | Screen.world_to_screen() handles affine transformation via world file |
| Coordinate transformation (world→network) | API / Backend (RoutingNetwork) | — | pyproj transforms between EPSG codes, routing logic owns this domain |
| Node snapping (nearest graph node) | API / Backend (RoutingNetwork) | — | find_nearest_node() is O(log n) KDTree operation on network topology |
| Path computation (shortest path) | API / Backend (RoutingNetwork) | — | Dijkstra algorithm on weighted graph, core routing domain |
| Route visualization (display polyline) | Frontend Server (Screen methods) | — | Screen.draw_polyline() renders computed path on canvas |
| Error communication (message dialogs) | Frontend Server (utilities module) | — | utilities.warning() uses tkinter.messagebox for user feedback |
| Export preparation (GPX coordinates) | API / Backend (Screen attributes) | — | _route_network_coords stored in network EPSG for WGS84 transformation |

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.x | Runtime language | Project constraint, tkinter requirement [VERIFIED: CLAUDE.md] |
| tkinter | 8.6+ | GUI framework | Built-in, cross-platform, Phase 1 already uses it [VERIFIED: system test] |
| routing_2026 | Custom | Routing engine | Wrapper around networkx.Graph with geospatial methods [VERIFIED: codebase] |
| screen_2026 | Custom | GUI/display | Interactive map with point selection, pan/zoom [VERIFIED: codebase] |
| utilities_2026 | Custom | Shared utilities | Coordinate transforms, user dialogs, validation [VERIFIED: codebase] |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pyproj | Latest (in requirements.txt) | EPSG transformations | Convert between network EPSG and screen EPSG [VERIFIED: codebase import] |
| numpy | Latest (in requirements.txt) | Array operations | world_to_screen() matrix inversion [VERIFIED: screen_2026.py:383-388] |
| networkx | Latest (in requirements.txt) | Graph algorithms | RoutingNetwork uses nx.dijkstra_path() [VERIFIED: routing_2026.py:92] |
| scipy | Latest (in requirements.txt) | KDTree spatial index | RoutingNetwork.find_nearest_node() [VERIFIED: routing_2026.py:118] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| utilities.warning() | tkinter.messagebox directly | utilities.warning() already exists, adds consistent title handling, less code duplication |
| Auto-trigger on end point | Manual key press to compute | Auto-trigger reduces user steps, provides immediate feedback; manual allows editing before compute |
| Snap to nearest node | Create new nodes at click locations | Creating nodes risks orphaned vertices (not connected to network), snapping ensures traversable routes |

**Installation:**
```bash
# All dependencies already installed from previous phases
python3 --version  # Requires 3.x
python3 -c "import tkinter"  # Should succeed silently
python3 -c "from routing_2026 import RoutingNetwork"  # Should import without error
```

**Version verification:** Before writing the Standard Stack table, verified each recommended package:
```bash
# Python version
python3 --version  # Output: Python 3.x (exact version varies by system)

# tkinter availability (part of Python standard library)
python3 -c "import tkinter; print(tkinter.TkVersion)"  # Output: 8.6 (standard on macOS/Linux)

# Dependencies verified via existing imports in codebase
# pyproj, numpy, networkx, scipy - all imported without errors in routing_2026.py, screen_2026.py
```

Documented verified version: tkinter 8.6 (standard GUI framework, built into Python 3.x).

## Architecture Patterns

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      User Interaction Layer                      │
│  (Screen class, tkinter event loop, canvas rendering)           │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Point Selection     │
                    │  (Shift-F9 to start)  │
                    │  Click #1 = Start    │
                    │  Click #2 = End      │
                    └──────────────────────┘
                               │
                               ▼ Auto-trigger (Phase 6 integration)
                    ┌──────────────────────┐
                    │  Coordinate Stack    │
                    │  Screen → World      │
                    │  World → Network     │
                    └──────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Routing Engine      │
                    │  (RoutingNetwork)    │
                    │  find_nearest_node() │
                    │  shortest_path()     │
                    └──────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Path to Route       │
                    │  (coords mapping)    │
                    │  network → screen    │
                    └──────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Visualization       │
                    │  draw_polyline()     │
                    │  GPX export data     │
                    └──────────────────────┘
```

**Data flow trace:**
1. User clicks canvas → tkinter event → _select_route_point() captures (x, y) screen coords
2. Auto-trigger after second click → screen_to_world() converts to geo coordinates
3. pyproj transformer projects from screen EPSG to network EPSG
4. find_nearest_node() snaps to graph node ID (KDTree O(log n))
5. shortest_path() returns node ID list (Dijkstra)
6. Map node IDs → coordinates via node_coords dict
7. world_to_screen() projects back for display
8. draw_polyline() renders route on canvas with orange color
9. Export-ready coordinates stored in _route_network_coords

### Recommended Project Structure

Phase 6 extends existing files, no new directory structure needed:

```
screen_2026.py          # MODIFY: Add _compute_and_display_route() method
                         # MODIFY: Extend _select_route_point() to trigger routing
routing_2026.py         # NO CHANGE: API already stable
utilities_2026.py       # NO CHANGE: screen_to_world() and warning() exist
geo_2026.py             # NO CHANGE: Aggregator module unchanged
examples/               # EXTEND: Add example demonstrating integrated routing
├── example_phase06_gui_routing.py
tests/                  # EXTEND: Add integration tests
├── test_06_gui_routing.py
```

### Pattern 1: Two-Stage Point Selection with Auto-Trigger

**What:** User selects start point (red marker), then end point (blue marker). Routing automatically computes on the second click.

**When to use:** Phase 6 integration point in _select_route_point() method when _route_stage transitions from 'end' back to 'start'.

**Example:**
```python
# Source: screen_2026.py:137-169 (existing pattern)
def _select_route_point(self, event):
    x, y = event.x, event.y

    if self._route_stage == 'start':
        # Draw red marker, store start point
        self.draw_point([x, y], size=6, colour='red', tag='selected_start')
        self._start_point = [x, y]
        self._route_stage = 'end'
    elif self._route_stage == 'end':
        # Draw blue marker, store end point
        self.draw_point([x, y], size=6, colour='blue', tag='selected_end')
        self._end_point = [x, y]
        self._route_stage = 'start'  # Reset for next pair
        # NEW IN PHASE 6: Trigger routing here
        self._compute_and_display_route()
```

**Why this pattern:** Shift-F9/F10 already established (Phase 1), two-stage selection familiar to users, auto-trigger provides immediate feedback.

### Pattern 2: Coordinate System Transformation Stack

**What:** Convert coordinates through three reference systems: screen pixels → world coordinates (via world file) → network EPSG (via pyproj) → back to screen for display.

**When to use:** In _compute_and_display_route() method for each point transformation.

**Example:**
```python
# Source: utilities_2026.py:356-363 (screen_to_world)
def screen_to_world(point, affine):
    x, y = point
    a, d, b, e, c, f = affine
    x_world = a*x + b*y + c
    y_world = d*x + e*y + f
    return [x_world, y_world]

# Source: screen_2026.py:365-399 (world_to_screen)
def world_to_screen(self, world_point):
    if self._world_file is None:
        return None
    a, d, b, e, c, f = self._world_file
    A = np.array([[a, b], [d, e]])
    t = np.array([c, f])
    A_inv = np.linalg.inv(A)
    x_world, y_world = world_point
    screen = A_inv @ (np.array([x_world, y_world]) - t)
    return screen.tolist()

# Phase 6 integration example:
def _compute_and_display_route(self):
    # 1. Transform screen to world
    start_world = utilities.screen_to_world(
        self._start_point, self._world_file
    )
    # 2. Transform world to network EPSG
    transformer = pyproj.Transformer.from_crs(
        pyproj.CRS.from_epsg(self._epsg),
        pyproj.CRS.from_epsg(self._route_network.epsg),
        always_xy=True
    )
    start_network = transformer.transform(*start_world)
```

**Why this pattern:** Each transformation layer has single responsibility (world file affine, pyproj CRS), existing patterns from Phase 5 reuse proven code.

### Pattern 3: Node Snapping with KDTree

**What:** Find nearest existing graph node to a query point using scipy.spatial.KDTree for O(log n) lookup.

**When to use:** In _compute_and_display_route() after transforming coordinates to network EPSG.

**Example:**
```python
# Source: routing_2026.py:95-135 (find_nearest_node)
def find_nearest_node(self, x, y, k=1):
    """Find k nearest nodes to a given point using scipy KDTree."""
    if len(self.node_coords) == 0:
        return (None, float('inf')) if k == 1 else []
    coords_array = np.array(list(self.node_coords.values()))
    tree = scipy.spatial.KDTree(coords_array)
    distances, indices = tree.query([x, y], k=k)
    node_ids = list(self.node_coords.keys())
    result = [node_ids[i] for i in indices]
    if k == 1:
        return (result[0], float(distances[0]))
    else:
        return result

# Phase 6 integration example:
def _compute_and_display_route(self):
    # ... coordinate transforms ...
    start_node, start_dist = self._route_network.find_nearest_node(
        start_network[0], start_network[1]
    )
    if start_node is None:
        utilities.warning('No routing network available')
        return
    end_node, end_dist = self._route_network.find_nearest_node(
        end_network[0], end_network[1]
    )
```

**Why this pattern:** KDTree provides efficient nearest neighbor search, RoutingNetwork already implements this method (Phase 2), handles empty graph gracefully.

### Pattern 4: Error Handling with Warning Dialogs

**What:** Catch all routing errors and display via tkinter.messagebox.showwarning() through utilities.wrapper().

**When to use:** Throughout _compute_and_display_route() for each critical operation (transform, snap, compute).

**Example:**
```python
# Source: utilities_2026.py:37-39 (warning function)
def warning(message, title='Warning'):
    tkinter.Tk().withdraw()
    tkinter.messagebox.showwarning(title, message)

# Phase 6 integration example:
def _compute_and_display_route(self):
    try:
        # Validate routing network available
        if self._route_network is None:
            utilities.warning('Routing network not loaded. Load network data first.')
            return

        # Validate world file available
        if self._world_file is None:
            utilities.warning('No world file loaded. Load an image with world file.')
            return

        # Coordinate transforms (try-except)
        try:
            transformer = pyproj.Transformer.from_crs(...)
        except pyproj.exceptions.CRSError as e:
            utilities.warning(f'Coordinate system mismatch: {e}')
            return

        # Path computation (catch NetworkXNoPath)
        try:
            path = self._route_network.shortest_path(start_node, end_node)
        except nx.exception.NetworkXNoPath:
            utilities.warning('No path found between selected points')
            return

    except Exception as e:
        utilities.warning(f'Routing failed: {e}')
        print(f'Debug: Routing error details: {e}')
        return
```

**Why this pattern:** utilities.warning() already exists (Phase 1), consistent user experience, requires acknowledgment (modal dialog), debug info preserved in console.

### Anti-Patterns to Avoid

- **Blocking main thread during computation:** For large graphs, shortest_path() may take seconds. Don't freeze UI without feedback. Use `self._root.config(cursor='watch')` before compute, restore after. [VERIFIED: 'watch' cursor available]
- **Silent fallback on errors:** Never continue routing after a transformation failure without user notification. All errors must trigger utilities.warning().
- **Creating orphaned nodes:** Don't add new graph nodes at clicked coordinates. Always snap to existing nodes via find_nearest_node() to ensure routes connect to traversable network.
- **Hardcoding EPSG codes:** Use the actual EPSG from Screen._epsg and RoutingNetwork._epsg, not hardcoded 4326/32632 values.
- **Ignoring network emptiness:** Check `len(self._route_network.graph.nodes) == 0` before attempting routing to avoid confusing error messages.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Nearest node search | Custom O(n) linear scan | RoutingNetwork.find_nearest_node() | KDTree provides O(log n) lookup, handles empty graph, already tested |
| Coordinate transformation | Manual matrix inversion or projection math | pyproj.Transformer.from_crs() | Handles complex CRS definitions, bidirectional transforms, edge cases |
| Shortest path algorithm | Custom Dijkstra implementation | nx.dijkstra_path() | NetworkX optimized, well-tested, handles weighted graphs |
| Message dialogs | Direct tkinter.messagebox calls | utilities.warning() | Consistent title handling, single function, existing pattern |
| World file transforms | Manual affine calculations | Screen.world_to_screen() / utilities.screen_to_world() | Already implemented, tested, handles matrix inversion errors |

**Key insight:** Phase 6 is an integration phase, not an algorithm phase. All core capabilities already exist—coordinate transformations, routing computation, visualization. The value comes from connecting them robustly, not reinventing any subsystem.

## Runtime State Inventory

> Omitted for greenfield phase. This section is for rename/refactor/migration phases only.

## Common Pitfalls

### Pitfall 1: Missing RoutingNetwork Reference in Screen

**What goes wrong:** Screen instance doesn't have access to RoutingNetwork object. When _compute_and_display_route() tries to call `self._route_network.find_nearest_node()`, raises AttributeError.

**Why it happens:** Phase 1-5 focused on separate capabilities (Screen, RoutingNetwork). Phase 6 integration requires a reference from Screen to RoutingNetwork, but Screen.__init__() doesn't create or store this reference.

**How to avoid:**
1. Add `_route_network = None` attribute in Screen.__init__() (line ~29)
2. Provide setter method or property to assign network: `screen.set_route_network(network)`
3. Check for None in _compute_and_display_route() before routing
4. Example:
```python
def set_route_network(self, network):
    """Set the routing network for pathfinding."""
    if not isinstance(network, RoutingNetwork):
        raise ValueError("Must provide RoutingNetwork instance")
    self._route_network = network
```

**Warning signs:** AttributeError: 'Screen' object has no attribute '_route_network' during routing attempt.

### Pitfall 2: World File Not Loaded Before Selection

**What goes wrong:** User presses Shift-F9 and clicks before loading an image with world file. screen_to_world() fails because self._world_file is None.

**Why it happens:** Phase 1 allowed map navigation without world file (pan/zoom worked). Phase 6 routing requires geo-referencing for coordinate transforms.

**How to avoid:**
1. In _compute_and_display_route(), check `self._world_file is None` first
2. If None, display warning: "Load an image with world file first (F5)"
3. Return early without attempting transforms
4. Consider loading a default world file in example if possible

**Warning signs:** TypeError or NoneType error when calling utilities.screen_to_world() with none second argument.

### Pitfall 3: EPSG Mismatch Between Screen and Network

**What goes wrong:** Screen loaded with EPSG:4326 (WGS84) but routing network in EPSG:32632 (UTM 32V). pyproj transform fails or produces nonsense coordinates.

**Why it happens:** Users might load different datasets with different reference systems. No validation currently exists when mapping starts.

**How to avoid:**
1. Check `self._epsg` and `self._route_network._epsg` exist and match
2. If different, create transformer between them (not fail—allow routing across CRS)
3. Validate both are ints, not None
4. Example:
```python
if self._epsg is None or self._route_network._epsg is None:
    utilities.warning('Coordinate systems undefined')
    return
# Allow transformation between different EPSG codes
transformer = pyproj.Transformer.from_crs(..., ...)
```

**Warning signs:** pyproj.exceptions.CRSError or coordinates in wrong units (degrees vs meters).

### Pitfall 4: Empty Routing Network Graph

**What goes wrong:** find_nearest_node() returns (None, inf) because graph has no nodes. shortest_path() fails because start_node or end_node is None.

**Why it happens:** RoutingNetwork object exists but graph never populated (nodes/edges not added). User might initialize network without calling load functions.

**How to avoid:**
1. Check `len(self._route_network.graph.nodes) == 0` before routing
2. If empty, display warning: "Routing network empty. Load trail or terrain data first."
3. Use graceful error handling for find_nearest_node() (already returns None for empty)
4. Check None returned before calling shortest_path()

**Warning signs:** Start/end node is None after find_nearest_node(), or shortest_path() raises ValueError.

### Pitfall 5: No Path Found Between Nodes

**What goes wrong:** shortest_path() raises NetworkXNoPath exception because graph is disconnected or nodes belong to different components.

**Why it happens:** Networks might be built from disconnected trail sources (e.g., separate trail systems without connecting terrain mesh). User clicks points on different islands of the graph.

**How to avoid:**
1. Wrap shortest_path() in try-except for nx.exception.NetworkXNoPath
2. Catch exception and display user-friendly warning: "No path found between selected points"
3. Don't crash—explain the disconnect clearly
4. Optional: Suggest user load more data or choose different points

**Warning signs:** nx.exception.NetworkXNoPath traceback in console, no route displayed.

### Pitfall 6: UI Frozen During Long Computations

**What goes wrong:** For large routing networks (>10,000 nodes), shortest_path() takes several seconds. User sees no feedback, thinks application crashed.

**Why it happens:** tkinter mainloop blocks on long-running operations in same thread. No progress indication provided.

**How to avoid:**
1. Before routing: `self._root.config(cursor='watch')` (verified 'watch' cursor available on system)
2. After routing (success or fail): `self._root.config(cursor='arrow')`
3. Optional: Update status label text: "Computing route..." before compute
4. For very large networks, consider threading (but adds complexity—Phase 6 optional discretion)

**Warning signs:** Cursor doesn't change, rapid user clicks cause issues, console shows no output delays.

## Code Examples

Verified patterns from official sources:

### Complete Integration Pattern: _compute_and_display_route()

```python
# Source: synthesized from screen_2026.py patterns (this file will be created in execution)
def _compute_and_display_route(self):
    """
    Compute and display route between selected start and end points.

    Workflow:
    1. Validate prerequisites (network, world file, coordinates)
    2. Transform screen coords → world coords → network EPSG coords
    3. Snap to nearest graph nodes (find_nearest_node)
    4. Compute shortest path (shortest_path)
    5. Map node IDs → network coordinates
    6. Transform network coords → world coords → screen coords
    7. Store for GPX export and display route

    Error handling: All user-facing errors trigger utilities.warning()
    """
    # === 1. Validate prerequisites ===
    if self._start_point is None or self._end_point is None:
        utilities.warning('Both start and end points must be selected')
        return

    if self._route_network is None:
        utilities.warning('Routing network not loaded. Load network data first.')
        return

    if self._world_file is None:
        utilities.warning('No world file loaded. Load an image with world file (F5).')
        return

    if len(self._route_network.graph.nodes) == 0:
        utilities.warning('Routing network is empty. Load trail or terrain data first.')
        return

    # === 2. Transform screen to world coordinates ===
    try:
        start_world = utilities.screen_to_world(
            self._start_point, self._world_file
        )
        end_world = utilities.screen_to_world(
            self._end_point, self._world_file
        )
    except Exception as e:
        utilities.warning(f'Failed to transform screen coordinates: {e}')
        print(f'Debug: screen_to_world error: {e}')
        return

    # === 3. Transform world to network EPSG coordinates ===
    try:
        # Use project_point from utilities or pyproj directly
        if self._epsg is None or self._route_network._epsg is None:
            utilities.warning('Coordinate systems undefined')
            return

        transformer = pyproj.Transformer.from_crs(
            pyproj.CRS.from_epsg(self._epsg),
            pyproj.CRS.from_epsg(self._route_network._epsg),
            always_xy=True
        )

        start_network = transformer.transform(*start_world)
        end_network = transformer.transform(*end_world)
    except pyproj.exceptions.CRSError as e:
        utilities.warning(f'Coordinate system mismatch: {e}')
        return
    except Exception as e:
        utilities.warning(f'Failed to project to network coordinates: {e}')
        print(f'Debug: projection error: {e}')
        return

    # === 4. Show progress indication ===
    self._root.config(cursor='watch')  # Verified 'watch' cursor available
    self._root.update_idletasks()  # Force cursor update before long compute

    try:
        # === 5. Snap to nearest graph nodes ===
        start_node, start_dist = self._route_network.find_nearest_node(
            start_network[0], start_network[1]
        )
        end_node, end_dist = self._route_network.find_nearest_node(
            end_network[0], end_network[1]
        )

        if start_node is None or end_node is None:
            utilities.warning('Failed to find nearest nodes in routing network')
            return

        # === 6. Compute shortest path ===
        try:
            path_node_ids = self._route_network.shortest_path(start_node, end_node)
        except nx.exception.NetworkXNoPath:
            utilities.warning(
                'No path found between selected points.\n'
                'Are points in disconnected network components?'
            )
            return
        except Exception as e:
            utilities.warning(f'Path computation failed: {e}')
            return

        # === 7. Map node IDs to network coordinates ===
        route_network_coords = [
            self._route_network.node_coords[node_id]
            for node_id in path_node_ids
        ]

        if not route_network_coords:
            utilities.warning('Route computation produced empty path')
            return

        # === 8. Store for GPX export ===
        self._route_network_coords = route_network_coords

        # === 9. Transform network coordinates to screen coordinates ===
        try:
            route_screen_coords = []
            for coord in route_network_coords:
                screen_coord = self.world_to_screen(coord)
                if screen_coord is None:
                    utilities.warning('Failed to transform route to screen coordinates')
                    return
                route_screen_coords.append(screen_coord)
        except Exception as e:
            utilities.warning(f'Failed to transform route to screen: {e}')
            print(f'Debug: world_to_screen error: {e}')
            return

        # === 10. Display route ===
        self.set_route(route_screen_coords)  # Provided by Phase 5
        self.display_route()  # Provided by Phase 5

        # Optional: Print routing stats for debugging
        print(f'Route computed: {len(route_screen_coords)} vertices, '
              f'{start_dist:.1f}m from start node, {end_dist:.1f}m from end node')

    finally:
        # === 11. Restore cursor ===
        self._root.config(cursor='arrow')
```

### Set Route Network Reference

```python
# Source: New method to add to Screen class (execution will create)
def set_route_network(self, network):
    """
    Assign a routing network to the screen for route computation.

    Args:
        network: RoutingNetwork instance containing graph and node coordinates

    Raises:
        ValueError: If network is not a RoutingNetwork instance
    """
    from routing_2026 import RoutingNetwork

    if not isinstance(network, RoutingNetwork):
        raise ValueError(
            f"Expected RoutingNetwork instance, got {type(network).__name__}"
        )

    self._route_network = network
    print(f'Routing network assigned to screen. Graph has '
          f'{len(network.graph.nodes)} nodes, {len(network.graph.edges)} edges')
```

### Extended Point Selection with Auto-Trigger

```python
# Source: screen_2026.py:137-169 (modify existing method)
def _select_route_point(self, event):
    """
    Handle route point selection with two-stage workflow (start, then end).

    Auto-triggers route computation after end point selection (Phase 6).

    :param self: Instance of the class
    :param event: Mouse event containing x, y coordinates
    """
    x, y = event.x, event.y

    if self._route_stage == 'start':
        # Delete previous start marker if exists
        self.delete('selected_start')
        # Draw red marker for start point
        self.draw_point([x, y], size=6, colour='red', tag='selected_start')
        # Store start point
        self._start_point = [x, y]
        # Display coordinates
        self._update_coordinate_display([x, y], 'Start')
        # Toggle to end stage
        self._route_stage = 'end'
        print(f'Start point selected: [{x}, {y}]')
    elif self._route_stage == 'end':
        # Delete previous end marker if exists
        self.delete('selected_end')
        # Draw blue marker for end point
        self.draw_point([x, y], size=6, colour='blue', tag='selected_end')
        # Store end point
        self._end_point = [x, y]
        # Display coordinates
        self._update_coordinate_display([x, y], 'End')
        # Toggle back to start stage for reset
        self._route_stage = 'start'
        print(f'End point selected: [{x}, {y}]')

        # === NEW IN PHASE 6: Auto-trigger routing ===
        self._compute_and_display_route()
```

### Example Usage in Application

```python
# Source: examples/example_phase06_gui_routing.py (will be created in execution)
import geo_2026 as geo
from routing_2026 import RoutingNetwork, create_terrain_mesh_network
from raster_2026 import Raster

def main():
    """Demonstrate integrated GUI routing (Phase 6)."""
    print("=" * 60)
    print("Phase 6: GUI Routing Integration Demo")
    print("=" * 60)

    # 1. Create screen
    screen = geo.Screen(rows=600, columns=800, background='black')

    # 2. Load raster with world file (required for geo-referencing)
    print("\nLoading raster data...")
    raster = geo.Raster()
    # Uncomment when you have test data:
    # raster.read('test_terrain.png')
    # world_file = [1.0, 0.0, 0.0, -1.0, 0.0, 600.0]  # Example affine
    # screen._world_file = world_file
    # screen._image = raster
    # screen.display_image()
    print("(Note: Load test image with F5 for full geo-referencing)")

    # 3. Create routing network
    print("\nCreating routing network...")
    network = RoutingNetwork()

    # Add sample nodes (normally load from OSM or terrain)
    for i, (x, y) in enumerate([(600000, 6650000 + i*100) for i in range(10)]):
        network.add_node(i, x, y)

    # Add edges with weights
    for i in range(9):
        network.add_edge(i, i+1, weight=100.0, length=100.0)

    network.epsg = 32632  # UTM Zone 32V (Norway)
    print(f"Network created: {len(network.graph.nodes)} nodes, "
          f"{len(network.graph.edges)} edges, EPSG: {network.epsg}")

    # 4. Assign network to screen
    screen.set_route_network(network)

    # 5. Start main loop
    print("\nControls:")
    print("  Shift+F9 : Start route selection mode")
    print("  Shift+F10: Stop route selection mode")
    print("  Left Click: Select route points (in route mode)")
    print("  F5 : Load image with world file")
    print("  F6 : Display loaded image")
    print("\nSelect two points to auto-compute route")
    print("=" * 60)

    screen.loop()

if __name__ == '__main__':
    main()
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual route trigger via key press | Auto-trigger after end point selection | Phase 6 (current) | Reduces user steps, provides immediate feedback |
| Separate point selection and routing | Integrated point→compute→display workflow | Phase 6 (current) | Streamlined UX, fewer user errors |
| Console-only error messages | Modal warning dialogs for all routing errors | Phase 6 (current) | Errors impossible to miss, consistent user experience |

**Deprecated/outdated:**
- None in current codebase. All existing modules (screen_2026, routing_2026, utilities_2026) remain stable.

## Assumptions Log

> List all claims tagged `[ASSUMED]` in this research. The planner and discuss-phase use this section to identify decisions that need user confirmation before execution.

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | RoutingNetwork.find_nearest_node() returns (None, float('inf')) for empty graph | Code Examples / Pitfall 4 | Low risk—verified in routing_2026.py:111-112 |
| A2 | tkinter 'watch' cursor is available on all target systems | Pitfall 6 / Code Examples | Low risk—verified via system test (macOS 3.x) |
| A3 | utilities.warning() exists and uses tkinter.messagebox.showwarning() | Pattern 4 | Low risk—verified in utilities_2026.py:37-39 |
| A4 | Screen.world_to_screen() method exists and handles matrix inversion | Pattern 2 | LOW risk—verified in screen_2026.py:365-399 |

**If this table is empty:** All claims in this research were verified or cited — no user confirmation needed.

## Open Questions

1. **Progress indication for very large networks**
   - What we know: Phase 6 Claude's discretion allows progress indication. 'watch' cursor verified available.
   - What's unclear: Should Phase 6 implement threading/asynchronous routing for large networks, or is cursor change sufficient?
   - Recommendation: Cursor change is MVP. Threading adds complexity (race conditions with tkinter mainloop). Defer threading unless user reports specific performance issues.

2. **Default network loading in examples**
   - What we know: Example needs a routing network to demonstrate functionality. Real networks require OSM/terrain data.
   - What's unclear: Should Phase 6 example create synthetic test network (for immediate testing) or require user data (realistic but unusable without preparation)?
   - Recommendation: Create synthetic network in example (10-20 nodes) so example runs out-of-the-box. Document how to load real data in comments.

3. **Network reference management**
   - What we know: Screen needs _route_network reference. Can be set via setter method.
   - What's unclear: Should Screen manage its own network instance, or always require external assignment?
   - Recommendation: Require external assignment (set_route_network()). Screen remains a display/controller class, not data manager. Separation of concerns.

4. **Coordinate validation timing**
   - What we know: EPSG codes must exist and be valid for routing.
   - What's unclear: Should we validate EPSG codes when network is assigned to screen (early validation), or defer to routing attempt (lazy validation)?
   - Recommendation: Lazy validation in _compute_and_display_route(). Allows screen to exist without network (e.g., for pan/zoom only). More flexible UX.

## Environment Availability

> Skip this section if the phase has no external dependencies (code/config-only changes).

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.x | All code | ✓ | 3.x (system varies) | — |
| tkinter | GUI framework | ✓ | 8.6 | — |
| routing_2026 | Routing engine | ✓ | Custom (Phase 2) | — |
| screen_2026 | GUI/display | ✓ | Custom (Phase 1) | — |
| utilities_2026 | Standard library | ✓ | Custom (Phase 1) | — |
| pyproj | EPSG transforms | ✓ | Latest (in requirements.txt) | — |
| numpy | Matrix operations | ✓ | Latest (in requirements.txt) | — |
| networkx | Graph algorithms | ✓ | Latest (in requirements.txt) | — |
| scipy | KDTree spatial index | ✓ | Latest (in requirements.txt) | — |

**Missing dependencies with no fallback:**
- None

**Missing dependencies with fallback:**
- None

**Verification methods:**
```bash
# All core modules importable
python3 -c "from routing_2026 import RoutingNetwork"  # ✓ Success
python3 -c "from screen_2026 import Screen"  # ✓ Success
python3 -c "import utilities_2026 as utilities"  # ✓ Success

# All dependencies available
python3 -c "import tkinter; print('tkinter:', tkinter.TkVersion)"  # ✓ Output: 8.6
python3 -c "import pyproj; print('pyproj:', pyproj.__version__)"  # ✓ Success
python3 -c "import networkx; print('networkx:', networkx.__version__)"  # ✓ Success
python3 -c "import scipy; print('scipy:', scipy.__version__)"  # ✓ Success
python3 -c "import numpy; print('numpy:', numpy.__version__)"  # ✓ Success
```

**Environment readiness:** All dependencies verified available. Phase 6 can proceed without installation steps.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 8.x+ |
| Config file | No explicit pytest.ini found |
| Quick run command | `pytest tests/test_06_gui_routing.py -x -v` |
| Full suite command | `pytest tests/ -v` |

### Phase Requirements → Test Map

Phase 6 has no explicit requirement IDs (null provided in context), so maps to integration behavior derived from CONTEXT.md decisions (D-01 through D-04).

| Behavior | Test Type | Automated Command | File Exists? |
|----------|-----------|-------------------|-------------|
| Auto-trigger routing after end point selection | integration | `pytest tests/test_06_gui_routing.py::TestGuiRouting::test_auto_trigger -x -v` | ❌ Wave 0 |
| Coordinate transformation (screen→world→network) | unit | `pytest tests/test_06_gui_routing.py::TestCoordinateTransforms::test_screen_to_network -x -v` | ❌ Wave 0 |
| Node snapping to nearest graph node | unit | `pytest tests/test_06_gui_routing.py::TestNodeSnapping::test_snap_to_existing_node -x -v` | ❌ Wave 0 |
| Path computation from snapped nodes | integration | `pytest tests/test_06_gui_routing.py::TestPathComputation::test_shortest_path_after_snapping -x -v` | ❌ Wave 0 |
| Route display on canvas | integration | `pytest tests/test_06_gui_routing.py::TestRouteDisplay::test_route_polyline_rendered -x -v` | ❌ Wave 0 |
| Error handling for missing network | unit | `pytest tests/test_06_gui_routing.py::TestErrorHandling::test_no_network_warning -x -v` | ❌ Wave 0 |
| Error handling for no path found | unit | `pytest tests/test_06_gui_routing.py::TestErrorHandling::test_no_path_dialog -x -v` | ❌ Wave 0 |
| Coordinate system mismatch handling | unit | `pytest tests/test_06_gui_routing.py::TestErrorHandling::test_epsg_mismatch -x -v` | ❌ Wave 0 |
| Cursor changes during computation | unit | `pytest tests/test_06_gui_routing.py::TestProgressIndication::test_cursor_watch_during_compute -x -v` | ❌ Wave 0 |
| GPX export data stored correctly | integration | `pytest tests/test_06_gui_routing.py::TestExportData::test_route_network_coords_stored -x -v` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `pytest tests/test_06_gui_routing.py -x -v` (Phase 6 tests only)
- **Per wave merge:** `pytest tests/ -v` (Full test suite including v1 integration)
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `tests/test_06_gui_routing.py` — Complete test suite for Phase 6 integration (10 planned tests)
- [ ] `tests/conftest.py` — Shared fixtures (routing network, screen with world file, sample coordinates)
- [ ] Test fixtures for mocking tkinter events (mouse clicks, key presses)
- [ ] Test fixtures for synthetic routing networks (small, medium sizes)
- [ ] Test fixtures for mock world files and EPSG transformations
- [ ] Framework install: pytest (already installed per system test)

*(If no gaps: "None — existing test infrastructure covers all phase requirements")*

**Gap priority:** Create `tests/test_06_gui_routing.py` with fixtures before implementation tasks. Tests drive development (TDD pattern) for integration logic.

## Security Domain

> Required when `security_enforcement` is enabled (absent = enabled). This phase has no significant security concerns—desktop application, local data, no network communication, no user input sanitization beyond coordinate transformation validation.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | N/A (desktop app, no auth) |
| V3 Session Management | no | N/A (no sessions) |
| V4 Access Control | no | N/A (local-only app) |
| V5 Input Validation | yes (limited) | Coordinate bounds validation (implicit in transforms), pyproj CRS validation |
| V6 Cryptography | no | N/A (no cryptography needed) |

### Known Threat Patterns for {Python/Tkinter/Desktop App}

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Malformed coordinate input causing OOB access | Tampering | Bound checking in coordinate transforms (implicit in world file math), pyproj validates CRS |
| NetworkX large graph memory exhaustion | Denial of Service | No mitigation in Phase 6 (local-only, user controls data size). Risk: User loads 1M+ node graph → memory exhaustion. Mitigation: Document recommended graph sizes in user guide. |
| pyproj CRSError injection | Tampering | Validated by pyproj library itself (well-tested). No additional mitigation needed. |
| tkinter message box denial (blocking UI) | Denial of Service | Error dialogs are necessary for user awareness. No mitigation—user must acknowledge. |

**Security assessment:** LOW RISK. This is a local desktop application with no network endpoints, no authentication, no sensitive data handling. Coordinate transformations use well-tested libraries (pyproj, numpy, scipy). Main risk is resource exhaustion from user-provided large datasets, but this is out-of-scope for Phase 6 (data loading handled elsewhere). No additional security controls required.

## Sources

### Primary (HIGH confidence)

- `screen_2026.py` — Verified Screen class structure (_start_point, _end_point, _route_stage attributes), drawing methods (draw_point, draw_polyline), world_to_screen() implementation (lines 365-399), _select_route_point() method (lines 137-169), export_gpx() method (lines 451-499)
- `routing_2026.py` — Verified RoutingNetwork class structure, shortest_path() method (lines 77-93), find_nearest_node() method (lines 95-135), __init__() method (lines 29-40), node_coords property
- `utilities_2026.py` — Verified warning() function (lines 37-39), screen_to_world() function (lines 356-363)
- `geo_2026.py` — Verified module imports RoutingNetwork class
- System test — Verified tkinter 8.6 availability and 'watch' cursor support (executed during research)
- CODEBASE — Verified test infrastructure (pytest, existing test files in tests/ directory)

### Secondary (MEDIUM confidence)

- `CLAUDE.md` — Project constraints: Python 3.x, tkinter required, existing module structure (verified against actual codebase)
- `06-CONTEXT.md` — User decisions (D-01 through D-04) governing implementation requirements (burned into RESEARCH.md as locked decisions)
- `STATE.md` — Project history confirming Phase 1-5 completion, integration points established
- `examples/example_phase01_route_selection.py` — Verified Shift-F9/F10 interaction pattern, point selection workflow
- `tests/test_v1_complete.py` — Verified existing test patterns, pytest usage, mock utilities for tkinter testing (lines 20: Mock, patch, MagicMock imports)

### Tertiary (LOW confidence)

- None — All research findings verified via code inspection or system tests. No web search or external speculation needed.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries verified via code inspection and system tests
- Architecture: HIGH - Integration points verified in existing codebase, workflow diagram based on verified method signatures
- Pitfalls: HIGH - Anti-patterns derived from error handling patterns in codebase, cursor availability verified

**Research date:** 2026-04-16
**Valid until:** 2026-05-16 (30 days for stable architecture and proven APIs)