
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

def get_mesowest_percentiles(stn, variable='air_temp',
                             percentiles=[0,5,25,50,75,95,100],
                             start = '010100',
                             end = '123123',
                             psource='PERCENTILES2', v=False):
    """
    Station history percentiles for a single station and single variable:
    Uses a 30 day window centered on the hour.
    Data at top of each hour of the year, including leap year.
    DATETIME is set to year 2016 to include leap year, but data is not limited to the year.
    
    stn = a mesowest station ID (only one station)
    variable = a mesowest API variable string (only one variable)
    start = '010100' MMDDHH 
    end = '123123' MMDDHH
    psource = 'PERCENTILES2' or 'PERCENTILES_HRRR'

    """
    
    if percentiles == 'ALL':
            URL = 'http://api.synopticlabs.org/v2/percentiles?&token=' + token \
          + '&start=' + start \
          + '&end=' + end \
          + '&vars=' + variable \
          + '&stid=' + stn \
          + '&psource=' + psource
    else:
        URL = 'http://api.synopticlabs.org/v2/percentiles?&token=' + token \
            + '&start=' + start \
            + '&end=' + end \
            + '&vars=' + variable \
            + '&stid=' + stn \
            + '&percentiles=' + ','.join([str(p) for p in percentiles]) \
            + '&psource=' + psource

    if v==True:
        # verbose
        print "MesoWest API Query: ",URL    
    
    ##Open URL and read the content
    f = urllib2.urlopen(URL)
    data = f.read()

    ##Convert that json string into some python readable format
    data = json.loads(data)
    d = data['STATION'][0]

    return_this = {'URL': URL,
                   'STID': d['STID'],
                   'NAME': d['NAME'],
                   'ELEVATION': float(d['ELEVATION']),
                   'LATITUDE': float(d['LATITUDE']),
                   'LONGITUDE': float(d['LONGITUDE']),
                   'variable': variable,
                   'counts': np.array(d['PERCENTILES'][variable+'_counts_1'], dtype='int'),
                   'DATETIME': np.array([datetime(2016, int(DATE[0:2]), int(DATE[2:4]), int(DATE[4:6])) for DATE in d['PERCENTILES']['date_time']])
                   }
    if psource == 'PERCENTILES2':
        return_this['years'] = np.array(d['PERCENTILES'][variable+'_years_1'], dtype='int')

    all_per = np.array(d['PERCENTILES'][variable+'_set_1'])
    for i, p in enumerate(data['PERCENTILE_LIST']):
        return_this['p%02d' % p] = all_per[:,i]
            
    return return_this
    

#--- Example -----------------------------------------------------------------#
if __name__ == "__main__":
    a = get_mesowest_percentiles('WBB')
    b = get_mesowest_percentiles('WBB', psource="PERCENTILES_HRRR")
    
    
    
    
