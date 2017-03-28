# Brian Blaylock
# March 21, 2017                                           Spring was yesterday

"""
Find the max, min, and mean for the CONUS between two dates, from the 
MesoWest HRRR S3 archive. Separated by hour, saved in a NetCDF file.
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

#DATE = date(2016, 12, 1)
#eDATE = DATE + timedelta(days=30)

days = (eDATE - DATE).days
DATES = [DATE + timedelta(days=x) for x in range(0, days)]


variable = 'TMP:2 m'
var_name = "temp_2m_TEST"
var_title = '2-m Temperature'
var_units = '(C)'
vrange = [-30, 40]
cmap = 'Spectral_r'
offset = 273.15

#variable = 'WIND:10 m'
#var_name = "wind_10m"
#var_title = '10-m Wind Speed'
#var_units = r'Wind Speed (ms$\mathregular{^{-1}}$)'
#vrange = [0, 15]
#cmap = 'plasma_r'
#offset = 0

#variable = 'DPT:2 m'
#var_name = "DPT_2m"
#var_title = '2-m Dew Point'
#var_units = 'Dew Point (C)'
#vrange = [-30, 30]
#cmap = 'BrBG'
#offset = 273.15

#variable = 'mean sea level'
#var_name = "MSLP"
#var_title = 'Mean Sea Level Pressure'
#var_units = 'Pressure (hPa)'
#vrange = [972, 1050]
#cmap = 'Blues_r'
#offset = 0

#variable = 'LTNG:'
#var_name = "Lightning"
#var_title = 'Lightning'
#var_units = r'Wind Speed (ms$\mathregular{^{-1}}$)'
#vrange = [0, 20]
#cmap = 'magma_r'
#offset = 0

#variable = 'GUST:surface'
#var_name = "Gust"
#var_title = 'Surface Wind Gust'
#var_units = r'Wind Speed (ms$\mathregular{^{-1}}$)'
#vrange = [0, 15]
#cmap = 'plasma_r'
#offset = 0

#variable = 'CIN:surface'
#var_name = "CIN"
#var_title = 'Surface CIN'
#var_units = r'(Jkg$\mathregular{^{-1}}$)'
#vrange = [0, 15]
#cmap = 'PuRd'
#offset = 0

#variable = 'SNOD:surface'
#var_name = "Snow_Depth"
#var_title = 'Snow Depth'
#var_units = 'm'
#vrange = [0, 10]
#cmap = 'GnBu'
#offset = 0

# The NetCDF file we want to create hasn't been made yet
created_NC = False

# multiprocessing :)
cpu_count = multiprocessing.cpu_count() - 1

# Hours to get
hours = range(0, 24)

timer_hours = []
timer_chunks = []
timer_dwnld = []

# we want to distribute chunks of data between the processors
def get_HRRR(getthisDATE):
    """
    Getting HRRR data
    """
    H = get_hrrr_variable(getthisDATE, variable, fxx=0, model='hrrr', field='sfc')
    return H

def get_HRRR_value(getthisDATE):
    """
    Getting HRRR data, just return the value
    """
    H = get_hrrr_variable(getthisDATE, variable, fxx=0, model='hrrr', field='sfc', value_only=True)
    return H['value']

for h in hours:
    timerH = datetime.now()
    # Iniitialize the arrays with the first date
    firstDATE = DATES[0]
    H = get_HRRR(datetime(firstDATE.year, firstDATE.month, firstDATE.day, h))
    maxH = H['value'].copy()
    minH = H['value'].copy()
    sumH = H['value'].copy(); count = 1

    # Create the NetCDF file if it hasn't been created yet
    if created_NC == False:
        f = netcdf.NetCDFFile('MP_MaxMinMean_hourly_'+var_name+'.nc', 'w')
        f.createDimension('x', np.shape(H['value'])[0])
        f.createDimension('y', np.shape(H['value'])[1])
        f.createDimension('t', 24)
        f.createDimension('d', 1)
        nc_maxH = f.createVariable('max_'+variable, float, ('x', 'y', 't'))
        nc_minH = f.createVariable('min_'+variable, float, ('x', 'y', 't'))
        nc_meanH = f.createVariable('mean_'+variable, float, ('x', 'y', 't'))
        nc_count = f.createVariable('count', 'i', ('t'))
        created_NC = True

    # Process DATES in chunks on all the specified processors.
    chunks = range(len(DATES))[1::cpu_count]
    chunks.append(len(DATES))
    for i in range(len(chunks)-1):
        timerC = datetime.now()
        chunk_DATES = DATES[chunks[i]:chunks[i+1]]

        # Add the hour to each date, and pass datetime object to multipro
        chunk_DATETIMES = [datetime(D.year, D.month, D.day, h) for D in chunk_DATES]
        timerD = datetime.now()
        p = multiprocessing.Pool(cpu_count)
        result = p.map(get_HRRR_value, chunk_DATETIMES)
        p.close()
        timer_dwnld.append(datetime.now()-timerD)

        # Remove empty arrays if any exist
        empty = [e for e in range(len(result)) if result[e] is None]
        if len(empty) > 0:
            offset = range(len(empty))
            for E in range(len(empty)):
                # adjust by the offset, becuase pop changes index number
                result.pop(empty[E]-offset[E])

        result = np.array(result)

        # Use numpy arrays to find max, min, sum
        # First find min, max, sum of the result array
        minR = np.min(result, axis=0)
        maxR = np.max(result, axis=0)
        sumR = np.sum(result, axis=0)

        # Then, combine the result array to the previous (this two step
        # process is faster than doing a np.dstack before finding min/max/sum)
        minH = np.min([minR, minH], axis=0)
        maxH = np.max([maxR, maxH], axis=0)
        sumH = np.sum([minR, sumH], axis=0); count += np.shape(result)[0]

        timer_chunks.append(datetime.now() - timerC)

    nc_maxH[:, :, h] = maxH
    nc_minH[:, :, h] = minH
    nc_meanH[:, :, h] = sumH/count
    nc_count[h] = count
    del maxH
    del minH
    del sumH
    timer_hours.append(datetime.now() - timerH)

f.history = 'HRRR Hourly Max/Min/Mean Climatology for '+variable

latH = f.createVariable('latitude', float, ('x', 'y'))
lonH = f.createVariable('longitude', float, ('x', 'y'))
latH[:] = H['lat']
lonH[:] = H['lon']
begD = f.createVariable('Begin Date', 'i', ('d'))
endD = f.createVariable('End Date', 'i', ('d'))
begD[:] = int(DATES[0].strftime('%Y%m%d%H'))
endD[:] = int(DATES[-1].strftime('%Y%m%d%H'))

f.close()

print "==========================================================="
print "total time:", datetime.now() - timer1
print ""
print "mean hour (seconds):", np.mean([i.seconds + i.microseconds/1000000. for i in timer_hours])
print "mean chunk (seconds):", np.mean([i.seconds + i.microseconds/1000000. for i in timer_chunks])
print "mean dwnld (seconds):", np.mean([i.seconds + i.microseconds/1000000. for i in timer_dwnld])

"""!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
For 30 days of data:
    total time: 0:01:15.466156
        mean hour (seconds): 2.67458229167
        mean chunk (seconds): 1.799924625
        mean dwnld (seconds): 1.46710783333
    (remaining time in set up and saving the NetCDF file)
