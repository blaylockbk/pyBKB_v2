# Brian Blaylock
# July 27, 2017                  Still excited about getting married to Rachel!
"""
Functions copied from pyBKB_v2/BB_downloads/HRRR_S3.py for use on the OSG
"""


import os
import pygrib
from datetime import datetime, timedelta
import urllib2
import ssl
import re
import numpy as np
import multiprocessing

def wind_uv_to_spd(U, V):
    """
    Calculates the wind speed from the u and v wind components
    Inputs:
      U = west / east direction(wind from the west is positive, from the east is negative)
      V = south / noth direction(wind from the south is positive, from the north is negative)
    """
    try:
        WSPD = np.sqrt(np.square(U) + np.square(V))
    except:
        # why didn't numpy work???
        WSPD = (U*U + V*V)**(.5)
    return WSPD

def get_hrrr_variable(DATE, variable,
                      fxx=0,
                      model='hrrr',
                      field='sfc',
                      removeFile=True,
                      value_only=False,
                      verbose=True,
                      outDIR='./'):
    """
    Uses cURL to grab just one variable from a HRRR grib2 file on the MesoWest
    HRRR archive.

    Input:
        DATE - the datetime(year, month, day, hour) for the HRRR file you want
               This must be in UTC, obviouslly.
        variable - a string describing the variable you are looking for.
                   Refer to the .idx files here: https://api.mesowest.utah.edu/archive/HRRR/
                   You want to put the variable short name and the level information
                   For example, for 2m temperature: 'TMP:2 m above ground'
        fxx - the forecast hour you desire. Default is the anlaysis hour.
        model - the model you want. Options include ['hrrr', 'hrrrX', 'hrrrAK']
        field - the file type your variable is in. Options include ['sfc', 'prs']
        removeFile - True will remove the grib2 file after downloaded. False will not.
        value_only - Only return the values. Fastest return speed if set to True, when all you need is the value.
                     Return Time .75-1 Second if False, .2 seconds if True.
        verbose - prints some stuff out
    """
    # Model direcotry names are named differently than the model name.
    if model == 'hrrr':
        model_dir = 'oper'
    elif model == 'hrrrX':
        model_dir = 'exp'
    elif model == 'hrrrAK':
        model_dir = 'alaska'


    # Temp file name has to be very unique, else when we use multiprocessing we
    # might accidentally delete files before we are done with them.
    outfile = '%stemp_%04d%02d%02d%02d_f%02d_%s.grib2' % (outDIR, DATE.year, DATE.month, DATE.day, DATE.hour, fxx, variable[:3])

    if verbose is True:
        print outfile

    # Dear User,
    # Only HRRR files for the previous day have been transfered to Pando.
    # That means if you are requesting data for today, you need to get it from
    # the NOMADS website. Good news, it's an easy fix. All we need to do is 
    # redirect you to the NOMADS URLs. I'll check that the date you are
    # requesting is not for today's date. If it is, then I'll send you to
    # NOMADS. Deal? :)
    #                                                    -Sincerely, Brian
    UTC = datetime.utcnow() # the current date in UTC
    if DATE < datetime(UTC.year, UTC.month, UTC.day):
        # Get HRRR from Pando
        if verbose is True:
            print "Oh, good, you requested a date that should be on Pando."
        # URL for the grib2.idx file
        fileidx = 'https://api.mesowest.utah.edu/archive/HRRR/%s/%s/%04d%02d%02d/%s.t%02dz.wrf%sf%02d.grib2.idx' \
                    % (model_dir, field, DATE.year, DATE.month, DATE.day, model, DATE.hour, field, fxx)
        # URL for the grib2 file (located on PANDO S3 archive)
        pandofile = 'https://pando-rgw01.chpc.utah.edu/HRRR/%s/%s/%04d%02d%02d/%s.t%02dz.wrf%sf%02d.grib2' \
                    % (model_dir, field, DATE.year, DATE.month, DATE.day, model, DATE.hour, field, fxx)
    else:
        # Get HRRR from NOMADS
        if verbose is True:
            print "\n-----------------------------------------------------------------------"
            print "!! Hey! You are requesting a date that is not on the Pando archive  !!"
            print "!! That's ok, I'll redirect you to the NOMADS server. :)            !!"
            print "-----------------------------------------------------------------------\n"
        # URL for the grib2 idx file
        fileidx = 'http://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod/hrrr.%04d%02d%02d/%s.t%02dz.wrf%sf%02d.grib2.idx' \
                    % (DATE.year, DATE.month, DATE.day, model, DATE.hour, field, fxx)
        # URL for the grib2 file (located on NOMADS server)
        pandofile = 'http://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod/hrrr.%04d%02d%02d/%s.t%02dz.wrf%sf%02d.grib2' \
                    % (DATE.year, DATE.month, DATE.day, model, DATE.hour, field, fxx)

    try:
        # 0) Read in the grib2.idx file
        try:
            # ?? Ignore ssl certificate (else urllib2.openurl wont work).
            #    Depends on your version of python.
            #    See here:
            #    http://stackoverflow.com/questions/19268548/python-ignore-certicate-validation-urllib2
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            idxpage = urllib2.urlopen(fileidx, context=ctx)
        except:
            idxpage = urllib2.urlopen(fileidx)

        lines = idxpage.readlines()

        # 1) Find the byte range for the variable. Need to first find where the
        #    variable is located. Keep a count (gcnt) so we can get the end
        #    byte range from the next line.
        gcnt = 0
        for g in lines:
            expr = re.compile(variable)
            if expr.search(g):
                if verbose is True:
                    print 'matched a variable', g
                parts = g.split(':')
                rangestart = parts[1]
                parts = lines[gcnt+1].split(':')
                rangeend = int(parts[1])-1
                if verbose is True:
                    print 'range:', rangestart, rangeend
                byte_range = str(rangestart) + '-' + str(rangeend)
                # 2) When the byte range is discovered, use cURL to download.
                os.system('curl -s -o %s --range %s %s' % (outfile, byte_range, pandofile))
            gcnt += 1

        # 3) Get data from the file, using pygrib
        grbs = pygrib.open(outfile)
        if value_only is True:
            value = grbs[1].values
            # (Remove the temporary file)
            #    ?? Is it possible to push the data straight from curl to ??
            #    ?? pygrib, without writing/removing a temp file? and     ??
            #    ?? would that speed up this process?                     ??
            if removeFile is True:
                os.system('rm -f %s' % (outfile))
            return {'value': value}

        else:
            value, lat, lon = grbs[1].data()
            validDATE = grbs[1].validDate
            anlysDATE = grbs[1].analDate
            msg = str(grbs[1])

            # 4) Remove the temporary file
            if removeFile == True:
                os.system('rm -f %s' % (outfile))

            # 5) Return some import stuff from the file
            return {'value': value,
                    'lat': lat,
                    'lon': lon,
                    'valid': validDATE,
                    'anlys': anlysDATE,
                    'msg':msg}

    except:
        print " ! Could not get the file:", pandofile
        print " ! Is the variable right?", variable
        print " ! Does the file exist?", fileidx
        return {'value' : None,
                'lat' : None,
                'lon' : None,
                'valid' : None,
                'anlys' : None,
                'msg' : None}