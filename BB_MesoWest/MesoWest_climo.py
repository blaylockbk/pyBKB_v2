# Brian Blaylock
# Version 2.0 update
# 9 November 2016                (The day Trump won the presidential election)

# Plot the temperature climotology for a station's lifetime

from datetime import datetime
import json
import urllib2
from get_token import my_token # returns my personal token
from convert_MW_date import MWdate_to_datetime

import numpy as np


# Get your own key and token from here: https://mesowest.org/api/signup/
token = my_token()


def get_mesowest_climatology(station, start, end):
    """
    Get data from MesoWest Climatology service for a station between two dates.

    Input:
        station - MesoWest station id as a string.a
        start - 'mmddHHMM'
        end - 'mmddHHMM'

    To Do: 
    [ ] Somehow convert the input as a datetime object, not string
    """
    # Convert datetime object to MesoWest input date string

    tz = 'utc'

    URL = 'http://api.mesowest.net/v2/stations/climatology?&token=' + token \
        + '&stid=' + station \
        + '&startclim=' + start \
        + '&endclim=' + end \
        + '&obtimezone=' + tz

    # Open URL and read JSON content. Convert JSON string to some python
    # readable format.
    f = urllib2.urlopen(URL)
    data = f.read()
    data = json.loads(data)

    return_this = {'URL': URL,
                   'NAME': np.array([]),
                   'STID': np.array([]),
                   'LAT': np.array([]),
                   'LON': np.array([]),
                   'ELEVATION': np.array([]),  # Note: Elevation is in feet.
                   'data': data
                   }

    for i in data['STATION']:
        return_this['NAME'] = np.append(return_this['NAME'], str(i['NAME']))
        return_this['STID'] = np.append(return_this['STID'], str(i['STID']))
        return_this['LAT'] = np.append(
            return_this['LAT'], float(i['LATITUDE']))
        return_this['LON'] = np.append(
            return_this['LON'], float(i['LONGITUDE']))
        return_this['ELEVATION'] = np.append(
            return_this['ELEVATION'], float(i['LONGITUDE']))

        return_this['air_temp'] = np.array(
            i['OBSERVATIONS']['air_temp_set_1'], dtype=float)

        # Convert all these to a datetime object
        vectorized_convert_time = np.vectorize(MWdate_to_datetime)
        return_this['DATETIME'] = vectorized_convert_time(
            i['OBSERVATIONS']['date_time'])
    return return_this


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    MONTH = np.array([])
    AVG_Temp = np.array([])
    MAX_Temp = np.array([])
    MIN_Temp = np.array([])

    station = 'UKBKB'

    months = np.arange(1, 13)
    for m in months:
        start = '%02d010000' % (m)
        end = '%02d280000' % (m)

        a = get_mesowest_climatology(station, start, end)

        MONTH = np.append(MONTH, m)

        avg_temp = np.nanmean(a['air_temp'])
        AVG_Temp = np.append(AVG_Temp, avg_temp)
        MAX_Temp = np.append(MAX_Temp, np.nanmax(a['air_temp']))
        MIN_Temp = np.append(MIN_Temp, np.nanmin(a['air_temp']))

    plt.plot(MONTH, MAX_Temp, label='Max')
    plt.plot(MONTH, AVG_Temp, label='Mean')
    plt.plot(MONTH, MIN_Temp, label='Min')
    plt.title(station
              + "\n"
              + a['DATETIME'][0].strftime('%b %Y')
              + ' to '
              + a['DATETIME'][-1].strftime('%b %Y'))
    plt.xlabel('Month')
    plt.ylabel('Temperature (C)')
    plt.legend()
    plt.xlim([1, 12])
    plt.show()
