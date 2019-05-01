### Brian Blaylock
### 12 August 2016


# Need more help with shapefiles??
# http://basemaptutorial.readthedocs.io/en/latest/shapefile.html


# Plot fires shape file with MesoWest stations

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import matplotlib.patheffects as PathEffects
from datetime import datetime
import os
import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB')  #for running on CHPC boxes
sys.path.append('B:\pyBKB')  # local path for testing on my machine 

from BB_cmap import LukeM_colormap
from BB_MesoWest.MesoWest_stations_radius import get_mesowest_radius_stations, get_mesowest_stations
import wind_calcs

import h5py

def cut_data(lat,lon,bl_lat,tr_lat,bl_lon,tr_lon):
    '''    
    Cut down full HRRR data for domain for faster plotting.
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

## Get 10-m winds and reflectivity from the HRRR for 


#------------------------------------------------------------------------------

fig = plt.figure(1, figsize=[8,8])
ax  = fig.add_subplot(111)

## Draw Background basemap
bot_left_lat = 43.565
bot_left_lon = -116.276
top_right_lat = 44.222+.05
top_right_lon = -115.29-.05

## Map in cylindrical projection (data points may apear skewed)
m = Basemap(resolution='i',projection='cyl',\
    llcrnrlon=bot_left_lon,llcrnrlat=bot_left_lat,\
    urcrnrlon=top_right_lon,urcrnrlat=top_right_lat,)
m.drawcoastlines()
m.drawcountries()
m.drawcounties(linewidth=2)
m.drawstates(linewidth=5)

# Brackground image
m.arcgisimage(service='NatGeo_World_Map', xpixels = 1000, dpi=100, verbose= True)

# Fire perimiter
perimiter = '160816'
p4 = m.readshapefile('/uufs/chpc.utah.edu/common/home/u0553130/fire_shape/perim_'+perimiter,'perim',drawbounds=False)

# fire August 6th, 2016
patches   = []
for info, shape in zip(m.perim_info, m.perim):
    #if info['FIRENAME'] == 'PIONEER' and info['SHAPENUM']==1772:
    if info['FIRENAME']== 'PIONEER' and info['PERDATTIME']==[2016,8,6] and np.shape(shape)[0]>6000 and info['SHAPENUM']==1914:
        x, y = zip(*shape) 
        print info['FIRENAME'],info['SHAPENUM'],info['PERDATTIME'],info['DATECRNT']
        print 'GIS Acres', info['GISACRES']
        #m.plot(x, y, marker=None,color=colors[colorI],linewidth=lw)
        patches.append(Polygon(np.array(shape), True) )
        print ""
ax.add_collection(PatchCollection(patches, facecolor= 'indianred', alpha=.75, edgecolor='k', linewidths=1.5, zorder=1))

# fire August 4th 2016
patches2   = []
for info, shape in zip(m.perim_info, m.perim):
    #if info['FIRENAME'] == 'PIONEER' and info['SHAPENUM']==1772:
    if info['FIRENAME']== 'PIONEER' and info['PERDATTIME']==[2016,8,4] and np.shape(shape)[0]>6000 and info['SHAPENUM']==1860:
        x, y = zip(*shape) 
        print info['FIRENAME'],info['SHAPENUM'],info['PERDATTIME'],info['DATECRNT']
        print 'GIS Acres', info['GISACRES']
        #m.plot(x, y, marker=None,color=colors[colorI],linewidth=lw)
        patches2.append(Polygon(np.array(shape), True) )
        print ""
ax.add_collection(PatchCollection(patches2, facecolor= 'maroon', alpha=.55, edgecolor='k', linewidths=1, zorder=2))


# Plot station locations
lats = [44.027889,43.960083] 
lons = [-115.803917,-115.687]
stnid = ['HFNC1','TT029']
elev = [6294,8142] # feet

m.scatter(lons,lats,color='darkorange',edgecolor='k',linewidth='1',s=150,zorder=500)
plt.text(lons[0],lats[0],stnid[0],zorder=500,fontdict={'weight':'bold','color':'oldlace','size':12},
            path_effects=[PathEffects.withStroke(linewidth=1,foreground="k")])
plt.text(lons[1],lats[1],stnid[1],zorder=500,fontdict={'weight':'bold','color':'oldlace','size':12},
            path_effects=[PathEffects.withStroke(linewidth=1,foreground="k")])

#m.scatter(-116.2146,43.6187,s=250) # Boise
#plt.text(-116.2146,43.6187,'Boise') # Boise
#m.scatter(-116.,44.1,color='dodgerblue',s=150) # sounding location\ 19 August 2016 1400 UTC
#plt.text(-116.,44.1,'sounding 08192016') # sounding location\ 19 August 2016 1400 UTC
print "finished plotting base"
#------------------------------------------------------------------------------
plotted_cb = False # colorbar plotted flag

fig.set_size_inches(8,10)

        
ah = range(6,24)


SAVEDIR = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/Pioneer_Fire/UU2DVAR_HighWind/'    

for analysis_h in ah:
     
    try:
        UU2DVAR_dir = '/uufs/chpc.utah.edu/common/home/horel-group/archive/20160805/uu2dvar/'
        UU2DVAR_file = '20160805_2p5km.h5' 
    
        
        save_name= '10m_Analysis_%02d' % (analysis_h)
            
        valid_time = '%02d:00' % (analysis_h)
    
        print "working on", save_name    
        
        hd = h5py.File(UU2DVAR_dir+UU2DVAR_file)
        
        UU_lat = hd['latitude'].value[:]
        UU_lon = hd['longitude'].value[:]
        UU_u   = hd['z%02d'%analysis_h]['anl_10m_uwnd'].value[:]  # m/s
        UU_v   = hd['z%02d'%analysis_h]['anl_10m_vwnd'].value[:]    # m/s
        UU_speed = hd['z%02d'%analysis_h]['anl_10m_wspd'].value[:]
        
        xmin,xmax,ymin,ymax = cut_data(UU_lat,UU_lon,bot_left_lat,top_right_lat,bot_left_lon,top_right_lon)
        UU_lat = UU_lat[xmin:xmax,ymin:ymax]
        UU_lon = UU_lon[xmin:xmax,ymin:ymax]
        UU_u   = UU_u[xmin:xmax,ymin:ymax]
        UU_v   = UU_v[xmin:xmax,ymin:ymax]
        UU_speed   = UU_speed[xmin:xmax,ymin:ymax]
            
        
        ## Plot contours of wind speed greater than these thresholds
        levels = np.array([5,10,15,20,25])
        
        #color contour    
    
    
           
        CC = m.contourf(UU_lon,UU_lat,UU_speed,
                     levels=levels,
                     colors=['whitesmoke','gold','darkorange','red'],
                     alpha=.6,
                     extend='max')                    
    
           
           
        if plotted_cb == False:
            cbar = plt.colorbar(CC, orientation='horizontal',shrink=.8,pad=.08)
            plotted_cb = True
            
        plt.xlabel(r'Half Barb = 2.5 ms$^-$$^1$  Full Barb = 5 ms$^-$$^1$')
               
        
        # plot HRRR 10-m winds
        WB = m.barbs(UU_lon,UU_lat,UU_u,UU_v,
                barb_increments=dict(half=2.5, full=5, flag=25),length=5.25)
        
        
        plt.title('Pioneer Fire\nUU2DVAR 10-m winds Analysis valid 5 August 2016 %s UTC' % (valid_time)) 
        plt.savefig(SAVEDIR+save_name+'.png',bbox_inches='tight')
    
        print "saved",SAVEDIR+save_name
        print ""
    
        WB[0].remove()
        WB[1].remove()    
        for cc in CC.collections:
            cc.remove()
    except:
        pass
    