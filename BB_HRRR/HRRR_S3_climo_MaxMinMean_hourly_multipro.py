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
eDATE = date.today()
days = (eDATE - DATE).days
DATES = [DATE + timedelta(days=x) for x in range(0, days)]

hours = range(0, 24)


#variable = 'TMP:2 m'
#var_name = "temp_2m"
#var_title = '2-m Temperature'
#var_units = '(C)'
#vrange = [-30,40]
#cmap = 'Spectral_r'
#offset = 273.15

#variable = 'WIND:10 m'
#var_name = "wind_10m"
#var_title = '10-m Wind Speed'
#var_units = r'Wind Speed (ms$\mathregular{^{-1}}$)'
#vrange = [0,15]
#cmap = 'plasma_r'
#offset = 0

variable = 'DPT:2 m'
var_name = "DPT_2m"
var_title = '2-m Dew Point'
var_units = r'Dew Point (C)'
vrange = [-10,30]
cmap = 'BrBG'
offset = 273.15

DATE_LIST = np.array([])

# The NetCDF file we want to create hasn't been made yet
created_NC = False

# multiprocessing :)
cpu_count = multiprocessing.cpu_count() - 1

# we want to distribute chunks of data between the processors

def get_HRRR(getthisDATE):
    """
    Getting HRRR data
    """
    print getthisDATE
    H = get_hrrr_variable(getthisDATE, variable, fxx=0, model='hrrr', field='sfc')
    return H


for h in hours:
    # Iniitialize the arrays with the first date
    firstDATE = DATES[0]
    H = get_HRRR(datetime(firstDATE.year, firstDATE.month, firstDATE.day, h))
    maxH = H['value'].copy()
    minH = H['value'].copy()
    sumH = H['value'].copy(); count = 1

    # Create the NetCDF file if it hasn't been created yet
    if created_NC == False:
        # And Create NetCDF Dimensions and Variables
        f = netcdf.NetCDFFile('MP_MaxMinMean_hourly_'+var_name+'.nc', 'w')
        f.createDimension('x', np.shape(H['value'])[0])
        f.createDimension('y', np.shape(H['value'])[1])
        f.createDimension('t', 24)
        f.createDimension('date', 1)
        nc_maxH = f.createVariable('max_'+variable, float, ('x', 'y', 't'))
        nc_minH = f.createVariable('min_'+variable, float, ('x', 'y', 't'))
        nc_meanH = f.createVariable('mean_'+variable, float, ('x', 'y', 't'))
        created_NC = True

    chunks = range(len(DATES))[1::cpu_count]
    chunks.append(len(DATES))
    for i in range(len(chunks)-1):
        chunk_DATES = DATES[chunks[i]:chunks[i+1]]
        # Add the hour to each datetime
        chunk_DATETIMES = [datetime(D.year, D.month, D.day, h) for D in chunk_DATES]
        p = multiprocessing.Pool(cpu_count)
        result = p.map(get_HRRR, chunk_DATETIMES)
        p.close()

        for G in result:
            if G['value'] != None:
                new = G['value']
                maxH[new > maxH] = new[new > maxH]
                minH[new < minH] = new[new < minH]
                sumH = sumH + new; count += 1

    nc_maxH[:, :, h] = maxH
    nc_minH[:, :, h] = minH
    nc_meanH[:, :, h] = sumH/count
    del maxH
    del minH
    del sumH

f.history = 'HRRR Hourly Max/Min/Mean Climatology for '+variable

latH =  f.createVariable('latitude', float, ('x', 'y'))
lonH =  f.createVariable('longitude', float, ('x', 'y'))
latH[:] = H['lat']
lonH[:] = H['lon']
begD = f.createVariable('Begin Date', 'i', ('date'))
endD = f.createVariable('End Date', 'i', ('date'))
begD[:] = int(DATES[0].strftime('%Y%m%d%H'))
endD[:] = int(DATES[-1].strftime('%Y%m%d%H'))

