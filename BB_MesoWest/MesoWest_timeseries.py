# Brian Blaylock
# Version 2.0 update
# 8 November 2016                     (Trump vs. Clinton Presidential Election)

"""
A collection of functions to quickly get data from the MesoWest API

If you have imported this function you can change the "variables" variables
by reassigning:
BB_MesoWest.MesoWest_timeseries.get_mesowest_ts.func_globals['variables'] = 'new string'
except this isn't very useful at the moment because while
the function will query the additional data it wont return the additional data.

To do list:
    [X] Make returned dictionary return just the variables requested.
    [ ] Input will take one or more station IDs.
    [ ] Fix MW_date to datetime function to accept any time zone.
    [ ] User specified the time zone if desired (UTC vs local)
    [ ] Incorporate multiple sets instead of grabbing just set_1 by default.
        This is important for grabbing the right sets for ozone for select
        stations.
    [ ] Indicate when a returned variable is a derived variable.
    [ ] For cases when blank data may be returned, replace with np.nan.
    [ ] Create a "load JSON function with only the URL input"
    [ ] Move all MesoWest functions into it's own class,
        and other general functions into another class.

Default variables returned should be:
    - temperature
    - humidity
    - wind direction
    - wind speed
    - altimeter
else, require the user to change the requested variables.
"""

# Function for getting MesoWest time series from the API for one station

from datetime import datetime
import json
import urllib2
from get_token import my_token # returns my personal token
from convert_MW_date import MWdate_to_datetime

import numpy as np

# Get your own key and token from here: https://mesowest.org/api/signup/
token = my_token()

# String of some MesoWest variables available from this list:
# https://synopticlabs.org/api/mesonet/variables/
default_vars = 'altimeter,pressure,sea_level_pressure,wind_direction,\
wind_speed,air_temp,relative_humidity,dew_point_temperature,wind_gust'


def get_mesowest_ts(stationID, start_time, end_time, variables=default_vars, verbose=True):
    """
    Get MesoWest Time Series:
    Makes a time series query from the MesoWest API for a single station.

    Note: Put all print statements under "if verbose==True:" because some of my 
    cgi scripts cannot deal with printed statements.

    Input:
        stationID  : string of the station ID (a single station)
        start_time : datetime object of the start time in UTC
        end_time   : datetime object of the end time in UTC
        verbose    : print out some diagnostics, defualt is True

    Output:
        A dictionary of the data.
    """

    # Convert the start and end time to the string format requried by the API
    start = start_time.strftime("%Y%m%d%H%M")
    end = end_time.strftime("%Y%m%d%H%M")
    tz = 'utc'  # This is hard coded for now. Local time could be added later.

    # The API request URL
    URL = 'http://api.mesowest.net/v2/stations/timeseries?&token=' + token \
        + '&stid=' + stationID \
        + '&start=' + start \
        + '&end=' + end \
        + '&vars=' + variables \
        + '&obtimezone=' + tz \
        + '&output=json'

    try:
        # Just try everything first.
        # If it doens't work, return an error message with the URL for
        # debugging

        # Open URL and read JSON content. Convert JSON string to some python
        # readable format.
        f = urllib2.urlopen(URL)
        data = f.read()
        data = json.loads(data)

        # Store the data we will return in this new dictionary
        return_this = {}

        # Get basic station information
        return_this['URL'] = URL
        return_this['NAME'] = str(data['STATION'][0]['NAME'])
        return_this['STID'] = str(data['STATION'][0]['STID'])
        return_this['LAT'] = float(data['STATION'][0]['LATITUDE'])
        return_this['LON'] = float(data['STATION'][0]['LONGITUDE'])
        return_this['ELEVATION'] = float(data['STATION'][0]['ELEVATION'])
                                      # Note: Elevation is in feet, NOT METERS!


        # Dynamically create keys in the dictionary for each requested variable
        for v in data['STATION'][0]['SENSOR_VARIABLES'].keys():
            if v == 'date_time':
                # Dates: Convert the strings to a python datetime object.mro
                dates = data["STATION"][0]["OBSERVATIONS"]["date_time"]
                converttime = np.vectorize(MWdate_to_datetime)
                return_this['DATETIME'] = converttime(dates)

            else:
                # v represents all the variables, but each variable may have
                # more than one set.
                # For now, just return the first set.
                key_name = str(v)
                set_num = 0

                grab_this_set = str(data['STATION'][0]['SENSOR_VARIABLES']\
                                    [key_name].keys()[set_num])

                # Always grab the first set (either _1 or _1d)
                # should make exceptions to this rule for certain stations and certain variables
                if grab_this_set[-1] != '1' and grab_this_set[-1] != 'd':
                    grab_this_set = grab_this_set[0:-1]+'1'
                if grab_this_set[-1] == 'd':
                    grab_this_set = grab_this_set[0:-2]+'1d'

                variable_data = np.array(data['STATION'][0]['OBSERVATIONS']\
                                        [grab_this_set], dtype=np.float)
                return_this[key_name] = variable_data


        return return_this


        ## Air Quality Variable Exceptions that need to be incorporated soon
        """
        try:
            if (stn_id == 'FWP') or (stn_id == 'LMS') or (stn_id == 'GSLM'):
                ozone_raw = data['STATION'][0]["OBSERVATIONS"]["ozone_concentration_set_2"]
                ##Look for blank data and replace with None
                for v in np.arange(0, len(ozone_raw)):
                    if ozone_raw[v] == '':
                            ozone_raw[v] = None
                ozone = np.array(ozone_raw, dtype=np.float)

            else:
                ozone_raw = data['STATION'][0]["OBSERVATIONS"]["ozone_concentration_set_1"]
                ##Look for blank data and replace with None
                for v in np.arange(0, len(ozone_raw)):
                    if ozone_raw[v] == '':
                        ozone_raw[v] = None
                ozone = np.array(ozone_raw, dtype=np.float)
        """

    except:
        # If it doens't work, then return the URL for debugging.
        if verbose==True:
            print 'Errors loading:', URL
        return 'ERROR'


#--- Example -----------------------------------------------------------------#
if __name__ == "__main__":

    import matplotlib.pyplot as plt
    from datetime import timedelta

    # Get MesoWest data from functin above
    station = 'NAA'
    start_time = datetime(2016, 9, 25)
    end_time = datetime(2016, 9, 26)

    a = get_mesowest_ts(station, start_time, end_time)

    # Make a quick temperature plot
    temp = a['air_temp']
    RH = a['relative_humidity']
    dates = a['DATETIME']

    #convert dates from UTC to mountain time (-6 hours)
    dates = dates - timedelta(hours=6)

    fig = plt.figure(figsize=(8, 4))
    plt.title(station)
    plt.xticks(rotation=30)
    plt.xlabel('Date Time MDT')

    ax1 = fig.add_subplot(111)
    ax1.plot(dates, temp, 'r')
    ax1.set_ylabel('Temperature (c)')
    ax2 = ax1.twinx()
    ax2.plot(dates, RH, 'g')
    ax2.set_ylabel('Relative Humidity (%)')

    plt.show()
