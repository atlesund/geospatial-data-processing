import geo_2026 as geo

dataset = geo.Vector()

dataset.random_points(500, -180, -90, 180, 90)
dataset.add_geometric_fields()
dataset.add_field('quadrant')

for attribute in dataset.attributes:
    attribute['quadrant'] = {
        (True, True): 1,
        (False, True): 2,
        (False, False): 3,
        (True, False): 4,
    }[(attribute['x'] >= 0, attribute['y'] >= 0)]

dataset.summary('quadrant', 'y', 'count')


## NOTES

# dataset.fields gives the attribute keys that exists.
# dataset.attributes gives all the attributes:
# [
# {'fid': 37, 'colour': 'red', 'x': 104.64638875618749, 'y': -22.031979039614228}, 
# {'fid': 38, 'colour': 'red', 'x': 119.17897663136938, 'y': 77.1060875614333},
# ]

# dataset.add_geometric_fields() assigns the coordinates as attributes (WHY?)

# dataset.select('credentials')
# dataset.selection() returns the current selection

