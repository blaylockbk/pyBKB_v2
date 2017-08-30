# Brian Blaylock
# July 31, 2017                     My parents got rid of their land line phone

"""
Plot a time series of statistics at a point from the OSG statistics grids
"""

import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
from BB_MesoWest.MesoWest_STNinfo import get_station_info
from BB_data.grid_manager import pluck_point_new

# =============================================================================
#  Parameters to change
# =============================================================================
stns = ['WBB', 'KSLC', 'KCGS', 'KTOP']

variable = 'TMP:2 m'
variable = 'WIND:10 m'
variable = 'REFC:entire'
fxx = 0
# =============================================================================

var = variable.replace(':', '_').replace(' ', '_')

# MesoWest Station Info
a = get_station_info(stns)

STN = {}

# Build arrays to store the data
for S in stns:
    STN[S] = {'count':np.array([]),
              'cores':np.array([]),
              'month':np.array([]),
              'hour':np.array([]),
              'monthhour':np.array([]),
              'MAX':np.array([]),
              'MIN':np.array([]),
              'MEAN':np.array([]),
              'p01':np.array([]),
              'p05':np.array([]),
              'p10':np.array([]),
              'p90':np.array([]),
              'p95':np.array([]),
              'p99':np.array([]),
              'timer':np.array([])}

for i in range(len(stns)):
    STN[a['STNID'][i]]['LAT'] = a['LAT'][i]
    STN[a['STNID'][i]]['LON'] = a['LON'][i]
    STN[a['STNID'][i]]['NAME'] = a['NAME'][i]


for m in range(1, 13):
    for h in range(0, 24):
        FILE = 'OSG_HRRR_%s_m%02d_h%02d_f%02d.nc' % (var, m, h, fxx)
        print FILE
        nc = Dataset(FILE, 'r')
        #
        for S in STN.keys():
            # Pluck value from each location
            point = pluck_point_new(STN[S]['LAT'], STN[S]['LON'], nc.variables['latitude'][:], nc.variables['longitude'][:])
            #
            # append the data to the list
            STN[S]['count'] = np.append(STN[S]['count'], nc.variables['count'][0])
            STN[S]['cores'] = np.append(STN[S]['cores'], nc.variables['cores'][0])
            STN[S]['month'] = np.append(STN[S]['month'], m)
            STN[S]['hour'] = np.append(STN[S]['hour'], h)
            STN[S]['monthhour'] = np.append(STN[S]['monthhour'], m+h/24.)
            STN[S]['MAX'] = np.append(STN[S]['MAX'], nc.variables['max_'+var][point[0], point[1]])
            STN[S]['MIN'] = np.append(STN[S]['MIN'], nc.variables['min_'+var][point[0], point[1]])
            STN[S]['MEAN'] = np.append(STN[S]['MEAN'], nc.variables['mean_'+var][point[0], point[1]])
            STN[S]['p01'] = np.append(STN[S]['p01'], nc.variables['percentile'][0][point[0], point[1]])
            STN[S]['p05'] = np.append(STN[S]['p05'], nc.variables['percentile'][1][point[0], point[1]])
            STN[S]['p10'] = np.append(STN[S]['p10'], nc.variables['percentile'][2][point[0], point[1]])
            STN[S]['p90'] = np.append(STN[S]['p90'], nc.variables['percentile'][3][point[0], point[1]])
            STN[S]['p95'] = np.append(STN[S]['p95'], nc.variables['percentile'][4][point[0], point[1]])
            STN[S]['p99'] = np.append(STN[S]['p99'], nc.variables['percentile'][5][point[0], point[1]])
            STN[S]['timer'] = np.append(STN[S]['timer'], ''.join(nc.variables['timer'][:]))


