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

        # F9-F12

        self._root.bind('<F9>', self._start_digit_points) # Start digit mode
        self._root.bind('<F10>', self._stop_digit_points) # Stop digit mode
    
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