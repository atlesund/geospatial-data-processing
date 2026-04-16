# Phase 6: GUI Routing Integration - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-16
**Phase:** 06-gui-routing-integration-connect-point-selection-with-routing
**Areas discussed:** Routing trigger timing, Coordinate mapping & snapping, Error handling & user feedback

---

## Routing Trigger Timing

| Option | Description | Selected |
|--------|-------------|----------|
| Auto after end point | Compute route immediately after user selects the end point. No extra key press needed but longer routes may feel like the UI is frozen during computation. | ✓ |
| Manual key trigger (F4) | User selects both points, then presses F4 to trigger route computation. Gives user control over when computation starts, follows existing F5/F9/F12 pattern. | |
| Manual key trigger (Enter) | User selects both points, then presses Enter to trigger route computation. More intuitive than F4, simple discovery. | |

**User's choice:** Auto after end point
**Notes:** Keeps workflow simple — user clicks twice and gets immediate route feedback. No extra interaction needed.

---

## Coordinate Mapping & Snapping - Part 1: Coordinate Flow

| Option | Description | Selected |
|--------|-------------|----------|
| Screen → WGS84 → Network EPSG | Transform screen coordinates to WGS84 first (decimal degrees), then to the routing network's EPSG (e.g., UTM 32V). This follows the flow from Phase 1 and adds one extra transformation step. | |
| Screen → World → Network EPSG | Use the Screen's existing world file transformation to convert screen to world coordinates, then project to the routing network's EPSG if needed. Direct path using Screen's existing capabilities. | ✓ |

**User's choice:** Screen → World → Network EPSG
**Notes:** Leverages existing Screen infrastructure via utilities.screen_to_world().

---

## Coordinate Mapping & Snapping - Part 2: Node Snapping

| Option | Description | Selected |
|--------|-------------|----------|
| Snap to nearest graph node | Use RoutingNetwork.find_nearest_node() to find the nearest graph node within a reasonable distance radius. Makes routes realistic (sticks to actual trails/mesh edges) but may snap to unintended nodes if network is sparse. | ✓ |
| Create nodes at exact clicked locations | Create new graph nodes exactly at the clicked coordinates by interpolating onto the nearest edge or adding isolated nodes. Most precise but adds computational overhead and may create isolated nodes unreachable from the main graph. | |
| Snap with distance threshold | Snap to nearest node but enforce a maximum distance threshold (e.g., 500m from click to graph). If no node within threshold, prompt user to click closer or zoom in to a more mapped area. | |

**User's choice:** Snap to nearest graph node
**Notes:** Simple, removes complexity of thresholding and node creation, ensures routes connect to traversable network.

---

## Error Handling & User Feedback - Part 1: No Path Found

| Option | Description | Selected |
|--------|-------------|----------|
| Message dialog with explanation | Show a tkinter.messagebox.showinfo() or showwarning() dialog explaining why no path exists (e.g., 'No path found between these points. They may be in disconnected network regions.'). User dismisses to continue. | ✓ |
| Console log + flashing marker | Print explanation to console and flash the start/end point markers to indicate routing failure. No dialog打断s the user. Less intrusive but the error may be noticed only if user is watching the console. | |
| Status text in window | Display routing status in a text label or window title ('Routing failed: no path found between points'). Visible in the GUI without a modal dialog that requires dismissal. | |

**User's choice:** Message dialog with explanation
**Notes:** Clear feedback that requires user acknowledgment, won't be missed like console output.

---

## Error Handling & User Feedback - Part 2: Other Error Types

| Option | Description | Selected |
|--------|-------------|----------|
| Message dialog for all | Use message dialog for ALL error types (no path, missing network, coordinate mismatch, etc.). Consistent UI interaction pattern for all failures. | ✓ |
| Dialog for blocking, log otherwise | Show dialog for blocking errors (missing network, no path), but print to console for informational issues (coordinate warnings,距离from click to graph). Let user explore without interruption for less critical issues. | |

**User's choice:** Message dialog for all
**Notes:** Consistent, noticeable error handling across all failure types.

---

## Claude's Discretion

None in this phase — user made explicit choices for all discussed areas.

---

## Deferred Ideas

None — discussion stayed within phase scope