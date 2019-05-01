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

from BB_HRRR.save_HRRR_MesoWest_point_FIRES import save_HRRR_MesoWest_point_JIMS_WIND
from BB_MesoWest.MesoWest_stations_radius import get_mesowest_radius_stations, get_mesowest_stations

# What stations
stations = 'NAA,MTMET,QHW,O3S02,GSLBY'
stations = 'FPS,UT23,UT12,UKBKB,KPVU,UTLGP,FG005,O3S08,O3S07,GNI,UFD08,FWP,QH3,QSA,QBV,O3S04,'

request_date = datetime(2015,6,17,15) # in order to go back any further you need to untar some directories
request_end = datetime(2015,6,19,23) # the way to get around my missing archive is by getting Jim's forecasts, which only have wind and reflectivity in them.
#request_date = datetime(2016,7,28) # earliest available day for HRRR forecasts. Can do earlier if you only do forecasts = ['f00']

# Start the fires dict with the extra other stations we wish to verify
start_API = request_date.strftime('%Y%m%d') 
end_API = request_end.strftime('%Y%m%d')
start_API2 = request_date.strftime('%Y%m%d%H%M') 
end_API2 = datetime.now().strftime('%Y%m%d%H%M')
extraAPI = '&varoperator=or&vars=wind_speed,wind_direction,air_temp,dew_point_temperature'
stn_str = stations
#b = get_mesowest_stations(start_API,stn_str,v=True)
b = get_mesowest_stations(None,stations)


# What is the Lat/Lon of these stations?
lats = b['LAT']
lons = b['LON']



fires_dict = {}
fires_dict['Other'] = {'stations':b,   
                      'f_name':'', #since these aren't for a fire, these are the directory we will save the other stations in.
                      's_DATE':'',
                      'f_lat':np.nan,
                      'f_lon':np.nan
                      }

base_dir = './line_forecasts/LakeBreeze_June2015/'
if not os.path.exists(base_dir):
        os.makedirs(base_dir)


# Get HRRR
forecasts = ['f00','f01','f02','f03','f04','f05','f06','f07','f08','f09','f10','f11','f12','f13','f14','f15'] # only analysis hours are available, unless you just want Jim's Wind :(
for forecast_hour in forecasts:
    save_HRRR_MesoWest_point_JIMS_WIND(fires_dict,request_date,forecast_hour,base_dir,terminal_date=datetime(2015,6,20,0))

