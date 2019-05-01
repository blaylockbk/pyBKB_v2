# encoding: utf-8

r"""Package supports working with the STRMv3 data files."""

import ConfigParser
import gzip
from io import BytesIO

import numpy as np
import tifffile


def err_out(err, mode):
    r"""Prints error message to console & logs

    Args:
    err: error output

    TODO:
    1: Add output log support
    """

    if mode is not "silent":
        print "Error '{0}'! Arguments {1}.".format(err.message, err.args)


def get_granule_name(latitude, longitude):
    r"""Returns the granule`s SRTM name

    Args:
    latitude, longitude: whole degree (integer)

    Returns:
    {string}: SRTM granule name
    """

    latitude = float(latitude)
    longitude = float(longitude) - 1

    cardinal = [None] * 2

    # Need to determine the cardinal direction (N,E,S,W)
    if latitude > 0:
        cardinal[0] = 'N'
    else:
        cardinal[0] = 'S'

    if longitude > 0:
        cardinal[1] = 'E'
    else:
        cardinal[1] = 'W'
        longitude = longitude * (-1)

    return cardinal[0] + '%02i' % (latitude) + cardinal[1] + '%03i' % (longitude)


def open_granule_30m(granule):
    r"""Opens 30m SRTMv3 data granule, returns the dataset

    Args:
    granule: granule name, ex: 'N47W110'

    Returns:
    {array}: n-by-n array

    Rasies:
    IOError: An error occurred accessing the SRTMv3 data files
    RuntimeError: General runtime error
    """

    # Create the file path/name for the DEM binary files
    path = '/uufs/chpc.utah.edu/common/home/horel-group4/oper/mesowest/elevation_data/DATASETS/SRTMv3/'
    file_ext = '.tiff.gz'
    file_prefix = 'SRTM1'
    file_suffix = 'V3'
    fullname = path + file_prefix \
               + granule + file_suffix + file_ext


    file_ = gzip.open(fullname, "rb")
    buffer_ = BytesIO(file_.read())
    file_.close()
    tif = tifffile.TiffFile(buffer_)
    data = tif.asarray()

    return data


def get_srtm_30m_elev(lat_, lon_, data_):
    r"""Returns the SRTMv3 30m elevation"""

    # The DEM (SRTMv3) binary files are 1 degree x 1 degree resolution
    # at 30m resolution. I.e. each data point is 1/3600 of the grid.
    # Total size is 3601x3601 with a buffer for each value.
    #
    # We expect an offset of 1/3600 so when we find a
    # granule that does not comply we should know about it.

    # Catch our known null (or bad) values.  This bails out!
    if lat_ == -8888 or lon_ == -8888:
        return -8888

    pixels = 1.0 / (len(data_) - 1)
    # if pixels != (1.0 / 3600.0):
    #     print "! pixels change at " + granule + " " + str(len(data_))

    lat_frac = lat_ - np.floor(lat_)
    lon_frac = lon_ - np.floor(lon_)

    # Find the lat/lon position in the the granule
    xpos = int(round(lon_frac / pixels))
    ypos = 3600 - int(round(lat_frac / pixels))

    try:
        srtm_elev = data_[xpos, ypos]
    except IndexError:
        srtm_elev = -8888

    return srtm_elev
