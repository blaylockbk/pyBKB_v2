# Brian Blaylock
# October 6, 2017        Getting our marriage license today :)

"""
Histogram bins for series of HRRR datasets
"""

import numpy as np
from datetime import datetime, timedelta
from netCDF4 import Dataset
import multiprocessing # :)
import matplotlib.pyplot as plt
import h5py

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2/')
from BB_downloads.HRRR_S3 import get_hrrr_variable
from BB_wx_calcs.wind import wind_uv_to_spd, wind_uv_to_dir

def get_HRRR_value(getthisDATE):
    """
    Getting HRRR data, just return the value (not the latitude and longitude)
    """
    print getthisDATE
    H = get_hrrr_variable(getthisDATE, variable, fxx=fxx, model='hrrr', field='sfc', value_only=True, verbose=False)
    if H['value'] is None:
        print "!! WARNING !! COULD NOT GET", getthisDATE
    return H['value']

def histogram(direction, var, bins, nsector, normed=False, blowto=False):
    """
    From windrose: https://github.com/python-windrose/windrose/
    Returns an array where, for each sector of wind
    (centred on the north), we have the number of time the wind comes with a
    particular var (speed, polluant concentration, ...).
    * direction : 1D array - directions the wind blows from, North centred
    * var : 1D array - values of the variable to compute. Typically the wind
      speeds
    * bins : list - list of var category against we're going to compute the table
    * nsector : integer - number of sectors
    * normed : boolean - The resulting table is normed in percent or not.
    * blowto : boolean - Normaly a windrose is computed with directions
    as wind blows from. If true, the table will be reversed (usefull for
    pollutantrose)
    """
    if len(var) != len(direction):
        raise(ValueError("var and direction must have same length"))

    angle = 360. / nsector

    dir_bins = np.arange(-angle / 2, 360. + angle, angle, dtype=np.float)
    dir_edges = dir_bins.tolist()
    dir_edges.pop(-1)
    dir_edges[0] = dir_edges.pop(-1)
    dir_bins[0] = 0.

    var_bins = bins.tolist()
    var_bins.append(np.inf)

    if blowto:
        direction = direction + 180.
        direction[direction >= 360.] = direction[direction >= 360.] - 360

    table = np.histogram2d(x=var, y=direction, bins=[var_bins, dir_bins], normed=False)[0]
    # add the last value to the first to have the table of North winds
    table[:, 0] = table[:, 0] + table[:, -1]
    # and remove the last col
    table = table[:, :-1]
    if normed:
        table = table * 100 / table.sum()
 
    return dir_edges, var_bins, table

def get_hist_table(ij):
    """
    (Function for multiprocessing)
    For each grid, create historgram table.
    """
    i, j = ij
    print i, j
    sector_edges, bins, table = histogram(WDIR[:, i, j], WSPD[:, i, j], speed_bins, num_dir_sectors)
    print np.shape(table)
    #return table.flatten()
    return table

# =============================================================================
# Input arguments (dates should represents the valid time)
month = 9
day = 15
hour = 0
fxx = 0

# Archvie Date Range
sDATE = datetime(2015, 4, 18, hour)
eDATE = datetime(2017, 8, 1, hour)
# =============================================================================
timer1 = datetime.now()

# Range of dates for the desired Month, Hour, and Day 
# (e.g. all 0100 UTC for 15 days before and after the 6th day of the month of January)
# requestDATES is the file we want from the Pando archive, and we will account
# for the offset with the fxx argument.
years = range(sDATE.year, eDATE.year+1)
validDATES = []
for y in years:
    try:
        centerDATE = datetime(y, month, day, hour)
        print datetime(y, month, day, hour), '    fxx:', fxx
    except:
        print 'Not a valid date: datetime(%s, %s, %s, %s)' % (y, month, day, hour)
        continue
    begin = centerDATE-timedelta(days=15)
    end = centerDATE+timedelta(days=15)
    chunk = [begin+timedelta(days=x) for x in range(0,(end-begin).days) if begin+timedelta(days=x) > sDATE]
    validDATES += chunk

requestDATES = np.array([d-timedelta(hours=fxx) for d in validDATES])

