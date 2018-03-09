# Brian Blaylock
# February 22, 2018

"""
Overlay OSG Statistics with current HRRR Runs
"""

import h5py
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
from collections import OrderedDict
from datetime import date, datetime, timedelta
import multiprocessing

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
from BB_downloads.HRRR_S3 import *
from BB_wx_calcs.wind import wind_uv_to_spd
from BB_data.grid_manager import pluck_point_new
from BB_MesoWest.MesoWest_STNinfo import get_MW_location_dict

from matplotlib.dates import DateFormatter
formatter = DateFormatter('%b %d\n%H:%M')

import matplotlib as mpl
mpl.rcParams['figure.figsize'] = [8, 6]
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


def plot_for_each_fxx(f):   
    ## HRRR Model Run date
    RUN = D-timedelta(hours=f)
    
    ## Get HRRR data for this run
    if var.split(':')[0] == 'UVGRD':
        # Calculate wind speed from U and V components
        level = var.split(':')[1]
        HU = get_hrrr_variable(RUN, 'UGRD:'+level, fxx=f, value_only=True, verbose=False)    
        HV = get_hrrr_variable(RUN, 'VGRD:'+level, fxx=f, value_only=True, verbose=False)
        speed = wind_uv_to_spd(HU['value'], HV['value'])
        H = HU
        H['value'] = speed
    else:
        H = get_hrrr_variable(RUN, var, fxx=f, value_only=True, verbose=False)
    
    ## Convert units and get values in bounding box area
    if var == 'TMP:2 m' or var == 'DPT:2 m':
        Hpoint = H['value'][x,y]-273.15
        Harea = H['value'][x-box_radius:x+box_radius+1,y-box_radius:y+box_radius+1]-273.15    
    else:
        Hpoint = H['value'][x,y]
        Harea = H['value'][x-box_radius:x+box_radius+1,y-box_radius:y+box_radius+1]
    
    ## Calculate the HRRR percentiles in the boxed area for this run
    HP = np.percentile(Harea, [0,25,50,75,100])

    ## --- Plot OSG percentiles ---------------------------------------
    plt.fill_between(percentiles, area_P[0][0], area_P[0][4],
                        color='lightgrey',
                        label='p100-p00',
                        zorder=1)
    plt.fill_between(percentiles, area_P[0][1], area_P[0][3],
                        color='grey',
                        label='p25-p75',
                        zorder=1)
    plt.plot(percentiles, area_P[0][2],
                color='lightgrey',
                label="p50",
                zorder=1)
    ## Plot all percentiles for each grid box
    #for i in range(box_radius*2+1):
    #    for j in range(box_radius*2+1):
    #        plt.plot(percentiles, PP[i,j,:])
    
    ## Plot OSG percentiles for the single grid box nearest the station of interest
    plt.plot(percentiles, PP[box_radius,box_radius,:],
                linestyle='--',
                color='k',
                label='%s OSG Percentiles' % stn,
                zorder=1)

    ## --- Plot RUN percentiles -------------------------------------
    # Linear interpolation to find the percentile for the value
    for i in range(5):
        p100Hpoint = HP[i]
        p100PP = area_P[0][i]
        if p100Hpoint >= np.max(p100PP):
            p100Y = p100Hpoint
            p100X = 100
            print "Hpoint > PP, exceeds p100", D, f
        elif p100Hpoint <= np.min(p100PP):
            p100Y = p100Hpoint
            p100X = 0
            print "Hpoint < PP exceeds p00", D, f,
        else:
            p100y1 = np.min(filter(lambda x: x>=p100Hpoint, p100PP))
            p100y1_idx = np.where(p100PP==p100y1)[0][0]
            p100x1 = percentiles[p100y1_idx]
            p100y2 = p100PP[p100y1_idx-1]
            p100x2 = percentiles[p100y1_idx-1]
            p100m = (p100y2-p100y1)/(p100x2-p100x1)
            p100b = 0-p100m*p100x1+p100y1
            p100Y = p100Hpoint
            p100X = (p100Y-p100b)/p100m
        plt.axhline(p100Hpoint, xmax=p100X/100, color='r', linewidth=1, zorder=50)
        plt.axvline(p100X, ymax=(p100Hpoint-ymin)/(ymax-ymin), color='r', linewidth=1, zorder=50)
        plt.scatter(p100X, p100Hpoint, s=25, color='r', zorder=50)
    ## Plot value from current HRRR run for every grid box
    #for i in range(box_radius*2+1):
    #    for j in range(box_radius*2+1):
    #        plt.axhline(Harea[i,j], linewidth=.1)
        
    ## Plot HRRR value for stn grid box for urrent HRRR run
    # Linear interpolation to find the percentile for the value
    stnPP = PP[box_radius,box_radius,:]
    if Hpoint >= np.max(stnPP):
        Y = Hpoint
        X = 100
        print "station Hpoint > PP, exceeds p100", D, f
    elif Hpoint <= np.min(stnPP):
        Y = Hpoint
        X = 0
        print "station Hpoint < PP, exceeds p00", D, f
    else:
        y1 = np.min(filter(lambda x: x>=Hpoint, stnPP))
        y1_idx = np.where(stnPP==y1)[0][0]
        x1 = percentiles[y1_idx]
        y2 = stnPP[y1_idx-1]
        x2 = percentiles[y1_idx-1]
        m = (y2-y1)/(x2-x1)
        b = 0-m*x1+y1
        Y = Hpoint
        X = (Y-b)/m
    plt.axhline(Hpoint, xmax=X/100, color='k', lw=6, zorder=100)
    plt.axvline(X, ymax=(Hpoint-ymin)/(ymax-ymin), color='k', lw=6, zorder=100)
    plt.scatter(X, Hpoint, s=150, color='k', zorder=100)

    ## --- Other Plot Elements --------------------------------------
    plt.grid()
    plt.legend(loc='upper left')

    plt.xlabel('Percentiles\n%sx%s km box centered at %s' % (np.shape(PP)[0]*3, np.shape(PP)[0]*3, stn))
    xtick_labels = [0,'','','','',5,10,25,33,50,66,75,90,95,'','','','',100]
    plt.xticks(percentiles, xtick_labels)
    plt.xlim([0,100])
    plt.ylabel(var)
    plt.ylim([ymin, ymax])
    
    plt.title('Valid: %s' % D.strftime('%Y-%b-%d %H:%M'), loc='Left')
    plt.title('%s\n%s' % (stn, var), loc='Center', fontweight='bold')
    plt.title('Run: %s F%02d' % (RUN.strftime("%Y-%b-%d %H:%M"), f), loc='right')

    plt.savefig(SAVEDIR+'%s_f%02d.png' % (D.strftime('%Y-%m-%d_%H'), f))
    plt.close()
    return None

