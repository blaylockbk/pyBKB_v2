"""
Plotting Ceilometer Data
Using OPeNDAP to grab ASN DATA
Mountain Meteorology Research Group
University of Utah
Brian Blaylock
Summer 2014

Call program with parameters:
$ python pydap_ASN_threshold.py start_date(UTC) end_date(UTC) bottom_height top_height STATION_name threshold
		start_date:	YYYYMMDDHH
		end_date:	YYYYMMDDHH
		bottom:		usually 0
		top:		about 1000
		station: 	URHCL (or ROOSC for 2013 data)
		threshold:	about -7

examples:
	python pydap_ASN_threshold.py 2013020100 2013020800 1 1000 ROOSC -7.5
	python pydap_ASN_threshold.py 2014011400 2014012900 1 1000 URHCL -7.5
	python pydap_ASN_threshold.py 2014021300 2014022200 1 1000 URHCL -7.5

troubleshooting:
	1) Check that dates are correct. It's possible there isn't data for your 

"""

import sys
import pydap.client as pd
import matplotlib.pyplot as plt
import numpy as np
import time
import calendar
from datetime import datetime, timedelta
from scipy.signal import medfilt


##___________Set desired times and plots__________
## Choose time zone to plot
plot_utc = True	
plot_local = False
## Process Methods
FIXED_threshold_method = True
ADJUSTABLE_threshold_method = False
gradient_method = False

## frequency of hour labels, set to 1, 12 or 24. 
## 		1:  every hour tick labels
## 		12: only "00" and "12" hour tick labels
## 		24: no hour tick labels
hr_tick_fq = 12  


#===============================================================================================
#                    Functions
#===============================================================================================

def load_ASN_data(st, et):
## Loads the data from the ASN network through OPeNDAP
	print 'loading data...'
	#___________________Load Data__________________________
	start = datetime.fromtimestamp(time.mktime(time.strptime(st,"%Y%m%d%H")))
	end = datetime.fromtimestamp(time.mktime(time.strptime(et,"%Y%m%d%H")))

	times = []
	levs = []
	bs_data = []
	fileList = []
	src = "http://asn.mesowest.net/data/opendap/PUBLIC/{0:%Y/%m/%d/}{1}_{0:%Y%m%d}.h5"

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

	## utc time
	times_utc = np.array([time.strftime("%Y%m%d%H",time.gmtime(i)) for i in times])

	## local time
	times_local = np.array([time.strftime('%Y%m%d%H',time.localtime(i)) for i in times])

	## time_mask in utc time
	time_mask = np.arange(times.shape[0])[(times>=calendar.timegm(start.timetuple()))&(times<calendar.timegm(end.timetuple()))]

	## time_mask in local time
	ustart = time.gmtime(time.mktime(start.timetuple()))
	uend = time.gmtime(time.mktime(end.timetuple()))
	time_mask_loc = np.arange(times.shape[0])[(times>=calendar.timegm(ustart))&(times<calendar.timegm(uend))]

	#print time_mask.min(), time_mask.max()

	### convert local time to utctime
	### times_utc = np.array([time.strftime("%Y%m%d%H",time.gmtime(time.mktime(time.strptime(i,"%Y%m%d%H")))) for i in times_local])

	## plot BS over a specific DATTIM and HEIGHT range. Grab time and height, so we can figure what dimensions to ask for from the BS dataset.
	## create an array of only the array-indices which are within our bottom to top limit.
	height_mask = np.arange(height.shape[0])[(height>=bottom)&(height<top)]
	height_restriction = (np.amin(height_mask),np.amax(height_mask))
	#print height_restriction

	time_restriction = (np.amin(time_mask),np.amax(time_mask))
	time_restriction_loc = (np.amin(time_mask_loc),np.amax(time_mask_loc))

	#print time_restriction

	bs_final = bs_data[time_restriction[0]:time_restriction[1],height_restriction[0]:height_restriction[1]]
	bs_final_loc = bs_data[time_restriction_loc[0]:time_restriction_loc[1],height_restriction[0]:height_restriction[1]]

	return bs_final, bs_final_loc, time_restriction, time_restriction_loc, height, height_restriction,times_utc,times_local
	
