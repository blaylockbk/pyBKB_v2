## Brian Blaylock
## 30 September 2016

# Plot line HRRR forecast and full MesoWest time series

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from datetime import datetime, timedelta

import os
import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB')  #for running on CHPC boxes
sys.path.append('B:\pyBKB')  # local path for testing on my machine 

from BB_MesoWest.MesoWest_timeseries import get_mesowest_ts
from wind_calcs import wind_spddir_to_uv, wind_uv_to_spd

## MatPlotLib Settings
#<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
label_font  = 10    
tick_font   = 8 
legend_font = 7
title_font = 12

width=7.48  # 
height=3   # adjust as needed, but bbox="tight" should take care of most of this


## Reset the defaults (see more here: http://matplotlib.org/users/customizing.html)
mpl.rc('figure',titlesize=title_font)
mpl.rc('legend', fontsize=legend_font)
mpl.rcParams['xtick.labelsize'] = tick_font
mpl.rcParams['ytick.labelsize'] = tick_font
mpl.rcParams['axes.labelsize'] = label_font
mpl.rcParams['legend.fontsize'] = legend_font

mpl.rcParams['figure.figsize'] = [width,height] 

mpl.rcParams['grid.linewidth'] = .25

mpl.rcParams['savefig.bbox'] = 'tight'
mpl.rcParams['savefig.dpi'] = 1000
#<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>





def get_pollywog(variable,start_index):
    """
    Creates a vector of a variable's value for each hour in a HRRR model 
    forecast initialized from a specific time.
    
    input:
        variable    - The name of the variable in the file header
        start_index - The index value in the file to start from. This number
                      is dependent on the initialized time you want.
    output:
        pollywog    - A vector with the data for the forecast
        dates       - Datetimes that correspond to the vector values
       
    global variables:
        Opened forecast .csv file (i.e. f00, f01, ...)
        station
        
    John Horel named these pollywogs because when you plot the series of a 
    forecast variable with the analysis hour being a circle, the lines look 
    like pollywogs.     
                    O----    Q_,--
    
    The pollywog line is created from each forecast hour file.
    (This assumes you have a .csv file for each of the forecast hours. I have
    another python script to pluck from the hrrr grib2 files to create .csv 
    files. Also assumes the file is complete, i.e. no missing dates.)
    
    Check here for example of how the HRRR files look:
        http://home.chpc.utah.edu/~u0553130/oper/HRRR_fires/Other/
    
    All dates in the .csv forecast files are the valid date. The file name 
    indicates what the forecast hour was. For example, f03 is a three hour 
    forecast for the times indicated in the file.
    
    Therefore, to create a line of the forecasts from an initialized time,
    we need to open each forecast hour file and sift through each time.
    We do this by creating a "line" of the forecast run, starting at f00, and 
    going to f15 or f18 (depending on what data is available).
    
    For example, if we want the forecast initialized at 22z on August 9th...
        open(f00), get and store (2016,8,9,hour22)
        open(f01), get and store (2016,8,9,hour23)
        open(f02), get and store (2016,8,9,hour00)
        open(f03), get and store (2016,8,9,hour01)
        ...
        open(f15), get and store (2016,8,9,hour13)
    """
    
    
    # First, grab the HRRR forecast from an initalized time and stor in a 
    # vecotor named 'line'. Save line as the pollywog to return
    line = np.array([])
    line = np.append(line,f00[variable][start_index])
    line = np.append(line,f01[variable][start_index+1])
    line = np.append(line,f02[variable][start_index+2])
    line = np.append(line,f03[variable][start_index+3])
    line = np.append(line,f04[variable][start_index+4])
    line = np.append(line,f05[variable][start_index+5])
    line = np.append(line,f06[variable][start_index+6])
    line = np.append(line,f07[variable][start_index+7])
    line = np.append(line,f08[variable][start_index+8])
    line = np.append(line,f09[variable][start_index+9])
    line = np.append(line,f10[variable][start_index+10])
    line = np.append(line,f11[variable][start_index+11])
    line = np.append(line,f12[variable][start_index+12])
    line = np.append(line,f13[variable][start_index+13])
    line = np.append(line,f14[variable][start_index+14])
    line = np.append(line,f15[variable][start_index+15])
    try: # again, see if these hours exist
        line = np.append(line,f16[variable][start_index+16])
        line = np.append(line,f17[variable][start_index+17])
        line = np.append(line,f18[variable][start_index+18])
    except:
        pass
    pollywog = line

    # Second, make a list of the dates we are getting.
    start_date = datetime.strptime(f00[station][start_index],'%Y-%m-%d %H:%M')     
    date_list = np.array([start_date + timedelta(hours=x) for x in range(0, len(line))])
    
                 
    return pollywog, date_list
        

    
