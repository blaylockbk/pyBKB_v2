# Brian Blaylock
# November 4, 2015

"""
Define map domains for drawing maps here
"""

import numpy as np

def get_domain(this_one):

    domains = {
    'UINTAH_BASIN': {
                    'map_domain'     : 'Uintah_Basin',                
                    'name'           : 'Uintah Basin',
                    'map_projection' : 'cyl',
                    'bot_left_lat'   : 39.73,                
                    'bot_left_lon'   : -111.,
                    'top_right_lat'  : 41.,                
                    'top_right_lon'  : -109.,                 
                    },

    'SALT_LAKE_VALLEY': {
                    'map_domain'     : 'Salt_Lake_Valley',
                    'name'           : 'Salt Lake Valley',
                    'map_projection' : 'cyl',
                    'bot_left_lat'   : 40.4,
                    'bot_left_lon'   : -112.19785,
                    'top_right_lat'  : 40.9,
                    'top_right_lon'  : -111.60
                    },

    'GREAT_SALT_LAKE': {
                    'map_domain'     : 'Great_Salt_Lake',
                    'name'           : 'Great Salt Lake',
                    'map_projection' : 'cyl',
                    'bot_left_lat'   : 40.5,
                    'bot_left_lon'   : -113.25,
                    'top_right_lat'  : 41.9,
                    'top_right_lon'  : -111.75
                    },

    'GREAT_SALT_LAKE_west': { # domain extended west to include BFLAT station
                    'map_domain'     : 'Great_Salt_Lake_West',
                    'name'           : 'Great Salt Lake West',
                    'map_projection' : 'cyl',
                    'bot_left_lat'   : 40.5,
                    'bot_left_lon'   : -114.0,
                    'top_right_lat'  : 41.9,
                    'top_right_lon'  : -111.75
                    },

    'GREAT_SALT_LAKE_cut': { # cut area for Summer 2015 lake repair
                    'map_domain'     : 'Great_Salt_Lake',
                    'name'           : 'Great Salt Lake',
                    'map_projection' : 'cyl',
                    'bot_left_lat'   : 40.492346,
                    'bot_left_lon'   : -113.75,
                    'top_right_lat'  : 41.858304,
                    'top_right_lon'  : -111.853761
                    },                    

    'UTAH_VALLEY': {
                    'map_domain'     : 'Utah_Valley',
                    'name'           : 'Utah Valley',
                    'map_projection' : 'cyl',
                    'bot_left_lat'   : 40.001550,
                    'bot_left_lon'   : -111.901389,
                    'top_right_lat'  : 40.451040,
                    'top_right_lon'  : -111.501889
                    },

    'UTAH_LAKE': {
                    'map_domain'     : 'Utah_Lake',
                    'name'           : 'Utah Lake',
                    'map_projection' : 'cyl',
                    'bot_left_lat'   : 40.,
                    'bot_left_lon'   : -111.95,
                    'top_right_lat'  : 40.38,
                    'top_right_lon'  : -111.65
                    },

    'BEAR_LAKE': {
                    'map_domain'     : 'Bear_Lake',
                    'name'           : 'Bear Lake',
                    'map_projection' : 'cyl',
                    'bot_left_lat'   : 41.826247,
                    'bot_left_lon'   : -111.455473,
                    'top_right_lat'  : 42.153301,
                    'top_right_lon'  : -111.189903
                    },

    'UTAH': {
                    'map_domain'     : 'Utah',
                    'name'           : 'Utah',
                    'map_projection' : 'cyl',
                    'bot_left_lat'   : 36.5,
                    'bot_left_lon'   : -114.5,
                    'top_right_lat'  : 42.5,
                    'top_right_lon'  : -108.5
                    },

    'CACHE_VALLEY': {
                    'map_domain'     : 'Cache_Valley',
                    'name'           : 'Cache Valley',
                    'map_projection' : 'cyl',
                    'bot_left_lat'   : 41.228045,
                    'bot_left_lon'   : -112.278722,
                    'top_right_lat'  : 41.99730,
                    'top_right_lon'  : -111.535024
                    },

    'MOSES_LAKE': {
                    'map_domain'     : 'Moses_Lake',
                    'name'           : 'Moses Lake',
                    'state'          : 'Washington',
                    'map_projection' : 'cyl',
                    'bot_left_lat'   : 47.050935,
                    'bot_left_lon'   : -119.403803,
                    'top_right_lat'  : 47.193245,
                    'top_right_lon'  : -119.252493
                    },

    'WILLARD_BAY': {
                    'map_domain'     : 'Willard_Bay',
                    'name'           : 'Willard Bay',
                    'map_projection' : 'cyl',
                    'bot_left_lat'   : 41.3423,
                    'bot_left_lon'   : -112.133,
                    'top_right_lat'  : 41.4172,
                    'top_right_lon'  : -112.049
                    },

    'CONUS_HRRR': {
                    'map_domain'     : 'CONUS_HRRR',
                    'name'           : 'CONUS HRRR',
                    'map_projection' : 'lcc',
                    'lat_0'          : 38.5,  # Requires plotting on lcc projection
                    'lon_0'          : -97.5,
                    'lat_1'          : 38.5,
                    'lat_2'          : 38.5,
                    'width'          : 1800*3000,
                    'height'         : 1060*3000,
                    }
    }

    if this_one == 'all':
        return domains
    else:
        return domains[this_one]
#------------------------------------------------------------------------------
    
    
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