def plot_for_each_fxx_with_Map(f):   
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=[15,6])
    plt.sca(ax1)
    ## HRRR Model Run date
    RUN = D-timedelta(hours=f)
    
    ## Get HRRR data for this run
    if var.split(':')[0] == 'UVGRD':
        # Calculate wind speed from U and V components
        level = var.split(':')[1]
        HU = get_hrrr_variable(RUN, 'UGRD:'+level, fxx=f, value_only=True, verbose=False)    
        HV = get_hrrr_variable(RUN, 'VGRD:'+level, fxx=f, value_only=True, verbose=False)
        speed = wind_uv_to_spd(HU['value'], HV['value'])
        H = {'value': speed}
        Hpoint = speed[x,y]
        Harea = speed[x-box_radius:x+box_radius+1,y-box_radius:y+box_radius+1]
        HUarea = HU['value'][x-box_radius:x+box_radius+1,y-box_radius:y+box_radius+1]
        HVarea = HV['value'][x-box_radius:x+box_radius+1,y-box_radius:y+box_radius+1]
    else:
        H = get_hrrr_variable(RUN, var, fxx=f, value_only=True, verbose=False)
        ## Convert units and get values in bounding box area
        if var == 'TMP:2 m' or var == 'DPT:2 m':
            H['value'] = H['value']-273.15
            Hpoint = H['value'][x,y]
            Harea = H['value'][x-box_radius:x+box_radius+1,y-box_radius:y+box_radius+1]
        else:
            Hpoint = H['value'][x,y]
            Harea = H['value'][x-box_radius:x+box_radius+1,y-box_radius:y+box_radius+1]
    
    ## Calculate the HRRR percentiles in the boxed area for this run
    HP = np.percentile(Harea, [0,25,50,75,100])

    ## --- Plot OSG percentiles ---------------------------------------
    plt.fill_between(percentiles, area_P[0][0], area_P[0][4],
                        color='lightgrey',
                        label='p100-p00',
                        zorder=1)
    plt.fill_between(percentiles, area_P[0][1], area_P[0][3],
                        color='grey',
                        label='p25-p75',
                        zorder=1)
    plt.plot(percentiles, area_P[0][2],
                color='lightgrey',
                label="p50",
                zorder=1)
    ## Plot all percentiles for each grid box
    #for i in range(box_radius*2+1):
    #    for j in range(box_radius*2+1):
    #        plt.plot(percentiles, PP[i,j,:])
    
    ## Plot OSG percentiles for the single grid box nearest the station of interest
    plt.plot(percentiles, PP[box_radius,box_radius,:],
                linestyle='--',
                color='k',
                label='%s OSG Percentiles' % stn,
                zorder=1)

    ## --- Plot RUN percentiles -------------------------------------
    # Linear interpolation to find the percentile for the value
    for i in range(5):
        p100Hpoint = HP[i]
        p100PP = area_P[0][i]
        if p100Hpoint >= np.max(p100PP):
            p100Y = p100Hpoint
            p100X = 100
            print "Hpoint > PP, exceeds p100", D, f
        elif p100Hpoint <= np.min(p100PP):
            p100Y = p100Hpoint
            p100X = 0
            print "Hpoint < PP exceeds p00", D, f,
        else:
            p100y1 = np.min(filter(lambda x: x>=p100Hpoint, p100PP))
            p100y1_idx = np.where(p100PP==p100y1)[0][0]
            p100x1 = percentiles[p100y1_idx]
            p100y2 = p100PP[p100y1_idx-1]
            p100x2 = percentiles[p100y1_idx-1]
            p100m = (p100y2-p100y1)/(p100x2-p100x1)
            p100b = 0-p100m*p100x1+p100y1
            p100Y = p100Hpoint
            p100X = (p100Y-p100b)/p100m
        plt.axhline(p100Hpoint, xmax=p100X/100, color='r', linewidth=1, zorder=50)
        plt.axvline(p100X, ymax=(p100Hpoint-ymin)/(ymax-ymin), color='r', linewidth=1, zorder=50)
        plt.scatter(p100X, p100Hpoint, s=25, color='r', zorder=50)
    ## Plot value from current HRRR run for every grid box
    #for i in range(box_radius*2+1):
    #    for j in range(box_radius*2+1):
    #        plt.axhline(Harea[i,j], linewidth=.1)
        
    ## Plot HRRR value for stn grid box for urrent HRRR run
    # Linear interpolation to find the percentile for the value
    stnPP = PP[box_radius,box_radius,:]
    if Hpoint >= np.max(stnPP):
        Y = Hpoint
        X = 100
        print "station Hpoint > PP, exceeds p100", D, f
    elif Hpoint <= np.min(stnPP):
        Y = Hpoint
        X = 0
        print "station Hpoint < PP, exceeds p00", D, f
    else:
        y1 = np.min(filter(lambda x: x>=Hpoint, stnPP))
        y1_idx = np.where(stnPP==y1)[0][0]
        x1 = percentiles[y1_idx]
        y2 = stnPP[y1_idx-1]
        x2 = percentiles[y1_idx-1]
        m = (y2-y1)/(x2-x1)
        b = 0-m*x1+y1
        Y = Hpoint
        X = (Y-b)/m
    plt.axhline(Hpoint, xmax=X/100, color='k', lw=6, zorder=100)
    plt.axvline(X, ymax=(Hpoint-ymin)/(ymax-ymin), color='k', lw=6, zorder=100)
    plt.scatter(X, Hpoint, s=150, color='k', zorder=100)

    ## --- Other Plot Elements --------------------------------------
    plt.grid()
    plt.legend(loc='upper left')

    plt.xlabel('Percentiles\n%sx%s km box centered at %s' % (np.shape(PP)[0]*3, np.shape(PP)[0]*3, stn))
    xtick_labels = [0,'','','','',5,10,25,33,50,66,75,90,95,'','','','',100]
    plt.xticks(percentiles, xtick_labels)
    plt.xlim([0,100])
    plt.ylabel(label_units)
    plt.ylim([ymin, ymax])
    
    
    plt.title('Run: %s F%02d' % (RUN.strftime("%Y-%b-%d %H:%M"), f), loc='left')

    #plt.savefig(SAVEDIR+'%s_f%02d.png' % (D.strftime('%Y-%m-%d_%H'), f))
    #plt.close()

    #####----- Side Map -------
    plt.sca(ax2)
    am.drawcounties()
    am.arcgisimage(service='World_Shaded_Relief')  
    
    if var == 'REFC:entire':
        dBZ = H['value']
        dBZ = np.ma.array(dBZ)
        dBZ[dBZ == -10] = np.ma.masked
        vmax = 80
        vmin = 0
        H['value'] = dBZ
    elif var in ['UVGRD:10 m', 'UVGRD:80 m', 'GUST:surface']:
        vmax = np.max(Harea)
        vmin = 0
    else:
        vmax = np.max(Harea)
        vmin = np.min(Harea)

    am.pcolormesh(lon, lat, H['value'], alpha=.3, cmap=cmap, vmax=vmax, vmin=vmin)
    cb = plt.colorbar(orientation='vertical', pad=0.01, shrink=0.85)
    cb.set_label(label_units)

    # Station Point
    am.scatter(MWlon, MWlat)
    # Bottom Boundary
    am.drawgreatcircle(LONS_BOX[0,-1], LATS_BOX[0,-1],
                    LONS_BOX[0,0], LATS_BOX[0,0],
                    color='k')
    # Left Boundary
    am.drawgreatcircle(LONS_BOX[0,0], LATS_BOX[0,0],
                    LONS_BOX[-1,0], LATS_BOX[-1,0],
                    color='k')
    # Top Boundary
    am.drawgreatcircle(LONS_BOX[-1,-1], LATS_BOX[-1,-1],
                    LONS_BOX[-1,0], LATS_BOX[-1,0],
                    color='k')
    # Right Boundary
    am.drawgreatcircle(LONS_BOX[-1,-1], LATS_BOX[-1,-1],
                    LONS_BOX[0,-1], LATS_BOX[0,-1],
                    color='k')
    # Barbs
    if var == 'UVGRD:10 m' or var == 'UVGRD:80 m':
        am.barbs(LONS_BOX, LATS_BOX, HUarea, HVarea,
                 zorder=200, length=5, color='k',
                 barb_increments={'half':2.5, 'full':5,'flag':25},
                 latlon=True)

    plt.title('Valid: %s' % D.strftime('%Y-%b-%d %H:%M'), loc='right')
    
    plt.suptitle('%s  %s' % (stn, var))
    plt.savefig(SAVEDIR+'h%02d_f%02d.png' % (D.hour, f))
    plt.close()
    return None

