# Brian Blaylock
# July 7, 2017

"""
DescartesLabs: MUST RUN ON VOSTRO PC (couldn't install on CHPC yet)

Fire Example: http://descartes-labs-python.readthedocs.io/en/latest/wildfire_assessment_demo.html

API token: https://iam.descarteslabs.com/
Home: descarteslabs.com
"""

# Pioneer Fire
# Let's start with importing all the toolboxes we will need for both analysis and vizualization
from IPython.display import display, Image
from descarteslabs.services import Places
from descarteslabs.services import Metadata
from mpl_toolkits.axes_grid1 import make_axes_locatable
from copy import deepcopy
from skimage import measure
from skimage.morphology import dilation #, erosion, opening, closing, white_tophat
from skimage.morphology import disk
from pprint import pprint
from pylab import *
import descarteslabs as dl
import numpy as np
import matplotlib.pyplot as plt


#==============================================================================
# First let's define the AOI as the county in which the Soberanes fire occurred

# Find potential AOI matches
matches = dl.places.find('idaho_boise')
pprint(matches)
# The first one looks good, so let's make that our area of interest.
aoi = matches[0]
shape = dl.places.shape(aoi['slug'], geom='low')

#==============================================================================
# Check for imagery before the start date of July 22nd

feature_collection = dl.metadata.search(const_id='L8', start_time='2016-09-15', end_time='2016-09-30', limit=10, place=aoi['slug'])
# As the variable name implies, this returns a FeatureCollection GeoJSON dictionary.
# Its 'features' are the available scenes.

print(len(feature_collection['features']))
# The 'id' associated with each feature is a unique identifier into our imagery database.
# In this case there are 4 L8 scenes from adjoining WRS rows.
print([f['id'] for f in feature_collection['features']])

# Now check for imagery in late October, i.e., towards the end of the fire
feature_collection = dl.metadata.search(const_id='L8', start_time='2016-11-03', end_time='2016-11-15', limit=10, place=aoi['slug'])

print(len(feature_collection['features']))
print([f['id'] for f in feature_collection['features']])

# Let's print out all the available bands we have for Landsat 8
L8_bands = dl.raster.get_bands_by_constellation("L8").keys()
print(L8_bands)
# Even though the 'bai' listed here stands for Burn Area Index, we need a normalized version of this index
# We get the NBR (normalized burn ratio) by using the swir2 and nir bands

#==============================================================================
# Collect the id's for each feature
ids = [f['id'] for f in feature_collection['features']]
# Rasterize the features.
#  * Select red, green, blue, alpha
#  * Scale the incoming data with range [0, 10000] down to [0, 4000] (40% TOAR)
#  * Choose an output type of "Byte" (uint8)
#  * Choose 60m resolution
#  * Apply a cutline of Taos county
arr, meta = dl.raster.ndarray(
    ids,
    bands=['red', 'green', 'blue', 'alpha'],
    scales=[[0,2048], [0, 2048], [0, 2048], None],
    data_type='Byte',
    resolution=60,
    cutline=shape['geometry'],
)

# Note: A value of 1 in the alpha channel signifies where there is valid data.
# We use this throughout the majority of our imagery as a standard way of specifying
# valid or nodata regions. This is particularly helpful if a value of 0 in a particular
# band has meaning, rather than specifying a lack of data.
#==============================================================================
# We'll use matplotlib to make a quick plot of the image.
plt.figure(1, figsize=[16,16])
plt.axis('off')
plt.imshow(arr)

#==============================================================================

# Let's choose a different band combination to look at the fire scar
# Rasterize the features.
#  * Select swir2, nir, aerosol, alpha
#  * Scale the incoming data with range [0, 10000] down to [0, 4000] (40% TOAR)
#  * Choose an output type of "Byte" (uint8)
#  * Choose 60m resolution for quicker vizualiation
#  * Apply a cutline of Taos county
arr, meta = dl.raster.ndarray(
    ids,
    bands=['swir2', 'nir', 'aerosol', 'alpha'],
    scales=[[0,4000], [0, 4000], [0, 4000], None],
    data_type='Byte',
    resolution=60,
    cutline=shape['geometry'],
)
# We'll use matplotlib to make a quick plot of the image.
plt.figure(2, figsize=[16,16])
plt.axis('off')
plt.imshow(arr)

