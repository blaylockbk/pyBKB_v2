# ceil_ozone_functions
import sys
import pydap.client as pd
import matplotlib.pyplot as plt
import numpy as np
import time
import calendar
from datetime import datetime, timedelta
from scipy.signal import medfilt
from scipy.signal import medfilt2d
from matplotlib.dates import DateFormatter, YearLocator, MonthLocator, DayLocator, HourLocator
import matplotlib.dates as mdates
from ceil_functions import *
from matplotlib import gridspec

def find_nearest(array,value):
## Finds index of the nearest value in an array
    index = (np.abs(array-value)).argmin()
    return index

def load_ozone_data_2014(st, et):
	print 'ozone data'
	station = 'Duchesne'					
	station2 = 'Horsepool'
	station3 = 'Castle_Peak'
		
	ozone_dir = '/uufs/chpc.utah.edu/common/home/horel-group/ubos/Utah_state_data/'
	data = np.genfromtxt(ozone_dir+'5min_ozone_2014.csv', delimiter=',', dtype=None, names=True, missing_values = '')
	
	
	ozone_data2= data[station2]
	ozone_data3= data[station3]
	dates = data['DateTime_end']		# Raw data is in Local time

	## utc time
	Otimes_utc= []
	for i in dates:
		i_time = datetime.strptime(i,'%m/%d/%Y %H:%M') + timedelta(hours=7)
		Otimes_utc.append(i_time)
	Ostart = datetime.strptime(st,'%Y%m%d%H')
	Oend = datetime.strptime(et,'%Y%m%d%H')

	time_start_index = Otimes_utc.index(Ostart)
	time_end_index = Otimes_utc.index(Oend)
		
	#ozone_data = ozone_data[time_start_index:time_end_index]
	ozone2 = ozone_data2[time_start_index:time_end_index]
	ozone3 = ozone_data3[time_start_index:time_end_index]
	Otimes_utc = Otimes_utc[time_start_index:time_end_index]
	#return Otimes_utc, ozone_data, ozone2, ozone3
	return Otimes_utc, ozone2, ozone3
	
def load_ozone_data_2013(st, et):
	print 'ozone data'
	station = 'Roosevelt'					# Roosevelt, Gusher, Lapoint
	station2 = 'Gusher'
	station3 = 'Lapoint'
		
	ozone_dir = '/uufs/chpc.utah.edu/common/home/horel-group/ubos/Utah_state_data/'
	data = np.genfromtxt(ozone_dir+'5min_ozone_2013.csv', delimiter=',', dtype=None, names=True, missing_values = '')
		
	ozone_data2= data[station2]
	ozone_data3= data[station3]
	dates = data['DateTime_end']		# Raw data is in Local time

	## utc time
	Otimes_utc= []
	for i in dates:
		i_time = datetime.strptime(i,'%m/%d/%Y %H:%M') + timedelta(hours=7)
		Otimes_utc.append(i_time)
	Ostart = datetime.strptime(st,'%Y%m%d%H')
	Oend = datetime.strptime(et,'%Y%m%d%H')

	time_start_index = Otimes_utc.index(Ostart)
	time_end_index = Otimes_utc.index(Oend)
		
	#ozone_data = ozone_data[time_start_index:time_end_index]
	ozone2 = ozone_data2[time_start_index:time_end_index]
	ozone3 = ozone_data3[time_start_index:time_end_index]
	Otimes_utc = Otimes_utc[time_start_index:time_end_index]
	#return Otimes_utc, ozone_data, ozone2, ozone3
	return Otimes_utc, ozone2, ozone3
	
def ozone_plot(st, et,timezone,plot_title,figname, times_utc, height, bs_final, ML_height=0, tick_every=12, save=False, show=True):
## Creates a plot of backscatter
	# convert DateTime array to matplotlib.dates format
	plot_dates = mdates.date2num(times_utc)
	
	# set plotting grids
	ptt = np.zeros(bs_final.shape)
	phh = np.zeros(bs_final.shape)
	for i in range(ptt.shape[0]):
		ptt[i,:] = plot_dates[i]
	for j in range(phh.shape[1]):
		phh[:,j] = height[j]
	
	# Set plotting range
	minv = -8
	maxv = -5
	
	# Create plot Grid
	gs = gridspec.GridSpec(2,2,height_ratios=(1,1),width_ratios=(40,1))
	#PLOT BACKSCATTER:
	fig = plt.figure(1, figsize=(12,9))
	ax = plt.subplot(gs[0,0])
	qmesh = ax.pcolormesh(ptt,phh,bs_final,cmap=plt.cm.jet,vmin=minv, vmax=maxv)
	
	
	
	# Labels
	plt.ylabel('Height (m)')
	plt.xlabel('Day:Hour ('+timezone+')')
	plt.title(plot_title)
		

	# Format Ticks
	if tick_every == 12:
	# Place a major tick and label every 12 hours, place minor tick every hour.
		days = DayLocator()
		hours = HourLocator(byhour=[0,12])
		hours_each = HourLocator()
		dateFmt = DateFormatter('%d:%H')
		ax.xaxis.set_major_locator(hours)
		ax.xaxis.set_major_formatter(dateFmt)
		ax.xaxis.set_minor_locator(hours_each)
	plt.xticks(rotation = 30, fontsize = 10)
	
	
	## Plot mixed layer height if provided:
	if len(ML_height)>1:
		plt.plot(times_utc,ML_height,'k', linewidth=2)


	
######### Ozone Plot #########
	O_times, ozone2, ozone3 = load_ozone_data_2014(st,et)
	ax = plt.subplot(gs[1,0])
	plt.plot(O_times, ozone2, 'b', linewidth=2, label='Horsepool')
	plt.plot(O_times, ozone3, 'r', linewidth=2, label='Castle_Peak')
	
	# Format Ticks
	months = MonthLocator()
	days = DayLocator(interval=2)
	days_each= DayLocator()
	hours = HourLocator(byhour=[0,12])
	hours_each = HourLocator()
	dateFmt = DateFormatter('%d:%H')
	ax.xaxis.set_major_locator(days)
	ax.xaxis.set_major_formatter(dateFmt)
	ax.xaxis.set_minor_locator(days_each)
	
	plt.xticks(rotation = 30, fontsize = 10)
	# Colorbar Space, need to find way to get rid of this
	#plt.colorbar(shrink=0, pad=0.02)
	
	# Add space to left to compensate for colorbar
	plt.subplots_adjust(right=.5)
	
	
	plt.axhline(75, c='r', linestyle='--')
	plt.title('5 Minute Ozone')
	plt.ylabel('Ozone Concentratoin (ppb)')
	plt.xlabel('Day:Hour (UTC)')
	plt.legend(loc=2)
	
##############################
	# Colorbar
	ax = plt.subplot(gs[0,1])
	cb = plt.colorbar(qmesh,cax=ax )
	cb.ax.set_ylabel('Backscatter [log10 m-1 sr-1]')
	tv = np.linspace(minv,maxv,7)
	cb.ax.set_yticklabels(tv, fontsize = 10)
	cb.set_ticks(tv)
	
	
	plt.tight_layout()
	
	if show == True:
		plt.show()

	if save == True:
		save_plot(figname,fig)
		

	return fig
	
	
def downsample_heights(ML_height, BS_time, ozone, ozone_time):
## Takes the ML_heights and downsamples them to the times each
## ozone measurement is taken.

	downSamp_height = []
	for i in ozone_time:
		index = find_nearest(BS_time,i)
		downSamp_height.append(ML_height[index])
	return downSamp_height









