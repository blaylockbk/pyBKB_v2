# Brian Blaylock
# September 25, 2017

# CONUS
from netCDF4 import Dataset
import numpy as np
from datetime import datetime, timedelta
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from pyproj import Proj

p = Proj(proj='geos', h='35786023.0', lon_0='-89.5', sweep='x')

C_file = 'H:/temp/OR_ABI-L2-MCMIPC-M3_G16_s20172531802165_e20172531804538_c20172531805050.nc'
C_file = '/uufs/chpc.utah.edu/common/home/u0553130/temp/OR_ABI-L2-MCMIPC-M3_G16_s20172531802165_e20172531804538_c20172531805050.nc'
C = Dataset(C_file, 'r')

from matplotlib.colors import LinearSegmentedColormap

cmap_WV = LinearSegmentedColormap.from_list('this', ['darkgreen', 'green', 'lightgreen', 'white', 'blue', 'yellow', 'red', 'k'])

# Seconds since 2000-01-01 12:00:00
add_seconds = C.variables['t'][0]
DATE = datetime(2000, 1, 1, 12) + timedelta(seconds=add_seconds)

# Low-Level Water Vapor (Channel 10)
WV10 = C.variables['CMI_C10']
WV09 = C.variables['CMI_C09']
WV08 = C.variables['CMI_C08']

h = C.variables['goes_imager_projection'].perspective_point_height
X = C.variables['x'][:] * h
Y = C.variables['y'][:] * h

# GOES-16 image on geostationary projection
m = Basemap(projection='geos', lon_0='-89.5',
            resolution='i', area_thresh=1500,
            llcrnrx=X.min(),llcrnry=Y.min(),
            urcrnrx=X.max(),urcrnry=Y.max())

# Low-Level Water Vapor
plt.figure(1)
m.imshow(np.flipud(WV10), cmap=cmap_WV, vmax=280, vmin=180)
m.drawcoastlines()
m.drawcountries()
m.drawstates()

plt.title('GOES-16 ABI Channel 10: Low-Level Troposphere WV Band' % ())
cb = plt.colorbar(orientation='horizontal', pad=.01, shrink=.75)
cb.set_label('Brightness Temperature (K)')


# Mid-Level Water Vapor
plt.figure(2)
m.imshow(np.flipud(WV09), cmap=cmap_WV, vmax=280, vmin=180)
m.drawcoastlines()
m.drawcountries()
m.drawstates()

plt.title('GOES-16 ABI Channel 09: Mid-Level Troposphere WV Band' % ())
cb = plt.colorbar(orientation='horizontal', pad=.01, shrink=.75)
cb.set_label('Brightness Temperature (K)')


# Upper-Level Water Vapor
plt.figure(3)
m.imshow(np.flipud(WV08), cmap=cmap_WV, vmax=280, vmin=180)
m.drawcoastlines()
m.drawcountries()
m.drawstates()

plt.title('GOES-16 ABI Channel 08: Upper Troposphere WV Band' % ())
cb = plt.colorbar(orientation='horizontal', pad=.01, shrink=.75)
cb.set_label('Brightness Temperature (K)')



# Convert map points to lats/lons
Xs, Ys = np.meshgrid(X, Y)
lons, lats = p(Xs, Ys, inverse=True)

# Plot GOES-16 on HRRR Map:
Hm = Basemap(resolution='i', projection='lcc', area_thresh=1000, \
             width=1800*3000, height=1060*3000, \
             lat_1=38.5, lat_2=38.5, \
             lat_0=38.5, lon_0=-97.5)

Hx, Hy = Hm(lons, lats)


# low-level Troposphere
plt.figure(4)
m = Hm.pcolormesh(Hx, Hy, WV10, cmap=cmap_WV, vmax=280, vmin=180)
Hm.drawstates()
Hm.drawcountries()
Hm.drawcoastlines()
plt.title('GOES-16 ABI Channel 10: Low-Level Troposphere WV Band' % ())
cb = plt.colorbar(orientation='horizontal', pad=.01, shrink=.75)
cb.set_label('Brightness Temperature (K)')

# mid-level Troposphere
plt.figure(5)
m = Hm.pcolormesh(Hx, Hy, WV09, cmap=cmap_WV, linewidth=0, vmax=280, vmin=180)
Hm.drawstates()
Hm.drawcountries()
Hm.drawcoastlines()
plt.title('GOES-16 ABI Channel 09: Mid-Level Troposphere WV Band' % ())
cb = plt.colorbar(orientation='horizontal', pad=.01, shrink=.75)
cb.set_label('Brightness Temperature (K)')

# upper-level Troposphere
plt.figure(6)
m = Hm.pcolormesh(Hx, Hy, WV08, cmap=cmap_WV, linewidth=0, vmax=280, vmin=180)
Hm.drawstates()
Hm.drawcountries()
Hm.drawcoastlines()
plt.title('GOES-16 ABI Channel 08: Upper-Level Troposphere WV Band' % ())
cb = plt.colorbar(orientation='horizontal', pad=.01, shrink=.75)
cb.set_label('Brightness Temperature (K)')

plt.show()