#==============================================================================
# Now let's track activity in this AOI over 4 time windows and look at the 4 false color images

times=[['2016-06-15','2016-07-01'], ['2016-08-15','2016-08-31'],
             ['2016-09-15','2016-09-30'], ['2016-11-01','2016-11-15']]

axes = [[0,0],[0,1],[1,0],[1,1]]
fig, ax = plt.subplots(2,2,figsize=[20,15])
ax=ax.flatten()
for iax in ax.reshape(-1):
    iax.get_xaxis().set_ticks([])
    iax.get_yaxis().set_ticks([])

for i, timewindow in enumerate(times):
    feature_collection = dl.metadata.search(const_id='L8', start_time=timewindow[0], end_time=timewindow[1],
                                        limit=10, place=aoi['slug'])
    ids = [f['id'] for f in feature_collection['features']]
    arr, meta = dl.raster.ndarray(
        ids,
        bands=['swir2', 'nir', 'aerosol', 'alpha'],
        scales=[[0,4000], [0, 4000], [0, 4000], None],
        data_type='Byte',
        resolution=60,
        cutline=shape['geometry'],
    )
    #ax[axes[i][0], axes[i][1]].imshow(arr)
    ax[i].imshow(arr)
    ax[i].set_xlabel('%s' %timewindow[1] , fontsize=7)

fig.suptitle('Boise County: Pioneer Fire Progress', size=10)
fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.025, wspace=0.025, hspace=0.025)

#==============================================================================
# The Normalized Burn Ratio (NBR) is defined as NBR = (nir-swir2)/(nir+swir2)
# The NBR values will be in a [-1, 1] physical range and we need full bit depth to compute a good index
# We will request the raw band rasters scaled now to 10000 (100% TOAR) to obtain a correct analytic value

# Get pre-fire NBR
feature_collection = dl.metadata.search(const_id='L8', start_time='2016-06-15', end_time='2016-07-01',
                                        limit=10, place=aoi['slug'])
ids = [f['id'] for f in feature_collection['features']]
arr, meta = dl.raster.ndarray(
    ids,
    bands=['swir2', 'nir','alpha'],
    scales=[[0,10000], [0, 10000], None],
    data_type='UInt16',
    resolution=30,
    cutline=shape['geometry'],
)

arr = arr.astype('double')
prenbr = (arr[:,:,1]-arr[:,:,0])/(arr[:,:,1]+arr[:,:,0]+1e-9)

# Get post-fire NBR
feature_collection = dl.metadata.search(const_id='L8', start_time='2016-09-15', end_time='2016-09-30',
                                        limit=10, place=aoi['slug'])
ids = [f['id'] for f in feature_collection['features']]
arr, meta = dl.raster.ndarray(
    ids,
    bands=['swir2', 'nir','alpha'],
    scales=[[0,10000], [0, 10000], None],
    data_type='UInt16',
    resolution=30,
    cutline=shape['geometry'],
)

arr = arr.astype('double')
postnbr = (arr[:,:,1]-arr[:,:,0])/(arr[:,:,1]+arr[:,:,0]+1e-9)

deltanbr = prenbr - postnbr

# Let's check the ranges of these indices
print(prenbr.max(), prenbr.min(), type(prenbr))
print(postnbr.max(), postnbr.min(), type(postnbr))
print(deltanbr.max(), deltanbr.min(), type(deltanbr))

fig, ax = plt.subplots(1,3,figsize=[30,10], dpi=300)
ax=ax.flatten()
for iax in ax.reshape(-1):
    iax.get_xaxis().set_ticks([])
    iax.get_yaxis().set_ticks([])

# Plot images
ax[0].imshow(prenbr,cmap='hsv') #cmap='nipy_spectral'
ax[1].imshow(postnbr,cmap='hsv')
ax[2].imshow(deltanbr,cmap='coolwarm')

