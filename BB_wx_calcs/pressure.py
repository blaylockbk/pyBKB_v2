import numpy as np

# --- Pressure ----------------------------------------------------------------
def pres_to_alt(p_hPa, h_m):
    """
    Converts a station pressure and height to an altimeter reading.
    Follows the NOAA converstion found here:
    http://www.wrh.noaa.gov/slc/projects/wxcalc/formulas/altimeterSetting.pdf

    Input:
        p_hPa - station pressure in hPa
        h_m - station height in meters

    Output:
        calculated altimeter value in hPa
    """
    c = 0.190284  # Some constant. Not sure what from

    alt_hPa = (p_hPa - 0.3) * (1 + ((1013.25**c * 0.0065 / 288)
                                    * (h_m / (p_hPa - 0.3)**c)))**(1 / c)
    return alt_hPa


def alt_to_pres(alt_hPa, h_m):
    """
    Converts a station altimeter and height to pressure.
    Follows the NOAA conversion found here:
    http://www.crh.noaa.gov/images/epz/wxcalc/stationPressure.pdf

    Input:
        alt_hPa - altimeter in hPa
        h_m - station elevation in meters

    Output:
        pres_hPa - station pressure in hPa
    """
    # The equation altimeter must be in inHg. Convert the presure hPa to inHg
    alt_inHg = 0.0295300 * alt_hPa

    pres_inHg = alt_inHg * ((288 - 0.0065 * h_m) / 288)**5.2561

    # Convert presure back to hPa
    pres_hPa = 33.8639 * pres_inHg

    return pres_hPa
