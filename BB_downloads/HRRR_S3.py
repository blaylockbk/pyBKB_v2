# March 14, 2017                                           It's Pi Day!! (3.14)
# Brian Blaylock

"""
Get data from a HRRR grib2 file on the MesoWest HRRR S3 Archive
Requires cURL

Contents:
    get_hrrr_variable()            - Returns dict of sinlge HRRR variable
    get_hrrr_variable_multi()      - Returns dict of multiple HRRR variables
    pluck_hrrr_point()             - Returns valid time and plucked value from lat/lon
    points_for_multipro()          - Feeds variables from multiprocessing for timeseries
    point_hrrr_time_series()       - Returns HRRR time serience (main function)
    point_hrrr_time_series_multi() - Returns dictionary of the HRRR timeseris for multiple stations
    get_hrrr_pollywog()            - Returns vector of the HRRR pollywog
    get_hrrr_pollywog_multi()      - Returns dictionary of the HRRR pollywog for multiple stations

    The difference between a time series and a pollywog is that:
        - a time series is for the analysis hours, f00, for any length of time.
        - a pollywog is the full forecast cycle, i.e. f00-f18

# (Remove the temporary file)
#    ?? Is it possible to push the data straight from curl to ??
#    ?? pygrib, without writing/removing a temp file? and     ??
#    ?? would that speed up this process?                     ??
"""


import os
import pygrib
from datetime import datetime, timedelta
import urllib2
from ftplib import FTP
import ssl
import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import multiprocessing

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
from BB_wx_calcs.wind import wind_uv_to_spd

