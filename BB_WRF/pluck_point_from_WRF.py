## Brian Blaylock
## 1 November 2016

## Create a time series from a point of WRF data

import numpy as np
from scipy.io import netcdf
from datetime import datetime,timedelta


def pluck_point_make_time_series(stn_lat,stn_lon,start_date,end_date,WRF_dir):
    
    base = start_date
    numhours = 48
    date_list = [base + timedelta(hours=x) for x in range(0,numhours)] 
    
    dates = np.array([])
    temps = np.array([])                 
    psfcs = np.array([]) # sea level pressures  
    lats = np.array([])
    lons = np.array([])
               
    for date in date_list:
        dates = np.append(dates,date)
        #convert datetime to a requested filename
        y = date.year
        m = date.month
        d = date.day
        H = date.hour
        M = date.minute
        file_name = 'wrfout_d02_%04d-%02d-%02d_%02d:%02d:00' % (y,m,d,H,M)
        
        # Open the file
        nc = netcdf.netcdf_file(WRF_dir+file_name)
        
        # extract some data
        lon = nc.variables['XLONG'][0]
        lat  = nc.variables['XLAT'][0]
        psfc = nc.variables['PSFC'][0] # surface pressure
        temp = nc.variables['T2'][0]
        
        elev = nc.variables['HGT'][0]
        
               
            
        # 1)  
        # get the WRF data for the point nearest the MesoWest station                    
        # Figure out the nearest lat/lon in the HRRR domain for the station location
        abslat = np.abs(lat-stn_lat)
        abslon = np.abs(lon-stn_lon)
        
        c = np.maximum(abslon,abslat)   #element-wise maxima. Plot this with pcolormesh to see what I've done.
                    
        latlon_idx = np.argmin(c)       #the minimum maxima (which which is the nearest lat/lon)  
        
        # Use that index (that's the flattened array index) to get the value of each variable at that point
        lats = np.append(lats,lat.flat[latlon_idx])
        lons = np.append(lons,lon.flat[latlon_idx])
        psfcs = np.append(psfcs,psfc.flat[latlon_idx])
        temps = np.append(temps,temp.flat[latlon_idx])
        
        elevation = elev.flat[latlon_idx]
        
    #convert surface pressure to sea level pressure
    g = 1-(0.0065*elevation/(temps+0.0065*elevation))
    slps = psfcs*g**(-5.257)
        
    return {'nc':nc,
            'temps':temps,
            'lats':lats,
            'lons':lons,
            'slps':slps,   # sea level pressures
            'pres':psfcs,  # surface pressures
            'dates':dates,
            'elevation':elevation,
            }  
    
    
    
if __name__ == '__main__':
    
    WRF_dir = '/uufs/chpc.utah.edu/common/home/horel-group4/model/bblaylock/WRF3.8.1_MYNN/DATA/'
    
    ksl_lat = 40.77069
    ksl_lon = -111.96503
    s_time = datetime(2015,6,17)
    e_time = datetime(2015,6,19)
    
    nc = pluck_point_make_time_series(ksl_lat,ksl_lon,s_time,e_time,WRF_dir)