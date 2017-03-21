# Brian Blaylock
# March 14, 2017                                           It's Pi Day!! (3.14)

"""
Get data from a HRRR grib2 file on the MesoWest HRRR S3 Archive

Requires cURL on your linux system
"""


import os
import pygrib
from datetime import datetime, timedelta
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

DATE = datetime(2015, 4, 17)
eDATE = datetime.now()

variable = 'WIND:10 m'
var_name = "wind_10m"
DATE_LIST = np.array([])

while DATE <= eDATE:
    print DATE
    try:
        H = get_hrrr_variable(DATE, variable, fxx=0, model='hrrr', field='sfc')
        DATE_LIST = np.append(DATE_LIST, DATE)
        try:
            sumH = H['value'] + sumH
        except:
            # sumH variable isn't assigned yet
            sumH = H['value']
    except:
        print "hour not available", DATE

    DATE += timedelta(hours=1)


# Calculate the average of H
average_H = sumH/float(len(DATE_LIST))


f = netcdf.netcdf_file('average_'+var_name+'.nc', 'w')
f.history = 'HRRR Climatology for '+variable

f.createDimension('x', np.shape(average_H)[0])
f.createDimension('y', np.shape(average_H)[1])

meanH = f.createVariable(variable, float, ('x', 'y'))
latH =  f.createVariable('latitude', float, ('x', 'y'))
lonH =  f.createVariable('longitude', float, ('x', 'y'))
meanH[:] = average_H
latH[:] = H['lat']
lonH[:] = H['lon']
f.close()


DATE_LIST = np.genfromtxt('dates_hrrr_wind.txt', dtype=None, delimiter='\n')

nc = netcdf.NetCDFFile('average_wind_10m.nc', 'r')
meanWind = nc.variables['WIND:10 m'].data
lat = nc.variables['latitude'].data
lon = nc.variables['longitude'].data

m = draw_CONUS_HRRR_map()
x, y = m(lon, lat)
m.drawcoastlines()
m.drawcountries()
m.drawstates()
m.pcolormesh(x, y, meanWind, cmap='plasma_r', vmin=3.5, vmax=10.5)
cb = plt.colorbar(orientation='horizontal', shrink=.9, pad=.05, extend='both')
cb = set_label('Average 10 m Wind Speed (m/s)')
cb.set_label(r'Wind Speed (ms$\mathregular{^{-1}}$)')
plt.title('HRRR Average Wind Speed')
plt.xlabel(str(DATE_LIST[0]) +' - '+str(DATE_LIST[-1]))
plt.savefig('hrrr_avg_wind.png', bbox_inches='tight', dpi=1000)