def get_hrrr_variable(DATE, variable,
                      fxx=0,
                      model='hrrr',
                      field='sfc',
                      removeFile=True,
                      value_only=False,
                      verbose=True,
                      outDIR='./'):
    """
    Uses cURL to grab the requested variable from a HRRR grib2 file in the
    HRRR archive. Uses the the requested variable string to search the .idx
    file and determine the byte range. When the byte range of a variable is
    known, cURL is capable of downloading a single variable from a larger GRIB2
    file. This function packages the data in a dictionary.

    Input:
        DATE       - The datetime(year, month, day, hour) for the HRRR file you
                     want. This is the same as the model run time, in UTC.
        variable   - A string describing the variable you are looking for in the
                     GRIB2 file. Refer to the .idx files. For example:
                        https://pando-rgw01.chpc.utah.edu/hrrr/sfc/20180101/hrrr.t00z.wrfsfcf00.grib2.idx
                     You want to put the variable short name and the level
                     information. For example, for 2m temperature:
                        variable='TMP:2 m above ground'
        fxx        - The forecast hour you desire. Default is the analysis hour,
                     or f00.
        model      - The model you want. Options include ['hrrr', 'hrrrX', 'hrrrak']
        field      - The file output type. Options include ['sfc', 'prs']
        removeFile - True: remove the GRIB2 file after it is downloaded
                     False: do not remove the GRIB2 file after it is downloaded
        value_only - True: only return the values, not the lat/lon.
                        Returns output in 0.2 seconds
                     False: returns value and lat/lon, grib message, analysis and valid datetime.
                        Returns output in 0.75-1 seconds
        verbose    - Prints some diagnostics
        outDIR     - Specify where the downloaded data should be downloaded.
                     Default is the current directory. 

    Tips:
        1. The DATE you request represents the model run time. If you want to
           retrieve the file based on the model's valid time, you need to
           offset the DATE with the forecast lead time. For example:
                VALID_DATE = datetime(year, month, day, hour)   # We want the model data valid at this time
                fxx = 15                                        # Forecast lead time
                RUN_DATE = VALID_DATE-timedelta(hours=fxx)      # The model run datetime that produced the data
                get_hrrr_variable(RUN_DATE, 'TMP:2 m', fxx=fxx) # The returned data will be a forecast for the requested valid time and lead time
        
        2. You can request both U and V components at a level by using
                variable='UVGRD:10 m'
            This special request will return the U and V component winds
            converted from grid-relative to earth-relative, as well as the 
            calculated wind speed.
            Note: You can still get the grid-relative winds by requesting both
                  'UGRD:10 m' and 'VGRD:10 m' individually.
    """

    ## --- Catch Errors -------------------------------------------------------
    if model not in ['hrrr', 'hrrrX', 'hrrrak']:
        raise ValueError("Requested model must be 'hrrr', 'hrrrX', or 'hrrrak'")
    if field not in ['prs', 'sfc']:
        raise ValueError("Requested field must be 'prs' or 'sfc'. We do not store other fields in the archive")
    if model == 'hrrr' and fxx not in range(19):
        raise ValueError("HRRR: fxx must be between 0 and 18")
    elif model == 'hrrrX' and fxx != 0:
        raise ValueError("HRRRx: fxx must be 0. We do not store other forecasts in the archive.")
    elif model == 'hrrrak' and fxx not in range(37):
        raise ValueError("HRRRak: fxx must be between 0 and 37")
    ## ---(Catch Errors)-------------------------------------------------------


    ## --- Temporary File Name ---
    # Temporary file name has to be unique, or else when we use multiprocessing
    # we might accidentally delete files before we are done with them.
    outfile = '%stemp_%s_f%02d_%s.grib2' % (outDIR, DATE.strftime('%Y%m%d%H'), fxx, variable[:3])

    if verbose is True:
        print 'Dowloading tempfile: %s' % outfile


    ## --- Requested Variable ---
    # A special variable request is 'UVGRD:[level]' which will get both the U
    # and V wind components converted to earth-relative direction in a single
    # download. Since UGRD always proceeds VGRD, we will set the get_variable
    # as UGRD. Else, set get_variable as variable.
    if variable.split(':')[0] == 'UVGRD':
        # We need both U and V to convert winds from grid-relative to earth-relative
        get_variable = 'UGRD:' + variable.split(':')[1]
    else:
        get_variable = variable


    ## --- Data Source ---
    # Dear User,
    # Only HRRR files for the previous day have been transferred to Pando.
    # That means if you are requesting data for today, you need to get it from
    # the NOMADS website. Good news, it's an easy fix. All we need to do is 
    # redirect you to the NOMADS URLs. I'll check that the date you are
    # requesting is not for today's date. If it is, then I'll send you to
    # NOMADS. Deal? :)
    #                                             -Sincerely, Brian
    
    if DATE+timedelta(hours=fxx) < datetime.utcnow()-timedelta(hours=6):
        # Get HRRR from Pando
        if verbose is True:
            print "Oh, good, you requested a date that should be on Pando."
        pandofile = 'https://pando-rgw01.chpc.utah.edu/%s/%s/%s/%s.t%02dz.wrf%sf%02d.grib2' \
                    % (model, field,  DATE.strftime('%Y%m%d'), model, DATE.hour, field, fxx)
        fileidx = pandofile+'.idx'
    else:
        # Get operational HRRR from NOMADS
        if model == 'hrrr':
            if verbose is True:
                print "\n-----------------------------------------------------------------------"
                print "!! Hey! You are requesting a date that is not on the Pando archive  !!"
                print "!! That's ok, I'll redirect you to the NOMADS server. :)            !!"
                print "-----------------------------------------------------------------------\n"
            # URL for the grib2 file (located on NOMADS server)
            pandofile = 'http://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod/hrrr.%s/%s.t%02dz.wrf%sf%02d.grib2' \
                        % (DATE.strftime('%Y%m%d'), model, DATE.hour, field, fxx)
            fileidx = pandofile+'.idx'
        # or, get experiemtnal HRRR from ESRL
        elif model == 'hrrrX':
            print "\n-----------------------------------------------------------------------"
            print "!! I haven't download that Experimental HRRR run from ESRL yet      !!"
            print "-----------------------------------------------------------------------\n"
            return None
        elif model == 'hrrrak':
            if verbose is True:
                print "\n-----------------------------------------------------------------------"
                print "!! Hey! You are requesting a date that is not on the Pando archive  !!"
                print "!! That's ok, I'll redirect you to the PARALLEL NOMADS server. :)   !!"
                print "-----------------------------------------------------------------------\n"
            # URL for the grib2 file (located on the PARALLEL NOMADS server)
            if model =='hrrrak':
                DOMAIN = 'alaska'
            elif model == 'hrrr':
                DOMAIN = 'conus'
            NOMADS = 'http://para.nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/para/hrrr.%s/%s/' \
                        % (DATE.strftime('%Y%m%d'), DOMAIN)
            FILE = 'hrrr.t%02dz.wrf%sf%02d.ak.grib2' % (DATE.hour, field, fxx)
            pandofile = NOMADS+FILE    
            fileidx = pandofile+'.idx'

    if verbose:
        print pandofile

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
            expr = re.compile(get_variable)
            if expr.search(g):
                if verbose is True:
                    print 'matched a variable', g
                parts = g.split(':')
                rangestart = parts[1]
                if variable.split(':')[0] == 'UVGRD':
                    parts = lines[gcnt+2].split(':')
                else:
                    parts = lines[gcnt+1].split(':')
                rangeend = int(parts[1])-1
                if verbose is True:
                    print 'range:', rangestart, rangeend
                byte_range = str(rangestart) + '-' + str(rangeend)
                # 2) When the byte range is discovered, use cURL to download.
                os.system('curl -s -o %s --range %s %s' % (outfile, byte_range, pandofile))
            gcnt += 1

        # If the file is for Alaska, we have to regrid and change to earth relative winds:
        if model == 'hrrrak':
            # wgrib2 documentation: http://www.cpc.ncep.noaa.gov/products/wesley/wgrib2/new_grid.html
            # command from Taylor McCorkle
            wgrib2 = '/uufs/chpc.utah.edu/sys/installdir/wgrib2/2.0.2/wgrib2/wgrib2'
            # regrid = 'latlon -175.75:1800:0.0269 46.863:1000:0.0269' # Old Alaska Domain
            regrid = 'nps:225.000000:60.000000 185.117126:1299:3000.000000 41.612949:919:3000.000000'
            os.system('%s %s -new_grid_winds earth -new_grid %s %s' % (wgrib2, outfile, regrid, outfile+'.earth'))
            os.system('rm -f %s' % outfile) # remove the original file
            outfile = outfile+'.earth'     # assign the `outfile` as the regridded file so we can remove it later


        # 3) Get data from the file, using pygrib
        grbs = pygrib.open(outfile)
        if value_only is True:
            if variable.split(':')[0] == 'UVGRD':
                value1 = grbs[1].values
                value2 = grbs[2].values
                if removeFile is True:
                    os.system('rm -f %s' % (outfile))
                return {'UGRD': value1,
                        'VGRD': value2,
                        'SPEED': wind_uv_to_spd(value1, value2)}
            else:
                value = grbs[1].values
                if removeFile is True:
                    os.system('rm -f %s' % (outfile))
                return {'value': value}

        else:
            if variable.split(':')[0] == 'UVGRD':
                value1, lat, lon = grbs[1].data()
                validDATE = grbs[1].validDate
                anlysDATE = grbs[1].analDate
                msg1 = str(grbs[1])
                value2 = grbs[2].values
                msg2 = str(grbs[2])
                if model == 'hrrrak':
                    lon[lon>0] -= 360
                #
                # 4) Remove the temporary file
                if removeFile == True:
                    os.system('rm -f %s' % (outfile))
                #
                # 5) Return some import stuff from the file
                if model == 'hrrr' or model == 'hrrrX':
                    return {'UGRD': value1,
                            'VGRD': value2,
                            'SPEED': wind_uv_to_spd(value1, value2),
                            'lat': lat,
                            'lon': lon,
                            'valid': validDATE,
                            'anlys': anlysDATE,
                            'msgU': msg1,
                            'msgV': msg2,
                            'URL': pandofile}
                elif model == 'hrrrak':
                    return {'UGRD': value1,
                            'VGRD': value2,
                            'SPEED': wind_uv_to_spd(value1, value2),
                            'lat': lat,
                            'lon': lon,
                            'valid': validDATE,
                            'anlys': anlysDATE,
                            'msgU': msg1,
                            'msgV': msg2,
                            'URL': pandofile}
            else:
                value, lat, lon = grbs[1].data()
                validDATE = grbs[1].validDate
                anlysDATE = grbs[1].analDate
                msg = str(grbs[1])
                if model == 'hrrrak':
                    lon[lon>0] -= 360

                # 4) Remove the temporary file
                if removeFile == True:
                    os.system('rm -f %s' % (outfile))

                # 5) Return some import stuff from the file
                if model == 'hrrr' or model == 'hrrrX':
                    return {'value': value,
                            'lat': lat,
                            'lon': lon,
                            'valid': validDATE,
                            'anlys': anlysDATE,
                            'msg': msg,
                            'URL': pandofile}
                elif model == 'hrrrak':
                    return {'value': value,
                            'lat': lat,
                            'lon': lon,
                            'valid': validDATE,
                            'anlys': anlysDATE,
                            'msg': msg,
                            'URL': pandofile}
            

    except:
        print " _______________________________________________________________"
        print " !!   Run Date Requested :", DATE, "F%02d" % fxx 
        print " !! Valid Date Requested :", DATE+timedelta(hours=fxx)
        print " !!     Current UTC time :", datetime.utcnow()
        print " !! ------------------------------------------------------------"
        print " !! ERROR downloading from:", pandofile
        print " !! Is the variable right?", variable
        print " !! Does the .idx file exist?", fileidx
        print " ---------------------------------------------------------------"
        return {'value' : np.nan,
                'lat' : np.nan,
                'lon' : np.nan,
                'valid' : np.nan,
                'anlys' : np.nan,
                'msg' : np.nan,
                'URL': pandofile}


