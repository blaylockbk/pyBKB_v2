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
	#height = height + 1561  #adjust for hight ASL
else: 
## get data from ASN
	bs_final, bs_final_local, times_utc, times_local, height  = load_ASN_data(st, et, bottom, top, station)
	#height = height + 1543  #adjust for hight ASL
	
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
	# (This is kind of subjective.)
	bs_final_smoothed = medfilt2d(bs_final,[49,49])			# [49,37] = 13 mins, 360 meters
	bs_final_smoothed = medfilt2d(bs_final_smoothed,[49,49])
	bs_final_smoothed = medfilt2d(bs_final_smoothed,[49,49])
	bs_final_smoothed = medfilt2d(bs_final_smoothed,[49,49])
	
	grad_method_results = gradient_method(bs_final_smoothed,height)
	grad_method_results = smoother(grad_method_results)
	plot_title = station+'\n'+sd_with_year+'\n'+'Gradient Method'
	plot_title = 'Ceilometer Backscatter\n'+sd_with_year

	# make plot
	if UTC:
		figname = station+'_'+sd+'_'+str(bottom)+'-'+str(top)+'_UTC_grad.png'
		fig_utc = new_plot('UTC', plot_title,figname, times_utc, height, bs_final, ML_height=grad_method_results, save=True, show=True)
		
	if LOCAL:
		figname = station+'_'+sd+'_'+str(bottom)+'-'+str(top)+'_loc_grad.png'
		fig_local = new_plot('Local', plot_title,figname, times_local, height, bs_final_local,ML_height=grad_method_results, save=False, show=False)

