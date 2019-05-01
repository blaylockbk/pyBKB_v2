#!/bin/csh
#
#------------------------------------------------------------------------------
# Eclipse2017
#------------------------------------------------------------------------------

limit coredumpsize 0

cd /uufs/chpc.utah.edu/common/home/u0553130/pyPlots_v2/MesoWest/Eclipse2017/

module load python/2.7.11
python plot_hourly_mesowest_hrrr_conus.py
python plot_2min_mesowest_domains.py
exit