def get_hrrr_variable_multi(DATE, variable, next=2, fxx=0, model='hrrr', field='sfc', removeFile=True):
    """
    Uses cURL to grab a range of variables from a HRRR grib2 file on the
    MesoWest HRRR archive.

    Input:
        DATE - the datetime(year, month, day, hour) for the HRRR file you want
        variable - a string describing the variable you are looking for.
                   Refer to the .idx files here: https://api.mesowest.utah.edu/archive/HRRR/
                   You want to put the variable short name and the level information
                   For example, for 2m temperature: 'TMP:2 m above ground'
        fxx - the forecast hour you desire. Default is the anlaysis hour.
        model - the model you want. Options include ['hrrr', 'hrrrX', 'hrrrAK']
        field - the file type your variable is in. Options include ['sfc', 'prs']
        removeFile - True will remove the grib2 file after downloaded. False will not.
    """
    # Model direcotry names are named differently than the model name.
    if model == 'hrrr':
        model_dir = 'oper'
    elif model == 'hrrrX':
        model_dir = 'exp'
    elif model == 'hrrrAK':
        model_dir = 'alaska'

    if removeFile is True:
        if DATE.hour % 2 == 0:
            try:
                outfile = '/scratch/local/brian_hrrr/temp_%04d%02d%02d%02d.grib2' \
                          % (DATE.year, DATE.month, DATE.day, DATE.hour)
            except:
                outfile = './temp_%04d%02d%02d%02d.grib2' \
                          % (DATE.year, DATE.month, DATE.day, DATE.hour)
        else:
            outfile = './temp_%04d%02d%02d%02d.grib2' \
                       % (DATE.year, DATE.month, DATE.day, DATE.hour)

    else:
        # Save the grib2 file as a temporary file (that isn't removed)
        outfile = './temp_%04d%02d%02d%02d.grib2' \
                  % (DATE.year, DATE.month, DATE.day, DATE.hour)

    print "Hour %s out file: %s" % (DATE.hour, outfile)

    # URL for the grib2 idx file
    fileidx = 'https://api.mesowest.utah.edu/archive/HRRR/%s/%s/%04d%02d%02d/%s.t%02dz.wrf%sf%02d.grib2.idx' \
                % (model_dir, field, DATE.year, DATE.month, DATE.day, model, DATE.hour, field, fxx)

    # URL for the grib2 file (located on PANDO S3 archive)
    pandofile = 'https://pando-rgw01.chpc.utah.edu/HRRR/%s/%s/%04d%02d%02d/%s.t%02dz.wrf%sf%02d.grib2' \
                % (model_dir, field, DATE.year, DATE.month, DATE.day, model, DATE.hour, field, fxx)
    try:
        try:
            # ?? Ignore ssl certificate (else urllib2.openurl wont work).
            #    (Depends on your version of python.)
            # See here:
            # http://stackoverflow.com/questions/19268548/python-ignore-certicate-validation-urllib2
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
                print 'matched a variable', g
                parts = g.split(':')
                rangestart = parts[1]
                parts = lines[gcnt+next].split(':')
                rangeend = int(parts[1])-1
                print 'range:', rangestart, rangeend
                byte_range = str(rangestart) + '-' + str(rangeend)

                # 2) When the byte range is discovered, use cURL to download.
                os.system('curl -s -o %s --range %s %s' % (outfile, byte_range, pandofile))
            gcnt += 1

        return_this = {'msg':np.array([])}

        # 3) Get data from the file
        grbs = pygrib.open(outfile)
        for i in range(1, next+1):
            return_this[grbs[i]['name']], return_this['lat'], return_this['lon'] = grbs[1].data()
            return_this['msg'] = np.append(return_this['msg'], str(grbs[i]))
        return_this['valid'] = grbs[1].validDate
        return_this['anlys'] = grbs[1].analDate

        # 4) Remove the temporary file
        if removeFile is True:
            os.system('rm -f %s' % (outfile))

        # 5) Return some import stuff from the file
        return return_this

    except:
        print " ! Could not get the file:", pandofile
        print " ! Is the variable right?", variable
        print " ! Does the file exist?", fileidx
        return {'value' : np.nan,
                'lat' : np.nan,
                'lon' : np.nan,
                'valid' : np.nan,
                'anlys' : np.nan,
                'msg' : np.nan}


