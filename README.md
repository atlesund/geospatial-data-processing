# ENVIRONMENT

```
conda deactivate
conda activate geo
```

# Running files

The file structure is: 

```text
root/
│
├── geo_2026/
│   ├── __init__.py
│   └── vector.py
│
├── examples/
│   └── example_102_random_points.py
│
├── exercises/
└── tests/
```
All examples, exercises and tests uses geo_2026,
so to run files from the project root, run the files as modules. Otherwise they wont be able to access the library we have built:
```bash
python -m examples.example_102_random_points
```

# REFERENCE SYSTEMS

1) Geographic: `Longitude` and `Latitude``
2) Projected: (x,y)

# FORMATS
1) CSV
2) GeoJSON
3) ShapeFile, binary format


# Lat n Lon

Latitude [-90, 90] `phi`
Longitude [-180, 180] `lambda`

# Screen

A window with a screen with rows and columns. Origin is upper left corner. A coordinate system flipped over the x-axis

# Raster- and World file