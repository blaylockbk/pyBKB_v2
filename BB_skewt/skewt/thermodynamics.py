from numpy import interp,pi,cos,sin,arctan,sqrt,linspace,min,exp,log,where

__version__="1.1.0"
__author__ = 'Thomas Chubb'
__mail__ = 'thomas.chubb@monash.edu'

#-----------------------------------------------------------------------
# Here we go. A set of functions that I use from time to time to calculate 
# the basic stuff that I'm sick of doing over and over! I'm going to 
# endeavour to include references and global constants to make it all nice 
# and legible.
#-----------------------------------------------------------------------

Rs_da=287.05          # Specific gas const for dry air, J kg^{-1} K^{-1}
Rs_v=461.51           # Specific gas const for water vapour, J kg^{-1} K^{-1}
Cp_da=1004.6          # Specific heat at constant pressure for dry air
Cv_da=719.            # Specific heat at constant volume for dry air
Cp_v=1870.            # Specific heat at constant pressure for water vapour
Cv_v=1410.            # Specific heat at constant volume for water vapour
Cp_lw=4218	          # Specific heat at constant pressure for liquid water
Epsilon=0.622         # Epsilon=Rs_da/Rs_v; The ratio of the gas constants
degCtoK=273.15        # Temperature offset between K and C (deg C)
rho_w=1000.           # Liquid Water density kg m^{-3}
grav=9.80665          # Gravity, m s^{-2}
Lv=2.5e6              # Latent Heat of vaporisation 
boltzmann=5.67e-8     # Stefan-Boltzmann constant
mv=18.0153e-3         # Mean molar mass of water vapor(kg/mol)
m_a=28.9644e-3        # Mean molar mass of air(kg/mol)
Rstar_a=8.31432       # Universal gas constant for air (N m /(mol K))



def barometric_equation(presb_pa,tempb_k,deltah_m,Gamma=-0.0065):
    """The barometric equation models the change in pressure with 
    height in the atmosphere.

    INPUTS: 
    presb_k (pa):     The base pressure
    tempb_k (K):      The base temperature
    deltah_m (m):     The height differential between the base height and the 
                      desired height
    Gamma [=-0.0065]: The atmospheric lapse rate

    OUTPUTS
    pres (pa):        Pressure at the requested level

    REFERENCE:
    http://en.wikipedia.org/wiki/Barometric_formula
    """

    return presb_pa*(tempb_k/(tempb_k+Gamma*deltah_m))**(grav*m_a/(Rstar_a*Gamma))

def barometric_equation_inv(heightb_m,tempb_k,presb_pa,prest_pa,Gamma=-0.0065):
    """The barometric equation models the change in pressure with height in 
    the atmosphere. This function returns altitude given 
    initial pressure and base altitude, and pressure change.

    INPUTS: 
    heightb_m (m):
    presb_pa (pa):    The base pressure
    tempb_k (K)  :    The base temperature
    deltap_pa (m):    The pressure differential between the base height and the 
                      desired height

    Gamma [=-0.0065]: The atmospheric lapse rate

    OUTPUTS
    heightt_m

    REFERENCE:
    http://en.wikipedia.org/wiki/Barometric_formula
    """


    return heightb_m + tempb_k*((presb_pa/prest_pa)**(Rstar_a*Gamma/(grav*m_a))-1)/Gamma

def Theta(tempk,pres,pref=100000.):
    """Potential Temperature

    INPUTS: 
    tempk (K)
    pres (Pa)
    pref: Reference pressure (default 100000 Pa)

    OUTPUTS: Theta (K)

    Source: Wikipedia
    Prints a warning if a pressure value below 2000 Pa input, to ensure
    that the units were input correctly.
    """

    try:
        minpres=min(pres)
    except TypeError:
        minpres=pres

    if minpres<2000:
        print "WARNING: P<2000 Pa; did you input a value in hPa?"

    return tempk*(pref/pres)**(Rs_da/Cp_da)

def TempK(theta,pres,pref=100000.):
    """Inverts Theta function."""

    try:
        minpres=min(pres)
    except TypeError:
        minpres=pres

    if minpres<2000:
        print "WARNING: P<2000 Pa; did you input a value in hPa?"

    return theta*(pres/pref)**(Rs_da/Cp_da)

