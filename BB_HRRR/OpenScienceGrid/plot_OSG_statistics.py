# Brian Blaylock
# July 28, 2017                                 Just sold my old bed on KSL.com

"""
Plot values from the OSG calculated HRRR statistics
"""

from netCDF4 import Dataset
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
sys.path.append('B:\pyBKB_v2')

from BB_downloads.HRRR_S3 import *
from BB_basemap.draw_maps import draw_CONUS_HRRR_map

m = draw_CONUS_HRRR_map()

for month in range(1,13):
    for hour in range(0, 24):
        plt.clf()
        plt.cla()
        
        # open a file
        var = 'TMP:2 m'
        var = 'WIND:10 m'
        #var = 'REFC:entire'
        variable = var.replace(":", '_').replace(' ', '_')
        fxx = 0

        FILE = 'OSG_HRRR_%s_m%02d_h%02d_f%02d.nc' % (var.replace(':', '_').replace(' ', '_'), month, hour, fxx)
        print FILE
        nc = Dataset(FILE, 'r')

        lat = nc.variables['latitude'][:]
        lon = nc.variables['longitude'][:]

        count = nc.variables['count'][:]
        sDATE = ''.join(nc.variables['Begin Date'])
        eDATE = ''.join(nc.variables['End Date'])
        timer = ''.join(nc.variables['timer'])
        cores = nc.variables['cores'][:]
        percentiles = nc.variables['percent_compute'][:]

        STAT = {'MAX': nc.variables['max_%s' % (variable)][:],
                'MIN': nc.variables['min_%s' % (variable)][:],
                'MEAN': nc.variables['mean_%s' % (variable)][:],
                'P01': nc.variables['percentile'][0][:],
                'P05': nc.variables['percentile'][1][:],
                'P10': nc.variables['percentile'][2][:],
                'P90': nc.variables['percentile'][3][:],
                'P95': nc.variables['percentile'][4][:],
                'P99': nc.variables['percentile'][5][:]
                }
        
        nSTAT = 'P95'

        x, y = m(lon, lat)
        m.drawstates()
        m.drawcoastlines()
        m.drawcountries()
        if var == 'TMP:2 m':
            m.pcolormesh(x, y, STAT[nSTAT], vmax=310, vmin=265, cmap='Spectral_r')
            cb = plt.colorbar(orientation='horizontal', shrink=.9, pad=.05)
            cb.set_label('2 m Temperature (K)')
        elif var == 'WIND:10 m':
            m.pcolormesh(x, y, STAT[nSTAT], vmax=0, vmin=20, cmap='plasma_r')
            cb = plt.colorbar(orientation='horizontal', shrink=.9, pad=.05)
            cb.set_label(r'10 m Wind Speed (ms$\mathregular{^{-1}}$)')
        elif var == 'REFC:entire':
            m.pcolormesh(x, y, STAT[nSTAT], vmax=0, vmin=80, cmap='gist_ncar')
            cb = plt.colorbar(orientation='horizontal', shrink=.9, pad=.05)
            cb.set_label(r'Simulated Composite Reflectivity (dBZ)')
        

        plt.title('HRRR Composite: %s Month:%s, Hour:%s, fxx:%s\nBegin: %s, End:%s\nCount:%s, Cores:%s\nTimer: %s\n' % (nSTAT, month, hour, fxx, sDATE, eDATE, count, cores, timer))

        plt.savefig('figs/OSG_%s_%s_m%02d_h%02d_f%02d.png' % (nSTAT, var.replace(':', '_').replace(' ', '_'), month, hour, fxx), bbox_inches='tight', dpi=300)

        nc.close()
