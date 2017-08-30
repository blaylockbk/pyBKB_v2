# Brian Blaylock
# August 25, 2017                            Rachel is flying to Europe

"""
Plot values from the OSG calculated HRRR statistics
Daily 30 is the 30-day average data
"""

import h5py
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import multiprocessing

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
sys.path.append('B:\pyBKB_v2')

from BB_downloads.HRRR_S3 import *
from BB_basemap.draw_maps import draw_CONUS_HRRR_map
from BB_MesoWest.MesoWest_STNinfo import get_station_info
from BB_data.grid_manager import pluck_point_new

m = draw_CONUS_HRRR_map()

# Get lat/lon grid from file for plotting
DIR = '/uufs/chpc.utah.edu/common/home/horel-group2/blaylock/HRRR_OSG/daily30_20150418-20170801/'
latlon_file = h5py.File(DIR+'OSG_HRRR_latlon.h5', 'r')
lat = latlon_file['latitude'].value
lon = latlon_file['longitude'].value
x, y = m(lon, lat)

def plot_OSG_map(args):
    month, day, hour, fxx, statistic, var = args

    variable = var.replace(":", '_').replace(' ', '_')

    # open a file
    DIR = '/uufs/chpc.utah.edu/common/home/horel-group2/blaylock/HRRR_OSG/daily30_20150418-20170801/%s/' % (variable)
    FILE = 'OSG_HRRR_%s_m%02d_d%02d_h%02d_f%02d.h5' % (variable, month, day, hour, fxx)
    print FILE
    
    if os.path.exists(DIR+FILE):
        h = h5py.File(DIR+FILE, 'r')
    else:
        return None

    cores = h['cores'].value
    count = h['count'].value

    sDATE = h['Beginning Date'].value
    eDATE = h['Ending Date'].value
    timer = h['timer'].value
    
    # A list of the available percentiles in the 'percentile value' key
    percentiles = h['percentile'].value

    # Build a dictionary of the statistic values
    STAT = {'mean' : h['mean'].value}
    for p in range(len(percentiles)):
        STAT['p'+str(percentiles[p])] = h['percentile value'][p]
    
    m.drawstates()
    m.drawcoastlines()
    m.drawcountries()
    if var == 'TMP:2 m':
        m.pcolormesh(x, y, STAT[statistic]-273.15, vmin=-8, vmax=38, cmap='Spectral_r')
        cb = plt.colorbar(orientation='horizontal', shrink=.9, pad=.05, extend="both")
        cb.set_label('2 m Temperature (C)')
    if var == 'DPT:2 m':
        m.pcolormesh(x, y, STAT[statistic]-273.15, vmin=-10, vmax=25, cmap='BrBG')
        cb = plt.colorbar(orientation='horizontal', shrink=.9, pad=.05, extend="both")
        cb.set_label('2 m Dew Point (C)')
    elif var == 'WIND:10 m':
        m.pcolormesh(x, y, STAT[statistic], vmin=0, vmax=20, cmap='plasma_r')
        cb = plt.colorbar(orientation='horizontal', shrink=.9, pad=.05, extend="both")
        cb.set_label(r'10 m Wind Speed (ms$\mathregular{^{-1}}$)')
    elif var == 'REFC:entire':
        # Mask out empty reflectivity values
        dBZ = STAT[statistic]
        dBZ = np.ma.array(dBZ)
        dBZ[dBZ == -10] = np.ma.masked
        m.pcolormesh(x, y, dBZ, vmax=0, vmin=80, cmap='gist_ncar')
        cb = plt.colorbar(orientation='horizontal', shrink=.9, pad=.05)
        cb.set_label(r'Simulated Composite Reflectivity (dBZ)')
    
    months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC',]
    plt.title('HRRR Composite: %s \n %s-%02d Hour:%02d, fxx:%02d +/- 15 Days\nFirst: %s, Last:%s\nCount:%02d, Cores:%02d\nOSG Timer: %s' % (statistic, months[month-1], day, hour, fxx, sDATE, eDATE, count, cores, timer))

    SAVEDIR = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/PhD/HRRR/OSG/daily30/%s_%s/' % (variable, statistic)
    if not os.path.exists(SAVEDIR):
        os.makedirs(SAVEDIR)
    plt.savefig(SAVEDIR+'OSG_%s_%s_m%02d_d%02d_h%02d_f%02d.png' % (statistic, variable, month, day, hour, fxx), bbox_inches='tight', dpi=100)
    plt.close()
    h.close()


