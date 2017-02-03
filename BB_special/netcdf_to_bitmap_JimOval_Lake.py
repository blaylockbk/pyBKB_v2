### Brian BLaylock
### 20 May 2016

"""
## Step 1 of 3 in "Edit netCDF variables in Photoshop"
# Step 1: convert netCDF wrfout variable into a bitmap image
# Step 2: edit the image in photoshop. Save as a bitmap image
# Step 3: open the editied bitmap image, save into the netCDF array
"""

from PIL import Image
import numpy as np
from scipy.io import netcdf

#-------------------
## MODIS 21 category land use
C = np.array([
    [0,.4,0],      #  1 Evergreen Needleleaf Forest
    [0,.4,.2],      #! 2 Evergreen Broadleaf Forest    
    [.2,.8,.2],     #  3 Deciduous Needleleaf Forest
    [.2,.8,.4],     #  4 Deciduous Broadleaf Forest
    [.2,.6,.2],     #  5 Mixed Forests
    [.3,.7,.1],      #  6 Closed Shrublands
    [.82,.41,.12],     #  7 Open Shurblands
    [.74,.71,.41],       #  8 Woody Savannas
    [1,.84,.0],     #  9 Savannas
    [0,1,.15],        #  10 Grasslands
    [.06,1,1],        #! 11 Permanant Wetlands
    [1,.95,.05],      #  12 Croplands
    [1,.05,0],     #  13 Urban and Built-up
    [.7,.9,.3],      #! 14 Cropland/Natual Vegation Mosaic
    [1,1,1],        #! 15 Snow and Ice
    [.914,.914,.7], #  16 Barren or Sparsely Vegetated
    [.5,.7,1],        #  17 Water (like oceans)
    [.86,.08,.23],        #  18 Wooded Tundra
    [.97,.5,.31],        #! 19 Mixed Tundra
    [.91,.59,.49],     #! 20 Barren Tundra
    [0,0,.88]])      #! 21 Lake

#-------------------
C = np.array(C*255,dtype=int)



# Load a netCDF WRF output file
WRFDIR = '/uufs/chpc.utah.edu/common/home/steenburgh-group2/leah/wrf/owles/control/tug_seaice_usgs/geo_em/'
filepath = 'geo_em.d03.nc'
nc = netcdf.netcdf_file(WRFDIR+filepath,'r')

# get varialbes and save as image
"""
# Masked data (i.e. "landmask") or Range data (i.e. "Temperature", "Height", etc.)
"""
landmask = nc.variables['LANDMASK'][0] # land mask
# Rotate the array to "image orientation" and change type to uint8 requried to save as BITMAP
landmask= np.rot90(np.transpose(landmask))
#Save as BITMAP using two different methods
#Image.fromarray(landmask).save("landmask1.bmp") ## must be a uint8 type with three array colors
import scipy.misc
scipy.misc.toimage(landmask).save('landmask2.bmp')
print "saved landmask"