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

print "some stuff"
SAVEDIR = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/MS/pollywog_plots/'
SAVEDIR = './'
#if not os.path.exists(SAVEDIR):
#        os.makedirs(SAVEDIR)


filedir = 'line_forecasts/LakeBreeze_June2015/Other/'
station = 'GSLBY'
#station = 'TT029'

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


## Analysis points
anal_dates = np.array([])
for i in range(0,len(f00[station])):
    D = datetime.strptime(f00[station][i],'%Y-%m-%d %H:%M')
    anal_dates = np.append(anal_dates,D)
#anal_temp = f00['temp']
#anal_dwpt = f00['dwpt']
anal_speed = f00['speed']
#anal_gust = f00['gust']
#anal_maxwind = f00['maxwind']
#anal_speed80 = wind_uv_to_spd(f00['u80'],f00['v80'])



def make_pollywog():
    # stuff here
    a=0
def make_pollywog_barb():
    # stuff for making barbs 
    a=0



date_start_index = 15 # how many hours from the first part in the file do you wish to start from??
file_start_date = datetime.strptime(f00[station][date_start_index],'%Y-%m-%d %H:%M')

# First grab the MesoWest Data.
MW_start = file_start_date-timedelta(hours=1)
MW_end = file_start_date+timedelta(days=1)
a = get_mesowest_ts(station,MW_start,MW_end)
# plot on a graph
fig = plt.figure(1)
ax = fig.add_subplot(111)
plt.plot(a['datetimes'],a['temperature'],color='k',linewidth=3,label='MesoWest')




anal_color=[.2,.2,.2]
anal_hours = range(0,13,1)
color = ['red','blue','green','darkorange','cornflowerblue','gold','yellowgreen',
         'violet','lawngreen','cyan','goldenrod','darksalmon','mediumorchid']
lw = np.linspace(2,1.5,len(anal_hours))




#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#### Do the same for wind speed
# plot on a graph
fig = plt.figure(3)

ax = fig.add_subplot(111)
file_start_date = datetime.strptime(f00[station][date_start_index],'%Y-%m-%d %H:%M')
plt.plot(a['datetimes'],a['wind speed'],color='k',linewidth=3,label='MesoWest')



for i in range(0,len(anal_hours)):
    file_start_date = datetime.strptime(f00[station][date_start_index+anal_hours[i]],'%Y-%m-%d %H:%M') 
    
    Aug5_00UTC_line = np.array([])
    Aug5_00UTC_line = np.append(Aug5_00UTC_line,f00['speed'][date_start_index+anal_hours[i]])
    Aug5_00UTC_line = np.append(Aug5_00UTC_line,f01['speed'][date_start_index+1+anal_hours[i]])
    Aug5_00UTC_line = np.append(Aug5_00UTC_line,f02['speed'][date_start_index+2+anal_hours[i]])
    Aug5_00UTC_line = np.append(Aug5_00UTC_line,f03['speed'][date_start_index+3+anal_hours[i]])
    Aug5_00UTC_line = np.append(Aug5_00UTC_line,f04['speed'][date_start_index+4+anal_hours[i]])
    Aug5_00UTC_line = np.append(Aug5_00UTC_line,f05['speed'][date_start_index+5+anal_hours[i]])
    Aug5_00UTC_line = np.append(Aug5_00UTC_line,f06['speed'][date_start_index+6+anal_hours[i]])
    Aug5_00UTC_line = np.append(Aug5_00UTC_line,f07['speed'][date_start_index+7+anal_hours[i]])
    Aug5_00UTC_line = np.append(Aug5_00UTC_line,f08['speed'][date_start_index+8+anal_hours[i]])
    Aug5_00UTC_line = np.append(Aug5_00UTC_line,f09['speed'][date_start_index+9+anal_hours[i]])
    Aug5_00UTC_line = np.append(Aug5_00UTC_line,f10['speed'][date_start_index+10+anal_hours[i]])
    Aug5_00UTC_line = np.append(Aug5_00UTC_line,f11['speed'][date_start_index+11+anal_hours[i]])
    Aug5_00UTC_line = np.append(Aug5_00UTC_line,f12['speed'][date_start_index+12+anal_hours[i]])
    Aug5_00UTC_line = np.append(Aug5_00UTC_line,f13['speed'][date_start_index+13+anal_hours[i]])
    Aug5_00UTC_line = np.append(Aug5_00UTC_line,f14['speed'][date_start_index+14+anal_hours[i]])
    Aug5_00UTC_line = np.append(Aug5_00UTC_line,f15['speed'][date_start_index+15+anal_hours[i]])
    
    base = file_start_date
    date_list = [base + timedelta(hours=x) for x in range(0, len(Aug5_00UTC_line))]

    
    plt.plot(date_list,Aug5_00UTC_line,color=color[i],linewidth=lw[i],label='%02d UTC forecast' % (date_list[0].hour))
    plt.scatter(date_list[0],Aug5_00UTC_line[0],s=80,color=color[i],edgecolor=None,zorder=100+i)