# Add some labels and markings
ax[0].set_xlabel('Pre-fire NBR' , fontsize=10)
ax[1].set_xlabel('Post-fire NBR' , fontsize=10)
ax[2].set_xlabel('Delta NBR' , fontsize=10)

fig.suptitle('Pioneer Fire Area: Normalized Burn Ratios', size=12)
fig.subplots_adjust(top = 0.98, wspace=0.025, hspace=0.025)
#==============================================================================

# We need to apply the thresholding proposed by the USGS FireMon program
# < -0.25   High post-fire regrowth
# -0.25 to -0.1     Low post-fire regrowth
# -0.1 to +0.1      Unburned
# 0.1 to 0.27       Low-severity burn
# 0.27 to 0.44      Moderate-low severity burn
# 0.44 to 0.66      Moderate-high severity burn
# > 0.66    High-severity burn

# First make a copy of the delta NBR array
deltanbrcat = deepcopy(deltanbr)
deltanbrcat[(deltanbr<0.1)]=0

deltanbrcat[((deltanbr >=0.1) & (deltanbr <0.27))]=1
deltanbrcat[(deltanbr >=0.27) & (deltanbr <0.44)]=2
deltanbrcat[(deltanbr >=0.44) & (deltanbr <0.66)]=3
deltanbrcat[(deltanbr >=0.66)]=4

# zoom to Soberanes fire area only
fire_dnbr = deltanbrcat

# Plot the severity index map we just derived
ax = plt.figure(4, figsize=[16,16])
plt.title('Pioneer Fire Burn Severity Index', fontsize=22)
plt.tick_params(
    axis='both',          # changes apply to the x-axis
    which='both',      # both major and minor ticks are affected
    bottom='off',      # ticks along the bottom edge are off
    top='off',         # ticks along the top edge are off
    labelbottom='off', # labels along the bottom edge are off
    left='off',      # ticks along the bottom edge are off
    right='off',
    labelleft='off')         # ticks along the top edge are off
ax = plt.imshow(fire_dnbr)

# And let's add a colorbar labeled with our categories
ax1 = plt.gca()
divider = make_axes_locatable(ax1)
cax = divider.append_axes("right", size="5%", pad=0.4)
cax.tick_params(
    axis='x',          # changes apply to the x-axis
    which='both',      # both major and minor ticks are affected
    bottom='off',      # ticks along the bottom edge are off
    top='off',         # ticks along the top edge are off
    labelbottom='off', # labels along the bottom edge are off
    left='off',      # ticks along the bottom edge are off
    right='off',
    labelleft='off')         # ticks along the top edge are off
cbar = plt.colorbar(ax,cax=cax,ticks=[0, 1,2,3, 4])
cbar.ax.set_yticklabels(['N/A', 'Low', 'Moderate-low', 'Moderate-high', 'High'],  fontsize=10)

#==============================================================================
# We mask out all pixels appearing unburned in the severity index map
image = (fire_dnbr>1.0)*1.0

# We use the skimage package to dilate this mask and make it smoother at the edges
selem=disk(6)
dilated = dilation(image, selem)

# We find the countours on the dilated mask
contours = measure.find_contours(dilated, 0.8)

# Display the image and plot all contours found
fig, ax = plt.subplots(figsize=(16,16))
ax.imshow(image, interpolation='nearest', cmap=plt.cm.gray)
maxlen=0
for item in contours:
    if len(item)>maxlen:
        maxlen=len(item) #find which of the detected contours is the fire perimeter

for n, contour in enumerate(contours):
    if len(contour)==maxlen:
        the_contour = contour
        ax.plot(contour[:, 1], contour[:, 0], linewidth=2)

ax.axis('image')
ax.set_xticks([])
ax.set_yticks([])

ax.set_title('Pioneer Burn Scar and Fire Contour', fontsize=12)
#==============================================================================

# Recopy the original DeltaNBR as the previous operations altered the values
deltanbrcat = deepcopy(deltanbr)
fire_dnbr = deltanbrcat
print(fire_dnbr.min(), fire_dnbr.max())

