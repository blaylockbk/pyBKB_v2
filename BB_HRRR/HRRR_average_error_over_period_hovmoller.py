# Brian Blaylock
# October 11, 2017          # I get married to my best friend next week :)

"""
Calculate the mean error for a time period.
Specify the forecast hour, date range, and variable (special case for wind).
"""

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from datetime import datetime, timedelta
import time
import numpy as np
import multiprocessing

#Import my custom functions: https://github.com/blaylockbk/pyBKB_v2
import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2/')
from BB_downloads.HRRR_S3 import get_hrrr_variable
from BB_basemap.draw_maps import draw_CONUS_HRRR_map
from BB_wx_calcs.wind import wind_uv_to_spd
from BB_data.grid_manager import pluck_point_new

import matplotlib as mpl
mpl.rcParams['figure.figsize'] = [15, 6]
mpl.rcParams['figure.titlesize'] = 15
mpl.rcParams['figure.titleweight'] = 'bold'
mpl.rcParams['xtick.labelsize'] = 10
mpl.rcParams['ytick.labelsize'] = 10
mpl.rcParams['axes.labelsize'] = 10
mpl.rcParams['axes.titlesize'] = 12
mpl.rcParams['lines.linewidth'] = 1.8
mpl.rcParams['grid.linewidth'] = .25
mpl.rcParams['figure.subplot.wspace'] = 0.05
mpl.rcParams['figure.subplot.hspace'] = 0.01
mpl.rcParams['legend.fontsize'] = 8
mpl.rcParams['legend.framealpha'] = .75
mpl.rcParams['legend.loc'] = 'best'
mpl.rcParams['savefig.bbox'] = 'tight'
mpl.rcParams['savefig.dpi'] = 100
mpl.rcParams['savefig.transparent'] = False

# 1) Locations (dictionary)
daylight = time.daylight # If daylight is on (1) then subtract from timezone.
locations = {'Oaks': {'latitude':40.084,
                      'longitude':-111.598,
                      'name':'Spanish Oaks Golf Course',
                      'timezone': 7-daylight,        # Timezone offset from UTC
                      'is MesoWest': False},         # Is the Key a MesoWest ID?
             'UKBKB': {'latitude':40.09867,
                       'longitude':-111.62767,
                       'name':'Spanish Fork Bench',
                       'timezone': 7-daylight,
                       'is MesoWest': True},
             'KSLC':{'latitude':40.77069,
                     'longitude':-111.96503,
                     'name':'Salt Lake International Airport',
                     'timezone': 7-daylight,
                     'is MesoWest': True},
             'WBB':{'latitude':40.76623,
                    'longitude':-111.84755,
                    'name':'William Browning Building',
                    'timezone': 7-daylight,
                    'is MesoWest': True},
             'FREUT':{'latitude':41.15461,
                      'longitude':-112.32998,
                      'name':'Fremont Island - Miller Hill',
                      'timezone': 7-daylight,
                      'is MesoWest': True},
             'GNI':{'latitude':41.33216,
                    'longitude':-112.85432,
                    'name':'Gunnison Island',
                    'timezone': 7-daylight,
                    'is MesoWest': True},
             'NAA':{'latitude':40.71152,
                    'longitude':-112.01448,
                    'name':'Neil Armstrong Academy',
                    'timezone': 7-daylight,
                    'is MesoWest': True},
             'UtahLake':{'latitude':40.159,
                         'longitude':-111.778,
                         'name':'Utah Lake',
                         'timezone': 7-daylight,
                         'is MesoWest': False},
             'UTPKL':{'latitude':40.98985,
                      'longitude':-111.90130,
                      'name':'Lagoon (UTPKL)',
                      'timezone': 7-daylight,
                      'is MesoWest': True},
             'Orderville':{'latitude':37.276,
                           'longitude':-112.638,
                           'name':'Orderville',
                           'timezone': 7-daylight,
                           'is MesoWest': False},
             'BFLAT':{'latitude':40.784,
                      'longitude':-113.829,
                      'name':'Bonneville Salt Flats',
                      'timezone': 7-daylight,
                      'is MesoWest': True},
             'UFD09':{'latitude':40.925,
                      'longitude':-112.159,
                      'name':'Antelope Island',
                      'timezone': 7-daylight,
                      'is MesoWest': True},
             'C8635':{'latitude':41.11112,
                      'longitude':-111.96229,
                      'name':'Hill Air Force Base (CW8635)',
                      'timezone': 7-daylight,
                      'is MesoWest': True},
             'FPS':{'latitude':40.45689,
                    'longitude':-111.90483,
                    'name':'Flight Park South',
                    'timezone': 7-daylight,
                    'is MesoWest': True},
             'EYSC':{'latitude':40.24715,
                     'longitude':-111.65001,
                     'name':'Brigham Young University',
                     'timezone': 7-daylight,
                     'is MesoWest': True},
             'UCC23':{'latitude':41.7665,
                      'longitude':-111.8105,
                      'name':'North Logan',
                      'timezone': 7-daylight,
                      'is MesoWest': True},
             'KIDA':{'latitude':43.52083,
                     'longitude':-112.06611,
                     'name':'Idaho Falls',
                     'timezone': 7-daylight,
                     'is MesoWest': True}
            }

