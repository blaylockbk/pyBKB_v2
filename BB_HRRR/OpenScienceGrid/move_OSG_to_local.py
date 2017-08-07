# Brian Blaylock
# July 28, 2017

"""
Copy files from OSG to Local drive
"""

import os 

path = 'hourly_by_month'

var = 'TMP_2_m'
#var = 'WIND_10_m'
#var = 'REFC_entire'

for month in range(1, 13):
    for hour in range(0,24):
        os.system('scp blaylockbk@login.osgconnect.net:~/%s/OSG_HRRR_%s_m%02d_h%02d_f00.nc .' % (path, var, month, hour))
        #os.system('nccopy -d1 OSG_HRRR_TMP_2_m_m%02d_h%02d_f00.nc OSG_HRRR_TMP_2_m_m%02d_h%02d_f00.nc4' % (month, hour, month, hour))
        #os.system('rm OSG_HRRR_TMP_2_m_m%02d_h%02d_f00.nc' % (month, hour))
