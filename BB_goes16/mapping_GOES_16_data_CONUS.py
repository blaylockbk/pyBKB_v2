# Brian Blaylock
# September 15, 2017

# CONUS
from netCDF4 import Dataset
import numpy as np
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from pyproj import Proj
p = Proj(proj='geos', h='35786023.0', lon_0='-89.5', sweep='x')

C_file = 'H:/temp/OR_ABI-L2-MCMIPC-M3_G16_s20172531802165_e20172531804538_c20172531805050.nc'
C = Dataset(C_file, 'r')
# RGB with gamma correction
Rc = np.sqrt(C.variables['CMI_C02'])
Gc = np.sqrt(C.variables['CMI_C03'])
Bc = np.sqrt(C.variables['CMI_C01'])
Gc_true = 0.48358168 * Rc + 0.45706946 * Bc + 0.06038137 * Gc
C_RGB = np.dstack([Rc, Gc_true, Bc])


h = C.variables['goes_imager_projection'].perspective_point_height
x = C.variables['x']
y = C.variables['y']
#X = (np.sign(x.scale_factor) * x[:] + x.add_offset) * h
#Y = (np.sign(y.scale_factor) * y[:] + y.add_offset) * h
X = x[:] * h
Y = y[:] * h


# GOES-16 image on geostationary projection
north = C.variables['geospatial_lat_lon_extent'].geospatial_northbound_latitude
south = C.variables['geospatial_lat_lon_extent'].geospatial_southbound_latitude
east = C.variables['geospatial_lat_lon_extent'].geospatial_eastbound_longitude
west = C.variables['geospatial_lat_lon_extent'].geospatial_westbound_longitude
plt.figure(1)
m = Basemap(projection='geos', lon_0='-89.5',
            llcrnrx=X.min(),llcrnry=Y.min(),
            urcrnrx=X.max(),urcrnry=Y.max())

m.imshow(np.flipud(C_RGB), extent=[west, east, south, north])
m.drawcoastlines()
m.drawcountries()
m.drawstates()


# Convert map points to lats/lons
Xs, Ys = np.meshgrid(X, Y)
lons, lats = p(Xs, Ys, inverse=True)

# Plot GOES-16 on HRRR Map:
plt.figure(2)
Hm = Basemap(resolution='i', projection='lcc', area_thresh=1000, \
             width=1800*3000, height=1060*3000, \
             lat_1=38.5, lat_2=38.5, \
             lat_0=38.5, lon_0=-97.5)

Hx, Hy = Hm(lons, lats)

# need to create a color tuple for Pcolormesh
rgb = C_RGB[:,:-1,:] # Use one less column is very imporant, else your image will be scrambled.
rgb = np.minimum(rgb, 1) # The maximum possible value is 1.
colorTuple = rgb.reshape((rgb.shape[0] * rgb.shape[1]), 3)
colorTuple = np.insert(colorTuple, 3, 1.0, axis=1) # Add an alpha channel for faster plotting (see https://stackoverflow.com/questions/41389335/how-to-plot-geolocated-rgb-data-faster-using-python-basemap)
m = Hm.pcolormesh(Hx, Hy, Rc, color=colorTuple, linewidth=0)
m.set_array(None) # without this, the linewidth is set to zero, but the RGB color is ignored
Hm.drawstates()
Hm.drawcountries()
Hm.drawcoastlines()

plt.show()