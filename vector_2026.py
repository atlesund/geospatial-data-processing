import utilities_2026 as utilities
import json
import pyproj
from numpy import random
from numpy import linalg
import numbers
import math


class Vector():

    # System methods
    def __init__(self, geometry ='POINT'):
        if geometry.upper() not in ['POINT', 'POLYLINE', 'POLYGON']:
            self._geometry = 'POINT'
        else:
            self._geometry = geometry.upper()

        # Other attributes

        self._source = None
        self._format = None
        self._epsg = None #EPSG code = reference system

        self._coordinates = []
        self._attributes = [] 
        self._bbox = None # Bounding box

        self._selection = None # Selected entities

        self._index = None # Spatial grid index

    def __repr__(self): # called on print
        report = {
            'geometry': self._geometry,
            'source': self._source,
            'format': self._format,
            'epsg': self._epsg,
            'coordinates': len(self._coordinates),
            'attributes':len(self._attributes),
            'bbox': self._bbox,
            'index': self._index
        }

        if self._selection is None:
            report['selected'] = 0
        else:
            report['selected'] = len(self._selection)
        return json.dumps(report, indent=4)



    # Properties 

    def _get_epsg(self):
        return self._epsg

    def _set_epsg(self, epsg_code):
        self._epsg = epsg_code

    epsg = property(fget=_get_epsg, fset=_set_epsg) # Reference system

    def _get_coordinates(self):
        return self._coordinates

    coordinates = property(fget=_get_coordinates)

    def _get_attributes(self):
        return self._attributes

    attributes = property(fget=_get_attributes)

    def _get_fields(self):
        if(len(self._attributes) == 0):
            return
        
        # Assume all records have the same fields

        return list(self._attributes[0].keys())


    fields = property(fget=_get_fields)

    def _get_selection(self):
        return self._selection
    
    selection = property(fget=_get_selection)

    # User methods

    def random_points(self, n, x_min, y_min, x_max, y_max):
        """
        Docstring for random_points
        
        :param self: Description
        :param n: number of radom points
        :params x_min, y_min, x_max, y_max: bounding box 
        """

        # Call utilities

        coordinates, attributes = utilities.random_points(
            n, x_min, y_min, x_max, y_max
        )

        self._source = 'random'
        self._format = 'list'
        self._geometry = 'POINT'
        self._coordinates = coordinates
        self._attributes = attributes

    def bounding_box(self):
        """
        Compute min and max coordinates of dataset
        
        :param self: Description
        """

        # Check that coordinates exist
        if len(self._coordinates) == 0:
            utilities.warning('Coordinates not found!')
            return
        
        if self._geometry == 'POINT':
            
            # Initial values
            x_min, y_min = self.coordinates[0]
            x_max, y_max = self.coordinates[0]

            # Examine all points
            for point in self.coordinates:
                x,y = point

                if x < x_min: x_min = x                    
                elif x > x_max: x_max = x
                if y < y_min: y_min = y
                elif y > y_max: y_max = y

        elif self._geometry == 'POLYLINE':
            x_min, y_min = self.coordinates[0][0]
            x_max, y_max = self.coordinates[0][0]

            for polyline in self.coordinates:
                for point in polyline:
                    x,y = point

                    if x < x_min: x_min = x                    
                    elif x > x_max: x_max = x
                    if y < y_min: y_min = y
                    elif y > y_max: y_max = y


        elif self._geometry == 'POLYGON':
            x_min, y_min = self.coordinates[0][0][0]
            x_max, y_max = self.coordinates[0][0][0]

            for polygon in self.coordinates:
                for part in polygon:
                    for point in part:
                        x,y = point

                        if x < x_min: x_min = x                    
                        elif x > x_max: x_max = x
                        if y < y_min: y_min = y
                        elif y > y_max: y_max = y


        self._bbox = [x_min, y_min, x_max, y_max]

    def add_field(self, field_name, default_value=None):
        """
        Add a new field to the attribute table
        
        :param self: Description
        :param field_name: Description
        :param default_value: Description
        """

        # Check there are data

        if len(self._attributes) == 0:
            utilities.warning('Attributes not found')
            return

        # What to do if field already exists?
        # TODO

        # Add field and value
        for record in self._attributes:
            record[field_name] = default_value

    def add_geometric_fields(self):
        """
        Different behaviour depending on the type of geometry:

        1. POINT: add coordinates x,y
        2. POLYLINE: add length of the polyline
        3. POLYGON: add area, perimeter, centroid, ...
        
        """

        for count, feature in enumerate(self.coordinates):
            if self._geometry == 'POINT':
                x, y = feature

                self._attributes[count]['x'] = x
                self._attributes[count]['y'] = y
            elif self._geometry == 'POLYLINE':
                self._attributes[count]['length'] = utilities.length()
            elif self._geometry == 'POLYGON':
                self._attributes[count]['area'] = utilities.area()
                self._attributes[count]['perimeter'] = utilities.perimeter()
                self._attributes[count]['centroid'] = utilities.centroid()
    
    
    def select(self, expression):
        """
        Select subset of features based on logical/relational expression
        PS! Loops through attributes to evaluate the expression.
        
        :param self: Description
        :param expression: Description
        """

        if len(self._attributes) == 0:
            utilities.warning('Attributes not found')
            return
        
        # Validate expression
        validation = utilities.validate(expression)

        #print(json.dumps(validation, indent = 4))

        if validation['status'] is False:
            utilities.warning(validation['message'])
            return
        
        # Create selection set

        selection = []

        for record_count, record in enumerate(self._attributes):
            values = [] 

            for label in validation['tokens']['label']:
                values.append(record[label])

            # Set variables

            for label_count, label in enumerate(validation['tokens']['label']):
                exec(f'{label} = {values[label_count]}') # Executes some code using f string

            # Evaluate expression DANGER!
            if eval(expression) is True: # eval is evil
                selection.append(record_count)

        # Update selection set

        self._selection = selection


    def calculate(self, target, expression):
        """
        dataset.calculate('colour', '"green"')
        dataset.calculate('size', 'x + 10')
        
        :param self: Description
        :param target: Description
        :param expression: Description
        """

        if len(self._attributes) == 0:
            utilities.warning('No attributes found in current dataset')
            return
        
        validation = utilities.validate(expression)

        # Check status

        if validation['status'] is False:
            utilities.warning(validation['messages'])
            return
        
        # Check labels (fields)

        for label in validation['tokens']['label']:
            if label not in self.fields:
                utilities.warning(f'Field "{label}" not found')
                return
            
        # Records to update

        if self._selection is None:
            # No records selected. If so we will apply the expression to all records
            records = range(len(self._attributes)) # All records

        else:
            records = self._selection

        # Ensure target field exists
        if target not in self.fields:
            self.add_field(target)

        # Calculate field
        for record_count in records:

            values = []
            for label in validation['tokens']['label']:
                values.append(records[label])

            # Set variables 

            for label_count, label in enumerate(validation['tokens']['label']):
                exec(f'{label} = {values[label_count]}')


            # Evaluate calculation
            self._attributes[record_count][target] = eval(expression)
            # Danger!!!



    def clear(self):
        """
        Clear selection set
        """
        self._selection = None

    
    def osm(self):

        """
        Shows geographic data on OpenStreetMap base map
        
        OSM coordinate_index reference system (CRS) is EPSG:4326
        """

        if len(self.coordinates) == 0:
            utilities.warning('No coordinates found')
            return
        
        # Create Layer
        if self._geometry == 'POINT':
            osm_layer = utilities.create_osm_point_layer(self)
        elif self._geometry == 'POLYLINE':
            pass
        elif self._geometry == 'POLYGON':
            pass
        # Draw layer
        
        if osm_layer is not None:
            utilities.show_osm_map([osm_layer])

    def summary(self, key_field, summary_field, operation='average'):

        dict = {}

        # GROUPING ALL VALUES

        if not self._attributes:
            return False
        if not key_field in self._attributes[0]:
            return False

        for attribute in self._attributes:
            key = attribute[key_field]
            if summary_field == 'x':
                dict.setdefault(key, []).append(attribute['x'])
            else:
                dict.setdefault(key, []).append(attribute['y'])

        # APPLYING OPERATION
        for i, list in dict.items():
            if operation == 'average':
                for number in list:
                    if not isinstance(number, numbers.Real):
                        print("Error, there exists a value that is not numeric")
                        return
                    
                avg_value = sum(dict[i]) / len(dict[i])
                dict[i] = avg_value

            if operation == 'sum':
                for number in list:
                    if not isinstance(number, numbers.Real):
                        print("Error, there exists a value that is not numeric")
                        return
                sum_value = sum(dict[i])
                dict[i] = sum_value
            if operation == 'random':
                random_value = random.choice(dict[i])
                dict[i] = float(random_value.round(2))
            if operation == 'count':
                counted_value = len(dict[i])
                dict[i] = counted_value

        print(dict)

    def select_by_rectangle(self, rectangle):
        x_min, y_min, x_max, y_max = rectangle

        self.select(
            f'x > {x_min} and '
            f'x < {x_max} and '
            f'y > {y_min} and '
            f'y < {y_max}'
            )
    def haversine_distance(self, point_a, point_b, radius=6371000):
        """
        Coordinates of point_a and point_b in decimal degrees.
        Earth radius in metres
        Computed distance in metres
        """
        longitude_a, latitude_a = map(math.radians, point_a)
        longitude_b, latitude_b = map(math.radians, point_b)
        delta_latitude = latitude_b - latitude_a
        delta_longitude = longitude_b - longitude_a
        t1 = math.sin(0.5 * delta_latitude)
        t2 = math.cos(latitude_a)
        t3 = math.cos(latitude_b)
        t4 = math.sin(0.5 * delta_longitude)
        a = t1 * t1 + t2 * t3 * t4 * t4
        c = 2.0 * math.asin(min(1.0, math.sqrt(a)))
        distance = radius * c
        return distance
    
    def euclidean_distance(self, point_a, point_b):
        """
        Geographic Euclidean distance (planar approximation).
        Input: (lon, lat) in decimal degrees
        Output: distance in metres
        """
        lon1, lat1 = point_a
        lon2, lat2 = point_b

        # Mean latitude for scaling longitude
        mean_lat = math.radians((lat1 + lat2) / 2.0)

        # Degree differences
        dlon = lon2 - lon1
        dlat = lat2 - lat1

        # Convert degrees → metres
        meters_per_degree = 111_320.0
        dx = dlon * meters_per_degree * math.cos(mean_lat)
        dy = dlat * meters_per_degree

        return math.sqrt(dx * dx + dy * dy)
    
    def manhattan_distance(self, point_a, point_b):
        """
        Geographic Manhattan distance (taxicab distance).
        Input: (lon, lat) in decimal degrees
        Output: distance in metres
        """
        lon1, lat1 = point_a
        lon2, lat2 = point_b

        mean_lat = math.radians((lat1 + lat2) / 2.0)

        dlon = abs(lon2 - lon1)
        dlat = abs(lat2 - lat1)

        meters_per_degree = 111_320.0
        dx = dlon * meters_per_degree * math.cos(mean_lat)
        dy = dlat * meters_per_degree

        return dx + dy
    
    def select_by_circle(self, center, radius, metric='haversine'):
        local_selection = []
        for count, point in enumerate(self._coordinates):
            if metric == 'manhattan':
                dist = self.manhattan_distance(center, point)
            elif metric == "haversine":
                dist = self.haversine_distance(center, point)
            elif metric == 'euclidean':
                dist = self.euclidean_distance(center, point)
            else:
                return("Error, no liable metric provided.")
            if dist < radius:
                local_selection.append(count)
            
        self._selection = local_selection

    def project(self, target_epsg):
        """From origin source CRS to target CRS"""

        if self._epsg is None:
            utilities.warning('Unknown source EPSG code')
            return
        if self._epsg == target_epsg:
            return
        # PYPROJ

        # 1. Define source and target CRSs
        source_crs = pyproj.CRS.from_epsg(self._epsg)
        target_crs = pyproj.CRS.from_epsg(target_epsg)

        # 2. Create Transformer class instance

        projection = pyproj.Transformer.from_crs(
            source_crs, target_crs, always_xy=True, # Order = lon, latitude
        )

        # 3. Transformation

        projected = []
        for entity in self._coordinates:

            if self._geometry == 'POINT':
                entity_projected = utilities.project_point(
                    entity, projection
                )

            elif self._geometry == 'POLYLINE':
                pass              
            elif self._geometry == 'POLYGON':
                pass

            projected.append(entity_projected)

        # 4. Update coordinates and EPSG of current vector instance
        self._coordinates = projected

        self._epsg = target_epsg

    def read_geojson(self, filename=None, multi=False):
        if filename is None:
            filename = utilities.input_file(['geojson'])

        with open(filename, 'rt') as f:
            data = json.load(f)

        if self._geometry == 'POINT':
            coordinates, attributes = utilities.read_geojson_points(data, multi)
        elif self._geometry == 'POLYLINE':
            coordinates, attributes = utilities.read_geojson_polylines(data, multi)
        elif self._geometry == 'POLYGON':
            coordinates, attributes = utilities.read_geojson_polygons(data, multi)

        self._coordinates = coordinates
        self._attributes = attributes
        self._source = filename
        self._format = 'GeoJSON'
        self._epsg = 4326

    def remove(self):
        if len(self._coordinates) == 0 or len(self._attributes) == 0:
            utilities.warning('The instance is empty')
            return

        if self._selection is None:
            utilities.warning('No records selected')
            return

        new_coordinates = []
        new_attributes = []

        for count in range(len(self._coordinates)):
            if count not in self._selection:
                new_coordinates.append(self._coordinates[count])
                new_attributes.append(self._attributes[count])

        self._coordinates = new_coordinates
        self._attributes = new_attributes
        self._selection = None


    def read_shapefile(self, filename=None, encoding='utf-8'):
        if filename is None:
            filename = utilities.input_file(['shp'])

        if filename is None:
            return
        
        if self._geometry == 'POINT':
            report = utilities.read_shapefile_points(filename, encoding)
        elif self._geometry == 'POLYLINE':
            pass
        elif self._geometry == 'POLYGON':
            pass

        # Check if the report contains errors:

        if report['status'] is False:
            utilities.warning(report['message'])
            return
        
        # Update Vector() instance
        self._coordinates = report['coordinates']
        self._attributes = report['attributes']
        self._epsg = report['epsg']
        self._source = filename
        self._format = 'Shapefile'

    def read_csv(self, id_field, x_field, y_field, filename=None, separator=','):
        if filename is None:
            filename = utilities.input_file(['csv'])

        if filename is None:
            return
        
        if self._geometry == 'POINT':
            dataset = utilities.read_csv_points(filename, id_field, x_field, y_field, separator)
        elif self._geometry == 'POLYLINE':
            dataset = utilities.read_csv_polylines(filename, id_field, x_field, y_field, separator)
        elif self._geometry == 'POLYGON':
            pass

        # Check if the report contains errors:
        if dataset is None:
            return
        
        # Update Vector() instance

        coordinates, attributes = dataset

        self._coordinates = coordinates
        self._attributes = attributes
        self._source = filename
        self._format = 'CSV'