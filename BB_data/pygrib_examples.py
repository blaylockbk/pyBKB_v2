# Brian Blaylcok
# Version 2.0 update
# # 21 December 2015

"""
Do some basic data extraction with pygrib.
Pygrib was installed in the CHPC space on December 21, 2015

I'm using this version of python:
/uufs/chpc.utah.edu/sys/pkg/python/2.7.3_rhel6/bin/python
(For Horel Group users, pygrib isn't installed locally).
If you have moduels set up you can source this verion with the following command:
module load python / 2.7.3

More usage documentation here:
http://pygrib.googlecode.com/svn/trunk/docs/index.html


"""


import pygrib


def print_grib2_variables(path):
    """
    Print the variable names in a pygrib directory.
    """
    grbs = pygrib.open(path)

    # Print an inventory of the file
    grbs.seek(0)  # (go back to top of file)
    for grb in grbs:
        print grb  # Yeah, we really don't need to look at all the lines.


if __name__ == '__main__':

    # Open a file
    DIR = '/uufs/chpc.utah.edu/common/home/horel-group/archive/20160805/models/hrrr/'
    FILE = 'hrrr.t12z.wrfprsf00.grib2'
    # FILE = 'hrrr.t12z.wrfsfcf06.grib2'
    print_grib2_variables(DIR + FILE)

    # jims files
    # DIR = '/uufs/chpc.utah.edu/common/home/horel-group/archive/20160805/models/hrrr/'
    # FILE = '2016080517F11hrrr.grib2'
    # print_grib2_variables(DIR + FIL

    # subhourly HRRR
    # DIR = './'
    # FILE = 'hrrr.t03z.wrfsubhf18.grib2'
    # print_grib2_variables(DIR + FIL
