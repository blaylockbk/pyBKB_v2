# Brian Blaylock
# February 14, 2017                                      Happy Valentine's Day!

"""
Finds the Lifting Condensation Level (LCL) for all layers in a bufr sounding.
Calculates temperatures of a rising parcel lifted from each layer.

Some code copied from John Horel's perl scripts:
/uufs/chpc.utah.edu/common/home/horel-group/horel/gps/proc/rmin_layer.pl
"""

from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
from BB_HRRR.get_bufr_sounding import get_bufr_sounding
from BB_wx_calcs.thermodynamics import TempPress_to_PotTemp, WBT, THTE

#==============================================================================

# Constants
rcp = 287/1004.
g = 9.81


def LCL_and_Parcels_from_bufr(DATE, site='kslc', fxx=0):
    """
    Lifts Parcels from each level in a bufr sounding. Returns the temperature
    of each lifted parcel including the LCL pressure and temperature, and
    the mean CAPE of each layer.

    Input:
        DATE - datetime object of the the HRRR bufr sounding
        fxx = forecast hour (for HRRR its 0-18)

    Return: a big dictionary of stuff
        keys: 'LCL'
                    'pres'
                    'temp'
              'bufr'
                    'temp'
                    'wetbulb'
                    'theta-e'
                    'hght'
                    'dwpt'
                    'theta'
                    'pres'
              'Parcels'
                    'temp'
                        level [0, 1, 2, 3, ... last parcel]
                    'pres'
                        level [0, 1, 2, 3, ... last parcel]
              'mean CAPE'
                    level [0, 1, 2, 3, ... level]
                        'CAPE'
                        'pres'
                        'hght'
    """
    # Variables
    buf = get_bufr_sounding(DATE, site=site) # buf is for bufr data
    t = buf['temp'][fxx]                  # Note: zeroth index is the analysis hour
    td = buf['dwpt'][fxx]
    p = buf['pres'][fxx]
    h = buf['hght'][fxx]                  # height in meters
    tw = buf['wetb'][fxx]                 # wetbulb temperature in C
    thte = buf['thte'][fxx]               # equivalent potential temperature
    theta = TempPress_to_PotTemp(t, p)  # calculate potential temperature

    # Storage
    plcls = np.zeros(len(t)) # LCL presures (s indicates plural)
    tlcls = np.zeros(len(t)) # LCL temperatures (s indicates plural)
    tParcels = {}            # Dictionary of lifted parcel temperatures for each level
    pParcels = {}            # Dictionary of lifted parcel pressures for each level

    for i in range(len(t)):
        tParcels[i] = np.zeros(len(t))*np.nan # a place to store parcel accent temperatures
        pParcels[i] = np.zeros(len(t))*np.nan # a place to store parcel accent pressures

        # Temperature and Dew Point in Kelvin
        tk = t[i] + 273.15
        tdk = td[i] + 273.15

        # find temperature and pressure of LCL.
        #    compute buoyancy with respect to unsat parcel below, sat parcel above
        tlcl = (800 * (tdk - 56)/(800 + (tdk - 56) * np.log(tk/tdk))) + 56
        plcl = p[i] * (tlcl/tk)**(1/rcp)

        # store the pressures and temperatures (converted to Celsius)
        plcls[i] = plcl
        tlcls[i] = tlcl - 273.15

        # Store the starting temperature (in Celsius) and pressure. 
        # (We will leave the levels below current level as nans)
        tParcels[i][i] = t[i]
        pParcels[i][i] = p[i]

        # lift the parcel parcel from the level to the top
        for j in range(i+1, len(t)): # from level to top
            # Next pressure level up
            pj = p[j]
            pParcels[i][j] = pj
            if pj > plcl:
                #lift unsaturated parcel (dry adiabatic accent)
                tp = theta[i] * (pj/1000)**rcp
                tParcels[i][j] = tp-273.15 # store parcel temp in Celsius
            else:
                #lift saturated parcel (moist adiabatic accent)
                #tp = WBT(pj, thte[i]) # this is wrong. Need to use thte of the LCL
                THTE_LCL = THTE(plcls[i], tlcls[i], tlcls[i])
                tp = WBT(p[j], THTE_LCL)
                tParcels[i][j] = tp-273.15 # store parcel temp in Celsius

    return_this = {'LCL':{'temp':tlcls,         # LCL height from each level
                          'pres':plcls},
                   'Parcels':{'temp':tParcels,  # lifted parcels each level
                              'pres':pParcels},
                   'bufr':{'temp':t,            # bufr data
                           'dwpt':td,
                           'pres':p,
                           'hght':h,
                           'wetbulb':tw,
                           'theta-e':thte,
                           'theta':theta},
                   'mean CAPE':{}              # mean CAPE for each level (fill with loop below)
                  }

    # =========================================
    #      Calculate CAPE
    # =========================================
    for i in range(len(tParcels)):
        this_parcel = tParcels[i]
        CAPE_calc = calc_CAPE(this_parcel, t, p, h)
        return_this['mean CAPE'][i] = {'CAPE':CAPE_calc['mean CAPE'],
                                       'pres':CAPE_calc['mean Pres'],
                                       'hght':CAPE_calc['mean Height']
                                      }

    return return_this

    """
    Next steps, return the CAPE of each layer for the lifted parcel.
    Do do this you have to create an array of temperatures and pressures
    that match the parcel levels.

    Then make some cool time-height series plots:
        - LCL heights of each level
        - Surface CAPE/CIN (use PRGn cmap)
        - minimum CIN of bottom 300 m or 500 m levels
        - etc.
    """

