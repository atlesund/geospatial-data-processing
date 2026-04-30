
import json
import os
import tempfile
import tkinter

import numpy as np
import rasterio
from PIL import Image

import utilities_2026 as utilities

class Raster():
    def __init__(self):
        self._filename = None
        self._epsg = None # Identifies a coordinate reference system (CRS)
        self._photoimage = None # Tkinter image format
        self._world_file = None
        self._elevation_grid = None

    def __repr__(self):
        report = {
            'filename': self._filename,
            'epsg': self._epsg,
            'world': self._world_file
        }
        return json.dumps(report, indent=4)

    # Properties

    def _get_epsg(self):
        return self._epsg

    def _set_epsg(self, epsg_code):
        self._epsg = epsg_code

    epsg = property(fget=_get_epsg, fset=_set_epsg) # Reference system

    def _get_shape(self):
        # Try PhotoImage first (for PNG files)
        if self._photoimage is not None:
            rows = self._photoimage.height()
            columns = self._photoimage.width()
            return [rows, columns]

        # Fall back to elevation grid dimensions (for GeoTIFF)
        if self._elevation_grid is not None:
            return list(self._elevation_grid.shape)

        return None

    shape = property(fget=_get_shape)

    def get_elevation_at(self, world_x, world_y):
        """
        Get elevation value at world coordinates (x, y).

        Uses world file affine transformation to convert world coordinates
        to pixel indices, then retrieves elevation from grid.

        Args:
            world_x: X coordinate in the raster's EPSG coordinate system
            world_y: Y coordinate in the raster's EPSG coordinate system

        Returns:
            Elevation value from grid, or None if outside bounds or grid not loaded
        """
        if self._elevation_grid is None or self._world_file is None:
            return None

        pixel_width, row_rotation, col_rotation = self._world_file[0:3]
        pixel_height = self._world_file[3]
        x_upper_left, y_upper_left = self._world_file[4:6]

        # Inverse affine transformation to map world -> pixel
        # Coordinate order from terrain_mesh_from_raster: lines 250-251
        # x = x_upper_left + col * pixel_width + row * col_rotation
        # y = y_upper_left + row * pixel_height + col * row_rotation
        # Solve for col, row:
        col = int((world_x - x_upper_left) // pixel_width)
        row = int((world_y - y_upper_left) // pixel_height)

        rows, cols = self.shape
        if 0 <= row < rows and 0 <= col < cols:
            return float(self._elevation_grid[row, col])
        return None

    # User method

    def read_image(self):
        """
        Load a georeferenced image file (PNG with world file or GeoTIFF).

        Supports:
        - PNG files with separate world file (.wld, .tfw, etc.)
        - GeoTIFF files (.tif, .tiff) with embedded georeferencing

        For GeoTIFF: Uses rasterio to extract affine transform and CRS metadata.
        For PNG: Uses tkinter.PhotoImage and reads world file via utilities.
        """
        filename = utilities.input_file(['png', 'tif', 'tiff'])

        if filename is None:
            return

        self._filename = filename

        # Try GeoTIFF format first (has embedded metadata)
        if filename.lower().endswith(('.tif', '.tiff')):
            self._read_geotiff(filename)
        else:
            # Fall back to PNG with separate world file
            self._read_png_with_worldfile(filename)

    def _read_geotiff(self, filename):
        """
        Read GeoTIFF file with embedded georeferencing metadata.

        Extracts:
        - Affine transform (pixel ↔ world coordinates)
        - EPSG code (coordinate reference system)
        - Elevation data as numpy array

        Args:
            filename: Path to GeoTIFF file
        """
        try:
            with rasterio.open(filename) as src:
                # Extract affine transform coefficients
                # rasterio Affine object is (a, b, c, d, e, f)
                # World file format is [a, d, b, e, c, f]:
                #   a = pixel width
                #   d = row rotation (typically 0)
                #   b = column rotation (typically 0)
                #   e = pixel height (typically negative for north-up rasters)
                #   c = x_upper_left
                #   f = y_upper_left


                affine = [
                    src.transform[0],  # a: pixel width
                    src.transform[3],  # d: row rotation (column rotation is transform[3])
                    src.transform[1],  # b: column rotation (row rotation is transform[1])
                    src.transform[4],  # e: pixel height
                    src.transform[2],  # c: x_upper_left
                    src.transform[5]   # f: y_upper_left
                ]
                print(f"DEBUG: world_file (affine) = {affine}")
                self._world_file = affine

                # Extract EPSG code from CRS. Use rasterio's CRS helpers rather
                # than parsing str(src.crs), because GDAL/rasterio versions can
                # represent the same CRS differently across machines.
                if src.crs:
                    self._epsg = src.crs.to_epsg()
                    if self._epsg is None:
                        authority = src.crs.to_authority()
                        if authority and authority[0].upper() == 'EPSG':
                            self._epsg = int(authority[1])
                else:
                    self._epsg = None

                # Load elevation data (first band)
                # Convert to float32 for mathematical operations
                elevation_data = src.read(1)
                # To make it compatible with NaN
                self._elevation_grid = elevation_data.astype(np.float32)

                # Handle nodata values - replace with NaN for consistency
                if src.nodata is not None:
                    self._elevation_grid[elevation_data == src.nodata] = np.nan

            # Create PhotoImage for tkinter display
            self._photoimage = self._convert_elevation_to_photoimage(self._elevation_grid)

            print(f'Loaded GeoTIFF: {filename}')
            print(f'  EPSG: {self._epsg}')
            print(f'  Bounds: {self._world_file[4]}, {self._world_file[5]} to '
                  f'{self._world_file[4] + self._world_file[0]*self.shape[1]}, '
                  f'{self._world_file[5] + self._world_file[3]*self.shape[0]}')
            print(f'  Resolution: {abs(self._world_file[0])}m x {abs(self._world_file[3])}m per pixel')

        except Exception as e:
            self._elevation_grid = None
            self._world_file = None
            utilities.warning(f'Failed to load GeoTIFF: {e}')

    def _read_png_with_worldfile(self, filename):
        """
        Read PNG file with separate world file.

        Args:
            filename: Path to PNG file
        """
        # Load image using tkinter
        self._photoimage = tkinter.PhotoImage(file=filename)

        # Read world file
        world_file = utilities.read_world_file(filename)
        if world_file is None:
            utilities.warning('No world file found. Coordinate transformation unavailable.')
        else:
            self._world_file = world_file

        try:
            self._elevation_grid = np.array(Image.open(filename))
        except Exception as e:
            self._elevation_grid = None
            utilities.warning(f'Failed to load elevation grid: {e}')

    def _convert_elevation_to_photoimage(self, elevation_grid):
        """
        Convert elevation array to tkinter PhotoImage for display.

        Applies a grayscale color mapping: low elevation = dark, high = bright.

        Args:
            elevation_grid: 2D numpy array of elevation values

        Returns:
            tkinter.PhotoImage instance
        """
        # Handle NaN values for display with boolean masking
        valid_mask = ~np.isnan(elevation_grid)
        valid_elevations = elevation_grid[valid_mask]

        if len(valid_elevations) == 0:
            # All NaN - create black image
            valid_elevations = np.array([0, 1])

        # Normalize elevation to 0-255 range for display
        elev_min = np.min(valid_elevations)
        elev_max = np.max(valid_elevations)
        elev_range = elev_max - elev_min

        if elev_range == 0:
            # Flat terrain - all mid-gray
            normalized = np.full_like(elevation_grid, 128)
        else:
            normalized = 255 * (elevation_grid - elev_min) / elev_range
            normalized[~valid_mask] = 0  # NaN = black

        normalized = np.clip(normalized, 0, 255).astype(np.uint8)

        # Create RGB array (grayscale)
        rgb_array = np.stack([normalized, normalized, normalized], axis=-1)

        # Convert to PhotoImage
        # Note: tkinter.PhotoImage doesn't accept numpy arrays directly
        # Save to temporary file and load
        img = Image.fromarray(rgb_array, mode='RGB')

        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            img.save(tmp_path)
            photo = tkinter.PhotoImage(file=tmp_path)
            os.unlink(tmp_path)  # Clean up temp file
            return photo
        except Exception as e:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            utilities.warning(f'Failed to create PhotoImage: {e}')
            return None
