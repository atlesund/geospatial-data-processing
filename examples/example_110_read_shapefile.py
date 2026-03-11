import geo_2026 as geo


dataset = geo.Vector()

dataset.read_shapefile()

dataset.osm()

print(dataset)