###############################################################################

###############################################################################

###############################################################################

## --- User Set Up ------------------------------------------------------------

# List of all hours for yesterday
DATE = date.today()-timedelta(days=1)
#DATE = datetime(2018, 3, 2)

# MesoWest Station ID and Info
stn = 'WBB'     # WBB   HWKC1   DBSU1
#stn = 'HWKC1'
#stn = 'DBSU1'
#stn = '26.022,-81.512'

# Box area "radius" for area statistics
box_radius = 7

VARS = ['TMP:2 m', 'UVGRD:10 m', 'DPT:2 m', 'UVGRD:80 m', 'REFC:entire', 'GUST:surface', 'HGT:500']
# -----------------------------------------------------------------------------

print 'working on ', DATE, stn

# Get datetimes for every hour of the requested DATE
DATES = [datetime(DATE.year, DATE.month, DATE.day, h) for h in range(24)]

# Get latitude and longitude of stn or lat,lon string
if len(stn.split(',')) == 1:
    LD = get_MW_location_dict(stn)
    MWlat = LD[stn]['latitude']
    MWlon = LD[stn]['longitude']
else:
    MWlat, MWlon = stn.split(',')
    MWlat = float(MWlat)
    MWlon = float(MWlon)

# List of percentiles computed in the percentiles file
percentiles = [0,1,2,3,4,5,10,25,33,50,66,75,90,95,96,97,98,99,100]

