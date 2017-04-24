# Brian Blaylock
#
# Created: November 4, 2015
# Udates:
# Plotting netCDF data that has been converted from grib2 format

#

## Must Convert grib2 file to a netcdf file
## in LINUX Terminal: 'wgrib2 gribfile.grib2 -netcdf newfile.nc'

## Lake shape files available here: http://www.census.gov/cgi-bin/geo/shapefiles/index.php?year=2015&layergroup=Water
print ""
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
import linecache

from functions_domains_models import *
from terrain_colormap import *

# Set universal figure margins
width = 20
height = 18

#Other directories
HOMEBASE    = '/uufs/chpc.utah.edu/common/home/u0553130/'
FIG_DIR = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/MS/HRRR_domains/'


# Get HRRR terrain
domain = get_domain('full_HRRR')
model = get_model_info('HRRR_geo')

# Open File
BASE=model['BASE']
file_name = BASE+model['string_format']

print 'File Name: ', file_name

MP = domain['map_projection']

MP = 'cyl'


stn_name = []
stn_sym = []
# load tslist
for i in np.arange(4,35):
    line = np.linecache.getline('/uufs/chpc.utah.edu/common/home/horel-group4/model/bblaylock/WRF3.7_sniplake/WRFV3/test/em_real/tslist',i)
    stn_name.append(line[0:25])
    stn_sym.append(line[25:32])    


## Get the locations of each TS list
#initialize some arrays
TS_lat = np.array([])
TS_lon = np.array([])
TS_stn = np.array([])


stn = ['FG005','GNI','GSLBY','HATUT','KOGD','KPVU','kslc','naa','O3S07','O3S08','QHW','QSF','UFD08','ukbkb','USDR2','UT12','UT23','UTLGP','wbb']

BASE = '/uufs/chpc.utah.edu/common/home/horel-group4/model/bblaylock/WRF3.7_sniplake/WRFV3/test/em_real/'
for s in stn:
    TS = linecache.getline(BASE+s+'.d02.TS',1) # read the first line
    TS_lat = np.append(TS_lat, float(TS[39:46]))
    TS_lon = np.append(TS_lon, float(TS[47:55]))
    TS_stn = np.append(TS_stn,s)






### Get Domain 2 WPS directory
file_name = '/uufs/chpc.utah.edu/common/home/horel-group4/model/bblaylock/WRF3.7_sniplake/WPS/geo_em.d02.nc'
hrrr_nc = netcdf.netcdf_file(file_name,'r')
height = hrrr_nc.variables['HGT_M'][0,:,:]
landmask = hrrr_nc.variables['LANDMASK'][0,:,:]
height = height.copy()
ter_lat = hrrr_nc.variables['XLAT_M'][0]
ter_lat = ter_lat.copy()
ter_lon = hrrr_nc.variables['XLONG_M'][0]
ter_lon = ter_lon.copy()
#hrrr_nc.close()

# Set water area to -99 in height variable. This will make it blue
height[landmask==0] = -99

## Full_domain
bot_left_lat  = ter_lat[0][0] 
bot_left_lon  = ter_lon[0][0]
top_right_lat = ter_lat[-1][-1]
top_right_lon = ter_lon[-1][-1]



if MP == 'cyl':
    ## Map in cylindrical projection (data points may apear skewed)
    m = Basemap(resolution='i',area_thresh=10.,projection='cyl',\
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
ter_x,ter_y = m(ter_lon,ter_lat)

# Turn ocean points to a really low number so we can plot it as blue, not green
masked_height = maskoceans(ter_x,ter_y,height,inlands=False,resolution='l')
masked_height.data[masked_height.data==0]=-99



m.drawstates(color='k', linewidth=.8)
m.drawcoastlines(color='k')
m.drawcountries(color='k', linewidth=1.25)

plt.figure(1, figsize=(width,height))
plt.rc("figure.subplot", left = .001)
plt.rc("figure.subplot", right = .999)
plt.rc("figure.subplot", bottom = .001)
plt.rc("figure.subplot", top = .999)
plt.tight_layout(pad=5.08)

#scale figure size to bigger image
N = 2
params = plt.gcf()
plSize = params.get_size_inches()
params.set_size_inches((plSize[0]*N, plSize[1]*N))
"""
plt.title('%s Terrain' % ('HRRR 3km'), \
			fontsize=18,bbox=dict(facecolor='white', alpha=0.95),\
			x=.5,y=.93,weight = 'demibold',style='oblique', \
			stretch='normal', family='sans-serif')
"""



im = plt.pcolormesh(ter_x,ter_y,masked_height.data,cmap=terrain_cmap_256())
cbar = plt.colorbar(orientation='horizontal',shrink=.7,pad=0)    
cbar.set_label('Terrain Height (meters)')

#Plot Domain 2 Box
m.drawgreatcircle(ter_lon[0,0], ter_lat[0,0],ter_lon[0,-1], ter_lat[0,-1], color='r', linewidth='4')
m.drawgreatcircle(ter_lon[-1,0], ter_lat[-1,0],ter_lon[-1,-1], ter_lat[-1,-1], color='r', linewidth='4')
m.drawgreatcircle(ter_lon[0,0], ter_lat[0,0],ter_lon[-1,0],ter_lat[-1,0], color='r', linewidth='4')
m.drawgreatcircle(ter_lon[0,-1], ter_lat[0,-1],ter_lon[-1,-1], ter_lat[-1,-1], color='r', linewidth='4')

#Plot TS Locations
m.scatter(TS_lon,TS_lat,color='w')
#Add Labels
for i in np.arange(0,len(TS_stn)):
    plt.annotate(TS_stn[i],xy=(TS_lon[i],TS_lat[i]))
'''
#Plot Subdomains (Salt Lake Valley, Utah Lake, etc...)
#for area in ['salt_lake_valley','uintah_basin','cache_valley','bear_lake','utah_lake','utah_valley']:    
for area in ['great_salt_lake']:    
    domain = get_domain(area)
    toprightlat = domain['top_right_lat']
    topleftlat = domain['top_right_lat']
    toprightlon = domain['top_right_lon']
    topleftlon = domain['bot_left_lon']
    botrightlat = domain['bot_left_lat']
    botrightlon = domain['top_right_lon']
    botleftlat = domain['bot_left_lat']
    botleftlon = domain['bot_left_lon']
    
    m.drawgreatcircle(toprightlon,toprightlat,topleftlon,topleftlat, color='#FFFF4C', linewidth='3')
    m.drawgreatcircle(topleftlon,topleftlat,botleftlon,botleftlat, color='#FFFF4c', linewidth='3')
    m.drawgreatcircle(botleftlon,botleftlat,botrightlon,botrightlat, color='#FFFF4c', linewidth='3')
    m.drawgreatcircle(botrightlon,botrightlat,toprightlon,toprightlat, color='#FFFF4c', linewidth='3')
'''

# Plot Roads
BASE = '/uufs/chpc.utah.edu/common/home/u0553130/'
m.readshapefile(BASE+'shape_files/tl_2015_UtahRoads_prisecroads/tl_2015_49_prisecroads','roads', linewidth=.1, color='grey')

'''# Plot height contours
plt.contour(ter_x,ter_y,height,np.arange(0,np.max(height),100),\
           colors='grey',width=5,linewidths=.5)
'''

print 'saving'
plt.savefig('test.png',bbox_inches='tight',dpi=300)
plt.show()
print ""