def load_ROOSC_data(st, et):
## Loads and converts the Roosevelt 2013 ceilometer data.
	print 'loading data...'
	#___________________Load Data__________________________
	start = datetime.fromtimestamp(time.mktime(time.strptime(st,"%Y%m%d%H")))
	end = datetime.fromtimestamp(time.mktime(time.strptime(et,"%Y%m%d%H")))
	
	dir = '/uufs/chpc.utah.edu/common/home/horel-group/ceilometer_archive/rooscl31/'
	
	times = []
	bs_data = []	
	height = []
	bs_data = []	
	
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
	
	for i in range(int(start_file),int(end_file)+1):
		file_list.append(str(i)+'.ascii')
	
	for i in range(len(file_list)):
		print dir+file_list[i]
		data = np.genfromtxt(dir+file_list[i],delimiter=',')
		data = np.flipud(np.rot90(data))
		tt = data[0,1:]
		bs = data[1:102,1:]
		if i == 0:
			bs_data = bs
		else:
			bs_data = np.column_stack([bs_data,bs])
		times = np.append(times,tt)
	lev = data[1:102,0]
	height = np.append(height,lev)
	bs_data = (np.rot90(np.fliplr((CONVERT(bs_data)))))


	## utc time
	times_utc = np.array([time.strftime("%Y%m%d%H",time.gmtime(i)) for i in times])

	## local time
	times_local = np.array([time.strftime('%Y%m%d%H',time.localtime(i)) for i in times])

	## time_mask in utc time
	time_mask = np.arange(times.shape[0])[(times>=calendar.timegm(start.timetuple()))&(times<calendar.timegm(end.timetuple()))]

	## time_mask in local time
	ustart = time.gmtime(time.mktime(start.timetuple()))
	uend = time.gmtime(time.mktime(end.timetuple()))
	time_mask_loc = np.arange(times.shape[0])[(times>=calendar.timegm(ustart))&(times<calendar.timegm(uend))]

	#print time_mask.min(), time_mask.max()

	### convert local time to utctime
	### times_utc = np.array([time.strftime("%Y%m%d%H",time.gmtime(time.mktime(time.strptime(i,"%Y%m%d%H")))) for i in times_local])

	## plot BS over a specific DATTIM and HEIGHT range. Grab time and height, so we can figure what dimensions to ask for from the BS dataset.
	## create an array of only the array-indices which are within our bottom to top limit.
	height_mask = np.arange(height.shape[0])[(height>=bottom)&(height<top)]
	height_restriction = (np.amin(height_mask),np.amax(height_mask))
	#print height_restriction

	time_restriction = (np.amin(time_mask),np.amax(time_mask))
	time_restriction_loc = (np.amin(time_mask_loc),np.amax(time_mask_loc))

	#print time_restriction

	bs_final = bs_data[time_restriction[0]:time_restriction[1],height_restriction[0]:height_restriction[1]]
	bs_final_loc = bs_data[time_restriction_loc[0]:time_restriction_loc[1],height_restriction[0]:height_restriction[1]]
	
	return bs_final, bs_final_loc, time_restriction, time_restriction_loc, height, height_restriction,times_utc,times_local

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

def fixed_threshold_method(input_backscatter, threshold):
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
	
def adjustable_threshold_method(input_backscatter, threshold, min_height=50):
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

def gradient_method(input_backscatter):
## Takes and array of backscatter data and returns an array of the
## mixed layer heights using the gradient method.
	ML_grad = []
	for each_ob in input_backscatter:
		slope = []
		i = 0
		while i < len(each_ob)-1:
			db_dz = (each_ob[i+1]-each_ob[i])/((i+1)-i)
			slope.append(db_dz)
			i += 1
		ML_grad.append(height[np.argmin(slope)])				
	return ML_grad

