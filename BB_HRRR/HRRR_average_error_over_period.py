# Brian Blaylock
# October 11, 2017          # I get married to my best friend next week :)

"""
Calculate the mean error for a time period.
Specify the forecast hour, date range, and variable (special case for wind).
"""

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from datetime import datetime, timedelta
import numpy as np
import multiprocessing

#Import my custom functions: https://github.com/blaylockbk/pyBKB_v2
import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2/')
from BB_downloads.HRRR_S3 import get_hrrr_variable
from BB_basemap.draw_maps import draw_CONUS_HRRR_map
from BB_wx_calcs.wind import wind_uv_to_spd

import matplotlib as mpl
mpl.rcParams['figure.figsize'] = [16, 7]
mpl.rcParams['figure.subplot.hspace'] = 0.1
mpl.rcParams['figure.subplot.wspace'] = 0.1
mpl.rcParams['savefig.bbox'] = 'tight'
mpl.rcParams['savefig.dpi'] = 100

def HRRR_error_wind_speed(DATE):
    """
    return the error between the forecast and the analysis
    Use this for multiprocessing
    """
    # HRRR Analysis
    Hu = get_hrrr_variable(DATE, variable='UGRD:'+level, verbose=False)
    Hv = get_hrrr_variable(DATE, variable='VGRD:'+level, verbose=False)
    #
    # HRRR Forecast
    Hfu = get_hrrr_variable(DATE-timedelta(hours=fxx), variable='UGRD:'+level, fxx=fxx, verbose=False)
    Hfv = get_hrrr_variable(DATE-timedelta(hours=fxx), variable='VGRD:'+level, fxx=fxx, verbose=False)
    #
    # proof that I grabbed the right data from the archive
    #print Hu['msg'], Hu['valid']
    #print Hfu['msg'], Hfu['valid']
    #
    # Calculate the difference between the HRRR analysis and HRRR forecast (fxx-anlys)
    #   so that the red shows where the forecast is fast and blue shows where forecast
    #   is slow.
    aSPD = wind_uv_to_spd(Hu['value'], Hv['value'])
    fSPD = wind_uv_to_spd(Hfu['value'], Hfv['value'])
    diff = fSPD-aSPD
    #
    return diff

def HRRR_error(DATE):
    """
    return the error between the forecast and the analysis
    Use this for multiprocessing
    """
    # HRRR Analysis
    H = get_hrrr_variable(DATE, variable=var, verbose=False)
    #
    # HRRR Forecast
    Hf = get_hrrr_variable(DATE-timedelta(hours=fxx), variable=var, fxx=fxx, verbose=False)
    #
    # proof that I grabbed the right data from the archive
    #print H['msg'], H['valid']
    #print Hf['msg'], Hf['valid']
    #
    # Calculate the difference between the HRRR analysis and HRRR forecast (fxx-anlys)
    #   so that the red shows where the forecast is fast and blue shows where forecast
    #   is slow.
    diff = Hf['value']-H['value']
    #
    return diff

# Draw HRRR CONUS
m = draw_CONUS_HRRR_map()

# need a set of lat/lon grid variables, so just grab with this...
H = get_hrrr_variable(datetime(2017, 10, 1), 'TMP:2 m')

# Make Figure
fig, [ax1, ax2] = plt.subplots(nrows=1, ncols=2)
plt.sca(ax1)
m.drawcoastlines()
m.drawcountries()
m.drawstates()
plt.sca(ax2)
m.drawcoastlines()
m.drawcountries()
m.drawstates()

