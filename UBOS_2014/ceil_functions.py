import sys
import pydap.client as pd
import matplotlib.pyplot as plt
import numpy as np
import time
import calendar
from datetime import datetime, timedelta
from scipy.signal import medfilt
from scipy.signal import medfilt2d
from matplotlib.dates import DateFormatter, YearLocator, MonthLocator, DayLocator, HourLocator, MinuteLocator
import matplotlib.dates as mdates

#===============================================================================================
#                    Functions
#===============================================================================================

def find_nearest(array,value):
## Finds index of the nearest value in an array
    index = (np.abs(array-value)).argmin()
    return index

def load_ASN_data(st, et, bottom, top, station):
## Loads the data from the ASN network through OPeNDAP
	print 'loading data...'
	#___________________Load Data__________________________
	
	start = datetime.strptime(st,"%Y%m%d%H")
	end = datetime.strptime(et,"%Y%m%d%H")
	
	times = []
	levs = []
	bs_data = []
	fileList = []
	src = "http://asn.mesowest.net/data/opendap/PUBLIC/{0:%Y/%m/%d/}{1}_{0:%Y%m%d}.h5"

	# Create file_list from start time and end time
	if st[0:8] != et[0:8]:
			for timestamp in datespan(start,end,delta=timedelta(hours=1)):
					source = src.format(timestamp,station)
					if source in fileList:
							pass
					else:
							fileList.append(source)
	else:
			timestamp = start
			source = src.format(timestamp,station)
			fileList.append(source)
			
	#print fileList
	# Get data from each file in file_list using pydap
	for ff in fileList:
		print ff
		## pydap created a "dataset" object, which we can see has all the structure of the file.  There is a HEIGHT attribute, which contains the height dimension, and a data attribute which contains all the different data columns. 
		data = pd.open_url(ff)
		height = data['HEIGHT'][:]
		tt = data['data']['DATTIM'][:]
		bs = data['data']['BS'][:]
		#print height.shape, tt.shape, bs.shape
		if len(times) == 0:
			times = tt
			levs = height
			bs_data = bs
		else:
			if (levs != height).sum()==0:
				times = np.append(times,tt)
				#levs = np.append(levs,height)
				bs_data= np.append(bs_data,bs,0)
			else:
				print "attention: different levels"
				pass

	# Convert times into datetime array
	times_utc = np.array([datetime.utcfromtimestamp(i) for i in times])
	times_local = np.array([datetime.fromtimestamp(i) for i in times])

	# Get index for desired times and create new times array
		#utc
	time_start_index_utc = find_nearest(times_utc, start)
	time_end_index_utc = find_nearest(times_utc, end)
	times_utc = times_utc[time_start_index_utc:time_end_index_utc]
		#local
	time_start_index_local = find_nearest(times_local, start)
	time_end_index_local = find_nearest(times_local, end)
	times_local = times_local[time_start_index_local:time_end_index_local]
	
	
	# Find index for height range requested and create new height array
	height_bottom_index = np.where(height==bottom)
	height_top_index = np.where(height==top)
	height = height[height_bottom_index[0]:height_top_index[0]+1] # need plus one to include last index
	
	# Slice the backscatter data for desired times and heights
	bs_final = bs_data[time_start_index_utc:time_end_index_utc,height_bottom_index[0]:height_top_index[0]+1]
	bs_final_local = bs_data[time_start_index_local:time_end_index_local,height_bottom_index[0]:height_top_index[0]+1]

	return bs_final, bs_final_local, times_utc, times_local, height
	
