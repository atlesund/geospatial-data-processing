

import ast
import json
import os
import random
import webbrowser

import tkinter
import tkinter.filedialog
import tkinter.messagebox
import tkinter.simpledialog

import shapefile
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
    'png': ('PNG Files', '*.png'),
    'tif': ('TIFF Files', '*.tif'),
    'tiff': ('TIFF Files', '*.tiff')
}

def warning(message, title='Warning'):
    tkinter.Tk().withdraw() # 
    tkinter.messagebox.showwarning(title, message)

def epsg(prompt='EPSG code (25833)', title='GEO 2026'):
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

def screen_to_world(point, affine):
    x,y = point
    a, d, b, e, c, f = affine

    x_world = a*x + b*y + c
    y_world = d*x + e*y + f

    return [x_world, y_world]

def write_geojson_points(filename, coordinates, attributes, source_epsg):
    if source_epsg != 4326: # GeoJSON CRS is always 4326

        source_crs = pyproj.CRS.from_epsg(source_epsg)
        target_crs = pyproj.CRS.from_epsg(4326) # Part of definition


        projection = pyproj.Transformer.from_crs(
            source_crs, target_crs, always_xy=True, # Order = lon, latitude
        )

        projected = []
        for point in coordinates:
            x_projected, y_projected = projection.transform(*point)
            projected.append([x_projected, y_projected])

        coordinates = projected

    # GeoJSON file

    features = [] #feature entry of GeoJSON format

    for count, point in enumerate(coordinates):
        # We are defining a feature collection
        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': point
            },
            'properties': attributes[count]
        }

        features.append(feature)

    geojson = {
        'type': 'FeatureCollection',
        'features': features
    }
    with open(filename, 'wt') as geojson_file:
        json.dump(geojson, geojson_file, indent=4)


def describe_geojson(filename=None):

    if filename is None:
        filename = input_file(['geojson'])

    with open(filename, 'rt') as f:
        data = json.load(f)

    counts = {
        'Point': 0,
        'LineString': 0,
        'Polygon': 0,
        'MultiPoint': 0,
        'MultiLineString': 0,
        'MultiPolygon': 0,
        'GeometryCollection': 0
    }

    for feature in data['features']:
        geometry_type = feature['geometry']['type']

        if geometry_type in counts:
            counts[geometry_type] += 1

    return counts


def read_geojson_points(data, multi=False):
    coordinates = []
    attributes = []

    count = 0
    for feature in data['features']:
        geom_type = feature['geometry']['type']

        if geom_type == 'Point':
            coordinates.append(feature['geometry']['coordinates'])
            attributes.append({'fid': count})
            count += 1

        elif geom_type == 'MultiPoint' and multi is True:
            for part in feature['geometry']['coordinates']:
                coordinates.append(part)
                attributes.append({'fid': count})
                count += 1

    return [coordinates, attributes]


def read_geojson_polylines(data, multi=False):
    coordinates = []
    attributes = []

    count = 0
    for feature in data['features']:
        geom_type = feature['geometry']['type']

        if geom_type == 'LineString':
            coordinates.append(feature['geometry']['coordinates'])
            attributes.append({'fid': count})
            count += 1

        elif geom_type == 'MultiLineString' and multi is True:
            for part in feature['geometry']['coordinates']:
                coordinates.append(part)
                attributes.append({'fid': count})
                count += 1

    return [coordinates, attributes]


def read_geojson_polygons(data, multi=False):
    coordinates = []
    attributes = []

    count = 0
    for feature in data['features']:
        geom_type = feature['geometry']['type']

        if geom_type == 'Polygon':
            coordinates.append(feature['geometry']['coordinates'])
            attributes.append({'fid': count})
            count += 1

        elif geom_type == 'MultiPolygon' and multi is True:
            for part in feature['geometry']['coordinates']:
                coordinates.append(part)
                attributes.append({'fid': count})
                count += 1

    return [coordinates, attributes]

