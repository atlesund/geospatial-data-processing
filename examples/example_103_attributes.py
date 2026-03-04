import geo_2026 as geo

dataset = geo.Vector()

dataset.random_points(500, -180, -90, 180, 90)

print(dataset.attributes)
print(dataset.fields)

dataset.add_field('colour', 'red')

dataset.add_geometric_fields()
print(dataset.attributes)
print(dataset.fields)

print(dataset.selection)
dataset.select('x < 0.0 and y > 0.0')
print(dataset.selection)
print(dataset)

# Calculate

dataset.calculate('colour', '"blue"')

print(dataset.attributes)
print(dataset.fields)