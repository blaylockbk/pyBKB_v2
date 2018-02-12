# Brian Blaylock
# Version 2.0 update
# 8 November 2016                     (Trump vs. Clinton Presidential Election)

"""
Get basic metadata for a list of station IDs
"""

import json
import urllib2
from get_token import my_token # returns my personal token
import time

import numpy as np

# Get your own key and token from here: https://mesowest.org/api/signup/
token = my_token()


def get_MW_location_dict(STID):
    """
    Return a location dictionary in the form
    location_dic = {'name':{'latitude':##.#,
                            'longitude':##.#,
                            'elevation':##,}}
    Input: 
        STID - a string of mesowest station IDs separated by a comma
               (i.e 'wbb,ukbkb,mtmet')
    """
    # The API request URL
    URL = 'http://api.mesowest.net/v2/stations/metadata?&token=' + token \
        + '&stid=' + STID

    # Open URL, read the content, and convert JSON to python readable form.

    f = urllib2.urlopen(URL)
    data = f.read()
    data = json.loads(data)

    location_dict = {}

    for i in data['STATION']:
        stid = i['STID']
        lat = i['LATITUDE']
        lon = i['LONGITUDE']
        name = i['NAME']
        elev = i['ELEVATION']
        
        location_dict[str(stid)] = {'latitude':float(lat),
                               'longitude':float(lon),
                               'name':str(name),
                               'elevation':float(elev)}
    return location_dict


def get_station_info(stationIDs):
    """
    Get the metadata info for a list of stations and return it as a dictionary.

    Input:
        stationIDs  : list of station IDs as a string ['UKBKB', 'KSLC', 'WBB']

    Output:
        A dictionary of the data you are looking for:
        - Latitude
        - Longitude
        - Station Name
        - Elevation
        - URL
    """
    
    tz_list = {'America/New_York': 5,
               'America/Indiana/Indianapolis': 5,
               'America/Chicago': 6,
               'America/Denver': 7,
               'America/Boise': 7,
               'America/Phoenix': 7,      # no daylight savings
               'America/Los_Angeles': 8,
               'America/Anchorage': 9,
               'America/Adak': 10,
               'Pacific/Honolulu': 10}    # no daylight savings

    # Check that the input is a list of stations.
    if type(stationIDs) != list:
        return "List of stations is required! s = ['KSLC', 'WBB', 'MTMET']"
    else:
        # Convert stationID list to a string deliminated by a comma
        stations = ','.join(stationIDs)

    # The API request URL
    URL = 'http://api.mesowest.net/v2/stations/metadata?&token=' + token \
        + '&stid=' + stations


    try:
        # Open URL, read the content, and convert JSON to python readable form.

        f = urllib2.urlopen(URL)
        data = f.read()
        data = json.loads(data)

        stnid = np.array([])
        name = np.array([])
        lat = np.array([])
        lon = np.array([])
        time_zone = np.array([])
        tz = np.array([])

        for i in data['STATION']:
            name = np.append(name, str(i['NAME']))
            stnid = np.append(stnid, str(i['STID']))
            lat = np.append(lat, float(i['LATITUDE']))
            lon = np.append(lon, float(i['LONGITUDE']))
            time_zone = np.append(time_zone, str(i['TIMEZONE']))
            tz = np.append(tz, tz_list[str(i['TIMEZONE'])])

        data_dict = {'URL': URL,
                     'NAME': name,
                     'STNID': stnid,
                     'LAT': lat,
                     'LON': lon,
                     'TIME_ZONE': time_zone,
                     'UTC Offset': tz
                    }

        return data_dict

    except:
        print 'errors loading:', URL

#--- Example -----------------------------------------------------------------#
if __name__ == "__main__":

    STATION = ['kslc', 'ukbkb', 'klax', 'kims', 'kjfk']
    A = get_station_info(STATION)
