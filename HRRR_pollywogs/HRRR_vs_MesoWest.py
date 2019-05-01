## Brian Blaylock

## 26 July 2016

# read the HRRR analysis csv created and plot against the MesoWest observations

import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib as mpl

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB')  #for running on CHPC boxes
sys.path.append('B:\pyBKB')

from BB_MesoWest import MesoWest_timeseries
import wind_calcs

label_font  = 10    
tick_font   = 8 
legend_font = 7

width=8  
height=2   # adjust as needed, but bbox="tight" should take care of most of this


## Reset the defaults (see more here: http://matplotlib.org/users/customizing.html)
mpl.rcParams['xtick.labelsize'] = tick_font
mpl.rcParams['ytick.labelsize'] = tick_font
mpl.rcParams['axes.labelsize'] = label_font
mpl.rcParams['legend.fontsize'] = legend_font

mpl.rcParams['figure.figsize'] = [width,height] 

mpl.rcParams['grid.linewidth'] = .25

mpl.rcParams['savefig.bbox'] = 'tight'
mpl.rcParams['savefig.dpi'] = 1000


# Which Station??
station = ['KSLC','UKBKB','WBB']
for stn in station:
    
    
    # Get the HRRR file
    HRRR = np.genfromtxt('./2016/Anal_'+stn+'.csv',names=True,dtype=None,delimiter=',')
    HRRR_dates = HRRR[stn]
    HRRR_DATES = np.array([])
    for j in HRRR_dates:
        converted_time = datetime.strptime(j,'%Y-%m-%d %H:%M')
        HRRR_DATES = np.append(HRRR_DATES,converted_time)
    
    HRRR_temp = HRRR['temp']
    HRRR_dwpt = HRRR['dwpt']
    HRRR_u = HRRR['u']
    HRRR_v = HRRR['v']
    HRRR_speed = HRRR['speed']
    
    
    # Get the MesoWest Observations for the same time period
    a = MesoWest_timeseries.get_mesowest_ts(stn,HRRR_DATES[0],HRRR_DATES[-1])
    MW_DATES = a['datetimes']
    MW_temp = a['temperature']
    MW_dwpt = a['dew point']
    MW_u,MW_v = wind_calcs.wind_spddir_to_uv(a['wind speed'],a['wind direction'])
    MW_speed = a['wind speed']
    MW_dir = a['wind direction']
    
    
    
    # Plot the comparison
    fig = plt.figure(1)
    plt.clf()  
    plt.cla()
    ax = fig.add_subplot(111)
    ax.plot(HRRR_DATES,HRRR_temp, color='k',lw=1)
    ax.plot(MW_DATES,MW_temp, lw=.5, color='r')
    plt.title(stn)
    plt.ylabel('Temperature (c)')
    
    ##Format Ticks##
    ##----------------------------------
    from matplotlib.dates import DateFormatter, YearLocator, MonthLocator, DayLocator, HourLocator
    # Find months
    months = MonthLocator()
    # Find days
    days = DayLocator(bymonthday=[1,15])
    # Find each 0 and 12 hours
    hours = HourLocator(byhour=[0,6,12,18])
    # Find all hours
    hours_each = HourLocator()
    # Tick label format style
    #dateFmt = DateFormatter('%b %d, %Y\n%H:%M')
    dateFmt = DateFormatter('%b %d\n%Y')
    # Set the x-axis major tick marks
    ax.xaxis.set_major_locator(days)
    # Set the x-axis labels
    ax.xaxis.set_major_formatter(dateFmt)
    # For additional, unlabeled ticks, set x-axis minor axis
    #ax.xaxis.set_minor_locator(hours)
    
    plt.savefig('./fig/'+stn+'_temp.png')
    
    # Plot the comparison
    fig = plt.figure(2)
    plt.clf()
    plt.cla()    
    ax = fig.add_subplot(111)
    ax.plot(HRRR_DATES,HRRR_dwpt, color='k',lw=1)
    ax.plot(MW_DATES,MW_dwpt, lw=.5, color='g')
    plt.title(stn)
    plt.ylabel('Dew Point (c)')
    
    ##Format Ticks##
    ##----------------------------------
    from matplotlib.dates import DateFormatter, YearLocator, MonthLocator, DayLocator, HourLocator
    # Find months
    months = MonthLocator()
    # Find days
    days = DayLocator(bymonthday=[1,15])
    # Find each 0 and 12 hours
    hours = HourLocator(byhour=[0,6,12,18])
    # Find all hours
    hours_each = HourLocator()
    # Tick label format style
    #dateFmt = DateFormatter('%b %d, %Y\n%H:%M')
    dateFmt = DateFormatter('%b %d\n%Y')
    # Set the x-axis major tick marks
    ax.xaxis.set_major_locator(days)
    # Set the x-axis labels
    ax.xaxis.set_major_formatter(dateFmt)
    # For additional, unlabeled ticks, set x-axis minor axis
    #ax.xaxis.set_minor_locator(hours)
    
    plt.savefig('./fig/'+stn+'_dwpt.png')
    
    # Plot the comparison
    fig = plt.figure(3)
    plt.clf()
    plt.cla()
    ax = fig.add_subplot(111)
    ax.plot(HRRR_DATES,HRRR_speed,color='k',lw=1)
    ax.plot(MW_DATES,MW_speed, lw=.5, color='b')
    plt.title(stn)
    plt.ylabel('Wind Speed (m/s)')
    
    ##Format Ticks##
    ##----------------------------------
    from matplotlib.dates import DateFormatter, YearLocator, MonthLocator, DayLocator, HourLocator
    # Find months
    months = MonthLocator()
    # Find days
    days = DayLocator(bymonthday=[1,15])
    # Find each 0 and 12 hours
    hours = HourLocator(byhour=[0,6,12,18])
    # Find all hours
    hours_each = HourLocator()
    # Tick label format style
    #dateFmt = DateFormatter('%b %d, %Y\n%H:%M')
    dateFmt = DateFormatter('%b %d\n%Y')
    # Set the x-axis major tick marks
    ax.xaxis.set_major_locator(days)
    # Set the x-axis labels
    ax.xaxis.set_major_formatter(dateFmt)
    # For additional, unlabeled ticks, set x-axis minor axis
    #ax.xaxis.set_minor_locator(hours)
    
    plt.savefig('./fig/'+stn+'_wspeed.png')