def calc_CAPE(parcel, environment, pressure, heights):
    """
    Calculates CAPE or CIN for each level of the lifted profile.

    Input:
        parcel - temperatures of a parcel rising [C]
        environment - temperatures of the environment, on same level as parcel [C]
        pressure - the pressure of each level
        heights - the heights of each level
    Output:
        mean_CAPE - the average CAPE of the layer [J/kg] or [m^2/s^2]
        mean_p - the average pressure of the layer. Simply (topP+botP)/2
    """
    # Mean CAPE calculations of each layer
    par = parcel + 273.15         # parcel [K]
    env = environment + 273.15    # environment [K]
    Tdiff = par - env             # parcel-environment [K]
    hgts = heights                # array of heights [m]
    prss = pressure               # array of pressures [hPa]
    g = 9.81                      # gravitational acc. [m/s^2]

    # Calculate the mean CAPE for each layer
    # (should get one less the length of "par" variable)
    mean_CAPE = np.array([])
    mean_p = np.array([])
    mean_h = np.array([])

    for i in range(len(par)-1):
        # for each level...
        # Get the deltaZ between the level and the next level
        z = hgts[i+1] - hgts[i]
        # CAPE = (Tparcel-Tenv)/Tenv * g * z      has units --> [J/kg]==[m^2/s^2]
        # layer_Mean_CAPE = [(Tparcel1-Tenv1)/Tenv1 + (Tparcel2-Tenv2)/Tenv2]*g*z/2
        layer_Mean_CAPE = 0.5 * g * z * (Tdiff[i]/env[i] + Tdiff[i+1]/env[i+1])
        mean_CAPE = np.append(mean_CAPE, layer_Mean_CAPE)
        mean_p = np.append(mean_p, np.mean([prss[i], prss[i+1]]))
        mean_h = np.append(mean_h, np.mean([hgts[i], hgts[i+1]]))

    return {'mean CAPE':mean_CAPE, 'mean Pres':mean_p, 'mean Height':mean_h}

if __name__=="__main__":
    DATE = datetime(2017, 2, 1)
    data = LCL_and_Parcels_from_bufr(DATE)

    t = data['bufr']['temp']
    td = data['bufr']['dwpt']
    p = data['bufr']['pres']
    tw = data['bufr']['wetbulb']
    hght = data['bufr']['hght']

    tParcels = data['Parcels']['temp']
    pParcels = data['Parcels']['pres']

    tlcls = data['LCL']['temp']
    plcls = data['LCL']['pres']


    # =========================================
    #                 Plots
    # =========================================

    plt.plot(t, p, label="temp", color='r', lw=3)
    plt.plot(td, p, label="dwpt", color='g', lw=3)
    plt.plot(tw, p, label="wetbulb", color='grey', lw=3, ls='--')
    plt.plot(np.array(tParcels[0]), pParcels[0], color='k', lw=3, label="lifted parcel")
    plt.plot(np.array(tParcels[5]), pParcels[5], color='k', lw=3, label="lifted parcel")

    plt.gca().invert_yaxis()
    plt.yscale('log')
    pranges = range(100, 901, 100)
    plt.yticks(pranges, [str(i) for i in pranges])
    plt.grid()
    plt.ylim([900, 600])
    plt.xlim([-50, 10])

    x = np.arange(0, 50, .5)
    for i in range(len(t)):
        plt.plot((t[i], tlcls[i]), (p[i], plcls[i]), lw=1)

    plt.legend(loc=3)
    plt.title(DATE)

    # ===== Next Plot with CAPE values ===========================
    parcel_t = data['Parcels']['temp'][0]
    parcel_p = data['Parcels']['pres'][0]
    mean_CAPE = data['mean CAPE'][0]['CAPE']
    mean_pres = data['mean CAPE'][0]['pres']

    plt.figure(2)
    plt.plot(t, p, label='env')
    plt.plot(parcel_t, parcel_p, label='parcel')
    for i in range(len(mean_CAPE)):
        plt.text(-20, mean_pres[i], mean_CAPE[i])

    plt.gca().invert_yaxis()
    plt.yscale('log')
    pranges = range(100, 901, 100)
    plt.yticks(pranges, [str(i) for i in pranges])
    plt.grid()
    plt.ylim([900, 600])
    plt.xlim([-50, 10])

    plt.title(DATE)

    plt.show(block=False)

    # ===== Next Plot with CAPE values (height) ======================
    parcel_t = data['Parcels']['temp'][0]
    parcel_p = data['Parcels']['pres'][0]
    mean_CAPE = data['mean CAPE'][0]['CAPE']
    mean_hght = data['mean CAPE'][0]['hght']

    plt.figure(3)
    plt.plot(t, data['bufr']['hght'], label='env')
    plt.plot(parcel_t, data['bufr']['hght'], label='parcel')
    for i in range(len(mean_CAPE)):
        plt.text(-20, mean_hght[i], mean_CAPE[i])

    plt.grid()
    plt.xlim([-50, 10])
    plt.ylim([1000, 4000])

    plt.title(DATE)

    plt.show(block=False)
