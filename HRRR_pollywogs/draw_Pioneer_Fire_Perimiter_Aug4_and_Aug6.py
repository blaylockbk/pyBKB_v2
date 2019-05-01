## Brian Blaylock
## 12 October 2016

# Explore a shapefire 

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



"""
Shapefile Description: http://rmgsc.cr.usgs.gov/outgoing/GeoMAC/historic_fire_data/perimeters_dd83_METADATA.htm
OBJECTID: internal feature number
GISACRES: GIS calculated acres within the fire perimeter
AGENCY: Administravtive agency at the fire's point of origin
COMMENTS: Wildland fire perimeter-related comments
FIRECODE: Firecode assigned to the incident
FIREYEAR: Calendar year fire started
COMPLEXNAME: parent complex name
ACTIVE: Yes or No
INCIDENTNAME: name assigned to an incident
PERIMETERDATETIME (PERDATTIME): The date and time that the fire perimeter was collected (mapped). 
                   Date should follow NWCG data standard for Date and time should 
                   follow NWCG standard for Time of Day, using 24 hour clock, 
                   YYYYMMDDhhmmss.ss (include seconds if available). Time zone is 
                   usually the local time zone where the perimeter was collected.
DATECURRENT (DATECRNT): The last edit, update, of this GIS record.

"""


SAVEDIR = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/Pioneer_Fire/'
if not os.path.exists(SAVEDIR):
        os.makedirs(SAVEDIR)





fig = plt.figure(1, figsize=[5,2.5])
ax  = fig.add_subplot(111)

## Draw Background basemap
bot_left_lat = 43.8876
bot_left_lon = -115.823
top_right_lat = 44.0951
top_right_lon = -115.433

## Map in cylindrical projection (data points may apear skewed)
m = Basemap(resolution='i',projection='cyl',\
    llcrnrlon=bot_left_lon,llcrnrlat=bot_left_lat,\
    urcrnrlon=top_right_lon,urcrnrlat=top_right_lat,)
m.drawcoastlines()
m.drawcountries()
m.drawcounties(linewidth=2)
m.drawstates(linewidth=5)


# Brackground image
m.arcgisimage(service='NatGeo_World_Map', xpixels = 1200, dpi=1000, verbose= True)
###############################################################################


# Fire perimiter
perimiter = '160816'
p4 = m.readshapefile('/uufs/chpc.utah.edu/common/home/u0553130/fire_shape/perim_'+perimiter,'perim',drawbounds=False)


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



###############################################################################

# Plot station locations
lats = [44.027889,43.960083] 
lons = [-115.803917,-115.687]
stnid = ['HFNC1','TT029']
elev = [6294,8142] # feet

m.scatter(lons,lats,color='darkorange',s=60,edgecolor='k',linewidth='.5',zorder=500)
plt.text(lons[0],lats[0],stnid[0],zorder=500,fontdict={'weight':'bold','color':'oldlace','size':9},
            path_effects=[PathEffects.withStroke(linewidth=1,foreground="k")])
plt.text(lons[1],lats[1],stnid[1],zorder=500,fontdict={'weight':'bold','color':'oldlace','size':9},
         path_effects=[PathEffects.withStroke(linewidth=1,foreground="k")])

"""
day = range(0,17)
for d in day:
    for info,shape in zip(m.perim_info,m.perim):
        if info['FIRENAME']== 'PIONEER' and info['PERDATTIME']==[2016,8,d] and np.shape(shape)[0]>6000:
            print "<<<<<<<<<<",np.shape(shape)        
            print info['FIRENAME'],info['PERDATTIME'],info['DATECRNT'],info['SHAPENUM'] 
            #for i in info:
                #print i,info[i]
            
            print ""

"""
plt.savefig(SAVEDIR+'Pioneer_fire_perimeter_Aug4_and_Aug6_2016',bbox_inches="tight",dpi=500)





