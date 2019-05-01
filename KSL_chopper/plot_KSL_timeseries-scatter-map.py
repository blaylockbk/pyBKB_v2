## Brian Blaylock
## May 2, 2016

# Creates three figures of KSL ozone observations.
# 1) time series plot of ozone, elevation of KSL helicopter
# 2) scatter plot of ozone vs height and potential temperature from SLC rawinsonde
# 3) map of ozone observations in the Salt Lake Valley

# Mobile Data retreived from:
# http://meso2.chpc.utah.edu/gslso3s/cgi-bin/mobile_data.cgi

import numpy as np
import linecache
import matplotlib.pyplot as plt
from datetime import datetime
from mpl_toolkits.basemap import Basemap
from matplotlib.dates import DateFormatter, YearLocator, MonthLocator, DayLocator, HourLocator, MinuteLocator
import matplotlib as mpl
from scipy.io import netcdf
import os
import urllib2
from bs4 import BeautifulSoup # I know this is installed on meso3
from mesowest_stations_radius import get_mesowest_radius_winds, wind_spddir_to_uv


## First set the plot font sizes and line width
tick_font = 8
label_font = 10
lw = 1.5    

mpl.rcParams['xtick.labelsize'] = tick_font
mpl.rcParams['ytick.labelsize'] = tick_font



def download_sounding(request_sounding):
    stn = '72572' # this is the id number for KSLC
    year = str(request_sounding.year).zfill(4)
    month= str(request_sounding.month).zfill(2)
    day  = str(request_sounding.day).zfill(2)
    hour = str(request_sounding.hour).zfill(2) # hour in UTC, 00 and 12 z usually available
    
    
    # Download, process and add to plot the Wyoming Data
    # 1)
    # Wyoming URL to download Sounding from
    url = 'http://weather.uwyo.edu/cgi-bin/sounding?region=naconf&TYPE=TEXT%3ALIST&YEAR='+year+'&MONTH='+month+'&FROM='+day+hour+'&TO='+day+hour+'&STNM='+stn
    content = urllib2.urlopen(url).read()
    print 'sounding url:', url
    
    # 2)
    # Remove the html tags
    soup = BeautifulSoup(content,"html.parser")
    data_text = soup.get_text()
    
    # 3)
    # Split the content by new line.
    splitted = data_text.split("\n",data_text.count("\n"))
    
    
    #4)
    # Must save the processed data as a .txt file to be read in by the skewt module.
    # Write this splitted text to a .txt document. Save in current directory.
    Sounding_dir = './'
    Sounding_filename = str(stn)+'.'+str(year)+str(month)+str(day)+str(hour)+'.txt'
    f = open(Sounding_dir+Sounding_filename,'w')
    for line in splitted[4:]:
        f.write(line+'\n')
    f.close()
    
    return Sounding_dir+Sounding_filename