options = {1:{'var'        : 'TMP:2 m',
              'name'       : '2 m Temperature',
              'mean label' : r'$\Delta$ Temperature (C)',
              'rmse label' : 'RMSE Temperature (C)',
              'save prefix': 'TMP2m',
              'mean maxmin': [3, -3],
              'rmse max'   : 5, 
              'mean cmap'  : 'bwr',
              'WIND'       : False},

           2:{'var'        : 'UGRD:10 m',
              'name'       : '10 m Wind Speed',
              'mean label' : r'$\Delta$ Wind Speed (m s$\mathregular{^{-1}}$)',
              'rmse label' : r'RMSE Wind Speed (m s$\mathregular{^{-1}}$)',
              'save prefix': 'WIND10m',
              'mean maxmin': [3, -3],
              'rmse max'   : 5, 
              'mean cmap'  : 'PRGn',              
              'WIND'       : True},

           3:{'var'        : 'REFC:entire',         # Consider there are some negative values in the data range -10 to 0
              'name'       : 'Composite Reflectivity',
              'mean label' : r'$\Delta$ Reflectivity (dBZ)',
              'rmse label' : 'RMSE Reflectivity (dBZ)',
              'save prefix': 'REFC',
              'mean maxmin': [20, -20],
              'rmse max'   : 40,
              'mean cmap'  : 'bwr', 
              'WIND'       : False},

           4:{'var'        : 'DPT:2 m',
              'name'       : 'Dew Point',
              'mean label' : r'$\Delta$ Dew Point (C)',
              'rmse label' : 'RMSE Dew Point (C)',
              'save prefix': 'DPT2m',
              'mean maxmin': [3, -3],
              'rmse max'   : 5,
              'mean cmap'  : 'BrBG', 
              'WIND'       : False},

           5:{'var'        : 'UGRD:80 m',
              'name'       : '80 m Wind Speed',
              'mean label' : r'$\Delta$ Wind Speed (m s$\mathregular{^{-1}}$)',
              'rmse label' : r'RMSE Wind Speed (m s$\mathregular{^{-1}}$)',
              'save prefix': 'WIND80m',
              'mean maxmin': [3, -3],
              'rmse max'   : 5, 
              'mean cmap'  : 'PiYG',              
              'WIND'       : True},
           6:{'var'        : 'HGT:500 mb',
              'name'       : '500 hPa Height',
              'mean label' : r'$\Delta$ 500 hPa Height (m)',
              'rmse label' : r'RMSE 500 hPa Height (m)',
              'save prefix': 'HGT500mb',
              'mean maxmin': [2, -2],
              'rmse max'   : 5, 
              'mean cmap'  : 'RdGy',              
              'WIND'       : True},
          }

# Choose your option
option = 5

o = options[option]
var = o['var']
var_str = var.replace(':', '_').replace(' ', '_')
SAVEDIR = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/PhD/HRRR/RMSE_mean/%s/' % o['save prefix']

if o['WIND'] is True:
    level = o['var'].split(':')[1]

# Calculate Mean Error and Root Mean Square Error
for f in range(1, 19):
    for h in range(0, 24):

        # Date Range
        hour = h
        sDATE = datetime(2017, 9, 1, hour)
        eDATE = datetime(2017, 12, 1, hour)
        days = (eDATE-sDATE).days
        date_list = np.array([sDATE + timedelta(days=x) for x in range(0, days)])

        # Multiprocessing :) will return the difference (fxx-anlys)
        fxx = f
        num_proc = multiprocessing.cpu_count() # use all processors
        p = multiprocessing.Pool(num_proc)
        if o['WIND'] is True:
            result = p.map(HRRR_error_wind_speed, date_list)
        else:
            result = p.map(HRRR_error, date_list)
        p.close()

        # Remove anny nan arrays
        samples_requested = len(result)
        result = np.array([i for i in result if not np.isnan(np.sum(i))])
        samples = len(result)

        # Calculate error statistics
        RMSE = np.sqrt(np.nanmean(result**2, axis=0))
        mean_error = np.nanmean(result, axis=0)

        # Create Figure
        plt.sca(ax1)
        plot_error = m.pcolormesh(H['lon'], H['lat'], mean_error, 
                                  latlon=True, cmap=o['mean cmap'],
                                  vmax=o['mean maxmin'][0], vmin=o['mean maxmin'][1])
        if f == 1 and h == 0:
            # Add colorbar
            ax1.set_title('Mean Error')
            cb = plt.colorbar(orientation='horizontal', pad=0.01, shrink=0.95)
            cb.set_label(o['mean label'])


        plt.sca(ax2)
        plot_rmse = m.pcolormesh(H['lon'], H['lat'], RMSE, 
                                 latlon=True, cmap='BuPu',
                                 vmax=o['rmse max'], vmin=0)
        if f == 1 and h == 0:
            # Add colorbar
            ax2.set_title('RMSE')
            cb = plt.colorbar(orientation='horizontal', pad=0.01, shrink=0.95)
            cb.set_label(o['rmse label'])


        plt.suptitle( \
'HRRR %s f%02d\n\
%s - %s %02d:00 UTC\n\
(%s/%s Samples Requested)' % (o['name'], fxx, sDATE.strftime('%Y %b %d'), eDATE.strftime('%Y %b %d'), hour, samples, samples_requested ), fontsize=20)

        plt.tight_layout()

        plt.savefig(SAVEDIR+'%s_%s-%s_h%02d_f%02d' %(o['save prefix'], sDATE.strftime('%Y%m%d'), eDATE.strftime('%Y%m%d'), hour, fxx))
        print "Saved %s, h%02d, f%02d" % (o['save prefix'], hour, fxx)

        plot_error.remove()
        plot_rmse.remove()