# Load HRRR lat/lon Grid
DIR = '/uufs/chpc.utah.edu/common/home/horel-group2/blaylock/HRRR_OSG/'
latlon_file = h5py.File(DIR+'OSG_HRRR_latlon.h5', 'r')
lat = latlon_file['latitude'].value
lon = latlon_file['longitude'].value

# Pluck point of MesoWest station location in HRRR grid
point = pluck_point_new(MWlat, MWlon, lat, lon)
x = point[0][0]
y = point[1][0]

print '     MesoWest  |  HRRR Nearest Point   '
print 'lat: %s        |  %s' % (MWlat, lat[x,y])
print 'lon: %s        |  %s' % (MWlon, lon[x,y])

# Bounding box around the point
LATS_BOX = lat[x-box_radius:x+box_radius+1,y-box_radius:y+box_radius+1]
LONS_BOX = lon[x-box_radius:x+box_radius+1,y-box_radius:y+box_radius+1]

top_right_lat = LATS_BOX.max()
top_right_lon = LONS_BOX.min()
bot_left_lat = LATS_BOX.min()
bot_left_lon = LONS_BOX.max()

# Draw area map
am = Basemap(llcrnrlon=MWlon-.3,  urcrnrlon=MWlon+.3,
            llcrnrlat=MWlat-.3, urcrnrlat=MWlat+.3)


