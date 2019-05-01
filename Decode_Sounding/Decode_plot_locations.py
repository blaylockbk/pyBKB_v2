## Brian Blaylock
## 29 August 2016

## An attempt to decode Sounding Data
## Copy of the C code on github: 
## https://github.com/Unidata/gempak/blob/bc574a37c27dd39027c570e49a26ba86d663aa3e/gempak/source/programs/gui/nsharp/decoder.c



import numpy as np
import matplotlib.pyplot as plt


# From the Manual FEDERAL METEOROLOGICAL HANDBOOK No. 3 RAWINSONDE AND PIBAL OBSERVATIONS
# Starting on page 121 (E-19)
# http://www.ofcm.gov/fmh3/pdf/00-entire-FMH3.pdf

table1845_elevation = {
                    'Code':[0,1,2,3,4,5,6,7,8,9],
                    'Units':['Not Used','Meters','Meters','Meters','Meters','Feet','Feet','Feet','Feet','Not Used'],
                    'Confidence':[None,'Excellent within 3 meters','Good within 10 meters','Fair within 20 meters','Poor more than 20 meters',
                                  'Excellent within 10 feet','Good within 30 feet','Fair within 60 feet','Poor more than 60 feet',None]
                    }
table3333_quadrant = {
                    'Code':[1,3,5,7],
                    'Latitude':['North','South','South','North'],
                    'Longitude':['East','East','West','West']
                    }


def barometric_equation_inv(heightb_m,tempb_k,presb_pa,prest_pa,Gamma=-0.0065):
    """The barometric equation models the change in pressure with height in 
    the atmosphere. This function returns altitude given 
    initial pressure and base altitude, and pressure change.

    INPUTS: 
    heightb_m (m):    {set to zero for sea level???}
    presb_pa (pa):    The base pressure {sea level, 101325 pa ???}
    {prest_pa (pa):   The pressure of the level???}
    tempb_k (K)  :    The base temperature {temperature at the level????}
    deltap_pa (m):    The pressure differential between the base height and the 
                      desired height {not even used in this function}

    Gamma [=-0.0065]: The atmospheric lapse rate. {Don't change this assumption}

    OUTPUTS
    heightt_m {}

    REFERENCE:
    http://en.wikipedia.org/wiki/Barometric_formula
    
    {Below 5000 m, the differences between this and the crude method, pres_to_hgt, are small}    
    """

    Rstar_a=8.31432       # Universal gas constant for air (N m /(mol K))
    grav=9.80665          # Gravity, m s^{-2}    
    m_a=28.9644e-3        # Mean molar mass of air(kg/mol)    
    
    return heightb_m + tempb_k*((presb_pa/prest_pa)**(Rstar_a*Gamma/(grav*m_a))-1)/Gamma

def pres_to_hgt(pres,temp):
    """
    Crude method to convert a pressure to height using the Hyposmetric Equation.
    Uses the temperature of the Level as the virtual temperature 
    when calculating the scale height, H.
    """
    Rd = 287 # J K-1 kg-1
    Tv = temp+273.15 # c
    g0 = 9.81 #ms-2
    H = Rd*Tv/g0 # m
    p0 = 1013.25 #hPa - pressure at sea level
    
    hgt = H*np.log(1+(p0-pres)/pres)
    return hgt #in meters


# Read the file (ha! there is no file named d.txt)
fname = 'f.txt'

def get_lat_lon(fname):
    
    month = 'August' #!! This is hard coded in    
    if fname=='q.txt' or fname=='r.txt':
        month='July'
    
    levelCode = [99,00,92,85,70,50,40,30,25,20,15,10]
    level = ['surface',1000,925,850,700,500,400,300,250,200,150,100]
    code = ['IIAA','IIBB','IICC','IIDD']
    codeKey = ['manditory','significant','manditory < 100 mb','significat < 100 mb']
    
    with open(fname) as f:
        content = f.readlines()
        # There. Now each line is an element of a list.
    
    
    Level = np.array([])
    Hgt = np.array([])
    Temp = np.array([])
    Dwpt = np.array([])
    Wspd = np.array([])
    Wdir = np.array([])
    
    #Significant Level Data (IIBB)
    sigLabel = np.array([])
    sigPress = np.array([])
    sigHgt = np.array([])
    sigTemp = np.array([])
    sigDwpt = np.array([])
    
    IIAA_data = np.array([])
    IIBB_data = np.array([])
    
    
    section = ''
        
    for i in content:
        a = i.split()
        
        #Header and Station Information
        if len(a)==3 and a[1].isalpha():
            # If line has three items and if the first item contains 
            # letters and numbers...
