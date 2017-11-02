# Brian Blaylock
# March 10, 2017
# updated: July 26, 2017
# updated: October 31, 2017               Happy Halloween

"""
Download a single HRRR variable from the Pando archive using cURL.
More Information at: https://hrrr.chpc.utah.edu
"""

import commands
import re
from StringIO import StringIO
from datetime import date, timedelta
import os
import urllib2


def download_HRRR_variable_from_pando(DATE, variable,
                                      hours=range(0, 24),
                                      fxx=[0],
                                      model='hrrr',
                                      field='sfc',
                                      outdir='./'):
    """
    Download a partial grib2 file from the Pando archive (http://hrrr.chpc.utah.edu)
    by specifying the variable you wish to download. These single-variable
    grib2 files are about 1 MB in size. If you don't need the full grib2 file,
    retrieving only the variables you need can save you a lot in disk space.
    
    Input:
        DATE     - a python date object for the date you want to download
        variable - a string of the variable abreviation and level that matches
                   the line in the .idx file you want to download from.
                   This string is used to search for the line in the grib2.idx
                   file so we can discover the byte range of the variable.
                   For example, if variable='TMP:2 m', we will search for that
                   line in the .idx file and use the byte range to do a partial
                   download from the full grib2 file to retrieve just that
                   field using cURL.
                   Check this URL for a sample of variable names you can match:
                   https://api.mesowest.utah.edu/archive/HRRR/oper/sfc/20170725/hrrr.t01z.wrfsfcf00.grib2.idx
                   String must be unique enough to only occure once in the .idx
                   file, else it will download the last instance. Thus, include
                   both the varibale abbreviation and the surface.
        hours    - a list of hours to download, within range(24).
        fxx      - a list of forecast hours to download, within range(19).
        model    - a string specifying the model you want to download.
                   Choose either 'hrrr', 'hrrrX', or 'hrrrAK'
        field    - a string specifying the filed to download from.
                   Choose either 'sfc' for surface file or 'prs' for the
                   pressure file (prs includes many more variables than the sfc
                   file).
        outdir   - a string specifying the directory to save the files retrived
    """

    # Check if the outdir exists. If not, create it.
    if not os.path.exists(outdir):
        os.makedirs(outdir)
        print "created new directory: %s" % outdir

    # Model file names are different than model directory names.
    if model == 'hrrr':
        model_dir = 'oper'
    elif model == 'hrrrX':
        model_dir = 'exp'
    elif model == 'hrrrAK':
        model_dir = 'alaska'

    # Download for all requested hours and forecast hours
    for h in hours:
        for f in fxx:

            # Rename the downloaded file based on the info from above
            # e.g. HRRRfromPando_20170310_h00_f00_TMP_2_m.grib2
            outfile = '%s/%sfromPando_%s_h%02d_f%02d_%s.grib2' \
                       % (outdir, model.upper(), DATE.strftime('%Y%m%d'), h, f, variable.replace(':', '_').replace(' ', '_'))

            # URL for the grib2 .idx metadata file.
            # The metadata contains the byte range for each variable, which we
            # will need for a partial download, in Step 2.
            idxfile = 'https://api.mesowest.utah.edu/archive/HRRR/%s/%s/%s/%s.t%02dz.wrf%sf%02d.grib2.idx' \
                       % (model_dir, field, DATE.strftime('%Y%m%d'), model, h, field, f)

            # URL to download the full grib2 file.
            # We will use the cURL comand to download the variable of interest
            # from this file using the byte range, in step 3.
            pandofile = 'https://pando-rgw01.chpc.utah.edu/HRRR/%s/%s/%s/%s.t%02dz.wrf%sf%02d.grib2' \
                    % (model_dir, field, DATE.strftime('%Y%m%d'), model, h, field, f)

            # 1) Open the Metadata URL and read the lines
            #    Remember, we are ignoring the certificate.
            try:
                try:
                    idxpage = urllib2.urlopen(idxfile)
                except:
                    # Depending on your version of urllib2, you may need to
                    # ignore the ssl certificate before urllib2.openurl will work.
                    # My Python 2.7.11 needs to do this, but my Python 2.7.3 does not.
                    # https://stackoverflow.com/questions/19268548/python-ignore-certicate-validation-urllib2/28048260#28048260
                    print ">>going to ignore the ssl certificate"
                    import ssl
                    ctx = ssl.create_default_context()
                    ctx.check_hostname = False
                    ctx.verify_mode = ssl.CERT_NONE
                    idxpage = urllib2.urlopen(idxfile, context=ctx)
                lines = idxpage.readlines()
            except:
                print "\n   ERROR!!! Does the .idx file exist: %s \n" % idxfile
                print "If is does, then something is wrong with urllib2.urlopen"
                continue
            
            # Check if the variable requested is in the .idx file.
            if not any(variable in s for s in lines):
                print "\n   ERROR!!!"
                print "   Can not retrieve %s from %s." % (variable, idxfile)
                print "   Check that your variable name matches a line in the .idx file.\n"
                return

            # 2) Find the byte range for the variable requested.
            #    Need to first find which line the variable is located. Keep a count
            #    of what line we are on, gcnt, so we can get the end byte range
            #    from the next line.
            gcnt = 0
            for g in lines:
                expr = re.compile(variable)
                if expr.search(g):
                    parts = g.split(':')
                    rangestart = parts[1]
                    parts = lines[gcnt+1].split(':')
                    rangeend = int(parts[1])-1
                    print variable+' byte range:', rangestart, rangeend
                    byte_range = str(rangestart) + '-' + str(rangeend)

                    # 3) When the byte range is discovered, use cURL to download.
                    try:
                        os.system('curl -s -o %s --range %s %s' % (outfile, byte_range, pandofile))
                        print 'Downloaded %s \n' % outfile
                    except:
                        print "\n   ERROR !!! Does the grib2 file exists: %s \n" % pandofile
                        continue
                gcnt += 1

            """
            Note: If you don't give the variable string a unique enough name,
                  it will only grab the last instance of that variable.
                  For example, there are many 'TMP' varibles at different levels.
                  If you set variable='TMP' it will download all the
                  fields that match TMP (i.e TMP:500 mb, TMP:700 mb) and
                  overwrite the file with the last instance. That is why you
                  need to also specify the variable abreviation and surface
                  when you name the variable string.
            """

