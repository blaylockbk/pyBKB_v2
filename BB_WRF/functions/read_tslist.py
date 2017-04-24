# Brian Blaylock
# 3 December 2015

import numpy as np

def read_tslist(tsfile):
    """
    Reads in a time series list (tslist) in the WRFV3/test/em_real directory
    and puts the data in arrays for station name, id, lat, and lon.
    More info on the WRF tslist can be found here:
    http://www2.mmm.ucar.edu/wrf/users/docs/user_guide_V3/users_guide_chap5.htm#timeseries
    
    Input:
        file: the location of your tslist file
    Output:
        NAME: name of the station.
        STNID: id of the station. Preferably use the same as listed in MesoWest
               for easy API queries. 
        LAT: latitude of the station
        LON: longitude of the station
    """
    # Initialize the arrays
    NAME = np.array([])
    STNID= np.array([])
    LAT  = np.array([])
    LON  = np.array([])
    
    # Read each line of the text file
    with open(tsfile,'r') as f:
        for line in f:
            if line[0]=='#':
            # Discard the commented lines, first three lines of the tslist file
                continue
            # Grab the data from each line (throw away white spaces)
            try:
                NAME = np.append(NAME, line[0:25].strip())
                STNID = np.append(STNID, line[25:32].strip())
                LAT = np.append(LAT, float(line[32:41]))
                LON = np.append(LON, float(line[41:]))
            except:
                print "----------------------------------------------------"                
                print "Error: something may be wrong with the tslist file."
                print "Check that there isn't a blank line at the bottom."
                print "----------------------------------------------------"            
                continue                
                
    return NAME,STNID,LAT,LON


#--- Example -----------------------------------------------------------------#
if __name__ == "__main__":
  
    import matplotlib.pyplot as plt 
    from mpl_toolkits.basemap import Basemap
    from scipy.io import netcdf # Other people like to use netcdf4, 
                                # but I don't have that installed :(
    from terrain_colormap import * # My custom colormap

    
    wrf_dir = '/uufs/chpc.utah.edu/common/home/horel-group4/model/bblaylock/WRF3.7_sniplake/WRFV3/test/em_real/'
    
    # Read the tslist file using the function above
    name,stn_id,lat,lon = read_tslist(wrf_dir+'tslist')
    
    # Plot the locations of the sites on a plane
    plt.figure(1)    
    plt.scatter(lon,lat)
    # Add Labels to each point
    for i in np.arange(0,len(stn_id)):
        plt.annotate(stn_id[i],xy=(lon[i],lat[i]))
    
    # Print a list of all the station names
    
    print "\nStation Names:"
    for i in name:
        print '  ',i
        
        
    #-------------------------------------------------------------------------#
    # We can also plot these locations on a terrain map using the wrfout file
    #-------------------------------------------------------------------------#    
    
    # Specify the wrfout file or use the met_em file or the geo_em, but may 
    # need to change some of the below variables if you do that.
    wrf_file = 'wrfout_d02_2015-06-18_00:00:00'
    
    # Open NetCDF file and import needed variables
    nc = netcdf.netcdf_file(wrf_dir+wrf_file,'r')
    wrf_lon = nc.variables['XLONG'][:][0].copy()
    wrf_lat = nc.variables['XLAT'][:][0].copy()
    wrf_ter = nc.variables['HGT'][:][0].copy()
    wrf_landmask = nc.variables['LANDMASK'][0].copy()
    
    # I like to set the water points to a negative elevation so that the color 
    # map will plot the water as blue
    wrf_ter[wrf_landmask==0] = -99

    # Set map boundaries with a little buffer on each side
    bot_left_lat =  lat.min()-0.2
    top_right_lat = lat.max()+0.2    
    bot_left_lon =  lon.min()-0.2
    top_right_lon = lon.max()+0.2
    
    # Create the map
    m = Basemap(resolution='i',area_thresh=10.,projection='cyl',\
        llcrnrlon=bot_left_lon,llcrnrlat=bot_left_lat,\
        urcrnrlon=top_right_lon,urcrnrlat=top_right_lat,)
         
            
    plt.figure(2)

    #m.drawcoastlines()
    #m.drawstates()
        
    # Plot a shapefile of the major roads (shape files can be downloaded here: https://www.census.gov/cgi-bin/geo/shapefiles/index.php)
    #BASE = '/uufs/chpc.utah.edu/common/home/u0553130/'
    #m.readshapefile(BASE+'shape_files/tl_2015_UtahRoads_prisecroads/tl_2015_49_prisecroads','roads', linewidth=.1, color='grey')
   
    # Plot terrain
    plt.pcolormesh(wrf_lon,wrf_lat,wrf_ter,
                   #cmap=plt.get_cmap('terrain'))    # Use python's terrain colormap
                   cmap=terrain_cmap_256())          # Use my custom terrain colormap
    cbar = plt.colorbar(orientation='horizontal',shrink=.7,\
                        fraction=0.036, pad=0)    
    cbar.set_label('Terrain Height (meters)')

    # Plot the station locations and labels on the map
    m.scatter(lon,lat, color='white')
    for i in np.arange(0,len(stn_id)):
        plt.annotate(stn_id[i],xy=(lon[i],lat[i]))
            
    plt.show()
    #plt.savefig('TS_location_map.png',bbox_inches='tight',dpi=300)
