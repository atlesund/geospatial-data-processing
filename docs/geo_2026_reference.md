# geo_2026 -- Complete Reference Guide

## The Four Core Modules

The codebase is built around four modules, all imported through `geo_2026.py`:

| Module | Class | Role |
|--------|-------|------|
| `vector_2026.py` | `Vector` | Data layer: stores points/polylines/polygons with attributes. No GUI. |
| `raster_2026.py` | `Raster` | Loads a PNG image and its world file (for georeferencing). No GUI. |
| `screen_2026.py` | `Screen` | Tkinter GUI: canvas, drawing, digitising, and event handling. |
| `utilities_2026.py` | (functions) | Dialogs, validation, coordinate transforms, file I/O, OSM/Folium helpers. |

---

## Built-in Keybindings (always available with Screen)

These are bound automatically the moment you create a `Screen()` instance.

### F5 Family -- Raster Image Management

| Key | Method | What it does |
|-----|--------|--------------|
| **F5** | `_read_image` | Opens a file dialog to select a PNG image. Reads the image and its `.pgw` world file (for georeferencing). Then asks for an EPSG code via a dialog. |
| **Shift-F5** | `_draw_image` | Draws the previously loaded image onto the canvas (anchored at the top-left corner). |
| **Ctrl-F5** | `_image_info` | Prints raster metadata to the terminal (filename, EPSG, world file parameters). |
| **Ctrl-Shift-F5** | `_fit_canvas_to_image` | Resizes the Tkinter window and canvas to match the image dimensions exactly. |

Typical workflow: **F5** (load) → **Shift-F5** (display) → optionally **Ctrl-Shift-F5** (resize window to fit).

### F9/F10 -- Digitising

| Key | Method | What it does |
|-----|--------|--------------|
| **F9** | `_start_digit_points` | Enters digitising mode: binds left-click to place points on the canvas. Changes the cursor to a crosshair. Each click draws a white point and stores the screen (pixel) coordinates in `screen._digits`. |
| **F10** | `_stop_digit_points` | Exits digitising mode: unbinds left-click and restores the default cursor. |

While in digitising mode (between F9 and F10), every left-click places a point.

### F12 -- Export

| Key | Method | What it does |
|-----|--------|--------------|
| **F12** | `_digit_points_to_geojson` | Converts all digitised points from screen (pixel) coordinates to real-world coordinates using the world file affine transformation, then saves them as a GeoJSON file. Requires an image with a world file (F5) and digitised points (F9). |

---

## User-Definable Bindings (public API)

`Screen` exposes four methods for creating custom bindings in scripts:

| Method | Binds on | Use for |
|--------|----------|---------|
| `keyboard_bind(event, function)` | Root window | Key presses (caught regardless of focus) |
| `keyboard_unbind(event)` | Root window | Remove a key binding |
| `mouse_bind(event, function)` | Canvas | Mouse events (only over the drawing area) |
| `mouse_unbind(event)` | Canvas | Remove a mouse binding |

Common events:
- `'1'`, `'2'`, `'3'`, `'R'`, etc. -- single key presses
- `'<Motion>'` -- mouse movement over the canvas
- `'<Button-1>'` -- left-click (already used internally during digitising mode)
- `'<F1>'` through `'<F4>'` -- unused function keys available for custom use

---

## Drawing Methods on Screen

| Method | What it draws |
|--------|---------------|
| `draw_point(point, size=3, colour='white', tag='point')` | A small filled rectangle simulating a point |
| `draw_polyline(polyline, width=3, colour='white', vertices=False, tag='polyline')` | A connected line, optionally with vertex markers |
| `draw_polygon(polygon, width=3, colour='white', vertices=False, stipple=False, boundary=False, tag='polyline')` | A filled polygon with optional stipple pattern and boundary lines |
| `draw_text(point, message, colour='white', tag='text')` | Text label at a position |
| `delete(tag)` | Removes all canvas items with the given tag (e.g., `'point'`, `'highlight'`) |
| `cursor(shape='')` | Changes the canvas cursor (e.g., `'tcross'` for crosshair) |

The **tag** parameter is important -- it lets you selectively delete groups of drawn elements later.

---

## Vector: Data Operations (no GUI required)

`Vector` is purely a data class. Everything works without `Screen`:

### Data Creation

| Method | Purpose |
|--------|---------|
| `random_points(n, x_min, y_min, x_max, y_max)` | Generate n random points in a bounding box |

### Attributes

| Method | Purpose |
|--------|---------|
| `add_field(field_name, default_value)` | Add a new attribute column to all features |
| `add_geometric_fields()` | Auto-add `x`, `y` for points; `length` for polylines; `area`, `perimeter`, `centroid` for polygons |

### Selection & Queries

| Method | Purpose |
|--------|---------|
| `select(expression)` | Attribute query, e.g., `'x > 100 and y < 200'` |
| `select_by_rectangle(rectangle)` | Spatial selection by bounding box |
| `select_by_circle(center, radius, metric)` | Spatial selection by distance (haversine, euclidean, or manhattan) |
| `calculate(target, expression)` | Compute a new field from existing ones |
| `clear()` | Clear the current selection |

### Spatial Analysis

| Method | Purpose |
|--------|---------|
| `bounding_box()` | Compute the min/max extent of all coordinates |
| `haversine_distance(point_a, point_b)` | Great-circle distance on a sphere (metres) |
| `euclidean_distance(point_a, point_b)` | Planar approximation distance (metres) |
| `manhattan_distance(point_a, point_b)` | Taxicab/grid distance (metres) |
| `summary(key_field, summary_field, operation)` | Group-by aggregation (average, sum, count, random) |

