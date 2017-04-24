# Brian Blaylock
# 11 Dec 2015

# Time-Height plot at a station defined by the tslist. Uses the STATION.d0Y.XX files where Y is the
# domain number and XX is PH, TH, UU, and VV output files.

from functions import wind_calcs, MesoWest_timeseries, WRF_timeseries, read_tslist, WRF_timeseries
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates
from matplotlib.dates import DateFormatter, YearLocator, MonthLocator, DayLocator, HourLocator
import os

def epoch_to_datetime(i):
    return datetime.fromtimestamp(i), datetime.fromtimestamp(i).strftime('%H')

def datetime_to_str(x):
    return x.strftime("%H")


timer1 = datetime.now()
model_start = datetime(2015,6,17,0)
wrf_dir = '/uufs/chpc.utah.edu/common/home/horel-group4/model/bblaylock/WRF3.7_lake303_ember/WRFV3/test/em_real/'    
STN_NAME, STN_ID, LAT, LON = read_tslist.read_tslist(wrf_dir+"tslist")

FIGDIR = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/MS/timeheight/'
if not os.path.exists(FIGDIR):
    os.makedirs(FIGDIR)

for s in np.arange(0,len(STN_ID)):
    station = STN_ID[s]
    st_name = STN_NAME[s]
    print 'working on',station    
    plt.cla()
    plt.clf()
    plt.close()
    
    # Open the geopotential height file
    dates, PH = WRF_timeseries.get_full_vert(wrf_dir+station+'.d02.PH',model_start)
    print 'got PH'
    TH = WRF_timeseries.get_full_vert(wrf_dir+station+'.d02.TH',model_start)[1]
    print 'got TH'
    VV = WRF_timeseries.get_full_vert(wrf_dir+station+'.d02.VV',model_start)[1]
    print 'got VV'
    UU = WRF_timeseries.get_full_vert(wrf_dir+station+'.d02.UU',model_start)[1]
    print 'got UU'
    QV = WRF_timeseries.get_full_vert(wrf_dir+station+'.d02.QV',model_start)[1]
    QV = QV*1000 #convert from kg/kg to g/kg
    print 'got QV'
    
    # Since pcolormesh doesn't like datetime on the xaxis I need to get a 
    # little creative making my own tick labels
        
    # Assign x-axis variables
    x = dates
    x2D = dates*np.ones_like(PH)
    
    # Get the index of every hour
    # Since there are 3600 seconds in one hour and the model time step is 2 seconds, then every 1800th index is an hour 
    hourindex = np.arange(0,len(x),1800)
    xticks = x[hourindex[24:]]
    # Make a list of datetimes at each of those hours that we will use as labels
    base = model_start
    numhours = len(hourindex)
    date_list = [base + timedelta(hours=z) for z in range(0, numhours)]
    dstr = np.vectorize(datetime_to_str)
    xlabel = dstr(date_list[24:])
    
    
    
    # Make Plot
    plt.figure(1, figsize=[20,14])
    
    plt.suptitle(st_name+", June 18 00z - June 19 07z, 2015, Model Version=lake303",fontsize=20)
    
    plt.subplot(3,1,1)
    plt.title(station+' Potential Temperature and Wind Direction',fontsize=15)
    
    ax = plt.pcolormesh(x2D,PH,wind_calcs.wind_uv_to_dir(UU,VV),
                        cmap=plt.get_cmap('hsv')) # dates,
    plt.ylim([np.min(PH),3500])
    plt.xlim([24,np.max(x)])
    plt.xticks(xticks,xlabel)
    cbar = plt.colorbar(ticks= np.arange(0,361,45),pad=0.01)
    cbar.set_ticklabels(['N','NE','E','SE','S','SW','W','NW','N'])
    cbar.set_label('Wind Direction')
    CS = plt.contour(x2D,PH,TH,
                     colors=.2,
                     levels=np.arange(int(np.min(TH)),int(np.max(TH)),1),
                     widths=.25)
    plt.clabel(CS, inline=1, fontsize=9,fmt='%1.0f') 
    
    plt.ylabel('Geopotential Height (m)')
    plt.xlabel('Hour')
    print "finished first plot"
    
    plt.subplot(3,1,2)
    plt.title(station+' Potential Temperature and Wind Speed',fontsize=15)
    
    ax = plt.pcolormesh(x2D,PH,wind_calcs.wind_uv_to_spd(UU,VV),
                        cmap=plt.get_cmap('YlGn')) # dates,
    plt.ylim([np.min(PH),3500])
    plt.xlim([24,np.max(x)])
    plt.xticks(xticks,xlabel)
    cbar = plt.colorbar(ticks= np.arange(0,20,2.5),pad=0.01)
    cbar.set_label('Wind Speed (m/s)')
    CS = plt.contour(x2D,PH,TH,
                     colors=.2,
                     levels=np.arange(int(np.min(TH)),int(np.max(TH)),1),
                     widths=.25)
    plt.clabel(CS, inline=1, fontsize=9,fmt='%1.0f') 
    
    plt.ylabel('Geopotential Height (m)')
    plt.xlabel('Hour')    
    print "finished second plot"
    
    
    plt.subplot(3,1,3)
    plt.title(station+' Potential Temperature and Mixing Ratio',fontsize=15)
    
    ax = plt.pcolormesh(x,PH,QV,
                        cmap=plt.get_cmap('BrBG')) # dates,
    plt.ylim([np.min(PH),3500])
    plt.xlim([24,np.max(x)])
    plt.xticks(xticks,xlabel)
    cbar = plt.colorbar(pad=0.01)
    cbar.set_label('Mixing Ratio g/kg')
    CS = plt.contour(x2D,PH,TH,
                     colors=.2,
                     levels=np.arange(int(np.min(TH)),int(np.max(TH)),1),
                     widths=.25)
    plt.clabel(CS, inline=1, fontsize=9,fmt='%1.0f') 
    
    plt.ylabel('Geopotential Height (m)')
    plt.xlabel('Hour')
    print "finished third plot"
    
    plt.savefig(FIGDIR+station+"_Theta-WindDir.png", bbox_inches='tight')
    print "Saved"

timer2 = datetime.now()

print "finished in", (timer2-timer1).seconds/60,'Minutes'