def pluck_hrrr_point(H, lat=40.771, lon=-111.965, verbose=True):
    """
    Pluck the value from the nearest lat/lon location in the HRRR grid.
    Input:
        H   - is a dictionary as returned from get_hrrr_variable
        lat - is the desired latitude location you want. Default is KSLC
        lon - is the desired longitude location you want. Default is KSLC
    Return:
        value from pluked location
    """
    try:
        # 1) Compute the abosulte difference between the grid lat/lon and the point
        abslat = np.abs(H['lat']-lat)
        abslon = np.abs(H['lon']-lon)

        # 2) Element-wise maxima. (Plot this with pcolormesh to see what I've done.)
        c = np.maximum(abslon, abslat)

        # 3) The index of the minimum maxima (which is the nearest lat/lon)
        x, y = np.where(c == np.min(c))
        # 4) Value of the variable at that location
        plucked = H['value'][x[0], y[0]]
        valid = H['valid']
        if verbose == True:
            print "requested lat: %s lon: %s" % (lat, lon)
            print "plucked %s from lat: %s lon: %s" % (plucked, H['lat'][x[0], y[0]], H['lon'][x[0], y[0]])

        # Returns the valid time and the plucked value
        return [valid, plucked]
    except:
        print "\n------------------------------------!"
        print " !> ERROR <! ERROR in pluck_hrrr_point() %s" % (H['msg']), lat, lon
        print "------------------------------------!\n"
        return [np.nan, np.nan]

