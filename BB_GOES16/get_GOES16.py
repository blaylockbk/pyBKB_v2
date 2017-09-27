# Brian Blaylock
# September 22, 2017                I'm getting married in less than a month :)

"""
Functions that return GOES-16 data with latitude and longitude.
Typically works with the multiband formatted files stored on Pando Archive and
NOAA GOES-16 archvie on Amazon.

When plotting the true color image with plt.pcolormesh(), pay attention to the
specifics. 
"""

from datetime import datetime, timedelta
from netCDF4 import Dataset
import numpy as np
from pyproj import Proj
import subprocess


def files_on_pando(DATE):
    """
    Get a list of file in Pando on the DATE requested
    """
    # List files in Pando bucket
    PATH_Pando = 'GOES16/ABI-L2-MCMIPC/%s/' % (DATE.strftime('%Y%m%d'))
    ls = ' ls horelS3:%s | cut -c 11-' % (PATH_Pando)
    rclone_out = subprocess.check_output('rclone ' + ls, shell=True)
    flist = rclone_out.split('\n')
    flist = np.array([l for l in flist if '.nc' in l]) # only include .nc files
    flist.sort()
    return flist

def get_GOES16_truecolor(FILE, only_RGB=False, night_IR=True):
    """
    Uses Channel 1, 2, 3, to create a "True Color" image. 

    Input:
        FILE - name of the netcdf file. Must be the multiband formatted data file.
               i.e. OR_ABI-L2-MCMIPC-M3_G16_s20172651517227_e20172651520000_c20172651520109.nc
        only_RGB - if True, only returns the RGB value, and not the additional details
        night_IR - if True, replaces darkness from night time with IR image
    """
    
    # Open the file
    try:
        C = Dataset(FILE, 'r')
        print "Fetching:", FILE
    except:
        print "Can't open file:", FILE
        return None

    # Load the RGB arrays and apply a gamma correction (square root)
    R = np.sqrt(C.variables['CMI_C02']) # Band 2 is red (0.64 um)
    G = np.sqrt(C.variables['CMI_C03']) # Band 3 is "green" (0.865 um)
    B = np.sqrt(C.variables['CMI_C01']) # Band 1 is blue (0.47 um)

    # "True Green" is some linear interpolation between the three channels
    G_true = 0.48358168 * R + 0.45706946 * B + 0.06038137 * G

    if night_IR == True:
        # Prepare the Clean IR band by converting brightness temperatures to greyscale values
        # From: https://github.com/occ-data/goes16-play/blob/master/plot.py
        cleanir = C.variables['CMI_C13'][:]
        cir_min = 90.0
        cir_max = 313.0
        cleanir_c = (cleanir - cir_min) / (cir_max - cir_min) # normalize array between 0 and 1
        cleanir_c = np.maximum(cleanir_c, 0.0)
        cleanir_c = np.minimum(cleanir_c, 1.0)
        cleanir_c = (1.0 - np.float64(cleanir_c))

        # This method makes some cold cloud tops more white near the day/night boundary.
        cleanir_c = cleanir_c/1.5 # Lower scale of IR: 
                                  # trying to make cold clouds near day/night
                                  # boundary not be changed too much
        RGB = np.dstack([np.maximum(R, cleanir_c), np.maximum(G_true, cleanir_c), np.maximum(B, cleanir_c)])
    
    else:
        # The final RGB array :)
        RGB = np.dstack([R, G_true, B])
    
    # don't need the other file info or processing? 
    if only_RGB:
        return RGB

    # Seconds since 2000-01-01 12:00:00
    add_seconds = C.variables['t'][0]
    DATE = datetime(2000, 1, 1, 12) + timedelta(seconds=add_seconds)

    # Satellite height
    sat_h = C.variables['goes_imager_projection'].perspective_point_height

    # Satellite longitude
    sat_lon = C.variables['goes_imager_projection'].longitude_of_projection_origin

    # Satellite sweep
    sat_sweep = C.variables['goes_imager_projection'].sweep_angle_axis

    # The projection x and y coordinates equals
    # the scanning angle (in radians) multiplied by the satellite height (http://proj4.org/projections/geos.html)
    X = C.variables['x'][:] * sat_h
    Y = C.variables['y'][:] * sat_h

    C.close()

    # map object with pyproj
    p = Proj(proj='geos', h=sat_h, lon_0=sat_lon, sweep=sat_sweep)

    # Convert map points to latitude and longitude with the magic provided by Pyproj
    XX, YY = np.meshgrid(X, Y)
    lons, lats = p(XX, YY, inverse=True)

    # Create a color tuple for pcolormesh
    rgb = RGB[:,:-1,:] # Using one less column is very imporant, else your image will be scrambled! (This is the stange nature of pcolormesh)
    rgb = np.minimum(rgb, 1) # Force the maximum possible RGB value to be 1 (the lowest should be 0).
    colorTuple = rgb.reshape((rgb.shape[0] * rgb.shape[1]), 3) # flatten array, becuase that's what pcolormesh wants.
    colorTuple = np.insert(colorTuple, 3, 1.0, axis=1) # adding an alpha channel will plot faster?? according to stackoverflow.

    return {'TrueColor': RGB,
            'lat': lats,
            'lon': lons,
            'DATE': DATE,
            'Satellite Height': sat_h,
            'lon_0': sat_lon,
            'X': X,
            'Y': Y,
            'rgb_tuple': colorTuple}


if __name__ == '__main__':

    import matplotlib.pyplot as plt
    from mpl_toolkits.basemap import Basemap

    import sys
    sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2/')
    from BB_basemap.draw_maps import draw_CONUS_HRRR_map, draw_Utah_map


    DATE = datetime(2017, 9, 25)
    DIR = '/uufs/chpc.utah.edu/common/home/horel-group/archive/%s/BB_test/goes16/' % DATE.strftime('%Y%m%d')
    
    FILES = files_on_pando(DATE)

    mHRRR = draw_CONUS_HRRR_map()
    mUtah = draw_Utah_map()

    for f in FILES:
        G = get_GOES16_truecolor(DIR+f, nightIR=True)

        # Plot on HRRR domain Map
        plt.figure(1)
        plt.clf(); plt.cla()        
        newmap = mHRRR.pcolormesh(G['LONS'], G['LATS'], G['TrueColor'][:,:,1],
                                color=G['rgb_tuple'],
                                linewidth=0,
                                latlon=True)
        newmap.set_array(None) # must have this line if using pcolormesh and linewidth=0
        mHRRR.drawcoastlines()
        plt.savefig('hrrr_'+G['DATE'].strftime('%Y%m%d_%H%M'))

        # Plot on Utah Map
        plt.figure(2)
        plt.clf(); plt.cla()    
        newmap = mUtah.pcolormesh(G['LONS'], G['LATS'], G['TrueColor'][:,:,1],
                                color=G['rgb_tuple'],
                                linewidth=0,
                                latlon=True)
        newmap.set_array(None) # must have this line if using pcolormesh and linewidth=0
        mUtah.drawstates()   
        plt.savefig('utah_'+G['DATE'].strftime('%Y%m%d_%H%M'))


