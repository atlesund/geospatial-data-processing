#import pyproj
#pyproj.CRS.from_epsg(4326) -> useful way of checking if the epsg is correct or not

import geo_2026 as geo

dataset = geo.Vector()

dataset.random_points(500, 727500, 4373000, 730000, 4374500) # Units in UTM are meters

#dataset.epsg = 4326 # This is wrong
dataset.epsg = 25830 # UTM zone 30 in meters

"""print(dataset.coordinates[0])
print(dataset)


dataset.project(4326) # From the UTM to geographic coordinates (in degrees)

print(dataset.coordinates[0])
print(dataset)"""

dataset.osm()


# In Example 110 we: 
# UTM ---{using the project method}----> Geographic ---{using the OSM method}---> print points on the OSM map