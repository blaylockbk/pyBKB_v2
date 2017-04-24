# Created by Brian Blaylock
# November 4, 2015

"""
If you have a large model domain but only want to process and plot a subsection
this is usefull for timming the data so it takes less processing time.
"""

import numpy as np


def cut_data(bl_lat,tr_lat,bl_lon,tr_lon,lat,lon,buff=0):
    '''    
    Cut down data for domain for faster plotting.
        
    input: the bottom left corner and top right corner lat/lon coordinates
        bl_lat = bottom left latitude
        tr_lat = top right latitude
        bl_lon = bottom left longitude
        tr_lon = top right longitude
        lat    = 2D latitude array of data
        lon    = 2D longitude array of data
        buff   = is a buffer in case the domain is skewed resulting in blank spots
                 on the map plot.
    return: the max and min of each the arrays x and y coordinates    
    
    '''
    lat_limit = np.logical_and(lat>bl_lat,lat<tr_lat)
    lon_limit = np.logical_and(lon>bl_lon,lon<tr_lon)
    
    total_limit = np.logical_and(lat_limit,lon_limit)
    
    xmin = np.min(np.where(total_limit==True)[0])-buff # +/- a buffer to cover map area 
    xmax = np.max(np.where(total_limit==True)[0])+buff
    ymin = np.min(np.where(total_limit==True)[1])-buff
    ymax = np.max(np.where(total_limit==True)[1])+buff
    
    return xmin,xmax,ymin,ymax
