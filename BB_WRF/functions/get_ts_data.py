# Brian Blaylock
# 4 December 2015

# Three functions to process data in a TS file outputted by WRF.
#   get_ts_header reads the header and puts the data in a dictionary.
#   get_ts_data reads the data and puts a variable in a numpy array.
#   get_vert_data reads the data from the vertical profiles

# More information about WRF's tslist can be found in the WRF directory
# WRFV3/run/README.tslist

import linecache
import numpy as np
from datetime import datetime
from wind_calcs import *

def get_ts_header(TSfile):
    """
    Returns a dictionary with information contined in the header of the TSfile
    produced by WRF.
    
    Input:
        TSfile - The time series output produced by WRF in the form XXX.d0Y.TS
                 where XXX is the station ID and Y is the domain.
    Output:
        header_dict - A dictionary that contains the following:
            stn_name    = string of the station's full name
            grid_id     = string of the station's ID
            stn_id      = tuple of the station's grid ID
            stn_latlon  = list of the station's real latitude and longitude
            grid_indices= tuple of the grid indices. Location on domain.
            grid_latlon = list of the grid latitude and longitude
            grid_elev   = float of the grid elevation
            elev_units       = units of the elevation 
    """
    line = linecache.getline(TSfile,1)
    
    name = line[0:25]
    gridID1 = line[26:29]
    gridID2 = line[29:32]
    stnID = line[33:38]
    stnlat = line[39:46]
    stnlon = line[47:55]
    gridindx1 = line[58:62]
    gridindx2 = line[63:67]
    gridlat = line[70:77]
    gridlon = line[78:86]
    grid_elev = line[88:94]
    elev_units = line[95:]
    
    header_dict = {
                    'stn_name':name.strip(),
                    'grid_id':(int(gridID1),int(gridID2)),
                    'stn_id':stnID.strip(), 
                    'stn_latlon':[float(stnlat),float(stnlon)],
                    'grid_indices':(int(gridindx1),int(gridindx2)),
                    'grid_latlon':[float(gridlat),float(gridlon)],
                    'grid_elev':float(grid_elev),
                    'elev_units':elev_units.strip()                      
                    }
    return header_dict

def get_ts_data(TSfile,variable):
    """
    Opens the tslist output. Packages and returns the data.
    The tslist oupt     
    
    Input:
        TSfile - The time series output produced by WRF in the form XXX.d0Y.TS
                 where XXX is the station ID and Y is the domain number
        variable - The variable in the TSfile you wish to retrieve
            id:          grid ID
            ts_hour:     forecast time in hours
            id_tsloc:    time series ID
            ix,iy:       grid location (nearest grid to the station)
            t:           2 m Temperature (K)
            q:           2 m vapor mixing ratio (kg/kg)
            u:           10 m U wind (earth-relative)
            v:           10 m V wind (earth-relative)
            psfc:        surface pressure (Pa)
            glw:         downward longwave radiation flux at the ground (W/m^2, downward is positive)
            gsw:         net shortwave radiation flux at the ground (W/m^2, downward is positive)
            hfx:         surface sensible heat flux (W/m^2, upward is positive)
            lh:          surface latent heat flux (W/m^2, upward is positive)
            tsk:         skin temperature (K)
            tslb(1):     top soil layer temperature (K)
            rainc:       rainfall from a cumulus scheme (mm)
            rainnc:      rainfall from an explicit scheme (mm)
            clw:         total column-integrated water vapor and cloud variables
            
    Output:
        A numpy array of the data for the variable you requrested
    """
    # column names as defined by the WRFV3/run/README.tslist
    col_names = ['id','ts_hour','id_tsloc','ix','iy','t','q','u','v','psfc',
                 'glw','gsw','hfx','lh','tsk','tsbl','rainc','rainnc','clw']
    
    # check that the input variable matches with one in the list
    if variable not in col_names:
        print "That variable is not available. Choose a variable from the following list"
        print "\
        'id'           grid ID\n\
        'ts_hour':     forecast time in hours\n\
        'id_tsloc':    time series ID\n\
        'ix':          grid location (nearest grid to the station)\n\
        'iy':          grid location (nearest grid to the station)\n\
        't':           2 m Temperature (K)\n\
        'q':           2 m vapor mixing ratio (kg/kg)\n\
        'u':           10 m U wind (earth-relative)\n\
        'v':           10 m V wind (earth-relative)\n\
        'psfc':        surface pressure (Pa)\n\
        'glw':         downward longwave radiation flux at the ground (W/m^2, downward is positive)\n\
        'gsw':         net shortwave radiation flux at the ground (W/m^2, downward is positive)\n\
        'hfx':         surface sensible heat flux (W/m^2, upward is positive)\n\
        'lh':          surface latent heat flux (W/m^2, upward is positive)\n\
        'tsk':         skin temperature (K)\n\
        'tslb':        top soil layer temperature (K)\n\
        'rainc':       rainfall from a cumulus scheme (mm)\n\
        'rainnc':      rainfall from an explicit scheme (mm)\n\
        'clw':         total column-integrated water vapor and cloud variables\n\n"

    
    # load the file into a numpy array
    TS = np.genfromtxt(TSfile, skip_header=1, names = col_names)
 
    return TS[variable]