def get_OSG_point_timeseries(inputs):
    month, day, hour, fxx, statistic, var, stn, point = inputs
    print inputs
    variable = var.replace(":", '_').replace(' ', '_')

    # open a file
    DIR = '/uufs/chpc.utah.edu/common/home/horel-group2/blaylock/HRRR_OSG/daily30_20150418-20170801/%s/' % (variable)
    FILE = 'OSG_HRRR_%s_m%02d_d%02d_h%02d_f%02d.h5' % (variable, month, day, hour, fxx)

    try:
        if os.path.exists(DIR+FILE):
            h = h5py.File(DIR+FILE, 'r')
        else:
            print "no file:", FILE
            return np.nan

        if statistic == 'mean':
            return h['mean'][point[0][0], point[1][0]]
        else:
            percentiles = h['percentile'].value
            p = np.where(int(statistic[1:])==percentiles)[0][0]

            return_this = h['percentile value'][p][point[0][0], point[1][0]]
            if return_this > 315:
                print 'greater than 315', return_this, month, day, hour, fxx, statistic, var
            return return_this
    except:
        print "ERRORS:", FILE

"""
from datetime import datetime
timer = datetime.now()
variable = 'TMP_2_m'
fxx = 0
DIR = '/uufs/chpc.utah.edu/common/home/horel-group2/blaylock/HRRR_OSG/daily30_20150418-20170801/%s/' % (variable)
months = range(1,13)
days = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
hours = range(24)
h = [h5py.File(DIR+'OSG_HRRR_%s_m%02d_d%02d_h%02d_f%02d.h5' % (variable, month, day, hour, fxx),'r')['mean'][10][10] for month in months for day in range(1,days[month-1]+1) for hour in hours]
print "TIMER:", datetime.now()-timer
"""

if __name__ == '__main__':

    fxx = 0

    #   mean, p0, p1, p2, p3, p4, p5, p10, p15, p25, p33, p50,
    #   p66, p75, p90, p95, p96, p97, p98, p99, p100
    statistic = 'p90'
    
    var = 'DPT:2 m'
    #var = 'REFC:entire'
    var = 'TMP:2 m'


    months = range(1,13)
    days = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    hours = range(24)

    # Plot maps
    if False:
        # Create a list to iterate over. 
        # statistic options:
        
        
        args = [[month, day, hour, fxx, statistic, var] for month in months for day in range(1,days[month-1]+1) for hour in hours]

        # Multiprocessing :)
        num_proc = multiprocessing.cpu_count() # use all processors
        p = multiprocessing.Pool(num_proc)
        result = p.map(plot_OSG_map, args)
        p.close()

    # Plot timeseries
    if True:
        # MesoWest Station Info
        stn = ['WBB']
        a = get_station_info(stn)

        # Pluck point
        point = pluck_point_new(a['LAT'][0], a['LON'][0], lat, lon)


        args = [[month, day, hour, fxx, statistic, var, stn[0], point] for month in months for day in range(1,days[month-1]+1) for hour in hours]

        # Multiprocessing :)
        timer = datetime.now()
        num = multiprocessing.cpu_count()
        p = multiprocessing.Pool(num)
        result = p.map(get_OSG_point_timeseries, args)
        print 'Timer Series TIMER:', datetime.now()-timer
        p.close()
        result = np.array(result)

        plt.title('%s +/- 15 Days HRRR Composite: %s %s' % (stn[0], var, statistic))
        plt.xlabel('Month and Hour')
        if var == 'TMP:2 m':
            plt.plot(result-273.15)
            plt.ylabel('2 m Temperature (C)')

        SAVEDIR = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/PhD/HRRR/OSG/daily30/'
        plt.savefig(SAVEDIR + stn[0]+'_'+var.replace(":", '_').replace(' ', "_")+'_'+statistic+'.png')