def load_ROOSC_data(st, et, bottom, top, station):
## Loads and converts the Roosevelt 2013 ceilometer data.
## Input: start time (string), end time (string), bottom (int), top (int), station name (string)
## Output: 2D array of backscatter for period and level requested, datetime array
	print 'loading data...'
	#___________________Load Data__________________________
	
	start = datetime.strptime(st,"%Y%m%d%H")
	end = datetime.strptime(et,"%Y%m%d%H")
	
	dir = '/uufs/chpc.utah.edu/common/home/horel-group/ceilometer_archive/rooscl31/'
	
	times = []
	bs_data = []	
	height = []	
	
	#Create file_list from start time and end time
		#remove hour from dates
	start_file = st[:-2]
	end_file = et[:-2]
	
	#The ROOSC 2013 files start at 07z, so we need the previous day's data too.
	# (or else the plots will start at 07z instead of 00z)
	start_PrevDay = datetime.strptime(start_file,"%Y%m%d") - timedelta(days=1)
	start_PrevDay = datetime.strftime(start_PrevDay, '%Y%m%d.ascii')
	print start_PrevDay
	file_list = [start_PrevDay]
	
	#for i in range(int(start_file),int(end_file)+1):
	#	file_list.append(str(i)+'.ascii')
	
	for timestamp in datespan(start,end):	
		file_date = datetime.strftime(timestamp,'%Y%m%d'+'.ascii')
		file_list.append(file_date)
	
	# get data from each file in file_list
	for i in range(len(file_list)):
		print dir+file_list[i]
		data = np.genfromtxt(dir+file_list[i],delimiter=',')
		data = np.flipud(np.rot90(data))
		tt = data[0,1:]
		bs = data[1:,1:]
		if i == 0:
			bs_data = bs
		else:
			bs_data = np.column_stack([bs_data,bs])
		times = np.append(times,tt)
	lev = data[1:,0]
	height = np.append(height,lev)
	bs_data = (np.rot90(np.fliplr((CONVERT(bs_data)))))

	
	# Convert times into datetime array
	times_utc = np.array([datetime.utcfromtimestamp(i) for i in times])
	times_local = np.array([datetime.fromtimestamp(i) for i in times])

	# Get index for desired times and create new times array
		#utc
	time_start_index_utc = find_nearest(times_utc, start)
	time_end_index_utc = find_nearest(times_utc, end)
	times_utc = times_utc[time_start_index_utc:time_end_index_utc]
		#local
	time_start_index_local = find_nearest(times_local, start)
	time_end_index_local = find_nearest(times_local, end)
	times_local = times_local[time_start_index_local:time_end_index_local]
	
	
	# Find index for height range requested and create new height array
	height_bottom_index = np.where(height==bottom)
	height_top_index = np.where(height==top)
	height = height[height_bottom_index[0]:height_top_index[0]+1] # need plus one to include last index
	
	# Slice the backscatter data for desired times and heights
	bs_final = bs_data[time_start_index_utc:time_end_index_utc,height_bottom_index[0]:height_top_index[0]+1]
	bs_final_local = bs_data[time_start_index_local:time_end_index_local,height_bottom_index[0]:height_top_index[0]+1]

	return bs_final, bs_final_local, times_utc, times_local, height

def datespan(startDate, endDate, delta=timedelta(days=1)):
## Creates a generator (an iterable) of each day or hour requested.
    currentDate = startDate
    while currentDate < endDate:
        yield currentDate
        currentDate += delta		

def find_threshold_index(threshold,profile):
## Finds the index of the top of the mixed layer 
## based on the given threshold parameter.        
	current_index_height = 0    
	for i in profile:
		if i < threshold:
			break
		else:
			current_index_height += 1
	return current_index_height

def fixed_threshold_method(input_backscatter, height, threshold):
## Takes an array of backscatter data and returns an array of the 
## mixed layer heights based on the given threshold.
	print 'in threshold method (fixed)'
	ML_height = []												# create an array containing the Mixed Layer heights.
	for each_ob in input_backscatter:									# For each observation (pulse) from the ceilometer (approx every 16 seconds)
		current_height_index = 0								# We are looking for the height of the mixed layer. Start at zero.
		for i in each_ob:										# For each element of each observation									
			if i < threshold:									# If the element is less than the threshold
				break											# stop.
			else:												# Else, if the element is greater than the threshold, 
				current_height_index += 1						# add one to the current height index.
		ML_height.append(height[current_height_index])			# When threshold height index is found, story in array. (Use the height index to find the height.)
	#print ML_height
	return ML_height
	
def adjustable_threshold_method(input_backscatter, height, threshold, min_height=50):
## Takes an array of backscatter data and returns an array of the
## mixed layer heights based on a changing threshold. We attempt to find
## the best threshold for the observation by increasing the threshold until 
## we find a mixed layer height above some minimum height.
## In other words, we're trying to find a threshold value that will give us
## a boundary layer that is above a minimum height (default is 50 m).
	print 'in ADJ'
	ADJ_height = []
	threshold_ARRAY = []  # we store these values so we can make a plot based on the colors.
	orig_threshold = threshold
	for each_ob in input_backscatter:
		profile = each_ob
		threshold = orig_threshold
		while True:
			
			height_index = find_threshold_index(threshold,profile)
			if height[height_index] > min_height:                       #If the height larger than 50m then we found a good threshold
				threshold_ARRAY.append(threshold)
				break
			else:
				threshold = threshold - .05                      # If the height index is zero we need to increase the threshold and try it again
				#print 'new threshold', threshold

		ADJ_height.append(height[height_index])

	return ADJ_height, threshold_ARRAY