# =============================================================================
#   Example Usage: Modify date and variable parameters
# =============================================================================
def get_single_variable_single_day():
    # Download single variable from single day
    DATE = date(2017, 3, 10)   # Model run date

    variable = 'TMP:2 m'       # Must be part of a line in the .idx file              

    download_HRRR_variable_from_pando(DATE, variable,
                                      hours=range(0, 24),
                                      fxx=[0],
                                      model='hrrr',
                                      field='sfc',
                                      outdir='./')


def get_single_variable_multiple_days():
    # === User modify variable and date range =================================
    # date range
    sDATE = date(2017, 3, 10)   # Start date
    eDATE = date(2017, 3, 13)   # End date (exclusive)
    # variable string (must be part of line in .idx file)
    variable = 'TMP:2 m'
    # =========================================================================

    # Create list of all dates
    days = (eDATE-sDATE).days
    DATES = [sDATE + timedelta(days=d) for d in range(days)]

    # Loop through main function for all dates
    for DATE in DATES:
        download_HRRR_variable_from_pando(DATE, variable,
                                          hours=range(0, 24),
                                          fxx=[0],
                                          model='hrrr',
                                          field='sfc',
                                          outdir='./')


def get_multiple_variables_multiple_days():
    # === User modify variable and date range =================================
    # date range
    sDATE = date(2017, 3, 10)   # Start date
    eDATE = date(2017, 3, 13)   # End date (exclusive)
    # variable list (must be part of line in .idx file)
    variables = ['TMP:2 m', 'DPT:2 m', 'UGRD:10 m', 'VGRD:10 m']
    # =========================================================================

    # Create list of all dates
    days = (eDATE-sDATE).days
    DATES = [sDATE + timedelta(days=d) for d in range(days)]

    # Loop through main function for all dates and all variables
    for variable in variables:
        for DATE in DATES:
            download_HRRR_variable_from_pando(DATE, variable,
                                              hours=range(0, 24),
                                              fxx=[0],
                                              model='hrrr',
                                              field='sfc',
                                              outdir='./')



def fast_dwnld_with_multithreading():
    # Fast download of HRRR grib2 files (single variable) with multithreading
    from queue import Queue 
    from threading import Thread

    def worker():
        # This is where the main download function is run.
        # Change the hour and fxx parameters here if needed.
        while True:
            item = q.get()
            # Unpack the date and variable from the item sent to this worker
            iDATE, ivar = item
            download_HRRR_variable_from_pando(iDATE, ivar,
                                              hours=range(0, 24),
                                              fxx=[0],
                                              model='hrrr',
                                              field='sfc',
                                              outdir='./')
            q.task_done()

    # ===== User Modify the Variables and date range ==========================
    variables = ['TMP:2 m', 'DPT:2 m'] # List of variable strings
    sDATE = date(2017, 3, 10)          # Start date
    eDATE = date(2017, 3, 13)          # End date (exclusive)
    # =========================================================================

    # Create list of dates to request
    days = (eDATE-sDATE).days
    DATES = [sDATE + timedelta(days=d) for d in range(days)]

    # Make a list of inputs to send to the worker
    input_list = [[d, v] for d in DATES for v in variables]

    # Multithreadding using the worker
    num_of_threads = 8
    q = Queue()
    for i in range(num_of_threads):
        t = Thread(target=worker)
        t.daemon = True
        t.start()

    # Run each item through the threads
    for item in input_list:
        q.put(item)

    q.join() # block until all tasks are done

if __name__=='__main__':

    from datetime import datetime
    timer = datetime.now()

    #get_single_variable_single_day()
    #get_single_variable_multiple_days()
    #get_multiple_variables_multiple_days()
    fast_dwnld_with_multithreading()

    print datetime.now()-timer   