# Adjust units
for S in STN.keys():
    if variable == 'TMP:2 m':
        STN[S]['MAX'] = STN[S]['MAX'] - 273.15
        STN[S]['MIN'] = STN[S]['MIN'] - 273.15
        STN[S]['MEAN'] = STN[S]['MEAN'] - 273.15
        STN[S]['p01'] = STN[S]['p01'] - 273.15
        STN[S]['p05'] = STN[S]['p05'] - 273.15
        STN[S]['p10'] = STN[S]['p10'] - 273.15
        STN[S]['p90'] = STN[S]['p90'] - 273.15
        STN[S]['p95'] = STN[S]['p95'] - 273.15
        STN[S]['p99'] = STN[S]['p99'] - 273.15
        ylabel = 'Temperature (C)'

    elif variable == 'WIND:10 m':
        ylabel = r'Wind Speed (ms$\mathregular{^{-1}}$)'

    elif variable == 'REFC:entire':
        ylabel = 'Simulated Composite Reflectivity (dBZ)'

#------------------------------------------------------------------------------
# Create Plots
#------------------------------------------------------------------------------
for S in STN.keys():
    plt.figure(1, figsize=[12, 6])
    plt.clf(); plt.cla()
    for i in range(len(STN[S]['monthhour']))[::24]:
        if i == 0:
            plt.plot(STN[S]['monthhour'][i:i+23], STN[S]['MAX'][i:i+23], c='r', label="max")
            plt.plot(STN[S]['monthhour'][i:i+23], STN[S]['MEAN'][i:i+23], c='g', label="mean")
            plt.plot(STN[S]['monthhour'][i:i+23], STN[S]['MIN'][i:i+23], c='b', label="min")
        else:
            plt.plot(STN[S]['monthhour'][i:i+23], STN[S]['MAX'][i:i+23], c='r')
            plt.plot(STN[S]['monthhour'][i:i+23], STN[S]['MEAN'][i:i+23], c='g')
            plt.plot(STN[S]['monthhour'][i:i+23], STN[S]['MIN'][i:i+23], c='b')

    plt.legend()
    plt.grid()
    plt.xlim(1,13)
    plt.xticks(range(1,13))
    plt.title('%s %s' % (variable, S))
    plt.xlabel('Hourly Statistics by Month')
    plt.ylabel(ylabel)
    plt.savefig('%s_%s_MMM.png' % (S, var), bbox_inches='tight')

    plt.figure(2, figsize=[12, 6])
    plt.clf(); plt.cla()
    for i in range(len(STN[S]['monthhour']))[::24]:
        if i == 0:
            plt.plot(STN[S]['monthhour'][i:i+23], STN[S]['p99'][i:i+23], c='firebrick', label='p99')
            plt.plot(STN[S]['monthhour'][i:i+23], STN[S]['p95'][i:i+23], c='orange', label='p95')
            plt.plot(STN[S]['monthhour'][i:i+23], STN[S]['p90'][i:i+23], c='yellow', label='p90')
            plt.plot(STN[S]['monthhour'][i:i+23], STN[S]['p10'][i:i+23], c='orchid', label='p10')
            plt.plot(STN[S]['monthhour'][i:i+23], STN[S]['p05'][i:i+23], c='turquoise', label='p05')
            plt.plot(STN[S]['monthhour'][i:i+23], STN[S]['p01'][i:i+23], c='dodgerblue', label='p01')
        else:
            plt.plot(STN[S]['monthhour'][i:i+23], STN[S]['p99'][i:i+23], c='firebrick')
            plt.plot(STN[S]['monthhour'][i:i+23], STN[S]['p95'][i:i+23], c='orange')
            plt.plot(STN[S]['monthhour'][i:i+23], STN[S]['p90'][i:i+23], c='yellow')
            plt.plot(STN[S]['monthhour'][i:i+23], STN[S]['p10'][i:i+23], c='orchid')
            plt.plot(STN[S]['monthhour'][i:i+23], STN[S]['p05'][i:i+23], c='turquoise')
            plt.plot(STN[S]['monthhour'][i:i+23], STN[S]['p01'][i:i+23], c='dodgerblue')

    plt.legend()
    plt.grid()
    plt.xlim(1,13)
    plt.xticks(range(1,13))
    plt.title('%s %s' % (variable, S))
    plt.xlabel('Hourly Statistics by Month')
    plt.ylabel(ylabel)
    plt.savefig('%s_%s_percentiles.png' % (S, var), bbox_inches='tight')