# =============================================================================
# =============================================================================
#if len(requestDATES) != 0:
# Multiprocessing :) Get field of each item in list requestDATES
cpu_count = multiprocessing.cpu_count()
#    
variable = 'UGRD:10 m'
p = multiprocessing.Pool(cpu_count)
U = p.map(get_HRRR_value, requestDATES)
U = np.array([x for x in U if x is not None])
p.close()
#
variable = 'VGRD:10 m'
p = multiprocessing.Pool(cpu_count)
V = p.map(get_HRRR_value, requestDATES)
V = np.array([x for x in V if x is not None])
p.close()

# Convert U and V to Speed and Direction
WSPD = wind_uv_to_spd(U, V)
WDIR = wind_uv_to_dir(U, V)

# get a single H dictionary (need the lat/lon arrays)
H = get_hrrr_variable(requestDATES[0], 'UGRD:10 m')

# Histogram bins
num_dir_sectors = 8              # Number of directional sectors (sectors calculated in histogram function)
speed_bins = np.arange(0, 10, 2)  # Speed bins
num_spd_bins = len(speed_bins)    # Number of speed bins

rose_dim = num_spd_bins * num_dir_sectors
x_dim, y_dim = H['value'].shape


# make rose table for each point in HRRR
indexes = [[i, j] for i in range(x_dim) for j in range(y_dim)]

p = multiprocessing.Pool(cpu_count)
result = np.array(p.map(get_hist_table, indexes))
p.close()

rose_storage = result.reshape(x_dim, y_dim, num_spd_bins, num_dir_sectors)

# Get the hisotgram bins to return
sector_edges, bins, table = histogram(WDIR[:, 0, 0], WSPD[:, 0, 0], speed_bins, num_dir_sectors)

timer = datetime.now() - timer1

# Write the HDF5 file of the data
var_name = 'ROSE_10m'
f = h5py.File('OSG_HRRR_%s_m%02d_d%02d_h%02d_f%02d.h5' % (var_name, month, day, hour, fxx), 'w')
h5_per = f.create_dataset('rose tables', data=rose_storage.astype(int), compression="gzip", compression_opts=9)
h5_count = f.create_dataset('wind speed bins', data=bins)
h5_count = f.create_dataset('wind direction edges', data=sector_edges)
h5_cores = f.create_dataset('cores', data=cpu_count)
h5_timer = f.create_dataset('timer', data=str(timer))
h5_begD = f.create_dataset('Beginning Date', data=validDATES[0].strftime('%Y-%m-%d-%H:00'))
h5_endD = f.create_dataset('Ending Date', data=validDATES[-1].strftime('%Y-%m-%d-%H:00'))
f.close()

# Could add percentiles for the wind speed
# Store counts as integers, not floats, to save memory (difference between 23 MB/file to 22 MB/file)



#==============================================================================
#==============================================================================
h5 = h5py.File('OSG_HRRR_%s_m%02d_d%02d_h%02d_f%02d.h5' % (var_name, month, day, hour, fxx), 'r')
rose = h5['rose tables']


#==============================================================================
# total samples in each point
samples = np.sum(rose[0,0]) # same as np.sum(rose[0, 0, :, :])

# total samples between last speed bin and infinity (top left corner)
count_highest_spd_bin = np.sum(rose[0,0][-1,:])

# total samples of north wind at a point (top left corner)
count_highest_spd_bin = np.sum(rose[0,0][:,0])

#==============================================================================
# Plot CONUS with count of highest wind bin (in this case, winds greater than 8) in all directions
CONUS_highest_bin_count = np.sum(rose[:,:,-1,:], axis=2)

plt.figure(1)
plt.pcolormesh(CONUS_highest_bin_count)
plt.colorbar()
plt.title('Count Wind Speed Greater than %s ms-1\nMonth:%02d, Day:%02d, Hour:%02d\nFirst: %s\n Last: %s' % (h5['wind speed bins'][-2], month, day, hour, validDATES[0], validDATES[-1]))

plt.figure(2)
plt.pcolormesh(CONUS_highest_bin_count/float(samples))
plt.colorbar()
plt.title('Occurance Wind Speed Greater than %s ms-1\nMonth:%02d, Day:%02d, Hour:%02d\nFirst: %s\n Last: %s' % (h5['wind speed bins'][-2], month, day, hour, validDATES[0], validDATES[-1]))
plt.show()

# Plot CONUS with north wind at all wind speeds
CONUS_north_wind_count = np.sum(rose[:,:,:,0], axis=2)

