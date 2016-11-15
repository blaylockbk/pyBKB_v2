# Brian Blaylock
# Version 2.0 update
# 9 November 2016

"""
Functions for loading and managing different data types and formats.
 - open_JSON (for reading MesoWest API)
 - download_UU_mobile
 - get_wyoming_sounding

"""

import urllib2
from scipy.io import netcdf
import linecache
try:
    from bs4 import BeautifulSoup
except:
    try:
        import sys
        # try getting bs4 from here...
        sys.path.append('/uufs/chpc.utah.edu/sys/installdir/anaconda/2.0.1/2.7.7/lib/python2.7/site-packages/')
        import bs4
    except:
        print 'beautiful soup is not installed'

from datetime import datetime

import numpy as np


def open_json(URL):
    """
    Retrieves a JSON file from a URL and returns the data as a python
    dictionary. This was built mainly to serve reading JSON from the MesoWest
    API. See more here: https://mesowest.org/api/

    Input:
        URL - URL string
    Output:
        data - dictionary of the JSON contents
    """
    import json

    f = urllib2.urlopen(URL)
    data = f.read()
    data = json.loads(data)
    return data


def open_NetCDF(file_name, t=0):
    """
    Opens a netcdf file (such as WRF output) and returns a dictionary with
    the file handle, as well as other more frequently used variables.

    Input:
        file_name - The path and file of the NetCDF file
    """
    nc = netcdf.netcdf_file(file_name, 'r')

    return_this = {'nc' : nc,
                   'ELEVATION' : nc.variables['HGT'],
                   'LAT' : nc.variables['XLAT'],
                   'LON' : nc.variables['XLONG'],
                   'TEMP': nc.variables['T2'],
                   'Q2' : nc.variables['Q2'],
                   'U10' : nc.variables['U10'],
                   'V10' : nc.variables['V10']
                  }

    return return_this


def open_HRRR(request_date, forecast_hour, field='sfc',
              BASE='/uufs/chpc.utah.edu/common/home/horel-group/archive/'):
    """
    Opens a grib2 HRRR file from the Horel-Group archive space.
    Uses the pygrib library installed on Meso4 on CHPC.

    Input:
        request_date - Datetime object of the model time you wish to open.
        forecast_hour - Integer of the forecast hour. This will be converted
                        to the format 'fxx' where xx is the two digit hour.
        field - the desired HRRR field. Either 'sfc', 'pfc', or 'subh'

        BASE = the basepath of the HRRR archive. This is the file path
               that preceeds the date directory e.g. (/20150601/hrrr/...).
               You may need to change the BASE if the HRRR archive has been
               compressed or you want to get data from a different directory.

    Output:
        path of the file
        grbs - A pygrib file handle object
    """
    import pygrib

    # Get the requested HRRR grib file, adjusted for the forecast hour
    y = request_date.year
    m = request_date.month
    d = request_date.day
    h = request_date.hour
    f = 'f%02d' % (forecast_hour)  # fxx

    # Open the GRIB file from the hore-group archive space.
    # Note: if you are using a custom base, you need to have this same file
    #       structure e.g. <BASE/20150607/models/hrrr/hrrr.06.wrfsfcf05.grib2>
    #       I appologize. That's just the way our archive is built.
    DIR = BASE + '%04d%02d%02d/models/hrrr/' % (y, m, d)
    FILE = 'hrrr.t%02dz.wrf%s%s.grib2' % (h, field, f)
    print "getting HRRR from:", DIR + FILE

    grbs = pygrib.open(DIR + FILE)

    return DIR_FILE, grbs

"""
# Adam Abernathy sent me this snipit. How to pipe grib2 data with wgrib2 
def read_grib_Adams_way():
    
    from subprocess import Popen, PIPE, STDOUT
    from numpy import frombuffer, roll, float32

    wgrib_path = "wgrib2"

    shell_cmd = wgrib_path + " " + args['grib_file'] + \
        " -match " + "\"" + args['grib_key'] + "\"" + \
        " -end -inv /dev/null -no_header -bin -"

    # Take the binary "slug" of data that's been piped in
    grib_binary = Popen(
        shell_cmd,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=STDOUT,
        close_fds=True
    ).stdout.read()
"""


