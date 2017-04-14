### Brian Blaylock

# 01 July 2016
# Updates:
#   18 July 2016    Use the 'data_map' instance to convert 8-bit data to floats in m/s
#                   Fixed the NWSVelocity colorbar                    

# MetPy read the TDWR level 3 .nids files
import os
import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB')  #for running on CHPC boxes
sys.path.append('B:\pyBKB')  
from functions_domains_models import *

# Bug fixed for reading TDWR data is located in my local verision of metpy_BB
from MetPy_BB.io.nexrad import Level3File
from MetPy_BB.plots import ctables

from BB_MesoWest.MesoWest_stations_radius import *

import multiprocessing #:)
import numpy as np
from numpy import ma
import matplotlib.pyplot as plt
from pyproj import Geod #this is used to convert range/azimuth to lat/lon
from mpl_toolkits.basemap import Basemap
from datetime import datetime


v = 'TV0'
ctable = 'NWSVelocity'
date = '20170414'
path = '/uufs/chpc.utah.edu/common/home/horel-group4/gslso3s/data/TDWR/%s/%s/' % (date, v)
out_dir = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/TDWR/Dust_20170414/%s/' % (v)
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

# Create a list of all the file names (assuming the directory only contains .nids files)
# List of file names we want to make plots for
def plot_tdwr(scan):
    print scan
    fig, axes = plt.subplots(1, 1, figsize=(5.5, 10))
    #for v, ctable, ax in zip(('N0Q', 'N0U'), ('NWSReflectivity', 'NWSVelocity'), axes):

    ax = axes
    #scan = 'Level3_SLC_%s_20160912_0000.nids' % v
    date = datetime.strptime(scan[-18:-5], '%Y%m%d_%H%M')
    FILE = path + scan

    f = Level3File(FILE)

    # Pull the data out of the file object (this stuff is in 8-bit)
    datadict = f.sym_block[0][0]

    # Turn into an array, then mask
    data = f.map_data(datadict['data']) # I'm confident this maps the data to floats with units of m/s
    data = ma.array(data)
    data[np.isnan(data)] = ma.masked

    # Convert knots to m/s
    data = data * .5144

    # Grab azimuths and calculate a range based on number of gates
    az = np.array(datadict['start_az'] + [datadict['end_az'][-1]])
    rng = np.linspace(0, f.max_range, data.shape[-1] + 1)

    # Convert az, range to a lat/lon
    g = Geod(ellps='clrk66') # This is the type of ellipse the earth is projected on. 
                             # There are other types of ellipses you can use,
                             # but the differences will be small
    center_lat = np.ones([len(az),len(rng)])*f.lat
    center_lon = np.ones([len(az),len(rng)])*f.lon
    az2D = np.ones_like(center_lat)*az[:,None]
    rng2D = np.ones_like(center_lat)*np.transpose(rng[:, None])*1000
    lon, lat, back = g.fwd(center_lon, center_lat, az2D, rng2D)

    # Convert az,range to x,y 
    # (use these variables if don't want to plot on a basemap. 
    # Value is range from the radar.)
    xlocs = rng * np.sin(np.deg2rad(az[:, np.newaxis]))
    ylocs = rng * np.cos(np.deg2rad(az[:, np.newaxis]))

    # Create Basemap
    domain = get_domain('salt_lake_valley')
    top_right_lat = domain['top_right_lat']+.3
    top_right_lon = domain['top_right_lon']
    bot_left_lat = domain['bot_left_lat']-.2
    bot_left_lon = domain['bot_left_lon']-.2

    ## Map in cylindrical projection
    m = Basemap(resolution='i',projection='cyl',\
        llcrnrlon=bot_left_lon,llcrnrlat=bot_left_lat,\
        urcrnrlon=top_right_lon,urcrnrlat=top_right_lat,)
    maps = ['ESRI_Imagery_World_2D',    # 0
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

    ## Draw high resolution background image from ESRI
    m.arcgisimage(service=maps[8], xpixels = 1000, verbose= False)
    m.drawcoastlines()
    m.drawstates()

    # get mesowest winds
    mesowest_time = date.strftime('%Y%m%d%H%M')
    a = get_mesowest_radius_winds(mesowest_time, '10')

    ## Now plot data on basemap

    # This uses the same colorbar as the NWS Velocity color scheme
    norm, cmap = ctables.registry.get_with_steps(ctable, -20, 2.5)
    this = m.pcolormesh(lon, lat, data, norm=norm, cmap=cmap)
    bar = plt.colorbar(this,ax=ax,orientation='horizontal',shrink=.8,pad=.01)
    bar.ax.set_xlabel('Radial Velocity ($\mathregular{m s^{-1}}$)',fontsize=10)
    ax.set_title(scan)
    #ax.set_aspect('equal', 'datalim')
    # Add MesoWest wind barbs
    u,v = wind_spddir_to_uv(a['WIND_SPEED'],a['WIND_DIR'])
    m.barbs(a['LON'],a['LAT'],u,v,
            length=5.5,                
            barb_increments=dict(half=2.5, full=5, flag=25),
            sizes=dict(spacing=0.15, height=0.3, emptybarb=.1))
    # Location of TDWR and other observing stations for reference
    m.scatter(-111.93,40.9669, s=75, c='w',zorder=40)               # TDWR
    plt.savefig(out_dir+"__"+scan[0:-5]+'.png',bbox_inches='tight')

    fig, axes = plt.subplots(1, 1, figsize=(5.5, 10))
    ax = axes
    # This uses the brown/green colorbar used in my MS Thesis
    m.arcgisimage(service=maps[8], xpixels = 1000, verbose= False)
    thesis_color = m.pcolormesh(lon,lat,data,cmap="BrBG_r",vmax=10,vmin=-10)
    bar = plt.colorbar(thesis_color,orientation='horizontal',shrink=.8,pad=.01,
                       label=r'Radial Velocity ($\mathregular{m s^{-1}}$)')
    # Add Mesowest Wind Barbs
    u,v = wind_spddir_to_uv(a['WIND_SPEED'],a['WIND_DIR'])
    m.barbs(a['LON'], a['LAT'], u, v,
            length=5.5,   
            barb_increments=dict(half=2.5, full=5, flag=25),
            sizes=dict(spacing=0.15, height=0.3, emptybarb=.1))
    # Location of TDWR and other observing stations for reference
    m.scatter(-111.93,40.9669, s=75, c='w',zorder=40)               # TDWR
    ax.set_title(scan)
    
    plt.savefig(out_dir+scan[0:-5]+'.png',bbox_inches='tight')
    
    #plt.show()


if __name__=='__main__':
    # List of file names we want to make plots for
    somelist = []
    #for i in os.listdir('./17-19_June/'):
    for i in os.listdir(path):    
        if i[0:10]=='Level3_SLC' and i[-4:]=='nids': # get the file name of a TDWR file for all files
            somelist.append(i)
            
    # Count number of processors
    num_proc = multiprocessing.cpu_count()
    #num_proc = 10 #we have a lot of plotting to do, so lets run this on ten computers. Whahahah!!
                        # I could speed up the process by only drawin the basemap once, rather than every time I draw a plot, but funcinality is more important than speed right now
    p = multiprocessing.Pool(num_proc)
    p.map(plot_tdwr,somelist)