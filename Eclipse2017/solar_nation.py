# Brian Blaylock
# August 9, 2017                Rachel is getting a root canal right now :(

"""
Plot map of solar radiation observed across the country right now
"""

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from mpl_toolkits.basemap import Basemap

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2/')
from BB_MesoWest.MesoWest_radius import get_mesowest_radius
from BB_basemap.draw_maps import draw_CONUS_cyl_map, draw_CONUS_HRRR_map, draw_HRRRwest, draw_HRRReast
from BB_downloads.HRRR_S3 import get_hrrr_variable

sDATE = datetime(2017, 8, 8)
eDATE = datetime(2017, 8, 10)
hours = (eDATE-sDATE).days*24
DATES = [sDATE+timedelta(hours=h) for h in range(hours)]

m = draw_CONUS_HRRR_map()
#m.arcgisimage(service='World_Shaded_Relief', xpixels=1000, dpi=100, verbose=False)
m.drawcoastlines()
m.drawstates()
m.drawcountries()

within = 10
for attime in DATES:
    print attime
    a = get_mesowest_radius(attime, within, extra='',
                            variables='solar_radiation',
                            verbose=True)

    x, y = m(a['LON'], a['LAT'])

    points = plt.scatter(x, y,
                         c=a['solar_radiation'],
                         cmap='magma',
                         vmin=0, vmax=1070,
                         linewidths=0)
    if attime == sDATE:
        cb = plt.colorbar(orientation='horizontal', pad=.01, shrink=.8)
        cb.set_label(r'Solar Radiation (W m$\mathregular{^{-2}}$)')
    plt.title('MesoWest Stations: %s' % attime.strftime('%Y-%m-%d %H%M UTC'))
    plt.savefig('solar_nation/%s.png' % attime.strftime('%Y-%m-%d_%H%M'), bbox_inches='tight')
    points.remove()

plt.clf(); plt.cla()
m.drawcoastlines()
m.drawstates()
m.drawcountries()
for attime in DATES:
    print attime
    H = get_hrrr_variable(attime, variable="DSWRF:surface")
    x, y = m(H['lon'], H['lat']) 
    mesh = plt.pcolormesh(x, y, H['value'], vmin=0, vmax=1070, cmap='magma')
    if attime == sDATE:
        cb = plt.colorbar(orientation='horizontal', pad=.01, shrink=.8)
        cb.set_label(r'Solar Radiation (W m$\mathregular{^{-2}}$)')
    plt.title('HRRR anlys: %s' % attime.strftime('%Y-%m-%d %H%M UTC'))
    plt.savefig('solar_nation/HRRR_%s.png' % attime.strftime('%Y-%m-%d_%H%M'), bbox_inches='tight')
    mesh.remove()