# Brian Blaylock
# March 21, 2017                                           Spring was yesterday

"""
Find basic statistics (max, min, mean, percentiles) for the CONUS between
two dates, from the MesoWest HRRR S3 archive.
Stats separated by hour, saved in a NetCDF file.
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
import psutil

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
sys.path.append('B:\pyBKB_v2')

from BB_downloads.HRRR_S3 import *
from BB_basemap.draw_maps import draw_CONUS_HRRR_map

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
    print getthisDATE
    H = get_hrrr_variable(getthisDATE, variable, fxx=0, model='hrrr', field='sfc', value_only=True, verbose=False)
    return H['value']

var_dict = {'temp2m':{'variable':'TMP:2 m',
                      'name':'temp_2m',
                      'title':'2-m Temperature',
                      'units':'(C)',
                      'range': [-40, 40],
                      'cmap':'Spectral_r',
                      'offset':273.15},
            'wind10m':{'variable': 'WIND:10 m',
                       'name': "wind_10m",
                       'title': '10-m Wind Speed',
                       'units': r'Wind Speed (ms$\mathregular{^{-1}}$)',
                       'range': [0, 20],
                       'cmap':'plasma_r',
                       'offset': 0},
            'dwpt2m':{'variable':'DPT:2 m',
                      'name':'DPT_2m',
                      'title':'2-m Dew Point',
                      'units':'(C)',
                      'range': [-30, 30],
                      'cmap':'BrBG',
                      'offset':273.15},
            'mslp':{'variable':'mean sea level',
                    'name':'MSLP',
                    'title':'Mean Sea Level Pressure',
                    'units':'Pressure (hPa)',
                    'range': [972, 1050],
                    'cmap':'Blues_r',
                    'offset':0},
            'lightning':{'variable':'LTNG:',
                         'name':'Lightning',
                         'title':'Lightning',
                         'units':'(unknown))',
                         'range': [0, 8],
                         'cmap':'magma_r',
                         'offset':0},
            'gust10m':{'variable':'GUST:surface',
                       'name':'Gust',
                       'title':'Surface Wind Gust',
                       'units':r'Wind Speed (ms$\mathregular{^{-1}}$)',
                       'range': [0, 30],
                       'cmap':'plasma_r',
                       'offset':0},
            'CIN':{'variable':'CIN:surface',
                   'name':'CIN',
                   'title':'Surface CIN',
                   'units':r'(Jkg$\mathregular{^{-1}}$)',
                   'range': [-1000, 0],
                   'cmap':'PuRd',
                   'offset':0},
            'CAPE':{'variable':'CAPE:surface',
                    'name':'CAPE',
                    'title':'Surface CAPE',
                    'units':r'(Jkg$\mathregular{^{-1}}$)',
                    'range': [0, 8000],
                    'cmap':'YlOrBr',
                    'offset':0},
            'snow':{'variable':'SNOD:surface',
                    'name':'Snow_Depth',
                    'title':'Snow Depth',
                    'units':'m',
                    'range': [0, 1],
                    'cmap':'GnBu',
                    'offset':0}}


timer1 = datetime.now()

DATE = date(2015, 4, 18)
eDATE = date.today()

# Test dates...
#DATE = date(2016, 12, 1)
#eDATE = DATE + timedelta(days=30)

days = (eDATE - DATE).days
DATES = [DATE + timedelta(days=x) for x in range(0, days)]

#V = 'temp2m'

for V in var_dict:

    variable = var_dict[V]['variable']
    var_name = var_dict[V]['name']+'_TEST'
    var_title = var_dict[V]['title']
    var_units = var_dict[V]['units']
    vrange = var_dict[V]['range']
    cmap = var_dict[V]['cmap']
    offset = var_dict[V]['offset']

    print "\n", variable, var_name, var_title, var_units

    # The NetCDF file we want to create hasn't been made yet
    created_NC = False

    # multiprocessing :)
    cpu_count = multiprocessing.cpu_count() - 1

    # Hours to get
    hours = range(24)

    timer_hours = []
    timer_chunks = []
    timer_dwnld = []
    timer_numpy = []
    mem_percent = []
    mem_used = []
    size_result = []


    for h in hours:
        try:
            del sumH
            del maxH
            del minH
            del perH
        except:
            pass

        print "\nWork on hour:", h
        mem_percent.append(psutil.virtual_memory().percent)
        mem_used.append(psutil.virtual_memory().free)
        timerH = datetime.now()
        # Iniitialize the arrays with the first date (if you don't copy the
        # variable then the values are shared between max and min
        # for some pythonic reason)
        firstDATE = DATES[0]
        H = get_HRRR(datetime(firstDATE.year, firstDATE.month, firstDATE.day, h))
        maxH = H['value'].copy()
        minH = H['value'].copy()
        sumH = H['value'].copy(); count = 1

        # Create the NetCDF file if it hasn't been created yet
        if created_NC is False:
            f = netcdf.NetCDFFile('MP_MaxMinMean_hourly_'+var_name+'.nc', 'w')
            f.createDimension('x', np.shape(H['value'])[0])
            f.createDimension('y', np.shape(H['value'])[1])
            f.createDimension('t', 24)  # Hours
            f.createDimension('d', 1)   # Date
            f.createDimension('p', 6)   # Percentile categories
            nc_maxH = f.createVariable('max_'+variable, float, ('x', 'y', 't'))
            nc_minH = f.createVariable('min_'+variable, float, ('x', 'y', 't'))
            nc_meanH = f.createVariable('mean_'+variable, float, ('x', 'y', 't'))
            nc_count = f.createVariable('count', 'i', ('t'))
            nc_perC = f.createVariable('percent_compute', 'i', ('p'))
            nc_perH = f.createVariable('percentile', float, ('p', 'x', 'y', 't'))
            created_NC = True

        # Process DATES in chunks with multiprocessing. Each chunk of DATES will
        # be processed on the number of processors we are allowed.
        # We do this in chunks so we don't return all the data at once, loading
        # everything into memory. So just load arrays from each chunk, thus saving
        # memory :) The majority of the time processing is in downloading, anyways,
        # not the numpy functions.
        # ## Still need an efficient way to compute percentiles (90th, 95th, 99th)
        # If you have lots of memory, go ahead and set i_have_lots_of_memory to
        # more than 1, else, set it to 1, which chunks the data based on the num of
        # processors you are allowing.
        # Number of days in a chunk = i_have_lots_of_memory * cpu_count
        i_have_lots_of_memory = 24
        chunks = range(len(DATES))[1::cpu_count*i_have_lots_of_memory]
        chunks.append(len(DATES))
        chunks = [0, len(DATES)]
        for i in range(len(chunks)-1):
            timerC = datetime.now()

            # The chunk of dates the processors will work on for this loop
            chunk_DATES = DATES[chunks[i]:chunks[i+1]]

            # Add the hour to each date, and pass datetime object to multipro
            chunk_DATETIMES = [datetime(D.year, D.month, D.day, h) for D in chunk_DATES]
            timerD = datetime.now()
            p = multiprocessing.Pool(cpu_count)
            result = p.map(get_HRRR_value, chunk_DATETIMES)
            print "got multiprocessing data...",
            p.close()
            print "closed processors"
            timer_dwnld.append(datetime.now()-timerD)

            # Remove empty arrays if any exist
            print "remove empty arrays...",
            #empty = [e for e in range(len(result)) if result[e] is None]
            #if len(empty) > 0:
            #    offset = range(len(empty))
            #    for E in range(len(empty)):
            #        # adjust by the offset, becuase pop changes index number
            #        result.pop(empty[E]-offset[E])
            result = [x for x in result if x is not None]
            print "done!"

            print "convert result to numpy array...",
            result = np.array(result)
            size_result.append(result.nbytes)
            print "done!"

            timerN = datetime.now()
            # Percentiles, if the entire hour was calculated in the same results
            if len(chunk_DATES) >= len(DATES):
                timerP = datetime.now()
                # remember to consider the first hour, currently in minH/maxH/sumH
                print "calculate percentiles..."
                ALL = np.vstack([[minH], result])
                percentiles = [1, 5, 10, 90, 95, 99]
                perH = np.percentile(ALL, percentiles, axis=0)
                print 'done!'
                timeP = datetime.now() - timerP

            # Use numpy arrays to find max, min, sum
            # First find min, max, sum of the result array
            minR = np.min(result, axis=0)
            maxR = np.max(result, axis=0)
            sumR = np.sum(result, axis=0)

            # Then, combine the result array to the previous (this two step
            # process is faster than doing a np.dstack before finding min/max/sum)
            minH = np.min([minR, minH], axis=0)
            maxH = np.max([maxR, maxH], axis=0)
            sumH = np.sum([sumR, sumH], axis=0); count += np.shape(result)[0]
            timer_numpy.append(datetime.now() - timerN)
            timer_chunks.append(datetime.now() - timerC)

        nc_maxH[:, :, h] = maxH
        nc_minH[:, :, h] = minH
        nc_meanH[:, :, h] = sumH/count
        nc_count[h] = count
        if 'perH' in locals().keys():
            nc_perC[:] = percentiles
            nc_perH[:, :, :, h] = perH

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
    print "mean numpy (seconds):", np.mean([i.seconds + i.microseconds/1000000. for i in timer_numpy])

"""!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
For 30 days of data (without percentiles):
    CPUs = 30
    ChunkSize = 30            (cpu_count * i_have_lots_of_memory)
    total time: 0:01:15.466156
        mean hour (seconds): 2.67458229167
        mean chunk (seconds): 1.799924625
        mean dwnld (seconds): 1.46710783333
    (remaining time in set up and saving the NetCDF file)
