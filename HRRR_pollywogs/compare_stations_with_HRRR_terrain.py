## Brian Blaylock
## 07 October 2016

# Compare station lat/lon and terrain height for stations with the HRRR

import numpy as np
from datetime import datetime
import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB')  #for running on CHPC boxes
sys.path.append('B:\pyBKB')  # local path for testing on my machine 

from BB_MesoWest.MesoWest_stations_radius import  get_mesowest_stations
from BB_HRRR.pluck_point_from_HRRR import pluck_point

# Start the fires dict with the extra other stations we wish to verify
#request_date = datetime(2016,7,5)
#request_end = datetime(2016,7,10)
#start_API = request_date.strftime('%Y%m%d') 
#end_API = request_end.strftime('%Y%m%d')
#start_API2 = request_date.strftime('%Y%m%d%H%M') 
#end_API2 = datetime.now().strftime('%Y%m%d%H%M')
#extraAPI = '&varoperator=or&vars=wind_speed,wind_direction,air_temp,dew_point_temperature'
#a = get_mesowest_stations(start_API+','+end_API,'HFNC1',extra=extraAPI,v=False)


## !!
## The API only returns the current location. This is an issue becuase IRAWS stations move!
# HFNC1 was at 44.027889, -115.803917, elevation 6294 ft from 7/27-10/4
# TT029 was at 43.960083, -115.687, elevation 8142 ft from 7/21-10/4

A = {'STNID':np.array(['HFNC1','TT029']),
     'LON':np.array([-115.803917,-115.687]),
     'LAT':np.array([44.027889,43.960083]),
     'ELEVATION':np.array([6294,8142])*0.3048 # feet converted to meters
    }


b = pluck_point(A,datetime(2016,8,5),'f00')

print b['terrain height']
print A['ELEVATION']

print 'stations are',b['stnid']
print 'actual elevation is', A['ELEVATION'],'meters'
print 'hrrr elevation is', b['terrain height'],'meters'
print 'actual - hrrr', A['ELEVATION']-b['terrain height'],'meters'

