
# Brian Blaylock
# 28 March 2018

# Get MesoWest percentile data for a station

import numpy as np
from datetime import datetime
import json
import urllib2
from get_token import my_token # returns my personal token

# Get your own key and token from here: https://mesowest.org/api/signup/
token = my_token()


def get_mesowest_latest(stn, tz='utc', units='metric', v=False):
    """
    For a single station:
    
    stn = a mesowest station ID (only one station)
    tz = time zone, 'UTC' or 'LOCAL'
    units = 'METRIC' or 'ENGLISH'
    v: verbose, print some stuff like the query URL
    """
    variables = 'wind_speed,wind_direction,air_temp,dew_point_temperature'
    
    URL = 'http://api.mesowest.net/v2/stations/nearesttime?&token='+token \
           +'&stid='+stn \
           +'&obtimezone='+tz \
           +'&units='+units
    #print '!! MESOWEST:',URL
    
    if v==True:
        # verbose
        print "MesoWest API Query: ",URL    
    
    ##Open URL and read the content
    f = urllib2.urlopen(URL)
    data = f.read()
    
    ##Convert that json string into some python readable format
    data = json.loads(data)
    d = data['STATION'][0]
    
    return_this = {'URL':URL,
                   'STID':d['STID'],
                   'NAME':d['NAME']}
        
    date = d['OBSERVATIONS']['air_temp_value_1']['date_time']
    if tz.upper() == "UTC":
        return_this['DATE'] = datetime.strptime(date,'%Y-%m-%dT%H:%M:%SZ')
    else:
        return_this['DATE'] = datetime.strptime(date[:-5],'%Y-%m-%dT%H:%M:%S')

    for U in data['UNITS']:
        return_this[U] = {'value':d['OBSERVATIONS'][U+'_value_1']['value'],
                          'unit':data['UNITS'][U]}
            
    return return_this
    

#--- Example -----------------------------------------------------------------#
if __name__ == "__main__":
    a = get_mesowest_latest('UKBKB')
    
    
    
    
