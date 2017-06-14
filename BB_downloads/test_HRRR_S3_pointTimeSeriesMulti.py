# Brian Blaylock
# June 14, 2017

"""
Test grabbing a HRRR time series from multiple points
"""

import numpy as np
from datetime import datetime, timedelta
import matplotlib as mpl
import matplotlib.pyplot as plt

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
sys.path.append('B:\pyBKB_v2')
from BB_downloads.HRRR_S3 import point_hrrr_time_series_multi

start = datetime(2017, 6, 1)
end = datetime(2017, 6, 3)
location_dic = {'WBB':{'latitude':40.76623,
                      'longitude':-111.84755},
               'KSLC':{'latitude':40.77069,
                       'longitude':-111.96503},
               'UKBKB':{'latitude':40.09867,
                        'longitude':-111.62767},
               'WBB2':{'latitude':40.7,
                      'longitude':-111.8},
               'KSLC2':{'latitude':40.7,
                       'longitude':-111.9},
               'UKBKB2':{'latitude':40.0,
                        'longitude':-111.6}}
timer = datetime.now()
z = point_hrrr_time_series_multi(start, end, location_dic)
print datetime.now()-timer
