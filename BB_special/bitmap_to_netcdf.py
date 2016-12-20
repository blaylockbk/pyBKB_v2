## Brian Blaylock
## 20 May 2016

### !Not finished. Just saving my progress!

# Convert image to array and to netCDF

# This method may only work for arrays with less than 255 unique values. That is all an image can distinguish
# This is useful for categorical data and masked data sets,
# but not for range data like temperature or elevation


import numpy as np
import os
from matplotlib.colors import ListedColormap

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

cm = ListedColormap(C)


labels = ['Evergreen Needleleaf Forest',
              'Evergreen Broadleaf Forest',
              'Deciduous Needleleaf Forest',
              'Deciduous Broadleaf Forest',
              'Mixed Forests',
              'Closed Shrublands',
              'Open Shrublands',
              'Woody Savannas',
              'Savannas',
              'Grasslands',
              'Permanent Wetlands',
              'Croplands',
              'Urban and Built-Up',
              'Cropland/Natural Vegetation Mosaic',
              'Snow and Ice',
              'Barren or Sparsely Vegetated',
              'Water',
              'Wooded Tundra',
              'Mixed Tundra',
              'Barren Tundra',
              'Lake'] 
#-------------------


from scipy import misc
path = './'


landuse = misc.imread(os.path.join(path,'landuse2.bmp'), flatten= 0)
elevation = misc.imread(os.path.join(path,'elevation2.bmp'), flatten= 0)
landmask = misc.imread(os.path.join(path,'landmask2.bmp'), flatten= 0)

sum_landuse = np.sum(landuse,axis=2)

# Sum the color array and divide by 255 (floor it) to get descreat values.
C255 = np.array(C*255,dtype=int)
sumC = C255.sum(axis=1)

# Check that we have same num of unique values in sumC as length of C
if len(sumC) == len(C):
    print "length of colors match :)"
else:
    print "len(sumC) and len(C) must match"
    print "cannot convert image colors to an array"

# replace values in new array with category that matches the color in the image
new_landuse = np.zeros_like(sum_landuse)
for i in range(0,len(C)):
    print i, labels[i]
    new_landuse[sum_landuse==sumC[i]] = i+1


# check that our sum_landuse category is in the sumC category
for i in np.unique(sum_landuse):
    print i    
    print i in sumC


## Show the difference between the original Land Use and modified
## open and save as NetCDF in place of old land_use


import matplotlib.pyplot as plt



plt.imshow(new_landuse,cmap = cm,vmin=1,vmax=len(labels)+1)
cbar = plt.colorbar(shrink=.8)
cbar.set_ticks(np.arange(0.5,len(labels)+1))
cbar.ax.set_yticklabels(labels)
