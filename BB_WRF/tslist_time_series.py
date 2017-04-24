# Brian Blaylock
# 7 December 2015

# Plot a timeseries of observed (from MesoWest API) and WRF wind and temperature variables
# This version has the ability to plot two different WRF outputs.

from functions import wind_calcs, MesoWest_timeseries, WRF_timeseries, read_tslist, WRF_timeseries
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, YearLocator, MonthLocator, DayLocator, HourLocator

timer1 = datetime.now()

start_date_early = datetime(2015,6,17,0)
start_date = datetime(2015,6,17,0)
end_date = datetime(2015,6,19,7)

FIGDIR = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/MS/timeseries/early/303/'
# Get list of TS station id
tslist = '/uufs/chpc.utah.edu/common/home/horel-group4/model/bblaylock/WRF3.7_lake303_ember/WRFV3/test/em_real/tslist'
ts = read_tslist.read_tslist(tslist)
station_IDs = ts[1]
station_names = ts[0]
station = 'UKBKB'


for i in np.arange(14,len(station_IDs)):    
    plt.cla()
    plt.clf()
    plt.close()

    station = station_IDs[i]    
    print "Working on", station
    station_name = station_names[i]
    if station =='USDR1' or station =='QHV':
        print "skipped"
        pass
    
    # Get observed timeseries data
    obs = MesoWest_timeseries.get_mesowest_ts(station,start_date_early,end_date)
    obs_dates = obs['datetimes']
    obs_spd = obs['wind speed']
    obs_dir = obs['wind direction']
    obs_temp = obs['temperature']
    # calculate the U and V components from wind speed
    obs_u, obs_v = wind_calcs.wind_spddir_to_uv(obs_spd,obs_dir)
    
    # Get the WRF timeseries data
    wrf_dir = '/uufs/chpc.utah.edu/common/home/horel-group4/model/bblaylock/WRF3.7_lake299_ember/WRFV3/test/em_real/'
    wrf_name='lake299'
    wrf_temp = WRF_timeseries.get_ts_data(wrf_dir+station+'.d02.TS','t')-273.15
    wrf_u = WRF_timeseries.get_ts_data(wrf_dir+station+'.d02.TS','u')
    wrf_v = WRF_timeseries.get_ts_data(wrf_dir+station+'.d02.TS','v')
    wrf_time = WRF_timeseries.get_ts_data(wrf_dir+station+'.d02.TS','ts_hour')
    # calculate the wind speed and direction from u and v
    wrf_spd = wind_calcs.wind_uv_to_spd(wrf_u,wrf_v)
    wrf_dir = wind_calcs.wind_uv_to_dir(wrf_u,wrf_v)
    # convert wrf_time to datetime
    wrf_dates = np.array([])
    for i in wrf_time:
        wrf_dates = np.append(wrf_dates,start_date+timedelta(hours=i))
        
        
    # Get the WRF timeseries data for a second series
    wrf_dir2 = '/uufs/chpc.utah.edu/common/home/horel-group4/model/bblaylock/WRF3.7_lake303_ember/WRFV3/test/em_real/'
    wrf_name2='lake303'
    wrf_temp2 = WRF_timeseries.get_ts_data(wrf_dir2+station+'.d02.TS','t')-273.15
    wrf_u2 = WRF_timeseries.get_ts_data(wrf_dir2+station+'.d02.TS','u')
    wrf_v2 = WRF_timeseries.get_ts_data(wrf_dir2+station+'.d02.TS','v')
    wrf_time2 = WRF_timeseries.get_ts_data(wrf_dir2+station+'.d02.TS','ts_hour')
    # calculate the wind speed and direction from u and v
    wrf_spd2 = wind_calcs.wind_uv_to_spd(wrf_u2,wrf_v2)
    wrf_dir2 = wind_calcs.wind_uv_to_dir(wrf_u2,wrf_v2)
    # convert wrf_time to datetime
    wrf_dates2 = np.array([])
    for i in wrf_time2:
        wrf_dates2 = np.append(wrf_dates2,start_date_early+timedelta(hours=i))
        
        
        
    # Make a 3x3 plot
    plt.figure(1, figsize=(18,10))    
    plt.suptitle(station_name+' '+station+' June 17 00z - June 19 07z', fontsize=20)
    # Plot wind speed, u and v
    ax1 = plt.subplot(3,3,1)
    plt.plot(obs_dates,obs_spd, color='r',label=station+' observed')
    plt.plot(wrf_dates,wrf_spd, color='g',label=station+' WRF '+wrf_name )
    plt.plot(wrf_dates2,wrf_spd2, color='b',label=station+' WRF '+wrf_name2 )
    plt.title('Wind Speed')
    plt.ylim([0,10])
    plt.ylabel('Wind Speed (m/s)')
    
    ax2 = plt.subplot(3,3,2)
    plt.plot(obs_dates,obs_u,color='r',label=station+' observed')
    plt.plot(wrf_dates,wrf_u,color='g',label=station+' WRF '+wrf_name )
    plt.plot(wrf_dates2,wrf_u2,color='b',label=station+' WRF '+wrf_name2 )
    plt.title('U')
    plt.ylim([-10,10])
    
    ax3 = plt.subplot(3,3,3)
    plt.plot(obs_dates,obs_v,color='r',label=station+' observed')
    plt.plot(wrf_dates,wrf_v,color='g',label=station+' WRF '+wrf_name )
    plt.plot(wrf_dates2,wrf_v2,color='b',label=station+' WRF '+wrf_name2 )
    plt.axhline(0,color='r',ls='--')
    plt.title('V')
    plt.ylim([-10,10])
    

    
    
    
    # Plot MesoWest-like wind plots
    ax4 = plt.subplot(3,3,4)
    plt.title("Observed Winds")
    ax4.plot(obs_dates, obs_spd, label = 'Wind Speed', linewidth="2", color="red")
    ax4.set_ylim([0,10])
    #ax4.plot(DATES, wind_gust, '--', label = 'Wind Gust', linewidth="2", color="red")
    ax4a = ax4.twinx()
    ax4a.plot(obs_dates, obs_dir, 'og', markersize=3, label='Wind Direction')
    #ax4.legend(loc='upper left')
    #ax4a.legend(loc='upper right')
    ax4.grid()
    ax4.set_xlabel("")
    ax4a.set_ylim([0,360])
    ax4a.set_yticks([0,45,90,135,180,225,270,315,360])
    ax4a.set_yticklabels(['N','NE','E','SE','S','SW','W','NW','N'])
    ax4.set_ylabel("Wind Speed (m/s)")
    
    
    
    ax5 = plt.subplot(3,3,5)
    plt.title("WRF winds "+wrf_name)
    ax5.plot(wrf_dates, wrf_spd, label = 'Wind Speed', linewidth="2", color="green")
    ax5.set_ylim([0,10])
    #ax4.plot(DATES, wind_gust, '--', label = 'Wind Gust', linewidth="2", color="red")
    ax5a = ax5.twinx()
    ax5a.plot(wrf_dates, wrf_dir, 'og', markersize=3, label = 'Wind Direction')
    #ax4.legend(loc='upper left')
    #ax4a.legend(loc='upper right')
    ax5.grid()
    ax5.set_xlabel("")
    ax5a.set_ylim([0,360])
    ax5a.set_yticks([0,45,90,135,180,225,270,315,360])
    ax5a.set_yticklabels(['N','NE','E','SE','S','SW','W','NW','N'])
    ax5.set_ylabel("Wind Speed (m/s)")
    
    
    ax6 = plt.subplot(3,3,6)
    plt.title("WRF winds "+wrf_name2)
    ax6.plot(wrf_dates2, wrf_spd2, label = 'Wind Speed', linewidth="2", color="blue")
    ax6.set_ylim([0,10])
    #ax4.plot(DATES, wind_gust, '--', label = 'Wind Gust', linewidth="2", color="red")
    ax6a = ax6.twinx()
    ax6a.plot(wrf_dates2, wrf_dir2, 'og', markersize=3, label = 'Wind Direction')
    #ax4.legend(loc='upper left')
    #ax4a.legend(loc='upper right')
    ax6.grid()
    ax6.set_xlabel("")
    ax6a.set_ylim([0,360])
    ax6a.set_yticks([0,45,90,135,180,225,270,315,360])
    ax6a.set_yticklabels(['N','NE','E','SE','S','SW','W','NW','N'])
    ax6.set_ylabel("Wind Speed (m/s)")
    
    
    # Temperature Plot
    ax7 = plt.subplot(3,3,7)
    plt.title('Temperature')
    plt.plot(obs_dates,obs_temp,color='r',label=station+' observed')
    plt.plot(wrf_dates,wrf_temp,color='g',label=station+' WRF '+wrf_name )
    plt.plot(wrf_dates2,wrf_temp2,color='b',label=station+' WRF '+wrf_name2 )
    plt.ylabel('Temperature (C)')    
    
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5),prop={'size':10})
    
    
    
    # Format Ticks
    # Find months
    months = MonthLocator()
    # Find days
    days = DayLocator([1])
    # Find each 0 and 12 hours
    hours = HourLocator(byhour=[0,3,6,9,12,15,18,21])
    # Find all hours
    hours_each = HourLocator()
    
    # Tick label format style
    dateFmt = DateFormatter('%H')
    
    # Set the x-axis major tick marks
    ax1.xaxis.set_major_locator(hours)
    ax1.xaxis.set_minor_locator(hours_each)
    # Set the x-axis labels
    ax1.xaxis.set_major_formatter(dateFmt)
    
    # Set the x-axis major tick marks
    ax2.xaxis.set_major_locator(hours)
    ax2.xaxis.set_minor_locator(hours_each)
    # Set the x-axis labels
    ax2.xaxis.set_major_formatter(dateFmt)
    
    # Set the x-axis major tick marks
    ax3.xaxis.set_major_locator(hours)
    ax3.xaxis.set_minor_locator(hours_each)
    # Set the x-axis labels
    ax3.xaxis.set_major_formatter(dateFmt)
    
    # Set the x-axis major tick marks
    ax4.xaxis.set_major_locator(hours)
    ax4.xaxis.set_minor_locator(hours_each)
    # Set the x-axis labels
    ax4.xaxis.set_major_formatter(dateFmt)
    
    # Set the x-axis major tick marks
    ax5.xaxis.set_major_locator(hours)
    ax5.xaxis.set_minor_locator(hours_each)
    # Set the x-axis labels
    ax5.xaxis.set_major_formatter(dateFmt)
    
    # Set the x-axis major tick marks
    ax6.xaxis.set_major_locator(hours)
    ax6.xaxis.set_minor_locator(hours_each)
    # Set the x-axis labels
    ax6.xaxis.set_major_formatter(dateFmt)
    
    # Set the x-axis major tick marks
    ax7.xaxis.set_major_locator(hours)
    ax7.xaxis.set_minor_locator(hours_each)
    # Set the x-axis labels
    ax7.xaxis.set_major_formatter(dateFmt)
    
    plt.savefig(FIGDIR+station+"_lake299.png", bbox_inches='tight') 

    print 'saved',station
timer2 = datetime.now()
print "Completed in:", (timer2-timer1).seconds/60, " minutes"
