## Not perfect, but a good place to start looking at your model levels

# Brian Blaylock
# 8 March 2016

# Plot model levels

# 1) Levels at one point to show vertically stacking
# 2) Cross Section of levels to show over terrain



#from netCDF4 import Dataset  # we dont have this library. use scipy instead
from scipy.io import netcdf
import matplotlib as mpl
#matplotlib.use('Agg')		#required for the CRON job. Says, "do not open plot in a window"??
import matplotlib.pyplot as plt
import numpy as np
import os

label_size = 12
mpl.rcParams['xtick.labelsize'] = label_size 
mpl.rcParams['ytick.labelsize'] = label_size 


#Other directories
HOMEBASE    = '/uufs/chpc.utah.edu/common/home/u0553130/'
FIG_DIR = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/MS/ModelLevels/'
if not os.path.exists(FIG_DIR):
        os.makedirs(FIG_DIR)


# Open File
wrf_version = 'defaultlake'
RUN='/uufs/chpc.utah.edu/common/home/horel-group4/model/bblaylock/WRF3.7_'+wrf_version+'/DATA/'

#wrf_version = 'spinup'
#RUN='/uufs/chpc.utah.edu/common/home/horel-group4/model/bblaylock/WRF3.7_'+wrf_version+'/DATA/FULL_RUN_June14-19/'

FILE = 'wrfout_d02_2015-06-18_00:00:00'

print 'File Name: ', RUN+FILE


### Get Domain 2 WPS directory
full_file = RUN+FILE

full_file = 'wrfout'

nc = netcdf.netcdf_file(full_file,'r')
HGT = nc.variables['HGT'][0,:,:].copy()
LAT = nc.variables['XLAT'][0].copy()
LON = nc.variables['XLONG'][0].copy()
PH = nc.variables['PH'][0].copy()
PHB = nc.variables['PHB'][0].copy()

phi = (PH+PHB)/9.81  # Total geopotential

# Levels at one point (KSLC)
pointLevs = phi[:,225,229]

# Lines
plt.figure(1,figsize=[2,5])
for i in pointLevs:
    plt.axhline(i)
plt.xticks([])
plt.yticks([pointLevs.min(),5000,10000,15000,20000,25000])
plt.ylabel('Geopotential Height of each eta level')
plt.ylim([pointLevs.min(),pointLevs.max()])
plt.title('%s Model Levels' % len(pointLevs))



# Indexes of a cross section.
lat = np.arange(229,230)
lon = np.arange(150,300)



num_levs = len(pointLevs)

# W-E cross section (KSLC)
plt.figure(2,figsize=[5,8])
WEcross = phi[:,lat,lon]
levels = (np.arange(0,num_levs) * np.ones([np.shape(WEcross)[1],num_levs])).T
LONcross = LON[lat,lon]*np.ones_like(WEcross)
eta = plt.contour(LONcross,WEcross,levels,levels=np.arange(0,num_levs),colors='k',linewidths=.7)
etaf = plt.contourf(LONcross,WEcross,levels,cmap='Paired',levels=np.arange(0,num_levs))


plt.ylabel('Geopotential Height [m]',fontsize=20)
plt.xlabel('Longitude',fontsize=20)


yticks = WEcross.min()
yticks = np.append(yticks, WEcross.max())
yticks = np.append(yticks, np.arange(np.floor(WEcross.min()/1000)*3000,WEcross.max(),2000))

plt.yticks(yticks)
plt.xlim([LONcross.min(),LONcross.max()])
plt.ylim([0,WEcross.max()])

cb = plt.colorbar(shrink=.95,pad=.02,ticks=np.arange(0,num_levs+1,4))
cb.ax.set_ylabel('Model Level',fontsize=15)
cb.ax.tick_params(labelsize=15) 
cb.add_lines(eta)
cb.ax.set_yticklabels(np.arange(1,num_levs+1,4))

plt.fill_between(LON[lat,lon],0,HGT[lat,lon],color="black")


# N-S cross section (KSLC)
NScross = phi[:,10:20,225]


plt.savefig(FIG_DIR+str(num_levs)+'.png',bbox_inches="tight",dpi=300)
plt.show()
