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

def get_rad_sounding(request_time, stn='DEQMR'):
    """
    Gets a single profile of from the radiometer. Will return the
    observation nearest the requested time.

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


def get_rad_sounding_range(start, end, stn='DEQMR'):
    """
    Get radiometer profiles for a time range between start and end time and
    calculate the average values.
    Please don't request long time periods > a day. Joe won't be happy.

    Input:
        start - The begining time (datetime object)
        end   - The ending time (datetime object)
        stn   - The station name of the radiometer. DEQMR is in Utah.
    Return:
        profile - the averaged profile for each of the variables.
    """
    # Request these variables to make the sounding. (PRES is always requested
    # in the API query below)
    variables = 'ZENITH_TEMP,ZENITH_RH,ANGLE_A_TEMP,ANGLE_A_RH,ANGLE_N_TEMP,ANGLE_N_RH,ANGLE_S_TEMP,ANGLE_S_RH'

    # Convert datetime time to epoch time. (I think it's funny there isn't a
    # datetime function that does this for you, so use calendar module.)
    startEpoch = calendar.timegm(start.timetuple())
    endEpoch = calendar.timegm(end.timetuple())

    # Build API Query
    URL = 'https://asn.synopticdata.com/api/v1/series?senabbr=' + stn \
           + '&variables=PRES,' + variables \
           + '&Begin=' + str(startEpoch) \
           + '&End=' + str(endEpoch)
    print URL

    # Make API request and convert from JSON to python dictionary
    f = urllib2.urlopen(URL)
    data = f.read()
    data = json.loads(data)

    # Convert DATTIM to datetime object
    DATE = np.array([datetime.utcfromtimestamp(i) for i in data['DATTIM']])

    # Use average surface pressure
    PRES = np.mean(data['PRES'])

    # Calculate Pressure levels, using hypsometric equation. Step through each level
    pres_levels = np.array([PRES])
    print pres_levels
    temp_var_to_use = 'ZENITH_TEMP'
    g0 = 9.8 # m s-1
    Rd = 281 # J K-1 kg-1
    for i in range(0, len(data['HEIGHT'])-1):
        p_bot = pres_levels[-1] # get the last pressure item
        Tv = np.mean([data[temp_var_to_use][0][i], \
                      data[temp_var_to_use][0][i+1]])
        dZ = data['HEIGHT'][i+1] - data['HEIGHT'][i]
        H = Rd*Tv/g0 # scale height
        p_top = p_bot / np.exp(dZ/H)
        pres_levels = np.append(pres_levels, p_top)

    # Return a dictionary
    return_this = dict(zip(('DATE', 'URL', \
                            'ZENITH_TEMP', 'ZENITH_DWPT', \
                            'ANGLE_A_TEMP', 'ANGLE_A_DWPT', \
                            'ANGLE_N_TEMP', 'ANGLE_N_DWPT', \
                            'ANGLE_S_TEMP', 'ANGLE_S_DWPT', \
                            'PRES', 'HEIGHT', 'PRES_LEVELS' \
                            ), \
                           (DATE, URL, \
                           np.around(np.array(data['ZENITH_TEMP'])-273.15, decimals=2), np.around(TempRH_to_dwpt(np.array(data['ZENITH_TEMP'])-273.15, np.array(data['ZENITH_RH'])), decimals=2), \
                           np.around(np.array(data['ANGLE_A_TEMP'])-273.15, decimals=2), np.around(TempRH_to_dwpt(np.array(data['ANGLE_A_TEMP'])-273.15, np.array(data['ANGLE_A_RH'])), decimals=2), \
                           np.around(np.array(data['ANGLE_N_TEMP'])-273.15, decimals=2), np.around(TempRH_to_dwpt(np.array(data['ANGLE_N_TEMP'])-273.15, np.array(data['ANGLE_N_RH'])), decimals=2), \
                           np.around(np.array(data['ANGLE_S_TEMP'])-273.15, decimals=2), np.around(TempRH_to_dwpt(np.array(data['ANGLE_S_TEMP'])-273.15, np.array(data['ANGLE_S_RH'])), decimals=2), \
                           PRES, np.array(data['HEIGHT']), pres_levels \
                           )))

    return return_this

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter
    from datetime import datetime, timedelta

    request = datetime(2017, 2, 1)
    b = get_rad_sounding(request)

    
    plt.figure(1)
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


    c = get_rad_sounding_range(request-timedelta(minutes=10), request+timedelta(minutes=10))

    plt.figure(2)
    z = np.mean(c['ZENITH_TEMP'], axis=0)
    a = np.mean(c['ANGLE_A_TEMP'], axis=0)
    n = np.mean(c['ANGLE_N_TEMP'], axis=0)
    s = np.mean(c['ANGLE_S_TEMP'], axis=0)
    ALL = np.mean([z, a, n, s], axis=0)
    plt.plot(ALL, c['PRES_LEVELS'], lw=4)
    plt.plot(z, c['PRES_LEVELS'])
    plt.plot(a, c['PRES_LEVELS'])
    plt.plot(n, c['PRES_LEVELS'])
    plt.plot(s, c['PRES_LEVELS'])

    plt.gca().invert_yaxis()
    plt.yscale('log')

    plt.yticks([1000, 900, 800, 700, 600, 500, 400, 300, 200], \
            ['1000', '900', '800', '700', '600', '500', '400', '300', '200'])
    plt.grid()
    plt.ylim([1050, 200])

    plt.show(block=False)
