import json
import tkinter
import pyproj


from vector_2026 import Vector
from raster_2026 import Raster


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

        self._root.bind('<F5>', self._read_image)
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
            # Toggle back to start stage for reset
            self._route_stage = 'start'
            print(f'End point selected: [{x}, {y}]')

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
        Read image with F5
        
        :param self: Description
        :param event: Description
        """

        self._image.read_image()
        self._world_file = self._image._world_file
        print(f'WORLD FILE SET IN READ_IMAGE (F5): {self._world_file}') #REMOVE

        epsg = utilities.epsg()
        if epsg is not None:
            self._epsg = epsg

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