def download_mobile(platform,requested_time,previous_mins):
    """
    Downloads mobile data from online and saves a temporary text file.
    Reads the text file, then deletes the temporary text file when completed.
    
    """
    # platform = 'KSL5', 'TRX01'
    
    year = str(requested_time.year).zfill(4)
    month= str(requested_time.month).zfill(2)
    day = str(requested_time.day).zfill(2)
    hour = str(requested_time.hour).zfill(2)
    minute = str(requested_time.minute).zfill(2)
    previous_mins = str(previous_mins)   
    
    url = 'http://meso2.chpc.utah.edu/gslso3s/cgi-bin/download_mobile_data.cgi?yr='+year+'&mo='+month+'&dy='+day+'&hr='+hour+'&mm='+minute+'&min='+previous_mins+'&stid='+platform

    print platform, 'download:', url

    rawdata = urllib2.urlopen(url).read()
    splitted = rawdata.split("\n",rawdata.count("\n"))
    
    # Save a text file of the data (this makes reading it easy, and I don't have to change my code I've already written)
    data_dir = './'
    filename = platform+'_'+year+month+day+hour+minute+'.txt'
    f = open(data_dir+filename,'w')
    for line in splitted[:]:
        f.write(line+'\n')
    f.close()   
    
    # Read File
    col_names = linecache.getline(filename,2)
    
    try:
        data = np.genfromtxt(filename,skip_header=2, names = col_names,delimiter=',',dtype=None)

    
        # Convert Dates and Times to Datetime Object
        DATES = np.array([])
        for i in range(0,len(data['Date'])):
            a = data['Date'][i]+' '+data['TimeUTC'][i]    
            b = datetime.strptime(a,'%Y-%m-%d %H:%M:%S')
            DATES = np.append(DATES,b)
            
        ozone = data['2b_ozone_ppbv']
        ozone[ozone<0]=np.nan
        lat = data['cr1000_gpslat_dd']
        lon = data['cr1000_gpslon_dd']
        elevation = data['cr1000_gpselev_m']
        
        elevation[elevation==-9999] = np.nan        
        
        try:    
            pressure = data['cr1000_pres_hpa']
        except:
            pressure = np.zeros(len(DATES))*np.nan
        
        os.remove(filename)
        
        return {'platform':platform,
                'DATES':DATES,
                'ozone':ozone,
                'latitude':lat,
                'longitude':lon,
                'elevation':elevation,
                'pressure':pressure    
                }
    except:
        data = 'No Data Available from '+platform+' at this time'
        return data    
    
def plot_ozone_timeseries(mobile):
    print""    
    print "--plot time series--"    
    """
    Input, the ksl_mobile data
    """    
    
    width=3.5
    height=2

    
    fig, (ax1) = plt.subplots(1,1,figsize=(width,height))
    
    # Left axis: Ozone Concentration
    ax1.plot(mobile['DATES'],mobile['ozone'],color='purple',linewidth=lw,label="Ozone")
    ax1.set_ylabel('Ozone Concentration (ppb)',fontsize=label_font)
    ax1.set_xlabel('Time (UTC)',fontsize=label_font)
    #ax1.set_yticks(range(40,85,5))
    ax1.legend(bbox_to_anchor=(0, 1.0, .45, .12),fontsize=7,frameon=False)
    plt.grid(linewidth=.25)
    
    # Right axis: Elevation
    ax1a = ax1.twinx()
    ax1a.plot(mobile['DATES'],mobile['elevation'],color='teal',lw=lw-.3,label='Elevation')
    ax1a.set_ylabel('Elevation (m)',fontsize=label_font)
    #ax1a.set_yticks(range(1200,4701,500))
    #ax1a.set_ylim([1200,4700])
    ax1a.legend(bbox_to_anchor=(0, 1.0,.8, .12),fontsize=7,frameon=False)
    
    duration = (mobile['DATES'][-1]-mobile['DATES'][0]).seconds/3600.  # flight duration in hours  
    print 'flight duration (hours)', duration    
    
    if duration > 1:
        # Set major ticks every 20 mins
        minutes20 = MinuteLocator(byminute=range(0,60,20))
        minutes10  = MinuteLocator(byminute=range(0,60,10))
        dateFmt = DateFormatter('%b %d\n%H:%M')
        blank_dateFmt = DateFormatter('')    
        # Set the x-axis major tick marks
        ax1.xaxis.set_major_locator(minutes20)
        # Set the x-axis labels
        ax1.xaxis.set_major_formatter(blank_dateFmt)
        # For additional, unlabeled ticks, set x-axis minor axis
        ax1.xaxis.set_minor_locator(minutes10)
        ax1.xaxis.set_major_formatter(dateFmt)
    else:
        # Set major tickes every 10 mins
        minutes10 = MinuteLocator(byminute=range(0,60,10))
        minutes5  = MinuteLocator(byminute=range(5,60,10))
        dateFmt = DateFormatter('%b %d\n%H:%M')
        blank_dateFmt = DateFormatter('')    
        # Set the x-axis major tick marks
        ax1.xaxis.set_major_locator(minutes10)
        # Set the x-axis labels
        ax1.xaxis.set_major_formatter(blank_dateFmt)
        # For additional, unlabeled ticks, set x-axis minor axis
        ax1.xaxis.set_minor_locator(minutes5)
        ax1.xaxis.set_major_formatter(dateFmt)
            
    
    # Save the figure
    plt.savefig(FIGDIR+string_time+'_'+mobile['platform']+'_timeseries_ozone-elevation.png',dpi=1000,bbox_inches="tight")
    print "saved ozone time series"
    print ""

