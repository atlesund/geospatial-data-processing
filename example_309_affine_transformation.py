# From rowxcolumn to UTM (real coordinates)
    # x_w = Ax + By + C
    # y_w = Dx + Ey + F

"""
694500.0 4301500.0
696000.0 4301500.0
696000.0 4300500.0
694500.0 4300500.0
"""

# Running this we define the 

import numpy as np
import geo_2026 as geo

# 1. Callbacks

def set_control_coordinates(event):
    """
    Select a number of digit points as control points
    """
    if len(screen._digits.coordinates) == 0:
        return
    for count, point in enumerate(screen._digits.coordinates):

        screen.delete('highlight')

        # Raster coordinates
        
        screen.draw_point(point, size=5, colour='red', tag='highlight')

        # Terrain coordaintes
        xy_string = geo.utilities.string(prompt= 'X Y (separated by blank space)')

        try: 
            x_control, y_control = map(float, xy_string.split())

            # TODO: Store control coordinates
            print(x_control, y_control)
            
            screen._digits._attributes[count]['x_control'] = x_control
            screen._digits._attributes[count]['y_control'] = y_control
        except:
            pass

    screen.delete('highlight')

    print(screen._digits.coordinates)
    print()
    print(screen._digits.attributes)
    

def compute_affine_transformation(event):

    # Making affine global, so its reachable outside the function scope
    
    global affine
    global data_points
    if len(screen._digits.coordinates) == 0:
        return
    
    affine_a = []
    affine_b = []
    data_points = []
    for count, point in enumerate(screen._digits.coordinates):
        try:
            # Collect control points
            x_control = screen._digits._attributes[count]['x_control']
            y_control = screen._digits._attributes[count]['y_control']

            x, y = point

            affine_a.append[(x,y,1,0,0,0)]
            affine_a.append[(0,0,0,x,y,1)]

            affine_b.append([x_control])
            affine_b.append([y_control])
        except:
            # Data points
            data_points.append(point)

    # Solving the system of equations 
    a = np.array(affine_a)
    b = np.array(affine_b)

    x = np.linalg.lstsq(a,b)

    affine = x[0].flatten().tolist()

    print(affine)

def transform_data_points(event):

    a, b, c, d, e, f = affine

    for count, point in enumerate(data_points):
        x, y = point # Raster coordinates

        x_world = a * x + b * y + c
        y_world = d * x + e * y + f

        screen._points._coordinates.append([x_world, y_world])
        screen._points._attributes.append({'fid': count})

    print(screen._points)
    print(screen._points._coordinates)
    


# 2. Screen instance

screen = geo.Screen()

# 3. Bindings

screen.keyboard_bind('1', set_control_coordinates)
screen.keyboard_bind('2', compute_affine_transformation)
screen.keyboard_bind('3', transform_data_points)

# 4. loop
screen.loop()