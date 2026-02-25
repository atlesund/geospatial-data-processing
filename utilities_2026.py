

import ast
import json
import os
import random
import webbrowser

import tkinter
import tkinter.filedialog
import tkinter.messagebox
import tkinter.simpledialog

import folium # For mapping
import pyproj # From one system to another




folium_colours = [
    'red', 'blue', 'green', 'purple', 'orange', 
    'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen',
    'cadetblue', 'darkpurple', 'white', 'pink', 'lightblue',
    'lightgreen', 'gray', 'black', 'lightgray'
]

geoformats = {
    'csv': ('CSV Files', '*.csv'),
    'geojson': ('GeoJSON Files', '*.geojson'),
    'shp': ('Shapefiles', '*.shp'),
    'png': ('PNG Files', '*.png')
}



def warning(message, title='Warning'):
    tkinter.Tk().withdraw() # 
    tkinter.messagebox.showwarning(title, message)

def epsg(prompt='EPSG code', title='GEO 2026'):
    tkinter.Tk().withdraw()
    epsg = tkinter.simpledialog.askinteger(
        title=title, prompt=prompt
    )

    # TODO: check that the EPSG code is valid (return None)

    return epsg



def string(prompt='Enter string', title='GEO 2026'):
    tkinter.Tk().withdraw()
    string = epsg = tkinter.simpledialog.askstring(
        title=title, prompt=prompt
    )


    return string


def validate(expression):
    """Validate an expression to be processed with eval()"""
    
    validation = {'status': True, 'tokens': []}

    block_list = ['os']

    # Get syntax tree

    try:
        tree = ast.parse(expression, mode='eval')
    except:
        validation['status'] = False
        validation['message'] = f'Syntax error in expression "{expression}"'
        return validation

    # Get relevant tokens

    module = []
    function = []
    arithmetic = []
    logical = []
    relational = []
    constant = []
    label = [] # Field names

    for node in ast.walk(tree):

        class_name = node.__class__.__name__

        if class_name == 'Call':
            try:
                function.append(node.func.id) # simple function
            except:
                module.append(node.func.value.id)
                function.append(f'{node.func.value.id}.{node.func.attr}')
        elif class_name in ['Add', 'Sub', 'Mult', 'Div', 'Pow']:
            arithmetic.append(class_name)
        elif class_name in ['Not', 'And', 'Or']:
            logical.append(class_name)
        elif class_name in ['Eq', 'NotEq', 'Gt', 'Lt', 'GtE', 'LtE']:
            relational.append(class_name)
        elif class_name == 'Constant':
            constant.append(node.value)
        elif hasattr(node, 'id'):
            if node.id not in function and node.id not in module:
                label.append(node.id)

    # Dictionary of tokens

    tokens = {
        'module': module,
        'function': function,
        'arithmetic': arithmetic,
        'logical': logical,
        'relational': relational,
        'constant': constant,
        'label': label
    }

    validation['tokens'] = tokens

    # Check block_list

    for token in tokens['module']:
        if token in block_list:
            validation['status'] = False
            validation['message'] = f'Forbidden keyword "{token}"'
            break

    return validation




def random_points(n, x_min, y_min, x_max, y_max):

    delta_x = x_max - x_min
    delta_y = y_max - y_min

    coordinates = []
    attributes = []

    for count in range(n):
        x_random = x_min + random.random() * delta_x
        y_random = y_min + random.random() * delta_y

        coordinates.append([x_random, y_random])

        attributes.append({
            'fid': count # fid = Feature ID
        })
    return [coordinates, attributes]


def create_osm_point_layer(vector):
    if vector.epsg is None:
        warning('Unknown EPSG code')
        return None
    if vector.epsg == 4326 or vector.epsg == 4258:
        projection = None

    else:
        # TODO: Create projection

        source_crs = pyproj.CRS.from_epsg(vector.epsg)
        target_crs = pyproj.CRS.from_epsg(4326) # Part of definition


        projection = pyproj.Transformer.from_crs(
            source_crs, target_crs, always_xy=True, # Order = lon, latitude
        )

    # Folium Marker color
    if 'colour' in vector.fields:
        colour_field = 'colour'
    elif 'color' in vector.fields:
        colour_field = 'color'
    else:
        colour_field = None
        marker_colour = random.choice(folium_colours)

        

    # Folium marker size
    marker_size = 4

    # Folium layer

    osm_layer = folium.FeatureGroup(name='osm')

    for count, point in enumerate(vector.coordinates):

        # Coordinates

        if projection is None:
            longitude, latitude = point
        else:
            #x, y = point
            #longitude, latitude = projection.transform(x, y)
            longitude, latitude = projection.transform(*point)

        # Popup with attributes
        osm_popup_text = ''

        for field, value in vector.attributes[count].items():
            osm_popup_text += field.upper() + ': ' + str(value) + '<br>'

            # Some characters are not allowed in HTML
            # TODO

        osm_popup = folium.Popup(osm_popup_text, max_width=500)

        # Folium colour
        if colour_field is not None:
            marker_colour = vector.attributes[count][colour_field]

        

        # Folium marker


        osm_marker = folium.CircleMarker(
            location = [latitude, longitude], # order is important
            popup = osm_popup,
            radius   = marker_size, 
            color    = marker_colour,
            fill     = True,
            fill_color = marker_colour,
            fill_opacity = 0.4,
        )

        osm_layer.add_child(osm_marker)

    return osm_layer


def show_osm_map(layers, filename='osm.html'):
    """Show layers on OSM base map"""

    osm_map = folium.Map()
    for layer in layers:
        osm_map.add_child(layer)

    osm_map.fit_bounds(
        osm_map.get_bounds()
    )

    osm_map.save(filename)

    webbrowser.open(
        os.path.abspath(filename)
    )

def input_file(formats=None, title='Select input file'):
    """Open a dialogue box to select an existing file"""

    try:

        if formats is None:
            filetypes = [('All Files', '*.*')]
        else:
            filetypes = []

            for geoformat in formats:

                try:
                    filetypes.append(geoformats[geoformat.lower()])
                except:
                    continue

                filetypes.append(('All Files', '*.*'))

        # GUI

        tkinter.Tk().withdraw()

        filename = tkinter.filedialog.askopenfilename(
            title=title, filetypes=filetypes
        )

        if not filename:
            filename = None
    except:
        filename = None

    return filename

def output_file(formats=None, title='Select output file'):
    """Open a dialogue box to select a new output file"""

    try:

        if formats is None:
            filetypes = [('All Files', '*.*')]
        else:
            filetypes = []

            for geoformat in formats:

                try:
                    filetypes.append(geoformats[geoformat.lower()])
                except:
                    continue

                filetypes.append(('All Files', '*.*'))

        # GUI

        tkinter.Tk().withdraw()

        filename = tkinter.filedialog.asksaveasfilename(
            title=title, filetypes=filetypes
        )

        if not filename:
            filename = None
    except:
        filename = None

    if not filename.endswith('.geojson'):
        filename = filename + '.geojson'
    
    return filename

def read_world_file(filename):
    image_filename, image_extension = os.path.splitext(filename)

    # Corresponding world file: png -> pgw
    world_extension = image_extension[1] + image_extension[-1] + 'w'

    world_filename = image_filename + '.' + world_extension

    # print(world_filename)

    try:
        with open(world_filename, 'rt') as world_file: # world_file = the file object
            records = world_file.readlines()

            world = list(map(float, records))

            if len(world) != 6:
                world = None
    
    except:
        world = None

    return world

def project_point(point, projection):
    x, y = point
    x_projected, y_projected = projection.transform(x,y)

    return [x_projected, y_projected]