def plot_ozone_theta_scatter(mobile):
    print "--plot scatter--" 
    width=3.5
    height=3.5    
    
    fig, (ax1) = plt.subplots(1,1,figsize=(width,height))
        
    # Bottom axis: ozone concentration
    ax1.scatter(mobile['ozone'],mobile['elevation'],color='purple',s=3,label="Ozone")
    ax1.set_ylabel('Elevation (m)',fontsize=label_font)
    ax1.set_xlabel('Ozone (ppb)',fontsize=label_font)
    #ax1.set_yticks(range(1200,4701,500))

    max_ozone_elevation = np.nanmax(mobile['elevation'])+100 

    
    ax1.set_ylim([1200,max_ozone_elevation])
    #ax1.set_xticks(range(45,76,5))
    #ax1.set_xlim([45,75])
    plt.grid(linewidth=.25)
    
    
    ## Top axis: Potential Temperature
    # If request_time is in the afternoon, then request the evening sounding
    if request_time.hour > 18:
        # Get the evening sounding (00 UTC) for the next day
        request_sounding = datetime(request_time.year,request_time.month,request_time.day+1,0)    
    elif request_time.hour < 6:
        # Get the evening sounding (00 UTC) for the same
        request_sounding = datetime(request_time.year,request_time.month,request_time.day,0)    
    else:
        # Get the morning sounding (12 UTC) for the same day
        request_sounding = datetime(request_time.year,request_time.month,request_time.day,12)
    
    print "SLC sounding for", request_sounding
    
    sound_file = download_sounding(request_sounding)
    col_names = ['PRES','HGHT','TEMP','DWPT','RELH','MIXR','DRCT','SKNT','THTA','THTE','THTV']
    sound_data = np.genfromtxt(sound_file,skip_header=8,skip_footer=45,names=col_names,dtype=float)
    
    height_asl = sound_data['HGHT']
    theta = sound_data['THTA']

    
    # Set xlim for potential temperature the creative way (this will scale it right)    
    theta_xmax = (theta[height_asl<4700]).max()+3    
    theta_xmin = (theta[height_asl<4700]).min()-3    
       
    
    ax1a = ax1.twiny()
    ax1a.plot(theta,height_asl,color='darkred',lw=lw,label='Potential Temperature')
    ax1a.set_ylim([1200,max_ozone_elevation])
    ax1a.set_xlabel('Potential Temperature (K)',fontsize=label_font)
    ax1a.set_xlim([theta_xmin,theta_xmax])
    #ax1a.set_xlim([theta.min()-3,theta[height_asl<5000].max()+3])
    #ax1a.legend(bbox_to_anchor=(0, 1.0,.8, .12),fontsize=7,frameon=False)
    
    plt.savefig(FIGDIR+string_time+'_'+mobile['platform']+'_scatter_ozone-theta.png',dpi=1000,bbox_inches="tight")
    print "saved scatter plot"
    print ""

