# Brian Blaylock
# Version 2.0 update
# 8 November 2016                     (Trump vs. Clinton Presidential Election)

# Get MesoWest data for all stations within a radius of a point.
# Return the Name, Lat, Lon, WS, and WD in a dictionary
# Test Update

import json
import urllib2
from datetime import datetime
from get_token import my_token # returns my personal token
import numpy as np

# Get your own key and token from here: https://mesowest.org/api/signup/
token = my_token()

default_vars = 'wind_speed,wind_direction,ozone_concentration,\
PM_25_concentration,air_temp,pressure'


def MWdate_to_datetime(x):
    """
    Converts a MesoWest date string to a python datetime object
    So far only works for summer months (daylight savings time). Best if you
    make all your MesoWest API calls in UTC time.

    For fastest calculations, vectorize this function before using:
    Example:
        vectorized_convert_time_function = np.vectorize(MWdate_to_datetime)
        DATES = vectorized_convert_time_function(dates)

    As my personal notation:
        DATES = list or array of python datetime object
        dates = native dates format, typically a string or number in epoch time
    """

    try:
        # print 'Times are in UTC'
        return datetime.strptime(x, '%Y-%m-%dT%H:%M:%SZ')

    except:
        # print 'Times are in Local Time'
        return datetime.strptime(x, '%Y-%m-%dT%H:%M:%S-0600')


def get_mesowest_radius(attime, within,
                        radius='kslc,30',
                        variables=default_vars):
    """
    Gets data nearest a time for all stations within a radius.

    Inputs:
        attime - A python datetime object of the desired time.
        within - A string of the number of minutes to request data from. Use
                 two numbers to request before and after attime 10,10.
        raduis - A string of the location to center the radius, followed by
                 number of {miles}.
                 Can center on a MesoWest station ID (ksl,30) like the default,
                 or center on a lat/lon (41.5,-120.25,30)

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
        + '&radius=' + radius \
        + '&obtimezone=' + tz \
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

    a = get_mesowest_radius(datetime(2016, 4, 4), '10', radius='kslc,7')