# Get extent of a pixel grid for the fire scar
nx, ny = (fire_dnbr.shape[0], fire_dnbr.shape[1])

x = np.arange(-100, 100, 1)
y = np.arange(0, 32000, 1)

fire_mask = measure.grid_points_in_poly((nx, ny), the_contour)                                 # This seems to run slow or cause some problems

burned_pixels = fire_dnbr[fire_mask]*1000 #scaled by 1000 to get dNBR

fig, ax = plt.subplots(figsize=(10,6))
counts, bins, patches = ax.hist(burned_pixels, bins=80, facecolor='blue', edgecolor='gray')

# Make matplotlib work for you and not against you
ax.set_xlim([-500, 1400])
ax.set_ylim([0, 80000])

ax.set_ylabel('Severity frequency (pixels)', fontsize=12)
ax.set_xlabel('dNBR', fontsize=12)

ax.set_xticks(range(-500,1400,100))
ax.set_xticklabels( range(-500,1400,100), rotation=45 )

ax.axvline(x=-100,lw=1.33, ls='--')
ax.axvline(x=100,lw=1.33, ls='--')

ax.annotate('Unburned', xy=(0, 78000), xycoords='data',horizontalalignment='center', verticalalignment='center', fontsize=12)
ax.annotate('Increasing burn severity', xy=(150, 78000), xycoords='data',horizontalalignment='left', verticalalignment='center', fontsize=12)
ax.arrow(700, 78000, 250, 0, shape='full', lw=2, length_includes_head=True,head_width=500,head_length=50, fc='k', ec='k')
ax.fill_between(x, 0, 80000, color='grey', alpha=0.5)

# And now let's use an intuitive color scheme to highlight the different burn severity categories
for patch, binm in zip(patches, bins):
    if (binm >= 660) :
        patch.set_facecolor('red')
    if (binm < 660) & (binm >= 440) :
        patch.set_facecolor('orange')
    if (binm < 440) & (binm >= 270) :
        patch.set_facecolor('yellow')
    if (binm < 270) & (binm >= 100) :
        patch.set_facecolor('green')
    if binm <100:
        patch.set_facecolor('blue')

ax.set_title('Pioneer Burn severity index histogram within fire contour', fontsize=12)

#==============================================================================
# Acres reported by officials: 132,127 acres

# Acreage of a square meter
acrem = 0.000247105

# Compute burn severity category respective acreage relative to total burned pixels
total_within_contour = fire_mask.sum()*30*30*acrem
total = (burned_pixels>=100).sum()*30*30*acrem
low = ((burned_pixels >=100) & (burned_pixels <270)).sum()*30*30*acrem
mlow = ((burned_pixels >=270) & (burned_pixels <440)).sum()*30*30*acrem
mhigh =((burned_pixels >=440) & (burned_pixels <660)).sum()*30*30*acrem
high = ((burned_pixels >=660)).sum()*30*30*acrem

print('total acres within perimeter', total_within_contour)
print('total burned acres', total)
print('low severity', low/total)
print('mlow severity', mlow/total)
print('mhigh severity', mhigh/total )
print('high severity',  high/total  )
print('not burned', (burned_pixels<100).sum()*30*30*acrem/total)

# Compute burn acreage estimation percent error
actual = 188404
ac_err = (total-actual)/actual*100

print('Acreage estimation percent error: %0.2f' %ac_err)
#==============================================================================

# Plot these relative stats as a pie chart using pylab

acreages = [low/total*100, mlow/total*100, mhigh/total*100, high/total*100]
labels = ['Low', 'Moderate-low', 'Moderate-high', 'High']
explode=(0, 0, 0, 0.05)
facecolor = ['green', 'yellow', 'orange', 'red']
pie(acreages,  explode=explode, labels=labels, colors = facecolor,
                 autopct='%.1f%%',shadow=True, startangle=90)

title('Burn severity area fractions')
fname = 'soberanes_pie_chart.png'
plt.savefig(fname, bbox_inches='tight')
#==============================================================================