def gradient_method(input_backscatter, height):
## Takes and array of backscatter data and returns an array of the
## mixed layer heights using the gradient method.
	
	ML_grad = []
	for each_ob in input_backscatter:
		slope = [0]
		i = 0
		while i < len(each_ob)-1:
			
			if each_ob[i]<-8.5:
			## If the backscatter is small, it has attenuated
			## and we shouldn't think it's a minimum in the gradient.
			## Instead, we'll input a nan to the slope list and move on.
				slope.append(np.nan)
				i +=1
			else:
				db_dz = (each_ob[i+1]-each_ob[i])/((i+1)-i)
				slope.append(db_dz)
				i += 1
		# find min index
		min_slope = np.nanmin(slope[6:]) #since there is noise below 50 meters, we only want to look at point above 60 meters
		min_index = np.where(slope==min_slope)
		ML_grad.append(height[min_index[0][0]])
	return ML_grad

def smoother(ML_height, num_times = 4):
## Smooths the ML_height array 
## num_times is the number of times it is smoothed: default is four.
	print 'applying smoother...'
	while num_times >0:
		ML_height = medfilt(ML_height,29) # higher kernal = more smoothing. Kernal must be odd. But best to smooth more times.
		num_times -= 1
	return ML_height
	
def CONVERT(B):
## Converts the 2013 rooscl31 data from units of 10^-9*(m*sr)^-1 to
## log10 [(m*sr)^-1]
	#return ((np.log10(B*10**-9)))
	return ((np.log10(B*10**-10))) 		#See email: https://mail.google.com/mail/u/0/#inbox/146ca4c452f43f57

def write_heights(times,heights,threshold):
## Writes a csv file containing the heights of the boundary layer.
## DOESN'T WORK YET
	file = open('height_output'+str(times[0])+'_'+str(times[-1])+'_'+str(threshold)+'.txt', 'w')
	print file
	for i in height:
		file.write(str(i)+'__\n')
	file.close()
	
def make_plots(type, bs_final, ML_height, time_restriction):
## Makes plots, compatibale with UTC and Local times.
## Type is a string, 'UTC' or 'LOCAL'
## bs_final is the final backscatter data. If local time, need to input bs_final_loc
## ML_height is the array containing the Mixed Layer heights. If local time, need to input ML_height_loc
	print 'creating plot...'
	if type == 'UTC':
		time_type = times_utc
	if type == "LOCAL":
		time_type = times_local
	
	sd = start.strftime(("%b%d%H")+"-"+end.strftime("%b%d%H"))						# string of dates
	sd_with_year = start.strftime(("%b %d, %Y")+' - '+end.strftime("%b %d, %Y"))	# string of dates (w/ years)	
	
	# set plotting grids
	ptt = np.zeros(bs_final.shape)
	phh = np.zeros(bs_final.shape)
	pheight = height[height_restriction[0]:height_restriction[1]]

	for i in range(ptt.shape[0]):
		ptt[i,:] = i
	for j in range(phh.shape[1]):
		phh[:,j] = pheight[j]
	figname = station+"_"+sd+"_"+str(int(bottom))+"-"+str(int(top))+"_"+type+".png"
	ptime = time_type[time_restriction[0]:time_restriction[1]]
	ts = [i[4:10] for i in ptime]
	uts = []	
	for timestamp in datespan(start,end,delta=timedelta(hours=1)):
		uts.append(timestamp.strftime("%m%d%H"))
			
	xts = []
	xtsl = []
	
	for kts in uts:
		ind = [i for i,v in enumerate(ts) if v[0:6]==kts]
		if ind!=[]:
			ind = ind[0]
			xts.append(ind)
			if hr_tick_fq != 24:
				xtsl.append(ts[ind][2:4]+":"+ts[ind][4:6])
			else:
				xtsl.append(ts[ind][2:4])
				
	if hr_tick_fq == 24:
		label_space = 24
	elif hr_tick_fq == 1:
		if len(xts) < 12:
			label_space = 1
		elif 12 <= len(xts) < 24:
			label_space = 2
		else:
			label_space = 4	
	else:
		label_space = 12
			
	fig = plt.figure(figsize=(12,6))
