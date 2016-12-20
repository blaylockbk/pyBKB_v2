## Brian Blaylock

## 14 June 2016

# Redo the wind script

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from datetime import datetime

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB')  #for running on CHPC boxes
sys.path.append('B:\pyBKB')                                        #for running on PC (B:\ is my network drive)

from BB_MesoWest import MesoWest_timeseries as MW
from pm25rose import WindroseAxes

label_font  = 10    
tick_font   = 8 
legend_font = 7

width=3.5  # refer to above table
height=3   # adjust as needed, but bbox="tight" should take care of most of this


## Reset the defaults (see more here: http://matplotlib.org/users/customizing.html)
mpl.rcParams['xtick.labelsize'] = tick_font
mpl.rcParams['ytick.labelsize'] = tick_font
mpl.rcParams['axes.labelsize'] = label_font
mpl.rcParams['legend.fontsize'] = legend_font

mpl.rcParams['figure.figsize'] = [width,height] 

mpl.rcParams['grid.linewidth'] = .25

mpl.rcParams['savefig.bbox'] = 'tight'
mpl.rcParams['savefig.dpi'] = 1000



# Make Ozone Rose
#A quick way to create new windrose axes...
def new_axes():
    fig = plt.figure(figsize=(5,10), facecolor='w', edgecolor='w')
    rect = [0.1, 0.1, 0.8, 0.8]
    ax = WindroseAxes(fig, rect, axisbg='w')
    fig.add_axes(ax)
    return ax
#...and adjust the legend box
def set_legend(ax):
    l = ax.legend()
    plt.setp(l.get_texts())
    plt.legend(loc='center left', bbox_to_anchor=(1.2, 0.5),prop={'size':10})
    

def rose_with_labels():    
    ax = new_axes()
    ax.bar(wd, ws, nsector = 16, \
                   bins = [0,12.1,35.5,55.5,150.5], normed=True, \
                   colors = ('green','yellow','orange', 'red', 'purple'))
    set_legend(ax)
    plt.title("PM2.5 Rose "+a['station name']+"\n"+start.strftime('%H:%M UTC %d%b%Y')+" - "+end.strftime('%H:%M UTC %d%b%Y')+ "\n")
    
    
    plt.grid(True)
    plt.yticks(np.arange(0,105,5))
    ax.set_yticklabels(['','5%','10%','15%', '20%','25%','30%','','40%'])
    #ax.set_rmax(25)
    ax.set_rmax(np.max(np.sum(ax._info['table'],axis=0)))
    plt.savefig("pm25_hi.png",bbox_inches="tight",dpi=500)
    #plt.show()
def rose_no_labels():    
    """
    There is no grid or labels, just the colorbars. 
    I like to use possition these on a map 
    """    
    ax = new_axes()
    ax.bar(wd, ws,nsector = 16, \
                   bins = [0,12.1,35.5,55.5,150.5], normed=True, \
                   colors = ('green','yellow','orange', 'red', 'purple'))
    #set_legend(ax)
    ax.axis('off')
    #ax.set_rmax(25)
    ax.set_rmax(np.max(np.sum(ax._info['table'],axis=0)))
    plt.savefig("pm25_hi_nolabel.png",bbox_inches="tight",dpi=500, transparent=True)
    #plt.show()

def clock_rose():
    """
    Creates an ozone rose clock and shows time of day each of the 
    observations occur in rather than the direction. Top of plot
    is hour 0, bottom is hour 12.
    """
    # Make array of hours and convert it to a "degree" for
    # The polar plot (multiply the hour by 15)
    hour = []
    for i in a['datetimes']:
        hour.append(i.hour*15)    
    ax = new_axes()

    ax.contourf(hour, ws,  nsector = 24,\
                   bins = [0,12.1,35.5,55.5,150.5], normed=True, \
                   colors = ('green','yellow','orange', 'red', 'purple'))
                   
    set_legend(ax)
    plt.title("PM2.5 Clock "+a['station name']+"\n"+start.strftime('%H:%M UTC %d%b%Y')+" - "+end.strftime('%H:%M UTC %d%b%Y')+ "\n")
    
    
    plt.grid(True)
    plt.yticks(np.arange(0,105,5))
    ax.set_yticklabels(['','','10%','15%', '20%','25%','30%','','40%'])
    ax.set_xticklabels(['06:00','03:00','00:00','21:00', '18:00','15:00','12:00','09:00'])
    
    # Maximum Radial Circle
    #ax.set_rmax(5)                                         # uncomment to unify all rmax
    ax.set_rmax(np.max(np.sum(ax._info['table'],axis=0)))   # set rmax as the biggest arm

    plt.savefig("pm25_hi_clock.png",bbox_inches="tight",dpi=500)
    #plt.show()
    #print np.sum(ax._info['table'],axis=0)


if __name__ == '__main__':
    ##All in-situ stations
    
        
    
    start = datetime(2016,6,15,6,0)
    end   = datetime(2016,6,16,6,0)
    
    a = MW.get_mesowest_ts('naa',start,end)
    
    # The idea is we are creating an ozone rose from a wind rose
    # wd is the wind direction
    # ws is typically the wind speed, but in this case it is ozone
    wd = a['wind direction']
    ws = a['pm25'] 
    
    rose_with_labels()
    rose_no_labels()
    clock_rose()
    
    
    
    
    """
    SOME NOTES:
    to look at the values used to create the plot look
      at ax._info
      ax._info['table'] contains the frequency for each bin in each direction
      np.sum(ax._info['table'],axis=0) is the total frequency for each direction
      np.max(np.sum(ax._info['table'],axis=0)) is the maximum frequency I like to use to set my max radius
    """
