# Brian Blaylock
# February 1, 2017


"""
Get radiometer data from the SynopticLabs Above Surface Network (ASN) API for
DEQMR. Return data as well as derived variables pressure levels and dew point.

See documentation: https://asn.synopticdata.com/networks/metadata/#DAQMR
"""

from datetime import datetime
import calendar
import json
import urllib2
import numpy as np

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
sys.path.append('B:\pyBKB_v2')
from BB_wx_calcs.humidity import TempRH_to_dwpt, TempRH_to_dwpt_2

def get_sounding(request_time, stn='DEQMR'):
    """
    Get the data needed to create a sounding profile. The time range request
    will return multiple instances. The API is set up this way because the
    radiometer makes profiles at approximate 5 min intervals.

    Input:
        request_time - The requested datetime (datetime object).

    """
    # Request these variables to make the sounding. (PRES is always requested
    # in the API query below)
    variables = 'ZENITH_TEMP,ZENITH_RH,ANGLE_A_TEMP,ANGLE_A_RH,ANGLE_N_TEMP,ANGLE_N_RH,ANGLE_S_TEMP,ANGLE_S_RH'

    # Convert datetime time to epoch time. (I think it's funny there isn't a
    # datetime function that does this for you, so use calendar module.)
    requestEpoch = calendar.timegm(request_time.timetuple())

    # Build API Query
    URL = 'https://asn.synopticdata.com/api/v1/single?senabbr=' + stn \
           + '&variables=PRES,' + variables \
           + '&time=' + str(requestEpoch) \
           + '&within=3600'
    print URL

    # Make API request and convert from JSON to python dictionary
    f = urllib2.urlopen(URL)
    data = f.read()
    data = json.loads(data)

    # Convert DATTIM to datetime object
    DATE = datetime.utcfromtimestamp(data['DATTIM'])

    # Return some data:

    # 1. Return the general, single item data
    return_this = {'URL':URL,
                   'Station': stn,
                   'DATETIME': DATE,
                   'Requested': request_time, # return the requested datetime
                   'PRES':data['PRES'],
                  }

    # 2. Return all list variables, converted to numpy and truncated to 2 decimals
    for i in data.keys():
        try:
            if isinstance(data[i], list):
                if i == 'HEIGHT':
                    return_this['HEIGHT'] = np.array(data['HEIGHT'])
                elif data[i][0] > 150:
                    # The data is probably in Kelvin, so convert to Celsius
                    return_this[str(i)] = np.around(data[i], decimals=2) - 273.15
                else:
                    return_this[str(i)] = np.around(data[i], decimals=2)
        except:
            print "ERROR: get_sounding -> couldn't do nothin' with", i

    # 3. Return some derived variables if those variables were requested
    # 3.a. Temp and RH to dewpoint
    try:
        temp = np.array(data['ZENITH_TEMP'])-273.15
        rh = np.array(data['ZENITH_RH'])
        zenith_dwpt = TempRH_to_dwpt(temp, rh)
        return_this['ZENITH_DWPT'] = np.around(zenith_dwpt, decimals=2)
    except:
        print "no zenith_dwpt"
    try:
        temp = np.array(data['ANGLE_A_TEMP'])-273.15
        rh = np.array(data['ANGLE_A_RH'])
        zenith_dwpt = TempRH_to_dwpt(temp, rh)
        return_this['ANGLE_A_DWPT'] = np.around(zenith_dwpt, decimals=2)
    except:
        print "no angle_a_dwpt"
    try:
        temp = np.array(data['ANGLE_N_TEMP'])-273.15
        rh = np.array(data['ANGLE_N_RH'])
        zenith_dwpt = TempRH_to_dwpt(temp, rh)
        return_this['ANGLE_N_DWPT'] = np.around(zenith_dwpt, decimals=2)
    except:
        print "no angle_n_dwpt"
    try:
        temp = np.array(data['ANGLE_S_TEMP'])-273.15
        rh = np.array(data['ANGLE_S_RH'])
        zenith_dwpt = TempRH_to_dwpt(temp, rh)
        return_this['ANGLE_S_DWPT'] = np.around(zenith_dwpt, decimals=2)
    except:
        print "no angle_s_dwpt"

    # 3.b. Pressure levels, using hypsometric equation. Step through each level
    pres_levels = np.array([return_this['PRES']])
    temp_var_to_use = 'ZENITH_TEMP'
    g0 = 9.8 # m s-1
    Rd = 281 # J K-1 kg-1
    for i in range(0, len(return_this['HEIGHT'])-1):
        p_bot = pres_levels[-1] # get the last pressure item
        Tv = np.mean([return_this[temp_var_to_use][i], \
                      return_this[temp_var_to_use][i+1]]) + 273.15
        dZ = return_this['HEIGHT'][i+1] - return_this['HEIGHT'][i]
        H = Rd*Tv/g0 # scale height
        p_top = p_bot / np.exp(dZ/H)
        pres_levels = np.append(pres_levels, p_top)
    return_this['PRES_LEVELS'] = pres_levels

    return return_this


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter
    import math

    request = datetime(2017, 2, 1)
    b = get_sounding(request)

    plt.plot(b['ZENITH_TEMP'], b['PRES_LEVELS'], color='r')
    plt.plot(b['ZENITH_DWPT'], b['PRES_LEVELS'], color='r')
    plt.plot(b['ANGLE_A_TEMP'], b['PRES_LEVELS'], color='g')
    plt.plot(b['ANGLE_A_DWPT'], b['PRES_LEVELS'], color='g')
    plt.plot(b['ANGLE_N_TEMP'], b['PRES_LEVELS'], color='b')
    plt.plot(b['ANGLE_N_DWPT'], b['PRES_LEVELS'], color='b')
    plt.plot(b['ANGLE_S_TEMP'], b['PRES_LEVELS'], color='k')
    plt.plot(b['ANGLE_S_DWPT'], b['PRES_LEVELS'], color='k')
    plt.gca().invert_yaxis()
    plt.yscale('log')
    plt.yticks([1000, 900, 800, 700, 600, 500, 400, 300, 200], \
               ['1000', '900', '800', '700', '600', '500', '400', '300', '200'])
    plt.grid()
    plt.ylim([1050, 200])

    plt.show(block=False)