Thus, most of the time is taken in downloading.
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"""

"""
#==============================================================================
# plots
# =============================================================================

SAVE = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/PhD/HRRR/climo/'
if not os.path.exists(SAVE):
    # make the SAVE directory
    os.makedirs(SAVE)
    # then link the photo viewer
    photo_viewer = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/Brian_Blaylock/photo_viewer/photo_viewer.php'
    os.link(photo_viewer, SAVE+'photo_viewer.php')

nc = netcdf.NetCDFFile('MP_MaxMinMean_hourly_'+var_name+'.nc', 'r')
ncT = netcdf.NetCDFFile('MP_MaxMinMean_hourly_temp_2m.nc', 'r')

plt.figure(1)
plt.plot(nc.variables['min_'+variable][1000,1000,:], label='min')
plt.plot(nc.variables['mean_'+variable][1000,1000,:], label='mean')
plt.plot(nc.variables['max_'+variable][1000,1000,:], label='max')
plt.legend()

if var_name == "MSLP":
    # Max and Min, get straight from the NC file
    maxV = np.max(nc.variables['max_'+variable][:],axis=2) / 100
    minV = np.max(nc.variables['min_'+variable][:],axis=2) / 100

    # Grand Mean (mean of means) error is small if the counts are close for each hour
    meanV = np.mean(nc.variables['mean_'+variable][:],axis=2) / 100
