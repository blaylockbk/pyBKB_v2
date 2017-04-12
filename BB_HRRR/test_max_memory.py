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
    print getthisDATE, psutil.virtmem_usage().used/1000000000, psutil.virtmem_usage().percent
    H = get_hrrr_variable(getthisDATE, 'TMP:2 m', fxx=0, model='hrrr', field='sfc', value_only=True, verbose=False)
    return H['value']


DATE = datetime(2015, 4, 18)
eDATE = datetime.now()

# Test dates...
#DATE = date(2016, 12, 1)
#eDATE = DATE + timedelta(days=30)

hours = (eDATE - DATE).days*24
DATES = [DATE + timedelta(hours=x) for x in range(0, hours)]

cpu_count = multiprocessing.cpu_count() - 1

p = multiprocessing.Pool(cpu_count)
result = p.map(get_HRRR_value, DATES)
print "got multiprocessing data...",
p.close()