def multiple_input_files(formats=None, title='Select multiple input files'):

    """Select multiple files by dialogue box"""
    
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

        filenames = tkinter.filedialog.askopenfilenames(
            title=title, filetypes=filetypes
        )

        if not filenames:
            filenames = None
    except:
        filenames = None

    return filenames


def merge_geojson(input_filenames, output_filename):
    # depending on type of geometry we will use: read_geojson_polylines etc. to retrieve the coordinates and attributes
    # NB! We have to alter it so that it reads the properties in geojson
    if input_filenames is None or output_filename is None:
        warning("Missing filename(s)")
        return
    

    coordinates = []
    attributes = []
    for input_file in input_filenames:
        with open(input_file, 'rt') as f:
            data = json.load(f)

        coordinates_temp, attributes_temp = read_geojson_points(data)
        
        coordinates.append(coordinates_temp)
        attributes.append(attributes_temp)
        # We dont have use for the attributes delivered from read_geojson_points, since they have overlapping fid, we need to 
        # create new fids
        

    features = [] #feature entry of GeoJSON format

    #for i in range(0,len(coordinates)):
    for count, point in enumerate(coordinates):
        # We are defining a feature collection
        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': point
            },
            'properties': {
                'MERGE_ID': count,
            }
        }

        features.append(feature)

    geojson = {
        'type': 'FeatureCollection',
        'features': features
    }
    with open(output_filename, 'wt') as geojson_file:
        json.dump(geojson, geojson_file, indent=4)


def read_shapefile_points(filename, encoding):
    report = {
        'status': False,
        'message': '',
        'coordinates': [],
        'attributes': [],
        'epsg': 'None'
    }

    # Create Shapefile "Reader"

    try:
        reader = shapefile.Reader(filename, encoding=encoding)
    except:
        report['message'] = 'Filename not found'
        return
    
    shapefile_geometry = reader.shapeType

    #if shapefile_geometry in [1, 8, 11, 18, 28] #Points, MultiPoints etc.
    if shapefile_geometry != 1:
        report['message'] = 'Wrong Shapefile geometry type'
        return
    
    # Fields in the shapefile
    fields = reader.fields[1:]

    coordinates = []
    attributes = []

    print(fields)

    # Coordinates and attributes

    for record in reader.shapeRecords():
        print("==================")
        print(record)
        print("==================")
        print(record.shape.points)
        print("==================")

        # Coordinates
        if shapefile_geometry == 1:
            coordinates.append(record.shape.points[0])
        elif shapefile_geometry == 8:
            pass # We are interested in the Point (1) for now

        # Attributes

        values = record.record[:]

        print(values)

        attribute = {}

        for count, value in enumerate(values):

            field_name = fields[count][0]
            field_type = fields[count][1]

            field_decimal_places = fields[count][-1]

            # Convert to int, float, or date

            if value is None:
                if field_type == 'N': # N = Number
                    if field_decimal_places == 0:
                        value = -9999
                    else:
                        value = -9999.0
                elif field_type == 'D': # Shapefile format for date
                    value = 'null'
            else:
                if field_type == 'N': # N = Number
                    if field_decimal_places == 0:
                        try: 
                            value = int(value)
                        except:
                            value = int(value.decode(encoding))

                    else:
                        value = float(value)
                elif field_type == 'D': # Shapefile format for date
                    value = value.strftime('%Y-%m-%d')

            
            attribute[field_name] = value

        attributes.append(attribute)


    report['status'] = True
    report['coordinates'] = coordinates
    report['attributes'] = attributes


    # EPSG code

    report['epsg'] = get_shapefile_epsg(filename)

    return report

def get_shapefile_epsg(filename):
    prj_filename = filename.replace('.shp', '.prj')

    try:
        with open(prj_filename, 'rt') as prj_file:
            wkt = prj_file.read()
            epsg = pyproj.CRS.from_wkt(wkt).to_epsg()

    except:
        epsg = None
    return epsg