def hrrr_subset(H, half_box=9, lat=40.771, lon=-111.965):
    """
    Cut up the HRRR data based on a center point and the half box surrounding
    the point.
    half_box - number of gridpoints half the size the box surrounding the center point.
    """
    # 1) Compute the abosulte difference between the grid lat/lon and the point
    abslat = np.abs(H['lat']-lat)
    abslon = np.abs(H['lon']-lon)

    # 2) Element-wise maxima. (Plot this with pcolormesh to see what I've done.)
    c = np.maximum(abslon, abslat)

    # 3) The index of the minimum maxima (which is the nearest lat/lon)
    x, y = np.where(c == np.min(c))
    xidx = x[0]
    yidx = y[0]

    print 'x:%s, y:%s' % (xidx, yidx)

    subset = {'lat': H['lat'][xidx-half_box:xidx+half_box, yidx-half_box:yidx+half_box],
              'lon': H['lon'][xidx-half_box:xidx+half_box, yidx-half_box:yidx+half_box],
              'value': H['value'][xidx-half_box:xidx+half_box, yidx-half_box:yidx+half_box]}

    return subset


def hrrr_area_stats(H, half_box=5, lat=40.771, lon=-111.965, verbose=True):
    """
    Pluck the value from the nearest lat/lon location in the HRRR grid.
    Input:
        H        - is a dictionary as returned from get_hrrr_variable
        half_box - is the number of grid boxes to +/- from center lat/lon
                   For the HRRR model, 5 reprsents a 30kmx30km box
                   5 for the number of grids in each direction from the center
                   point (so we get a 10x10 grid box) and multiply by 3km for
                   size of each grid box.
        lat      - is the center of the box. Default is KSLC
        lon      - is the desired longitude location you want. Default is KSLC
    Return:
        Dictionary of the stats around each point.
    """
    if verbose is True:
        print "half_box is set to %s, so your box will be %s-km2 centered at %s %s" % (half_box, half_box*2*3, lat, lon)

    try:
        # 1) Compute the abosulte difference between the grid lat/lon and the point
        abslat = np.abs(H['lat']-lat)
        abslon = np.abs(H['lon']-lon)

        # 2) Element-wise maxima. (Plot this with pcolormesh to see what I've done.)
        c = np.maximum(abslon, abslat)

        # 3) The index of the minimum maxima (which is the nearest lat/lon)
        x, y = np.where(c == np.min(c))
        xidx = x[0]
        yidx = y[0]

        if verbose is True:
            print 'hrrr latlon:', H['lat'][x[0], y[0]], H['lon'][x[0], y[0]]
            print 'requested:', lat, lon

        # 4) Get desired data box and perform statistics
        box = H['value'][xidx-half_box:xidx+half_box, yidx-half_box:yidx+half_box]

        p = np.percentile(box, [1, 5, 10, 90, 95, 99])

        return_this = {'half box': half_box,
                       'center': [lat, lon],
                       'valid':H['valid'],
                       'box center':H['value'][x[0], y[0]],
                       'min':np.nanmin(box),
                       'p1':p[0],
                       'p5':p[1],
                       'p10':p[2],
                       'mean':np.nanmean(box),
                       'p90':p[3],
                       'p95':p[4],
                       'p99':p[5],
                       'max':np.nanmax(box),
                      }

        # Returns the valid time and the plucked value
        return return_this
    except:
        print "\n------------------------------------!"
        print " !> ERROR <! ERROR in hrrr_area_stats. Returning a nan value."
        print "------------------------------------!\n"
        return {'half box': half_box,
                'center': [lat, lon],
                'valid':np.nan,
                'box center':np.nan,
                'min':np.nan,
                'p1':np.nan,
                'p5':np.nan,
                'p10':np.nan,
                'mean':np.nan,
                'p90':np.nan,
                'p95':np.nan,
                'p99':np.nan,
                'max':np.nan,
               }

def points_for_multipro(multi_vars):
    """
    Need to feed a bunch of variables to these functions for multiprocessing
    """
    DATE = multi_vars[0]
    VAR = multi_vars[1]
    LAT = multi_vars[2]
    LON = multi_vars[3]
    FXX = multi_vars[4]
    MODEL = multi_vars[5]
    FIELD = multi_vars[6]
    VERBOSE = multi_vars[7]
    if VERBOSE == True:
        print 'working on', multi_vars
    H = get_hrrr_variable(DATE, VAR, fxx=FXX, model=MODEL, field=FIELD, verbose=VERBOSE)
    value = pluck_hrrr_point(H, LAT, LON, verbose=VERBOSE)
    del H # does this help prevent multiprocessing from hanging??
    return value

def points_for_multipro2(multi_vars):
    """
    Need to feed a bunch of variables to these functions for multiprocessing
    With the location_dic as an input
    """
    DATE = multi_vars[0]
    LOC_DIC = multi_vars[1]
    VAR = multi_vars[2]
    FXX = multi_vars[3]
    MODEL = multi_vars[4]
    FIELD = multi_vars[5]
    STATS = multi_vars[6]
    VERBOSE = multi_vars[7]
    if VERBOSE == True:
        print 'working on', multi_vars
        if STATS != False:
            print 'NOTICE! Getting time series for Area Statistics for a %s-km2 box centerd at the location' % (STATS*2*3)

    values = {'DATETIME':DATE}

    # Download the HRRR field once, and pluck values from it at locations
    H = get_hrrr_variable(DATE, VAR, fxx=FXX, model=MODEL, field=FIELD, verbose=VERBOSE)
    for l in LOC_DIC.keys():
        if STATS is False:
            value = pluck_hrrr_point(H, LOC_DIC[l]['latitude'], LOC_DIC[l]['longitude'],
                                     verbose=VERBOSE)
            values[l] = value[1] # only need to store the value, and not the date
        else:
            value = hrrr_area_stats(H, half_box=STATS,
                                    lat=LOC_DIC[l]['latitude'],
                                    lon=LOC_DIC[l]['longitude'],
                                    verbose=VERBOSE)
            values[l] = value
    del H # does this help prevent multiprocessing from hanging??
    return values


