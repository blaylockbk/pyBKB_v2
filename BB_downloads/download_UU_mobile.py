## Brian Blaylock
## Downloads mobile ozone data collected by the University of Utah Mt. Met group for the
## KSL helicopter (KSL5), UTA TRAX (TRX01, TRX01), and other vehicles (UUTK01, UUTK02, UUTK03, UUPOM, UNERD)

import numpy as np
import linecache
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
import urllib2

def download_mobile(platform,requested_time,previous_mins='30'):
    """
    Downloads mobile data from online and saves a temporary text file.
    Reads the text file, then deletes the temporary text file when completed.
    
    """
    # platform = 'KSL5', 'TRX01'
    
    year = str(requested_time.year).zfill(4)
    month= str(requested_time.month).zfill(2)
    day = str(requested_time.day).zfill(2)
    hour = str(requested_time.hour).zfill(2)
    minute = str(requested_time.minute).zfill(2)
    previous_mins = str(previous_mins)   
    
    url = 'http://meso2.chpc.utah.edu/gslso3s/cgi-bin/download_mobile_data.cgi?yr='+year+'&mo='+month+'&dy='+day+'&hr='+hour+'&mm='+minute+'&min='+previous_mins+'&stid='+platform

    print url

    rawdata = urllib2.urlopen(url).read()
    splitted = rawdata.split("\n",rawdata.count("\n"))
    
    # Save a text file of the data (this makes reading it easy, and I don't have to change my code I've already written)
    data_dir = './'
    filename = platform+'_'+year+month+day+hour+minute+'.txt'
    f = open(data_dir+filename,'w')
    for line in splitted[:]:
        f.write(line+'\n')
    f.close()   
    
    # Read File
    col_names = linecache.getline(filename,2)
    
    try:
        data = np.genfromtxt(filename,skip_header=2, names = col_names,delimiter=',',dtype=None)

    
        # Convert Dates and Times to Datetime Object
        DATES = np.array([])
        for i in range(0,len(data['Date'])):
            a = data['Date'][i]+' '+data['TimeUTC'][i]    
            b = datetime.strptime(a,'%Y-%m-%d %H:%M:%S')
            DATES = np.append(DATES,b)
            
        ozone = data['2b_ozone_ppbv']
        ozone[ozone<0]=np.nan
        lat = data['cr1000_gpslat_dd']
        lon = data['cr1000_gpslon_dd']
        elevation = data['cr1000_gpselev_m']
        try:    
            pressure = data['cr1000_pres_hpa']
        except:
            pressure = np.zeros(len(DATES))*np.nan
        
        os.remove(filename)
        
        return {'DATES':DATES,
                'ozone':ozone,
                'latitude':lat,
                'longitude':lon,
                'elevation':elevation,
                'pressure':pressure    
                }
    except:
        data = 'No Data Available from '+platform+' at this time'
        return data    