def plot_pollywog(p,SAVEDIR,custom_end_date=False):
    """
    Plots the pollywogs for all the variables in the pollywog dictionary.
    Plots the pollywog with the MesoWest observation
    
    inputs:
        p       - p is a pollywog dictionary
        SAVEDIR - a string name for the save directory
    
    output:
        none
        
    global:
        station
        analysis vectors (i.e. Adates, Atemp, Au, ...)
        width - the figure width (barb figure height is higher)
    """
    Acolor = [.2,.2,.2] #color of the analysis points
    barbs_colors = []
    hours = mpl.dates.HourLocator([0,3,6,9,12,15,18,21])
    hours_each = mpl.dates.HourLocator()    

    # find the first time in the p dictionary
    fv = p.keys()[0]        # first variable key
    num_v = len(p.keys())   # number of variables
    num_h = len(p[fv])      # number of hours
    #            p[variable][hour][dates array][position]
    first_date = p[fv][0][1][0]
    last_date  = p[fv][len(p[fv])-1][1][-1]
    
    # First grab the MesoWest Data.
    MW_start = first_date-timedelta(hours=1)
    if custom_end_date != False:
        MW_end = custom_end_date
    else:
        MW_end = last_date
    a = get_mesowest_ts(station,MW_start,MW_end)
    print "got MesoWest"
    
    for i in range(0,num_v): # for each variable
        #%%
        if p.keys()[i]=='temp':
            print 'working on temp'
            fig = plt.figure(i+1)
            ax = fig.add_subplot(111)
            # Add a grid
            plt.grid()
            # Plot MesoWest
            plt.plot(a['datetimes'],a['temperature'],
                     color='k',
                     linewidth=3)
            # Plot each pollywog
            for h in range(0,num_h):
                lw = np.linspace(2,1.5,num_h)
                z = plt.plot(p['temp'][h][1],p['temp'][h][0],
                             linewidth=lw[h])
                
                # store the line color and plot head with same color
                color = z[0]._get_rgba_ln_color() 
                barbs_colors = barbs_colors+[color]
                
                # Plot the Pollywog head, the analysis time, with same color
                plt.scatter(p['temp'][h][1][0],p['temp'][h][0][0],
                            color=color,
                            s=80)
            
            # Plot the analysis hours
            plt.scatter(Adates,Atemp,color=Acolor,s=30,zorder=10)
            
            plt.title(station)
            plt.ylabel(r'2-m Temperature (C)')
            #plt.ylim([0,15])
            plt.xlim(MW_start,MW_end)
            ax.xaxis.set_major_locator(hours)
            ax.xaxis.set_minor_locator(hours_each)
            ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%m/%d\n%H:%M'))
            plt.savefig(SAVEDIR+station+'_temp_2m.png')
        #%%
        elif p.keys()[i]=='dwpt':
            print 'working on dwpt'
            fig = plt.figure(i+1)
            ax = fig.add_subplot(111)
            # Add a grid
            plt.grid()
            # Plot MesoWest
            plt.plot(a['datetimes'],a['dew point'],
                     color='k',
                     linewidth=3)
            # Plot each pollywog
            for h in range(0,num_h): 
                lw = np.linspace(2,1.5,num_h)
                z = plt.plot(p['dwpt'][h][1],p['dwpt'][h][0],
                             linewidth=lw[h])
                
               

                # store the line color and plot head with same color
                color = z[0]._get_rgba_ln_color() 
                # store the line color and plot head with same color
                barbs_colors = barbs_colors+[color]

                
                # Plot the Pollywog head, the analysis time, with same color
                plt.scatter(p['dwpt'][h][1][0],p['dwpt'][h][0][0],
                            color=color,
                            s=80)
            
            # Plot the analysis hours
            plt.scatter(Adates,Adwpt,color=Acolor,s=30,zorder=10)
            
            plt.title(station)
            plt.ylabel(r'2-m Dew Point (C)')
            #plt.ylim([0,15])
            plt.xlim(MW_start,MW_end)
            ax.xaxis.set_major_locator(hours)
            ax.xaxis.set_minor_locator(hours_each)
            ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%m/%d\n%H:%M'))
            plt.savefig(SAVEDIR+station+'_dwpt_2m.png')
        #%%
        elif p.keys()[i]=='speed':
            print 'working on speed'
            fig = plt.figure(i+1)
            ax = fig.add_subplot(111)
            # Add a grid
            plt.grid()
            # Plot MesoWest
            plt.plot(a['datetimes'],a['wind speed'],
                     color='k',
                     linewidth=3,
                     zorder=1)
            # Plot each pollywog
            for h in range(0,num_h):
                lw = np.linspace(2,1.5,num_h)
                z = plt.plot(p['speed'][h][1],p['speed'][h][0],
                             linewidth=lw[h],
                                zorder=2)
                

                # store the line color and plot head with same color
                color = z[0]._get_rgba_ln_color()
                # store the line color and plot head with same color
                barbs_colors = barbs_colors+[color]
                # Plot the Pollywog head, the analysis time, with same color
                plt.scatter(p['speed'][h][1][0],p['speed'][h][0][0],
                            color=color,
                            s=80,
                            zorder=2)
            
            # Plot the analysis hours
            plt.scatter(Adates,Aspeed,color=Acolor,s=30,zorder=10)
            
            plt.title(station)
            plt.ylabel(r'10-m Wind Speed (ms$\mathregular{^{-1}}$)')
            plt.ylim([0,15])
            plt.xlim(MW_start,MW_end)
            ax.xaxis.set_major_locator(hours)
            ax.xaxis.set_minor_locator(hours_each)
            ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%m/%d\n%H:%M'))
            plt.savefig(SAVEDIR+station+'_speed_10m.png')
        #%%
        ## for u and v variables, plot the wind barbs
        elif p.keys()[i]=='u':
            print 'working on u'
            fig = plt.figure(i+1,[width,6])
            ax = fig.add_subplot(111)
            # Add a grid
            plt.grid()
            # Plot MesoWest
            MW_u, MW_v = wind_spddir_to_uv(a['wind speed'],a['wind direction'])
            # If u or v is nan, then set to zero. We got a nan origianlly 
            # becuase no direction was reported. Speed is zero in these instances.
            MW_u[np.isnan(MW_u)]=0
            MW_v[np.isnan(MW_v)]=0
            idx = mpl.dates.date2num(a['datetimes'])
            y = np.ones_like(MW_u)*-.5
            # ONLY PLOT EVERY THIRD MESOWEST OBSERVATION!!!!
            plt.barbs(idx[::3],y[::3],MW_u[::3],MW_v[::3],
                      barb_increments=dict(half=1, full=2, flag=10),length=5.25)
            
            #print barbs_colors
            yticks = [-0.5]
            ylabels = ['MesoWest']
            for h in range(0,num_h):
                idx = mpl.dates.date2num(p['u'][h][1])
                plt.barbs(idx,np.ones_like(idx)*h+1,p['u'][h][0],p['v'][h][0],color=barbs_colors[h],
                          barb_increments=dict(half=1, full=2, flag=10),length=5.25)
                yticks.append(h+1)
                ylabels.append('%02d UTC' % (p['u'][h][1][0].hour))
            
            plt.yticks(yticks,ylabels)
            
                
            plt.title(station)
            plt.ylabel(r'10-m Wind Speed (ms$\mathregular{^{-1}}$)')
            #plt.ylim([0,15])
            plt.xlim(MW_start,MW_end)
            ax.xaxis.set_major_locator(hours)
            ax.xaxis.set_minor_locator(hours_each)
            ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%m/%d\n%H:%M'))
            plt.savefig(SAVEDIR+station+'_barbs_10m_full2_half1.png') 
            
        #%%
        
    return {'fv':fv,
            'num_v':num_v,
            'first_date':first_date,
            'last_date':last_date,
            'mesowest':a,
            'plots':z,
            'barbs_colors':barbs_colors}


    
