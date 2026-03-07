import geo_2026 as geo

# Extract the features from the geojson files:
filenames = geo.utilities.multiple_input_files()
# Use filenames to extract information through our newly created merge_geojson function

outputfilename = 'merged.geojson'

geo.utilities.merge_geojson(filenames, outputfilename)
