# Brian Blaylock
# March 24, 2017                           Yesterday Salt Lake had lots of rain

"""
Fast download of HRRR grib2 files with multi-threading to a queue
"""

from queue import Queue
from threading import Thread
from datetime import datetime, timedelta
import numpy as np
import urllib2
import re
import os

def get_hrrr_variable(DATE, variable, fxx=0, model='hrrr', field='sfc', removeFile=True):
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
        removeFile - True will remove the grib2 file after downloaded. False will not.
    """
    # Model direcotry names are named differently than the model name.
    if model == 'hrrr':
        model_dir = 'oper'
    elif model == 'hrrrX':
        model_dir = 'exp'
    elif model == 'hrrrAK':
        model_dir = 'alaska'
    #
    # Save the grib2 file as a temporary file (we remove it later)
    outfile = './temp_%04d%02d%02d%02d.grib2' % (DATE.year, DATE.month, DATE.day, DATE.hour)
    #
    # URL for the grib2 idx file
    fileidx = 'https://api.mesowest.utah.edu/archive/HRRR/%s/%s/%04d%02d%02d/%s.t%02dz.wrf%sf%02d.grib2.idx' \
                % (model_dir, field, DATE.year, DATE.month, DATE.day, model, DATE.hour, field, fxx)
    #
    # URL for the grib2 file (located on PANDO S3 archive)
    pandofile = 'https://pando-rgw01.chpc.utah.edu/HRRR/%s/%s/%04d%02d%02d/%s.t%02dz.wrf%sf%02d.grib2' \
                % (model_dir, field, DATE.year, DATE.month, DATE.day, model, DATE.hour, field, fxx)
    #try:
    try:
        # ?? Ignore ssl certificate (else urllib2.openurl wont work). Depends on your version of python.
        # See here: http://stackoverflow.com/questions/19268548/python-ignore-certicate-validation-urllib2
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
            parts = lines[gcnt+1].split(':')
            rangeend = int(parts[1])-1
            print 'range:', rangestart, rangeend
            byte_range = str(rangestart) + '-' + str(rangeend)
            # 2) When the byte range is discovered, use cURL to download.
            os.system('curl -s -o %s --range %s %s' % (outfile, byte_range, pandofile))
        gcnt += 1
    #
    print "got it!", pandofile

#    except:
#        print " !", DATE
#        print " ! Could not get the file:", pandofile
#        print " ! Is the variable right?", variable
#        print " ! Does the file exist?", fileidx

if __name__ == "__main__":
    DATE = datetime(2015, 4, 18)
    eDATE = datetime(2015, 5, 1)
    hours = (eDATE-DATE).days*24 + (eDATE-DATE).seconds*3600
    date_list = np.array([DATE + timedelta(hours=x) for x in range(0, hours)])

    num_of_threads = 10
    def worker():
        while True:
            item = q.get()
            print "number:", item
            get_hrrr_variable(item, "TMP:2 m")
            q.task_done()

    q = Queue()
    for i in range(num_of_threads):
        t = Thread(target=worker)
        t.daemon = True
        t.start()

    timer1 = datetime.now()
    for item in date_list:
        q.put(item)

    q.join()       # block until all tasks are done