def get_vert_data(TSfile,model_start,get_this_time,model_timestep=2,p_top_requested=5000):
    """
    Gets the vertical profile data at a station defined in the tslist.
    Gets the data required to create a sounding.
    Returns a dictionary that can be used by sounding.py to plot on SkewT

    To use this you have to know something about the timestep of you model 
    output. Model_timestep is the timestep in seconds.
    
    Input: 
        TSfile: use the same TS file location as other scripts above. It 
                doesn't matter what the last two labels are. We'll strip if off
                and add our own.
        model_start: a datetime object with the start time of the model
        get_this_time: a datetime object with the time step you desire
        model_timestep: the timestep of the model domain in seconds
        p_top_requested: the model top. Used for calculating pressure
        
    Output:
        The profile UU, VV, TH, PH, and QV
        Also calculted values of wind speed and direction temp and dwpt required
        to make sounding plots.
    """
    
    # Figure out which line our desired time is on
    # 1)difference between desired time and model start time
    # 2)how many seconds is between the times?
    # 3)divide by the model timestep = line number the profile is in
    deltaT = get_this_time-model_start    
    seconds_from_start = deltaT.seconds+deltaT.days*86400
    row_number = seconds_from_start/model_timestep + 1 #plus one to account for header row    
    # if the model start and the get time are the same then return the first
    # row time in the model which is really the first time step.      
    if model_start == get_this_time:
        print "called the first time", model_start==get_this_time
        row_number = 2
    print 'line:', row_number
    
    # Read the line then load into a numpy array 
    #(don't return the zeroth column which is just the time)
    
    # U wind
    UU = linecache.getline(TSfile[:-2]+'UU',row_number)
    UU = np.array(UU.split(),dtype=float)[1:]
    # V wind    
    VV = linecache.getline(TSfile[:-2]+'VV',row_number)
    VV = np.array(VV.split(),dtype=float)[1:]
    # Potential Temperature (K)    
    TH = linecache.getline(TSfile[:-2]+'TH',row_number)
    TH = np.array(TH.split(),dtype=float)[1:]
    # Geopotential Height
    PH = linecache.getline(TSfile[:-2]+'PH',row_number)
    PH = np.array(PH.split(),dtype=float)[1:]
    # Mixing Ratio
    QV = linecache.getline(TSfile[:-2]+'QV',row_number)
    QV = np.array(QV.split(),dtype=float)[1:]

    
    # Need to make a few calculations for additional data (THIS IS NOT FINISHED!!!)
    #----------------------------------------------------------------------
    # Convert geopotential to pressure
    # p2 = p1*exp(-(Z2-Z1)/H) where H=RTa/g0
    Rd = 287  # J/K/kg
    g0 = 9.81 # m/s/s
    p1 = 900  # surface pressure???
    p = np.array([])
    Ta = TH[0]      # K  # column "average" temperature. Just use the bottom
    H = Rd*Ta/g0    # Scale Height        
    for i in np.arange(len(PH))-1:
        Z2 = PH[i+1]
        Z1 = PH[i]
        p2 = p1*np.exp(-(Z2-Z1)/H)
        p = np.append(p,p2)                
        
        
    #Convert Potential Temperature (K) to Temperature (C)
    # theta = T*(p0/p)^(R/cp)
    p0 = 1000 # hpa
    R = 287 # J/K/kg
    cp = 1004 # J/K/kg
    T = TH/((p0/p)**(R/cp))-273.15
    
    # Convert mixing ratio to dewpoint temperature

    profile = {
            'UU':UU,
            'VV':VV,
            'TH':TH,
            'PH':PH,
            'QV':QV,
            'pres':p,
            'temp':T,
            'dwpt':0,
            'drct':wind_uv_to_dir(UU,VV), 
            'sknt':wind_uv_to_spd(UU,VV)

    }    

    return profile
    
    
    
    