def ThetaE(tempk, pres, e):
    """Calculate Equivalent Potential Temperature
        for lowest model level (or surface)

    INPUTS:
    tempk:      Temperature [K] 
    pres:       Pressure [Pa]
    e:          Water vapour partial pressure [Pa]

    OUTPUTS:
    theta_e:    equivalent potential temperature

    References:
    Eq. (9.40) from Holton (2004)
    Eq. (22) from Bolton (1980)
    Michael P. Byrne and Paul A. O'Gorman (2013), 'Land-Ocean Warming
    Contrast over a Wide Range of Climates: Convective Quasi-Equilibrium
    Theory and Idealized Simulations', J. Climate """

    # tempc
    tempc=tempk-degCtoK
    # Calculate theta
    theta=Theta(tempk,pres)


    # T_lcl formula needs RH
    es=VaporPressure(tempc)
    RH=100.*e/es

    # theta_e needs q (water vapour mixing ratio)
    qv=MixRatio(e,pres)

    # Calculate the temp at the Lifting Condensation Level
    T_lcl = ( (tempk-55)*2840 / (2840-(log(RH/100)*(tempk-55)))) + 55

    # print "T_lcl :%.3f"%T_lcl

    #### DEBUG STUFF ####
    theta_l=tempk*(100000./(pres-e))**(Rs_da/Cp_da)*(tempk/T_lcl)**(0.28*qv)
    # print "theta_L: %.3f"%theta_l

    # Calculate ThetaE
    theta_e = theta_l * exp((Lv * qv) / (Cp_da * T_lcl))

    return theta_e

def ThetaE_Bolton(tempk, pres, e, pref=100000.):
    """Theta_E following Bolton (1980)
    INPUTS:
    tempk:      Temperature [K] 
    pres:       Pressure [Pa]
    e:          Water vapour partial pressure [Pa]

    See http://en.wikipedia.org/wiki/Equivalent_potential_temperature
    """

    # Preliminary:
    T=tempk
    qv=MixRatio(e,pres)
    Td=DewPoint(e)+degCtoK
    kappa_d=Rs_da/Cp_da

    # Calculate TL (temp [K] at LCL):
    TL=56+((Td-56.)**-1+(log(T/Td)/800.))**(-1)

    # print "TL: %.3f"%TL

    # Calculate Theta_L:
    thetaL=T*(pref/(pres-e))**kappa_d*(T/TL)**(0.28*qv)

    # print "theta_L: %.3f"%thetaL

    # put it all together to get ThetaE
    thetaE=thetaL*exp((3036./TL-0.78)*qv*(1+0.448*qv))

    return thetaE

def ThetaV(tempk,pres,e):
    """Virtual Potential Temperature
    
    INPUTS
    tempk (K)
    pres (Pa)
    e: Water vapour pressure (Pa) (Optional)

    OUTPUTS
    theta_v    : Virtual potential temperature
    """ 

    mixr=MixRatio(e,pres)
    theta=Theta(tempk,pres)

    return theta*(1+mixr/Epsilon)/(1+mixr)

def GammaW(tempk,pres):
    """Function to calculate the moist adiabatic lapse rate (deg C/Pa) based
    on the environmental temperature and pressure.

    INPUTS:
    tempk (K)
    pres (Pa)
    RH (%)

    RETURNS:
    GammaW: The moist adiabatic lapse rate (Deg C/Pa)
    REFERENCE: 
    http://glossary.ametsoc.org/wiki/Moist-adiabatic_lapse_rate
    (Note that I multiply by 1/(grav*rho) to give MALR in deg/Pa)

    """

    tempc=tempk-degCtoK
    es=VaporPressure(tempc)
    ws=MixRatio(es,pres)

    # tempv=VirtualTempFromMixR(tempk,ws)
    tempv=VirtualTemp(tempk,pres,es)
    latent=Latentc(tempc)

    Rho=pres/(Rs_da*tempv)

    # This is the previous implementation:
    # A=1.0+latent*ws/(Rs_da*tempk)
    # B=1.0+Epsilon*latent*latent*ws/(Cp_da*Rs_da*tempk*tempk)
    # Gamma=(A/B)/(Cp_da*Rho)

    # This is algebraically identical but a little clearer:
    A=-1.*(1.0+latent*ws/(Rs_da*tempk))
    B=Rho*(Cp_da+Epsilon*latent*latent*ws/(Rs_da*tempk*tempk))
    Gamma=A/B

    return Gamma

def DensHumid(tempk,pres,e):
    """Density of moist air.
    This is a bit more explicit and less confusing than the method below.

    INPUTS:
    tempk: Temperature (K)
    pres: static pressure (Pa)
    mixr: mixing ratio (kg/kg)

    OUTPUTS: 
    rho_air (kg/m^3)

    SOURCE: http://en.wikipedia.org/wiki/Density_of_air
    """

    pres_da=pres-e
    rho_da=pres_da/(Rs_da*tempk)
    rho_wv=e/(Rs_v*tempk)

    return rho_da+rho_wv


