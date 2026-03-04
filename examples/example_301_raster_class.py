import geo_2026 as geo

dataset = geo.Raster()

dataset.epsg = 25830 # UTM coordinates

dataset.read_image()

print(dataset)