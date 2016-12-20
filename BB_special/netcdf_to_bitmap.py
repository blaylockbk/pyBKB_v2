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
WRFDIR = '/uufs/chpc.utah.edu/common/home/horel-group4/model/bblaylock/WRF3.7_spinup/DATA/FULL_RUN_June14-19/'
filepath = 'wrfout_d02_2015-06-18_18:00:00'
nc = netcdf.netcdf_file(WRFDIR+filepath,'r')


# get varialbes and save as image

"""
# Cateogorical data (i.e. "Land Use" save as a color image acording to the colorscheme defined by C)
"""
lu = nc.variables['LU_INDEX'][0] # landuse

# initiate R,G,B, arrays 
R = np.zeros_like(lu)
G = np.zeros_like(lu)
B = np.zeros_like(lu)

# fill R,G,B arrays with color defined by C
for i in np.arange(1,len(C)+1):  
    R[lu==i] = C[i-1][0]
    G[lu==i] = C[i-1][1]
    B[lu==i] = C[i-1][2]

#combine R,G,B arrays into one. Multiplly by 255 to get correct amount (C is in % of 255)
RGB = np.array([R,G,B])
# Rotate the array to "image orientation" and change type to uint8 requried to save as BITMAP
RGB= np.rot90(np.transpose(np.uint8(RGB)))

#Save as BITMAP using two different methods
Image.fromarray(RGB).save("landuse1.bmp")
import scipy.misc
scipy.misc.toimage(RGB).save('landuse2.bmp')
print "saved landuse"


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



HGT = nc.variables['HGT'][0] # elevation in meters
# Rotate the array to "image orientation" and change type to uint8 requried to save as BITMAP
HGT= np.rot90(np.transpose(HGT))
#Save as BITMAP using two different methods
# Image.fromarray(HGT).save("elevation1.bmp") ## must be a uint8 type with three array colors
import scipy.misc
scipy.misc.toimage(HGT).save('elevation2.bmp')
print "saved elevation"