
import json
import tkinter

import utilities_2026 as utilities
import numpy as np


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
        if self._photoimage is None:
            return None
        
        rows = self._photoimage.height()
        columns = self._photoimage.width()

        return [rows, columns]

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
        filename = utilities.input_file(['png'])

        if filename is None:
            return

        # Update Raster() instance

        self._photoimage = tkinter.PhotoImage(file=filename)
        self._filename = filename

        # World file
        world_file = utilities.read_world_file(filename)
        self._world_file = world_file

        # Load elevation grid using Pillow for terrain analysis
        from PIL import Image
        try:
            self._elevation_grid = np.array(Image.open(filename))
        except Exception as e:
            self._elevation_grid = None
            utilities.warning(f'Failed to load elevation grid: {e}')