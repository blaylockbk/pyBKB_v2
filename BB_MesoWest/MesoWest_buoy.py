# Brian Blaylock
# 17 Feb. 2015


# Function for getting MesoWest time series from the API for one station

import numpy as np
import datetime
import json
import urllib2


token = '2562b729557f45f5958516081f06c9eb' #Request your own token at http://mesowest.org/api/signup/

variables = 'T_water_temp,wind_direction,wind_speed,wind_gust,air_temp,dew_point_temperature,relative_humidity,ozone_concentration'

def get_mesowest_ts(start_time,end_time,stationID='GSLBY'):
    """
    Makes a time series query from the MesoWest API
    
    Input:
        stationID  : string of the station ID
        start_time : datetime object of the start time in UTC
        end_time   : datetime object of the end time in UTC
        
    Output:
        a dictionary of the data
    """

    # convert the start and end time to the string format requried by the API
    start = start_time.strftime("%Y%m%d%H%M")
    end = end_time.strftime("%Y%m%d%H%M")
    
    # The API request URL
    URL = 'http://api.mesowest.net/v2/stations/timeseries?stid='+stationID+'&start='+start+'&end='+end+'&vars='+variables+'&obtimezone=utc&token='+token
    
    print URL    
    
    ##Open URL and read the content
    f = urllib2.urlopen(URL)
    data = f.read()
    
    ##Convert that json string into some python readable format
    data = json.loads(data)
    
    # Need to do some special stuff with the dates
    ##Get date and times
    dates = data["STATION"][0]["OBSERVATIONS"]["date_time"]
    ##Convert to datetime and put into a numpy array
    DATES = np.array([]) #initialize the array to store converted datetimes    
    ##Loop through each date. Convert into datetime format and put into DATES array
    ## NOTE: only works for MDT which is 6 hours behind UTC
    for j in dates:
    	try:
    		converted_time = datetime.datetime.strptime(j,'%Y-%m-%dT%H:%M:%SZ')
    		DATES = np.append(DATES,converted_time)
    		#print 'Times are in UTC'
    	except:
    		converted_time = datetime.datetime.strptime(j,'%Y-%m-%dT%H:%M:%S-0600')
    		DATES = np.append(DATES,converted_time)
    		#print 'Times are in Local Time'    
    
    stn_name = str(data['STATION'][0]['NAME'])
    stn_id   = str(data['STATION'][0]['STID'])
    
    try:
        Water_temp1     = np.array(data['STATION'][0]["OBSERVATIONS"]["T_water_temp_set_1"],dtype=float) 
    except:
        Water_temp1 = np.ones(len(DATES))*np.nan
    try:
        Water_temp2     = np.array(data['STATION'][0]["OBSERVATIONS"]["T_water_temp_set_2"],dtype=float) 
    except:
        Water_temp2 = np.ones(len(DATES))*np.nan        
    try:
        Water_temp3     = np.array(data['STATION'][0]["OBSERVATIONS"]["T_water_temp_set_3"],dtype=float) 
    except:
        Water_temp3 = np.ones(len(DATES))*np.nan    
    try:
        Water_temp4     = np.array(data['STATION'][0]["OBSERVATIONS"]["T_water_temp_set_4"],dtype=float) 
    except:
        Water_temp4 = np.ones(len(DATES))*np.nan
    try:
        Water_temp5     = np.array(data['STATION'][0]["OBSERVATIONS"]["T_water_temp_set_5"],dtype=float) 
    except:
        Water_temp5 = np.ones(len(DATES))*np.nan
    try:
        Water_temp6     = np.array(data['STATION'][0]["OBSERVATIONS"]["T_water_temp_set_6"],dtype=float) 
    except:
        Water_temp6 = np.ones(len(DATES))*np.nan
    try:
        Water_temp7     = np.array(data['STATION'][0]["OBSERVATIONS"]["T_water_temp_set_7"],dtype=float) 
    except:
        Water_temp7 = np.ones(len(DATES))*np.nan
    try:
        Water_temp8     = np.array(data['STATION'][0]["OBSERVATIONS"]["T_water_temp_set_8"],dtype=float) 
    except:
        Water_temp8 = np.ones(len(DATES))*np.nan        
    try:
        Water_temp9     = np.array(data['STATION'][0]["OBSERVATIONS"]["T_water_temp_set_9"],dtype=float) 
    except:
        Water_temp9 = np.ones(len(DATES))*np.nan
    try:
        Water_temp10     = np.array(data['STATION'][0]["OBSERVATIONS"]["T_water_temp_set_10"],dtype=float) 
    except:
        Water_temp10 = np.ones(len(DATES))*np.nan
    try:
        Water_temp11     = np.array(data['STATION'][0]["OBSERVATIONS"]["T_water_temp_set_11"],dtype=float) 
    except:
        Water_temp11 = np.ones(len(DATES))*np.nan
    try:
        Water_temp12     = np.array(data['STATION'][0]["OBSERVATIONS"]["T_water_temp_set_12"],dtype=float) 
    except:
        Water_temp12 = np.ones(len(DATES))*np.nan
    try:
        Water_temp13     = np.array(data['STATION'][0]["OBSERVATIONS"]["T_water_temp_set_13"],dtype=float) 
    except:
        Water_temp13 = np.ones(len(DATES))*np.nan
    try:
        Water_temp14     = np.array(data['STATION'][0]["OBSERVATIONS"]["T_water_temp_set_14"],dtype=float) 
    except:
        Water_temp14 = np.ones(len(DATES))*np.nan
    try:
        Water_temp15     = np.array(data['STATION'][0]["OBSERVATIONS"]["T_water_temp_set_15"],dtype=float) 
    except:
        Water_temp15 = np.ones(len(DATES))*np.nan
        
    
    data_dict = {'DATES': DATES,
                 'STID': stn_id,
                 'NAME': stn_name,
                 'T_water1':Water_temp1,
                 'T_water2':Water_temp2,
                 'T_water3':Water_temp3,
                 'T_water4':Water_temp4,
                 'T_water5':Water_temp5,               
                 'T_water6':Water_temp6,              
                 'T_water7':Water_temp7,
                 'T_water8':Water_temp8,
                 'T_water9':Water_temp9,
                 'T_water10':Water_temp10,
                 'T_water11':Water_temp11,
                 'T_water12':Water_temp12,
                 'T_water13':Water_temp13,
                 'T_water14':Water_temp14,
                 'T_water15':Water_temp15
                }
                
    return data_dict


    
