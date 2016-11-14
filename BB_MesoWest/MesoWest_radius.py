# Brian Blaylock
# Version 2.0 update
# 8 November 2016                     (Trump vs. Clinton Presidential Election)

"""
Get MesoWest data for all stations within within defined bounds:
    - stations within a radius within a latitude longitude point
    - stations within a radius of a specified station
    - specific state or states
    - etc. (see MesoWest API documentation
            https://synopticlabs.org/api/mesonet/reference/#stations_Resources)

Returns a dictionary that contains station names, ids, lats/lons, and observed
variables.

another change
"""

import json
import urllib2
from datetime import datetime
from get_token import my_token  # returns my personal token
from convert_MW_date import MWdate_to_datetime
import numpy as np

# Get my token. You may request an API key and token from the here:
# https://mesowest.org/api/signup/
token = my_token()

# Request these default variables.
default_vars = 'wind_speed,wind_direction,ozone_concentration,\
PM_25_concentration,air_temp,pressure'


def get_mesowest_radius(attime, within,
                        extra='&radius=kslc,30',
                        variables=default_vars):
    """
    Gets data nearest a time for all stations.
    https://synopticlabs.org/api/mesonet/reference/

    Inputs:
        attime - A python datetime object of the desired time.
        within - A string of the number of minutes to request data from. Use
                 two numbers to request before and after attime 10,10.
        extra - A string of extra API calls (refer to the API documentation)
                The default is to return stations within a 30 mile radius of
                kslc.

    Outputs:
        Dictionary containing the station metadata, observations, and datetimes
        for statins within the requested radius.
    """
    # Convert attime to string required for MesoWest API query.
    attime = attime.strftime("%Y%m%d%H%M")
    tz = 'utc'

    URL = 'http://api.mesowest.net/v2/stations/nearesttime?&token=' + token \
        + '&attime=' + attime \
        + '&within=' + within \
        + '&obtimezone=' + tz \
        + extra \
        + '&vars=' + variables

    # Open URL and read JSON content. Convert JSON string to some python
    # readable format.
    f = urllib2.urlopen(URL)
    data = f.read()
    data = json.loads(data)

    # Store the data we will return in this new dictionary
    return_this = {'URL': URL,
                   'NAME': np.array([]),
                   'STID': np.array([]),
                   'LAT': np.array([]),
                   'LON': np.array([]),
                   'ELEVATION': np.array([]),  # Note: Elevation is in feet.
                   'DATETIME': np.array([])
                  }

    # Create a new key for each possible variable
    for v in data['UNITS'].keys():
        return_this[str(v)] = np.array([])

        # Since some observation times between variables for the same station
        # *could* be different, I will store the datetimes from each variable
        # with a similar name as the variable.
        return_this[str(v) + '_DATETIME'] = np.array([])

    for i in range(0, len(data['STATION'])):
        stn = data['STATION'][i]  # this represents the station

        # Store basic metadata for each station in the dictionary.
        return_this['NAME'] = np.append(return_this['NAME'], str(stn['NAME']))
        return_this['STID'] = np.append(return_this['STID'], str(stn['STID']))
        return_this['LAT'] = np.append(return_this['LAT'],
                                       float(stn['LATITUDE']))
        return_this['LON'] = np.append(return_this['LON'],
                                       float(stn['LONGITUDE']))
        return_this['ELEVATION'] = np.append(return_this['ELEVATION'],
                                             float(stn['ELEVATION']))

        # Dynamically store data from each available variable.
        for v in data['UNITS'].keys():

            key_name = str(v)  # Same as the API variable name
            set_num = 0        # Always get the first set: value_1 or value_1d
            # May need to write some exceptions to this rule

            try:
                # If value exists, then append with the data
                grab_this_set = str(stn['SENSOR_VARIABLES']
                                    [key_name].keys()[set_num])
                variable_data = float(stn['OBSERVATIONS']
                                      [grab_this_set]['value'])
                date_data = MWdate_to_datetime(stn['OBSERVATIONS']
                                               [grab_this_set]['date_time'])

                return_this[key_name] = \
                    np.append(return_this[key_name], variable_data)
                return_this[key_name + '_DATETIME'] = \
                    np.append(return_this[key_name + '_DATETIME'], date_data)

            except:
                # If it doesn't exist, then append with np.nan
                return_this[key_name] = \
                    np.append(return_this[key_name], np.nan)
                return_this[key_name + '_DATETIME'] = \
                    np.append(return_this[key_name + '_DATETIME'], np.nan)

    return return_this


#--- Example -----------------------------------------------------------------#
if __name__ == "__main__":

    a = get_mesowest_radius(datetime(2016, 4, 4), '10', extra='&radius=kslc,7')
