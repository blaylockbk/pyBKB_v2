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
do_gradient_method = False


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

	
##--------------- Make Plots ----------------------##
plot_title = station+'\n'+sd_with_year
plot_title = station+'\n'+ start.strftime(("%b %d, %Y"))
plot_title = start.strftime(("%b %d, %Y"))

# make plot
if UTC:
	figname = 'RAW_'+station+'_'+sd+'_'+str(bottom)+'-'+str(top)+'_UTC_grad.png'
	fig_utc = new_plot('UTC', plot_title,figname, times_utc, height, bs_final, save=True, show=True)
	
if LOCAL:
	figname = station+'_'+sd+'_'+str(bottom)+'-'+str(top)+'_loc_grad.png'
	fig_local = new_plot('Local', plot_title,figname, times_local, height, bs_final_local, save=False, show=False)

