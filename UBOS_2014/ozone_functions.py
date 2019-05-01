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
	
def load_5min_ozone_data(st, et, station):
	## Retrives USU ozone data for one particular station for the
	## time period requested.
	## Returns a list of times and a list of ozone concentration in ppb.
	print 'Getting ozone data for',station					

	year = st[0:4]
	
	ozone_dir = '/uufs/chpc.utah.edu/common/home/horel-group/ubos/Utah_state_data/'
	data = np.genfromtxt(ozone_dir+'5min_ozone_'+year+'.csv', delimiter=',', dtype=None, names=True, missing_values = '')
	
	dates = data['DateTime_end'] # Raw data is in Local time
	ozone_data= data[station]

	## convert to UTC
	Otimes_utc= []
	for i in dates:
		i_time = datetime.strptime(i,'%m/%d/%Y %H:%M') + timedelta(hours=7)
		Otimes_utc.append(i_time)
		
	## Slice data for times requested
	Ostart = datetime.strptime(st,'%Y%m%d%H')
	Oend = datetime.strptime(et,'%Y%m%d%H')
	time_start_index = Otimes_utc.index(Ostart)
	time_end_index = Otimes_utc.index(Oend)
	ozone_data = ozone_data[time_start_index:time_end_index]
	Otimes_utc = Otimes_utc[time_start_index:time_end_index]
	
	return Otimes_utc, ozone_data
	
	

def load_8hr_ozone_data(st, et, station):
	## Retrives USU ozone data for one particular station for the
	## time period requested.
	## Returns a list of times and a list of ozone concentration in ppb.
	print 'Getting 8hr ozone data for',station					

	year = st[0:4]
	
	ozone_dir = '/uufs/chpc.utah.edu/common/home/horel-group/ubos/Utah_state_data/'
	data = np.genfromtxt(ozone_dir+'8hrAvg_ozone_'+year+'.csv', delimiter=',', dtype=None, names=True, missing_values = '')
	
	dates = data['DateTime'] 
	ozone_data= data[station]

	# Raw data is in Local time, so we need to add 7 hours to convert
	# it to UTC time. The time is also is the beginning of the averaging 
	# period, so we need to add 8 hours to get the end hour of 
	# the averaging period.
	Otimes_utc= []
	for i in dates:
		i_time = datetime.strptime(i,'%m/%d/%Y %H:%M') + timedelta(hours=(7+8))
		Otimes_utc.append(i_time)
		
	## Slice data for times requested
	Ostart = datetime.strptime(st,'%Y%m%d%H')
	Oend = datetime.strptime(et,'%Y%m%d%H')
	time_start_index = Otimes_utc.index(Ostart)
	time_end_index = Otimes_utc.index(Oend)
	ozone_data = ozone_data[time_start_index:time_end_index]
	Otimes_utc = Otimes_utc[time_start_index:time_end_index]
	
	return Otimes_utc, ozone_data
	
	
	
	
	
	
	