def point_hrrr_time_series(start, end, variable='TMP:2 m',
                           lat=40.771, lon=-111.965,
                           fxx=0, model='hrrr', field='sfc',
                           verbose=True,
                           reduce_CPUs=2):
    """
    Produce a time series of HRRR data for a specified variable at a lat/lon
    location. Use multiprocessing to speed this up :)
    Input:
        start - datetime begining time
        end - datetime ending time
        variable - the desired variable string from a line in the .idx file.
                   Refer https://api.mesowest.utah.edu/archive/HRRR/
        lat - latitude of the point
        lon - longitude of the point
        fxx - forecast hour
        model - model type. Choose one: ['hrrr', 'hrrrX', 'hrrrAK']
        field - field type. Choose one: ['sfc', 'prs']
        reduce_CPUs - How many CPUs do you not want to use? Default is to use
                      all except 2, to be nice to others using the computer.
                      If you are working on a wx[1-4] you can safely reduce 0.
    """

    # 1) Create a range of dates and inputs for multiprocessing
    #    the get_hrrr_variable and pluck_point_functions.
    #    Each processor needs these: [DATE, variable, lat, lon, fxx, model, field]
    base = start
    hours = (end-start).days * 24 + (end-start).seconds / 3600
    date_list = [base + timedelta(hours=x) for x in range(0, hours)]
    multi_vars = [[d, variable, lat, lon, fxx, model, field, verbose] for d in date_list]

    # 2) Use multiprocessing to get the plucked values from each map.
    cpu_count = multiprocessing.cpu_count() - reduce_CPUs
    p = multiprocessing.Pool(cpu_count)
    timer_MP = datetime.now()
    ValidValue = p.map(points_for_multipro, multi_vars)
    p.close()
    print "f%02d: finished multiprocessing in %s on %s processers" % (fxx, datetime.now()-timer_MP, cpu_count)

    # Convert to numpy array so the columns can be indexed
    ValidValue = np.array(ValidValue)

    valid = ValidValue[:, 0] # First returned is the valid datetime
    value = ValidValue[:, 1] # Second returned is the value at that datetime

    return valid, value

def point_hrrr_time_series_multi(start, end, location_dic,
                                 variable='TMP:2 m',
                                 fxx=0, model='hrrr', field='sfc',
                                 area_stats=False,
                                 reduce_CPUs=2,
                                 verbose=True):
    """
    Produce a time series of HRRR data for a specified variable at multiple
    lat/lon locations. Use multiprocessing to speed this up :)
    Input:
        start - datetime begining time
        end - datetime ending time
        location_dic - a dictionary {'name':{'latitude':xxx, 'longitude':xxx}}
        variable - the desired variable string from a line in the .idx file.
                   Refer https://api.mesowest.utah.edu/archive/HRRR/
        fxx - forecast hour
        model - model type. Choose one: ['hrrr', 'hrrrX', 'hrrrAK']
        field - field type. Choose one: ['sfc', 'prs']
        area_stats - default is False (does not return area statistics)
                     or, if you want the statistics for an area around a point,
                     set to a number that represents the number of grid
                     points around the point (length of half the box).
                     The number will be the number of grid points to +/- from
                     the location lat/lon point. To convert the number to the
                     size of the box in km2, multiply by 6 (ie. if you set this
                     to 5, then you will get a 30x30 km2 box centered at lat/lon)
        reduce_CPUs - How many CPUs do you not want to use? Default is to use
                      all except 2, to be nice to others using the computer.
                      If you are working on a wx[1-4] you can safely reduce 0.
    Output:
        a dictinary of the data for the requested variable and the stations
        and has the keys ['DATETIME', 'stid1', 'stnid2', 'stnid3']

        *The DATETIME returned is the valid time.
    """

    # 1) Create a range of dates
    base = start
    hours = (end-start).days * 24 + (end-start).seconds / 3600
    date_list = [base + timedelta(hours=x) for x in range(0, hours)]

    # Remember to add the fxx to the date list to get vaild date
    valid_dates = [D+timedelta(hours=fxx) for D in date_list]

    # 2) Intialzie dicitonary to store data with the valid_dates. Each station
    #    will also be a key, and the value is empty until we fill it.
    return_this = {'DATETIME':valid_dates}
    for l in location_dic:
        return_this[l] = np.array([])

    # 3) Create and inputs for multiprocessing
    #    the get_hrrr_variable and pluck_point functions.
    #    Each processor needs these: [DATE, location_dic, variable, fxx, model, field]

    multi_vars = [[d, location_dic, variable, fxx, model, field, area_stats, verbose] for d in date_list]

    # 2) Use multiprocessing to get the plucked values from each map.
    cpu_count = multiprocessing.cpu_count() - reduce_CPUs
    p = multiprocessing.Pool(cpu_count)
    timer_MP = datetime.now()
    ValidValue = p.map(points_for_multipro2, multi_vars)
    p.close()
    print "finished multiprocessing in %s on %s processers" % (datetime.now()-timer_MP, cpu_count)

    # Convert to numpy array so the columns can be indexed
    ValidValue = np.array(ValidValue)

    # REPACKAGE THE RETURNED VALUES FROM MULTIPROCESSING so that each key value
    # is the station name, and contains the time sereis for that station.
    for l in location_dic:
        num = range(len(ValidValue))
        if area_stats is False:
            return_this[l] = np.array([ValidValue[i][l] for i in num])
        else:
            return_this[l] = {'valid':np.array([ValidValue[i][l]['valid'] for i in num]),
                              'min':np.array([ValidValue[i][l]['min'] for i in num]),
                              'p1':np.array([ValidValue[i][l]['p1'] for i in num]),
                              'p5':np.array([ValidValue[i][l]['p5'] for i in num]),
                              'p10':np.array([ValidValue[i][l]['p10'] for i in num]),
                              'mean':np.array([ValidValue[i][l]['mean'] for i in num]),
                              'p90':np.array([ValidValue[i][l]['p90'] for i in num]),
                              'p95':np.array([ValidValue[i][l]['p95'] for i in num]),
                              'p99':np.array([ValidValue[i][l]['p99'] for i in num]),
                              'max':np.array([ValidValue[i][l]['max'] for i in num]),
                              'box center':np.array([ValidValue[i][l]['box center'] for i in num])
                             }

    return return_this