else:
    # Max and Min, get straight from the NC file
    maxV = np.max(nc.variables['max_'+variable][:],axis=2) - offset
    minV = np.max(nc.variables['min_'+variable][:],axis=2) - offset

    # Grand Mean (mean of means) error is small if the counts are close for each hour
    meanV = np.mean(nc.variables['mean_'+variable][:],axis=2) - offset

# If you dont' want any error in the mean,
# need to backtrack the sum from the average and count to recalculate the average
hourCounts = nc.variables['count'][:]
hourSums = nc.variables['mean_'+variable][:] * hourCounts
sumV = np.sum(hourSums, axis=2)
#meanV = sumV/np.sum(hourCounts)
## But we will assume the counts are very close

lat = nc.variables['latitude'].data
lon = nc.variables['longitude'].data


m = draw_CONUS_HRRR_map()
x, y = m(lon, lat)

# Mean
plt.figure(10)
m.drawcoastlines()
m.drawcountries()
m.drawstates()
m.pcolormesh(x, y, meanV, cmap=cmap, vmax=.3048)
cb = plt.colorbar(orientation='horizontal', shrink=.9, pad=.05)
cb.set_label('%s %s' % (var_title, var_units))
plt.title('HRRR Mean '+var_title)
plt.xlabel(str(DATES[0]) +' - '+str(DATES[-1]))
plt.savefig(SAVE+'hrrr_'+var_name+'_mean.png', bbox_inches='tight', dpi=500)

# Max
plt.figure(20)
m.drawcoastlines()
m.drawcountries()
m.drawstates()
m.pcolormesh(x, y, maxV, cmap=cmap, vmax=1)
cb = plt.colorbar(orientation='horizontal', shrink=.9, pad=.05)
cb.set_label('%s %s' % (var_title, var_units))
plt.title('HRRR Max '+var_title)
plt.xlabel(str(DATES[0]) +' - '+str(DATES[-1]))
plt.savefig(SAVE+'hrrr_'+var_name+'_max.png', bbox_inches='tight', dpi=500)

# Min
plt.figure(30)
m.drawcoastlines()
m.drawcountries()
m.drawstates()
m.pcolormesh(x, y, minV, cmap=cmap)
cb = plt.colorbar(orientation='horizontal', shrink=.9, pad=.05)
cb.set_label('%s %s' % (var_title, var_units))
#m.contour(x, y, minV, colors='blue', levels=[0]) # add freezing line
plt.title('HRRR Min '+var_title)
plt.xlabel(str(DATES[0]) +' - '+str(DATES[-1]))
plt.savefig(SAVE+'hrrr_'+var_name+'_min.png', bbox_inches='tight', dpi=500)
"""

"""
# Temperature Range
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

# Lightning sum 
plt.figure(10)
m.drawcoastlines()
m.drawcountries()
m.drawstates()
m.pcolormesh(x, y, sumV, cmap=cmap, vmax=100)
cb = plt.colorbar(orientation='horizontal', extend="max", shrink=.9, pad=.05)
cb.set_label('%s %s' % (var_title, var_units))
plt.title('HRRR Sum '+var_title)
plt.xlabel(str(DATES[0]) +' - '+str(DATES[-1]))
plt.savefig(SAVE+'hrrr_'+var_name+'_sum.png', bbox_inches='tight', dpi=500)

"""