#plt.legend(loc=4)
plt.grid()
plt.title(station)
plt.ylabel(r'10-m Wind Speed (ms$\mathregular{^{-1}}$)')
plt.ylim([0,15])
plt.xlim(MW_start,MW_end)

plt.scatter(anal_dates,anal_speed,color=anal_color,zorder=200)

hours = mpl.dates.HourLocator([0,3,6,9,12,15,18,21])
hours_each = mpl.dates.HourLocator()
ax.xaxis.set_major_locator(hours)
ax.xaxis.set_minor_locator(hours_each)
ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%m/%d\n%H:%M'))
plt.savefig(SAVEDIR+station+'_speed_10m_forecasts_stream_all.png')



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#### Do the same for wind barbs
# plot on a graph
fig = plt.figure(7, figsize=[7.48,6])
ax = fig.add_subplot(111)
file_start_date = datetime.strptime(f00[station][date_start_index],'%Y-%m-%d %H:%M')

MW_u, MW_v = wind_spddir_to_uv(a['wind speed'],a['wind direction'])
# If u or v is nan, then set to zero. We got a nan origianlly 
# becuase no direction was reported. Speed is zero in these instances.
MW_u[np.isnan(MW_u)]=0
MW_v[np.isnan(MW_v)]=0
idx = mpl.dates.date2num(a['datetimes'])
plt.barbs(idx,np.ones_like(MW_u),MW_u,MW_v,
          barb_increments=dict(half=2.5, full=5, flag=25),length=5.25)



