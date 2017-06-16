# Brian Blaylock
# June 14, 2017

"""
Test grabbing a HRRR Hovmoller array
"""

import numpy as np
from datetime import datetime, timedelta
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, HourLocator

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
sys.path.append('B:\pyBKB_v2')
from BB_downloads.HRRR_S3 import *

start = datetime(2017, 6, 11)
end = datetime(2017, 6, 14)

location_dic = {'WBB':{'latitude':40.76623,
                       'longitude':-111.84755},
                'KSLC':{'latitude':40.77069,
                        'longitude':-111.96503},
                'UKBKB':{'latitude':40.09867,
                         'longitude':-111.62767}}

half_box = 4
VAR = 'WIND:10 m'
z = get_hrrr_hovmoller(start, end, location_dic, variable=VAR, area_stats=half_box)

# in order to plot the full mesh, need to extend the range by one
# see here: https://stackoverflow.com/questions/44526052/can-someone-explain-this-matplotlib-pcolormesh-quirk

stn = 'KSLC'

# pcolormesh the center grid point
plt.figure(1)
ax1 = plt.subplot(111)
plt.pcolormesh(z['valid_1d+'], z['fxx_1d+'], z[stn]['box center'], cmap='magma_r', vmin=0, vmax=20)
CS = plt.contour(z['valid_2d'], z['fxx_2d'], z[stn]['max']-z[stn]['box center'],
                 colors='k', levels=[2, 4, 6, 8, 10, 12, 14])
plt.clabel(CS, inline=1, fontsize=10, fmt='%1.f')

plt.title("%s\n%s-km2 box centerd at %s" % (VAR, half_box*6, stn))

ax1.xaxis.set_major_locator(HourLocator(byhour=[0, 6, 12, 18]))
dateFmt = DateFormatter('%b %d\n%H:%M')
ax1.xaxis.set_major_formatter(dateFmt)
ax1.set_yticks(range(0, 20, 3))

plt.show(block=False)


# pcolormesh the max in the area
plt.figure(2)
ax2 = plt.subplot(111)
plt.pcolormesh(extraV, extraF, z[stn]['max'], cmap='magma_r', vmin=0, vmax=20)
CS = plt.contour(z['valid_2d'], z['fxx_2d'], z[stn]['max']-z[stn]['box center'], colors='k', levels=[2,4,6,8,10])
plt.clabel(CS, inline=1, fontsize=10, fmt='%1.f')

plt.title("%s\n%s-km2 box centerd at %s" % (VAR, half_box*6, stn))

ax2.xaxis.set_major_locator(HourLocator(byhour=[0, 6, 12, 18]))
dateFmt = DateFormatter('%b %d\n%H:%M')
ax2.xaxis.set_major_formatter(dateFmt)
ax2.set_yticks(range(0, 20, 3))

plt.show(block=False)