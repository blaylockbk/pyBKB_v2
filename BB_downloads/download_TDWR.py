# Brian Blaylock
# Version 2 update
# Summer 2015

"""
Download TDWR files from internet and save it to the current directory based
on date and scan type.
You can explore the avaialble files here: 
http://thredds.ucar.edu/thredds/catalog/terminal/level3/TV0/SLC/catalog.html

Terminal Doppler Weather Radar - SLC
 lat:  40.97
 lon:-111.93

downloaded from
http://thredds.ucar.edu/thredds/catalog/terminal/level3/catalog.html

As an example, this is the HTTP server URL you can download from
http://thredds.ucar.edu/thredds/fileServer/terminal/level3/TV0/SLC/20160123/Level3_SLC_TV0_20160123_2359.nids

Catalog: browse the availalbe data here
http://thredds.ucar.edu/thredds/catalog/terminal/level3/TV0/SLC/catalog.html


TV0/Base Velocity Tilt 1 (knots)
TV1/Base Velocity Tilt 2 (knots)
TV2/Base Velocity Tilt 3 (knots)
TR0/Base Reflectivity Tilt 1 (dbz)
TR1/Base Reflectivity Tilt 2 (dbz)
TR2/Base Reflectivity Tilt 3 (dbz)
NCR/Composite Reflectivity
"""

import urllib
import os
from datetime import datetime, timedelta


# ---- Start Date Options -----------------------------------------------------
year  = '2016' 
month = '11'
day   = '15'

num_days = 3  # The number of consecutive days you wish to download, including
              # the intitial date.
              # NOTE: The THREDDS server only keeps the last 20 days of data


# ---- Create a list of dates -------------------------------------------------
# We need to check if a radar file exists for every minute
base = datetime.strptime(year+month+day, '%Y%m%d')
num_minutes = num_days*24*60
date_list = [base + timedelta(minutes=x) for x in range(0, num_minutes)]


# ---- Specify which scan you want to download --------------------------------
scan = ['TV0']                                      ## Just download one scan type
#scan = ['TV0','TV1','TV2']                         ## TV0, TV1, and TV2 are radial velocity
scan = ['TV0','TV1','TV2','NCR','TR0','TR1','TR2']  ## velocity, reflectivity, and composite, just grabbing all 

# ---- Location ---------------------------------------------------------------
tdwr = 'SLC' # SLC is the Salt Lake City TDWR

print "Ok, I'll work on these..."
print "Dates",date_list[0],'through',date_list[-1]
print "Scans",scan

for DATE in date_list:
    for j in scan:
        # Make a directory for this day
        new_dir = str(DATE.year).zfill(4)+str(DATE.month).zfill(2)+str(DATE.day).zfill(2)

        # Make a directory for each YYYYMMDD and sub directory for the scan type
        if os.path.exists(new_dir+'/'+j) == False:
            os.makedirs(new_dir+'/'+j)
            print "created subdirectory", new_dir+"/"+j

        # look for a file for every possible hour and minute
        # Download if the data exists
        hrmin = str(DATE.hour).zfill(2)+str(DATE.minute).zfill(2)
        url = "http://thredds.ucar.edu/thredds/fileServer/terminal/level3/" \
            + j + "/" \
            + tdwr + "/" \
            + new_dir \
            + "/Level3_" + tdwr + "_" + j + "_" + new_dir + "_" + hrmin + ".nids"
        filename = new_dir+"/"+j+"/"+'Level3_'+tdwr+'_'+j+'_'+new_dir+'_'+hrmin+'.nids'
        urllib.urlretrieve(url, filename)

        # if that file is smaller than 1KB then delete it because the file is empty
        if os.path.getsize(filename) < 1000:
            os.remove(filename)
        #else, keep the file
        else:
            print "Saved", filename, os.path.getsize(filename)/1000., 'KB'
