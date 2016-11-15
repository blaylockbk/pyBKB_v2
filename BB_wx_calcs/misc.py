# Brian Blaylock
# Version 2 update
# 15 November 2016

"""
Miscelaneous Code
"""

import numpy as np

def GetAbsVorticity(inlatgrid,inlongrid,inugrid,invgrid):
    """
    Author: Alex Jaques
    Date: 15 November 2016
    Absolute Vorticity Function
    Takes in grids of latitude,longitude,u,v
    Uses lat,lon 0,0 as a reference point and figures out x,y in meters from that ref point
    Uses numpy gradient method from there to get dX,dY,dU,dV
    Note that for this function expects grid orintation to be lower-left at [0,0] and upper-right at [-1,-1]
	"""
    my_gridym = inlatgrid*111321.5
    my_gridxm = np.empty(inlongrid.shape)
    my_coriolis = 2*7.292e-5*np.sin((inlatgrid/180.)*np.pi)
    for i in range(0,inlongrid.shape[0]):
        for j in range(0,inlongrid.shape[1]):
            if(inlongrid[i,j] >= 0):
                my_gridxm[i,j] = np.cos((inlatgrid[i,j]/180.)*np.pi)*111321.5*inlongrid[i,j]
            else:
                my_gridxm[i,j] = -1*(np.cos((inlatgrid[i,j]/180.)*np.pi)*111321.5*inlongrid[i,j])
    dX = -1*(np.gradient(my_gridxm)[1])
    dV = np.gradient(invgrid)[1]
    dY = np.gradient(my_gridym)[0]		
    dU = np.gradient(inugrid)[0]	
    vortout = my_coriolis+((dV/dX)-(dU/dY))
    return vortout
    