def plot_map(mobile,other_mobile=False,auto_map_boundaries=True,background='WRF'):
    print "--plot map--"    
    """
    makes a map of the helicopter observations. Also plots MesoWest
    input: mobile=ksl observations from the get moblie function
    
    other_mobile: if set to true will plot truck and trax data if available
    auto_map_boundaries: will find the location of the helicopter and will set auto boundaries
                         else, will map the salt lake valley or you can change the lat/lon manually
    background: 'WRF' will use a wrf file to contour the boundary
                'sat' will use an old satellite image
                'topo' will use a topographical image
    
    """
    plt.cla()
    plt.clf()
    plt.close()
    
    
    width=4
    height=4.5
    
    
    fig, (ax1) = plt.subplots(1,1,figsize=(width,height))
    
    
    ## ---- Draw map
    top_right_lat = 40.9+.1
    top_right_lon = -111.60
    bot_left_lat = 40.4+.05
    bot_left_lon = -112.19785-.05
    
    ## Map in cylindrical projection (data points may apear skewed)
    m = Basemap(resolution='i',projection='cyl',\
        llcrnrlon=bot_left_lon,llcrnrlat=bot_left_lat,\
        urcrnrlon=top_right_lon,urcrnrlat=top_right_lat,)    
    
    
    
    # -----Set Background images
    
    if background == 'WRF':
        ## ---- Grab terrain data
        directory = '/uufs/chpc.utah.edu/common/home/horel-group4/model/bblaylock/WRF3.7_spinup/DATA/FULL_RUN_June14-19/'
        spat = 'auxhist23_d02_2015-06-14_00:00:00'
        nc_spatial = netcdf.netcdf_file(directory+spat,'r')
        # This sets the standard grid point structure at full resolution
        #	Converts WRF lat and long to the maps x an y coordinate
        XLONG = nc_spatial.variables['XLONG'][0]
        XLAT  = nc_spatial.variables['XLAT'][0]
        HGT = nc_spatial.variables['HGT'][0,:,:] #topography
        landmask = nc_spatial.variables['LANDMASK'][0,:,:]
            
        # Plot Terrain 
        X,Y = m(XLONG,XLAT)
        plt.contourf(X,Y,HGT,levels=np.arange(1000,4000,500),cmap='binary')            
        # Draw major roads from shapefile
        m.readshapefile('/uufs/chpc.utah.edu/common/home/u0553130/shape_files/tl_2015_UtahRoads_prisecroads/tl_2015_49_prisecroads','roads', linewidth=.2)
    
        ## Contour Lake Outline
        plt.contour(X,Y,landmask, [0,1], linewidths=1, colors="b")


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
    if background == 'sat':
        ## Instead of using WRF terrain fields you can get a high resolution image from ESRI
        m.arcgisimage(service=maps[0], xpixels = 3000, verbose= True)
    if background == 'topo':
        ## Instead of using WRF terrain fields you can get a high resolution image from ESRI
        m.arcgisimage(service=maps[8], xpixels = 3000, verbose= True)
        # Draw major roads from shapefile
        m.readshapefile('/uufs/chpc.utah.edu/common/home/u0553130/shape_files/tl_2015_UtahRoads_prisecroads/tl_2015_49_prisecroads','roads', linewidth=.2)
    # can use any other map background from maps list
    
    # Plot Mobile Ozone points (KSL)
    x,y = m(mobile['longitude'],mobile['latitude']) 
    # plot every 30 seconds rather than every 10 seconds (thus the [::3] indexes)    
    m.scatter(x[::3],y[::3],c=ksl_mobile['ozone'][::3],vmax=80,vmin=45.,lw = .3,s=30,cmap=plt.cm.get_cmap('jet'),zorder=50)
    cbar = plt.colorbar(orientation='horizontal',extend='both',shrink=.8,pad=.03)
    cbar.ax.set_xlabel('Ozone Concentration (ppb)',fontsize=10)
    cbar.ax.tick_params(labelsize=8)
    cbar.set_ticks([45,50,55,60,65,70,75,80,85])
    
    # Plot Other Mobile data
    if other_mobile == True:
        # Plot Mobile Ozone points (TRAX01)
        try:
            x,y = m(trax_mobile['longitude'],trax_mobile['latitude']) 
            m.scatter(x[:],y[:],c=trax_mobile['ozone'][:],vmax=80,vmin=45.,lw = .3,marker='d',s=30,cmap=plt.cm.get_cmap('jet'),zorder=50)
        except:
            print 'no TRAX01 data'
            
        # Plot Mobile Truck points (UUTK3)
        try:
            x,y = m(trk3_mobile['longitude'],trk3_mobile['latitude']) 
            m.scatter(x[:],y[:],c=trk3_mobile['ozone'][:],vmax=80,vmin=45.,lw = .3,marker='p',s=30,cmap=plt.cm.get_cmap('jet'),zorder=50)
        except:
            print 'no UUTK3 data'
        
        # Plot Mobile Truck points (UUTK1)
        try:
            x,y = m(trk1_mobile['longitude'],trk1_mobile['latitude']) 
            m.scatter(x[:],y[:],c=trk1_mobile['ozone'][:],vmax=80,vmin=45.,lw = .3,marker='p',s=30,cmap=plt.cm.get_cmap('jet'),zorder=50)
        except:
            print 'no UUTK1 data'
    
    
    ## Plot MesoWest  (top of the hour, +/- 10 mins) 
    # Plot MesoWest wind data
    mesowest_time = str(request_time.year).zfill(2)+str(request_time.month).zfill(2)+str(request_time.day).zfill(2)+str(request_time.hour).zfill(2)+'00'
    print 'plotting mesowest observations within 10 minutes of top of the hour',mesowest_time    
    a = get_mesowest_radius_winds(mesowest_time,'10')
    u,v = wind_spddir_to_uv(a['WIND_SPEED'],a['WIND_DIR'])
    m.barbs(a['LON'],a['LAT'],u,v,
            length=4.5,                
            linewidth=.5,
            barb_increments=dict(half=1, full=2, flag=10),
            sizes=dict(spacing=0.15, height=0.3, emptybarb=.1))
    # ozone
    m.scatter(a['LON'],a['LAT'],c=a['OZONE'],vmax=80,vmin=45.,lw =.3,s=20, marker='s',cmap=plt.cm.get_cmap('jet'),zorder=50)
    
    
    # Manually plot other Sensor locations by lat/lon
    """
    m.scatter(-111.93,40.9669, s=75, c='w',zorder=40)
    m.scatter(-112.01448,40.71152, s=75, c='b',zorder=40) # NAA
    m.scatter(-111.93072,40.95733, s=75, c='darkorange',zorder=40) # O3S02                        
    m.scatter(-111.828211,40.766573, s=75, c='r',zorder=40) # MTMET                       
    m.scatter(-111.8717,40.7335, s=75, c='darkgreen',zorder=40) # QHW               
    m.scatter(-111.96503,40.77069, s=75, c='w',zorder=40) # SLC               
    m.scatter(-112.34551,40.89068 , s=75, c='w',zorder=40) # GSLBY
    """
    
    plt.savefig(FIGDIR+string_time+'_map.png',dpi=500,bbox_inches="tight")
    print 'saved map'
    print ""

  