def Density(tempk,pres,mixr):
    """Density of moist air

    INPUTS:
    tempk: Temperature (K)
    pres: static pressure (Pa)
    mixr: mixing ratio (kg/kg)

    OUTPUTS: 
    rho_air (kg/m^3)
    """
    
    virtualT=VirtualTempFromMixR(tempk,mixr)
    return pres/(Rs_da*virtualT)


def VirtualTemp(tempk,pres,e):
    """Virtual Temperature

    INPUTS:
    tempk: Temperature (K)
    e: vapour pressure (Pa)
    p: static pressure (Pa)

    OUTPUTS:
    tempv: Virtual temperature (K)

    SOURCE: hmmmm (Wikipedia)."""

    tempvk=tempk/(1-(e/pres)*(1-Epsilon))
    return tempvk
    

def VirtualTempFromMixR(tempk,mixr):
    """Virtual Temperature

    INPUTS:
    tempk: Temperature (K)
    mixr: Mixing Ratio (kg/kg)

    OUTPUTS:
    tempv: Virtual temperature (K)

    SOURCE: hmmmm (Wikipedia). This is an approximation
    based on a m
    """

    return tempk*(1.0+0.6*mixr)

def Latentc(tempc):
    """Latent heat of condensation (vapourisation)

    INPUTS:
    tempc (C)

    OUTPUTS:
    L_w (J/kg)

    SOURCE:
    http://en.wikipedia.org/wiki/Latent_heat#Latent_heat_for_condensation_of_water
    """
   
    return 1000*(2500.8 - 2.36*tempc + 0.0016*tempc**2 - 0.00006*tempc**3)

def VaporPressure(tempc,phase="liquid"):
    """Water vapor pressure over liquid water or ice.

    INPUTS: 
    tempc: (C) OR dwpt (C), if SATURATION vapour pressure is desired.
    phase: ['liquid'],'ice'. If 'liquid', do simple dew point. If 'ice',
    return saturation vapour pressure as follows:

    Tc>=0: es = es_liquid
    Tc <0: es = es_ice

   
    RETURNS: e_sat  (Pa)
    
    SOURCE: http://cires.colorado.edu/~voemel/vp.html (#2:
    CIMO guide (WMO 2008), modified to return values in Pa)
    
    This formulation is chosen because of its appealing simplicity, 
    but it performs very well with respect to the reference forms
    at temperatures above -40 C. At some point I'll implement Goff-Gratch
    (from the same resource).
    """

    over_liquid=6.112*exp(17.67*tempc/(tempc+243.12))*100.
    over_ice=6.112*exp(22.46*tempc/(tempc+272.62))*100.
    # return where(tempc<0,over_ice,over_liquid)

    if phase=="liquid":
        # return 6.112*exp(17.67*tempc/(tempc+243.12))*100.
        return over_liquid
    elif phase=="ice":
        # return 6.112*exp(22.46*tempc/(tempc+272.62))*100.
        return where(tempc<0,over_ice,over_liquid)
    else:
        raise NotImplementedError

def SatVap(dwpt,phase="liquid"):
    """This function is deprecated, return ouput from VaporPres"""

    print "WARNING: This function is deprecated, please use VaporPressure()"+\
            " instead, with dwpt as argument"
    return VaporPressure(dwpt,phase)

def MixRatio(e,p):
    """Mixing ratio of water vapour
    INPUTS
    e (Pa) Water vapor pressure
    p (Pa) Ambient pressure
          
    RETURNS
    qv (kg kg^-1) Water vapor mixing ratio`
    """

    return Epsilon*e/(p-e)

def MixR2VaporPress(qv,p):
    """Return Vapor Pressure given Mixing Ratio and Pressure
    INPUTS
    qv (kg kg^-1) Water vapor mixing ratio`
    p (Pa) Ambient pressure
          
    RETURNS
    e (Pa) Water vapor pressure
    """

    return qv*p/(Epsilon+qv)


def DewPoint(e):
    """ Use Bolton's (1980, MWR, p1047) formulae to find tdew.
    INPUTS:
    e (Pa) Water Vapor Pressure
    OUTPUTS:
    Td (C) 
      """

    ln_ratio=log(e/611.2)
    Td=((17.67-ln_ratio)*degCtoK+243.5*ln_ratio)/(17.67-ln_ratio)
    return Td-degCtoK

def WetBulb(tempc,RH):
    """Stull (2011): Wet-Bulb Temperature from Relative Humidity and Air
    Temperature.
    INPUTS:
    tempc (C)
    RH (%)
    OUTPUTS:
    tempwb (C)
    """

    Tw=tempc*arctan(0.151977*(RH+8.313659)**0.5)+\
	    arctan(tempc+RH) - arctan(RH-1.676331)+\
	    0.00391838*RH**1.5*arctan(0.023101*RH)-\
	    4.686035

    return Tw
