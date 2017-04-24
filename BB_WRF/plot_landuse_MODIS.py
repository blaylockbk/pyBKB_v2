# Brian Blaylock
#
# Created: March 2, 2016
print ""

import sys,getopt
#from netCDF4 import Dataset  # we dont have this library. use scipy instead
from scipy.io import netcdf
import matplotlib
#matplotlib.use('Agg')		#required for the CRON job. Says, "do not open plot in a window"??
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime, timedelta

from mpl_toolkits.basemap import Basemap, maskoceans
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.axes as maxes


from functions_domains_models import *
from terrain_colormap import *
from landuse_colormap import *

# Set universal figure margins
width = 20
height = 18

#Other directories
HOMEBASE    = '/uufs/chpc.utah.edu/common/home/u0553130/'
FIG_DIR = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/MS/landuse/'
if not os.path.exists(FIG_DIR):
        os.makedirs(FIG_DIR)


# Get HRRR terrain
domain = get_domain('full_HRRR')
model = get_model_info('HRRR_geo')

# Open File
RUN='/uufs/chpc.utah.edu/common/home/horel-group4/model/bblaylock/WRF3.7_spinup/DATA/FULL_RUN_June14-19/'

FILE = 'wrfout_d02_2015-06-18_00:00:00'

print 'File Name: ', RUN+FILE




### Get Domain 2 WPS directory
full_file = RUN+FILE
nc = netcdf.netcdf_file(full_file,'r')
HGT = nc.variables['HGT'][0,:,:].copy()
LU_INDEX = nc.variables['LU_INDEX'][0,:,:].copy()
LAT = nc.variables['XLAT'][0].copy()
LON = nc.variables['XLONG'][0].copy()

#nc.close()


## Full_domain
bot_left_lat  = LAT[0][0]+.1
bot_left_lon  = LON[0][0]
top_right_lat = LAT[-1][-1]
top_right_lon = LON[-1][-1]-.15

"""
# Custom Domain
domain = get_domain('salt_lake_valley')
top_right_lat = domain['top_right_lat']+1
top_right_lon = domain['top_right_lon']+1
bot_left_lat = domain['bot_left_lat']-1
bot_left_lon = domain['bot_left_lon']-1
"""

plt.figure(1)
MP = 'cyl'
if MP == 'cyl':
    ## Map in cylindrical projection (data points may apear skewed)
    m = Basemap(resolution='i',area_thresh=10000.,projection='cyl',\
        llcrnrlon=bot_left_lon,llcrnrlat=bot_left_lat,\
        urcrnrlon=top_right_lon,urcrnrlat=top_right_lat,)

if MP == 'lcc':
    ## Map in HRRR projected Coordinates
    m = Basemap(resolution='i',area_thresh=10000.,projection='lcc',\
        lat_0=38.5,lon_0=-97.5,\
        lat_1=38.5, lat_2=38.5,\
        llcrnrlon=bot_left_lon,llcrnrlat=bot_left_lat,\
        urcrnrlon=top_right_lon,urcrnrlat=top_right_lat,)



# This sets the standard grid point structure at full resolution
# Converts WRF lat and long to the maps x an y coordinate
x,y = m(LON,LAT)


m.drawstates(color='k', linewidth=.8)
m.drawcoastlines(color='k')
m.drawcountries(color='k', linewidth=1.25)


cm,labels = LU_MODIS21()



im = plt.pcolormesh(x,y,LU_INDEX,cmap=cm,vmax=len(labels)+1,vmin=1)
cbar = plt.colorbar(orientation='vertical',shrink=.98,pad=.02)    
cbar.set_ticks(np.arange(0.5,len(labels)+1))
cbar.ax.set_yticklabels(labels)

# Add terrain contours
#plt.contour(x,y,HGT,colors='k',lw=.5)




plt.title('MODIS Land Use Categories')

#plt.savefig(FIG_DIR+file_name+'.png',bbox_inches='tight',dpi=300)


plt.show()
print ""




