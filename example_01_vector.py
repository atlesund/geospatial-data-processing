import geo_2026 as geo

dataset = geo.Vector()

print(dataset)
print(dataset.epsg)
dataset.epsg = 4326
print(dataset.epsg)

print(dataset.coordinates)

