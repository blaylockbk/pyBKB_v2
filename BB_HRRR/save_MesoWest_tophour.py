## Brian Blaylock

## 26 July 2016

# read the HRRR analysis csv created and plot against the MesoWest observations

import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.dates import DateFormatter, YearLocator, MonthLocator, DayLocator, HourLocator

import os
import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB')  #for running on CHPC boxes
sys.path.append('B:\pyBKB')

from BB_MesoWest import MesoWest_stations_nearesttime
import wind_calcs


def append_MW(start_time,out_dir,stn,date_str,MW_temp,MW_dwpt,MW_u,MW_v,MW_speed):
    # The first column will match the HRRR time. The last Column is the actual MW time used.    
    HRRR_str = start_time.strftime('%Y-%m-%d %H:%M')    
    
    # save the file to a .csv file
    # first check if it exists:
    MW_file = out_dir + 'MW_'+stn+'.csv'
    #print MW_file
    if not os.path.isfile(MW_file):
    # if it doesn't exist, make the header, like so...
        write_header = open(MW_file,'a')
        header = '%s,temp,dwpt,u,v,speed,MW_time\n'%(stn)
        write_header.write(header)
        write_header.close()
    else:
    # if it does exist, then check the last time in the file.
    # If the last entry is greater than what we've requested,
    # then go to next hour and continue the loop.
        # What is the last entry? Open the file and find out...
        all_lines = np.genfromtxt(MW_file,names=True,dtype=None,delimiter=',')                
        try: # use a try statement because if we just created the file there isn't a last line in the file
            # get the last line
            last_line_date = datetime.strptime(all_lines[-1][0],'%Y-%m-%d %H:%M')
        except:
            # ok, if the last line doesn't exist (we have barley created the file) then
            # just set the last_line_date to much earlier (my birthday) so it will be less than the request date
            last_line_date = datetime(1989,12,13)                
        
        if last_line_date >= start_time:
            print stn,"thanks for playing, but we already have that date. requested:", start_time,'last_line',last_line_date
            start_time = start_time + timedelta(hours=1)
            return None
    
    
    # Save the line in the .csv file
    line = '%s,%s,%s,%s,%s,%s,%s\n' % (HRRR_str,MW_temp,MW_dwpt,MW_u,MW_v,MW_speed,date_str) 
    stn_file = open(MW_file,'a')
    stn_file.write(line)
    stn_file.close()
    


def save_MesoWest_tophour(stations,out_dir,start_API,end_API):
    """
    saves MesoWest observations for a station at the top of the 
    hour to compare with HRRR analyses and forecasts.
    
    stations: a numy list of stations
    out_dir: where you want to save the MesoWest data, usually in fire_dir
    start_API: a string date you want to start
    end_API: the end date you want to stop
    """    
    
    
    # list of dates:
    start_time = datetime.strptime(start_API,'%Y%m%d%H%M')
    end_time = datetime.strptime(end_API,'%Y%m%d%H%M')
    


    # Convert the stations list to a stations string separated by a comma for the API call
    stn_str = ''    
    for i in stations:
        stn_str = stn_str+i+','
        
    while start_time < datetime(end_time.year,end_time.month,end_time.day):
        request_time = start_time.strftime('%Y%m%d%H%M')
        print request_time
        a = MesoWest_stations_nearesttime.get_mesowest_nearesttime(request_time,'40,40',stn_str,v=False)
        
        
        
        #loop each station
        for s in range(0,len(a['STNID'])):                
            stn = a['STNID'][s]

            try:
                MW_DATES = a['DATES'][s]
                date_str = MW_DATES.strftime('%Y-%m-%d %H:%M') #save the date in the file as the valid time.
            except:
                MW_DATES = start_time #if there isn't a MW date then put the tophour in as a place holder. We'll know there is no data because of the nan value in the temp array
                date_str = MW_DATES.strftime('%Y-%m-%d %H:%M') #save the date in the file as the valid time.
            try:            
                MW_temp = a['TEMP'][s]     
            except:
                MW_temp = [np.nan]
            try:
                MW_dwpt = a['DWPT'][s]
            except:
                MW_dwpt = [np.nan]
            try:
                MW_speed = a['WIND_SPEED'][s]
            except:
                MW_speed = [np.nan]
            try:
                MW_dir = a['WIND_DIR'][s]
            except:
                MW_dir = [np.nan]
            try:
                MW_u, MW_v = wind_calcs.wind_spddir_to_uv(a['WIND_SPEED'][s],a['WIND_DIR'][s])
            except:
                MW_u = [np.nan]
                MW_v = [np.nan]
            
            # Append the fiel via the function append_MW            
            append_MW(start_time,out_dir,stn,date_str,MW_temp,MW_dwpt,MW_u,MW_v,MW_speed)
        
        # If the station doesn't exist then you need to fill in the data        
        for stn in stations:
            if (stn in a['STNID'])==False:
                # No MesoWest Time, so fill hour with NaNs
                print "!! Skipped",stn,start_time
                append_MW(start_time,out_dir,stn,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan)
    
        # now do the next time
        start_time = start_time + timedelta(hours=1)
                    
    return a    
        
        
if __name__=='__main__':
    stations=['KSLC','UKBKB']
    out_dir ='./test/'
    
    a = save_MesoWest_tophour(stations,out_dir,'20160730','20160801')