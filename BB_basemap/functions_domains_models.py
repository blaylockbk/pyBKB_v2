# Dictionaries for plotting
# Created by Brian Blaylock
# November 4, 2015

import numpy as np




def get_domain(this_one):

    domains = {
    'uintah_basin': {
                    'map_domain'    :'Uintah_Basin',                
                    'name'          :'Uintah Basin',
                    'map_projection':'cyl',
                    'units'         :'m/s',
                    'thin'          :3,
                    'max_speed'     :25,
                    'time_zone'     :6,
                    'bot_left_lat'  :39.73,                
                    'bot_left_lon'  :-111.,
                    'top_right_lat' :41.,                
                    'top_right_lon' :-109.
                    },
    'salt_lake_valley': {
                    'map_domain'    :'Salt_Lake_Valley',
                    'name'          :'Salt Lake Valley',
                    'map_projection':'cyl',
                    'units'         :'m/s',
                    'thin'          :1,
                    'max_speed'     :25,
                    'time_zone'     :6,
                    'bot_left_lat'  :40.4,
                    'bot_left_lon'  :-112.19785,
                    'top_right_lat' :40.9,
                    'top_right_lon' :-111.60
                    },
    'great_salt_lake': {
                    'map_domain'    :'Great_Salt_Lake',
                    'name'          :'Great Salt Lake',
                    'map_projection':'cyl',
                    'units'         :'m/s',
                    'thin'          :1,
                    'max_speed'     :25,
                    'time_zone'     :6,
                    'bot_left_lat'  :40.492346,
                    'bot_left_lon'  :-113.25,
                    'top_right_lat' :41.858304,
                    'top_right_lon' :-111.753761
                    },
    'great_salt_lake_cut': { # cut area for Summer 2015
                    'map_domain'    :'Great_Salt_Lake',
                    'name'          :'Great Salt Lake',
                    'map_projection':'cyl',
                    'units'         :'m/s',
                    'thin'          :1,
                    'max_speed'     :25,
                    'time_zone'     :6,
                    'bot_left_lat'  :40.492346,
                    'bot_left_lon'  :-113.75,
                    'top_right_lat' :41.858304,
                    'top_right_lon' :-111.853761
                    },                    
    'utah_valley': {
                    'map_domain'    :'Utah_Valley',
                    'name'          :'Utah Valley',
                    'map_projection':'cyl',
                    'units'         :'m/s',
                    'thin'          :1,
                    'max_speed'     :25,
                    'time_zone'     :6,
                    'bot_left_lat'  :40.001550,
                    'bot_left_lon'  :-111.901389,
                    'top_right_lat' :40.451040,
                    'top_right_lon' :-111.501889
                    },
    'utah_lake': {
                    'map_domain'    :'Utah_Lake',
                    'name'          :'Utah Lake',
                    'map_projection':'cyl',
                    'units'         :'mph',
                    'thin'          :1,
                    'max_speed'     :30,
                    'time_zone'     :6,
                    'bot_left_lat'  :40.,
                    'bot_left_lon'  :-111.951,
                    'top_right_lat' :40.375,
                    'top_right_lon' :-111.65
                    },
    'bear_lake': {
                    'map_domain'    :'Bear_Lake',
                    'name'          :'Bear Lake',
                    'map_projection':'cyl',
                    'units'         :'mph',
                    'thin'          :1,
                    'max_speed'     :30,
                    'time_zone'     :6,
                    'bot_left_lat'  :41.826247,
                    'bot_left_lon'  :-111.455473,
                    'top_right_lat' :42.153301,
                    'top_right_lon' :-111.189903
                    },
    'full_utah': {
                    'map_domain'    :'Full_Utah',
                    'name'          :'Utah',
                    'map_projection':'cyl',
                    'units'         :'m/s',
                    'thin'          :7,
                    'max_speed'     :25,
                    'time_zone'     :6,
                    'bot_left_lat'  :36.5,
                    'bot_left_lon'  :-114.5,
                    'top_right_lat' :42.5,
                    'top_right_lon' :-108.5
                    },
    'cache_valley': {
                    'map_domain'    :'Cache_Valley',
                    'name'          :'Cache Valley',
                    'map_projection':'cyl',
                    'units'         :'m/s',
                    'thin'          :1,
                    'max_speed'     :25,
                    'time_zone'     :6,
                    'bot_left_lat'  :41.228045,
                    'bot_left_lon'  :-112.278722,
                    'top_right_lat' :41.99730,
                    'top_right_lon' :-111.535024
                    },
    'moses_lake': {
                    'map_domain'    :'Moses_Lake',
                    'name'          :'Moses Lake (WA)',
                    'map_projection':'cyl',
                    'units'         :'mph',
                    'thin'          :1,
                    'max_speed'     :30,
                    'time_zone'     :7,
                    'bot_left_lat'  :47.050935,
                    'bot_left_lon'  :-119.403803,
                    'top_right_lat' :47.193245,
                    'top_right_lon' :-119.252493
                    },
    'willard_bay': {
                    'map_domain'    :'Willard_Bay',
                    'name'          :'Willard Bay',
                    'map_projection':'cyl',
                    'units'         :'m/s',
                    'thin'          :1,
                    'max_speed'     :30,
                    'time_zone'     :6,
                    'bot_left_lat'  :41.3423,
                    'bot_left_lon'  :-112.133,
                    'top_right_lat' :41.4172,
                    'top_right_lon' :-112.049
                    },
    'full_HRRR': {
                    'map_domain'    :'Full_HRRR',
                    'name'          :'HRRR',
                    'map_projection':'lcc',
                    'units'         :'m/s',
                    'thin'          :30,
                    'max_speed'     :30,
                    'time_zone'     :6,
                    'ref_lat'       :38.5,  # Requires plotting on lcc projection
                    'ref_lon'       :-97.5,
                    'truelat1'      :38.5,
                    'truelat2'      :38.5,
                    'stand_lon'     :-97.5,
                    'bot_left_lat'  :30,
                    'bot_left_lon'  :-127,
                    'top_right_lat' :42,
                    'top_right_lon' :-105
                    }
    }
    if this_one == 'all':
        return domains
    else:
        return domains[this_one]
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
def get_model_info(this_one):    
    MODEL_INFO = {
    
    'NAM': # Used NCL command 'ncl_convert2nc' to convert raw NAM analysis to a NetCDF file
        {
        'name':'NAM',
        'resolution':'12km',    
        'BASE':'/uufs/chpc.utah.edu/common/home/horel-group4/model/bblaylock/NAM_data/', #location of files    
        'string_format':'namanl_218_%04d%02d%02d_%02d00_000.nc', #YYYMMDD_HH00_000
        'hours':np.arange(0,24,6), # model hours
        'type':'analysis' #analysis or forecast
        },
    'HRRR': # Used grib2 to convert raw HRRR grib2 file to a NetCDF
        {
        'name':'HRRR',
        'resolution':'3km',
        'BASE':'/uufs/chpc.utah.edu/common/home/u0553130/MS/June18_HRRR/raw_HRRR/', #location of files        
        'string_format':'%04d%02d%02d_hrrr.t%02dz.wrfsfcf00.nc', #YYYMMDD_hrrr.tHHz.wrfshcf00.nc
        'hours':np.arange(0,24,1), # model hours
        'type':'analysis' #analysis or forecast
        },
    'HRRR_geo': # Used grib2 to convert raw HRRR grib2 file to a NetCDF
        {
        'name':'HRRR Geo',
        'resolution':'3km',
        'BASE':'/uufs/chpc.utah.edu/common/home/u0553130/MS/HRRR_domains/', #location of files        
        'string_format':'geo_em.d01.nc',
        'type':'WPS' #analysis or forecast
        },
    'WRF':  # WRF Output file
        {
        'name':'WRF',
        'resolution':'1km',
        'BASE':'/uufs/chpc.utah.edu/common/home/horel-group4/model/bblaylock/WRF3.7_kingspeakTest/WRFV3/test/em_real/',
        'string_format':'wrfout_d02_%04d-%02d-%02d_%02d:00:00', #wrfout_d02_YYY-MM-DD_HH:00:00
        'hours':np.arange(0,24,1), # model hours
        'type':'forecast' #analysis or forecast
        }
    }
    
    return MODEL_INFO[this_one]
    
    
if __name__ == "__main__":
    domain = get_domain('salt_lake_valley')
    print domain
    print domain.keys()
    print ""
    print 'Domain Name: ', domain['name']
    print get_domain('all')
    
    print ""
    print ""
    model = get_model_info('HRRR_geo')
    print model
    print model.keys()
    print ""
    print 'Model Name: ', model['name']