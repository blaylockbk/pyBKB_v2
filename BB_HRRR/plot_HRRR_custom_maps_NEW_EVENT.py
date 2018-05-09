# Brian Blaylock
# December 8, 2017                   The Horel Christmas Party is tonight :)

"""
Plot a custom HRRR map for an event.

Plots a sample image of HRRR near the fire.

Note: For CGI, cannot print anything to screen when outputting a .png file
"""

import numpy as np
from datetime import datetime, timedelta
import multiprocessing #:)


import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
## Reset the defaults (see more here: http://matplotlib.org/users/customizing.html)
mpl.rcParams['figure.figsize'] = [12, 10]
mpl.rcParams['savefig.bbox'] = 'tight'
mpl.rcParams['savefig.dpi'] = 100     # For web
mpl.rcParams['figure.titleweight'] = 'bold'
mpl.rcParams['xtick.labelsize'] = 10
mpl.rcParams['ytick.labelsize'] = 10
mpl.rcParams['axes.labelsize'] = 8
mpl.rcParams['axes.titlesize'] = 12
mpl.rcParams['figure.subplot.hspace'] = 0.01


import sys, os
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
from plot_HRRR_custom_NEW import *

def lots_of_plots(VALIDDATE):
    plt.clf()
    plt.cla()

    model = 'hrrr'
    dsize = 'full'
    background = 'none'
    location = None
    lat = None
    lon = None

    fxx = 18
    RUNDATE = VALIDDATE - timedelta(hours=fxx)


    lats, lons = load_lats_lons(model)

    m, alpha, half_box, barb_thin = draw_map_base(model, dsize, background,
                                                  location, lat, lon,
                                                  RUNDATE, VALIDDATE, fxx)

    draw_tmp_dpt(m, lons, lats,
                 model, dsize, background,
                 location, lat, lon,
                 RUNDATE, VALIDDATE, fxx,
                 alpha, half_box, barb_thin,
                 variable='DPT:2 m',
                 p05p95=True)
    '''
    draw_wind(m, lons, lats,
            model, dsize, background,
            location, lat, lon,
            RUNDATE, VALIDDATE, fxx,
            alpha, half_box, barb_thin,
            level='10 m',
            p95=True)
    '''
    draw_hgt(m, lons, lats,
            model, dsize, background,
            location, lat, lon,
            RUNDATE, VALIDDATE, fxx,
            alpha, half_box, barb_thin,
            level='500 mb')


    SAVEDIR = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/PhD/HRRR/Events_Day/tmp/'
    if not os.path.exists(SAVEDIR):
        os.makedirs(SAVEDIR)

    plt.savefig(SAVEDIR+'DPT_p05p95_%s_F%02d' % (VALIDDATE.strftime('%Y%m%d_%H%M'), fxx))



# Valid Dates
sDATE = datetime(2018, 4, 12, 12)
eDATE = datetime(2018, 4, 14, 12)

hours = (eDATE-sDATE).seconds/60/60 + (eDATE-sDATE).days*24
DATES = [sDATE + timedelta(hours=h) for h in range(0,hours+1)]

# Multiprocessing :)

num_proc = multiprocessing.cpu_count() # use all processors

num_proc = 12                           # specify number to use (to be nice)

p = multiprocessing.Pool(num_proc)

p.map(lots_of_plots, DATES)
p.close()
