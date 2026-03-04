import geo_2026 as geo

dataset = geo.Vector()
dataset.random_points(1000, -0.3570, 39.4750, -0.3250, 39.4860)
dataset.add_field('colour', 'orange')
dataset.add_field('distance', 1000)
dataset.add_geometric_fields()
dataset.select_by_circle([-0.3410,39.4810],500, 'haversine')
print(dataset._attributes)
print(dataset)
dataset.calculate('colour', '"red"')

dataset.epsg = 4326
dataset.osm()