# Brian Blaylock
# 21 December 2015

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
DIR = '/uufs/chpc.utah.edu/common/home/horel-group/archive/20160805/models/hrrr/'
FILE = 'hrrr.t12z.wrfprsf00.grib2'
#FILE = 'hrrr.t12z.wrfsfcf06.grib2'

# jims files
#DIR = '/uufs/chpc.utah.edu/common/home/horel-group/archive/20160805/models/hrrr/'
#FILE = '2016080517F11hrrr.grib2'

# subhourly HRRR
DIR = './'
FILE = 'hrrr.t03z.wrfsubhf18.grib2'

grbs = pygrib.open(DIR+FILE)




# Print an inventory of the file
grbs.seek(0) #(go back to top of file)
for grb in grbs:
    grb    
    print grb  ## Yeah, we really don't need to look at all the lines. 


## ^ All that stuff above is great for learning what's in the file.
## Now lets do something with th estuff in the file
