import geo_2026 as geo

dataset = geo.Vector(geometry='POLYGON')
dataset.read_geojson()
print(dataset)
