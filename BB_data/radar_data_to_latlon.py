# Brian Blaylock
# Version 2 update
# 17 November 2016

"""
The MetPy package makes it possible to read raw radar level 2 and level 3 data
files, but it doesn't convert the radar "grid" to the latitude and longitude
coordinate system. These functions use MetPy to read in radar data following
the instuctions in their doc, then it converts that data to a latitude and
longitude grid for plotting on a basemap.

More info:
http://metpy.readthedocs.io/en/latest/examples/generated/NEXRAD_Level_3_File.html
http://kbkb-wx-python.blogspot.com/2016/07/plotting-radar-data-with-metpy-pyproj.html
"""

# There was a bug in the MetPy package for reading TDWR radar data, which hash
# been fixed and available in new releases, but I have a fixed version here:
import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
from MetPy_BB.io.nexrad import Level3File
from MetPy_BB.io.nexrad import Level2File
from MetPy_BB.plots import ctables


# Used to convert range/azimuth to lat/lon
from pyproj import Geod
import numpy as np
from numpy import ma

def level3_radar_to_latlon(FILE):
    """
    Open a radar level 3 .nids file (such as from a TDWR) with MetPy, read the
    data as a numpy array, and calculate the latitude and longitude for each
    observation so you can plot the radar data on a basemap.

    Input:
        FILE - The path and filename of the radar file you wish to open.

    Outpu:
    """

    # Open the TDWR with MetPy and extract the data we want.
    f = Level3File(FILE)
    datadict = f.sym_block[0][0]

    # Some of the stuff going on in MetPy is strange, but I'm confident this
    # maps the radar data to floats with units of m/s for radial velocity.
    data = f.map_data(datadict['data'])
    data = ma.array(data)
    data[np.isnan(data)] = ma.masked

    # Grab azimuths and calculate a range based on number of gates
    az = np.array(datadict['start_az'] + [datadict['end_az'][-1]])
    rng = np.linspace(0, f.max_range, data.shape[-1] + 1)

    # Convert azimuth (az) and range (rng) to a latitutde and longitude.
    g = Geod(ellps='clrk66') # This is the type of ellipse the earth is
                             # projected on. There are other types of ellipses,
                             # but the differences are small.
    center_lat = np.ones([len(az), len(rng)])*f.lat
    center_lon = np.ones([len(az), len(rng)])*f.lon
    az2D = np.ones_like(center_lat)*az[:, None]
    rng2D = np.ones_like(center_lat)*np.transpose(rng[:, None])*1000
    lon, lat, back = g.fwd(center_lon, center_lat, az2D, rng2D)

    # Convert azimuth and range to x,y
    # Use these variables if don't want to plot on a basemap.
    # The value represents range from the radar.
    xlocs = rng * np.sin(np.deg2rad(az[:, np.newaxis]))
    ylocs = rng * np.cos(np.deg2rad(az[:, np.newaxis]))

    return_this = {'FILE' : FILE,
                   'data' : data,
                   'LON' : lon,
                   'LAT' : lat,
                   'x' : xlocs,
                   'y' : ylocs}

    return return_this


def level2_radar_to_latlon(FILE, sweep=0):
    """
    NEXRAD Level 2 data is quite a bit different than TDWR data.
    Download from Amazon Web Service
    https://s3.amazonaws.com/noaa-nexrad-level2/index.html
    Download URL Example:
    https://noaa-nexrad-level2.s3.amazonaws.com/2016/08/05/KCBX/KCBX20160805_205859_V06

    Use the Local Version of python on Meso3 or Meso4: /usr/local/bin/python

    Input:
        File - the path and file name of the radar scan
        variable - the variable you want to get (deafult is radial velocity).
                   Accepted variables (that I know of):
                   'REF','RHO','PHI','ZDR','SW','VEL'
                   Reflectivity, RHO?, PHI?, ZDR, SW?, Radial Velocity

    """
    f = Level2File(FILE)
    rLAT = f.sweeps[0][0][1].lat  # Radar latitude
    rLON = f.sweeps[0][0][1].lon  # Radar longitude
    rDT = f.dt # Date in local time (I think)

    # Choose a sweep. Sweep reprsents the scan elevation angle (Note: sweep
    # number is not necessarily in order of lowest to highest scan. To get the
    # elevation angle try: f.sweeps[x][0][0].el_angle where x is your sweep
    # index.
    elevation_angle = f.sweeps[sweep][0][0].el_angle

    # Azimuth Agnle: found in the first item of "ray" which is a header.
    az = np.array([ray[0].az_angle for ray in f.sweeps[sweep]])

    return_this = {'FILE' : FILE,
                   'radar_lat' : rLAT,
                   'radar_lon' : rLON,
                   'DATE' : rDT,
                   'elevation_angle' : elevation_angle}

    # Grab the range and data for the available variables
    for VAR in f.sweeps[sweep][0][4].keys():
        var_header = f.sweeps[sweep][0][4][VAR][0]
        var_range = (np.arange(var_header.num_gates + 1) - 0.5) \
                * var_header.gate_width + var_header.first_gate
        var_data = np.array([ray[4][VAR][1] for ray in f.sweeps[sweep]])

        # Turn into an array, then mask
        data = ma.array(var_data)
        data[np.isnan(data)] = ma.masked

        #rngs = np.array([ray[0].rad_length for ray in f.sweeps[sweep]])  # ??
        rng = np.linspace(0, var_range[-1], data.shape[-1] + 1)

        # Convert azimuth (az) and range (rng) to a latitutde and longitude.
        g = Geod(ellps='clrk66') # This is the type of ellipse the earth is
                                # projected on. There are other types,
                                # but the differences are small.
        center_lat = np.ones([len(az), len(rng)])*rLAT
        center_lon = np.ones([len(az), len(rng)])*rLON
        az2D = np.ones_like(center_lat)*az[:, None]
        rng2D = np.ones_like(center_lat)*np.transpose(rng[:, None])*1000
        lon, lat, back = g.fwd(center_lon, center_lat, az2D, rng2D)

        # Convert az,range to x,y
        xlocs = var_range * np.sin(np.deg2rad(az[:, np.newaxis]))
        ylocs = var_range * np.cos(np.deg2rad(az[:, np.newaxis]))

        # Latitude and Longitude data is unique to the variable.
        return_this[VAR+'_DATA'] = data
        return_this[VAR+'_LON'] = lon
        return_this[VAR+'_LAT'] = lat
        return_this[VAR+'_x'] = xlocs
        return_this[VAR+'_y'] = ylocs

    return return_this


if __name__ == "__main__":

    # Test a TDWR radar file
    tdwr = '/uufs/chpc.utah.edu/common/home/horel-group4/gslso3s/data/TDWR/20161116/TV0/Level3_SLC_TV0_20161116_1130.nids'
    a = level3_radar_to_latlon(tdwr)

    nexrad = '/uufs/chpc.utah.edu/common/home/u0553130/python_scripts/NEXRAD_II/KCBX20160805_205859_V06'
    b = level2_radar_to_latlon(nexrad, variable='REF')