# Number of hours used to calculate the mean for each hour
f.close()
print "total time:", datetime.now() - timer1

#==============================================================================
# plot
# =============================================================================

SAVE = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/PhD/HRRR/climo/'
if not os.path.exists(SAVE):
    # make the SAVE directory
    os.makedirs(SAVE)
    # then link the photo viewer
    photo_viewer = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/Brian_Blaylock/photo_viewer/photo_viewer.php'
    os.link(photo_viewer, SAVE+'photo_viewer.php')

nc = netcdf.NetCDFFile('MP_MaxMinMean_hourly_'+var_name+'.nc', 'r')

plt.figure(1)
plt.plot(nc.variables['min_'+variable][1000,1000,:], label='min')
plt.plot(nc.variables['mean_'+variable][1000,1000,:], label='mean')
plt.plot(nc.variables['max_'+variable][1000,1000,:], label='max')
plt.legend()


maxV = np.max(nc.variables['max_'+variable][:],axis=2) - offset
minV = np.max(nc.variables['min_'+variable][:],axis=2) - offset
meanV = np.mean(nc.variables['mean_'+variable][:],axis=2) - offset
lat = nc.variables['latitude'].data
lon = nc.variables['longitude'].data


m = draw_CONUS_HRRR_map()
x, y = m(lon, lat)

plt.figure(10)
m.drawcoastlines()
m.drawcountries()
m.drawstates()
m.pcolormesh(x, y, meanV, cmap=cmap, vmin=vrange[0], vmax=vrange[1])
cb = plt.colorbar(orientation='horizontal', shrink=.9, pad=.05, extend='both', ticks=range(-30,41,10))
cb.set_label('%s %s' % (var_title, var_units))
plt.title('HRRR Average '+var_title)
plt.xlabel(str(DATES[0]) +' - '+str(DATES[-1]))
plt.savefig(SAVE+'hrrr_'+var_name+'_mean.png', bbox_inches='tight', dpi=500)

plt.figure(20)
m.drawcoastlines()
m.drawcountries()
m.drawstates()
m.pcolormesh(x, y, maxV, cmap=cmap, vmin=vrange[0], vmax=vrange[1])
cb = plt.colorbar(orientation='horizontal', shrink=.9, pad=.05, extend='both', ticks=range(-30,41,10))
cb.set_label('%s %s' % (var_title, var_units))
plt.title('HRRR Max '+var_title)
plt.xlabel(str(DATES[0]) +' - '+str(DATES[-1]))
plt.savefig(SAVE+'hrrr_'+var_name+'_max.png', bbox_inches='tight', dpi=500)

plt.figure(30)
m.drawcoastlines()
m.drawcountries()
m.drawstates()
m.pcolormesh(x, y, minV, cmap=cmap, vmin=vrange[0], vmax=vrange[1])
cb = plt.colorbar(orientation='horizontal', shrink=.9, pad=.05, extend='both', ticks=range(-30,41,10))
cb.set_label('%s %s' % (var_title, var_units))
#m.contour(x, y, minV, colors='blue', levels=[0]) # add freezing line
plt.title('HRRR Min '+var_title)
plt.xlabel(str(DATES[0]) +' - '+str(DATES[-1]))
plt.savefig(SAVE+'hrrr_'+var_name+'_min.png', bbox_inches='tight', dpi=500)

"""
plt.figure(40)
m.drawcoastlines()
m.drawcountries()
m.drawstates()
m.pcolormesh(x, y, maxV-minV, cmap=cmap, vmin=0, vmax=70)
cb = plt.colorbar(orientation='horizontal', shrink=.9, pad=.05, ticks=range(0,71,10))
cb.set_label(r'$\Delta$T %s' % (var_units))
plt.title('HRRR '+var_title+' range')
plt.xlabel(str(DATES[0]) +' - '+str(DATES[-1]))
plt.savefig(SAVE+'hrrr_'+var_name+'_range.png', bbox_inches='tight', dpi=500)
"""