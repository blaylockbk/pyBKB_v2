## Simple plots the data from 2012-2014 8-hr ozone concentrations

import sys
import pydap.client as pd
import matplotlib.pyplot as plt
import numpy as np
import time
import calendar
from datetime import datetime, timedelta
from scipy.signal import medfilt


def datespan(startDate, endDate, delta=timedelta(days=1)):
## Creates a generator (an iterable) of each day or hour requested.
    currentDate = startDate
    while currentDate < endDate:
        yield currentDate
        currentDate += delta

## Inputs collected from program call
st = sys.argv[1]          				# YYYYMMDDHH: 2014050618
et = sys.argv[2]           				# YYYYMMDDHH: 2014050818
station = sys.argv[3]					# Roosevelt, Gusher, Lapoint
time_frame = sys.argv[4]				# 1, 8, 5min		
		
dir = '/uufs/chpc.utah.edu/common/home/horel-group/ubos/Utah_state_data/'
if time_frame == '5min':
	data = np.genfromtxt(dir+'5min_ozone_2013.csv', delimiter=',', dtype=None, names=True, missing_values = '')
elif time_frame == '1':
	data = np.genfromtxt(dir+'1hrAvg_ozone_2013.csv', delimiter=',', dtype=None, names=True, missing_values = '')
elif time_frame == '8':
	data = np.genfromtxt(dir+'8hrAvg_ozone_2013.csv', delimiter=',', dtype=None, names=True, missing_values = '')

# print list of stations

"""
for i in ozone_5min_2013.dtype.names:
	print i
for i in ozone_1hr_2013.dtype.names:
	print i
for i in ozone_8hr_2013.dtype.names:
	print i
"""

## Inputs collected from program call
st = sys.argv[1]          				# YYYYMMDDHH: 2014050618
et = sys.argv[2]           				# YYYYMMDDHH: 2014050818
station = sys.argv[3]					# Roosevelt, Gusher, Lapoint
time_space = sys.argv[4]				# 1, 8, 5min
	
	
ozone_data = data[station]
print ozone_data
dates = data['DateTime']

## utc time
times= []
for i in dates:
	times.append(datetime.strptime(i,'%m/%d%Y %H:%M'))
print times




plt.plot(ozone_data)
plt.show()


