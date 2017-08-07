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
from BB_data.grid_manager import pluck_point_new



def get_OSG_stats(locs, variable, stats, months=range(1,13), hours=range(0,24), extra=True, fxx=0):
    """
    Returns a dictionary of values plucked from the OSG HRRR statistics files.

    Input:
        locs - a dictionary with the latitude and longitude of each location
               e.g. {'NAME':{'latitude':40, 'longitude':-111}}
        variable - the HRRR variable name (e.g. 'TMP:2 m' or 'WIND:10 m')
        stats - a list of the requested statistics. May include:
               ['MAX', 'MIN', 'MEAN', 'P01', 'P05', 'P10', 'P90', 'P95', 'P99']
               (the more you ask for, the longer it takes)
        months - a list of months
        hours - a list of hours
        extra - returns other data if True, 
                count: sample size of statistics
                cores: number of cores used by the OSG node to compute the statistics
                timer: length of time to create the file on the OSG
        fxx - the forecast hour. So far only fxx is available
    """
    
    # The variable with underscores replacing the special characters in the 
    # HRRR variable name
    var = variable.replace(':', '_').replace(' ', '_')

    # Define an offset for temperature
    if variable == 'TMP:2 m' or variable == 'DPT:2 m':
        offset = 273.15
    else:
        offset = 0

    # Open the first file, so we can pluck the points and store the position
    A = '/uufs/chpc.utah.edu/common/home/horel-group/archive/'
    B = 'HRRR/OSG_hourbymonth_stats_20150418-2017731/'
    C = '%s/' % var

    DIR = A+B+C
    FILE = 'OSG_HRRR_%s_m%02d_h%02d_f%02d.nc' % (var, 1, 0, fxx)

    # Handle for every netCDF file we want: 
    # Starting with all hours for first month first, then all hours the second month, etc.
    a = [Dataset(DIR+'OSG_HRRR_%s_m%02d_h%02d_f%02d.nc' % (var, i, j, fxx), 'r') for i in months for j in hours]
    print 'Got the file handles'

    # Initalize the return dictionary
    return_this = {'month':np.array([i for i in months for j in hours]),
                   'hour':np.array([j for i in months for j in hours]),
                   'monthhour':np.array([i+j/24. for i in months for j in hours])}

    # Store the requested values in the return dictionary
    if extra==True:
        return_this['count'] = np.array([i.variables['count'][0] for i in a])
        return_this['cores'] = np.array([i.variables['cores'][0] for i in a])
        return_this['timer'] = np.array([''.join(i.variables['timer'][:]) for i in a])
        print 'Got the count, cores, and timer'

    # Get the pluck indexes for each requested location
    Hlat = a[0].variables['latitude'][:]  # HRRR latitude grid
    Hlon = a[0].variables['longitude'][:] # HRRR longitude grid
    for L in locs:
        print 'working on L...',
        Slat = locs[L]['latitude']            # Station latitude point
        Slon = locs[L]['longitude']           # Statin longitude point   
        x, y = pluck_point_new(Slat, Slon, Hlat, Hlon)
        print 'got the plucked points...',

        return_this[L] = {'stn_latlon':[Slat, Slon],
                          'hrrr_latlon':[Hlat[x[0],y[0]], Hlon[x[0],y[0]]]}
        if 'MAX' in stats:
            return_this[L]['MAX'] = np.array([i.variables['max_'+var][x[0],y[0]]-offset for i in a])
            print 'got the max...',
        if 'MIN' in stats:
            return_this[L]['MIN'] = np.array([i.variables['min_'+var][x[0],y[0]]-offset for i in a])
            print 'got the min...',
        if 'MEAN' in stats:
            return_this[L]['MEAN'] = np.array([i.variables['mean_'+var][x[0],y[0]]-offset for i in a])
            print 'got the mean...',
        if 'P01' in stats:
            return_this[L]['P01'] = np.array([i.variables['percentile'][0][x[0],y[0]]-offset for i in a])
            print 'got the P01...',
        if 'P05' in stats:
            return_this[L]['P05'] = np.array([i.variables['percentile'][1][x[0],y[0]]-offset for i in a])
            print 'got the P05...',
        if 'P10' in stats:
            return_this[L]['P10'] = np.array([i.variables['percentile'][2][x[0],y[0]]-offset for i in a])
            print 'got the P10...',
        if 'P90' in stats:
            return_this[L]['P90'] = np.array([i.variables['percentile'][3][x[0],y[0]]-offset for i in a])
            print 'got the P90...',
        if 'P95' in stats:
            return_this[L]['P95'] = np.array([i.variables['percentile'][4][x[0],y[0]]-offset for i in a])
            print 'got the P95...',
        if 'P99' in stats:
            return_this[L]['P99'] = np.array([i.variables['percentile'][5][x[0],y[0]]-offset for i in a])    
            print 'got the P99...',

    # Close the NetCDF files
    for close in a:
        close.close()
    print 'done!'

    return return_this

