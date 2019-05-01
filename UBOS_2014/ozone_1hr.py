## Simple plots the data from 2012-2014 8-hr ozone concentrations

from ceil_ozone_functions import *


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

		
ozone_dir = '/uufs/chpc.utah.edu/common/home/horel-group/ubos/Utah_state_data/'
data = np.genfromtxt(ozone_dir+'1hrAvg_ozone_2013.csv', delimiter=',', dtype=None, names=True, missing_values = '')

"""
# Print list of staions
for i in ozone_5min_2013.dtype.names:
	print i
for i in ozone_1hr_2013.dtype.names:
	print i
for i in ozone_8hr_2013.dtype.names:
	print i
"""
	
ozone_data = data[station]
dates = data['DateTime']


## utc time
times_utc= []
for i in dates:
	i_time = datetime.strptime(i,'%m/%d/%Y %H:%M') + timedelta(hours=7)
	times_utc.append(i_time)
start = datetime.strptime(st,'%Y%m%d%H')
end = datetime.strptime(et,'%Y%m%d%H')

time_start_index = times_utc.index(start)
time_end_index = times_utc.index(end)
	
ozone_data_utc = ozone_data[time_start_index:time_end_index]
times_utc = times_utc[time_start_index:time_end_index]
	

	

plt.figure(1)
plt.subplot(2,1,1)
plt.plot(times_utc, ozone_data_utc)
height = plt.axhline(75, c='r', linestyle='--')

plt.show()