#            print "this line contains station information"
            station1 = a[0]
            station2 = a[1]
            date = a[2]
            day = date[:2]
            hour = date[2:]


#            print station1,station2,date
            
            
        
        if len(i)>1 and a[0] in code:
            # If the line contains stuff, and if the first item is
            # one of the codes...
            section = a[0]
            sectionName=codeKey[code.index(a[0])]
#            print section,sectionName
            
            # Station ID
            stnid = a[1]
    
            # Date Info (again)
            date99 = a[2]
            day99 = int(date99[0:2])
            if day99 > 50: 
                day99 = day99-50
                wind_units='knots'
            else:
                wind_units='m/s'
            hour99 = int(date99[2:4])
            
            #Latitude
            # first two number is 99
            lat99 = int(a[3][2:])/10.
    
            #Quadrant and Longitude
            quadrant99_code = int(a[4][0])
            quadrant99_str = table3333_quadrant['Latitude'][table3333_quadrant['Code'].index(quadrant99_code)]+' '+table3333_quadrant['Longitude'][table3333_quadrant['Code'].index(quadrant99_code)]                
            lon99 = int(a[4][1:])/10.*-1
            
            # Marsden Square Number (See Table 2590 in documentation)
            mar99 = a[5][0:3] #marsden square
            Ulat99 = a[5][3] #unit digit reported latitude
            Ulon99 = a[5][4] #unit digit reported longitude        
            
            # Elevation
            elevation99 = a[6][0:4]
            elevation99_code = int(a[6][-1])
            elevation99_units = table1845_elevation['Units'][table1845_elevation['Code'].index(elevation99_code)]
            elevation99_confidence = table1845_elevation['Confidence'][table1845_elevation['Code'].index(elevation99_code)]        
            
        # Manditory Data
        if section == 'IIAA' and len(i)>1 and (a[0].isdigit() or a[0]=='/////') and a[0][0:2] != '88' and a[0][0:2] != '77'and a[0][0:2] != '31':
            # the first element of this line contains only numbers
            # and is not tropopause level, a max wind data level, or regional level        
#            print "only contains numbers, put into clean data array"
            #fill the data array with the string of numbers in each element
            for d in a:        
                IIAA_data = np.append(IIAA_data,d)
        # Significant Levels
        if section == 'IIBB' and len(i)>1 and (a[0].isdigit() or a[0]=='/////') and a[0][0:2] != '88' and a[0][0:2] != '77'and a[0][0:2] != '31':
            # the first element of this line contains only numbers
            # and is not tropopause level, a max wind data level, or regional level        
#            print "only contains numbers, put into clean data array"
            #fill the data array with the string of numbers in each element
            for d in a:        
                IIBB_data = np.append(IIBB_data,d)
       
         
#    print '-->',Level
    for l in np.arange(0,len(IIAA_data),3):
            # Each level of data is in a triplet. 
            # The first is the pressure level, 
            # Second is the temperature and humidity
            # Third is the wind speed and direction         
            triplet = IIAA_data[l:l+3]
            #print triplet
            if int(triplet[0][:2])==99:
                #the next three numbers are the station pressure
                surf_pres = int(triplet[0][2:])
                if surf_pres < 100:
                    surf_pres = surf_pres+1000
                Level = np.append(Level,surf_pres)
                #convert to an elevation and store
                Elevation = pres_to_hgt(surf_pres,float(triplet[1][:3])/10)
                
            else:
                if int(triplet[0][:2])==0:
                    Level = np.append(Level,1000)
                else:
                    Level = np.append(Level,int(triplet[0][:2])*10)
                Elevation = int(triplet[0][2:])
            
            if len(Hgt)>0:
                # The elevation is recorded in meteres *until* 
