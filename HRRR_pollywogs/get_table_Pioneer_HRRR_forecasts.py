## Brian Blaylock
## 28 September 2016

# Grab the HRRR values at a point for every forecast hour 
# from an initial time

from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt

import os
import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB')  #for running on CHPC boxes
sys.path.append('B:\pyBKB')  # local path for testing on my machine 

from BB_HRRR.save_HRRR_MesoWest_point_FIRES import save_HRRR_MesoWest_point_EXTRA_WIND
from BB_MesoWest.MesoWest_stations_radius import get_mesowest_radius_stations, get_mesowest_stations

# What stations
stations  = ['HFNC1','TT029']


request_date = datetime(2016,8,3,0) 
request_end = datetime(2016,8,6,12)
#request_date = datetime(2016,7,28) # earliest available day for HRRR forecasts. Can do earlier if you only do forecasts = ['f00']

# Start the fires dict with the extra other stations we wish to verify
start_API = request_date.strftime('%Y%m%d') 
end_API = request_end.strftime('%Y%m%d')
start_API2 = request_date.strftime('%Y%m%d%H%M') 
end_API2 = datetime.now().strftime('%Y%m%d%H%M')
extraAPI = '&varoperator=or&vars=wind_speed,wind_direction,air_temp,dew_point_temperature'
stn_str = 'HFNC1,TT029'
b = get_mesowest_stations(start_API+','+end_API,stn_str,extra=extraAPI,v=False)


# What is the Lat/Lon of these stations?
lats = b['LAT']
lons = b['LON']

# initialize time
# Plot station locations
lats = [44.027889,43.960083] 
lons = [-115.803917,-115.687]
stnid = ['HFNC1','TT029']
elev = [6294,8142] # feet

B = {'STNID':np.array(['HFNC1','TT029']),
     'LON':np.array([-115.803917,-115.687]),
     'LAT':np.array([44.027889,43.960083]),
     'ELEVATION':np.array([6294,8142])*0.3048 # feet converted to meters
    }


fires_dict = {}
fires_dict['Other'] = {'stations':B,   
                      'f_name':'', #since these aren't for a fire, these are the directory we will save the other stations in.
                      's_DATE':'',
                      'f_lat':np.nan,
                      'f_lon':np.nan
                      }

base_dir = './line_forecasts/EXTRA_WINDS/'
if not os.path.exists(base_dir):
        os.makedirs(base_dir)


# Get HRRR
forecasts = ['f00','f01','f02','f03','f04','f05','f06','f07','f08','f09','f10','f11','f12','f13','f14','f15','f16','f17','f18']
for forecast_hour in forecasts:
    save_HRRR_MesoWest_point_EXTRA_WIND(fires_dict,request_date,forecast_hour,base_dir,terminal_date=datetime(2016,8,9,0))