def get_hrrr_pollywog(DATE, variable, lat, lon, forecast_limit=18, verbose=True):
    """
    Creates a vector of a variable's value for each hour in a HRRR model 
    forecast initialized from a specific time.
    
    John Horel named these pollywogs because when you plot the series of a 
    forecast variable with the analysis hour being a circle, the lines look 
    like pollywogs.   O----

    input:
        DATE           - datetime for the pollywog head
        variable       - The name of the variable in the HRRR .idx file
        lat            - latitude
        lon            - longitude
        forecast_limit - the last hour of the pollywog, default all 18 hours.
                         but maybe you are only interested in the first, say,
                         the first 5 forecast hours, then you would set to 5.
    output:
        valid date, pollywog vector   - A vector with the data for the forecast
    """
    pollywog = np.array([])
    valid_dates = np.array([])

    forecasts = range(forecast_limit+1)
    for fxx in forecasts:
        try:
            H = get_hrrr_variable(DATE, variable, fxx, model='hrrr', field='sfc', verbose=verbose)
            Vdate, plucked = pluck_hrrr_point(H, lat, lon, verbose=verbose)
            pollywog = np.append(pollywog, plucked)
            valid_dates = np.append(valid_dates, Vdate)
        except:
            # If hour isn't available, fill with nan, and date is next hour
            pollywog = np.append(pollywog, np.nan)
            valid_dates = np.append(valid_dates, valid_dates[-1]+timedelta(hours=1))

    return valid_dates, pollywog

def get_hrrr_pollywog_multi(DATE, variable, location_dic, forecast_limit=18, verbose=True):
    """
    Creates a vector of a variable's value for each hour in a HRRR model
    forecast initialized from a specific time. FOR MULTIPLE LOCATIONS. Requires
    a dictionary of sites which includes the keys, 'latitude' and 'longitude'.

    input:
        DATE           - datetime for the pollywog head
        variable       - The name of the variable in the HRRR .idx file
        location_dic   - Dictionary of locations that include the 'latitude'
                         and 'longitude'.
                         location_dic = {'name':{'latitude':###,'longitude':###}}
        forecast_limit - the last hour of the pollywog, default all 18 hours.
                         but maybe you are only interested in the first, say,
                         the first 5 forecast hours, then you would set to 5.
    output:
        dictionary   - Valid times, and values for each station key
    """
    # Create a vector of times
    valid_dates = np.array([DATE + timedelta(hours=x) for x in range(0, forecast_limit+1)])

    # Intialzie dicitonary to store data with the valid_dates. Each station 
    # will also be a key, and the value is empty until we fill it.
    return_this = {'DATETIME':valid_dates}
    for l in location_dic:
        return_this[l] = np.array([])


    for fxx in range(len(valid_dates)):
        try:
            # Get the HRRR file
            H = get_hrrr_variable(DATE, variable, fxx, model='hrrr', field='sfc', verbose=verbose)
            # For each station, pluck the value and store it
            for l in location_dic:
                Vdate, plucked = pluck_hrrr_point(H, location_dic[l]['latitude'], location_dic[l]['longitude'], verbose=verbose)
                return_this[l] = np.append(return_this[l], plucked)
        except:
            # If hour isn't available, fill with nan, and date is next hour
            for l in location_dic:
                return_this[l] = np.append(return_this[l], np.nan)

    return return_this

