# Brian Blaylock
# March 21, 2017                                           Spring was yesterday

"""
Get data from a HRRR grib2 file on the MesoWest HRRR S3 Archive

Requires cURL on your linux system
"""


import os
import pygrib
from datetime import date, datetime, timedelta
import urllib2
import ssl
import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import multiprocessing
from scipy.io import netcdf

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
sys.path.append('B:\pyBKB_v2')

from BB_downloads.HRRR_S3 import *
from BB_basemap.draw_maps import draw_CONUS_HRRR_map

timer1 = datetime.now()

DATE = date(2015, 4, 18)
DATE = date(2017, 3, 15)
eDATE = date.today()
days = (eDATE - DATE).days
DATES = np.array([DATE + timedelta(days=x) for x in range(0, days)])

hours = range(0, 24)

variable = 'TMP:2 m'
var_name = "temp_2m"

DATE_LIST = np.array([])

created_NC = False

for h in hours:
    for D in DATES:
        print D, h
        try:
            getDATE = datetime(D.year, D.month, D.day, h)
            H = get_hrrr_variable(getDATE, variable, fxx=0, model='hrrr', field='sfc')
            DATE_LIST = np.append(DATE_LIST, getDATE)
            try:
                new = H['value']
                sumH = sumH + new; count += 1
                maxH[new > maxH] = new[new > maxH]
                minH[new < minH] = new[new < minH]
            except:
                # maxH and minH variables are not assigned yet, so make those.
                # (if you don't copy the variable then the values are shared between max and min
                # for some pythonic reason)
                maxH = H['value'].copy()
                minH = H['value'].copy()
                sumH = H['value'].copy(); count = 1
                if created_NC == False:
                    # And Create NetCDF Dimensions and Variables
                    # Create NetCDF file
                    f = netcdf.NetCDFFile('MaxMinMean_hourly_'+var_name+'.nc', 'w')
                    f.createDimension('x', np.shape(H['value'])[0])
                    f.createDimension('y', np.shape(H['value'])[1])
                    f.createDimension('t', 24)
                    nc_maxH = f.createVariable('max_'+variable, float, ('x', 'y', 't'))
                    nc_minH = f.createVariable('min_'+variable, float, ('x', 'y', 't'))
                    nc_meanH = f.createVariable('mean_'+variable, float, ('x', 'y', 't'))
                    created_NC = True
        except:
            print "hour not available", DATE

    nc_maxH[:, :, h] = maxH
    nc_minH[:, :, h] = minH
    nc_meanH[:, :, h] = sumH/count
    del maxH
    del minH
    del sumH

f.history = 'HRRR Hourly Max/Min Climatology for '+variable


latH =  f.createVariable('latitude', float, ('x', 'y'))
lonH =  f.createVariable('longitude', float, ('x', 'y'))
latH[:] = H['lat']
lonH[:] = H['lon']
f.close()


nc = netcdf.NetCDFFile('MaxMinMean_hourly_temp_2m.nc', 'r')
plt.plot(nc.variables['min_TMP:2 m'][1000,1000,:], label='min')
plt.plot(nc.variables['mean_TMP:2 m'][1000,1000,:], label='mean')
plt.plot(nc.variables['max_TMP:2 m'][1000,1000,:], label='max')
plt.legend()

print "total time:", datetime.now() - timer1