if __name__ == '__main__':

    ###########################################################################
    ###########################################################################    
    
    # What is the directory of the .csv forecast hour files?
    filedir = './line_forecasts/LakeBreeze_June2015/Other/'
    # What station do you want to plot?
    station = "NAA"
    
    # Where do you want to save the plots?
    SAVEDIR = 'B:/public_html/MS/HRRR_pollywog/'
    SAVEDIR = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/MS/HRRR_pollywog/'
    # What date do you want to start on?
    find_date = datetime(2015,6,18,6)
    # How many forecasts do you want?
    num = 13
    
    ###########################################################################
    ###########################################################################
    
    # Load all the HRRR forecast files
    f00 = np.genfromtxt(filedir+'f00/f00_'+station+'.csv',delimiter=',',dtype=None,names=True)
    f01 = np.genfromtxt(filedir+'f01/f01_'+station+'.csv',delimiter=',',dtype=None,names=True)
    f02 = np.genfromtxt(filedir+'f02/f02_'+station+'.csv',delimiter=',',dtype=None,names=True)
    f03 = np.genfromtxt(filedir+'f03/f03_'+station+'.csv',delimiter=',',dtype=None,names=True)
    f04 = np.genfromtxt(filedir+'f04/f04_'+station+'.csv',delimiter=',',dtype=None,names=True)
    f05 = np.genfromtxt(filedir+'f05/f05_'+station+'.csv',delimiter=',',dtype=None,names=True)
    f06 = np.genfromtxt(filedir+'f06/f06_'+station+'.csv',delimiter=',',dtype=None,names=True)
    f07 = np.genfromtxt(filedir+'f07/f07_'+station+'.csv',delimiter=',',dtype=None,names=True)
    f08 = np.genfromtxt(filedir+'f08/f08_'+station+'.csv',delimiter=',',dtype=None,names=True)
    f09 = np.genfromtxt(filedir+'f09/f09_'+station+'.csv',delimiter=',',dtype=None,names=True)
    f10 = np.genfromtxt(filedir+'f10/f10_'+station+'.csv',delimiter=',',dtype=None,names=True)
    f11 = np.genfromtxt(filedir+'f11/f11_'+station+'.csv',delimiter=',',dtype=None,names=True)
    f12 = np.genfromtxt(filedir+'f12/f12_'+station+'.csv',delimiter=',',dtype=None,names=True)
    f13 = np.genfromtxt(filedir+'f13/f13_'+station+'.csv',delimiter=',',dtype=None,names=True)
    f14 = np.genfromtxt(filedir+'f14/f14_'+station+'.csv',delimiter=',',dtype=None,names=True)
    f15 = np.genfromtxt(filedir+'f15/f15_'+station+'.csv',delimiter=',',dtype=None,names=True)
    try:
        # depending on the date, these might be available, so open if they are
        f16 = np.genfromtxt(filedir+'f16/f16_'+station+'.csv',delimiter=',',dtype=None,names=True)
        f17 = np.genfromtxt(filedir+'f17/f17_'+station+'.csv',delimiter=',',dtype=None,names=True)
        f18 = np.genfromtxt(filedir+'f18/f18_'+station+'.csv',delimiter=',',dtype=None,names=True)
    except:
        pass
        
    ## Grab the available variables and dates for all the analysis points
    
    Adates = np.array([datetime.strptime(x,'%Y-%m-%d %H:%M') for x in f00[station]])
    
    vars_avail = np.array([])
    try:
        Atemp = f00['temp']
        vars_avail = np.append(vars_avail,'temp')
    except:
        print 'no temperature'
    try:
        Adwpt = f00['dwpt']
        vars_avail = np.append(vars_avail,'dwpt')
    except:
        print 'no dewpoint'
    try:
        Au = f00['u']
        vars_avail = np.append(vars_avail,'u')
    except:
        print 'no u wind'
    try:
        Av = f00['v']
        vars_avail = np.append(vars_avail,'v')
    except:
        print 'no u wind'
    try:
        Aspeed = f00['speed']
        vars_avail = np.append(vars_avail,'speed')
    except:
        print 'no speed'
    try:
        Agust = f00['gust']
        vars_avail = np.append(vars_avail,'gust')
    except:
        print 'no gust'
    try:
        Amaxwind = f00['maxwind']
        vars_avail = np.append(vars_avail,'maxwind')
    except:
        print 'no maxwind'
    try:
        Au80 = f00['u80']   
        Av80 = f00['v80']        
        vars_avail = np.append(vars_avail,'u80')
        vars_avail = np.append(vars_avail,'v80')
    except:
        print 'no 80-m winds'
    
    
    # Find index value for a specific date
    first_date_index = np.argwhere(Adates==find_date)[0][0]
    
    # This is the cool part...
    # Create a dictionary of all the pollywog variables from initialized hours
    pollywog = {}    
    
    hours = range(0,num)
    for v in vars_avail:
        pollywog[v]={}
        for h in hours:
            pollywog[v][h]=get_pollywog(v,first_date_index+h) 
   
    
    ### Access the pollywog by variable and hour number. 
    ### Returns a numpy array of values datetimes.
    ### values,dates = pollywog['speed'][3]
    

    # Plot and save all the polllywog plots.
    plots = plot_pollywog(pollywog,SAVEDIR,custom_end_date=find_date+timedelta(days=1))
    plt.show()