def get_hrrr_hovmoller(start, end, location_dic,
                       variable='TMP:2 m',
                       area_stats=False,
                       fxx=range(19),
                       reduce_CPUs=2):
    """
    Have you ever seen a Hovmoller plot? This "HRRR Hovmoller" will read kind
    of like one of those.
    I plot the HRRR forecast hour on the y-axis increasing from f00-f18, then 
    I plot the vaild time on the x-axis across the bottom. It helps you see how
    the forecasts are changing over time

    start - a python datetime object
    end   - a python datetime object
    location_dic - Dictionary of locations that include the 'latitude' and 'longitude'.
                   location_dic = {'name':{'latitude':###,'longitude':###}}
    area_stats - a half box you want to calculate statistics for, with point at center of the box
    fxx - a list of forecast times

    Returns a 2D array
    """
    data = {}
    for f in fxx:
        sOffset = start - timedelta(hours=f)
        eOffset = end - timedelta(hours=f)
        data[f] = point_hrrr_time_series_multi(sOffset, eOffset, location_dic,
                                               variable=variable,
                                               fxx=f,
                                               verbose=False,
                                               field='sfc',
                                               area_stats=area_stats,
                                               reduce_CPUs=reduce_CPUs)

    # Number of observations (hours in the time series)
    num = len(data[0]['DATETIME'])
    dates = data[0]['DATETIME']

    # Organize into Hovmoller array
    # matplotlib.pyplot.confourf requires a 2d array of the dates/fxx to plot
    # matplotlib.pyplot.pcolormesh requers a 1d array of the dates/fxx with size +1 for the limits
    #                              (otherwise it'll cut off the last row and column)
    hovmoller = {'fxx_2d':np.array([np.ones(num)*i for i in fxx]),
                 'valid_2d':np.array([data[0]['DATETIME'] for i in fxx]),
                 'fxx_1d+':fxx+[fxx[-1]+1],
                 'valid_1d+':np.append(dates, dates[-1]+timedelta(hours=1))}

    if area_stats is False:
        # Returns a dictionary like hovmoller['WBB'] = 2D array
        for l in location_dic:
            hovmoller[l] = np.array([data[i][l] for i in fxx])

    else:
        # NEED To repackage the statistical data with an extra layer
        # i.e. >> hovmoller[station id][area statistic]
        # i.e. >> hovmoller['WBB']['max'] = 2D array
        for l in location_dic:
            hovmoller[l] = {}
            for s in data[0][l]:
                hovmoller[l][s] = np.array([data[i][l][s] for i in fxx])

    return hovmoller


if __name__ == "__main__":
    """
    DATE = datetime(2017, 3, 11, 0)
    variable = 'TMP:2 m'

    timer1 = datetime.now()
    data = get_hrrr_variable(DATE, variable)

    plt.figure(1)
    plt.pcolormesh(data['lon'], data['lat'], data['value'], cmap="Spectral_r")
    plt.colorbar()
    plt.title('%s, Valid: %s' % (variable, data['valid']))
    plt.xlabel('Value at KSLC: %s' % pluck_hrrr_point(data))
    plt.savefig('example.png')
    plt.show(block=False)

    print ""
    print 'timer single map:', datetime.now() - timer1
    """

    """
    # Time Series (25 seconds to make a 5 day time series on 8 processors)
    timer2 = datetime.now()
    START = datetime(2016, 3, 1)
    END = datetime(2016, 4, 1)
    dates, data = point_hrrr_time_series(START, END, variable='SOILW:0.04', lat=40.5, lon=-113.5, fxx=0, model='hrrr', field='prs')
    fig, ax = plt.subplots(1)
    plt.plot(dates, data-273.15) # convert degrees K to degrees C
    plt.title('4 cm layer soil moisture at SLC')
    plt.ylabel('Fractional Soil Moisture')
    plt.ylim([0,.6])
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d\n%Y'))
    plt.savefig('CUAHSI_soil_moisture_2016.png')
    plt.show(block=False)

    print 'timer time series:', datetime.now() - timer2
    """
    from mpl_toolkits.basemap import Basemap
    import matplotlib.pyplot as plt

    m = Basemap()
    m.drawcoastlines()

    AK = get_hrrr_variable(datetime(2018, 2, 24, 15), 'TMP:2 m', fxx=0, model='hrrrak')
    H = get_hrrr_variable(datetime(2018, 2, 24, 15), 'TMP:2 m', fxx=0, model='hrrr')

    m.pcolormesh(AK['lon'], AK['lat'], AK['value'], latlon=True, vmax=320, vmin=240)
    m.pcolormesh(H['lon'], H['lat'], H['value'], latlon=True, vmax=310, vmin=210)
    plt.colorbar()
    plt.show()
