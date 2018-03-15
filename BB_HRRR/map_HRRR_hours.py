#!/uufs/chpc.utah.edu/sys/installdir/anaconda/4.2.0/bin/python

# Brian Blaylock
# June 8, 2017     # I accidentally made beef jerky in the crock pot last night


"""
Plots a sample image of HRRR near the fire.

Note: For CGI, cannot print anything to screen when outputting a .png file
"""

import numpy as np
from datetime import datetime, timedelta
import h5py


import matplotlib as mpl

import matplotlib.pyplot as plt
## Reset the defaults (see more here: http://matplotlib.org/users/customizing.html)
mpl.rcParams['figure.figsize'] = [12, 10]
mpl.rcParams['savefig.bbox'] = 'tight'
mpl.rcParams['savefig.dpi'] = 300
mpl.rcParams['figure.titleweight'] = 'bold'
mpl.rcParams['xtick.labelsize'] = 10
mpl.rcParams['ytick.labelsize'] = 10
mpl.rcParams['axes.labelsize'] = 8
mpl.rcParams['axes.titlesize'] = 12
mpl.rcParams['figure.subplot.hspace'] = 0.01

# Colorbar
pad = 0.01
shrink = 0.7
# Map Resolution, 'l' - low, 'i' - intermediate, 'h' - high
map_res = 'h'


import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
sys.path.append('/uufs/chpc.utah.edu/sys/pkg/python/2.7.3_rhel6/lib/python2.7/site-packages/')
from BB_basemap.draw_maps import draw_CONUS_HRRR_map, Basemap
from BB_downloads.HRRR_S3 import get_hrrr_variable
from BB_MesoWest.MesoWest_STNinfo import get_station_info
from BB_wx_calcs.wind import wind_uv_to_spd
from BB_wx_calcs.humidity import Tempdwpt_to_RH
from BB_data.grid_manager import pluck_point_new


# === Load Form Input =========================================================
model = 'hrrr'
sDATE = datetime(2017, 3, 14, 0)
eDATE = datetime(2017, 3, 15, 12)

DATES = [sDATE+timedelta(hours=h) for h in range((eDATE-sDATE).days*24+(eDATE-sDATE).seconds/60/60)]

fxx = 0
dsize = 'conus'

plotcode = 'MSLP_Contour,dBZ_Fill'


# === Some housekeeping variables =============================================

# Preload the latitude and longitude grid
latlonpath = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando/hrrr/HRRR_latlon.h5'
latlonh5 = h5py.File(latlonpath, 'r')
gridlat = latlonh5['latitude'][:]
gridlon = latlonh5['longitude'][:]


# === Create map of the domain ================================================

m = draw_CONUS_HRRR_map(res=map_res)
m.drawcountries(zorder=500)
m.drawstates(zorder=500)
m.drawcoastlines(zorder=500)
m.fillcontinents(color='tan',lake_color='lightblue', zorder=0)
m.drawmapboundary(fill_color='lightblue')

for DATE in DATES:
    # Convert Valid Date to Run Date, adjusted by the forecast
    DATE = DATE - timedelta(hours=fxx)

    plt.title('%s' % (model.upper()), fontweight='bold')
    plt.title('Run: %s F%02d' % (DATE.strftime('%Y-%m-%d %H:%M UTC'), fxx), loc='left')
    plt.title('Valid: %s' % (DATE+timedelta(hours=fxx)).strftime('%Y-%m-%d %H:%M UTC') , loc='right')
    # =============================================================================

    from BB_cmap.reflectivity_colormap import reflect_ncdc
    # Get Data
    if model == 'hrrr':
        REFC = 'REFC:entire'
    elif model == 'hrrrX' or model == 'hrrrAK':
        REFC = 'var discipline=0 center=59 local_table=1 parmcat=16 parm=196'
    H_ref = get_hrrr_variable(DATE, REFC,
                                model=model, fxx=fxx,
                                outDIR='/uufs/chpc.utah.edu/common/home/u0553130/temp/',
                                verbose=False, value_only=True)

    # Mask values
    dBZ = H_ref['value']
    dBZ = np.ma.array(dBZ)
    dBZ[dBZ == -10] = np.ma.masked

    # Add Contour to plot
    PM = m.pcolormesh(gridlon, gridlat, dBZ,
                        cmap=reflect_ncdc(),
                        vmax=80, vmin=0,
                        latlon=True)
    if DATE == DATES[0]:
        cb2 = plt.colorbar(orientation='horizontal', shrink=shrink, pad=pad)
        cb2.set_label('Simulated Composite Reflectivity (dBZ)')

    # Add contour
    H = get_hrrr_variable(DATE, 'MSLMA:mean sea level',
                        model=model, fxx=fxx,
                        outDIR='/uufs/chpc.utah.edu/common/home/u0553130/temp/',
                        verbose=False, value_only=True)
    CS = m.contour(gridlon, gridlat, H['value']/100., 
                    latlon=True,
                    levels=range(952, 1200, 4),
                    colors='k',
                    zorder=400)
    CSL = CS.clabel(inline=1, fmt='%2.f',
                    zorder=400)

    plt.savefig('/uufs/chpc.utah.edu/common/home/u0553130/public_html/Events/MSLP_march13-14_eastcoast_storm/radar_mslp/%s_f%02d' % (DATE.strftime('%Y-%m-%d_%H%M'), fxx))	# Plot standard output.

    PM.remove()
    for i in CS.collections:
        i.remove()
    for i in CSL:
        i.remove()
    
    print "finished", DATE