for i in locations.keys():
    locations[i]['mean error'] = np.zeros([18, 24])
    locations[i]['RMSE'] = np.zeros([18, 24])

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

# need a set of lat/lon grid variables, so just grab with this...
H = get_hrrr_variable(datetime(2017, 10, 1), 'TMP:2 m')


options = {1:{'var'        : 'TMP:2 m',
              'name'       : '2 m Temperature',
              'mean label' : r'$\Delta$ Temperature (C)',
              'rmse label' : 'RMSE Temperature (C)',
              'save prefix': 'TMP2m',
              'mean maxmin': [3, -3],
              'rmse max'   : 5, 
              'WIND'       : False},

           2:{'var'        : 'UGRD:10 m',
              'name'       : '10 m Wind Speed',
              'mean label' : r'$\Delta$ Wind Speed (m s$\mathregular{^{-1}}$)',
              'rmse label' : r'RMSE Wind Speed (m s$\mathregular{^{-1}}$)',
              'save prefix': 'WIND10m',
              'mean maxmin': [3, -3],
              'rmse max'   : 5, 
              'WIND'       : True},

           3:{'var'        : 'REFC:entire',         # Consider there are some negative values in the data range -10 to 0
              'name'       : 'Composite Reflectivity',
              'mean label' : r'$\Delta$ Reflectivity (dBZ)',
              'rmse label' : 'RMSE Reflectivity (dBZ)',
              'save prefix': 'REFC',
              'mean maxmin': [20, -20],
              'rmse max'   : 40, 
              'WIND'       : False},
          }

# Choose your option
option = 3

o = options[option]
var = o['var']
var_str = var.replace(':', '_').replace(' ', '_')
SAVEDIR = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/PhD/HRRR/RMSE_mean_Hovmoller/%s/' % o['save prefix']

if o['WIND'] is True:
    level = o['var'].split(':')[1]

# Calculate Mean Error and Root Mean Square Error
for f in range(1, 19):
    for h in range(0, 24):

        # Date Range
        hour = h
        sDATE = datetime(2017, 8, 10, hour)
        eDATE = datetime(2017, 10, 10, hour)
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

        for f in range(1,19):
            for h in range(24):
                for i in locations.keys():
                    # Pluck point
                    x, y = pluck_point_new(locations[i]['latitude'], locations[i]['longitude'], H['lat'], H['lon'])
                    locations[i]['mean error'][f-1, h] = mean_error[x[0], y[0]]
                    locations[i]['RMSE'][f-1, h] = RMSE[x[0], y[0]]

for i in locations.keys():
    fig, [ax1, ax2] = plt.subplots(nrows=1, ncols=2)
    plt.sca(ax1)
    plt.pcolormesh(locations[i]['mean error'])
    plt.title('Mean Error')
    
    plt.sca(ax2)
    plt.pcolormesh(locations[i]['RMSE'])
    plt.title('RMSE')

    plt.show()