# Brian Blaylock
# Version 2.0 update
# 07 October 2016

"""
Returns data from a grid in the HRRR model that matches the nearest latitude
and longitude point of a verification station.
"""



from datetime import datetime, timedelta

import sys
sys.path.append('C:\Users\blaylockbk\OneDrive\02_Horel Group\pyBKB_v2.0')
from pyBKB_v2.BB_data.data_manager import open_HRRR
from pyBKB_v2.BB_conversions.convert import K_to_C

import numpy as np

# HRRR_vars is a dictionary of basic HRRR variables to retreive. The value of
# each key is the short name stored in the returned data.
HRRR_vars = {'2 metre temperature': 'air_temp_2m',
             '2 metre dewpoint temperature': 'dwpt_2m',
             '10 metre U wind component': 'u10',
             '10 metre V wind component': 'v10',
             'Orography': 'ELEVATION'
            }

def pluck_point(dict, request_date, forecast_hour, vars=HRRR_vars):
    """
    Opens a HRRR surface field and plucks out the variables at a grid point
    nearest a latitude longitude point.
    Outputs a dictinary of the values.

    Input:
        dict - A dictionary of latitude and longitude points to pluck from
               the model grid. Required keys: 'LAT', 'LON', 'STID'
        request_date - Datetime object of the model time you wish to pluck.
        forecast_hour - Integer of the forecast hour. This will be converted
                        to the format 'fxx' where xx is the two digit hour.

        vars = a dictionary where is key is a variable name in the grib2 file
               and the value is the short name we will return the data as.
    """

    FILE, grbs = open_HRRR(request_date, forecast_hour)
    print "**"
    print "opened HRRR:", FILE
    print "**"

    valid_time = request_date + timedelta(hours=forecast_hour)
    print "valid date:", valid_time

    lat, lon = grbs.select(name='Orography')[0].latlons()

    grib_data = {'LAT': np.array(lat),
                 'LON': np.array(lon)
                }

    return_this = {'DATETIME': request_date,
                   'FORECAST': forecast_hour,
                   'VALID': valid_time,
                   'FILE': FILE
                  }

    # For each variable, load and store the grib data with the corresponding
    # short name. (This could take lots of meemory if you ask for a lot.)
    for i in vars:
        grib_data[vars[i]] = grbs.select(name=i)[0].values
        # empty arrays in the return data for each variable
        return_this[vars[i]] = np.array([])

    # For each station id in our dict, pluck the values for each variable

    for i in range(0, len(dict['STID'])):

        print i
        print "working on:", dict['STID'][i]

        # 1)
        # Get the HRRR data for the point nearest the MesoWest station
        # Find the nearest lat/lon in the HRRR domain for the station location
        abslat = np.abs(grib_data['LAT'] - dict['LAT'][i])
        abslon = np.abs(grib_data['LON'] - dict['LON'][i])

        # Element-wise maxima.
        # (go ahead and plot this with pcolormesh to see what I've done.)
        c = np.maximum(abslon, abslat)

        # The minimum maxima is is the nearest lat/lon.
        latlon_idx = np.argmin(c)

        # Use that index (that's the flattened array index) to get the value of
        # each variable at that point.
        return_this = {'STID': dict['STID'][i]}
        for k in grib_data.keys():
            return_this[k] = np.append(return_this[k],
                                       grib_data[k].flat[latlon_idx])

    return return_this


# --- Example -----------------------------------------------------------------
if __name__ == "__main__":
    request_date = datetime(2016, 7, 31, 0)
    stns_dict = {'LAT': np.array([40.77069]),
                 'LON': np.array([-111.96503]),
                 'STID': np.array(['KSLC'])
                }
    forecast_hour = 'f12'

    p = pluck_point(stns_dict, request_date, forecast_hour)
