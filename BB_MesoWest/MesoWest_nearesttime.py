
# Brian Blaylock
# 4 February 2016

# test push

# Get MesoWest Wind Data for all stations in a radius
# Return the Name, Lat, Lon, WS, and WD in a dictionary

import numpy as np
from datetime import datetime
import json
import urllib2
from get_token import my_token # returns my personal token

# Get your own key and token from here: https://mesowest.org/api/signup/
token = my_token()

default_vars = 'wind_speed,wind_direction,dew_point_temperature'

def get_mesowest_nearesttime(DATE,stn,within='120', tz='utc',
                             variables=default_vars,
                             v=False):
    """
    attime: datetime object of nearest time to retrieve
    within: a string of the number of minutes to request data from
    radius: a string of the location to center the radius, followed by number of miles
            can center on a MesoWest station ID (ksl,30) like the default, or
            can center on a lat/lon (41.5,-120.25,30)
    v: verbose, print some stuff like the query URL
    """
    
    URL = 'http://api.mesowest.net/v2/stations/nearesttime?&token='+token \
           +'&stid='+stn \
           +'&attime='+DATE.strftime('%Y%m%d%H%M') \
           +'&within='+within \
           +'&obtimezone='+tz \
           +'&units=metric' \
           +'&vars=air_temp,'+variables
    #print '!! MESOWEST:',URL
    
    if v==True:
        # verbose
        print "MesoWest API Query: ",URL    
    
    ##Open URL and read the content
    f = urllib2.urlopen(URL)
    data = f.read()
    
    ##Convert that json string into some python readable format
    data = json.loads(data)
    
    UNITS = data['UNITS']

    return_this = {}
    
    for i in data['STATION']:
        return_this[i['STID']] = {'NAME': i['NAME'],
                                  'ELEVATION': i['ELEVATION'],
                                  'LATITUDE': i['LATITUDE'],
                                  'LONGTUDE': i['LONGITUDE']
                                  }
        for v in i['SENSOR_VARIABLES']:
            return_this[i['STID']][v] = {}
            try:
                return_this[i['STID']][v]['value'] = i['OBSERVATIONS'][v+'_value_1']['value']
                return_this[i['STID']][v]['DATETIME'] = datetime.strptime(i['OBSERVATIONS'][v+'_value_1']['date_time'], '%Y-%m-%dT%H:%M:%SZ')
            except:
                return_this[i['STID']][v]['value'] = i['OBSERVATIONS'][v+'_value_1d']['value']
                return_this[i['STID']][v]['DATETIME'] = datetime.strptime(i['OBSERVATIONS'][v+'_value_1d']['date_time'], '%Y-%m-%dT%H:%M:%SZ')
    return return_this


    

#--- Example -----------------------------------------------------------------#
if __name__ == "__main__":
    DATE = datetime(2017, 10, 9, 6)
    a = get_mesowest_nearesttime(DATE,'HWKC1')
    
    
    
    