#------------------------------------------------------------------------------  
#------------------------------------------------------------------------------  

if __name__ == '__main__':
    # Specify place to save the figures    
    FIGDIR = './figs/'
    # If that directory doesn't exist then create it
    if not os.path.exists(FIGDIR):
        os.makedirs(FIGDIR)
    
    
    
    # Different case studies 
    # add to this list          'Name': [endtime UTC, previous minutes]
    cases = {
            'Smoke1':[datetime(2015, 8,18,23,20),30],
            'Smoke2':[datetime(2015, 8,19,23,20),30],
            'Lake Breeze':[datetime(2015, 6,18,23,40),60],
            'Morning':[datetime(2016, 5,3,13,20),180],
    }
    
    
    #set the case name you want, from the cases dictinary
    request_case = 'Lake Breeze'
    
    
    request_time = cases[request_case][0]
    previous_mins = cases[request_case][1]
    string_time = request_time.strftime('%Y%m%d%H%M')
    
    print 'plotting', request_time, 'and previous', previous_mins, 'minutes'
    
    # Get Mobile Data sets if they are available
    ksl_mobile = download_mobile('KSL5',request_time,previous_mins)           # KSL Helicopter
    trax_mobile = download_mobile('TRX01',request_time,previous_mins)         # UTA TRAX
    trk1_mobile = download_mobile('UUTK1',request_time,previous_mins)         # UUTruck
    trk3_mobile = download_mobile('UUTK3',request_time,previous_mins)         # UUTruck
    
    # Make Plots
    plot_ozone_timeseries(ksl_mobile)
    plot_ozone_theta_scatter(ksl_mobile)
    plot_map(ksl_mobile,other_mobile=True,background='topo')
    
