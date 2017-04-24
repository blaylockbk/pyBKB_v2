# Brian Blaylock
#
# Plotting WRF netCDF output
# Plots a map view of wind barbs and color shading of vertical velocity for a given model level
# Uses the stagger_to_mass.py module to convert the U and V variables to mass point values by averaging.


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
from functions import stagger_to_mass

# Running Script example:
# $ python my_WRF_map.py wrfout_d0x_YYYY-MM-DD_HH:MM:SS

# list of files


#directory = '/uufs/chpc.utah.edu/common/home/horel-group4/model/bblaylock/WRF3.7_defaultlake/DATA/'
directory = '/uufs/chpc.utah.edu/common/home/horel-group4/model/bblaylock/WRF3.7_spinup/DATA/FULL_RUN_June14-19/'
#directory = '/uufs/chpc.utah.edu/common/home/horel-group4/model/bblaylock/WRF3.7_spinup_41levs/WRFV3/WRFV3/test/em_real/'

model_level = 7
#model_level = 'surface'

out_dir = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/MS/planeview_wind/w_wind/model_level_'+str(model_level)+'/'
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
        top_right_lat = domain['top_right_lat']+.1
        top_right_lon = domain['top_right_lon']-.1
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
            
            sinalpha = nc.variables['SINALPHA'][t]
            cosalpha = nc.variables['COSALPHA'][t]
            ## Convert grid relative winds to earth relative winds
            U10 = U10*cosalpha - V10*sinalpha
            V10 = V10*cosalpha + U10*sinalpha
            ## In reality, this has such a small effect on our small domain. 
            ## In fact in our wind barb convention there is no change at all
            ## because the change in angle or speed is so small.
            
            

            # Vertical Velocity on model level 7
            if model_level == 'surface':
                W = nc.variables['W'][t][7]
                U = nc.variables['U'][t][7]
                V = nc.variables['V'][t][7]
                # What model level is model level 8??
                PH = nc.variables['PH'][t][7]
                PHB = nc.variables['PHB'][t][7]   
                phi = ( PH + PHB ) / 9.81
            else:
                W = nc.variables['W'][t][model_level]
                U = nc.variables['U'][t][model_level]
                V = nc.variables['V'][t][model_level]
                # What model level is model level 8??
                PH = nc.variables['PH'][t][model_level]
                PHB = nc.variables['PHB'][t][model_level]   
                phi = ( PH + PHB ) / 9.81
                
            XLAT_U = nc.variables['XLAT_U'][t]           
            XLAT_V = nc.variables['XLAT_V'][t]
            XLONG_U = nc.variables['XLONG_U'][t]           
            XLONG_V = nc.variables['XLONG_V'][t]
            

            
#==============================================================================
            # Really need to convert U and V to mass point to plot barb  
            # Convert U and V wind, lat, and lon, to mass point
            # Take two points and average them using the functions in stagger_to_mass.py
            
            U_masspoint = stagger_to_mass.Ustagger_to_mass(U)
            V_masspoint = stagger_to_mass.Vstagger_to_mass(V)
            Ulat_masspoint = stagger_to_mass.Ustagger_to_mass(XLAT_U)
            Ulon_masspoint = stagger_to_mass.Ustagger_to_mass(XLONG_U)            
            Vlat_masspoint = stagger_to_mass.Vstagger_to_mass(XLAT_V)
            Vlon_masspoint = stagger_to_mass.Vstagger_to_mass(XLONG_V)            
            
            ### The difference between V and U lat is very small (10^-5) so we'll only calculate one of them
            x_ml,y_ml = m(Vlon_masspoint,Vlat_masspoint)    
