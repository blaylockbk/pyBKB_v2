# Brian Blaylock
# August 25, 2017                            Rachel is flying to Europe

"""
Plot values from the OSG calculated HRRR statistics
Daily 30 is the 30-day average data
"""

import h5py
import numpy
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.dates import DateFormatter
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
        STAT['p'+str(percentiles[p])] = h[statistic]
    
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

def get_point(FILE, STAT, ROW, COL):
    """
    Funciton for List Comphensions:
    Return the value from a point in the HDF5 file array
    """
    with h5py.File(FILE, 'r') as f:
        return f[STAT][ROW][COL]

def get_point_MP(inputs):
    """
    Function for MultiProcessing:
    Return the value from a point in the HDF5 file array
    """
    FILE, STAT, ROW, COL = inputs
    with h5py.File(FILE, 'r') as f:
        return f[STAT][ROW][COL]

def get_field_MP(inputs):
    """
    Function for MultiProcessing:
    Return the value from a key in the HDF5 file array
    """
    FILE, STAT = inputs
    with h5py.File(FILE, 'r') as f:
        return f[STAT].value


if __name__ == '__main__':

    fxx = 0
    
    #   mean, p0, p1, p2, p3, p4, p5, p10, p15, p25, p33, p50,
    #   p66, p75, p90, p95, p96, p97, p98, p99, p100
    statistic = 'p95'
    
    #var = 'DPT:2 m'
    #var = 'REFC:entire'
    #var = 'TMP:2 m'
    var = 'WIND:10 m'
    
    variable = var.replace(':', '_').replace(' ', '_')

    DIR = '/uufs/chpc.utah.edu/common/home/horel-group2/blaylock/HRRR_OSG/daily30_20150418-20170801/%s/' % (variable)

    months = range(1,13)
    days = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    hours = range(24)

    # Dates (with leap year)
    HOURS = 366*24
    DATES = np.array([datetime(2016, 1, 1) + timedelta(hours = h) for h in range(HOURS)])


    # Plot maps
    if True:
        # Create a list to iterate over. 
        # statistic options:
        
        
        args = [[month, day, hour, fxx, statistic, var] for month in months for day in range(1,days[month-1]+1) for hour in hours]

        # Multiprocessing :)
        num_proc = multiprocessing.cpu_count() # use all processors
        p = multiprocessing.Pool(num_proc)
        result = p.map(plot_OSG_map, args)
        p.close()

    # Plot timeseries: HTS is the HRRR-statistic Time Series
    if False:
        
        
        '''
        # List Comprehension
        ROW = 10
        COL = 10
        timer = datetime.now()
        HTS = np.array([get_point(DIR+'OSG_HRRR_%s_m%02d_d%02d_h%02d_f00.h5' % \
                    (variable, month, day, hour), 'mean', ROW, COL) \
                    for month in months \
                    for day in range(1,days[month-1]+1) \
                    for hour in hours])
        print datetime.now()-timer
        '''
        # MesoWest Station Info
        stn = ['WBB']
        a = get_station_info(stn)

        # Pluck point
        point = pluck_point_new(a['LAT'][0], a['LON'][0], lat, lon)
        

        # Multiprocessing :)
        args_p90 = [[DIR+'OSG_HRRR_%s_m%02d_d%02d_h%02d_f00.h5' % \
                (variable, month, day, hour), 'p90', point[0][0], point[1][0]] \
                for month in months for day in range(1,days[month-1]+1) for hour in hours]
        num_proc = multiprocessing.cpu_count()
        p = multiprocessing.Pool(num_proc)
        HTS_p90 = p.map(get_point_MP, args_p90)
        p.close()

        # Multiprocessing :)
        args_p10 = [[DIR+'OSG_HRRR_%s_m%02d_d%02d_h%02d_f00.h5' % \
                (variable, month, day, hour), 'p10', point[0][0], point[1][0]] \
                for month in months for day in range(1,days[month-1]+1) for hour in hours]
        num_proc = multiprocessing.cpu_count()
        p = multiprocessing.Pool(num_proc)
        HTS_p10 = p.map(get_point_MP, args_p10)
        p.close()

        # Convert to numpy array so we can perform math on it
        HTS_p90 = np.array(HTS_p90)
        HTS_p10 = np.array(HTS_p10)


        # Create a figure
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
        mpl.rcParams['figure.subplot.hspace'] = 0.05
        mpl.rcParams['legend.fontsize'] = 8
        mpl.rcParams['legend.framealpha'] = .75
        mpl.rcParams['legend.loc'] = 'best'
        mpl.rcParams['savefig.bbox'] = 'tight'
        mpl.rcParams['savefig.dpi'] = 100
        plt.figure(100)
        plt.title('%s +/- 15 Days HRRR Composite: %s\nHRRR point: %s %s\nMesoWest Point: %s %s' \
                % (stn[0], var, \
                lat[point[0][0]][point[1][0]], lon[point[0][0]][point[1][0]], \
                a['LAT'][0], a['LON'][0]))

        if var == 'TMP:2 m':
            plt.plot(DATES, HTS_p90-273.15, label='p90')
            plt.plot(DATES, HTS_p10-273.15, label='p10')
        if var == 'DPT:2 m':
            plt.plot(DATES, HTS_p90-273.15, label='p90')                
            plt.plot(DATES, HTS_p10-273.15, label='p10')
            plt.ylabel('2 m Dew Point Temperature (C)')
        elif var == 'WIND:10 m':
            plt.plot(DATES, HTS_p90, label='p90')
            plt.plot(DATES, HTS_p10, label='p10')
            plt.ylabel(r'10 m Wind Speed (ms$\mathregular{^{-1}}$)')

        # Method 1: when you are using plt
        formatter = DateFormatter('%b-%d\n%H:00')
        plt.gcf().axes[0].xaxis.set_major_formatter(formatter)
        plt.grid()
        plt.legend()
        SAVEDIR = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/PhD/HRRR/OSG/daily30/'
        plt.savefig(SAVEDIR + stn[0]+'_'+variable+'_p90p10.png')

    # Plot Compute statistics
    if False:         
        # Multiprocessing :)
        cores = [[DIR+'OSG_HRRR_%s_m%02d_d%02d_h%02d_f00.h5' % \
                (variable, month, day, hour), 'cores'] \
                for month in months for day in range(1,days[month-1]+1) for hour in hours]
        count = [[DIR+'OSG_HRRR_%s_m%02d_d%02d_h%02d_f00.h5' % \
                (variable, month, day, hour), 'count'] \
                for month in months for day in range(1,days[month-1]+1) for hour in hours]
        timer = [[DIR+'OSG_HRRR_%s_m%02d_d%02d_h%02d_f00.h5' % \
                (variable, month, day, hour), 'timer'] \
                for month in months for day in range(1,days[month-1]+1) for hour in hours]
        num_proc = multiprocessing.cpu_count()
        p = multiprocessing.Pool(num_proc)
        cores = np.array(p.map(get_field_MP, cores))
        count = np.array(p.map(get_field_MP, count))
        timer = np.array(p.map(get_field_MP, timer))
        p.close()

        # Timer in seconds
        timer = np.array([int(t.split(':')[0])*86400 + int(t.split(':')[1])*60 + float(t.split(':')[2]) for t in timer])


        SAVEDIR = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/PhD/HRRR/OSG/daily30/'
        plt.figure(1)
        plt.scatter(DATES, cores)
        plt.ylabel('Cores')
        plt.title(var)
        formatter = DateFormatter('%b-%d\n%H:00')
        plt.gcf().axes[0].xaxis.set_major_formatter(formatter)
        plt.grid()
        plt.xlim(DATES[0], DATES[-1])
        plt.ylim(ymin=0)
        plt.savefig(SAVEDIR + variable+'_cores.png', bbox_inches='tight')

        plt.figure(2)
        plt.scatter(DATES, count)
        plt.ylabel('Sample Count')
        plt.title(var)
        formatter = DateFormatter('%b-%d\n%H:00')
        plt.gcf().axes[0].xaxis.set_major_formatter(formatter)
        plt.grid()
        plt.xlim(DATES[0], DATES[-1])
        plt.ylim(ymin=0)
        plt.savefig(SAVEDIR + variable+'_count.png', bbox_inches='tight')

        plt.figure(3)
        plt.scatter(DATES, timer)
        plt.ylabel('Statistical Compute Time (seconds)')
        plt.title(var)
        formatter = DateFormatter('%b-%d\n%H:00')
        plt.gcf().axes[0].xaxis.set_major_formatter(formatter)
        plt.grid()
        plt.xlim(DATES[0], DATES[-1])
        plt.ylim(ymin=0)
        plt.savefig(SAVEDIR + variable+'_timer.png', bbox_inches='tight')

        plt.figure(4)
        plt.scatter(count, timer)
        plt.xlabel('Sample Count')
        plt.ylabel('Computation Timer (seconds)')
        plt.title(var)
        plt.grid()
        plt.ylim(ymin=0)
        plt.savefig(SAVEDIR + variable+'_CountTimer.png', bbox_inches='tight')

        plt.figure(5)
        plt.scatter(cores, timer)
        plt.xlabel('Cores')
        plt.ylabel('Computation Timer (seconds)')
        plt.title(var)
        plt.grid()
        plt.ylim(ymin=0)
        plt.savefig(SAVEDIR + variable+'_CoresTimer.png', bbox_inches='tight')