position = range(2,len(anal_hours)+2)
for i in range(0,len(anal_hours)):
    file_start_date = datetime.strptime(f00[station][date_start_index+anal_hours[i]],'%Y-%m-%d %H:%M') 
    
    Aug5_00UTC_line_U = np.array([])
    Aug5_00UTC_line_V = np.array([])
    Aug5_00UTC_line_U = np.append(Aug5_00UTC_line_U,f00['u'][date_start_index+anal_hours[i]])
    Aug5_00UTC_line_U = np.append(Aug5_00UTC_line_U,f01['u'][date_start_index+1+anal_hours[i]])
    Aug5_00UTC_line_U = np.append(Aug5_00UTC_line_U,f02['u'][date_start_index+2+anal_hours[i]])
    Aug5_00UTC_line_U = np.append(Aug5_00UTC_line_U,f03['u'][date_start_index+3+anal_hours[i]])
    Aug5_00UTC_line_U = np.append(Aug5_00UTC_line_U,f04['u'][date_start_index+4+anal_hours[i]])
    Aug5_00UTC_line_U = np.append(Aug5_00UTC_line_U,f05['u'][date_start_index+5+anal_hours[i]])
    Aug5_00UTC_line_U = np.append(Aug5_00UTC_line_U,f06['u'][date_start_index+6+anal_hours[i]])
    Aug5_00UTC_line_U = np.append(Aug5_00UTC_line_U,f07['u'][date_start_index+7+anal_hours[i]])
    Aug5_00UTC_line_U = np.append(Aug5_00UTC_line_U,f08['u'][date_start_index+8+anal_hours[i]])
    Aug5_00UTC_line_U = np.append(Aug5_00UTC_line_U,f09['u'][date_start_index+9+anal_hours[i]])
    Aug5_00UTC_line_U = np.append(Aug5_00UTC_line_U,f10['u'][date_start_index+10+anal_hours[i]])
    Aug5_00UTC_line_U = np.append(Aug5_00UTC_line_U,f11['u'][date_start_index+11+anal_hours[i]])
    Aug5_00UTC_line_U = np.append(Aug5_00UTC_line_U,f12['u'][date_start_index+12+anal_hours[i]])
    Aug5_00UTC_line_U = np.append(Aug5_00UTC_line_U,f13['u'][date_start_index+13+anal_hours[i]])
    Aug5_00UTC_line_U = np.append(Aug5_00UTC_line_U,f14['u'][date_start_index+14+anal_hours[i]])
    Aug5_00UTC_line_U = np.append(Aug5_00UTC_line_U,f15['u'][date_start_index+15+anal_hours[i]])
    
    Aug5_00UTC_line_V = np.append(Aug5_00UTC_line_V,f00['v'][date_start_index+anal_hours[i]])
    Aug5_00UTC_line_V = np.append(Aug5_00UTC_line_V,f01['v'][date_start_index+1+anal_hours[i]])
    Aug5_00UTC_line_V = np.append(Aug5_00UTC_line_V,f02['v'][date_start_index+2+anal_hours[i]])
    Aug5_00UTC_line_V = np.append(Aug5_00UTC_line_V,f03['v'][date_start_index+3+anal_hours[i]])
    Aug5_00UTC_line_V = np.append(Aug5_00UTC_line_V,f04['v'][date_start_index+4+anal_hours[i]])
    Aug5_00UTC_line_V = np.append(Aug5_00UTC_line_V,f05['v'][date_start_index+5+anal_hours[i]])
    Aug5_00UTC_line_V = np.append(Aug5_00UTC_line_V,f06['v'][date_start_index+6+anal_hours[i]])
    Aug5_00UTC_line_V = np.append(Aug5_00UTC_line_V,f07['v'][date_start_index+7+anal_hours[i]])
    Aug5_00UTC_line_V = np.append(Aug5_00UTC_line_V,f08['v'][date_start_index+8+anal_hours[i]])
    Aug5_00UTC_line_V = np.append(Aug5_00UTC_line_V,f09['v'][date_start_index+9+anal_hours[i]])
    Aug5_00UTC_line_V = np.append(Aug5_00UTC_line_V,f10['v'][date_start_index+10+anal_hours[i]])
    Aug5_00UTC_line_V = np.append(Aug5_00UTC_line_V,f11['v'][date_start_index+11+anal_hours[i]])
    Aug5_00UTC_line_V = np.append(Aug5_00UTC_line_V,f12['v'][date_start_index+12+anal_hours[i]])
    Aug5_00UTC_line_V = np.append(Aug5_00UTC_line_V,f13['v'][date_start_index+13+anal_hours[i]])
    Aug5_00UTC_line_V = np.append(Aug5_00UTC_line_V,f14['v'][date_start_index+14+anal_hours[i]])
    Aug5_00UTC_line_V = np.append(Aug5_00UTC_line_V,f15['v'][date_start_index+15+anal_hours[i]])
    
    base = file_start_date
    date_list = [base + timedelta(hours=x) for x in range(0, len(Aug5_00UTC_line))]

    
    idx = mpl.dates.date2num(date_list)
    plt.barbs(idx,np.ones_like(idx)*position[i],Aug5_00UTC_line_U,Aug5_00UTC_line_V,color=color[i],
              barb_increments=dict(half=2.5, full=5, flag=25),length=5.25)
    

plt.legend(loc=4)

plt.title(station)
plt.ylabel('10-m Winds')
plt.yticks(range(1,len(anal_hours)+2),['MesoWest','06 UTC','07 UTC','08 UTC','09 UTC',
               '10 UTC','11 UTC','12 UTC','13 UTC','14 UTC','15 UTC','16 UTC','17 UTC','18 UTC'])
plt.xlim(MW_start,MW_end)
plt.ylim([-.5,15.3])
plt.grid()

hours = mpl.dates.HourLocator([0,3,6,9,12,15,18,21])
hours_each = mpl.dates.HourLocator()
ax.xaxis.set_major_locator(hours)
ax.xaxis.set_minor_locator(hours_each)
ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%m/%d\n%H:%M'))
plt.savefig(SAVEDIR+station+'_barbs_10m_forecasts_stream_all.png')