def plot_corescount_vs_time():
    locs = {'KSLC' :{'latitude':40.77069, 'longitude':-111.96503}}
    variable = 'TMP:2 m'
    var = variable.replace(':', '_').replace(' ', '_')
    stats = []
    SS = get_OSG_stats(locs, variable, stats, months=range(1,13), hours=range(0,24), extra=True, fxx=0)

    # Plot scatter graph showing time to compute versus number of cores
    minutes = np.array([int(T.split(':')[1]) for T in SS['timer']])
    seconds = np.array([float(T.split(':')[2]) for T in SS['timer']])
    total_seconds = (minutes*60)+seconds
    plt.figure(1)
    plt.scatter(SS['cores'], total_seconds)
    plt.title(var)
    plt.xlabel('Number of cores')
    plt.ylabel('Seconds')
    plt.xticks(np.unique(SS['cores']))
    plt.ylim([0,np.max(total_seconds)+25])
    plt.savefig(var+'cores_vs_seconds.png', bbox_inches='tight')

    # Plot scatter graph showing time to compute versus sample size
    plt.figure(2)
    plt.scatter(SS['count'], total_seconds)
    plt.title(var)
    plt.xlabel('Number of samples')
    plt.ylabel('Seconds')
    plt.ylim([0,np.max(total_seconds)+25])
    plt.savefig(var+'count_vs_seconds.png', bbox_inches='tight')

    # Plot scatter graph showing number of samples for each file
    plt.figure(3)
    plt.scatter(SS['monthhour'], SS['count'])
    plt.title(var)
    plt.xlabel('Month, with values for each hour')
    plt.ylabel('Count')
    plt.xlim([1,13])
    plt.savefig(var+'count_vs_month.png', bbxo_inches='tight')

if __name__ == '__main__':
    locs = {'KSLC' :{'latitude':40.77069, 'longitude':-111.96503},
            'WBB'  :{'latitude':40.76623, 'longitude':-111.84755},
            'TT047':{'latitude':37.735778, 'longitude':-112.702306}}
    variable = 'TMP:2 m'
    #variable = 'WIND:10 m'
    var = variable.replace(':', '_').replace(' ', '_')
    
    
    stats = ['MAX']
    SS = get_OSG_stats(locs, variable, stats, months=range(1,13), hours=range(0,24), extra=True, fxx=0)

    
    for S in stats:
        plt.figure(1, figsize=[12, 6])
        for i in range(0, 288, 24):
            if i == 0:
                plt.plot(SS['monthhour'][i:i+24], SS['KSLC'][S][i:i+24], label='KSLC', c='b')
                plt.plot(SS['monthhour'][i:i+24], SS['WBB'][S][i:i+24], label='WBB', c='r')
                plt.plot(SS['monthhour'][i:i+24], SS['TT047'][S][i:i+24], label='TT047', c='k')
            else:
                plt.plot(SS['monthhour'][i:i+24], SS['KSLC'][S][i:i+24], c='b')
                plt.plot(SS['monthhour'][i:i+24], SS['WBB'][S][i:i+24], c='r')
                plt.plot(SS['monthhour'][i:i+24], SS['TT047'][S][i:i+24], c='k')
        plt.title('%s %s' % (S, var))
        plt.xlabel('Month, with values for each hour')
        if variable == 'TMP:2 m':
            plt.ylabel('Temperature (C)')
        elif variable == 'WIND:10 m':
            plt.ylabel(r'Wind Speed (ms$\mathregular{^{-1}}$)')
        plt.grid()
        plt.xticks(range(1,13))
        plt.legend()
        plt.xlim([1,13])
        plt.savefig(S+'_'+var+'_hourbymonth.png', bbox_inches='tight')

