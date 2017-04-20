## Brian Blaylock
## 27 June 2016

# A lot of the stations in Utah are at elevations.
# I want to plot station data on a skew-t graph to get a 
# psudo vertical profile for any time of day.

import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB')  #for running on CHPC boxes
sys.path.append('B:\pyBKB')                                        #for running on PC (B:\ is my network drive)

from BB_MesoWest import MesoWest_stations_radius as MW
from skewt_900_700 import SkewT #this version plots between 900-700 hPa
import wyoming_sounding

##############################

request_time = datetime(2016,6,29,12,0)

##############################

MWdatetime = request_time.strftime('%Y%m%d%H%M')
a = MW.get_mesowest_radius_winds(MWdatetime,'10')

p = a['PRESS']>0 #pressure is in these indexes
pres = a['PRESS'][p]/100
temp = a['TEMP'][p]
hght = a['ELEVATION'][p]
dwpt = a['TEMP'][p]*np.nan #don't get the dewpoint now
wd   = a['WIND_DIR'][p]
ws   = a['WIND_SPEED'][p]
stns = a['STNID'][p]

# sort all that data based on pressure
from operator import itemgetter
pres,temp,hght,dwpt,wd,ws,stns = zip(*sorted(zip(pres,temp,hght,dwpt,wd,ws,stns),key=itemgetter(0)))



data = {'drct':wd,
        'dwpt':dwpt,        #don't plot dwpt right now
        'hght':hght,
        'pres':pres,
        'sknt':ws,
        'temp':temp}
S=SkewT.Sounding(soundingdata=data)

S.plot_skewt(title='psudo sounding\n'+MWdatetime,color='r',lw=.8,parcel_type=None,
             pmin=700.,pmax=900.)

for i in range(0,len(stns)):
    if temp[i]>0: #wont accept nan values
        print temp[i],pres[i],stns[i]
        S.plot_point(temp[i],pres[i])
        S.plot_text(temp[i],pres[i],str(stns[i]))
        
# Add real sounding to plot

# If request_time is in the afternoon, then request the evening sounding
if request_time.hour > 18:
    # Get the evening sounding (00 UTC) for the next day
    next_day = request_time + timedelta(days=1)
    request_sounding = datetime(next_day.year,next_day.month,next_day.day,0)    
elif request_time.hour < 6:
    # Get the evening sounding (00 UTC) for the same
    request_sounding = datetime(request_time.year,request_time.month,request_time.day,0)    
else:
    # Get the morning sounding (12 UTC) for the same day
    request_sounding = datetime(request_time.year,request_time.month,request_time.day,12)

print "SLC sounding for", request_sounding

a = wyoming_sounding.get_sounding(request_sounding)
balloon = {'drct':a['wdir'],
           #'dwpt':a['dwpt'],
           'hght':a['height'],
           'pres':a['press'],
           'sknt':a['wspd'],
           'temp':a['temp']}
# Add to plot
T = SkewT.Sounding(soundingdata=balloon)
S.soundingdata=T.soundingdata
S.add_profile(color='g',lw=.9,bloc=1.2)

             
