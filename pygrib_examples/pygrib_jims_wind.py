# Brian Blaylock
# 25 May 2016

"""
Testing the new pygrib library. Installed on CHPC on December 21, 2015

I'm using this version of python:
/uufs/chpc.utah.edu/sys/pkg/python/2.7.3_rhel6/bin/python
(For Horel Group users, can't use the local version of python becuase pygrib isn't installed there)

If you have moduels set up you can source this verion with the following command:
module load python/2.7.3

More usage documentation here: http://pygrib.googlecode.com/svn/trunk/docs/index.html

"""

import pygrib
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from datetime import datetime

# Open a file
DIR = '/uufs/chpc.utah.edu/common/home/horel-group/archive/20160405/models/hrrr/'
FILE = '2016040500F00hrrr.grib2'

grbs = pygrib.open(DIR+FILE)



# Print an inventory of the file
grbs.seek(0) #(go back to top of file)
for grb in grbs:
    grb    
    # print grb  ## Yeah, we really don't need to look at all the lines. 


## ^ All that stuff above is great for learning what's in the file.
## Now lets do something with th estuff in the file


# Grab geopotential height at 500 mb (just had to figure out that it's in the 18th index)
u = grbs.select(name='10 metre U wind component')[0] # there is only one element of this array, still need to get the zeroth element
v = grbs.select(name='10 metre V wind component')[0] # there is only one element of this array, still need to get the zeroth element

# Total Precipt returns two items. Get the zeroth and first 
p1 = grbs.select(name='Total Precipitation')[0]
p2 = grbs.select(name='Total Precipitation')[1]

lat,lon = u.latlons()


U = u.values
V = v.values
P1 = p1.values
P2 = p2.values

speed = np.sqrt(U**2+V**2)

plt.figure(1)


bot_left_lon  = lon.min()
bot_left_lat  = lat.min()
top_right_lon = lon.max()
top_right_lat = lat.max()
m = Basemap(resolution='i',projection='cyl',\
                llcrnrlon=bot_left_lon,llcrnrlat=bot_left_lat,\
                urcrnrlon=top_right_lon,urcrnrlat=top_right_lat,)
m.drawstates()
m.drawcoastlines()
m.pcolormesh(lon,lat,speed)

plt.show()

