# Brian Blaylock
# August 25, 2017                            Rachel is flying to Europe

"""
Plot values from the OSG calculated HRRR statistics
Daily 30 is the 30-day average data
"""

import h5py
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
sys.path.append('B:\pyBKB_v2')

var = 'TMP:2 m'
#var = 'WIND:10 m'
#var = 'REFC:entire'
#var = 'TMP:surface'
variable = var.replace(":", '_').replace(' ', '_')
fxx = 0

DIR = '/uufs/chpc.utah.edu/common/home/horel-group2/blaylock/HRRR_OSG/daily30_20150418-20170801/'
latlon_file = h5py.File(DIR+'OSG_HRRR_latlon.h5', 'r')
lat = latlon_file['latitude'].value
lon = latlon_file['longitude'].value

cores = []
count = []
timer = []
date = []

# day count
dc=0


for month in range(1, 13):
    for day in range(1, 32):
        for hour in range(0, 24):
            plt.clf()
            plt.cla()
            
            # Day number
            dc += 1
            
            # open a file
            DIR = '/uufs/chpc.utah.edu/common/home/horel-group2/blaylock/HRRR_OSG/daily30_20150418-20170801/%s/' % (variable)
            FILE = 'OSG_HRRR_%s_m%02d_d%02d_h%02d_f%02d.h5' % (var.replace(':', '_').replace(' ', '_'), month, day, hour, fxx)
            print FILE
            h = h5py.File(DIR+FILE, 'r')

            cores.append(h['cores'].value)
            count.append(h['count'].value)
            timer.append(h['timer'].value)
            date.append(dc)

            h.close()
