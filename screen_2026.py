import tkinter
import pyproj
import numpy as np
import networkx as nx


from vector_2026 import Vector
from raster_2026 import Raster
from routing_2026 import RoutingNetwork, terrain_mesh_from_raster


import utilities_2026 as utilities


class Screen():

    def __init__(self, rows=600, columns=800, background='black'):

        # Attributes

        self._rows = rows
        self._columns = columns

        self._epsg = None
        self._world_file = None

        # Route selection state
        self._start_point = None
        self._end_point = None
        self._route_stage = None
        self._route_network = None      # RoutingNetwork instance for path computation

        # Route storage for visualization and export
        # _current_route: List of [x, y] screen coordinate tuples for display
        # _route_network_coords: List of (x, y) network EPSG tuples for GPX export
        self._current_route = None  # Store route as list of screen coordinates
        self._route_network_coords = []  # Store route as list of network EPSG coordinates for GPX

        # Root window    
        self._root = tkinter.Tk()

        # Canvas
        self._canvas = tkinter.Canvas(
            self._root,
            width=self._columns,
            height=self._rows,
            bg=background,
            borderwidth=0,
            highlightthickness=0
        )
        
        # Pack
        self._canvas.pack()

        # Datasets

        self._digits = Vector(geometry='POINT')

        self._points = Vector(geometry='POINT')
        self._polylines = Vector(geometry='POLYLINE')
        self._polygons = Vector(geometry='POLYGON')

        self._image = Raster()

        # Class bindings

        # F1-F4

        # F5-F8

        # F5: Export route as GPX (fallback to image load if no route)
        self._root.bind('<F5>', self.export_gpx)
        self._root.bind('<Shift-F5>', self._draw_image)
        self._root.bind('<Control-F5>', self._image_info) # Image info
        self._root.bind('<Control-Shift-F5>', self._fit_canvas_to_image)

        # F9-F12

        self._root.bind('<F9>', self._start_digit_points) # Start digit mode
        self._root.bind('<F10>', self._stop_digit_points) # Stop digit mode

        # Route selection mode bindings
        self._root.bind('<Shift-F9>', self._start_route_selection) # Start route selection
        self._root.bind('<Shift-F10>', self._stop_route_selection) # Stop route selection

        # Pan and zoom navigation bindings
        self._canvas.bind('<Button-2>', self._start_pan)  # Middle mouse start pan
        self._canvas.bind('<B2-Motion>', self._do_pan)   # Middle mouse drag pan
        self._canvas.bind('<Button-3>', self._start_pan)  # Right mouse start pan (alternative)
        self._canvas.bind('<B3-Motion>', self._do_pan)   # Right mouse drag pan (alternative)

        # Mouse wheel bindings (cross-platform)
        self._root.bind('<MouseWheel>', self._handle_mouse_wheel)   # Windows/macOS
        self._root.bind('<Button-4>', self._handle_mouse_wheel)    # Linux scroll up
        self._root.bind('<Button-5>', self._handle_mouse_wheel)    # Linux scroll down

        # Zoom keyboard shortcuts
        self._root.bind('<plus>', self._zoom_in)    # Zoom in with + key
        self._root.bind('<equal>', self._zoom_in)   # Zoom in with = key (unshifted +)
        self._root.bind('<minus>', self._zoom_out)  # Zoom out with - key

        self._root.bind('<F12>', self._digit_points_to_geojson) # points to geojson
        
    
    # "Protected methods"
    # - Only to be used within the library, not by external files

    def _start_digit_points(self, event):
        """
        Digit a point by left-button
        
        :param self: Instance of the class
        :param event: 
        """
        print('Start digitising mode...')

        self._root.bind('<Button-1>', self._get_point) # Left button click
        self.cursor('tcross')

        #'<Button-1>,' 'tcross', defined in tkinter package

    def _get_point(self, event):
        
        self.draw_point([event.x, event.y])

        self._digits._coordinates.append([event.x, event.y])
        count = len(self._digits.coordinates)
        self._digits._attributes.append({'fid': count})



        
    def _stop_digit_points(self, event):
        print('Stop digitising mode..')

        self._root.unbind('<Button-1>')
        self.cursor()

    def _select_route_point(self, event):
        """
        Handle route point selection with two-stage workflow (start, then end).

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
            # End route selection mode after route computation
            self._route_stage = None
            print(f'End point selected: [{x}, {y}]')

            # === NEW IN PHASE 6: Auto-trigger routing ===
            self._compute_and_display_route()

    def _start_route_selection(self, event):
        """
        Start route selection mode for picking start and end points.

        :param self: Instance of the class
        :param event: Keyboard event (Shift-F9)
        """
        self._route_stage = 'start'
        self._root.bind('<Button-1>', self._select_route_point)
        self.cursor('tcross')
        print('Route selection started: click to select start point, then end point')

    def _stop_route_selection(self, event):
        """
        Stop route selection mode and reset state.

        :param self: Instance of the class
        :param event: Keyboard event (Shift-F10)
        """
        self._root.unbind('<Button-1>')
        self.cursor()
        self._route_stage = None
        print('Route selection stopped')

    def _start_pan(self, event):
        """
        Start panning by marking the initial mouse position.

        :param self: Instance of the class
        :param event: Mouse event (middle or right button)
        """
        self._canvas.scan_mark(event.x, event.y)

    def _do_pan(self, event):
        """
        Continue panning by dragging the canvas.

        :param self: Instance of the class
        :param event: Mouse event with drag coordinates
        """
        self._canvas.scan_dragto(event.x, event.y, gain=1)
        # Redisplay coordinate labels after pan
        if self._start_point:
            self._update_coordinate_display(self._start_point, 'Start')
        if self._end_point:
            self._update_coordinate_display(self._end_point, 'End')

    # Zoom in/out around mouse cursor position
    def _zoom_in(self, event):
        """
        Zoom in by 10% around the cursor position.

        :param self: Instance of the class
        :param event: Mouse event with cursor coordinates
        """
        canvas_x = self._canvas.canvasx(event.x)
        canvas_y = self._canvas.canvasy(event.y)
        scale_factor = 1.1
        self._canvas.scale('all', canvas_x, canvas_y, scale_factor, scale_factor)
        # Redisplay coordinate labels after zoom
        if self._start_point:
            self._update_coordinate_display(self._start_point, 'Start')
        if self._end_point:
            self._update_coordinate_display(self._end_point, 'End')

    def _zoom_out(self, event):
        """
        Zoom out by 10% around the cursor position.

        :param self: Instance of the class
        :param event: Mouse event with cursor coordinates
        """
        canvas_x = self._canvas.canvasx(event.x)
        canvas_y = self._canvas.canvasy(event.y)
        scale_factor = 0.9
        self._canvas.scale('all', canvas_x, canvas_y, scale_factor, scale_factor)
        # Redisplay coordinate labels after zoom
        if self._start_point:
            self._update_coordinate_display(self._start_point, 'Start')
        if self._end_point:
            self._update_coordinate_display(self._end_point, 'End')

    # Cross-platform mouse wheel handler for Windows/macOS/Linux
    def _handle_mouse_wheel(self, event):
        """
        Handle mouse wheel events for zooming on all platforms.

        :param self: Instance of the class
        :param event: Mouse wheel event (delta for Windows/macOS, num for Linux)
        """
        if hasattr(event, 'delta'):
            # Windows/macOS: event.delta is positive for scroll up, negative for down
            delta = event.delta
        else:
            # Linux: use event.num (4 for scroll up, 5 for scroll down)
            delta = 120 if event.num == 4 else -120

        if delta > 0:
            self._zoom_in(event)
        else:
            self._zoom_out(event)

    def screen_to_decimal_degrees(self, screen_point):
        """
        Transform screen coordinates to WGS84 decimal degrees.

        :param self: Instance of the class
        :param screen_point: [x, y] screen coordinates
        :return: [lon, lat] in decimal degrees, or None if world file not set
        """
        if self._world_file is None:
            return None

        # Screen to world coordinates using affine transformation
        world_point = utilities.screen_to_world(screen_point, self._world_file)

        # If already EPSG:4326 or no EPSG set, return as-is
        if self._epsg is None or self._epsg == 4326:
            return world_point

        # Transform from current EPSG to EPSG:4326 (WGS84)
        try:
            transformer = pyproj.Transformer.from_crs(
                pyproj.CRS.from_epsg(self._epsg),
                pyproj.CRS.from_epsg(4326),
                always_xy=True
            )
            lon, lat = transformer.transform(*world_point)
            return [lon, lat]
        except Exception:
            return world_point  # Fallback if transformation fails

    def _update_coordinate_display(self, point, label):
        """
        Display decimal degree coordinates for a selected point.

        :param self: Instance of the class
        :param point: [x, y] screen coordinates
        :param label: Label for the point ('Start' or 'End')
        """
        coord_point = self.screen_to_decimal_degrees(point)
        if coord_point is None:
            return

        lon, lat = coord_point
        self.delete('coord_display')

        # Format with 6 decimal places for precision
        message = f'{label}: Lat {lat:.6f}, Lon {lon:.6f}'
        self.draw_text(point, message, colour='white', tag='coord_display')

    def _read_image(self, event):
        """
        Read image with F5 and auto-generate routing network (Phase 7).

        User loads GeoTIFF terrain file, system automatically generates
        routing mesh for immediate route computation via GUI.

        Per D-01: Auto-trigger after terrain load.
        Per D-02: Fixed 200m mesh spacing for v1.
        Per D-03: Cursor progress indication during generation.
        Per D-04: Warning dialogs for all error types.
        Per D-05: Validate network non-emptily before assignment.
        Per D-06: Network replacement on re-load (hot reload).

        :param self: Instance of the class
        :param event: Keyboard event (F5 key press)
        """
        # Load terrain data
        self._image.read_image()
        self._world_file = self._image._world_file
        print(f"WORLD FILE SET (F5): {self._world_file}")  # Debug output

        # Use embedded EPSG from GeoTIFF if available, otherwise prompt user
        if self._image.epsg is not None:
            self._epsg = self._image.epsg
            print(f"EPSG set from terrain file: {self._epsg}")
        else:
            epsg = utilities.epsg()
            if epsg is not None:
                self._epsg = epsg
                self._image.epsg = epsg
                print(f"EPSG set from user input: {self._epsg}")

        # === Phase 7: Auto-generate routing network from terrain ===
        try:
            # Progress indication: cursor changes to watch
            self._root.config(cursor='watch')
            self._root.update_idletasks()
            print("Generating routing network from terrain...")

            # Generate mesh with fixed 200m spacing (v1)
            # Disable water queries for v1 to avoid blocking OSM API calls in GUI
            routing_net = terrain_mesh_from_raster(
                self._image,
                mesh_spacing=200,  # Fixed per D-02: performance vs detail tradeoff
                enable_water_queries=True
            )

            # Validate network before assignment (D-05)
            if len(routing_net.graph.nodes) == 0:
                utilities.warning(
                    "Mesh generation produced empty network. "
                    "Terrain data may be invalid."
                )
                print("Warning: Empty network, not assigned to screen.")
            else:
                # Assign network to screen (Phase 6 integration)
                self.set_route_network(routing_net)
                print(f"Mesh network created and assigned: "
                      f"{len(routing_net.graph.nodes)} nodes, "
                      f"{len(routing_net.graph.edges)} edges")

            # Display the terrain image on canvas
            if self._image and hasattr(self._image, '_photoimage') and self._image._photoimage:
                self._canvas.delete('all')
                self._canvas.create_image(0, 0, image=self._image._photoimage, anchor='nw')
                print("Terrain image displayed on canvas")

        except Exception as e:
            # Error handling with warning dialog (D-04)
            utilities.warning(f"Failed to generate routing network: {e}")
            print(f"Mesh generation error: {e}")
        finally:
            # Restore cursor even if fails (D-03)
            self._root.config(cursor='arrow')

    def _draw_image(self, event):

        self._canvas.create_image(0,0, image=self._image._photoimage, anchor='nw') # North west

    def _image_info(self, event):

        print(self._image)

    def _fit_canvas_to_image(self, event):
        if self._image is None:
            return
        
        if self._image.shape is None:
            return
        
        rows, columns = self._image.shape

        self._canvas.configure(
            height=rows, width=columns
        )

        self._root.geometry(f'{columns}x{rows}')

        self._rows = rows
        self._columns = columns

    def world_to_screen(self, world_point):
        """
        Transform world coordinates to screen coordinates using world file.

        :param self: Instance of the class
        :param world_point: [x, y] world coordinates
        :return: [x, y] screen coordinates, or None if world file not set
        """
        if self._world_file is None:
            return None

        # World to screen using inverse of screen_to_world transformation
        # Affine transformation: [a, d, b, e, c, f]
        # screen_to_world: x_world = a*x + b*y + c, y_world = d*x + e*y + f
        # world_to_screen: Invert the affine matrix
        a, d, b, e, c, f = self._world_file

        # Create 2x2 transformation matrix and translation vector
        A = np.array([[a, b], [d, e]])
        t = np.array([c, f])

        # Invert the transformation matrix
        try:
            A_inv = np.linalg.inv(A)
        except np.linalg.LinAlgError:
            return None

        x_world, y_world = world_point

        # Apply inverse transformation: screen = A_inv * (world - t)
        screen = A_inv.dot(np.array([x_world, y_world]) - t)

        return [float(screen[0]), float(screen[1])]

    def display_route(self, route_coords):
        """
        Display computed route on the canvas with distinctive orange styling.

        Per locked decisions: bright color (orange), medium width (4px),
        auto-show after computation, clear old routes first.

        :param self: Instance of the class
        :param route_coords: List of (x, y) network EPSG coordinate tuples
        """
        # Clear old routes before displaying new one (D-06)
        self.delete('route')

        if not route_coords:
            return

        # Transform network EPSG coordinates to screen coordinates
        screen_coords = []
        for coord in route_coords:
            screen_point = self.world_to_screen(coord)
            if screen_point is not None:
                screen_coords.append(screen_point)

        if not screen_coords:
            return

        # Store screen coordinates for potential later use
        self._current_route = screen_coords

        # Display route with orange color, 4px width (D-02, D-03)
        self.draw_polyline(
            polyline=screen_coords,
            width=4,
            colour='orange',
            tag='route'
        )

        print(f'Route displayed: {len(screen_coords)} points')

    def set_route(self, network_coords):
        """
        Set and display route coordinates from routing computation.

        :param self: Instance of the class
        :param network_coords: List of (x, y) network EPSG coordinate tuples
        """
        # Store original network coordinates for GPX export
        self._route_network_coords = network_coords

        # Display route on canvas
        self.display_route(network_coords)

    def set_route_network(self, network):
        """
        Assign a routing network to the screen for path computation.

        Args:
            network: RoutingNetwork instance containing graph and node coordinates

        Raises:
            ValueError: If network is not a RoutingNetwork instance

        Per D-02: Network provides EPSG context for coordinate transformations.
        """
        if not isinstance(network, RoutingNetwork):
            raise ValueError(
                f"Expected RoutingNetwork instance, got {type(network).__name__}"
            )

        self._route_network = network
        print(f'Routing network assigned to screen. Graph has '
              f'{len(network.graph.nodes)} nodes, {len(network.graph.edges)} edges')

    def _compute_and_display_route(self):
        """
        Compute and display route between selected start and end points.

        Workflow:
        1. Validate prerequisites (network, world file, coordinates)
        2. Transform screen coords -> world coords -> network EPSG coords
        3. Snap to nearest graph nodes (find_nearest_node)
        4. Compute shortest path (shortest_path)
        5. Map node IDs -> network coordinates
        6. Transform network coords -> world coords -> screen coords
        7. Store for GPX export and display route

        Per D-01: Auto-triggered after end point selection.
        Per D-02: Screen -> World -> Network EPSG coordinate mapping.
        Per D-03: Snap to nearest graph node.
        Per D-04: Message dialog for all error types.

        Error handling: All user-facing errors trigger utilities.warning().
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
            if self._epsg is None or self._route_network.epsg is None:
                utilities.warning('Coordinate systems undefined')
                return

            transformer = pyproj.Transformer.from_crs(
                pyproj.CRS.from_epsg(self._epsg),
                pyproj.CRS.from_epsg(self._route_network.epsg),
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
        self._root.config(cursor='watch')
        self._root.update_idletasks()

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
            self.set_route(route_network_coords)

            # Print routing stats for debugging
            print(f'Route computed: {len(route_screen_coords)} vertices, '
                  f'{start_dist:.1f}m from start node, {end_dist:.1f}m from end node')

        finally:
            # === 11. Restore cursor ===
            self._root.config(cursor='arrow')

    def export_gpx(self, event=None):
        """
        Export current route as GPX file with WGS84 coordinates.

        Triggered by F5 key. Shows file save dialog. Falls back to
        _read_image if no route computed yet.

        :param self: Instance of the class
        :param event: tkinter event (optional, for keyboard binding)
        """
        # Check if route has been computed
        if not self._route_network_coords:
            # No route available, fall back to image load (existing F5 behavior)
            print('No route computed. Loading image instead.')
            self._read_image(event)
            return

        # Check coordinate system availability
        if self._epsg is None:
            print('Error: EPSG code not set. Cannot transform to WGS84 for GPX.')
            return

        # Transform coordinates from network EPSG to WGS84 (EPSG:4326)
        try:
            transformer = pyproj.Transformer.from_crs(
                pyproj.CRS.from_epsg(self._epsg),
                pyproj.CRS.from_epsg(4326),
                always_xy=True
            )
        except Exception as e:
            print(f'Error creating coordinate transformer: {e}')
            return

        # Generate GPX track points with 6 decimal places (~0.1 meter precision)
        track_points = []
        for (x, y) in self._route_network_coords:
            lon, lat = transformer.transform(x, y)
            track_points.append(f'      <trkpt lat="{lat:.6f}" lon="{lon:.6f}"></trkpt>')

        # Generate GPX 1.1 XML structure (track-only format per D-07)
        gpx_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="Norwegian Hiking Route Planner" xmlns="http://www.topografix.com/GPX/1/1">
  <trk>
    <name>Route</name>
    <trkseg>
{chr(10).join(track_points)}
    </trkseg>
  </trk>
</gpx>
'''

        # Show file save dialog (D-09)
        from tkinter import filedialog
        from datetime import datetime

        today = datetime.now().strftime("%Y-%m-%d")
        filename = filedialog.asksaveasfilename(
            title='Export Route as GPX',
            defaultextension='.gpx',
            initialfile=f'route_{today}.gpx',
            filetypes=[
                ('GPX files', '*.gpx'),
                ('All files', '*.*')
            ]
        )

        if not filename:  # User cancelled dialog
            print('Export cancelled by user')
            return

        # Write GPX file with UTF-8 encoding
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(gpx_content)
            print(f'Route exported successfully to: {filename}')
        except Exception as e:
            print(f'Error writing GPX file: {e}')

    def _digit_points_to_geojson(self, event):

        if len(self._digits.coordinates) == 0:
            utilities.warning('Digitised points not found')
            return
        
        if self._world_file is None:
            utilities.warning('World file data not found')
            return
        
        # 1. Screen to world coordinates

        terrain_coordinates = []

        for point in self._digits.coordinates:
            terrain_point = utilities.screen_to_world(point, self._world_file)
            terrain_coordinates.append(terrain_point)

        print(terrain_coordinates) # UTM coordinates

        # Write GeoJSON file

        # 2.1 Filename
        filename = utilities.output_file(['geojson'])

        if filename is None:
            return
        
        # 2.2 Write file

        utilities.write_geojson_points(
            filename,
            terrain_coordinates,
            self._digits.attributes,
            self._epsg
        )

    # User Methods

    def loop(self):
        self._root.mainloop()

    # Interfaces for final users to create binding
    # Link between some event and some function. keyboard click triggers function

    def keyboard_bind(self, event, function):
        """
        Docstring for keyboard_bind
        
        :param event: trigger (key, mouse, or any other event)
        :param function: action
        """
        
        self._root.bind(event, function)

    def keyboard_unbind(self, event):
        self._root.unbind(event)

    def mouse_bind(self, event, function):
        self._canvas.bind(event, function)
    
    def mouse_unbind(self, event):
        self._canvas.unbind(event)

    def cursor(self,shape=''):
        self._canvas.config(cursor=shape)

    # Important to become familiare with!
    def delete(self, tag):
        """
        Delete graphic elements on canvas
        
        :param self: Description
        :param tag: Description
        """
        self._canvas.delete(tag)
    
    def draw_point(self, point, size=3, colour='white', tag = 'point'):
        """
        Draw point (in screen coordinates) on the canvas
        Doesnt have a native method to draw points. We will draw a small rectangle and fill it with a colour
        
        :param self: Description
        :param point: Description
        :param size: Description
        :param colour: Description
        :param tag: Description
        """

        x, y = point
        # Defining coordinates for the rectangle
        x_min = x - size
        x_max = x + size
        y_min = y - size
        y_max = y + size
        
        # Using existing create_rectangle() function
        self._canvas.create_rectangle(
            x_min, y_min, x_max, y_max, fill=colour, tag=tag
        )

    
    def draw_polyline(self, polyline, width=3, colour='white',
                      vertices = False, tag = 'polyline'):
        """
        Draw polyline (in screen coordinates) on the canvas
        """
  
        self._canvas.create_line(
            polyline, fill=colour, width=width, tag=tag
        )
        if vertices is True:
            for point in polyline:
                self.draw_point(point, colour=colour, size=4, tag=tag)

    
    def draw_polygon(self, polygon, width=3, colour='white', vertices = False, 
                     stipple=False, boundary=False, tag = 'polyline'):
        
        """
        Holes: Tkinter > 8.6
        
        """

        if stipple is True:
            pattern = 'gray25'
        else:
            pattern = ''

        self._canvas.create_polygon(
            polygon, fill=colour, width=width, stipple=pattern, tag=tag
        )

        if boundary is True:

            for part in polygon:
                self.draw_polyline(part, colour=colour, tag=tag)

        if vertices is True:
            for part in polygon:
                for part in part[1:]:
                    self.draw_point(point=part, colour=colour, tag=tag)


    def draw_text(self, point, message, colour='white', tag='text'):

        self._canvas.create_text(
            *point, text=message, fill=colour, tag=tag
        )
        # ^ by using "*" python unpacks the sequence and passes its elements as separate positional arguments.
