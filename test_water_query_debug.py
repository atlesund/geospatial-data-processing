"""
Debug script for water query issue.

Tests terrain_mesh_from_raster with enable_water_queries=True
to understand what happens when querying OSM water features.
"""

from raster_2026 import Raster
from routing_2026 import terrain_mesh_from_raster
import numpy as np
from unittest.mock import patch

# Load a real .tif file using rasterio
print("Loading terrain raster...")
try:
    import rasterio
    filename = "/Users/dev/Code/School/geospatial-data-processing/data/terrain/6701_50m_33.tif"

    with rasterio.open(filename) as src:
        print(f"File: {filename}")
        print(f"Shape: {src.shape}")
        print(f"CRS: {src.crs}")
        print(f"Transform: {src.transform}")
        print(f"Bounds: {src.bounds}")

        # Create mock raster with real data
        raster = Raster()
        raster._filename = filename

        # Extract affine transform
        affine = [
            src.transform[0],  # a: pixel width
            src.transform[3],  # d: row rotation (column rotation is transform[3])
            src.transform[1],  # b: column rotation (row rotation is transform[1])
            src.transform[4],  # e: pixel height
            src.transform[2],  # c: x_upper_left
            src.transform[5]   # f: y_upper_left
        ]
        raster._world_file = affine
        raster._shape = list(src.shape)

        # Extract EPSG code from CRS
        if src.crs:
            crs_str = str(src.crs)
            if 'EPSG:' in crs_str:
                raster._epsg = int(crs_str.split(':')[1])

        # Load elevation data (first band, small subset for quick test)
        elevation_data = src.read(1)
        # Convert to float32 and handle nodata
        raster._elevation_grid = elevation_data.astype(np.float32)
        if src.nodata is not None:
            raster._elevation_grid[elevation_data == src.nodata] = np.nan

    print(f"\nMock raster created:")
    print(f"  EPSG: {raster._epsg}")
    print(f"  Shape: {raster.shape}")
    print(f"  World file: {raster._world_file}")
    print(f"  Elevation grid shape: {raster._elevation_grid.shape}")

except Exception as e:
    print(f"ERROR loading GeoTIFF: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n=== Testing with small mesh spacing for quick test ===")
print("\nTest 1: terrain_mesh_from_raster with enable_water_queries=False (baseline)")
try:
    # Test without water queries first
    routing_net = terrain_mesh_from_raster(raster, mesh_spacing=200, enable_water_queries=False)
    print(f"Success! Network created with {len(routing_net.graph.nodes)} nodes and {len(routing_net.graph.edges)} edges")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n\nTest 2: terrain_mesh_from_raster with enable_water_queries=True")
try:
    # Test with water queries enabled
    routing_net = terrain_mesh_from_raster(raster, mesh_spacing=200, enable_water_queries=True)
    print(f"Success! Network created with {len(routing_net.graph.nodes)} nodes and {len(routing_net.graph.edges)} edges")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()