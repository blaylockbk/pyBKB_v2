# Brian Blaylock
# March 9, 2017

"""
Download archived HRRR files from MesoWest PANDO S3 archive system.

Please register before downloading from our HRRR archive:
http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/hrrr_download_register.html

For info on the University of Utah HRRR archive and to see what dates are 
availabe, look here:
http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/hrrr_FAQ.html

Contact:
brian.blaylock@utah.edu
"""

import urllib
from datetime import date, datetime, timedelta
import time
import os

def reporthook(a, b, c):
    """
    Report download progress in megabytes
    """
    # ',' at the end of the line is important!
    print "% 3.1f%% of %.2f MB\r" % (min(100, float(a * b) / c * 100), c/1000000.),

def download_HRRR(DATE,
                  model='hrrr',
                  field='sfc',
                  hour=range(0, 24),
                  fxx=range(0, 1),
                  OUTDIR='./'):
    """
    Downloads from the University of Utah MesoWest HRRR archive
    Input:
        DATE   - A date object for the model run you are downloading from.
        model  - The model type you want to download. Default is 'hrrr'
                 Model Options are ['hrrr', 'hrrrX','hrrrAK']
        field  - Variable fields you wish to download. Default is sfc, surface.
                 Options are fields ['prs', 'sfc','subh', 'nat']
        hour   - Range of model run hours. Default grabs all hours of day.
        fxx    - Range of forecast hours. Default grabs analysis hour (f00).
        OUTDIR - Directory to save the files.

    Outcome:
        Downloads the desired HRRR file and renames with date info preceeding
        the original file name (i.e. 20170101_hrrr.t00z.wrfsfcf00.grib2)
    """
    # Model file names are different than model directory names.
    if model == 'hrrr':
        model_DIR = 'oper'
    elif model == 'hrrrX':
        model_DIR = 'exp'
    elif model == 'hrrrAK':
        model_DIR = 'alaska'

    # Loop through each hour and each forecast and download.
    for h in hour:
        for f in fxx:
            # 1) Build the URL string we want to download.
            #    fname is the file name in the format
            #    [model].t[hh]z.wrf[field]f[xx].grib2
            #    i.e. hrrr.t00z.wrfsfcf00.grib2
            fname = "%s.t%02dz.wrf%sf%02d.grib2" % (model, h, field, f)
            URL = "https://pando-rgw01.chpc.utah.edu/HRRR/%s/%s/%04d%02d%02d/%s" \
                   % (model_DIR, field, DATE.year, DATE.month, DATE.day, fname)

            # 2) Rename file with date preceeding original filename
            #    i.e. 20170105_hrrr.t00z.wrfsfcf00.grib2
            rename = "%04d%02d%02d_%s.t%02dz.wrf%sf%02d.grib2" \
                     % (DATE.year, DATE.month, DATE.day, model, h, field, f)

            # 3) Download the file via https
            # Check the file size, make it's big enough to exist.
            check_this = urllib.urlopen(URL)
            file_size = int(check_this.info()['content-length'])
            if file_size > 10000:
                print "Downloading:", URL
                urllib.urlretrieve(URL, OUTDIR+rename, reporthook)
                print "\n"
            else:
                # URL returns an "Key does not exist" message
                print "ERROR:", URL, "Does Not Exist"

            # 4) Sleep five seconds, as a courtesy for using the archive.
            time.sleep(5)

if __name__ == '__main__':

    # Example downloads all analysis hours for a single day.

    # -------------------------------------------------------------------------
    # --- Settings: Check online documentation for available dates and hours --
    # -------------------------------------------------------------------------
    # Start and End Date
    get_this_date = date(2017, 2, 1)

    # Model Type: options include 'hrrr', 'hrrrX', 'hrrrAK'
    model_type = 'hrrr'

    # Variable field: options include 'sfc' or 'prs'
    # (if you want to initialize WRF with HRRR, you'll need the prs files)
    var_type = 'sfc'

    # Specify which hours to download
    # (this example downloads all hours)
    if model_type == 'hrrrAK':
        # HRRR Alaska run every 3 hours at [0, 3, 6, 9, 12, 15, 18, 21] UTC
        hours = range(0, 24, 3)
    else:
        hours = range(0, 24)

    # Specify which forecasts hours to download
    # (this example downloads the analysis hours, f00)
    forecasts = range(0, 1)

    # Specify a Save Directory
    SAVEDIR = './HRRR_from_UofU/'
    # -------------------------------------------------------------------------

    # Make SAVEDIR path if it doesn't exist.
    if not os.path.exists(SAVEDIR):
        os.makedirs(SAVEDIR)

    # Call the function to download
    download_HRRR(get_this_date, model=model_type, field=var_type,
                  hour=hours, fxx=forecasts, OUTDIR=SAVEDIR)
