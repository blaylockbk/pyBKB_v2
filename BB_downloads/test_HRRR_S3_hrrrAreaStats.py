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
from BB_downloads.HRRR_S3 import *

start = datetime(2017, 6, 1)
end = datetime(2017, 6, 2)

location_dic = {'WBB':{'latitude':40.76623,
                       'longitude':-111.84755},
                'KSLC':{'latitude':40.77069,
                        'longitude':-111.96503},
                'UKBKB':{'latitude':40.09867,
                         'longitude':-111.62767}}

H = get_hrrr_variable(start, 'TMP:2 m')
z = hrrr_area_stats(H)

zz = point_hrrr_time_series_multi(start, end, location_dic, area_stats=5)


for t in  zz['KSLC'].keys():
    if t == 'box center':
        plt.plot(zz['DATETIME'], zz['UKBKB'][t], linewidth=5)
    else:
        plt.plot(zz['DATETIME'], zz['UKBKB'][t])
plt.show()