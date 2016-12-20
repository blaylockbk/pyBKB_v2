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

   
"""
-------------------------------------------------------------------------------
@author Geir Arne Waagb
@see http://code.google.com/p/pywrfplot/
-------------------------------------------------------------------------------
"""

# constants used to calculate moist adiabatic lapse rate
# See formula 3.16 in Rogers&Yau
a = 2./7.
b = eps*L*L/(R*cp)
c = a*L/R

def gamma_s(T,p):
    """Calculates moist adiabatic lapse rate for T (Celsius) and p (Pa)
    Note: We calculate dT/dp, not dT/dz
    See formula 3.16 in Rogers&Yau for dT/dz, but this must be combined with
    the dry adiabatic lapse rate (gamma = g/cp) and the 
    inverse of the hydrostatic equation (dz/dp = -RT/pg)"""
    esat = es(T)
    wsat = eps*esat/(p-esat) # Rogers&Yau 2.18
    numer = a*(T+T_zero) + c*wsat
    denom = p * (1 + b*wsat/((T+T_zero)**2)) 
    return numer/denom # Rogers&Yau 3.16

def es(T):
    """Returns saturation vapor pressure (Pascal) at temperature T (Celsius)
    Formula 2.17 in Rogers&Yau"""
    return 611.2*np.exp(17.67*T/(T+243.5))

def e(w,p):
    """Returns vapor pressure (Pa) at mixing ratio w (kg/kg) and pressure p (Pa)
    Formula 2.18 in Rogers&Yau"""
    return w*p/(w+eps)

def td(e):
    """Returns dew point temperature (C) at vapor pressure e (Pa)
    Insert Td in 2.17 in Rogers&Yau and solve for Td"""
    return 243.5 * np.log(e/611.2)/(17.67-np.log(e/611.2))

def interp(geopot, pres, p):
    """ Returns the interpolated geopotential at p using the values in pres. 
    The geopotential for an element in pres must be given by the corresponding
    element in geopot. The length of the geopot and pres arrays must be the same. 
    """
    if (len(geopot) != len(pres)):
        raise Exception, "Arrays geopot and pres must have same length"
    
    k = len(pres)-1
    while (k > 1 and pres[k-1] <= p):
        k = k-1

    if (pres[k] > p):
        w = 0.0
    elif (pres[k-1] < p):
        w = 1.0
    else: 
        w = (p-pres[k])/(pres[k-1]-pres[k])

    return (1.0-w)*geopot[k] + w*geopot[k-1]