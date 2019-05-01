# encoding: utf-8
"""Interfaces with 1km DEM 'global30.bin' file"""

import numpy as np


def open_granule_1km(filename):
    r"""Loads the 1km DEM file into memory"""

    try:
        data = np.fromfile(filename, dtype=np.int16)
        data = data.reshape(18000, 43200).T
    except IOError:
        print filename + ' was not accessed.'
        data = None
    return data


def get_elev_from_1km(lat_, lon_, data_):
    r"""Returns the 1km elevation from the global DEM file"""

    if data_ is None:
        return None

    # It is possiable here to have a bad data_ array slip thru as we don't
    # do any error checking yet.  Once we know what to look for we can add
    # those conditions here
    if lat_ != None and lon_ != None:

        # Catch our known null (or bad) values, this bails out!
        if lat_ == -8888 or lon_ == -8888:
            return -8888

        # Should be 120 pixels per 1 degree (lat/lon)
        pixels = int(120)

        # Find the x-pos and y-pos for lat/lon pair in the DEM.  To do this
        # first we find the fractional degrees in terms of pixels *
        lon_frac = (lon_ - np.floor(lon_)) * pixels
        lon_frac = (lat_ - np.floor(lat_)) * pixels

        xpos = int(((180 + np.floor(lon_)) * pixels) + lon_frac)
        ypos = int(((90 - np.floor(lat_)) * pixels) + lon_frac)

        ## Diagnostic plot
        # import matplotlib.pyplot as plt
        # print ypos, xpos
        # plt.figure(figsize=(10, 10))
        # plt.imshow(data_[::5, ::5], origin="lower")
        # plt.plot(ypos/5, xpos/5, marker='o', color='r', ls='')
        # plt.plot(0, 0, marker='o', color='y', ls='')
        # plt.show()
        ##

        # Pull out the elevation from the DEM and convert to feet.
        if data_[xpos, ypos] != -9999:
            closest_elev = data_[xpos, ypos] * 3.28028
        else:
            # -9999 is the sea flag, i.e. no elevation.
            closest_elev = 0
        return closest_elev
    else:
        return None
