# Brian Blaylock
# March 14, 2017                                  It's Pi Day!! (3.14)

"""
Get the values of a single variable from a HRRR grib2 file

Requirements: 
    - cURL
    - pygrib
"""

import os
import pygrib
from datetime import datetime, timedelta
import urllib2
import re
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import multiprocessing #:)

# Save directory
BASE = '/uufs/chpc.utah.edu/common/home/u0553130/'
SAVE = BASE + 'public_html/PhD/HRRR/plan-view/temperature/'
if not os.path.exists(SAVE):
    # make the SAVE directory
    os.makedirs(SAVE)
    # then link the photo viewer
    photo_viewer = BASE + 'public_html/Brian_Blaylock/photo_viewer/photo_viewer.php'
    os.link(photo_viewer, SAVE+'photo_viewer.php')

def draw_CONUS_HRRR_map(res='i'):
    """
    Draw the Contintental United States HRRR Domain with lambert conformal
    projection.
    Map specifications are from the HRRR's namelis.wps file:
    http://ruc.noaa.gov/hrrr/namelist.wps.txt
    """
    m = Basemap(resolution=res, projection='lcc', area_thresh=2000,\
                width=1800*3000, height=1060*3000, \
                lat_1=38.5, lat_2=38.5, \
                lat_0=38.5, lon_0=-97.5)
    return m

# Draw HRRR Map
m = draw_CONUS_HRRR_map()

def get_variable_from_S3(DATE, variable, fxx=0, model='hrrr', field='sfc'):
    """
    Uses cURL to grab just one variable from a HRRR grib2 file on the MesoWest
    HRRR archive.

    Input:
        DATE - the datetime(year, month, day, hour) for the HRRR file you want
        variable - a string describing the variable you are looking for.
                   Refer to the .idx files here: https://api.mesowest.utah.edu/archive/HRRR/
                   You want to put the variable short name and the level information
                   For example, for 2m temperature: 'TMP:2 m above ground'
        fxx - the forecast hour you desire. Default is the anlaysis hour.
        model - the model you want. Options include ['hrrr', 'hrrrX', 'hrrrAK']
        field - the file type your variable is in. Options include ['sfc', 'prs']
    """
    # Model direcotry names are named differently than the model name.
    if model == 'hrrr':
        model_dir = 'oper'
    elif model == 'hrrrX':
        model_dir = 'exp'
    elif model == 'hrrrAK':
        model_dir = 'alaska'

    # Save the grib2 file as a temporary file (we remove it later)
    outfile = './temp_%04d%02d%02d%02d.grib2' % (DATE.year, DATE.month, DATE.day, DATE.hour)

    # URL for the grib2 idx file
    fileidx = 'https://api.mesowest.utah.edu/archive/HRRR/%s/%s/%04d%02d%02d/%s.t%02dz.wrf%sf%02d.grib2.idx' \
                % (model_dir, field, DATE.year, DATE.month, DATE.day, model, DATE.hour, field, fxx)

    # URL for the grib2 file (located on PANDO S3 archive)
    pandofile = 'https://pando-rgw01.chpc.utah.edu/HRRR/%s/%s/%04d%02d%02d/%s.t%02dz.wrf%sf%02d.grib2' \
                % (model_dir, field, DATE.year, DATE.month, DATE.day, model, DATE.hour, field, fxx)

    try:
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
                parts = lines[gcnt+1].split(':')
                rangeend = int(parts[1])-1
                print 'range:', rangestart, rangeend
                byte_range = str(rangestart) + '-' + str(rangeend)
                # 2) When the byte range is discovered, use cURL to download.
                os.system('curl -o %s --range %s %s' % (outfile, byte_range, pandofile))
            gcnt += 1

        # 3) Get data from the file
        grbs = pygrib.open(outfile)
        value, lat, lon = grbs[1].data()
        validDATE = grbs[1].validDate
        anlysDATE = grbs[1].analDate
        msg = grbs[1]

        # 4) Remove the temporary file
        os.system('rm -f %s' % (outfile))

        # 5) Return some import stuff from the file
        return {'value': value,
                'lat': lat,
                'lon': lon,
                'valid': validDATE,
                'anlys': anlysDATE,
                'msg':msg}

    except:
        print "! Could not get the file:", pandofile
        print "!  Is the variable right?", variable
        print "!  Does the file exist?", fileidx

def make_plot(DATE):
    variable = 'TMP:2 m above ground'

    fig = plt.figure()
    fig.add_subplot(111)

    data = get_variable_from_S3(DATE, variable)
    x, y = m(data['lon'], data['lat'])
    temp = data['value'] - 273.15
    m.drawcoastlines()
    m.drawstates()
    m.drawcountries()
    m.pcolormesh(x, y, temp, cmap="Spectral_r", vmin=-20, vmax=35)
    cb = plt.colorbar(orientation='horizontal',
                      shrink=.9,
                      pad=.03,
                      ticks=range(-20, 36, 5),
                      extend="both")
    cb.set_label('Temperature (C)')
    plt.title('%s, Valid: %s' % (variable, data['valid']))

    savedate = data['valid'].strftime('%Y-%m-%d_%H%M')
    plt.savefig(SAVE+savedate, bbox_inches="tight")
    print 'saved', savedate


if __name__ == "__main__":

    timer1 = datetime.now()

    DATE = datetime(2017, 3, 10, 0)
    eDATE = datetime(2017, 3, 15, 0)

    base = DATE
    hours = (eDATE-DATE).days * 24
    date_list = [base + timedelta(hours=x) for x in range(0, hours)]

    num_proc = multiprocessing.cpu_count() # use all processors
    num_proc = num_proc - 3                # specify number to use (to be nice)
    p = multiprocessing.Pool(num_proc)
    p.map(make_plot, date_list)

    total_time = datetime.now() - timer1
    print 'total time:', total_time, 'with', num_proc, 'processors.'
    