def smoother(ML_height, num_times = 4):
## Smooths the ML_height array 
## num_times is the number of times it is smoothed: default is four.
	print 'applying smoother...'
	while num_times >0:
		ML_height = medfilt(ML_height,21) # higher kernal = more smoothing. Kernal should be odd.
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
	
	print ptt
	print phh
	print ptt.shape
	print phh.shape
	print bs_final.shape
	CS = plt.pcolormesh(ptt,phh,bs_final,cmap=plt.cm.jet,vmin=-8, vmax=-5)
	cb = plt.colorbar(shrink=.8,pad = 0.02)
	cb.ax.set_ylabel('Backscatter [log10 m-1 sr-1]')
	tv = np.linspace(minv,maxv,7)
	cb.ax.set_yticklabels(tv, fontsize = 10)
	cb.set_ticks(tv)
	plt.xticks(xts,xtsl,rotation = 30, fontsize = 10)
	plt.setp(ax1.get_xticklabels(), visible=False)
	plt.setp(ax1.get_xticklabels()[::label_space], visible=True)
	
	x1,x2,y1,y2 = plt.axis()
	plt.axis((x1,x2,pheight[0],pheight[-1]))
	plt.ylabel('Height (m)')
	plt.xlabel('Day:Hour ('+type+')')
	plt.title(station+'\n'+sd_with_year+'\n'+'Threshold: '+str(threshold))
	
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

#===============================================================================================	

## Inputs collected from program call
st = sys.argv[1]          				# YYYYMMDDHH: 2014050618
et = sys.argv[2]           				# YYYYMMDDHH: 2014050818
bottom = float(sys.argv[3])				# 0
top = float(sys.argv[4])				# 1000
station = (sys.argv[5]).upper()			# URHCL, ROOSC
threshold = float(sys.argv[6])			# used in fixed-threshold method


print st, et, bottom, top, station, threshold
outputDir = "./"
   

start = datetime.fromtimestamp(time.mktime(time.strptime(st,"%Y%m%d%H")))
end = datetime.fromtimestamp(time.mktime(time.strptime(et,"%Y%m%d%H")))


##--------------- Load Data ----------------------##

if station == 'ROOSC':
## Get data from ceil_archive directory
	bs_final, bs_final_loc, time_restriction, time_restriction_loc, height, height_restriction, times_utc, times_local  = load_ROOSC_data(st,et)
else: 
## get data from ASN
	bs_final, bs_final_loc, time_restriction, time_restriction_loc, height, height_restriction, times_utc, times_local  = load_ASN_data(st,et)

	
##------------ Identify Mixed Layer ---------------##

if FIXED_threshold_method:
	'''
	Threshold Method:
	Method to determine depth of the boundary layer.
	A threshold backscatter value is subjectively chosen as the mixed layer boundary.
	The Following provide two threshold methods: FIXED and ADJUSTABLE
	FIXED: 		A single threshold value is chosen. This has some disadvantages if 
				the threshold is to low then the mixed layer height will not be found.
	'''
	# Threshold value is defined when program is called
	
	if plot_utc:
		ML_height = fixed_threshold_method(bs_final,threshold) 
		ML_height = smoother(ML_height)
		#! Write Data
		#write_heights(ML_height,ML_height,threshold)
		
	if plot_local:
		ML_height_loc = fixed_threshold_method(bs_final_loc, threshold)
		ML_height_loc = smoother(ML_height_loc)

if ADJUSTABLE_threshold_method:
	"""
	Threshold Method:
	Method to determine depth of the boundary layer.
	A threshold backscatter value is subjectively chosen as the mixed layer boundary.
	The Following provide two threshold methods: FIXED and ADJUSTABLE
	ADJUSTABLE: First, find the mixed layer height with the maximum threshold. 
				If that threshold returns a height below 50 meters then subtract 
				.01 from the threshold and try again. (The heights are colored by
				the threshold used to find that height.)
	"""
	if plot_utc:
		ADJ_height, threshold_ARRAY = adjustable_threshold_method(bs_final,threshold)
		
	if plot_local:	
		ADJ_height_loc = adjustable_threshold_method(bs_final_loc,threshold)

if gradient_method:
	"""
	The Gradient Method:
	Method to determine the depth of the mixed layer. 
	Height is defined by the maximum negative gradient of backscatter.
	h_GM = min[G(z)], where G(z)=dBackscatter/dz

	This doesn't really seem to work because of the noise at upper levels.
	Or my method is incorrect.
	"""
	if plot_utc:
		ML_grad = gradient_method(bs_final)
		
	if plot_local:
		ML_grad_loc = gradient_method(bs_final_loc)


#------------ Make Plots -------------------------##

if plot_utc:
	make_plots('UTC', bs_final, ML_height, time_restriction)

if plot_local:
	make_plots('LOCAL', bs_final_loc, ML_height_loc, time_restriction_loc)
	
	
exit(0)
