
# Brian Blaylock
# 4 February 2016

# test push

# Get MesoWest Wind Data for all stations in a radius
# Return the Name, Lat, Lon, WS, and WD in a dictionary

import numpy as np
import datetime
import json
import urllib2
import matplotlib.pyplot as plt
from get_token import my_token # returns my personal token

# Get your own key and token from here: https://mesowest.org/api/signup/
token = my_token()

within = '15'
attime = '201506182100'



def get_mesowest_nearesttime(attime,within,stn,v=False):
    """
    attime: a string in the format YYYYDDMMHHMM used in the API query
    within: a string of the number of minutes to request data from
    raduis: a string of the location to center the radius, followed by number of miles
            can center on a MesoWest station ID (ksl,30) like the default, or
            can center on a lat/lon (41.5,-120.25,30)
    v: verbose, print some stuff like the query URL
    """
    variables = 'wind_speed,wind_direction,air_temp,dew_point_temperature'
    
    URL = 'http://api.mesowest.net/v2/stations/nearesttime?&token='+token+'&stid='+stn+'&attime='+attime+'&within='+within+'&obtimezone=utc&units=metric&vars='+variables
    #print '!! MESOWEST:',URL
    
    if v==True:
        # verbose
        print "MesoWest API Query: ",URL    
    
    ##Open URL and read the content
    f = urllib2.urlopen(URL)
    data = f.read()
    
    ##Convert that json string into some python readable format
    data = json.loads(data)
    
    
    name = np.array([])
    stnid = np.array([])
    DATES = np.array([])    
    ws = np.array([])
    wd = np.array([])
    dwpt = np.array([])
    temp = np.array([])

    
    for i in data['STATION']:
        name = np.append(name,i['NAME'])
        stnid = np.append(stnid,i['STID'])
        try:    
            wd = np.append(wd,i['OBSERVATIONS']['wind_direction_value_1']['value'])
        except:
            wd =np.append(wd,np.nan)
        try:    
            ws = np.append(ws,i['OBSERVATIONS']['wind_speed_value_1']['value'])
        except:
            ws = np.append(ws,np.nan)
        try:    
            temp = np.append(temp,i['OBSERVATIONS']['air_temp_value_1']['value'])
            date = i['OBSERVATIONS']['air_temp_value_1']['date_time']
            converted_time = datetime.datetime.strptime(date,'%Y-%m-%dT%H:%M:%SZ')
            DATES = np.append(DATES,converted_time)
        except:
            temp = np.append(temp,np.nan)
            DATES = np.append(DATES,np.nan)
        try:    
            dwpt = np.append(dwpt,i['OBSERVATIONS']['dew_point_temperature_value_1d']['value'])
        except:
            dwpt = np.append(dwpt,np.nan)
        
        
        
        
    
    # Convert datatype from Unicode to String or floats
    name = name.astype(str)
    stnid = stnid.astype(str)
    
    ws = ws.astype(float)
    wd = wd.astype(float)
    
    temp = temp.astype(float)
    
    
    
    data = {'URL':URL,
            'NAME':name,
            'STNID':stnid,
            'DATES':DATES,
            'DWPT':dwpt,
            'WIND_SPEED':ws,
            'WIND_DIR':wd,
            'TEMP':temp,
            }
            
    return data

# Wind Calculations
def wind_spddir_to_uv(wspd,wdir):
    """
    calculated the u and v wind components from wind speed and direction
    Input:
        wspd: wind speed
        wdir: wind direction
    Output:
        u: u wind component
        v: v wind component
    """    
    
    rad = 4.0*np.arctan(1)/180.
    u = -wspd*np.sin(rad*wdir)
    v = -wspd*np.cos(rad*wdir)

    return u,v
    

#--- Example -----------------------------------------------------------------#
if __name__ == "__main__":
    a = get_mesowest_nearesttime('201506190000','10,10','wbb,ukbkb')
    u,v = wind_spddir_to_uv(a['WIND_SPEED'],a['WIND_DIR'])
    
    
    
    
