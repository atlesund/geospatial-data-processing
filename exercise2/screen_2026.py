import json
import tkinter


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
        self._root.bind('<Control-Shift-F5>', self._fit_canvas_to_image) # Image info

        # F9-F12

        self._root.bind('<F9>', self._start_digit_points) # Start digit mode
        self._root.bind('<F10>', self._stop_digit_points) # Stop digit mode
        
        self._root.bind('<F12>', self._digit_points_to_geojson) # 
        
    
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

    def _read_image(self, event):

        """
        Read image with F5
        
        :param self: Description
        :param event: Description
        """

        self._image.read_image()
        self._world_file = self._image._world_file

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