import numpy as np

# --- Humidity ---------------------------------------------------------------

def dwptRH_to_Temp(dwpt, RH):
    """
    Convert a dew point temerature and relative humidity to an air temperature.
    Equation from:
    http://andrew.rsmas.miami.edu/bmcnoldy/humidity_conversions.pdf

    Input:
        dwpt - Dew point temperature in Celsius
        RH - relative humidity in %
    Output:
        Temp - Temperature in Celsius
    """
    a = 17.625
    b = 243.04
    Temp = b * (a*dwpt/(b+dwpt)-np.log(RH/100.)) / (a+np.log(RH/100.)-(a*dwpt/(b+dwpt)))
    return Temp


def Tempdwpt_to_RH(Temp, dwpt):
    """
    Convert a temperature and dew point temerature to relative humidity.
    Equation from:
    http://andrew.rsmas.miami.edu/bmcnoldy/humidity_conversions.pdf

    Input:
        Temp - Temperature in Celsius
        dwpt - Dew point temperature in Celsius

    Output:
        RH - relative humidity in % 
    """
    a = 17.625
    b = 243.04
    RH = 100*(np.exp((a*dwpt/(b+dwpt)))/np.exp((a*Temp/(b+Temp))))
    return RH


def TempRH_to_dwpt(Temp, RH):
    """
    Convert a temperature and relative humidity to a dew point temperature.
    Equation from:
    http://andrew.rsmas.miami.edu/bmcnoldy/humidity_conversions.pdf

    Input:
        Temp - Air temperature in Celsius
        RH - relative humidity in %
    Output:
        dwpt - Dew point temperature in Celsius 
    """
    # Check if the Temp coming in is in celsius and if RH is between 0-100%
    passed = False
    test_temp = temp<65

    if np.sum(test_temp) == np.size(temp):
        passed = True
        test_rh = np.logical_and(RH<=100,RH>=0)
        if np.sum(test_rh) == np.size(RH):
            passed = True
        else:
            print "faied relative humidity check"
    else:
        print "faild temperature check"

    if passed == True:
        a = 17.625
        b = 243.04
        dwpt = b * (np.log(RH/100.) + (a*Temp/(b+Temp))) / (a-np.log(RH/100.)-((a*Temp)/(b+Temp)))
        return dwpt

    else:
        print "TempRH_to_dwpt input requires a valid temperature and humidity."
        return "Input needs a valid temperature (C) and humidity (%)."
