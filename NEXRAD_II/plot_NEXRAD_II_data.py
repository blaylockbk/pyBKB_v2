### Brian Blaylock

## View NEXRAD Level II Data

## Download from Amazon Web Service
## https://s3.amazonaws.com/noaa-nexrad-level2/index.html

## Use the Local Version of python on Meso3 or Meso4: /usr/local/bin/python

# Download URL Example: https://noaa-nexrad-level2.s3.amazonaws.com/2016/08/05/KCBX/KCBX20160805_205859_V06

# Boise: KCBX

import os
import numpy as np
from numpy import ma
from datetime import datetime
import matplotlib.pyplot as plt
import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB')  #for running on CHPC boxes
sys.path.append('B:\pyBKB')  # local path for testing on my machine 

from BB_MesoWest.MesoWest_stations_radius import *
from MetPy_BB.io.nexrad import Level2File
from MetPy_BB.plots import ctables



from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

from pyproj import Geod #this is used to convert range/azimuth to lat/lon
from mpl_toolkits.basemap import Basemap


SAVEDIR = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/Pioneer_Fire/NEXRAD_II/'
if not os.path.exists(SAVEDIR):
        os.makedirs(SAVEDIR)
    

#### Some Settings
radar = 'KCBX'
date = datetime.datetime(2016,8,5,20,58,59)

#file name example: KCBX20160805_205859_V06
filename = '%s%04d%02d%02d_%02d%02d%02d_V06' % (radar, date.year,date.month,date.day,date.hour,date.minute,date.second)

f = Level2File(filename)

rLAT = f.sweeps[0][0][1].lat
rLON = f.sweeps[0][0][1].lon
rDT = f.dt # this is in local time



## Create Figure and plot the background image outside the loop.
## Then, in each loop, we'll remove the radar data after we plotted and saved.

### ---------------- Create Basemap -------------------------
fig = plt.figure(1,figsize=[8,8])
ax  = fig.add_subplot(111)
top_right_lat = rLAT+1.25
top_right_lon = rLON+1.25
bot_left_lat = rLAT-1
bot_left_lon = rLON-1

## Map in cylindrical projection
m = Basemap(resolution='i',projection='cyl',\
    llcrnrlon=bot_left_lon,llcrnrlat=bot_left_lat,\
    urcrnrlon=top_right_lon,urcrnrlat=top_right_lat,)
maps = [
    'ESRI_Imagery_World_2D',    # 0
    'ESRI_StreetMap_World_2D',  # 1
    'NatGeo_World_Map',         # 2
    'NGS_Topo_US_2D',           # 3
    'Ocean_Basemap',            # 4
    'USA_Topo_Maps',            # 5
    'World_Imagery',            # 6
    'World_Physical_Map',       # 7
    'World_Shaded_Relief',      # 8
    'World_Street_Map',         # 9
    'World_Terrain_Base',       # 10
    'World_Topo_Map'            # 11
    ]
     
## Instead of using blank background, get a high resolution image from ESRI
m.arcgisimage(service=maps[2], xpixels = 1000, verbose= True)
m.drawcoastlines(zorder=1000)
m.drawstates(zorder=1000)
m.drawcounties(linewidth=.5,zorder=1000)


### ---------------- Add Fire Perimeter -------------------------             
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
ax.add_collection(PatchCollection(patches, facecolor= 'indianred', alpha=.75, edgecolor='k', linewidths=1.5, zorder=2))

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


### The IRAWS stations moved, so if the mesowest stations return these, then use these lat/lons...
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

print "finished plotting basemap"


### ---------------- Add MesoWest Surface Winds -------------------------
mesowest_time = date.strftime('%Y%m%d%H%M')
# grab most recent observations 15 mins before and after the radar scan. Grab stations within a 150 mile radius of radar.
a = get_mesowest_radius_winds(mesowest_time,'15,15',radius=str(rLAT)+','+str(rLON)+','+'150')

# (There are some funky IRAWS stations stashed in the parking lot. Don't plot these)
raws_lat = 43.565
raws_idx = np.argwhere(a['LAT']==43.565)
a['WIND_SPEED'][np.argwhere(a['LAT']==43.565)] = np.nan

# Add MesoWest wind barbs
u,v = wind_spddir_to_uv(a['WIND_SPEED'],a['WIND_DIR'])
m.barbs(a['LON'],a['LAT'],u,v,
        length=5.5,                
        barb_increments=dict(half=2.5, full=5, flag=25),
        sizes=dict(spacing=0.15, height=0.3, emptybarb=.1),zorder=500)            


### ---------------- Add Points of Interest --------- -------------------------
# NEXRAD location
m.scatter(rLON,rLAT, s=75, c='w',zorder=500)  


### ----------- Loop through each sweep (scan elevation) ---------------------
# Pull data out of the file
# sweep reprsents the scan elevation angle (Note: sweep number is not in order of lowest to highest scan)
# to get the elevation angle try: f.sweeps[x][0][0].el_angle where x is your sweep index

