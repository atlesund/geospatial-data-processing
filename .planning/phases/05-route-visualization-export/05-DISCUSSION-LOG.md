# Phase 5: Route Visualization & Export - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-16
**Phase:** 05-route-visualization-export
**Areas discussed:** Route visualization style, Visualization behavior, GPX file format, Export UI flow

---

## Area: Route visualization style

### Question: What color should highlight the route on the map?

| Option | Description | Selected |
|--------|-------------|----------|
| Bright distinctive color | Red, yellow, or orange - high contrast against map, easy to see | ✓ |
| Nature-inspired color | Green or blue - blends with outdoor theme, feels more natural/hiking-appropriate | |
| You decide | Claude chooses based on the map's color scheme for best contrast | |

**User's choice:** Bright distinctive color
**Notes:**

### Question: How thick should the route line be?

| Option | Description | Selected |
|--------|-------------|----------|
| Thin line | 1-2 pixels - subtle, doesn't obscure map details | |
| Medium line | 3-4 pixels - clearly visible, standard for route visualization | ✓ |
| Thick line | 5+ pixels - very prominent, easy to spot but may cover map features | |

**User's choice:** Medium line
**Notes:** Matches Screen.draw_polyline() default of 3 pixels for consistency

### Question: Should the route have any styling variations, or keep it simple?

| Option | Description | Selected |
|--------|-------------|----------|
| Point markers | Add markers at key points (start, end, vertices) to highlight route structure | |
| Line pattern | Use dashed or dotted line pattern to distinguish route from other map features | |
| Keep simple | No additional visual elements - keep it simple with just color and width | ✓ |

**User's choice:** Keep simple
**Notes:** Clean, straightforward approach

---

## Area: Visualization behavior

### Clarification: Tkinter window vs. OSM HTML

User clarified: prefers Tkinter window approach over html folium for route visualization.

**User's choice:** Tkinter window (Screen class)
**Notes:** Routes drawn directly in desktop window using screen.draw_polyline() on canvas

### Question: When should the route be displayed in the tkinter window?

| Option | Description | Selected |
|--------|-------------|----------|
| Auto-show | Route displays immediately after routing completes | ✓ |
| Manual show | Route shows when user clicks a 'Show route' button | |
| Auto + toggle | Route displays immediately, but user can toggle show/hide with a button | |

**User's choice:** Auto-show
**Notes:** No user action required to see the result

### Question: What should happen when the user calculates a new route with different points?

| Option | Description | Selected |
|--------|-------------|----------|
| Replace old route | Replace the old route display when a new route is calculated | |
| Accumulate routes | Keep previous routes visible alongside new routes | |
| Clear then recalc | Clear old routes before computing new route, then display | ✓ |

**User's choice:** Clear then recalc
**Notes:** Clean slate each time routing is triggered

---

## Area: GPX file format

### Question: What should the exported GPX file contain?

| Option | Description | Selected |
|--------|-------------|----------|
| Track only | GPX with <trk> track containing just the route coordinates | ✓ |
| Track + waypoints | GPX with <trk> track plus waypoint markers for start/end points | |
| Full route with metadata | GPX with <rte> route element plus course details (name, description, distance) | |

**User's choice:** Track only
**Notes:** Minimal format, works with most GPS devices

---

## Area: Export UI flow

### Question: How should users trigger the GPX export?

| Option | Description | Selected |
|--------|-------------|----------|
| On-screen button | Add a button in the tkinter window labeled 'Export GPX' | |
| Keyboard shortcut | Use a keyboard shortcut (e.g., E for export or Ctrl+E) | ✓ |
| File dialog | Use a standard file save dialog - user chooses export location and filename | |

**User's choice:** Keyboard shortcut (clarified below)
**Notes:** Fast workflow once learned

### Question: Which keyboard shortcut should export the GPX file?

| Option | Description | Selected |
|--------|-------------|----------|
| Ctrl+E (or Cmd+E) | Standard convention for export operations | |
| Just E | Simpler, no modifier key required | |
| Function key | Follows the existing F9/F12 pattern for screen interaction | ✓ |

**User's choice:** Function key
**Notes:** Follows existing pattern for screen interaction

### Question: Which function key should export the GPX?

| Option | Description | Selected |
|--------|-------------|----------|
| F8 | Pairs nicely with F9/F12 for screen operations | |
| F5 | Follows file save conventions in many applications | ✓ |
| F6 | Another available function key in the F5-F9 range | |

**User's choice:** F5
**Notes:** Follows file save conventions

---

## Claude's Discretion

Areas where user said "you decide" or Claude has flexibility:
- Specific bright color selection (red vs yellow vs orange)
- Whether to add a visual indicator when export succeeds/displays a success message to user
- Error handling for export failures (file write errors, no route computed yet)
- Coordinate system transformation for GPX export (route coordinates in network EPSG may need conversion to WGS84)
- GPX track name generation (auto-generated vs fixed name vs prompt user)

## Deferred Ideas

None — discussion stayed within phase scope