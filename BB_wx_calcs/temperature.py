import numpy as np


# --- Temperature -------------------------------------------------------------
def K_to_C(T_K):
    """
    Convert temperature in Kelvin and return temperature in Celsius
    Input:
        T_K - Temperature in Kelvin
    """
    return T_K - 273.15

def C_to_K(T_C):
    """
    Converts celsius to Kelvin
    input: 
         temperature in celsius
    return:
         temperature in Kelvin
    """
    return T_C + 273.15