# encoding: utf-8
"""Resolve Metadata QC Issues"""


import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from srtm import get_granule_name, open_granule_30m

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
from BB_downloads.HRRR_S3 import get_hrrr_variable, hrrr_subset

# =============================================================================
# Brian Head Fire (center of fire)
# =============================================================================
lat = 37.7736
lon = -112.6418
hrrr_half_box = 6
srtm_half_box = hrrr_half_box * 3000 / 30

# =============================================================================
# UKBKB - Spanish Fork
# =============================================================================
#lat = 40.09867 	
#lon = -111.62767 

# =============================================================================
# KSLC - Salt Lake Airport
# =============================================================================
#lat = 40.77069 
#lon = -111.96503 



# =============================================================================
# Get 30m terrain data
# =============================================================================

# Center panels:
granule = get_granule_name(lat, lon)


srtm_data = open_granule_30m(granule)
srtm_data = np.flipud(srtm_data)           # because the data was an image, and images are fliped vertically
srtm_data = srtm_data[0:3600, 0:3600]

# Get granual just below
below = get_granule_name(lat-1, lon)
srtm_below = open_granule_30m(below)
srtm_below = np.flipud(srtm_below)           # because the data was an image, and images are fliped vertically
srtm_below = srtm_below[0:3600, 0:3600]

# Get granual just above
above = get_granule_name(lat+1, lon)
srtm_above = open_granule_30m(above)
srtm_above = np.flipud(srtm_above)           # because the data was an image, and images are fliped vertically
srtm_above = srtm_above[0:3600, 0:3600]

#stich together
srtm_center = np.vstack([srtm_below, srtm_data, srtm_above])

# Right panels:
# Get top right
TR = get_granule_name(lat+1, lon+1)
srtm_TR = open_granule_30m(TR)
srtm_TR = np.flipud(srtm_TR)           # because the data was an image, and images are fliped vertically
srtm_TR = srtm_TR[0:3600, 0:3600]

# Get right
R = get_granule_name(lat, lon+1)
srtm_R = open_granule_30m(R)
srtm_R = np.flipud(srtm_R)           # because the data was an image, and images are fliped vertically
srtm_R = srtm_R[0:3600, 0:3600]

# Get bottom right
BR = get_granule_name(lat-1, lon+1)
srtm_BR = open_granule_30m(BR)
srtm_BR = np.flipud(srtm_BR)           # because the data was an image, and images are fliped vertically
srtm_BR = srtm_BR[0:3600, 0:3600]

#stich together
srtm_right = np.vstack([srtm_BR, srtm_R, srtm_TR])

# Left panels:
# Get top left
TL = get_granule_name(lat+1, lon-1)
srtm_TL = open_granule_30m(TL)
srtm_TL = np.flipud(srtm_TL)           # because the data was an image, and images are fliped vertically
srtm_TL = srtm_TL[0:3600, 0:3600]

# Get left
L = get_granule_name(lat, lon-1)
srtm_L = open_granule_30m(L)
srtm_L = np.flipud(srtm_L)           # because the data was an image, and images are fliped vertically
srtm_L = srtm_L[0:3600, 0:3600]

# Get bottom left
BL = get_granule_name(lat-1, lon-1)
srtm_BL = open_granule_30m(BL)
srtm_BL = np.flipud(srtm_BL)           # because the data was an image, and images are fliped vertically
srtm_BL = srtm_BL[0:3600, 0:3600]

#stich together left column
srtm_left = np.vstack([srtm_BL, srtm_L, srtm_TL])

# Stich all together
srtm_full = np.hstack([srtm_left, srtm_center, srtm_right])

# mesh lat/lon grid
W = -int(granule[-3:])-1
E = W+3
S = int(granule[1:3])-1
N = S+3
data_lons = np.linspace(W, E, 3600*3)
data_lats = np.linspace(S, N, 3600*3)

lons2D, lats2D = np.meshgrid(data_lons, data_lats)

# 1) Compute the abosulte difference between the grid lat/lon and the point
abslat = np.abs(lats2D-lat)
abslon = np.abs(lons2D-lon)

# 2) Element-wise maxima. (Plot this with pcolormesh to see what I've done.)
c = np.maximum(abslon, abslat)

# 3) The index of the minimum maxima (which is the nearest lat/lon)
x, y = np.where(c == np.min(c))
xidx = x[0]
yidx = y[0]

print 'x:%s, y:%s' % (xidx, yidx)
print 'lat:%s, lon:%s' % (lats2D[xidx, yidx], lons2D[xidx, yidx])

half_box= srtm_half_box
subset = {'lat': lats2D[xidx-half_box:xidx+half_box, yidx-half_box:yidx+half_box],
            'lon': lons2D[xidx-half_box:xidx+half_box, yidx-half_box:yidx+half_box],
            'value': srtm_full[xidx-half_box:xidx+half_box, yidx-half_box:yidx+half_box]}


# =============================================================================
# HRRR model resolution
# =============================================================================
# Get Terrain Data from HRRR
DATE = datetime(2017, 6, 25)
variable = 'HGT:surface'
topo = get_hrrr_variable(DATE, variable)

topo = hrrr_subset(topo, lat=lat, lon=lon, half_box=hrrr_half_box)



# =============================================================================
# Make 3D projection plot
# =============================================================================
fig = plt.figure(1)
ax = fig.gca(projection='3d')
# Plot the HRRR surface
surf = ax.plot_surface(topo['lon'], topo['lat'], topo['value'],
                       cmap='terrain',
                       linewidth=.1, antialiased=False,
                       rstride=1, cstride=1)
plt.savefig('HRRR_ter.png')


fig = plt.figure(2)
ax = fig.gca(projection='3d')
# Plot the 30 m surface.
srfm = ax.plot_surface(subset['lon'], subset['lat'], subset['value'],
                       cmap='terrain',
                       linewidth=0, antialiased=False)
plt.savefig('REAL_ter.png')


print 'HRRR grid:'
print  topo['lat'][0][0], topo['lon'][0][0] 
print  topo['lat'][0][-1], topo['lon'][0][-1]
print  topo['lat'][-1][0], topo['lon'][-1][0]  
print  topo['lat'][-1][-1], topo['lon'][-1][-1] 

print 'SRTM 30m grid:'
print  subset['lat'][0][0], subset['lon'][0][0] 
print  subset['lat'][0][-1], subset['lon'][0][-1]
print  subset['lat'][-1][0], subset['lon'][-1][0]  
print  subset['lat'][-1][-1], subset['lon'][-1][-1] 