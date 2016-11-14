## Brian Blaylock

## 27 July 2016

# Creates a .csv file of a point's temperature, dewpoint, u and v wind, and wind speed
# in the HRRR model

## TO DO: for fires that have been burning for a while, check if the 
##        .csv file exists, if it does, then we already have some data.
##        Read the last line, figure out the last date, and begin from that time.

import pygrib
import numpy as np
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

def KtoC(Tk):
    return Tk-273.15

def save_HRRR_MesoWest_point(request_date,MesoWest_stations_dict,out_dir,fig_dir,name,forecast_hour):
    """
    Opens a HRRR surface field and plucks out the temp,dwpt,u,v at a point
    (the point closest to a MesoWest station) and saves the data to a .csv file
    for later processing.
    Handels the forecast_hour so that the saved time is the valid time.
    It is left the to user to know what forecast hour it is based on
    the directory the array is saved in.
    
    Input:
        request_date = a datetime object for the starting time,
                       which begins with the fire start time and 
                       loops each hour forward until the current day.
        MesoWest_stations_dict = a dictionary of MesoWest stations
            and lat, lons. a['STNIDS'] = station IDs
            a['LAT'] and a['LON'] = lat/lon
        out_dir = the file path you save the output .csv file
        fig_dir = the file path you save the output figure to
        name = name of the fire
        forecast_hour = forecasted hour in string format: 'f##'
    """
    print "-->save_HRRR_MesoWest_point"   
    
    # The request date should be the valid time [HRRR date + the forecast hour]
    int_forecast = int(forecast_hour[1:]) #convert string forecast hour to an integer to add to date_str    
    request_date = request_date-timedelta(hours=int_forecast) # the HRRR data we are looking for is in the request time minus the forecast hour
                                                              # For example: if we request hour 6, but are looking for a 2 hour forecasts, then
                                                              # request HRRR hour 4, but get the 2nd forecast hour, which is valid for hour 6.
    
    a = MesoWest_stations_dict

    # we want to make a map of these station locations and HRRR verification points, too
    bot_left_lon = a['LON'].min()-1
    bot_left_lat = a['LAT'].min()-1
    top_right_lon = a['LON'].max()+1
    top_right_lat = a['LAT'].max()+1
    m = Basemap(resolution='i',projection='cyl',\
                llcrnrlon=bot_left_lon,llcrnrlat=bot_left_lat,\
                urcrnrlon=top_right_lon,urcrnrlat=top_right_lat,)
    #m.pcolormesh(lon,lat,orography)
    m.drawstates()
    m.drawcoastlines()
    m.drawcounties()
    
    valid_time = request_date + timedelta(hours=int_forecast) # see, we have taken the request time, added the forecast hours, to get the valid time which was our original request time before adjusting for the forecast hour
    today = datetime.now()
    while valid_time < datetime(today.year,today.month,today.day): # only loop to begining of today. We haven't downloaded all forecasts for today yet.
        
        # date_str is the date we will save in the .csv file which will be the valid time. The vaild time is the requested_date
        
        date_str = valid_time.strftime('%Y-%m-%d %H:%M') #save the date in the file as the valid time.
        print "HRRR:",date_str
        
        # Get the requested HRRR grib file, adjusted for the forecast hour.
        y = request_date.year
        m = request_date.month
        d = request_date.day
        h = request_date.hour
        f = forecast_hour
        
        # Do the GRIB stuff
        # Open a file
        DIR = '/uufs/chpc.utah.edu/common/home/horel-group/archive/%04d%02d%02d/models/hrrr/' % (y,m,d)
        FILE = 'hrrr.t%02dz.wrfsfc%s.grib2' % (h,f)
        print "getting HRRR file:",FILE
        print "requestin: ", request_date
        print "valid date:", valid_time
        
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
        
        
        # for all the stations in our station dictionary we're going to
        # 1) Create a .csv file to save stuff
        # 2) find the index of the nearest HRRR grid to the station location
        # 3) Save the varialbes to that file using the vaild time (date_str)
        
        ## ONLY OPEN THE HRRR FILE ONCE FOR ALL THE FILES.        
        
        for i in range(0,len(a['LAT'])):
            print "working on:", a['STNID'][i]        
            
            # 1)            
            # Append the verification .csv for the station [.../out_dir/f##_StnName.csv]
            ver_file = out_dir+forecast_hour+'_'+a['STNID'][i]+'.csv'
            #print ver_file
            
            # first check if it exists:
            if not os.path.isfile(ver_file):
            # if it doesn't exist, make the header, like so...
                write_header = open(ver_file,'a')
                header = '%s,temp,dwpt,u,v,speed\n'%(a['STNID'][i])
                write_header.write(header)
                write_header.close()            
             
            # What is the last entry? Open the file and find out...
            all_lines = np.genfromtxt(ver_file,names=True,dtype=None,delimiter=',')
            try: # use a try statement because if we just created the file there isn't a last line in the file
                # get the last line
                last_line_date = datetime.strptime(all_lines[-1][0],'%Y-%m-%d %H:%M')
            except:
                # ok, if the last line doesn't exist (we have barley created the file) then
                # just set the last_line_date to much earlier (my birthday) so it will be less than the request date
                last_line_date = datetime(1989,12,13)
            # if the last line's date is greater than the requested time, then we don't need to get the HRRR for this date again.
            # Just request the next hour until we find a day we don't have...
            if last_line_date >= valid_time:
            #if 0==1:
                print "thanks for playing, but we already have that date:", request_date, valid_time
                
            
            else: # get the HRRR data for the point nearest the MesoWest station                    
                # Figure out the nearest lat/lon in the HRRR domain for the station location
                abslat = np.abs(lat-a['LAT'][i])
                abslon = np.abs(lon-a['LON'][i])
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
                plt.scatter(HRRR_lon,HRRR_lat,s=40)
                plt.scatter(a['LON'][i],a['LAT'][i],s=20,c='red')
                
                # Save the line in the .csv file
                line = '%s,%s,%s,%s,%s,%s\n' % (date_str,HRRR_temp,HRRR_dwpt,HRRR_u,HRRR_v,HRRR_speed) 
                stn_file = open(ver_file,'a')
                stn_file.write(line)
                stn_file.close()
        
        # now that you have appended all the station verification file, do the next hour, until we reach the current day
        request_date = request_date + timedelta(hours=1)
        valid_time = request_date + timedelta(hours=int_forecast) # see, we have taken the request time, added the forecast hours, to get the valid time which was our original request time before adjusting for the forecast hour
        print "next hour:", request_date        
    
    # before we finish, lets save the map of the station and HRRR points to the fig directory.   
    plt.title(name)
    plt.savefig(fig_dir+name+'_map.png',bbox_inches='tight',dpi=500)


if __name__ == "__main__":
    request_date = datetime(2016,7,31,0)
    MesoWest_stations_dict = {'LAT':np.array([40.77069]),
                              'LON':np.array([-111.96503]) ,
                              'STNID':np.array(['KSLC'])    
                                }
    out_dir = './test/'
    fig_dir = './test/'
    name = 'TEST'
    forecast_hour = 'f12' 
    
    save_HRRR_MesoWest_point(request_date,MesoWest_stations_dict,out_dir,fig_dir,name,forecast_hour)