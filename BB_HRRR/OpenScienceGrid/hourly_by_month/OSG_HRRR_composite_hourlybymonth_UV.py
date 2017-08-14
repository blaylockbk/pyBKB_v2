# Brian Blaylock
# July 27, 2017                     Rachel and I are getting married in October

"""
Find basic statistics (max, min, mean, percentiles) for the CONUS between
two dates, from the MesoWest HRRR S3 archive.
Stats separated by hour, saved in a NetCDF file.
"""

import os
import pygrib
from datetime import datetime, timedelta
import urllib2
import ssl
import re
import numpy as np
import multiprocessing
from scipy.io import netcdf
from netCDF4 import Dataset
import sys

from HRRR_S3 import get_hrrr_variable

# we want to distribute chunks of data between the processors
def get_HRRR(getthisDATE):
    """
    Getting HRRR data
    """
    U = get_hrrr_variable(getthisDATE, variable, fxx=fxx, model='hrrr', field='sfc')
    V = get_hrrr_variable(getthisDATE, variable, fxx=fxx, model='hrrr', field='sfc')
    return H{'lat':U['lat'],
             'lon':V['lon'],
             'value':np.sqrt(U['value']**2+V['value']**2)}

def get_HRRR_value(getthisDATE):
    """
    Getting HRRR data, just return the value (not the latitude and longitude)
    """
    print getthisDATE
    U = get_hrrr_variable(getthisDATE, variable, fxx=fxx, model='hrrr', field='sfc', value_only=True, verbose=False)
    V = get_hrrr_variable(getthisDATE, variable, fxx=fxx, model='hrrr', field='sfc', value_only=True, verbose=False)
    return H{'value':np.sqrt(U['value']**2 + V['value']**2)}

start_timer = datetime.now()


# =============================================================================
# Input arguments (dates should represents the valid time)
variable = sys.argv[1].replace('_', ' ') # omit the U or V. Example: GRD:700 or GRD:10 m 
month = int(sys.argv[2])
hour = int(sys.argv[3])
fxx = int(sys.argv[4])
sDATE = datetime(2015, 4, 18, hour)
eDATE = datetime(2017, 8, 1, hour)
# =============================================================================
print variable, month, hour, fxx
# Range of dates for the desired Hour and Month (e.g. all 0100 UTC for the month of January)
# request dates is the file we want from the Pando archive, an we will account
# for the offset with the fxx argument.
validDATES = np.array([sDATE + timedelta(days=x) for x in range(0, (eDATE-sDATE).days) if (sDATE+timedelta(days=x)).month == month])
requestDATES = np.array([d-timedelta(hours=fxx) for d in validDATES])

# Fix the variable name for saving purposes
var_name = variable.replace(':', '_').replace(' ', '_')

# The NetCDF file we want to create hasn't been made yet
created_NC = False

# multiprocessing :)
cpu_count = multiprocessing.cpu_count()

# Iniitialize the arrays with the first date 
# (For some pythonic reason, if you don't copy the variable then the values are
#  shared between max and min for some pythonic reason)

# Get Latitude and Longitude (same for every file)
U, V = get_HRRR(requestDATES[0])
lat = U['lat'].copy()
lon = U['lon'].copy()

# Create the NetCDF file if it hasn't been created yet
if created_NC is False:
    f = Dataset('OSG_HRRR_%s_m%02d_h%02d_f%02d.nc' % (var_name, month, hour, fxx), 'w')
    f.createDimension('x', np.shape(H['value'])[0])
    f.createDimension('y', np.shape(H['value'])[1])
    f.createDimension('d', 1)   # Date
    f.createDimension('D', 16)   # Date
    f.createDimension('T', 14)   # Timer
    f.createDimension('p', 6)   # Percentile categories
    nc_count = f.createVariable('count', 'i', ('d'), zlib=True, complevel=1)
    nc_cores = f.createVariable('cores', 'i', ('d'), zlib=True, complevel=1)
    nc_timer = f.createVariable('timer', 'c', ('T'), zlib=True, complevel=1) # 'c' if for character, T is the dimension which has 14 characters
    nc_maxH = f.createVariable('max_'+var_name, float, ('x', 'y'), zlib=True, complevel=1)
    nc_minH = f.createVariable('min_'+var_name, float, ('x', 'y'), zlib=True, complevel=1)
    nc_meanH = f.createVariable('mean_'+var_name, float, ('x', 'y'), zlib=True, complevel=1)
    nc_perC = f.createVariable('percent_compute', 'i', ('p'), zlib=True, complevel=1)
    nc_perH = f.createVariable('percentile', float, ('p', 'x', 'y'), zlib=True, complevel=1)
    created_NC = True

"""
Process DATES in chunks with multiprocessing. Each chunk of DATES will
be processed on the number of processors we are allowed.
We do this in chunks so we don't return all the data at once, loading
everything into memory. So just load arrays from each chunk, thus saving
memory :) The majority of the time processing is in downloading, anyways,
not the numpy functions.
Still need an efficient way to compute percentiles (90th, 95th, 99th)
"""

# Add the hour to each date, and pass datetime object to multipro
p = multiprocessing.Pool(cpu_count)
result = p.map(get_HRRR_value, requestDATES)
print "got multiprocessing data...",
p.close()
print "closed processors"

# Remove empty arrays if any exist
print "remove empty arrays...",
result = [x for x in result if x is not None]
print "done!"

# Convert result to numpy array
print "convert result to numpy array...",
result = np.array(result)
print "done!"

# Calculate Statistics
# Percentiles: remember to consider the first hour, currently in minH/maxH/sumH
print "calculate percentiles..."

percentiles = [1, 5, 10, 90, 95, 99]
perH = np.percentile(result, percentiles, axis=0)
print 'done!'

# Use numpy arrays to find max, min, sum
# First find min, max, sum of the result array
minH = np.min(result, axis=0)
maxH = np.max(result, axis=0)
sumH = np.sum(result, axis=0)
count = len(result)

timer = datetime.now() - start_timer

# Store values in the NetCDF file
nc_maxH[:, :] = maxH
nc_minH[:, :] = minH
nc_meanH[:, :] = sumH/count
nc_count[:] = count
nc_cores[:] = cpu_count
nc_timer[:] = ('%s') % timer

nc_perC[:] = percentiles
nc_perH[:, :, :] = perH

f.history = 'HRRR Hourly Max/Min/Mean Climatology for %s, Month: %s, Hour:%s, fxx:%s' % (var_name, month, hour, fxx)

latH = f.createVariable('latitude', float, ('x', 'y'), zlib=True, complevel=1)
lonH = f.createVariable('longitude', float, ('x', 'y'), zlib=True, complevel=1)
latH[:] = H['lat']
lonH[:] = H['lon']

begD = f.createVariable('Begin Date', 'c', ('D'), zlib=True, complevel=1)
endD = f.createVariable('End Date', 'c', ('D'), zlib=True, complevel=1)
begD[:] = validDATES[0].strftime('%Y-%m-%d-%H:00')
endD[:] = validDATES[-1].strftime('%Y-%m-%d-%H:00')

f.close()