#--- Example -----------------------------------------------------------------#
if __name__ == "__main__":
    
    station = 'KSLC'
    wrf_dir = '/uufs/chpc.utah.edu/common/home/horel-group4/model/bblaylock/WRF3.7_sniplake/DATA/'    
    tsfile = station+'.d02.TS'    

    # Use above function to get the header dictionary    
    header = get_ts_header(wrf_dir+tsfile)
    
    # Print all the keys and values in the header dictionary    
    print "\nHeader info from", tsfile    
    for i in header:
        print '  ',i, '=',header[i]
    print ""
    
    
    # Use above function to get the data for a few variables
    temp_2m = get_ts_data(wrf_dir+tsfile,'t')
    u_10m = get_ts_data(wrf_dir+tsfile,'u')
    
    # Get a vertical profile
    model_start = datetime(2015,6,18,0)
    get_time = datetime(2015,6,19,0,0)
    
    profile = get_vert_data(wrf_dir+tsfile,model_start,get_time)
    
    # plot a vertical profile
    import matplotlib.pyplot as plt
    plt.figure(1,figsize=[20,10])
    plt.suptitle(station +' '+datetime.strftime(get_time,'%b %d, %Y %H:%Mz'),fontsize=20)
    plt.subplot(1,3,1)
    plt.title('Potential Temperature')    
    plt.plot(profile['TH'],profile['PH'],linewidth=2,color='red')
    plt.xlabel('Potential Temperature (K)')
    plt.ylabel('Geopotential Height (m)')

    plt.subplot(1,3,2)    
    plt.title('Mixing Ratio')
    plt.plot(profile['QV'],profile['PH'],linewidth=2,color='green')
    plt.xlabel('Mixing Ratio (kg/kg)')
    plt.ylabel('Geopotential Height (m)')

    plt.subplot(1,3,3)
    plt.title('Wind')
    plt.plot(profile['UU'],profile['PH'],linewidth=2, color='blue', label="U vector")
    plt.ylabel('Geopotential Height (m)')
        
    plt.plot(profile['VV'],profile['PH'],linewidth=2, color='orange', label="V vector")
    plt.xlabel('V wind (m/s)')
    plt.ylabel('Geopotential Height (m)')
    plt.axvline(0,color='red')
    
    plt.barbs(np.zeros(len(profile['PH'])),profile['PH'],profile['UU'],profile['VV'])
    plt.xlabel('Wind Vector (m/s) Half=5, Full=10, Flag=50')
    plt.ylabel('Geopotential Height (m)')
    
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5),prop={'size':10})
        
    plt.show()
    
