
import json
import tkinter

import utilities_2026 as utilities


class Raster():
    def __init__(self):
        self._filename = None
        self._epsg = None
        self._photoimage = None # Tkinter image format
        self._world_file = None

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
        pass

    shape = property(fget=_get_shape)

    # User method

    def read_image(self):
        filename = utilities.input_file(['png'])

        if filename is None:
            return
        
        # Update Raster() instance

        self._photoimage = tkinter.PhotoImage(file=filename)
        self._filename = filename

        # World file world file world file world file world file world file world file world file world file