def download_UU_mobile(platform, requested_time, previous_mins):
    """
    Downloads University of Utah Atmos. Department mobile data
    from online. See here: http: // meso2.chpc.utah.edu / gslso3s / cgi - bin / download_mobile_data.cgi
    If that page seems broken, ask Alex Jaques about it.

    This script reads the text file from the online request.

    Input:
        platform - string ID of the mobile platform: 'KSL5', 'TRX01', 'TRX01',
                   'UUTK01', 'UUTK01', or others that may be added.
        request_time - the requested time as a datetime object
        previous_mins - get a time series of for the request_time and
                        preceeding minutes.
    """

    year = str(requested_time.year).zfill(4)
    month = str(requested_time.month).zfill(2)
    day = str(requested_time.day).zfill(2)
    hour = str(requested_time.hour).zfill(2)
    minute = str(requested_time.minute).zfill(2)
    previous_mins = str(previous_mins)

    URL = 'http://meso2.chpc.utah.edu/gslso3s/cgi-bin/' \
        + 'download_mobile_data.cgi?' \
        + '&stid=' + platform \
        + 'yr=' + year \
        + '&mo=' + month \
        + '&dy=' + day \
        + '&hr=' + hour \
        + '&mm=' + minute \
        + '&min=' + previous_mins

    print platform, 'download:', URL

    rawdata = urllib2.urlopen(URL).read()
    splitted = rawdata.split("\n", rawdata.count("\n"))

    # Save a text file of the data (this makes reading it easy, and I don't
    # have to change my code I've already written)
    data_dir = './'
    filename = platform + '_' + year + month + day + hour + minute + '.txt'
    f = open(data_dir + filename, 'w')
    for line in splitted[:]:
        f.write(line + '\n')
    f.close()

    # Read File
    col_names = linecache.getline(filename, 2)

    try:
        data = np.genfromtxt(filename,
                             skip_header=2,
                             names=col_names,
                             delimiter=',',
                             dtype=None)

        # remove text file after we have the data
        print 'remove', filename
        os.remove(filename)

        # Convert Dates and Times to Datetime Object
        DATES = np.array([])
        for i in range(0, len(data['Date'])):
            a = data['Date'][i] + ' ' + data['TimeUTC'][i]
            b = datetime.strptime(a, '%Y-%m-%d %H:%M:%S')
            DATES = np.append(DATES, b)

        try:
            ozone = data['2b_ozone_ppbv']
            ozone[ozone < 0] = np.nan
        except:
            ozone = np.zeros_like(DATES) * np.nan

        try:
            pm25 = data['esampler_pm25_ugm3']
            pm25[pm25 < 0] = np.nan
        except:
            pm25 = np.zeros_like(DATES) * np.nan

        lat = data['cr1000_gpslat_dd']
        lat[lat == -9999] = np.nan
        lon = data['cr1000_gpslon_dd']
        lon[lon == -9999] = np.nan
        elevation = data['cr1000_gpselev_m']
        elevation[elevation == -9999] = np.nan

        try:
            pressure = data['cr1000_pres_hpa']
        except:
            pressure = np.zeros(len(DATES)) * np.nan

        return {'platform': platform,
                'DATES': DATES,
                'ozone': ozone,
                'pm25': pm25,
                'latitude': lat,
                'longitude': lon,
                'elevation': elevation,
                'pressure': pressure,
                'URL': URL
                }
    except:
        data = 'No Data Available from ' + platform + ' at this time'
        return data, URL


