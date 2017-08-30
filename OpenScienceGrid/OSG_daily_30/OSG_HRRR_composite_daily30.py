# Brian Blaylock
# August 29, 2017                      I need to buy lightbulbs for the vanity

"""
Calculate basic 30-day (+15/-15 days of center day) mean and percentiles for
the CONUS between two dates from the Pando HRRR archive. 
New file is created for each hour, saved as a HDF5 file.
"""

import os
from datetime import datetime, timedelta
import numpy as np
import multiprocessing
import h5py
import sys

from HRRR_S3 import get_hrrr_variable

# we want to distribute chunks of data between the processors
def get_HRRR(getthisDATE):
    """
    Getting HRRR data
    """
    H = get_hrrr_variable(getthisDATE, variable, fxx=fxx, model='hrrr', field='sfc')
    return H

def get_HRRR_value(getthisDATE):
    """
    Getting HRRR data, just return the value (not the latitude and longitude)
    """
    print getthisDATE
    H = get_hrrr_variable(getthisDATE, variable, fxx=fxx, model='hrrr', field='sfc', value_only=True, verbose=False)
    if H['value'] is None:
        print "!! WARNING !! COULD NOT GET", getthisDATE
    return H['value']

# Begin a timer for the calculations
start_timer = datetime.now()

# =============================================================================
# Input arguments (dates should represents the valid time)
variable = sys.argv[1].replace('_', ' ')
month = int(sys.argv[2])
day = int(sys.argv[3])
hour = int(sys.argv[4])
fxx = int(sys.argv[5])

# Archvie Date Range
sDATE = datetime(2015, 4, 18, hour)
eDATE = datetime(2017, 8, 1, hour)

# List percentiles you want
percentiles = [0, 1, 2, 3, 4, 5, 10, 25, 33, 50, 66, 75, 90, 95, 96, 97, 98, 99, 100]

# Create the separate latlon hdf5 file?
create_latlon_h5 = True
# =============================================================================

# Fix the variable name for saving purposes
var_name = variable.replace(':', '_').replace(' ', '_')

# Range of dates for the desired Month, Hour, and Day 
# (e.g. all 0100 UTC for 15 days before and after the 6th day of the month of January)
# requestDATES is the file we want from the Pando archive, and we will account
# for the offset with the fxx argument.
years = range(sDATE.year, eDATE.year+1)
validDATES = []
for y in years:
    try:
        centerDATE = datetime(y, month, day, hour)
        print datetime(y, month, day, hour), '    fxx:', fxx
    except:
        print 'Not a valid date: datetime(%s, %s, %s, %s)' % (y, month, day, hour)
        continue
    begin = centerDATE-timedelta(days=15)
    end = centerDATE+timedelta(days=15)
    chunk = [begin+timedelta(days=x) for x in range(0,(end-begin).days) if begin+timedelta(days=x) > sDATE]
    validDATES += chunk
requestDATES = np.array([d-timedelta(hours=fxx) for d in validDATES])

# =============================================================================
# =============================================================================
if len(requestDATES) != 0:
    # Multiprocessing :) Get field of each item in list requestDATES
    cpu_count = multiprocessing.cpu_count()
    p = multiprocessing.Pool(cpu_count)
    result = p.map(get_HRRR_value, requestDATES)
    print "got multiprocessing data...",
    p.close()
    print "closed processors"

    # Remove empty arrays that may exist (None arrays exist if the HRRR file couldn't be downloaded from Pando)
    print "remove empty arrays..."
    result = np.array([x for x in result if x is not None])
    print "done!"

    # Calculate Statistics:
    # Percentiles
    print "calculate percentiles..."
    perH = np.percentile(result, percentiles, axis=0)
    print 'done!'

    # Mean
    print "calculate mean..."
    sumH = np.sum(result, axis=0)
    count = len(result)
    meanH = sumH/count
    print 'done!'

    # End computations timer
    timer = datetime.now() - start_timer

    # Create HDF5 file of the data
    print 'Saving the HDF5 file...'
    f = h5py.File('OSG_HRRR_%s_m%02d_d%02d_h%02d_f%02d.h5' % (var_name, month, day, hour, fxx), 'w')
    h5_per = f.create_dataset('percentile', data=np.array(percentiles), compression="gzip", compression_opts=9)
    h5_count = f.create_dataset('count', data=count)
    h5_cores = f.create_dataset('cores', data=cpu_count)
    h5_timer = f.create_dataset('timer', data=str(timer))
    h5_mean = f.create_dataset('mean', data=np.round(meanH, 3), compression="gzip", compression_opts=9)
    
    # Create dataset for each percentile:
    for i in range(len(percentiles)):
        f.create_dataset('p%02d' % (percentiles[i]), data=np.round(perH[i], 3), compression="gzip", compression_opts=9)

    #h5_percentile = f.create_dataset('percentile value', data=np.round(perH, 3), compression="gzip", compression_opts=9)
    h5_begD = f.create_dataset('Beginning Date', data=validDATES[0].strftime('%Y-%m-%d-%H:00'))
    h5_endD = f.create_dataset('Ending Date', data=validDATES[-1].strftime('%Y-%m-%d-%H:00'))
    f.close()
    print 'done!'

    if create_latlon_h5 is True:
        # Get Latitude and Longitude (same for every file)
        print 'Getting the lat/lon fields...'
        H = get_HRRR(requestDATES[0])
        lat = H['lat'].copy()
        lon = H['lon'].copy()
        # Save the data.
        print 'Saving the HDF5 file...'
        f2 = h5py.File('OSG_HRRR_latlon.h5', 'w')
        h5_lat = f2.create_dataset('latitude', data=np.round(H['lat'], 5), compression="gzip", compression_opts=9)
        h5_lon = f2.create_dataset('longitude', data=np.round(H['lon'],5), compression="gzip", compression_opts=9)    
        f2.close()
        print 'done!'
        