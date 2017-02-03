## Brian Blaylock
## 20 May 2016

### !Not finished. Just saving my progress!

# Convert image to array and to netCDF

# This method may only work for arrays with less than 255 unique values. 
# That is all an image can distinguish.
# This is useful for categorical data and masked data sets,
# but not for range data like temperature or elevation,
# unless I come up with some method to use the full RBG specturm, in that 
# case there are several million unique values.


import numpy as np
import os
from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt
import shutil
from scipy.io import netcdf

from scipy import misc
path = './'

landmask = misc.imread(os.path.join(path, 'landmask2_Jim_Edit.bmp'), flatten=0)

# Image needs to be flipped vertically
landmask = np.flipud(landmask)
# Convert the water points to zero, land points to 1, (water points are already 0)
landmask[landmask==255] = 1

# replace values in new array with category that matches the color in the image
DIR = '/uufs/chpc.utah.edu/common/home/steenburgh-group2/leah/wrf/owles/control/tug_seaice_usgs/geo_em/'
FILE = DIR + 'geo_em.d03.nc'

# 0. Make a copy of the original geo_em file
nc = netcdf.netcdf_file(FILE,'r')
NEW_FILE = './LakeSurgery_geo_em.d03.nc'
shutil.copy2(FILE, NEW_FILE)

# 1. open new file netcdf in append mode
nc_copy = netcdf.netcdf_file(NEW_FILE,'a')

# 2. replace the land mask variable with new mask
nc_copy.variables['LANDMASK'][0] = landmask 


# 3. Set the land use index for the lake mask as lake
old_LU = nc_copy.variables['LU_INDEX'][0]
new_LU = old_LU.copy()
new_LU[landmask==0] = 16
nc_copy.variables['LU_INDEX'][0] = new_LU


nc_copy.sync()
nc_copy.close