### Projection & Visualisation

| Method | Purpose |
|--------|---------|
| `project(target_epsg)` | Reproject coordinates using pyproj |
| `osm()` | Visualise points on OpenStreetMap via Folium (opens in browser) |

### Properties

| Property | Access |
|----------|--------|
| `epsg` | Get/set the EPSG code |
| `coordinates` | Get the list of coordinates |
| `attributes` | Get the list of attribute dictionaries |
| `fields` | Get the list of field names |
| `selection` | Get the current selection set |

---

## Raster Class

| Method/Property | Purpose |
|-----------------|---------|
| `read_image()` | Open a file dialog to select a PNG; loads the image and its world file |
| `epsg` | Get/set the EPSG code |
| `shape` | Returns `[rows, columns]` of the loaded image |

---

## Utilities (standalone functions)

| Function | Purpose |
|----------|---------|
| `warning(message)` | Show a warning dialog |
| `epsg(prompt)` | Ask for an EPSG code via dialog |
| `string(prompt)` | Ask for a text string via dialog |
| `validate(expression)` | Validate an expression for safe use with `eval()` |
| `random_points(...)` | Generate random point coordinates and attributes |
| `input_file(formats)` | File dialog to select an existing file |
| `output_file(formats)` | File dialog to choose a new output file |
| `read_world_file(filename)` | Read the 6-parameter world file for a given image |
| `project_point(point, projection)` | Reproject a single point |
| `screen_to_world(point, affine)` | Convert pixel coordinates to world coordinates using affine parameters |
| `create_osm_point_layer(vector)` | Create a Folium layer from a Vector dataset |
| `show_osm_map(layers)` | Render Folium layers on an OSM basemap and open in browser |
| `write_geojson_points(...)` | Write point data to a GeoJSON file |

---

## Workflow Combinations

### 1. Pure Vector Analysis (no Screen)

**Uses:** `Vector` + `utilities`
**Bindings:** None

Good for: generating data, querying attributes, projecting coordinates, viewing on OSM. No GUI needed.

### 2. Screen + Custom Keyboard/Mouse Bindings (no raster)

**Uses:** `Screen` with custom `keyboard_bind` / `mouse_bind`
**Bindings:** Your own keys like `'1'`, `'2'`, `'R'`, `<Motion>`

Good for: interactive drawing, mouse tracking, triggering custom logic.

### 3. Screen + Raster (image display only)

**Uses:** `Screen` with built-in **F5** / **Shift-F5**
**Bindings:** F5, Shift-F5, optionally Ctrl-F5, Ctrl-Shift-F5

Good for: loading and viewing a georeferenced image.

### 4. Screen + Raster + Digitising + GeoJSON Export

**Uses:** `Screen` with **F5/Shift-F5** + **F9/F10** + **F12**
**Bindings:** F5, Shift-F5, F9, F10, F12

Good for: loading an image, clicking on features to digitise them, then exporting the digitised points to GeoJSON in real-world coordinates.

### 5. Screen + Raster + Digitising + Custom Analysis (full stack)

**Uses:** Everything -- `Screen` + `Raster` + `Vector` + custom bindings
**Bindings:** F5, Shift-F5, F9, F10 + custom `'1'`, `'2'`, `'3'`

Good for: the most advanced workflow where you load a raster, digitise both control and data points, compute a custom transformation, and derive real-world coordinates.

---

## Example 309: Affine Transformation -- Detailed Walkthrough

This example uses the full stack. The custom bindings (`1`, `2`, `3`) implement a three-step affine georeferencing workflow:

### Step-by-step

1. **F5** -- Load a georeferenced raster image (PNG + world file). Enter its EPSG code.
2. **Shift-F5** -- Display the image on the canvas.
3. **F9** -- Enter digitising mode (crosshair cursor).
4. **Click** on both **control points** (where you know the real-world coordinates) and **data points** (where you want to find out the real-world coordinates) on the image.
5. **F10** -- Exit digitising mode.
6. **Press `1`** -- Loops through every digitised point, highlights each in red, and prompts you to type the known real-world X Y coordinates. Points where you enter coordinates become **control points**. Points you skip or cancel remain as **data points**.
7. **Press `2`** -- Separates control points from data points. Builds a least-squares system from control point pairs and solves for the 6 affine parameters (A, B, C, D, E, F).
8. **Press `3`** -- Applies the affine formula to all **data points**, computing their real-world coordinates from pixel coordinates.

### Control Points vs Data Points

- **Control points** (step `1`): You know both pixel AND real-world coordinates. They teach the system the pixel-to-world mapping.
- **Data points** (step `3`): You only know pixel coordinates. The system computes their real-world coordinates using the transformation derived from control points.

---

## Quick Reference Card

| Key | Always Available? | Purpose |
|-----|:-:|---------|
| F5 | Yes | Load image |
| Shift-F5 | Yes | Draw image |
| Ctrl-F5 | Yes | Print image info |
| Ctrl-Shift-F5 | Yes | Fit window to image |
| F9 | Yes | Start digitising |
| F10 | Yes | Stop digitising |
| F12 | Yes | Export digitised points to GeoJSON |
| Left-click | Only between F9 and F10 | Place a point |
| `'1'`, `'2'`, `'3'`, etc. | Only if you `keyboard_bind` them | Whatever you define |
| `<Motion>`, etc. | Only if you `mouse_bind` them | Whatever you define |