#--- Example -----------------------------------------------------------------#
if __name__ == "__main__":
    
    import matplotlib.pyplot as plt
    from matplotlib.dates import DateFormatter, YearLocator, MonthLocator, DayLocator, HourLocator
    import matplotlib as mpl
    import os    
    
    # Get MesoWest data from functin above
    station_list = ['GSLBY']
    for station in station_list:
        print station
        #plt.cla()
        #plt.clf()
        #plt.close()
        start_time = datetime.datetime(2015,6,18,12)
        end_time = datetime.datetime(2015,6,19,6)
        
        a = get_mesowest_ts(station,start_time,end_time)
        
        # Make a quick water temperature plot
        dates = a['datetimes']        
        sub40 = a['T_water1']+273.15 # 0.4m subsurface
        sub100 = a['T_water2']+273.15 # 1.0m subsurface
    
        
        #convert dates from UTC to mountain time (-6 hours)
        #dates = dates - datetime.timedelta(hours=6)
        
        
        
        tick_font = 15
        label_font = 20
        lw = 4
        
        width=12
        height=8
        
        
        mpl.rcParams['xtick.labelsize'] = tick_font
        mpl.rcParams['ytick.labelsize'] = tick_font
        
        
        fig, ax1 = plt.subplots(1,1,figsize=(width,height))
        #ax1.set_title(station+' '+a['station name']+'\n-0.4m below surface',fontsize=label_font)
           
        
        ax1.plot(dates,sub40,lw=lw,label='-0.4 m')   
        ax1.plot(dates,sub100,lw=lw-1,label='-1.0 m')   
        ax1.set_ylabel('Water Temperature (K)',fontsize=label_font)
        
        ax1.axhline(y=302)      
        ax1.axhline(y=295)      
        ax1.legend(loc='upper left',fontsize=18)    
        #ax1.set_ylim([10,40])
        ax1.set_ylim([295,302])
        ax1.grid()        

        #ax1a.legend(loc='upper right')    
        
        
        fig.subplots_adjust(hspace=.05)    
        
        
        ##Format Ticks##
        ##----------------------------------
        # Find months
        months = MonthLocator()
        # Find days
        days = DayLocator()
        # Find each 0 and 12 hours
        hours = HourLocator(byhour=[0,3,6,9,12,15,18,21])
        # Find all hours
        hours_each = HourLocator()
        # Tick label format style
        dateFmt = DateFormatter('%b %d\n%H:%M')
        blank_dateFmt = DateFormatter('')    
        # Set the x-axis major tick marks
        ax1.xaxis.set_major_locator(hours)
        # Set the x-axis labels
        ax1.xaxis.set_major_formatter(dateFmt)
        # For additional, unlabeled ticks, set x-axis minor axis
        ax1.xaxis.set_minor_locator(hours_each)
        
        
        out_dir = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/MS/laketemp/'
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        plt.savefig(out_dir+station+'_bouy.png',bbox_inches="tight",dpi=300)

        
        