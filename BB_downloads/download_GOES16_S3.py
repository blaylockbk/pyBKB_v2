# Brian Blaylock
# September 6, 2017         Current Event: Hurricane Irma

"""
Download GOES-16 data from Amazon S3
"""

import urllib

URL = 'https://s3.amazon.aws.com/'


URL = 'https://goesingest.s3.amazonaws.com/'

FILE = 'OR_ABI-L1b-RadC-M3C01_G16_s20170612201495_e20170612204268_c20170612204310.nc'

urllib.urlretrieve(URL+FILE, 'goes16file.nc')
