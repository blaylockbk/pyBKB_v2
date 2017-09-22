# GNC-A Blog Python Tutorial: Part VI
# https://geonetcast.wordpress.com/2017/07/25/geonetclass-manipulating-goes-16-data-with-python-part-vi/

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from remap import remap
import numpy as np
from datetime import datetime

#import sys
#sys.path.append('H:/pyBKB_v2')
#from BB_downloads.HRRR_S3 import get_hrrr_variable
#==============================================================================

# Choose the visualization extent (min lon, min lat, max lon, max lat)
extent = [-175.0, -80.0, -5.0, 80.0] # Full Disk 
extent = [-135, 21, -61, 53]# CONUS (matches close to HRRR domain)

# === Load the GOES-16 Data ===================================================
# Full Disk
path = 'H:/temp/OR_ABI-L2-MCMIPF-M3_G16_s20172531800356_e20172531811128_c20172531811213.nc'

# Choose the image resolution (the higher the number the faster the processing)
resolution = 2.0

# Call the reprojection funcion (path, map extent, resolution, band, file type)
B_grid = remap(path, extent, resolution, 1, 'NETCDF')
R_grid = remap(path, extent, resolution, 2, 'NETCDF')
G_grid = remap(path, extent, resolution, 3, 'NETCDF')

# Read the data returned by the function
B_data = B_grid.ReadAsArray()
R_data = R_grid.ReadAsArray()
G_data = G_grid.ReadAsArray()

# Apply a Gamma Correction
B_gamma = np.sqrt(B_data)
R_gamma = np.sqrt(R_data)
G_gamma = np.sqrt(G_data)

# "True" Green Correction
G_true = 0.48358168 * R_gamma + 0.45706946 * B_gamma + 0.06038137 * G_gamma

RGB = np.flipud(np.dstack([R_gamma, G_true, B_gamma]))
#==============================================================================

# === Load the HRRR Data ======================================================
#DATE = datetime.strptime('20172531800356', '%Y%j%H%M%S%f')
#H = get_hrrr_variable(DATE, 'REFC:surface')
# My computer doesn't have pygrib and CHPC doesn't have gdal, so I saved the 
# HRRR dictionary from CHPC to my temp file so I can load it here.
H = np.load('H:/temp/HRRR_sample.npy').item()

# === Plot the Data ===========================================================
m = Basemap(llcrnrlon=extent[0], llcrnrlat=extent[1], urcrnrlon=extent[2], urcrnrlat=extent[3], epsg=4326)

# --- GOES-16 Data ------------------------------------------------------------
plt.figure(1)
# Draw map elements
m.drawparallels(np.arange(-90.0, 90.0, 20.0), linewidth=0.25, color='white', labels=[True,False,False,True])
m.drawmeridians(np.arange(0.0, 360.0, 20.0), linewidth=0.25, color='white', labels=[True,False,False,True])
m.drawcoastlines()

# Plot the GOES-16 True Color
m.imshow(RGB, origin='upper')

# Add a title to the plot
plt.title("GOES-16 ABI True Color" + str(DATE))

# --- HRRR Data ---------------------------------------------------------------
plt.figure(2)
# Plot Radar Data
x, y = m(H['lon'], H['lat'])
dBZ = H['value']
dBZ = np.ma.array(dBZ)
dBZ[dBZ == -10] = np.ma.masked
m.pcolormesh(x, y, dBZ)

# Draw box around HRRR domain for reference
m.plot(H['lon'][:,0], H['lat'][:,0], c='k')
m.plot(H['lon'][:,-1], H['lat'][:,-1], c='k')
m.plot(H['lon'][0,:], H['lat'][0,:], c='k')
m.plot(H['lon'][-1,:], H['lat'][-1,:], c='k')

# Show the plot
plt.show()



lats = np.linspace(extent[1], extent[3], int(RGB.shape[1]))
lons = np.linspace(extent[0], extent[2], int(RGB.shape[0]))




# Cut full disk in half:
m = Basemap(llcrnrlon=extent[0], llcrnrlat=0, urcrnrlon=extent[2], urcrnrlat=extent[3], epsg=4326, resolution='i')
half = np.flipud(RGB[:len(RGB)/2, :, :])
m.imshow(half)
m.drawcoastlines()

lons = np.linspace(extent[0], extent[2], int(half.shape[1]))
lats = np.linspace(0, extent[3], int(len(half)))

res = 'l'
area_thresh = 1000
m = Basemap(resolution=res, projection='lcc', area_thresh=area_thresh, \
                width=1800*3000, height=1060*3000, \
                lat_1=38.5, lat_2=38.5, \
                lat_0=38.5, lon_0=-97.5)

LONS, LATS = np.meshgrid(lons, lats)

XH, YH = m(H['lon'], H['lat'])

color_tuple = half.transpose((1,0,2)).reshape((half.shape[0]*half.shape[1],half.shape[2]))/255.0
m.pcolormesh(XG, YG, half[:, :, 0], color=color_tuple)

