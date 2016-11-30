# Brian Blaylock
# 28 November 2016                    (first day back after Thanksgiving break)

"""
Download eXperimental HRRR (hrrr_X) files from ESRL via FTP

This script should be run by the LDM user.

Run the CRON job at 8:00 PM Mountain Time (20:00) to get all fields for the 
UTC "previous day". (i.e. Since 8:00 PM Mountain Time is the next day in UTC,
when I download from ESRL I am getting the data from "yesterday")
"""

from ftplib import FTP
from datetime import date, datetime, timedelta
import os
import stat

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2/')
sys.path.append('B:/pyBKB_v2')

from BB_MesoWest.get_token import get_ESRL_credentials

def check_downloads():
    """
    Print a table of the files that were successfully retreived
    """
    hours = range(0,24)
    forecasts = range(0,19)

    print 'Date:', yesterday.strftime('%Y-%m-%d')
    print 'sfc  - HRRRX surface fields'

    # print a header with the forecast hours: hour | f00 | f01 | f02| (etc.)    
    f_header = ' hour |'    
    for z in forecasts:
        f_header = f_header + ' f%02d |' % (z)
    print f_header

    # Now fill in the line for each hour
    for h in hours:
        h_line = '  %02d  |' % (h)
        for f in forecasts:
            sfc_file = OUTDIR+'hrrrX.t%02dz.wrfsfcf%02d.grib2' % (h,f)

            sfc_exist = os.path.isfile(sfc_file)
            if sfc_exist==True:            
                h_line = h_line + ' [X] |'
            else:
                h_line = h_line + ' [ ] |'
        print h_line


    ## Do again for the pressure data
    print '\nprs  - HRRRX pressure fields'

    # print a header with the forecast hours: hour | f00 | f01 | f02| (etc.)    
    f_header = ' hour |'    
    for z in forecasts:
        f_header = f_header + ' f%02d |' % (z)
    print f_header

    # Now fill in the line for each hour
    for h in hours:
        h_line = '  %02d  |' % (h)
        for f in forecasts:
            prs_file = OUTDIR+'hrrrX.t%02dz.wrfprsf%02d.grib2' % (h,f)

            prs_exist = os.path.isfile(prs_file)
            if prs_exist==True:            
                h_line = h_line + ' [X] |'
            else:
                h_line = h_line + ' [ ] |'
        print h_line            
            
    print "\n"

# -----------------------------------------------------------------------------
if __name__ == '__main__':

    # Function for getting user name and password to download ESRL eXperimental
    # HRRR files (that function is hidden from GitHub)
    user, password = get_ESRL_credentials()


    # Date: "yesterday" is the previous day accorting to the UTC clock.
    yesterday = date.today() #-timedelta(days=1)
    print 'Grabbing files for:', yesterday

    # Directory to save the downloads
    OUTDIR = '/uufs/chpc.utah.edu/common/home/horel-group/archive/%04d%02d%02d/models/hrrrX/' \
            % (yesterday.year, yesterday.month, yesterday.day)
    if not os.path.exists(OUTDIR):
        # If that directory doesn't exist, then create it and change permissions
        # to match permissions of Taylor's downloads for HRRR Alaska.
        os.makedirs(OUTDIR)
        print "\nCreated:", OUTDIR
        
    os.chmod(OUTDIR, stat.S_IRWXU | \
                        stat.S_IRGRP | stat.S_IXGRP | \
                        stat.S_IROTH | stat.S_IXOTH) 
    # User can read, write, execute
    # Group can read and execute
    # Others can read and execute


    """
    Download Surface 2D fields
    """
    print "\nGetting Surface Fields\n-------------------------------------"
    # FTP login: gsdftp.fsl.noaa.gov
    ftp = FTP('gsdftp.fsl.noaa.gov')
    ftp.login(user, password)
    ftp.cwd('hrrr/conus/wrftwo')

    # List the files...
    filenames = ftp.nlst()

    for item in filenames:
        # Only download files that contain only numbers (these represent dates),
        # and files for which the date matches the OUTDIR date. (We don't want 
        # to accidentally put "todays" fields in "yesterdays" directory.)
        if item.isdigit() and datetime.strptime(item[0:5], '%y%j').day==yesterday.day:

            # item file name is in the form... YYJJJHH00FF00
            # Year, Day of Year, Model Hour, Forecast
            # print datetime.strptime(item[0:5], '%y%j')

            # What is the initalized hour and forecast?
            hour = item[5:7]
            forecast = item[9:11]

            # Save the file similar to the standard hrrr file naming convention
            # except insert an X to represent that this is the experimental version
            NEWFILE = 'hrrrX.t%sz.wrfsfcf%s.grib2' % (hour, forecast)
            ftp.retrbinary('RETR '+ item, open(OUTDIR+NEWFILE, 'wb').write)
            print 'saved:', NEWFILE
    ftp.quit()


    """
    Download Pressure fields
    """
    print "\nGetting Pressure Fields\n-------------------------------------"
    # FTP login: gsdftp.fsl.noaa.gov
    ftp = FTP('gsdftp.fsl.noaa.gov')
    ftp.login(user, password)
    ftp.cwd('hrrr/conus/wrfprs')

    # List the files...
    filenames = ftp.nlst()

    # Download the files that contain only numbers (these represent dates)
    for item in filenames:
        # Only download files that contain only numbers (these represent dates),
        # and only the analysis hours (last four digits are '0000'),
        # and files for which the date matches the OUTDIR date. (We don't want 
        # to accidentally put "todays" fields in "yesterdays" directory)
        
        if item.isdigit() \
        and item[-4:] == '0000' \
        and datetime.strptime(item[0:5], '%y%j').day==yesterday.day:
            # iten file name in the form... YYJJJHH00FF00
            print datetime.strptime(item[0:5], '%y%j')

            # What is the initalized hour and forecast?
            hour = item[5:7]
            forecast = item[9:11]

            # Save the file similar to the standard HRRR file name convention,
            # with hrrrX representing that this is the eXperimental HRRR.
            NEWFILE = 'hrrrX.t%sz.wrfprsf%s.grib2' % (hour, forecast)
            ftp.retrbinary('RETR '+ item, open(OUTDIR+NEWFILE, 'wb').write)
    ftp.quit()
