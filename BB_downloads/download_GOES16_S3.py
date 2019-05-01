# Brian Blaylock
# September 6, 2017         Current Event: Hurricane Irma

"""
Download GOES-16 data from Amazon S3
"""

#import urllib
#URL = 'https://goesingest.s3.amazonaws.com/'
#FILE = 'OR_ABI-L1b-RadC-M3C01_G16_s20170612201495_e20170612204268_c20170612204310.nc'

#urllib.urlretrieve(URL+FILE, 'goes16file.nc')

#URL = 'https://s3.amazon.aws.com/'
#FILE = 'ABI-L1b-RadF/2017/167/11/OR_ABI-L1b-RadF-M3C02_G16_s20171671145342_e20171671156109_c20171671156144.nc'

# Command
#aws s3 cp s3://noaa-goes16/ABI-L1b-RadF/2017/249/00/OR_ABI-L1b-RadF-M3C16_G16_s20172490045346_e20172490056125_c20172490056175.nc .
#rclone lds goes16:noaa-goes16

from datetime import datetime
import itertools
from tempfile import NamedTemporaryFile

import boto3
import botocore
from botocore.client import Config
from netCDF4 import Dataset

class GOESArchiveDownloader(object):
    def __init__(self):
        s3 = boto3.resource('s3', config=Config(signature_version=botocore.UNSIGNED, user_agent_extra='Resource'))
        self._bucket = s3.Bucket('goesingest')

    def _get_iter(self, start, product):
        prod_prefix = str(product)
        start_marker = product.with_start_time(start)
        print(prod_prefix, start_marker)
        return self._bucket.objects.filter(Marker=start_marker, Prefix=str(product))
        
    def get_next(self, time, product):
        return next(iter(self._get_iter(time, product)))

    def get_range(self, start, end, product):
        end_key = product.with_start_time(end)

        # Get a list of files that have the proper prefix up to the hour
        return list(itertools.takewhile(lambda obj: obj.key <= end_key, self._get_iter(start, product)))

class GOESProduct(object):
    def __init__(self, **kwargs):
        self.sector = 'conus'
        self.satellite = 'goes16'
        self.typ = 'ABI'
        self.channel = 1
        self.mode = 3
        self.__dict__.update(kwargs)

    def __str__(self):
        env = 'OR'
        sat = {'goes16': 'G16', 'goes17': 'G17'}[self.satellite]

        if self.typ == 'ABI':
            sector = {'conus': 'C', 'meso1': 'M1', 'meso2': 'M2', 'full': 'F'}[self.sector]
            prod_id = 'ABI-L1b-Rad{sector}-M{mode}C{channel:02d}'.format(sector=sector,
                                                                         mode=self.mode,
                                                                         channel=self.channel)
        elif self.typ == 'GLM':
            prod_id = 'GLM-L2-LCFA'
        else:
            raise ValueError('Unhandled data type: {}'.format(self.typ))
        return '{env}_{prodid}_{sat}'.format(env=env, prodid=prod_id, sat=sat)

    __repr__ = __str__

    def with_start_time(self, time):
        return str(self) + '_s{time:%Y%j%H%M%S}'.format(time=time)

arc = GOESArchiveDownloader()    
files = arc.get_range(datetime(2017, 6, 14, 12), datetime(2017, 7, 15, 12), GOESProduct(typ='ABI', channel=2, sector='conus'))

for f in files:
    urllib.urlretrieve(URL+f.key, './goes16/'+f.key)