s = range(0,21) # a list of sweeps
#s = [1]
for sweep in s:
    elv_angle = f.sweeps[sweep][0][0].el_angle
     

    # First item in ray is header, which has azimuth angle
    az = np.array([ray[0].az_angle for ray in f.sweeps[sweep]])
    
    
    # 5th item is a dict mapping a var name (byte string) to a tuple
    # of (header, data array)
    ref_hdr = f.sweeps[sweep][0][4][b'REF'][0]
    ref_range = np.arange(ref_hdr.num_gates) * ref_hdr.gate_width + ref_hdr.first_gate
    ref = np.array([ray[4][b'REF'][1] for ray in f.sweeps[sweep]])
    try:
        vel_hdr = f.sweeps[sweep][0][4][b'VEL'][0]
        vel_range = (np.arange(vel_hdr.num_gates + 1) - 0.5) * vel_hdr.gate_width + vel_hdr.first_gate
        vel = np.array([ray[4][b'VEL'][1] for ray in f.sweeps[sweep]])
    except:
        pass
    try:
        sw_hdr = f.sweeps[sweep][0][4][b'SW'][0]
        sw_range = (np.arange(sw_hdr.num_gates + 1) - 0.5) * sw_hdr.gate_width + sw_hdr.first_gate
        sw = np.array([ray[4][b'SW'][1] for ray in f.sweeps[sweep]])
    except:
        pass
    try:
        rho_hdr = f.sweeps[sweep][0][4][b'RHO'][0]
        rho_range = (np.arange(rho_hdr.num_gates + 1) - 0.5) * rho_hdr.gate_width + rho_hdr.first_gate
        rho = np.array([ray[4][b'RHO'][1] for ray in f.sweeps[sweep]])
    except:
        pass
    try:
        phi_hdr = f.sweeps[sweep][0][4][b'PHI'][0]
        phi_range = (np.arange(phi_hdr.num_gates + 1) - 0.5) * phi_hdr.gate_width + phi_hdr.first_gate
        phi = np.array([ray[4][b'PHI'][1] for ray in f.sweeps[sweep]])
    except:
        pass
    try:
        zdr_hdr = f.sweeps[sweep][0][4][b'ZDR'][0]
        zdr_range = (np.arange(zdr_hdr.num_gates + 1) - 0.5) * zdr_hdr.gate_width + zdr_hdr.first_gate
        zdr = np.array([ray[4][b'ZDR'][1] for ray in f.sweeps[sweep]])                        
    except:
        pass
    #fig, axes = plt.subplots(1, 2, figsize=(15, 8))
    
    if len(f.sweeps[sweep][0][4])==4:
        get_these = (ref,rho,phi,zdr)
        get_these_r = (ref_range,rho_range,phi_range,zdr_range)
        fignum = [1,2,3,4]
        names = ('REF','RHO','PHI','ZDR')
    elif len(f.sweeps[sweep][0][4])==3:
        get_these = (ref,sw,vel)
        get_these_r = (ref_range,sw_range,vel_range,)
        fignum = [1,2,3]
        names = ('REF','SW','VEL')
    else:
        get_these = (ref,rho,phi,zdr,sw,vel)
        get_these_r = (ref_range,rho_range,phi_range,zdr_range,sw_range,vel_range)
        fignum = [1,2,3,4,5,6]
        names = ('REF','RHO','PHI','ZDR','SW','VEL')
   
    
    #for var_data, var_range, ax in zip((ref, rho), (ref_range, rho_range), axes):

    for var_data, var_range, num, name in zip(get_these, get_these_r, fignum, names):
           
        print name
           
        ax = fig.add_subplot(111)  # drawing axes
        # Turn into an array, then mask
        data = ma.array(var_data)
        data[np.isnan(data)] = ma.masked
    
        #rngs = np.array([ray[0].rad_length for ray in f.sweeps[sweep]]) 
        rng = np.linspace(0, var_range[-1], data.shape[-1] + 1)
        print len(rng)
    
        # Convert az, range to a lat/lon
        g = Geod(ellps='clrk66') # This is the type of ellipse the earth is projected on. 
                                 # There are other types of ellipses you can use,
                                 # but the differences will be small
        center_lat = np.ones([len(az),len(rng)])*rLAT    
        center_lon = np.ones([len(az),len(rng)])*rLON
        az2D = np.ones_like(center_lat)*az[:,None]
        rng2D = np.ones_like(center_lat)*np.transpose(rng[:,None])*1000
        lon,lat,back=g.fwd(center_lon,center_lat,az2D,rng2D)
    
    
        # Convert az,range to x,y
        xlocs = var_range * np.sin(np.deg2rad(az[:, np.newaxis]))
        ylocs = var_range * np.cos(np.deg2rad(az[:, np.newaxis]))
    
        # Plot the data
        cmap = ctables.registry.get_colortable('viridis')
        
        #p = ax.pcolormesh(xlocs, ylocs, data, cmap=cmap)
        if name=='VEL':                
            p = m.pcolormesh(lon,lat,data,cmap='BrBG_r',vmax=10,vmin=-10,zorder=300)
        else:
            p = m.pcolormesh(lon,lat,data,cmap=cmap,zorder=300)
        #m.set_aspect('equal', 'datalim')
        #ax.set_xlim(-40, 20)
        #ax.set_ylim(-30, 30)
        
        cb = plt.colorbar(p,orientation='horizontal',shrink=.8,pad=.01,
                       label='??')

               
    
        
    
        plt.title('%s\n%s_ElvAngle_%.2f.png'%(filename,name,elv_angle))
        plt.savefig(SAVEDIR+'%s_ElvAngle_%.2f.png'%(name,elv_angle),bbox_inches='tight')
        print 'saved', name
        cb.remove()         # need to remove the colorbar before removing the pcolormesh    
        p.remove()
            

#plt.show()