#	ax1 = fig.add_subplot(1,1,1)
	ax1 = fig.add_axes([0.05,0.1,1.05,0.84])

	
	pspace = 1
	margin = 0.5*len(xts)
	#print margin
	ax1.set_xlim(xmax=np.max(ptt[::pspace])+margin)
	ax1.set_xlim(xmin=-margin)
	ax1.set_ylim(ymin= (bottom-5))
	ax1.set_ylim(ymax= (top))
	
	
	# set plotting range
	#minv = int(np.around(np.min(bs_final)))
	#maxv = int(np.around(np.max(bs_final)))
	minv = -8
	maxv = -5
	bs_final[bs_final>maxv] = maxv
	bs_final[bs_final<minv] = minv
	
	CS = plt.pcolormesh(ptt,phh,bs_final,cmap=plt.cm.jet,vmin=-8, vmax=-5)
	cb = plt.colorbar(shrink=.8,pad = 0.02)
	cb.ax.set_ylabel('Backscatter [log10 m-1 sr-1]')
	tv = np.linspace(minv,maxv,7)
	cb.ax.set_yticklabels(tv, fontsize = 14)
	cb.set_ticks(tv)
	plt.xticks(xts,xtsl,rotation = 30, fontsize = 14)
	plt.setp(ax1.get_xticklabels(), visible=False)
	plt.setp(ax1.get_xticklabels()[::label_space], visible=True)
	
	x1,x2,y1,y2 = plt.axis()
	plt.axis((x1,x2,pheight[0],pheight[-1]))
	plt.ylabel('Height (m)', fontsize=14)
	plt.xlabel('Day:Hour ('+type+')', fontsize=14)
	plt.title(station+'\n'+sd_with_year+'\n'+'Threshold: '+str(threshold), fontsize = 16)
	
	## Plot threshold method results
	plt.hold(True)
	
	if FIXED_threshold_method:
		#plt.scatter(np.arange(len(ML_height)),ML_height, s=50)
		plt.plot(np.arange(len(ML_height)),ML_height,'k', linewidth=2)
	
	## Broken: Need more parameters, need to send in ADJ_height or ADJ_height_loc and ML_grad, etc.
	"""
	if ADJUSTABLE_threshold_method:
		plt.scatter(np.arange(len(ADJ_height)),ADJ_height, c=threshold_ARRAY, s = 50)		
		cbar = plt.colorbar()
		cbar.ax.set_ylabel('Threshold Value')
	## Plot gradient method results
	if gradient_method:
		plt.scatter(np.arange(len(ML_grad)),ML_grad, c='g', edgecolors='none')
	"""
	
	plt.show()	
	save_plot(figname, fig)
	plt.close()
	
def save_plot(figname, fig):
	outputDir = "./"
	outputDir = '/uufs/chpc.utah.edu/common/home/u0553130/python_scripts/Summer_Research_2014/figs/'
	fig.savefig(outputDir+figname, bbox_inches='tight',pad_inches=0.01)
	print 'image saved: '+ outputDir+figname
	
def new_plot(timezone,plot_title,figname, times_utc, height, bs_final, ML_height=0, tick_every=12, save=False, show=True):
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
	minv = -7.4
	maxv = -6.8
	
	#fig = plt.figure(1, figsize=(20,8)) # Long plot
	fig = plt.figure(1, figsize=(12,6)) # Short Plot
	ax = fig.add_subplot(111)
	qmesh = ax.pcolormesh(ptt,phh,bs_final,cmap=plt.cm.jet,vmin=minv, vmax=maxv)
	
	# Colorbar
	cb = fig.colorbar(qmesh,ax=ax, shrink=0.8, pad = 0.02)
	cb.ax.set_ylabel('Backscatter [log10 m-1 sr-1]', fontsize=14)
	tv = np.linspace(minv,maxv,7)
	cb.ax.set_yticklabels(tv, fontsize = 14)
	cb.set_ticks(tv)
	
	# Labels
	plt.ylabel('Height (m)', fontsize=16)
	plt.xlabel('Hour:Minute ('+timezone+')', fontsize=16)
	#plt.xlabel('Time ('+timezone+')')
	plt.title(plot_title, fontsize=21)
		

	# Format Ticks
	if tick_every == 12:
	# Place a major tick and label every 12 hours, place minor tick every hour.
		days = DayLocator(interval=2)
		days_each=DayLocator()
		hours = HourLocator(byhour=[0,12])
		hours_each = HourLocator()
		mins = MinuteLocator(byminute=[10,20,30,40,50])
		#mins = MinuteLocator(byminute=30)
		mins_each = MinuteLocator()
		dateFmt = DateFormatter('%H:%M')
		ax.xaxis.set_major_locator(hours_each)
		ax.xaxis.set_major_formatter(dateFmt)
		ax.xaxis.set_minor_locator(mins)
		#increase size of tick marks
		ax.tick_params('both', length=8, width=1.2, which='major')
		ax.tick_params('both', length=4, width=1, which='minor')
	
	plt.xticks(rotation = 30, fontsize = 14)
	plt.yticks(fontsize=14)
	
	
	## Plot mixed layer height if provided:
	#if ML_height!=0:
	if len(ML_height)>0:
		plt.plot(times_utc,ML_height,'k', linewidth=2)

	
	plt.tight_layout()
	
	if show == True:
		plt.show()

	if save == True:
		save_plot(figname,fig)

	return fig