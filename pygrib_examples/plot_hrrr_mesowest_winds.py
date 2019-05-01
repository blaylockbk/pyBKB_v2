# Brian Blaylock
# 24 December 2015

# Plot Winds from HRRR forecasts


import pygrib
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import matplotlib as mpl
import os
from datetime import datetime, timedelta

# Now import modules of my own invention
import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB')

from functions_domains_models import get_domain
from BB_MesoWest import mesowest_stations_radius as MWr


## First set the plot font sizes and line width
tick_font = 8
label_font = 10
lw = 1.5    

mpl.rcParams['xtick.labelsize'] = tick_font
mpl.rcParams['ytick.labelsize'] = tick_font

FIGDIR = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/MS/raw_HRRR-MesoWest/'
# If that directory doesn't exist then create it
if not os.path.exists(FIGDIR):
    os.makedirs(FIGDIR)



def cut_data(bl_lat,tr_lat,bl_lon,tr_lon):
    '''    
    Cut down full netcdf data for domain for faster plotting.
    input: the bottom left corner and top right corner lat/lon coordinates
        bl_lat = bottom left latitude
        tr_lat = top right latitude
        bl_lon = bottom left longitude
        tr_lon = top right longitude
    return: the max and min of each the arrays x and y coordinates    
    
	lat and lon are global variables of the grids lat and lon
    '''
    lat_limit = np.logical_and(lat>bl_lat,lat<tr_lat)
    lon_limit = np.logical_and(lon>bl_lon,lon<tr_lon)
    
    total_limit = np.logical_and(lat_limit,lon_limit)
    
    xmin = np.min(np.where(total_limit==True)[0])-5 # +/- a buffer to cover map area (prevents white space in plot area) 
    xmax = np.max(np.where(total_limit==True)[0])+5
    ymin = np.min(np.where(total_limit==True)[1])-5
    ymax = np.max(np.where(total_limit==True)[1])+5
       
    return xmin,xmax,ymin,ymax


#--------------------------


request_time = datetime(2015,6,18,6,0,0)
while request_time < datetime(2015,6,19,6):
    # Open a file
    DIR = '/uufs/chpc.utah.edu/common/home/horel-group/archive/%04.f%02.f%02.f/models/hrrr/' % (request_time.year,request_time.month,request_time.day)
    FILE = 'hrrr.t%02.fz.wrfprsf00.grib2' % (request_time.hour)


    mesowest_time = request_time.strftime('%Y%m%d%H%M')

    timer = datetime.now()
    grbs = pygrib.open(DIR+FILE)
    print 'open',datetime.now()-timer


    timer = datetime.now()
    lat, lon = grbs.select(name='V component of wind')[-1].latlons()
    print 'lat/lon',datetime.now()-timer

    timer = datetime.now()
    u = grbs.select(name='U component of wind')[-1].values    # m/s
    print 'u',datetime.now() - timer
    timer = datetime.now()
    v = grbs.select(name='V component of wind')[-1].values    # m/s
    print 'v',datetime.now() - timer

    timer = datetime.now()
    speed = np.sqrt(u**2+v**2)
    print "speed", datetime.now() - timer



    timer = datetime.now()
    domain = get_domain('salt_lake_valley')
    bot_left_lat = domain['bot_left_lat']
    bot_left_lon = domain['bot_left_lon']
    top_right_lat = domain['top_right_lat']
    top_right_lon = domain['top_right_lon']
    print 'domians', datetime.now() - timer

    timer = datetime.now()
    xmin,xmax,ymin,ymax = cut_data(bot_left_lat,top_right_lat,bot_left_lon,top_right_lon)
    lat = lat[xmin:xmax,ymin:ymax]
    lon = lon[xmin:xmax,ymin:ymax]
    u   = u[xmin:xmax,ymin:ymax]
    v   = v[xmin:xmax,ymin:ymax]
    speed = speed[xmin:xmax,ymin:ymax]
    print 'trim', datetime.now() - timer


    timer = datetime.now()
    m = Basemap(resolution='i',projection='cyl',\
                llcrnrlon=bot_left_lon,llcrnrlat=bot_left_lat,\
                urcrnrlon=top_right_lon,urcrnrlat=top_right_lat,)
    print 'map',datetime.now()-timer
                
    timer = datetime.now()
    x,y = m(lon,lat)
    print 'convert',datetime.now()-timer


    timer = datetime.now()
    BASE = '/uufs/chpc.utah.edu/common/home/u0553130/'
    # Draw major roads from shapefile
    m.readshapefile('/uufs/chpc.utah.edu/common/home/u0553130/shape_files/tl_2015_UtahRoads_prisecroads/tl_2015_49_prisecroads','roads', linewidth=.2)
    print 'shapefile', datetime.now()-timer

    timer = datetime.now()
    im = plt.contourf(x,y,speed, np.arange(0,np.max(speed),.25),cmap = plt.cm.Greens)
    print 'contour',datetime.now()-timer

    timer = datetime.now()
    ## Wind Barbs
    units = 'm/s'
    if units == 'm/s':
        HALF = 2.5
        FULL = 5
        FLAG = 25
    if units == 'mph':
        HALF = 2.5
        FULL = 5
        FLAG = 25
    barbs = m.barbs(x,y,u,v,length=6,barbcolor="k",\
                       flagcolor='r',linewidth=.5,\
                        barb_increments=dict(half=HALF, full=FULL, flag=FLAG))

    print 'barbs',datetime.now()-timer


    timer = datetime.now()
    ## MesoWest Wind Barbs
    units = 'm/s'
    if units == 'm/s':
        HALF = 2.5
        FULL = 5
        FLAG = 25
    if units == 'mph':
        HALF = 2.5
        FULL = 5
        FLAG = 25
        
        
    a = MWr.get_mesowest_radius_winds(mesowest_time,'10')
    u,v = MWr.wind_spddir_to_uv(a['WIND_SPEED'],a['WIND_DIR'])
    m.barbs(a['LON'],a['LAT'],u,v,
            length=6.5,barbcolor="b",\
            flagcolor='r',linewidth=.75,\
            barb_increments=dict(half=HALF, full=FULL, flag=FLAG))

    print 'mesowest barbs',datetime.now()-timer

    plt.title(request_time.strftime('%d %b %Y %H:%M UTC'))

    
    
    plt.savefig(FIGDIR+request_time.strftime('%y%m%d_%H%M'))
    
    request_time=request_time +timedelta(hours=1)
    
    
    #plt.show()


