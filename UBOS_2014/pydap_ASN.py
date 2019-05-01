## Original pydap_ASN.py created by Xia
## May 2014

## Using OPeNDAP to grab ASN DATA
## Plotting MMLCL data from the opendap server using pydap

import sys
import pydap.client as pd
import matplotlib.pyplot as plt
import numpy as np
import time
import calendar
from datetime import datetime, timedelta

def datespan(startDate, endDate, delta=timedelta(days=1)):
    currentDate = startDate
    while currentDate < endDate:
        yield currentDate
        currentDate += delta

## start time, end time, height bottom, height top, station name

st = sys.argv[1]          ## YYYYMMDDHH: 2014050618
et = sys.argv[2]            ## YYYYMMDDHH: 2014050818
bottom = float(sys.argv[3])
top = float(sys.argv[4])
station = (sys.argv[5]).upper()
threshold = float(sys.argv[6])

print st, et, bottom, top, station
outputDir = "./"
plot_utc = 1            ## plot in utc time
plot_local = 1          ## plot local utc time

## frequency of hour labels, set to 1, 12 or 24. 
## 1:every hour tick labels
## 12: only "00" and "12" hour tick labels
## 24: no hour tick labels
hr_tick_fq = 12       

start = datetime.fromtimestamp(time.mktime(time.strptime(st,"%Y%m%d%H")))
end = datetime.fromtimestamp(time.mktime(time.strptime(et,"%Y%m%d%H")))


times = []
levs = []
bs_data = []
for timestamp in datespan(start,end,delta=timedelta(days=1)):
	src = "http://asn.mesowest.net/data/opendap/PUBLIC/{0:%Y/%m/%d/}{1}_{0:%Y%m%d}.h5"
	source = src.format(timestamp,station)
	print source
	## pydap created a "dataset" object, which we can see has all the structure of the file.  There is a HEIGHT attribute, which contains the height dimension, and a data attribute which contains all the different data columns. 
	data = pd.open_url(source)
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



########################################################################
###### Threshold Method ################################################

# Threshold defined when program is called

## for UTC time
ML_height = []												# create an array containing the Mixed Layer heights.

for each_ob in bs_final:									# For each observation from the ceilometer
	current_height_index = 0								# We are looking for the height of the mixed layer. Start at zero.
	for i in each_ob:										# For each element of each observation									
		if i < threshold:									# If the element is less than the threshold
			break											# stop.
		else:												# Else, if the element is greater than the threshold, 
			current_height_index += 1						# add one to the current height index.
	ML_height.append(height[current_height_index])			# When threshold height index is found, story in array. (Use the height index to find the height.)
#print ML_height								

## for Local time
ML_height_loc = []

for each_ob in bs_final_loc:								
	current_height_index_loc = 0							
	for i in each_ob:																			
		if i < threshold:									
			break											
		else:												
			current_height_index_loc += 1						
	ML_height_loc.append(height[current_height_index_loc])
#print ML_height_loc


########################################################################
########################################################################


## plot
sd = start.strftime(("%b%d%H")+"-"+end.strftime("%b%d%H"))						# string dates
sd_with_year = start.strftime(("%b %d, %Y")+' - '+end.strftime("%b %d, %Y"))		

if plot_utc:
	# set plotting grids
	pheight = height[height_restriction[0]:height_restriction[1]]
	ptt = np.zeros(bs_final.shape)
	phh = np.zeros(bs_final.shape)
	for i in range(ptt.shape[0]):
		ptt[i,:] = i
	for j in range(phh.shape[1]):
		phh[:,j] = pheight[j]
	figname = outputDir + station+"_"+sd+"_"+str(int(bottom))+"-"+str(int(top))+"_utc.png"
	ptime = times_utc[time_restriction[0]:time_restriction[1]]
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
	ax1 = fig.add_subplot(1,1,1)
	
	# set plotting range
	minv = int(np.around(np.min(bs_final)))
	maxv = int(np.around(np.max(bs_final)))
	bs_final[bs_final>maxv] = maxv
	bs_final[bs_final<minv] = minv

	CS = plt.pcolormesh(ptt,phh,bs_final,cmap=plt.cm.jet)
	cb = plt.colorbar(shrink=.8,pad = 0.02)
	tv = np.linspace(minv,maxv,6)
	cb.ax.set_yticklabels(tv, fontsize = 10)
	cb.set_ticks(tv)
	plt.xticks(xts,xtsl,rotation = 30, fontsize = 10)
	plt.setp(ax1.get_xticklabels(), visible=False)
	plt.setp(ax1.get_xticklabels()[::label_space], visible=True)
	
	x1,x2,y1,y2 = plt.axis()
	plt.axis((x1,x2,pheight[0],pheight[-1]))
	plt.ylabel('Height (m)')
	plt.xlabel('Day:Hour (UTC)')
	plt.title(station+'\n'+sd_with_year+'\n'+'Threshold: '+str(threshold))
	
	## Plot scatter boundary layer (from threshold method)
	plt.hold(True)
	plt.scatter(np.arange(len(ML_height)),ML_height)
	plt.show()
	
	fig.savefig(figname, bbox_inches='tight',pad_inches=0.05)
	plt.close()	


if plot_local:
	# set plotting grids
	pheight = height[height_restriction[0]:height_restriction[1]]
	ptt = np.zeros(bs_final_loc.shape)
	phh = np.zeros(bs_final_loc.shape)
	for i in range(ptt.shape[0]):
		ptt[i,:] = i
	for j in range(phh.shape[1]):
		phh[:,j] = pheight[j]
	figname = outputDir + station+"_"+sd+"_"+str(int(bottom))+"-"+str(int(top))+"_local.png"
	ptime = times_local[time_restriction_loc[0]:time_restriction_loc[1]]
	ts = [i[4:10] for i in ptime]
	uts = []
	for timestamp in datespan(start,end,delta=timedelta(hours=1)):
		uts.append(timestamp.strftime("%m%d%H"))

	
	xts = []
	xtsl = []
	for kts in uts:
		ind = [i for i,v in enumerate(ts) if v[0:6]==kts]
		if ind != []:
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
	ax1 = fig.add_subplot(1,1,1)
	# set plotting range
	minv = int(np.around(np.min(bs_final_loc)))
	maxv = int(np.around(np.max(bs_final_loc)))
	bs_final_loc[bs_final_loc>maxv] = maxv
	bs_final_loc[bs_final_loc<minv] = minv
	CS = plt.pcolormesh(ptt,phh,bs_final_loc,cmap=plt.cm.jet)
	cb = plt.colorbar(shrink=.8,pad = 0.02)
	tv = np.linspace(minv,maxv,6)
	cb.ax.set_yticklabels(tv, fontsize = 10)
	cb.set_ticks(tv)
	plt.xticks(xts,xtsl,rotation = 30, fontsize = 10)
	plt.setp(ax1.get_xticklabels(), visible=False)
	plt.setp(ax1.get_xticklabels()[::label_space], visible=True)
	
	x1,x2,y1,y2 = plt.axis()
	plt.axis((x1,x2,pheight[0],pheight[-1]))
	plt.ylabel('Height (m)')
	plt.xlabel('Day:Hour (Local)')
	plt.title(station+'\n'+sd_with_year+'\n'+'Threshold: '+str(threshold))
	
	## Plot scatter boundary layer (from threshold method)
	plt.hold(True)
	plt.scatter(np.arange(len(ML_height_loc)),ML_height_loc)
	plt.show()
	
	fig.savefig(figname, bbox_inches='tight',pad_inches=0.05)	
	plt.close()	
	
exit(0)
