# Brian Blaylock
# February 2, 2017                             Well, it's Groundhog day...again

"""
Read a hrrr bufr sounding file and return data as dictionary.
"""

from datetime import datetime
import numpy as np

def get_bufr_sounding(request_time, site='kslc', model='hrrr'):
    """
    Get data from buf soundings.

    Input:
        request_time - datetime object of requested model initialization (UTC)
        site - bufr sounding site, default is "kslc" (lowercase)
        model - the bufr sounding model type, default is 'hrrr'. Must be
                lowercase becuase of check done later in the function.abs
    Output:
        Dictionary of the data. Index values correspond to forecast hour.
    """

    print "\nPROCESSING DATA for model: '{0}'".format(model.upper())
    print "  Site: '{0}'".format(site)

    # Read in Bufr file
    DIR = '/uufs/chpc.utah.edu/common/home/horel-group/archive/%04d%02d%02d/models/hrrr/' \
        % (request_time.year, request_time.month, request_time.day)
    FILE = DIR +'%s_%04d%02d%02d%02d.buf' \
        % (site, request_time.year, request_time.month, request_time.day, request_time.hour)

    #FILE = 'kslc_2017011516.buf' #local file

    print "  Reading buffer file: {0}".format(FILE)
    f = open(FILE, 'r')
    ls = f.readlines()
    f.close()

    # Get dimensions/validtimes of BUFR data
    ptimes = [] # valid datetime of analysis hour and each forecast hour
    fhr = [] # forecast hour integers
    for i in range(len(ls)):
        l = ls[i]
        # If adding stations, confirm that the first digits of the station id is in
        # this list:
        if l[0:5] == '72572' or l[0:5] == '72575' or l[0:4] == '298 ' or \
        l[0:5] == '45012' or l[0:5] == '45139' or l[0:5] == '71629' or \
        l[0:5] == '71624' or l[0:5] == '72529' or l[0:5] == '72515' or \
        l[0:5] == '72519' or l[0:4] == '821 ' or l[0:5] == '72622' or \
        l[0:5] == '72475' or l[0:5] == '72577' or l[0:5] == '72779' or \
        l[0:5] == '72570' or l[0:4] == '728 ' or l[0:5] == '72592' or \
        l[0:5] == '72479' or l[0:5] == '72679' or l[0:6] == '856290':
            # The data in these lines are at the bottom of the burf file. They
            # contain the dates of each data forecast hour.
            ptimes.append(datetime(2000+int(l.split(' ')[1][0:2]), \
                                int(l.split(' ')[1][2:4]), \
                                int(l.split(' ')[1][4:6]), \
                                int(l.split(' ')[1][7:9])))
        if l[0:4] == 'STIM':
            # This is the forecast hour
            fhr.append(int(l.split(' ')[2]))

    ptimes = np.array(ptimes)
    starttime = ptimes[0]
    endtime = ptimes[-1]
    maxfhr = int(24.0*(endtime-starttime).days + (endtime-starttime).seconds/3600)
    step = int(maxfhr/float(len(ptimes)-1))
    numhours = len(ptimes)

    getind = [] # line number the new record starts
    for l in ls:
        if l[0:4] == 'STID':
            getind.append(ls.index(l))

    # Some creative way for determining how many lines of sounding data are in the
    # file. Minius 12 because there are 12 header lines. Divide by 2 becuase
    # each "line of data" occupied 2 lines of text. They should all be the same
    # size, but grab the minimum.
    numlevs = (min(np.array(getind)[1:-1]-np.array(getind)[0:-2])-12)/2

    print "  FOUND DATA (time) from {0} to {1}".format(starttime, endtime)
    print "  Data captured every {0} hours through hour {1}".format(step, maxfhr)
    print "  Time step size: {0}".format(step)
    print "  Vertical levels: {0}".format(numlevs)
    print "  Hours: {0}".format(numhours)

    # initialize 2-D np.arrays of BUFR data (val versus time, level)
    p = np.zeros((numhours, numlevs))
    z = np.zeros((numhours, numlevs))
    t = np.zeros((numhours, numlevs))
    tw = np.zeros((numhours, numlevs))
    td = np.zeros((numhours, numlevs))
    wdir = np.zeros((numhours, numlevs))
    wspd = np.zeros((numhours, numlevs))

    # Fill 2-D BUFR np.arrays
    for i in range(numhours):
        ind1 = np.arange(getind[0] + i*(numlevs*2+12) + 11, \
                         getind[0] + i*(numlevs*2 + 12) + 11 + numlevs*2,
                         2)
        for j in range(len(ind1)):
            p[i, j] = float((ls[ind1[j]].rstrip()).split(' ')[0])
            t[i, j] = float((ls[ind1[j]].rstrip()).split(' ')[1])
            tw[i, j] = float((ls[ind1[j]].rstrip()).split(' ')[2])
            td[i, j] = float((ls[ind1[j]].rstrip()).split(' ')[3])

        #   Hack here forces td to be <= t.  Needed due to problems with GFS BUFR data
            if td[i, j] > t[i, j]:
                print "WARNING: td > t -> HACK prevented this from occuring"
                print 'Reseting', model, 'td at', site
                print 'Run initialized at', starttime, 'forecast hour= ', fhr[i]
                print 'p=', p[i, j], 't=', t[i, j], 'td=', td[i, j]
                td[i, j] = t[i, j]

            wdir[i, j] = float((ls[ind1[j]].rstrip()).split(' ')[5])
            wspd[i, j] = float((ls[ind1[j]].rstrip()).split(' ')[6])

            # The next line (current_line+1) contains the height data.
            if 'nam' in model:
                z[i, j] = float((ls[ind1[j]+1].rstrip()).split(' ')[1])
            elif 'hrrr' in model:
                z[i, j] = float((ls[ind1[j]+1].rstrip()).split(' ')[1])
            else:
                z[i, j] = float((ls[ind1[j]+1].rstrip()).split(' ')[0])

        # QC measures for BUFR data (??)
        tw[i, :] = np.where(np.logical_and(np.greater(tw[i, :], 50), \
                                        np.greater(z[i, :], 1000)), -80.0, tw[i, :])


    # Each key index is a forecast hour (0th index is the analysis)
    mydata = dict(zip(('hght', 'pres', 'temp', 'dwpt', 'drct', 'sknt', 'fHour', 'DATETIME'), \
                        (z, p, t, td, wdir, wspd, fhr, ptimes)))

    return mydata

if __name__ == '__main__':
    request_time = datetime(2017, 1, 30)

    s = get_bufr_sounding(request_time)