#                print "SHOW THE LEVEL",Level[-1], Elevation
                #if Level[-1]<=500: # then eleveation is in decameters
                #    print Elevation
                #    Elevation = Elevation *10 #because the elevation is now in decameters
                #    print Elevation
                #while Hgt[-1]>Elevation:
                #    Elevation = Elevation + 1000
                
                ## Sort through all this crazyness: make guesses on the standard atmosphere            
                if Level[-1]==850:
                    Elevation = Elevation +1000
                if Level[-1]==700:
                    Elevation = Elevation +3000
                if Level[-1]<=500:
                    Elevation = Elevation*10 #height is in decameters
                if Level[-1]<=250:
                    Elevation = Elevation+10000
#                print Elevation
            Hgt = np.append(Hgt,Elevation)
            
            if triplet[1].isdigit()==False:      
                Temp = np.append(Temp,np.nan)
                Dwpt = np.append(Dwpt,np.nan)
            else:
                Temp = np.append(Temp,float(triplet[1][:3])/10)
                Dwpt = np.append(Dwpt,float(triplet[1][:3])/10-float(triplet[1][3:])/10)
            if triplet[2].isdigit()==False:
                Wdir = np.append(Wdir,np.nan)
                Wspd = np.append(Wspd,np.nan)
            else:
                Wdir = np.append(Wdir,int(triplet[2][:3]))
                Wspd = np.append(Wspd,int(triplet[2][3:]))
    
    
    ##Need to fix this line here....the significant levels data is a pair (no wind data)
    ## Significant Levels
    for l in np.arange(0,len(IIBB_data),2):
            # Each level of data is in a pair. 
            # The first is the elevation level, 
            # Second is the temperature and humidity (no wind data)
            if IIBB_data[l] in ['21212', '31313','41414']:
                break     # I'm not sure what these labels mean yet   
            pair = IIBB_data[l:l+2]
            #print pair
           
            if int(pair[0][0:2]) in [11,22,33,44,55,66,77,88,99]:        
                sigLabel = np.append(sigLabel,int(pair[0][:2]))        
                press = int(pair[0][2:])      
                if press < 50:
                    press = press+1000 #because the 1000 digit was omitted
                sigPress = np.append(sigPress,press)
                            
                if pair[1]=='/////':
                    temp = np.nan
                    dwpt = np.nan
                    sigTemp = np.append(sigTemp,temp)
                    sigDwpt = np.append(sigDwpt,dwpt)
                else:
                    temp = float(pair[1][:3])/10
                    dwpt = float(pair[1][:3])/10-float(triplet[1][3:])/10
                    sigTemp = np.append(sigTemp,temp)
                    sigDwpt = np.append(sigDwpt,dwpt)
                    
                sigHgt= np.append(sigHgt,pres_to_hgt(press,temp))

    return lat99,lon99

if __name__=='__main__':
    
    lats = np.array([])
    lons = np.array([])
    fs = np.array([])
    files = 'befghijklmnopqrst'
    for f in files:
        try:    
            lat,lon = get_lat_lon(f+'.txt')
            lats = np.append(lats,lat)
            lons = np.append(lons,lon)
            fs = np.append(fs,f)
        except:
            print 'skipped',f
        
    # Plot a basemap
    ## Create Basemap
    top_right_lat = 50
    top_right_lon = -105
    bot_left_lat = 30
    bot_left_lon = -125
    from mpl_toolkits.basemap import Basemap
    m = Basemap(resolution='i',projection='cyl',\
            llcrnrlon=bot_left_lon,llcrnrlat=bot_left_lat,\
            urcrnrlon=top_right_lon,urcrnrlat=top_right_lat,)
    m.drawcoastlines()
    m.drawcountries()
    m.drawstates()
    
    m.scatter(lons,lats,facecolor='none',edgecolors='darkred',s=250)
    for i in range(0,len(lons)):
        num1 = np.random.random(1)*np.random.random(1)
        num2 = np.random.random(1)*np.random.random(1)
        plt.text(lons[i]+num1,lats[i]+num2,fs[i])
        print lons[i],lats[i],fs[i],'\t'
    
    
    
    