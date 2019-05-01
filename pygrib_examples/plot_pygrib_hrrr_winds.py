# Brian Blaylock
# 24 December 2015

# Plot Winds from HRRR forecasts


import pygrib
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from datetime import datetime




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

# Dicitonaries of Map Domains
        # Notes: 'thin' is used to thin out the wind barbs.
domains = {			
'salt_lake_valley': {
                'map_domain'    :'Salt_Lake_Valley',
                'name'          :'Salt Lake Valley',
                'map_projection':'cyl',
                'units'         :'m/s',
                'thin'          :1,
                'max_speed'     :25,
                'time_zone'     :6,
                'bot_left_lat'  :40.4,
                'bot_left_lon'  :-112.19785,
                'top_right_lat' :40.9,
                'top_right_lon' :-111.60
                },
'utah_valley': {
                'map_domain'    :'Utah_Valley',
                'name'          :'Utah Valley',
                'map_projection':'cyl',
                'units'         :'m/s',
                'thin'          :1,
                'max_speed'     :25,
                'time_zone'     :6,
                'bot_left_lat'  :40.001550,
                'bot_left_lon'  :-111.901389,
                'top_right_lat' :40.451040,
                'top_right_lon' :-111.501889
                },
'utah_lake': {
                'map_domain'    :'Utah_Lake',
                'name'          :'Utah Lake',
                'map_projection':'cyl',
                'units'         :'mph',
                'thin'          :1,
                'max_speed'     :30,
                'time_zone'     :6,
                'bot_left_lat'  :40.,
                'bot_left_lon'  :-111.951,
                'top_right_lat' :40.375,
                'top_right_lon' :-111.65
                } # remember to add the , and } if you uncomment the stuff below!!!
}

#--------------------------


request_date = datetime(2015,6,18,0)

y = request_date.year
m = request_date.month
d = request_date.day
h = request_date.hour 
f = 0


# Open a file
DIR = '/uufs/chpc.utah.edu/common/home/horel-group/archive/%04d%02d%02d/models/hrrr/' % (y,m,d)
FILE = 'hrrr.t%02dz.wrfprsf%02d.grib2' % (h,f)




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
domain = domains['salt_lake_valley']
bot_left_lat = domain['bot_left_lat']-.25
bot_left_lon = domain['bot_left_lon']-.25
top_right_lat = domain['top_right_lat']+.25
top_right_lon = domain['top_right_lon']+.25
print 'domians', datetime.now() - timer

timer = datetime.now()
xmin,xmax,ymin,ymax = cut_data(bot_left_lat,top_right_lat,bot_left_lon,top_right_lon)
lat = lat[xmin:xmax,ymin:ymax]
lon = lon[xmin:xmax,ymin:ymax]
u   = u[xmin:xmax,ymin:ymax]
v   = v[xmin:xmax,ymin:ymax]
speed = speed[xmin:xmax,ymin:ymax]
print 'trim', datetime.now() - timer

plt.figure(figsize=(20,20))
timer = datetime.now()
m = Basemap(resolution='i',projection='cyl',\
            llcrnrlon=bot_left_lon,llcrnrlat=bot_left_lat,\
            urcrnrlon=top_right_lon,urcrnrlat=top_right_lat,)
m.drawcoastlines(linewidth=2,color='b')
print 'map',datetime.now()-timer
            
timer = datetime.now()
x,y = m(lon,lat)
print 'convert',datetime.now()-timer


timer = datetime.now()
BASE = '/uufs/chpc.utah.edu/common/home/u0553130/'
# Draw other shape files (selected lakes, Utah roads, county lines)
m.readshapefile(BASE+'shape_files/tl_2015_UtahLake_areawater/tl_2015_49049_areawater','lakes', linewidth=1.5)
m.readshapefile(BASE+'shape_files/tl_2015_UtahRoads_prisecroads/tl_2015_49_prisecroads','roads', linewidth=.5)
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
                    
# Location of TDWR and other observing stations for reference
m.scatter(-111.93,40.9669, s=75, c='w',zorder=40)               # TDWR
m.scatter(-112.01448,40.71152, s=75, c='b',zorder=40)           # NAA
m.scatter(-111.93072,40.95733, s=75, c='darkorange',zorder=40)  # O3S02                        
m.scatter(-111.828211,40.766573, s=75, c='r',zorder=40)         # MTMET                       
m.scatter(-111.8717,40.7335, s=75, c='darkgreen',zorder=40)     # QHW               
m.scatter(-111.96503,40.77069, s=75, c='w',zorder=40)           # SLC               
m.scatter(-112.34551,40.89068 , s=75, c='w',zorder=40)          # GSLBY   

name = request_date.strftime('%d %b %Y    %H:%M')
plt.title(name)

print 'barbs',datetime.now()-timer
plt.show()