Thus, most of the time is taken in downloading.

For ~2 years of data, and i_have_lots_of_memory==6
    total time: 0:13:43.555768
        mean hour (seconds): 33.8404787917
        mean chunk (seconds): 8.18831652083
        mean dwnld (seconds): 6.49187252083

For ~2 years of data, and i_have_lots_of_memory==12
    total time: 0:14:05.679720
        mean hour (seconds): 34.63923225
        mean chunk (seconds): 16.6543909792
        mean dwnld (seconds): 13.3053043333

For ~2 years of data, and i_have_lots_of_memory==24
    total time: 0:17:19.317700
        mean hour (seconds): 42.7128093333
        mean chunk (seconds): 41.4714707917
        mean dwnld (seconds): 34.268950625
        mean numpy (seconds): 4.32911054167
        Memory per hour 27 %

For ~2 Years of data, and i_have_lots_of_memory==24, and compute percentiles:
    total time: 0:35:58.816907
        mean hour (seconds): 88.5667959583
        mean chunk (seconds): 87.21266875
        mean dwnld (seconds): 28.030954
        mean numpy (seconds): 4.25179025

For ~2 Years of data, and i_have_lots_of_memory==24, and compute percentiles:
For 9 variables
    total time: 6:35:06.746097
        mean hour (seconds): 209.145321208
        mean chunk (seconds): 206.485765292
        mean dwnld (seconds): 131.370061125
        mean numpy (seconds): 7.230093875

    !!!32 Trillion Values for one variable, for each hour, for two years!!!

    max memory used: 78%, 30 GB
    min memory used: 52%,  8 GB  
    max, min "result" size: 10.8 GB, 10.7
    

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"""





#==============================================================================
# Hourly Plots

def plot_P(inputs):
    """
    Plot the different percentages for each hour
    """
    V = inputs[0] # variable
    m = inputs[1] # map object
    h = inputs[2] # hour (UTC)
    #
    variable = var_dict[V]['variable']
    var_name = var_dict[V]['name']+'_TEST'
    var_title = var_dict[V]['title']
    var_units = var_dict[V]['units']
    vrange = var_dict[V]['range']
    cmap = var_dict[V]['cmap']
    offset = var_dict[V]['offset']
    #
    SAVE = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/PhD/HRRR/percentile/%s/' % (var_name)
    if not os.path.exists(SAVE):
        # make the SAVE directory
        os.makedirs(SAVE)
        # then link the photo viewer
        photo_viewer = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/Brian_Blaylock/photo_viewer/photo_viewer.php'
        os.link(photo_viewer, SAVE+'photo_viewer.php')
    #
    nc = netcdf.NetCDFFile('MP_MaxMinMean_hourly_'+var_name+'.nc', 'r')
    Ps = [1, 5, 10, 90, 95, 99]
    lat = nc.variables['latitude'].data
    lon = nc.variables['longitude'].data
    x, y = m(lon, lat)
    #
    cb_ranges = True
    #
    for i in range(len(Ps)):
        plt.figure(i+h)
        plt.clf()
        plt.cla()
        m.drawcoastlines()
        m.drawcountries()
        m.drawstates()
        if V == "mslp":
            P = nc.variables['percentile'][i,:,:,h] / 100
        else:
            P = nc.variables['percentile'][i,:,:,h]-offset
        if cb_ranges is True:
            m.pcolormesh(x, y, P, cmap=cmap, vmin=vrange[0], vmax=vrange[1])
        else:
            m.pcolormesh(x, y, P, cmap=cmap)
        plt.title('HRRR %s %02d percentile (UTC: %02d)' % (var_title, Ps[i], h))
        cb = plt.colorbar(orientation='horizontal', shrink=.9, pad=.05)
        cb.set_label('%s %s' % (var_title, var_units))
        plt.xlabel(str(DATES[0]) +' - '+str(DATES[-1]))
        print 'Hour:', h, 'Percentile:', Ps[i]
        plt.savefig(SAVE+'hrrr_%s_%02dth_h%02d.png' % (var_name, Ps[i], h), bbox_inches='tight', dpi=300)

def plot_MMM(inputs):
    """
    Plot the min, max, mean, for each hour
    """
    V = inputs[0]
    m = inputs[1] # map object
    h = inputs[2] # hour (UTC)
    S = inputs[3] # statistic, [max, min, or mean]
    #
    variable = var_dict[V]['variable']
    var_name = var_dict[V]['name']+'_TEST'
    var_title = var_dict[V]['title']
    var_units = var_dict[V]['units']
    vrange = var_dict[V]['range']
    cmap = var_dict[V]['cmap']
    offset = var_dict[V]['offset']
    #
    SAVE = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/PhD/HRRR/%s/%s/' % (S, var_name)
    if not os.path.exists(SAVE):
        # make the SAVE directory
        os.makedirs(SAVE)
        # then link the photo viewer
        photo_viewer = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/Brian_Blaylock/photo_viewer/photo_viewer.php'
        os.link(photo_viewer, SAVE+'photo_viewer.php')
    #
    nc = netcdf.NetCDFFile('MP_MaxMinMean_hourly_'+var_name+'.nc', 'r')
    Ps = [1, 5, 10, 90, 95, 99]
    lat = nc.variables['latitude'].data
    lon = nc.variables['longitude'].data
    x, y = m(lon, lat)
    #
    cb_ranges = True
    #
    plt.figure(h)
    plt.clf()
    plt.cla()
    m.drawcoastlines()
    m.drawcountries()
    m.drawstates()
    if V == "mslp":
        P = nc.variables[S+'_'+variable][:,:,h] / 100
    else:
        P = nc.variables[S+'_'+variable][:,:,h]-offset
    #
    if cb_ranges is True:
        m.pcolormesh(x, y, P, cmap=cmap, vmin=vrange[0], vmax=vrange[1])
    else:
        m.pcolormesh(x, y, P, cmap=cmap)
    #
    plt.title('HRRR %s %s (UTC: %02d)' % (var_title, S, h))
    cb = plt.colorbar(orientation='horizontal', shrink=.9, pad=.05)
    cb.set_label('%s %s' % (var_title, var_units))
    plt.xlabel(str(DATES[0]) +' - '+str(DATES[-1]))
    plt.savefig(SAVE+'hrrr_%s_%s_h%02d.png' % (var_name, S, h), bbox_inches='tight', dpi=300)

v = 'lightning'

m = draw_CONUS_HRRR_map()
num_cpu = multiprocessing.cpu_count()

# Plot Percentiles
inputs = [[v, m, i] for i in range(24)]
p = multiprocessing.Pool(num_cpu)
p.map(plot_P, inputs)
p.close()

# Plot Max, Min, Mean
inputs = [[v, m, i, j] for i in range(24) for j in ['max', 'min', 'mean']]
p = multiprocessing.Pool(num_cpu)
p.map(plot_MMM, inputs)
p.close()
#==============================================================================


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