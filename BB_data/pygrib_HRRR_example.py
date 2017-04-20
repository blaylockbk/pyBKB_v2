# Brian Blaylock
# 21 December 2015

"""
Testing the new pygrib library. Installed on CHPC on December 21, 2015
pygrib makes it possible to read data stored in grib and grib2 files

More usage documentation here: http://pygrib.googlecode.com/svn/trunk/docs/index.html

"""

import pygrib
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from datetime import datetime

# Open a file
DIR = '/uufs/chpc.utah.edu/common/home/horel-group/archive/20150618/models/hrrr/'
FILE = 'hrrr.t00z.wrfprsf00.grib2'

grbs = pygrib.open(DIR+FILE)


# Can look at messages form any line
# Puts you at the top line of the file
grbs.seek(0)

# Puts you at line 5
grbs.seek(4)

# Reads the line you are on
grbs.read(1)

# Reads three lines down your current position
grbs.read(3)

# Reads all the lines 
grbs.read()

# Print an inventory of the file
grbs.seek(0) #(go back to top of file)
for grb in grbs:
    grb    
    # print grb  ## Yeah, we really don't need to look at all the lines. 


## ^ All that stuff above is great for learning what's in the file.
## Now lets do something with th estuff in the file


# Grab geopotential height at 500 mb (just had to figure out that it's in the 18th index)
Z = grbs.select(name='Geopotential Height')[18].values

    
# Lets make a plot of each of these surface variables
variables = ['Temperature','Relative humidity','Vertical velocity']
figure_num = 1    
for v in variables:
   
   # find first grb message with a matching name
    grb = grbs.select(name=v)[-1] # <-- the number in brackets is the level [0] is model top, [-1] is surface
   
    
    # print grb. There is some good info in here, like the model level
    print grb
    
    # Now lets look at the data in this...
    
    # Look at what data is available in the keys. Try to print the values too (for some reason unknown to me not all the keys work)
    print "Available Keys..."
    
    for i in grb.keys():
        try:        
            print i, ' ...... ', grb[i]
        except:
            print 'CANT ACCESS THIS KEY. Use grb.'+i+ ' instead'
        
    print ""
    # access a key...if 'validDate' is the key you want then...
    print grb.validDate
    
    # Now lets plot something useful...
    # grab the temperature values
    temps = grb.values
    
    # lat/lon comes in as 1D array. Need to convert to the same shape as temps
    lat,lon = grb.latlons()
    
    # Plot a map of this stuff, using the Grib File map parameters
    ## These HRRR files have a lambert projection
    print grb.gridType
    lat_0 = grb.LaDInDegrees
    lon_0 = grb.LoVInDegrees-360 
    lat_1 = grb.Latin1InDegrees
    lat_2 = grb.Latin2InDegrees
    
    bot_left_lon = lon[0][0]
    bot_left_lat = lat[0][0]
    top_right_lon = lon[-1][-1]
    top_right_lat = lat[-1][-1]
    
    print ""
    print "Plotting", v
    print ""
    
    m = Basemap(resolution='i',area_thresh=10000.,projection='lcc',\
        lat_0=lat_0,lon_0=lon_0,\
        lat_1=lat_1, lat_2=lat_2,\
        llcrnrlon=bot_left_lon,llcrnrlat=bot_left_lat,\
        urcrnrlon=top_right_lon,urcrnrlat=top_right_lat,)
    
    plt.figure(num=figure_num)
    m.drawcoastlines()
    m.drawcountries()
    m.drawstates()
    
    x,y = m(lon,lat)    
    m.pcolormesh(x,y,temps)
    cb = plt.colorbar()
    cb.set_label(grb.name + " ("+grb.units+")")
    
    # Just becuase we can, add 500 mb Geopotential Height Contours on top.
    CS = m.contour(x,y,Z,colors='black',levels=np.arange(0,6000,60))
    plt.clabel(CS, inline=1, fontsize=9,fmt='%1.0f')    
    
    
    validDate = grb.validDate
    
    plt.title('Valid Date: '+validDate.strftime('%Y-%b-%d %H:%M:%S')+'\n'+
              'Variable: '+grb.name+"\n Level: "+str(grb.level))

    figure_num += 1
    

plt.show()