def get_wyoming_sounding(request_date, station='slc'):
    """
    June 13, 2016

    Download a sounding file from University of Wyoming Site and
    return a dictinary of the values

    Input:
        request_date - a datetime object in UTC. Hour must be either 0 or 12
        station - defaults to slc, the Salt Lake City. Alternativley use a
                  number for the station identier.

    Return:
        a dictionary of the data
    """

    if station == 'slc':
        stn = '72572'  # this is the id number for KSLC
    else:
        stn = str(station)

    year = str(request_date.year).zfill(4)
    month = str(request_date.month).zfill(2)
    day = str(request_date.day).zfill(2)
    # hour in UTC, 00 and 12 z usually available
    hour = str(request_date.hour).zfill(2)

    # Download, process and add to plot the Wyoming Data
    # 1)
    # Wyoming URL to download Sounding from
    url = 'http://weather.uwyo.edu/cgi-bin/sounding?' \
        + 'region=naconf&TYPE=TEXT%3ALIST' \
        + '&YEAR=' + year \
        + '&MONTH=' + month \
        + '&FROM=' + day + hour \
        + '&TO=' + day + hour \
        + '&STNM=' + stn
    content = urllib2.urlopen(url).read()

    # 2)
    # Remove the html tags
    soup = BeautifulSoup(content, "html.parser")
    data_text = soup.get_text()

    # 3)
    # Split the content by new line.
    splitted = data_text.split("\n", data_text.count("\n"))

    # 4)
    # Save the processed data as a .txt file to be read in by the skewt module.
    # See more here: https://pypi.python.org/pypi/SkewT
    Sounding_dir = './'
    Sounding_filename = str(stn) + '.' + str(year) + \
        str(month) + str(day) + str(hour) + '.txt'
    f = open(Sounding_dir + Sounding_filename, 'w')
    for line in splitted[4:]:
        f.write(line + '\n')
    f.close()

    # 5) Read the observed sounding file
    # Figure out where the footer is so we can skip it in np.genfromtxt
    # This is the line the data ends
    lookup = 'Station information and sounding indices'
    with open(Sounding_filename) as myFile:
        for num, line in enumerate(myFile, 1):
            if lookup in line:
                end_data_line = num
    last_line = sum(1 for line in open(Sounding_filename))
    # Not entirely sure why we need to subtract 14, but it works.
    foot = last_line - end_data_line - 14
    print last_line
    print end_data_line

    sounding = np.genfromtxt(Sounding_filename,
                             skip_header=8, skip_footer=foot)
    obs_press = sounding[:, 0]         # hPa
    obs_hght = sounding[:, 1]          # m
    obs_temp = sounding[:, 2]          # C
    obs_dwpt = sounding[:, 3]          # C
    obs_rh = sounding[:, 4]            # %
    obs_mixing = sounding[:, 5] / 1000   # kg/kg
    obs_wdir = sounding[:, 6]          # degrees
    obs_wspd = sounding[:, 7] * 0.51444  # m/s
    obs_theta = sounding[:, 8]         # K
    obs_u, obs_v = wind_calcs.wind_spddir_to_uv(obs_wspd, obs_wdir)  # m/s

    # 6)
    # Would be nice to return a diction of the station information from the
    # sounding file such as the Station identified, latitude, longitude,
    # calculated indexes, etc.

    data = {'url': url,                  # URL the data is retrived from
            'file': Sounding_filename,   # Path to the file we created
            'DATE': request_date,        # Date requested (datetime object)
            'station': str(station),     # Requested station
            'press': obs_press,
            'height': obs_hght,
            'temp': obs_temp,
            'dwpt': obs_dwpt,
            'rh': obs_rh,
            'mixing ratio': obs_mixing,
            'wdir': obs_wdir,
            'wspd': obs_wspd,
            'theta': obs_theta,
            'u': obs_u,
            'v': obs_v
            }

    return data


if __name__ == "__main__":

    import matplotlib.pyplot as plt

    request_date = datetime(2016, 6, 13, 0)
    a = get_wyoming_sounding(request_date)

    # plot a simple vertical profile
    plt.grid()
    plt.plot(a['temp'], a['height'], c='r', label='Temp')
    plt.plot(a['dwpt'], a['height'], c='g', label='Dwpt')
    plt.barbs(np.zeros_like(a['temp'])[::5], a['height'][::5],
              a['u'][::5], a['v'][::5], label='Wind')
    plt.legend()

    plt.title("%s    %s" % (a['station'], a['DATE']))
    plt.xlabel('Temperture (C)')
    plt.ylabel('Height (m)')