def intersect(p_1, p_2, p_3, p_4):

    """
    Compute intersection between:
    Segment 1 = (p_1, p_2)
    Segment 2 = (p_3, p_4)

    Return coordinates and type of intersection
    """

    x_1, y_1 = p_1
    x_2, y_2 = p_2
    x_3, y_3 = p_3
    x_4, y_4 = p_4

    # Check denominator

    d = (y_2 - y_1) * (x_4 - x_3) - (x_2 - x_1) * (y_4 - y_3)

    if d == 0: # Tolerance
        return None # There is no intersection, i.e. parallel segments
    
    # Compute the numerators

    n_a = (x_1 - x_3) * (y_4 - y_3) * (y_1 - y_3) * (x_4 - x_3)
    n_b = (x_2 - x_1) * (y_3 - y_1) * (y_2 - y_1) * (x_3 - x_1)

    # Scale factors

    u_a = n_a / d
    u_b = n_b / d

    # Intersection coordinates

    x_intersection = x_1 + u_a * (x_2 - x_1)
    y_intersection = y_1 + u_a * (y_2 - y_1)

    # Type of intersection

    if u_a >= 0.0 and u_a <= 1.0 and u_b >= 0.0 and u_b <= 1.0:
        type_intersection = True # The segments intersect
    elif (u_a >= 0.0 and u_a <= 1.0) and (u_b < 0.0 or u_b > 1.0):
        type_intersection = None # The lines intersect but not the segments
    else:
        type_intersection = False # The lines do not intersect

    return [x_intersection, y_intersection, type_intersection] 


def read_csv_points(filename, id_field, x_field, y_field, separator):

    # Read file contents

    with open(filename, 'rt') as csv_file:
        data = csv_file.readlines()

    # Header

    header = data[0].strip().split(separator)

    # Check fields

    if id_field not in header:
        warning(f'ID field "{id_field}" not found')
        return
    
    if x_field not in header:
        warning(f'X field "{x_field}" not found')
        return

    if y_field not in header:
        warning(f'Y field "{y_field}" not found')
        return

    # Field indices

    id_field_index = header.index(id_field)
    x_field_index = header.index(x_field)
    y_field_index = header.index(y_field)

    # Process data

    coordinates = []
    attributes = []

    for record in data[1:]:

        attribute = {}

        for field_index, field_value in enumerate(record.strip().split(separator)):

            if field_index == id_field_index:
                attribute['fid'] = field_value
            elif field_index == x_field_index:
                x = float(field_value)
            elif field_index == y_field_index:
                y = float(field_value)
            else:
                attribute[header[field_index]] = field_value

        coordinates.append([x, y])
        attributes.append(attribute)
                
    return [coordinates, attributes]


def read_csv_polylines(filename, id_field, x_field, y_field, separator):

    # Read file contents

    points = read_csv_points(filename, id_field, x_field, y_field, separator)

    if points is None:
        return None

    coordinates, attributes = points

    raw_polylines = {}
    raw_attributes = {}

    for count, point in enumerate(coordinates):
        point_id = attributes[count]['fid'] # WE store id's as 'fid' in the attributes
        try:
            raw_polylines[point_id].append(point)
        except:
            raw_polylines[point_id] = [point]
            raw_attributes[point_id] = attributes[count]

            # Keep attributes from first vertex of the polyline, or we could also store all attributes in a list

    # Ensure there are polylines with more than 1 vertex

    new_polylines = []
    new_attributes = []

    for poly_id, polyline in raw_polylines.items():
        if len(polyline) > 1:
            new_polylines.append(polyline)
            new_attributes.append(raw_attributes[poly_id])

    if len(new_polylines) == 0:
        warning("no polylines found")
        return None
    
    return [new_polylines, new_attributes]


def get_segments(polyline):
    number_of_vertices = len(polyline)

    segments = []

    for count in range(1,number_of_vertices):
        p_1 = polyline[count - 1]
        p_2 = polyline[count]

        segments.append([p_1,p_2])

    return segments