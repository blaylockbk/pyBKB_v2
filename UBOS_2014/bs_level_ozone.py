### Uses functions from ceil_functions.py to create ceilometer plots

from ceil_functions import *
from ceil_ozone_functions import *
from ozone_functions import *

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
##--------- Plot Mixed Layer Height Methods -----------##
if do_threshold_method:

	thresh_method_results = fixed_threshold_method(bs_final,height,threshold)
	thresh_method_results = smoother(thresh_method_results)
	plot_title = station+'\n'+sd_with_year+'\n'+'Threshold: '+str(threshold)
	
	# make plot
	if UTC:
		figname = 'Ozone'+station+'_'+sd+'_'+str(bottom)+'-'+str(top)+'_UTC_T-'+str(int(abs(threshold*10)))+'.png'
		fig_utc = ozone_plot(st, et,'UTC', plot_title,figname, times_utc, height, bs_final, ML_height=thresh_method_results, save=True, show=True)
	if LOCAL:
		figname = 'Ozone'+station+'_'+sd+'_'+str(bottom)+'-'+str(top)+'_loc_T-'+str(int(abs(threshold*10)))+'.png'
		fig_local = ozone_plot(st, et,'Local', plot_title,figname, times_local, height, bs_final_local,ML_height=thresh_method_results_results, save=False, show=False)


if do_gradient_method:
	# First, smooth the backscatter data to eliminate noise.
	bs_final = medfilt2d(bs_final,51)
	bs_final = medfilt2d(bs_final,51)
	bs_final = medfilt2d(bs_final,51)
	bs_final = medfilt2d(bs_final,51)
	
	grad_method_results = gradient_method(bs_final,height)
	grad_method_results = smoother(grad_method_results)
	plot_title = station+'\n'+sd_with_year+'\n'+'Gradient Method'
"""
	# make plot
	if UTC:
		figname = 'Ozone'+station+'_'+sd+'_'+str(bottom)+'-'+str(top)+'_UTC_grad.png'
		fig_utc = ozone_plot(st, et,'UTC', plot_title,figname, times_utc, height, bs_final, ML_height=grad_method_results, save=True, show=True)
		
	if LOCAL:
		figname = 'Ozone'+station+'_'+sd+'_'+str(bottom)+'-'+str(top)+'_loc_grad.png'
		fig_local = ozone_plot(st, et,'Local', plot_title,figname, times_local, height, bs_final_local,ML_height=grad_method_results, save=False, show=False)

##---------- Ozone and Height Correlation -----##
ozone_times, ozone_gusher, ozone_lapoint = load_ozone_data_2013(st,et)

# need to downsample Backscatter 16 second data to 5 minute data like the ozone measurments
downSamp_height = downsample_heights(grad_method_results,times_utc, ozone_gusher, ozone_times)
plt.plot(ozone_gusher)
plt.plot(downSamp_height)
plt.show()
plt.scatter(ozone_gusher,downSamp_height)
plt.show()
"""

# Make Plots
