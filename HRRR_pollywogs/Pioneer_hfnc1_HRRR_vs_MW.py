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


def get_HRRR(datadir,forecast_hour,station):
    """
    datadir is the location of the files    
    forecast_hour is a string, either '00', '06', or '12'
    station is the MesoWest station ID
    """    
    
    HRRRfxx = datadir+forecast_hour+'/'+forecast_hour+'_'+stn+'.csv'
    f = np.genfromtxt(HRRRfxx,names=True,dtype=None,delimiter=',')
    f_dates = f[stn]
    f_DATES = np.array([])
    for j in f_dates:
        converted_time = datetime.strptime(j,'%Y-%m-%d %H:%M')
        f_DATES = np.append(f_DATES,converted_time)
        
    temp = f['temp']
    dwpt = f['dwpt']
    u = f['u']
    v = f['v']
    speed = f['speed']
    
    a = {'forecast hour':forecast_hour,
         'dates':f_DATES,         
         'station':station,         
         'temp':temp,
         'dwpt':dwpt,
         'u':u,
         'v':v,
         'speed':speed}
    
    return a

def get_MesoWest(datadir,station):
    """
    datadir is the file location
    station is the MesoWest ID
    """
    MW = datadir+'MW_'+stn+'.csv'
    f = np.genfromtxt(MW,names=True,dtype=None,delimiter=',')
    f_dates = f[stn]
    f_DATES = np.array([])
    for j in f_dates:
        converted_time = datetime.strptime(j,'%Y-%m-%d %H:%M')
        f_DATES = np.append(f_DATES,converted_time)
    mw_dates = f['MW_time']
    mw_DATES = np.array([])
    for j in mw_dates:
        converted_time = datetime.strptime(j,'%Y-%m-%d %H:%M')
        mw_DATES = np.append(mw_DATES,converted_time)

    
    temp = f['temp']
    dwpt = f['dwpt']
    u = f['u']
    v = f['v']
    speed = f['speed']
    
    a = {'dates':f_DATES,
         'MW dates':mw_DATES,         
         'station':station,         
         'temp':temp,
         'dwpt':dwpt,
         'u':u,
         'v':v,
         'speed':speed}
    
    return a

# Which Station??
station = ['HFNC1','TT029']
for stn in station:

    # get the data    
    datadir = 'B:/public_html/oper/HRRR_fires/PIONEER_18-Jul-16/'    
    
    MW = get_MesoWest(datadir,stn)
    f00 = get_HRRR(datadir,'f00',stn)
    f06 = get_HRRR(datadir,'f06',stn)
    f12 = get_HRRR(datadir,'f12',stn)

    
    # trim for the period we want
    begin_dt = datetime(2016,8,5)
    end_dt = datetime(2016,8,6)
    
    MW_idx = np.logical_and(MW['dates']>begin_dt,MW['dates']<end_dt)
    f00_idx = np.logical_and(f00['dates']>begin_dt,f00['dates']<end_dt)
    f06_idx = np.logical_and(f06['dates']>begin_dt,f06['dates']<end_dt)
    f12_idx = np.logical_and(f12['dates']>begin_dt,f12['dates']<end_dt)
    
    
    # Plot the comparison
    fig = plt.figure(1)
    plt.clf()  
    plt.cla()
    ax = fig.add_subplot(111)
    ax.plot(MW['dates'][MW_idx],MW['temp'][MW_idx], lw=2, color='k',label='MesoWest')    
    ax.plot(f00['dates'][f00_idx],f00['temp'][f00_idx], color='r',lw=1.5,label='f00')
    ax.plot(f06['dates'][f06_idx],f06['temp'][f06_idx], color='b',lw=1,label='f06')    
    ax.plot(f12['dates'][f12_idx],f12['temp'][f12_idx], color='g',lw=.5,label='f12')          
    plt.title(stn)
    plt.grid()
    plt.ylabel('Temperature (c)')
    plt.legend()
    
    ##Format Ticks##
    ##----------------------------------
    from matplotlib.dates import DateFormatter, YearLocator, MonthLocator, DayLocator, HourLocator
    # Find months
    months = MonthLocator()
    # Find days
    days = DayLocator(bymonthday=[1,15])
    days = DayLocator(bymonthday=range(0,31))
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
    ax.plot(MW['dates'][MW_idx],MW['dwpt'][MW_idx], lw=2, color='k',label='MesoWest')    
    ax.plot(f00['dates'][f00_idx],f00['dwpt'][f00_idx], color='r',lw=1.5,label='f00')
    ax.plot(f06['dates'][f06_idx],f06['dwpt'][f06_idx], color='b',lw=1,label='f06')    
    ax.plot(f12['dates'][f12_idx],f12['dwpt'][f12_idx], color='g',lw=.5,label='f12')
    plt.title(stn)
    plt.grid()
    plt.ylabel('Dew Point (c)')
    plt.legend()
    
    ##Format Ticks##
    ##----------------------------------
    from matplotlib.dates import DateFormatter, YearLocator, MonthLocator, DayLocator, HourLocator
    # Find months
    months = MonthLocator()
    # Find days
    days = DayLocator(bymonthday=range(0,31))
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
    ax.plot(MW['dates'][MW_idx],MW['speed'][MW_idx], lw=2, color='k',label='MesoWest')    
    ax.plot(f00['dates'][f00_idx],f00['speed'][f00_idx], color='r',lw=1.5,label='f00')
    ax.plot(f06['dates'][f06_idx],f06['speed'][f06_idx], color='b',lw=1,label='f06')    
    ax.plot(f12['dates'][f12_idx],f12['speed'][f12_idx], color='g',lw=.5,label='f12')
    plt.title(stn)
    plt.grid()
    plt.ylabel('Wind Speed (m/s)')
    plt.legend()
    
    ##Format Ticks##
    ##----------------------------------
    from matplotlib.dates import DateFormatter, YearLocator, MonthLocator, DayLocator, HourLocator
    # Find months
    months = MonthLocator()
    # Find days
    days = DayLocator(bymonthday=range(1,31))
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