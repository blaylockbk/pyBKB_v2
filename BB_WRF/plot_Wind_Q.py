# Brian Blaylock
#
# Plotting WRF netCDF output
# Parts and Pieces of this code is from Luke Madaus (University of Washington)


import sys,getopt
#from netCDF4 import Dataset  # use scipy instead
from scipy.io import netcdf
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime, timedelta
from mpl_toolkits.basemap import Basemap
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.axes_grid import make_axes_locatable
import matplotlib.axes as maxes
#import mayavi.mlab as mlab #Used for 3d Plotting
import matplotlib.colors as mcolors
from functions_domains_models import *

# Running Script example:
# $ python my_WRF_map.py wrfout_d0x_YYYY-MM-DD_HH:MM:SS

# list of files


#directory = '/uufs/chpc.utah.edu/common/home/horel-group4/model/bblaylock/WRF3.7_defaultlake/DATA/'
directory = '/uufs/chpc.utah.edu/common/home/horel-group4/model/bblaylock/WRF3.7_spinup/DATA/FULL_RUN_June14-19/'
#directory = '/uufs/chpc.utah.edu/common/home/horel-group4/model/bblaylock/WRF3.7_spinup_41levs/WRFV3/WRFV3/test/em_real/'


out_dir = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/MS/planeview_wind/'
if not os.path.exists(out_dir):
    os.makedirs(out_dir)


spat= 'auxhist23_d02_2015-06-18_00:00:00'
spat = 'auxhist23_d02_2015-06-14_00:00:00'

