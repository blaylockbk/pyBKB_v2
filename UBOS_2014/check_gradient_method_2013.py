# Brian Blaylock
# Summer 2014
# University of Utah

### Uses functions from ceil_functions.py to create ceilometer plots

# Creates backscatter plot and finds mixed layer height with 
# gradient or threshold method

from ceil_functions import *

## Inputs collected from program call
st = sys.argv[1]          				# YYYYMMDDHH: 2014050618
et = sys.argv[2]           				# YYYYMMDDHH: 2014050818
bottom = float(sys.argv[3])				# 0
top = float(sys.argv[4])				# 1000
station = (sys.argv[5]).upper()			# URHCL, ROOSC
threshold = float(sys.argv[6])			# used in fixed-threshold method

UTC = True
LOCAL = False
do_threshold_method = False
do_gradient_method = True


# String Date Range Formats
start = datetime.strptime(st,"%Y%m%d%H")
end = datetime.strptime(et,"%Y%m%d%H")
sd = start.strftime(("%b%d%H")+"-"+end.strftime("%b%d%H"))
sd_with_year = start.strftime(("%b %d, %Y")+' - '+end.strftime("%b %d, %Y"))

##--------------- Load Data ----------------------##
if station == 'ROOSC':
## Get data from ceil_archive directory
	bs_final, bs_final_local, times_utc, times_local, height  = load_ROOSC_data(st, et, bottom, top, station)
else: 
## get data from ASN
	bs_final, bs_final_local, times_utc, times_local, height  = load_ASN_data(st, et, bottom, top, station)

	
##--------- Mixed Layer Height Methods -----------##
if do_threshold_method:

	thresh_method_results = fixed_threshold_method(bs_final,height,threshold)
	thresh_method_results = smoother(thresh_method_results)
	plot_title = station+'\n'+sd_with_year+'\n'+'Threshold: '+str(threshold)
	
	# make plot
	if UTC:
		figname = station+'_'+sd+'_'+str(bottom)+'-'+str(top)+'_UTC_T-'+str(int(abs(threshold*10)))+'.png'
		fig_utc = new_plot('UTC', plot_title,figname, times_utc, height, bs_final, ML_height=thresh_method_results, save=True, show=True)
	if LOCAL:
		figname = station+'_'+sd+'_'+str(bottom)+'-'+str(top)+'_loc_T-'+str(int(abs(threshold*10)))+'.png'
		fig_local = new_plot('Local', plot_title,figname, times_local, height, bs_final_local,ML_height=thresh_method_results_results, save=False, show=False)
		

if do_gradient_method:
	# First, smooth the backscatter data to eliminate noise.
	bs_final = medfilt2d(bs_final,51)
	bs_final = medfilt2d(bs_final,51)
	bs_final = medfilt2d(bs_final,51)
	bs_final = medfilt2d(bs_final,51)

	
	grad_method_results = gradient_method(bs_final,height)
	grad_method_results = smoother(grad_method_results)
	plot_title = station+'\n'+sd_with_year+'\n'+'Gradient Method'

	
###
### make plot

figname = station+'_'+sd+'_'+str(bottom)+'-'+str(top)+'_UTC_grad.png'

## Creates a plot of backscatter
	# convert DateTime array to matplotlib.dates format
timezone='UTC'
ML_height=grad_method_results
tick_every = 12
	
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

fig = plt.figure(1, figsize=(12,6))
ax = fig.add_subplot(1,2,1)
qmesh = ax.pcolormesh(ptt,phh,bs_final,cmap=plt.cm.jet,vmin=minv, vmax=maxv)

# Colorbar
cb = fig.colorbar(qmesh,ax=ax, shrink=0.8, pad = 0.02)
cb.ax.set_ylabel('Backscatter [log10 m-1 sr-1]')
tv = np.linspace(minv,maxv,7)
cb.ax.set_yticklabels(tv, fontsize = 10)
cb.set_ticks(tv)

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

##### Plot a single backscatter profile
# plot the 12th hour backscatter profile
hour = 12
ax = fig.add_subplot(1,2,2)
profile_index = len(bs_final)/24 *hour
profile = bs_final[profile_index]
#find slope
slope=[0]
i = 0
while i < len(profile)-1:
	if profile[i]<-8.5:
			## If the backscatter is small, it has attenuated
			## and we shouldn't think it's a minimum in the gradient.
			## Instead, we'll input a nan to the slope list and move on.
				slope.append(np.nan)
				i +=1
				continue	
	db_dz = (profile[i+1]-profile[i])/((i+1)-i)
	slope.append(db_dz)
	i += 1	
print 'min',np.argmin(slope)
print profile
print profile.size
print slope
plt.plot(profile,np.arange(len(profile))*10, label="profile")
plt.plot(slope,np.arange(len(profile))*10, label="gradient")

plt.title('backscatter:\nhour '+str(hour))
plt.legend(loc="upper center")
plt.tight_layout()


plt.show()		
