"""
BB_WRF
===========

Modules and Functions useful for dealing with WRF output.
Created by Brian Blaylock

Output types:
    - NetCDF wrfout
    - tslists
    - ts output (time series and vertical profiles)
"""

__version__="2.0.0"
__author__="Brian K. Blaylock"
__date__= "9 November 2016"
__url__="http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/home.html"
__all__ = ['read_tslist','WRF_timeseries','stagger_to_mass']