plt.figure(1)
plt.pcolormesh(CONUS_north_wind_count)
plt.colorbar()
plt.title('Count North Wind\nMonth:%02d, Day:%02d, Hour:%02d\nFirst: %s\n Last: %s' % (month, day, hour, validDATES[0], validDATES[-1]))

plt.figure(2)
plt.pcolormesh(CONUS_north_wind_count/float(samples))
plt.colorbar()
plt.title('Occurance North Wind\nMonth:%02d, Day:%02d, Hour:%02d\nFirst: %s\n Last: %s' % (month, day, hour, validDATES[0], validDATES[-1]))
plt.show()

# Plot CONUS with south wind at all wind speeds
CONUS_south_wind_count = np.sum(rose[:,:,:,4], axis=2)

plt.figure(1)
plt.pcolormesh(CONUS_south_wind_count)
plt.colorbar()
plt.title('Count South Wind\nMonth:%02d, Day:%02d, Hour:%02d\nFirst: %s\n Last: %s' % (month, day, hour, validDATES[0], validDATES[-1]))

plt.figure(2)
plt.pcolormesh(CONUS_south_wind_count/float(samples))
plt.colorbar()
plt.title('Occurance South Wind\nMonth:%02d, Day:%02d, Hour:%02d\nFirst: %s\n Last: %s' % (month, day, hour, validDATES[0], validDATES[-1]))
plt.show()



## ============================================================================
# Pluck a point from HRRR grid
latlon = h5py.File('/uufs/chpc.utah.edu/common/home/horel-group2/blaylock/HRRR_OSG/daily30_20150418-20170801/OSG_HRRR_latlon.h5', 'r')
lat = latlon['latitude'].value
lon = latlon['longitude'].value

wbb_lat = 40.76623
wbb_lon = -111.84755

from BB_data.grid_manager import pluck_point_new
from pylab import poly_between
from BB_rose.windrose import WindroseAxes

I, J = pluck_point_new(wbb_lat, wbb_lon, lat, lon)
i = I[0]
j = J[0]

wbb_rose_table = rose[i, j]

## ============================================================================
# Plot a rose for the point
new_bins = bins[0:-1]
new_nbins = num_spd_bins
new_nsector = num_dir_sectors
new_cmap = mpl.cm.jet
new_colors = [new_cmap(i) for i in np.linspace(0.0, 1.0, new_nbins)]
new_angles = np.arange(0, -2*np.pi, -2*np.pi/new_nsector) + np.pi/2

plot_angles = np.hstack((new_angles, new_angles[-1]-2*np.pi/new_nsector))
plot_vals = np.hstack((wbb_rose_table,
                       np.reshape(wbb_rose_table[:,0],
                                 (wbb_rose_table.shape[0], 1))))

fig = plt.figure(figsize=(8, 8), dpi=80, facecolor='w', edgecolor='w')
rect = [0.1, 0.1, 0.8, 0.8]
ax = WindroseAxes(fig, rect, axisbg='w')
fig.add_axes(ax)

opening = 0.8
dtheta = 2*np.pi/new_nsector
opening = dtheta*opening

wbb_rose_percent = wbb_rose_table/float(samples)

for j in range(new_nsector):
    offset = 0
    for i in range(new_nbins):
        if i > 0:
            offset += wbb_rose_percent[i-1, j]
        val = wbb_rose_percent[i, j]
        zorder = ZBASE + new_nbins - i
        patch = mpl.patches.Rectangle((plot_angles[j]-opening/2, offset), opening, val,
                                      facecolor=new_colors[i], edgecolor=None, zorder=zorder)
        ax.add_patch(patch)
        if j == 0:
            ax.patches_list.append(patch)


handles = list()
for p in ax.patches_list:
    if isinstance(p, mpl.patches.Polygon) or \
    isinstance(p, mpl.patches.Rectangle):
        color = p.get_facecolor()
    elif isinstance(p, mpl.lines.Line2D):
        color = p.get_color()
    else:
        raise AttributeError("Can't handle patches")
    handles.append(mpl.patches.Rectangle((0, 0), 0.2, 0.2,
        facecolor=color, edgecolor='black'))


labels = np.copy(bins)
labels = ["[%.1f : %0.1f] m s-1" %(labels[i], labels[i+1]) \
            for i in range(len(labels)-1)]
ax.legend_ = mpl.legend.Legend(ax, handles, labels, loc='lower left')
