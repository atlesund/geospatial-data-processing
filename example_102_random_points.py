import geo_2026 as geo

dataset = geo.Vector()

print(dataset.random_points(500, -180, -90, 180, 90))
print(dataset.epsg)
dataset.epsg = 4326
print(dataset.epsg)

print(dataset.coordinates)

dataset.bounding_box()
print(dataset)