for output_file in os.listdir(directory):
    if output_file[0:21]=='wrfout_d02_2015-06-18' or output_file[0:21]=='wrfout_d02_2015-06-19': # get the file name of a TDWR file
        print output_file    
        # Open file in a netCDF reader   

        wrf_file_name = output_file #NOTE: the .nc files are named differently in a windows system
        print 'opening', directory+wrf_file_name
        nc         = netcdf.netcdf_file(directory+wrf_file_name,'r')
        nc_spatial = netcdf.netcdf_file(directory+spat,'r')
        
        
        
        #-------------------------------------------
        # Creat the basemap only once per domain. (This significantly speeds up the plotting speed)
        #-------------------------------------------
        
        # x_dim and y_dim are the x and y dimensions of the model
        # domain in gridpoints
        x_dim = nc.dimensions['west_east']
        y_dim = nc.dimensions['south_north']
        
        # Get the grid spacing
        dx = float(nc.DX)
        dy = float(nc.DY)
        
        width_meters = dx * (x_dim - 1)		#Domain Width
        height_meters = dy * (y_dim - 1)	#Domain Height
        
        """ #Full map
        cen_lat = float(nc.CEN_LAT)
        cen_lon = float(nc.CEN_LON)
        truelat1 = float(nc.TRUELAT1)
        truelat2 = float(nc.TRUELAT2)
        standlon = float(nc.STAND_LON)
        
        # Draw the base map behind it with the lats and
        # lons calculated earlier
        m = Basemap(resolution='i',projection='lcc',\
            width=width_meters,height=height_meters,\
            lat_0=cen_lat,lon_0=cen_lon,lat_1=truelat1,\
            lat_2=truelat2)
        """
        domain = get_domain('salt_lake_valley')
        top_right_lat = domain['top_right_lat']
        top_right_lon = domain['top_right_lon']
        bot_left_lat = domain['bot_left_lat']
        bot_left_lon = domain['bot_left_lon']
    
        ## Map in cylindrical projection (data points may apear skewed)
        m = Basemap(resolution='i',projection='cyl',\
            llcrnrlon=bot_left_lon,llcrnrlat=bot_left_lat,\
            urcrnrlon=top_right_lon,urcrnrlat=top_right_lat,)
         
         
        # This sets the standard grid point structure at full resolution
        #	Converts WRF lat and long to the maps x an y coordinate
        XLONG = nc_spatial.variables['XLONG'][0]
        XLAT  = nc_spatial.variables['XLAT'][0]
        x,y = m(XLONG,XLAT)    
        
        # Define transparent colormaps    
        colors = [(1,0,0,c) for c in np.linspace(0,1,100)]
        cmapred = mcolors.LinearSegmentedColormap.from_list('mycmap', colors, N=8)
        colors = [(0,0,1,c) for c in np.linspace(0,1,100)]
        cmapblue = mcolors.LinearSegmentedColormap.from_list('mycmap', colors, N=8)
        
        colors = [(0,0,0,c) for c in np.linspace(0,1,100)]
        cmapgrey = mcolors.LinearSegmentedColormap.from_list('mycmap', colors, N=4)    
        
        
        for t in np.arange(0,int(np.shape(nc.variables['Times'])[0])):
            plt.cla()
            plt.clf()
            plt.close()        
            
            # Grab these variables for now
            #landmask =  nc.variables['LANDMASK']				# HRRR metgrid landmask
            
            time = ''.join(nc.variables['Times'][t])
            time_dt = datetime.strptime(time,'%Y-%m-%d_%H:%M:%S')
            time_str= datetime.strftime(time_dt,'%Y-%m-%d %H:%M:%S UTC')
            time_str_local=datetime.strftime(time_dt-timedelta(hours=6),'%Y-%m-%d %H:%M:%S MDT')
            time_file=datetime.strftime(time_dt,'%Y%m%d%H%M%S')
            HGT = nc_spatial.variables['HGT'][0,:,:] #topography
            landmask = nc_spatial.variables['LANDMASK'][0,:,:]
            
            U10 = nc.variables['U10'][t]
            V10 = nc.variables['V10'][t]
            Q2 = nc.variables['Q2'][t]*1000
            
            
            # This sets a thinn-ed out grid point structure for plotting
            # wind barbs at the interval specified in "thin"
            #thin = 5 
            #x_th,y_th = m(XLONG[0,::thin,::thin],XLAT[0,::thin,::thin])
            	
            # Set universal figure margins
            width = 10
            height = 8
            
            print 'Plotting',time_str
            plt.figure(t+1,figsize=(width,height))
            
            """        
            plt.rc("figure.subplot", left = .001)	#gets rid of white space in plot
            plt.rc("figure.subplot", right = .999)
            plt.rc("figure.subplot", bottom = .001)
            plt.rc("figure.subplot", top = .999)
                           
            F = plt.gcf()  # Gets the current figure
            """        
            
            m.drawstates(color='k', linewidth=1.25)
            #m.drawcoastlines(color='k')
            #m.drawcountries(color='k', linewidth=1.25)
            
        ######################################################
            
            masked_V10 = np.ma.masked_array(V10,HGT>1600)            
            masked_U10 = np.ma.masked_array(U10,HGT>1600)
            masked_Q2  = np.ma.masked_array(Q2, HGT>1600)
            
            plt.contourf(x,y,HGT,cmap='binary')            
                        
            #plt.pcolormesh(x,y,plume,cmap='PuOr', vmin=0,vmax=.01)
            #plt.pcolormesh(x,y,U10,cmap=cmapred,vmax=8,vmin=0)
            
            """
            # pcolormesh            
            plt.pcolormesh(x,y,masked_V10,cmap='BrBG',vmax=8,vmin=-8)
            cbar_loc = plt.colorbar(shrink=.8,pad=.01,ticks= np.arange(-8,8.1,1),extend='both')
            cbar_loc.ax.set_ylabel('Wind Speed (m/s)')
            
            """
            # contourf
            plt.contourf(x,y,masked_V10,cmap='BrBG',levels=np.arange(-8,8.1,.5),extend='both')
            cbar_loc = plt.colorbar(shrink=.8,pad=.01,ticks= np.arange(-8,8.1,1))
            cbar_loc.ax.set_ylabel('10-m V Wind (m/s)')
            
            
            plt.contour(x,y,landmask, [0,1], linewidths=1, colors="b")
            #plt.contour(x,y,HGT)
            #plt.contourf(x,y,HGT,cmap=cmapgrey) # transparent greay if plotted on top
            
            plt.barbs(x[::3,::3],y[::3,::3],masked_U10[::3,::3],masked_V10[::3,::3],
                      length=6,
                      barb_increments=dict(half=1, full=2, flag=10),
                      sizes=dict(emptybarb=.1))  
                      
            plt.contour(x,y,masked_Q2,linewidths=2,levels=[1,2,3,4,5,6,7,8,9,10],cmap='PiYG')
            cbar_WV = plt.colorbar(orientation='horizontal',shrink=.8,pad=.01,)
            cbar_WV.ax.set_xlabel('2-m Water Vapor (g/kg)')
            
            
                      
            
            xs,ys = m(-111.97,40.78) #buffr sounding coordinates
            #plt.scatter(xs,ys, s=70, c='w')
            plt.title(time_str+'\n'+time_str_local, bbox=dict(facecolor='white', alpha=0.65),\
        			x=0.5,y=1.05,weight = 'demibold',style='oblique', \
        			stretch='normal', family='sans-serif')            
            plt.savefig(out_dir+'contour_V10_barbs_'+time_file+'.png',bbox_inches="tight")
            print 'Saved',time_str
    
            #plt.show()
            
        