#==============================================================================
            

            
            # What is the height of model level in middle of Salt Lake Valley??
            center_valley_height = phi[232,204]  # valid for domain 2          
            print "geopotential height SLV:", center_valley_height
            
            
            # This sets a thinn-ed out grid point structure for plotting
            # wind barbs at the interval specified in "thin"
            #thin = 5 
            #x_th,y_th = m(XLONG[0,::thin,::thin],XLAT[0,::thin,::thin])
            	
            # Set universal figure margins
            width = 10
            height = 12
            
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
            
            # only plot W in the valley
            masked_W = np.ma.masked_array(W,HGT>1600)
            masked_V10 = np.ma.masked_array(V10,HGT>1600)            
            masked_U10 = np.ma.masked_array(U10,HGT>1600)
            masked_Q2  = np.ma.masked_array(Q2, HGT>1600)

            masked_U_masspoint = np.ma.masked_array(U_masspoint, HGT>1600)
            masked_V_masspoint = np.ma.masked_array(V_masspoint, HGT>1600)
            
            
            plt.contourf(x,y,HGT,levels=np.arange(1000,4000,500),cmap='binary')            
                        
            
            """
            # V-Component Wind pcolormesh            
            plt.pcolormesh(x,y,masked_V10,cmap='BrBG',vmax=8,vmin=-8)
            cbar_loc = plt.colorbar(shrink=.8,pad=.01,ticks= np.arange(-8,8.1,1),extend='both')
            cbar_loc.ax.set_ylabel('Wind Speed (m/s)')
            
            """
            """
            ## V-Component Wind Contour Fill (colored)
            plt.contourf(x,y,masked_V10,cmap='BrBG',levels=np.arange(-10,10.1,.5),extend='neither')
            cbar_loc = plt.colorbar(shrink=.8,ticks= np.arange(-10,10.1,2))
            cbar_loc.ax.set_ylabel('10-m V Wind (m/s)',fontsize=20)
            cbar_loc.ax.tick_params(labelsize=20)
            """
            
            
            """
            ## Water Vapor Mixing Ratio Contours
            plt.contour(x,y,masked_Q2,linewidths=2,levels=[1,2,3,4,5,6,7,8,9,10],cmap='PiYG')
            cbar_WV = plt.colorbar(orientation='horizontal',shrink=.8,pad=.01,)
            cbar_WV.ax.set_xlabel('2-m Water Vapor (g/kg)',fontsize=20)
            cbar_WV.ax.tick_params(labelsize=20)
            """
            
            if model_level == 'surface':
                ## W-Component vertical Wind Contour Fill (colored)
                plt.contourf(x,y,masked_W,cmap='bwr',levels=np.arange(-5,5.1,.5),extend='both')
                cbar_loc = plt.colorbar(shrink=.8,ticks= np.arange(-5,5.1,1))
                cbar_loc.ax.set_ylabel('Vertical Velocity Wind on model level 7 (m/s)\n Approx. '+str(int(center_valley_height))+' meters',fontsize=20)
                cbar_loc.ax.tick_params(labelsize=20)
                
                
                ## Contour Lake Outline
                plt.contour(x,y,landmask, [0,1], linewidths=3, colors="b")
                #plt.contour(x,y,HGT)
                #plt.contourf(x,y,HGT,cmap=cmapgrey) # transparent greay if plotted on top                
                
                ## Wind Barbs surface
                plt.barbs(x[::3,::3],y[::3,::3],masked_U10[::3,::3],masked_V10[::3,::3],
                          length=6,
                          barb_increments=dict(half=1, full=2, flag=10),
                          sizes=dict(emptybarb=.1),
                          zorder=40)
                plt.title('Surface wind barbs with \n vertical velocity on model level 7 (~2300 m)')
            
            else:
                ## W-Component vertical Wind Contour Fill (colored)
                plt.contourf(x,y,masked_W,cmap='bwr',levels=np.arange(-5,5.1,.5),extend='both')
                cbar_loc = plt.colorbar(shrink=.8,ticks= np.arange(-5,5.1,1))
                cbar_loc.ax.set_ylabel('Vertical Velocity Wind on model level '+str(model_level)+' (m/s)\n Approx. '+str(int(center_valley_height))+' meters',fontsize=20)
                cbar_loc.ax.tick_params(labelsize=20)
                
                
                ## Contour Lake Outline
                plt.contour(x,y,landmask, [0,1], linewidths=3, colors="b")
                #plt.contour(x,y,HGT)
                #plt.contourf(x,y,HGT,cmap=cmapgrey) # transparent greay if plotted on top                
                
                ## Wind Barbs model level
                plt.barbs(x_ml[::3,::3],y_ml[::3,::3],masked_U_masspoint[::3,::3],masked_V_masspoint[::3,::3],
                          length=6,
                          barb_increments=dict(half=1, full=2, flag=10),
                          sizes=dict(emptybarb=.1),
                          zorder=40) #put barbs on top 

                      
            
            xs,ys = m(-111.97,40.78) #buffr sounding coordinates
            #plt.scatter(xs,ys, s=70, c='w')
            """            
            plt.title(time_str+'\n'+time_str_local, bbox=dict(facecolor='white', alpha=0.65),\
        			x=0.5,y=1.05,weight = 'demibold',style='oblique', \
        			stretch='normal', family='sans-serif')            
            """            
            #plt.savefig(out_dir+'w_wind_'+time_file+'.png',bbox_inches="tight",dpi=500)
            #print 'Saved',time_str
    
            plt.show()
    
        
        
