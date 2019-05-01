### Uses functions from ceil_functions.py to complete tasks

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

	

##--------------Mixed Layer Height Methods --------##
if do_gradient_method:
	# First, smooth the backscatter data
	bs_final = medfilt2d(bs_final,21)
	bs_final = medfilt2d(bs_final,21)
	bs_final = medfilt2d(bs_final,21)
	bs_final = medfilt2d(bs_final,21)
	
	grad_method_results = gradient_method(bs_final,height)
	grad_method_results = smoother(grad_method_results)
	plot_title = station+'\n'+sd_with_year+'\n'+'Gradient Method'
	
#------------ Make Plots -------------------------##
# make plot title
	# string of dates
sd = start.strftime(("%b%d%H")+"-"+end.strftime("%b%d%H"))
	# string of dates w/ years
sd_with_year = start.strftime(("%b %d, %Y")+' - '+end.strftime("%b %d, %Y"))
	
plot_title = station+'\n'+sd_with_year+'\n'+'Gradient Method'


if UTC:
	fig_utc = new_plot('UTC', plot_title, times_utc, height, bs_final, ML_height=grad_method_results, save=True, show=True)
if LOCAL:
	fig_local = new_plot('Local', plot_title, times_local, height, bs_final_local,ML_height=grad_method_results, save=False, show=False)

#fig_utc.axhline(200, c='r', linestyle='--')

fig_utc.show()




