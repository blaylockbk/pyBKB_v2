## Brian Blaylock

## 26 July 2016

## HRRR analysis and forecast verification tables

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB')  #for running on CHPC boxes
sys.path.append('B:\pyBKB')  

from BB_MesoWest.MesoWest_STNinfo import get_mesowest_stn
from functions_domains_models import get_domain


import pygrib #requires the CHPC python version --% module load python/2.7.3
import numpy as np
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap


def KtoC(Tk):
    return Tk-273.15

#------------------------------------------------------------------
# Create a list of MesoWest station ID's we want to verfiy
#------------------------------------------------------------------
#! Could use the MesoWest API to auto generate this list for a state or set of organizations

STIDs = 'KSLC,UKBKB,WBB,UT12,NAA'

# Get the latitude and longitude for those stations
a = get_mesowest_stn(STIDs)
print a['lon']
print a['lat']



#------------------------------------------------------------------
# Now find thse station locations on the HRRR Grid
#------------------------------------------------------------------

# Open a HRRR file
request_date = datetime(2016,5,14,7)

while request_date < datetime.now():
    date_str = request_date.strftime('%Y-%m-%d %H:%M')
    print date_str    
    
    y = request_date.year
    m = request_date.month
    d = request_date.day
    h = request_date.hour
    f = 0
    
    # Open a file
    DIR = '/uufs/chpc.utah.edu/common/home/horel-group/archive/%04d%02d%02d/models/hrrr/' % (y,m,d)
    FILE = 'hrrr.t%02dz.wrfsfcf%02d.grib2' % (h,f)
    
    grbs = pygrib.open(DIR+FILE)
    
    lat, lon = grbs.select(name='2 metre temperature')[0].latlons()
    #orography = grbs.select(name='Orography')[0].values #this just takes extra time and we don't really need it
    
    u = grbs.select(name='10 metre U wind component')[0].values    # m/s
    v = grbs.select(name='10 metre V wind component')[0].values    # m/s
    speed = np.sqrt(u**2+v**2)
    temp = KtoC(grbs.select(name='2 metre temperature')[0].values)
    dwpt = KtoC(grbs.select(name='2 metre dewpoint temperature')[0].values)
    
    lat = np.array(lat)
    lon = np.array(lon)
    
    # minimum function finds where both lat/lon are a minimum
    
    
    
    domain = get_domain('full_utah')
    m = Basemap(resolution='i',projection='cyl',\
                llcrnrlon=domain['bot_left_lon'],llcrnrlat=domain['bot_left_lat'],\
                urcrnrlon=domain['top_right_lon'],urcrnrlat=domain['top_right_lat'],)
    #m.pcolormesh(lon,lat,orography)
    m.drawstates()
    m.drawcoastlines()
    m.drawcounties()
    
    
    for i in range(0,len(a['lat'])):
        
        # Figure out the nearest lat/lon in the HRRR domain for the station location
        abslat = np.abs(lat-a['lat'][i])
        abslon = np.abs(lon-a['lon'][i])
        c = np.maximum(abslon,abslat)   #element-wise maxima. Plot this with pcolormesh to see what I've done.
        latlon_idx = np.argmin(c)       #the minimum maxima (which which is the nearest lat/lon)  
        
        # Use that index (that's the flattened array index) to get the value of each variable at that point
        HRRR_lat = lat.flat[latlon_idx]
        HRRR_lon = lon.flat[latlon_idx]
        HRRR_u = u.flat[latlon_idx]
        HRRR_v = v.flat[latlon_idx]
        HRRR_speed = speed.flat[latlon_idx]
        HRRR_temp = temp.flat[latlon_idx]
        HRRR_dwpt = dwpt.flat[latlon_idx]
    
        # Plot a point at the station and the HRRR grid used (bottom left corner)
        m.scatter(HRRR_lon,HRRR_lat,s=150)
        m.scatter(a['lon'][i],a['lat'][i],s=100,c='red')
        
        # Append the verification csv for the station
        ver_file = './2016/Anal_'+a['station id'][i]+'.csv'
        if not os.path.isfile(ver_file):
            write_header = open(ver_file,'a')
            header = '%s,temp,dwpt,u,v,speed\n'%(a['station id'][i])
            write_header.write(header)
            write_header.close()
                
        line = '%s,%s,%s,%s,%s,%s\n' % (date_str,HRRR_temp,HRRR_dwpt,HRRR_u,HRRR_v,HRRR_speed) 
        stn_file = open('./2016/Anal_'+a['station id'][i]+'.csv','a')
        stn_file.write(line)
        stn_file.close()
        
    request_date = request_date + timedelta(hours=1)
    

plt.show() #for the purpose of proving that the station in near the HRRR grid used to verify