for var in VARS:
    print var
    variable = var.replace(':', '_').replace(' ', '_')

    ## Define the Save Directory
    SAVEDIR = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/PhD/HRRR/OSG/area_current_HRRR/%s/%s/' % (stn, variable)
    if not os.path.isdir(SAVEDIR):
        os.makedirs(SAVEDIR)

    ## OSG data directory
    DIR = '/uufs/chpc.utah.edu/common/home/horel-group2/blaylock/HRRR_OSG/hourly30/%s/' % (variable)

    # Variable specific variables
    if var == 'TMP:2 m':
        cmap = 'Spectral_r'
        label_units = '2 m Temperature (C)'
    elif var == 'DPT:2 m':
        cmap = 'BrBG'
        label_units = '2 m Dew Point (C)'
    elif var == 'REFC:entire':
        cmap = 'gist_ncar'
        label_units = 'Simulated Reflectivity (dBZ)'
    elif var == 'UVGRD:10 m':
        cmap = 'inferno_r'
        label_units = r'10 m Wind Speed (ms$\mathregular{^{-1}}$)'
    elif var == 'UVGRD:80 m':
        cmap = 'magma_r'
        label_units = r'80 m Wind Speed (ms$\mathregular{^{-1}}$)'
    elif var == 'HGT:500':
        cmap = 'Blues'
        label_units = '500 mb Geopotential Height'
    else:
        cmap = 'viridis'
        label_units = 'unknown (unknown)'

    for D in DATES:
        ## Get area OSG percentiles from the bounding box for each percentile
        FILE = 'OSG_HRRR_%s_m%02d_d%02d_h%02d_f00.h5' % ((variable, D.month, D.day, D.hour))
        print DIR+FILE
        
        ## Calculate area percentiles from the OSG percentiles for each percentile
        with h5py.File(DIR+FILE, 'r') as ff:
            for i, percentile in enumerate(percentiles):
                # The area box for this percentile (converted units if necessary)
                pp = ff["p%02d" % percentile][x-box_radius:x+box_radius+1,y-box_radius:y+box_radius+1]
                if var == 'TMP:2 m' or var == 'DPT:2 m':
                    pp -= 273.15
                # Percentiles for that box area (percentiles of percentiles)
                p = np.percentile(pp, [0, 25, 50, 75, 100])
                # Store in an array
                if i == 0:
                    PP = pp
                    area_P = p
                else:
                    PP = np.dstack([PP, pp])
                    area_P = np.dstack([area_P, p])

        
        # Y axis limits only once (we want the axes to be the same for all plots)
        if D == DATES[0]:
            if var in ['UVGRD:10 m', 'UVGRD:80 m', 'WIND:10 m', 'GUST:surface']:
                ymax = PP.max()+10
                ymin = 0
            elif var == 'REFC:entire':
                ymax = 80
                ymin = -10
            else:
                ymax = PP.max()+15
                ymin = PP.min()-15
        
        ## For this valid date, loop through each forecast hour
        #p = multiprocessing.Pool(19)
        #p.map(plot_for_each_fxx, range(19))
        #p.close()

        p = multiprocessing.Pool(19)
        p.map(plot_for_each_fxx_with_Map, range(19))
        p.close()


        

            
