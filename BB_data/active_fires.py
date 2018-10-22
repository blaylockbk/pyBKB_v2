# Brian Blaylock
# May 24, 2018                                    Wildfire season in full swing

"""
Functions for getting data on active fires
"""

from datetime import datetime, timedelta
import urllib
import urllib2
import xml.etree.ElementTree as ET
import numpy as np
import os
import zipfile
import operator


def get_fires(DATE=datetime.utcnow(),
              max_size=3000000,
              max_containment=60,
              west_of=-100,
              limit_num=14,
              AK=False, HI=False,
              verbose=True):
    """
    Returns a dictionary of fire information from the Active Fire Mapping Program
        Modify the date as needed:
        https://fsapps.nwcg.gov/afm/data/lg_fire/lg_fire_info_2016-06-01.txt
    
    column names:
      0  INAME      - Incident Name
      1  INUM
      2  CAUSE
      3  REP_DATE   - reported date
      4  START_DATE - start date
      5  IMT_TYPE   - Incident Management Team Type. 5:local, 4:city, 3:state, 2:National+State, 1:National+State
      6  STATE
      7  AREA       - fire area in acres
      8  P_CNT      - Percent Contained
      9  EXP_CTN    - Expected Containment
      10 LAT        - latitude of fire start location
      11 LONG       - longitude of fire start location
      12 COUNTY

    Input:
        DATE     - Datetime object. Defaults to the current utc datetime.
        max_size - The maximum fire size in acres (hurricanes sometimes shown in the list).
        AK       - False: do not include fires from Alaska (default)
                   True:  include fires from Alaska
        HI       - False: do not include fires from Hawaii (default)
                   True:  include fires from Hawaii
        verbose  - True: print some stuff to the screen (default)
                   False: do not print some stuff
    """
    try:
        # Build URL and make request
        URL = 'https://fsapps.nwcg.gov/afm/data/lg_fire/lg_fire_info_%s.txt' % DATE.strftime('%Y-%m-%d')
        text = urllib2.urlopen(URL).readlines()
        if len(text)<2:
            # Maybe today's file isn't up yet. Try yesterdays...
            URL = 'https://fsapps.nwcg.gov/afm/data/lg_fire/lg_fire_info_%s.txt' % (DATE-timedelta(days=1)).strftime('%Y-%m-%d')
            text = urllib2.urlopen(URL)    
    except:
        # Maybe today's file isn't up yet. Try yesterdays...
        URL = 'https://fsapps.nwcg.gov/afm/data/lg_fire/lg_fire_info_%s.txt' % (DATE-timedelta(days=1)).strftime('%Y-%m-%d')
        text = urllib2.urlopen(URL)

    # Dictionary of all fires within defined limitations
    all_fires = {}
        
    # Fill the all_fires dictionary with each fire information
    for i, line in enumerate(text):
        F = line.split('\t')
        try: 
            float(F[7])
        except:
            continue # Sometimes there is an error in the data input. F[7] should be a number
        if i==0 or float(F[7]) > max_size:
            continue # Skip first line (header) and large incidents
        if AK is False and F[6] == 'Alaska':
            continue # Skip Alaska
        if HI is False and F[6] == 'Hawaii':
            continue # Skip Hawaii
        if F[8] == 'Not Reported' or int(F[8]) > max_containment:
                continue # Skip fires that are mostly contained or not specified
        if float(F[11]) > west_of:
            continue # Skip fires east of the west longitude
        all_fires[F[0]] = {'incident number': F[1],
                           'cause': F[2],
                           'report date': datetime.strptime(F[3], '%d-%b-%y') if F[3] != 'Not Reported' else 'Not Reported',
                           'start date': datetime.strptime(F[4], '%d-%b-%y') if F[4] != 'Not Reported' else 'Not Reported',
                           'IMT Type': int(F[5]) if F[5] not in ['',  'N'] else np.nan,
                           'state': F[6],
                           'area': float(F[7]),
                           'percent contained': int(F[8]) if F[8] != 'Not Reported' else 'Not Reported',
                           'expected containment': datetime.strptime(F[9], '%d-%b-%y')  if F[9] != 'Not Reported' else 'Not Reported',
                           'latitude': float(F[10]),
                           'longitude': float(F[11]),
                           'is MesoWest': False} # MesoWest station ID if you want to include the observed data in plot

    # For the list of fires that passed those checks, get some info about fire size
    sort_this = []
    for i in all_fires:
        F = all_fires[i]
        sort_this.append([i, F['IMT Type'], F['percent contained'], F['area']])

    # Sort the list by the fire size. (You can change the itemgetter to sort by IMT Type or percent contained if you want)
    sorted_by_size = np.array(sorted(sort_this, key=operator.itemgetter(3), reverse=True))
    # Get the names of the largest fires, number limited by limit_num
    names = sorted_by_size[:,0][:limit_num]

    # Initialize a dictionary to return
    return_this = {'DATE Requested':DATE,
                   'URL':URL,
                   'FIRES':{}}

    # Return fire info if it is included in the list of names we have sorted
    hardcoded_fires = ['COAL HOLLOW', 'CARR', 'COUGAR CREEK', 'GOLD HILL', 'BALD MOUNTAIN', 'POLE CREEK']
    for i in all_fires:
        if i in names or i in hardcoded_fires:
            return_this['FIRES'][i] = all_fires[i]

    if verbose:
        print 'Got fire data from Active Fire Mapping Program: %s' % URL       

    return return_this



def get_incidents(inctype="Wildfire", recent_days=3, limit_num=10, verbose=True):
    '''
    Return a dictionary of incidents from InciWeb XML RSS in the same format
    as get_fires().
        https://inciweb.nwcg.gov/feeds/rss/incidents/
    
    Note: InciWeb only includes lat/lon of each incident and does not include
          size of incident or location by state (thus you can't filter by fire
          size or remove Alaska and Hawaii incidents). If there are two
          fires with the same name, one incident will be overwitten.
    
    Input:
        inctype     - The type of incident.
                        'Wildfire' (default)
                        'Prescribed Fire'
                        'Flood'
                        'Burned Area Emergency Response'
        recent_days - Limit incidents to those occuring within the recent days.
                      Default is set to three for the most recent three days.
        limit_num   - Limit the number of incidents to return.
        verbose     - True: print some stuff to the screen (default)
    '''
    # Built URL and make request
    URL = 'https://inciweb.nwcg.gov/feeds/rss/incidents/'
    xml = urllib2.urlopen(URL)
    
    # Parse the xml data
    tree = ET.parse(xml)

    # Refer to the 'channel' branch and get all items
    items = [i for i in tree.find('channel') if i.tag == 'item']

    # Initialize the 
    return_this = {}

    for i in items:
        if len(return_this.keys()) >= limit_num:
            continue
        try:
            # Only grab fires updated in within recent_dates
            published = i.find('published').text
            DATE = datetime.strptime(published[5:22], "%d %b %Y %H:%M")
            if DATE > datetime.utcnow()-timedelta(days=recent_days):
                # Only grab requested incident type
                title = i.find('title').text
                if title.split(' ')[-1] == '(%s)' % inctype:
                    # Remove unnecessary names from title
                    title = title.replace(' Fire (%s)' % inctype, '')
                    title = title.replace(' Fire  (%s)' % inctype, '')
                    title = title.replace(' (%s)' % inctype, '')
                    title = title.replace('  (%s)' % inctype, '')
                    title = title.upper()
                    lat, lon = i.find('{http://www.georss.org/georss}point').text.split(' ')
                    return_this[title] = {'incident number': np.nan,
                                        'cause': np.nan,
                                        'report date': np.nan,
                                        'start date': np.nan,
                                        'IMT Type': np.nan,
                                        'state': np.nan,
                                        'area': np.nan,
                                        'percent contained': np.nan,
                                        'expected containment': np.nan,
                                        'latitude': float(lat),
                                        'longitude': float(lon),
                                        'is MesoWest': False} 
        except:
            print "XLM !ERROR!, had to skip an incident. Probably a bad lat/lon??"
            continue

    if verbose:
        print 'Got incident data from InciWeb: %s' % URL   

    return return_this


def download_latest_fire_shapefile(TYPE='fire'):
    """
    Download active fire shapefiles from the web.
    Points of active fire.
    Original Script from '/uufs/chpc.utah.edu/host/gl/oper/mesowest/fire/get_fire.csh'
    Input:
        TYPE - 'fire' or 'smoke'
    """
    URL = 'http://satepsanone.nesdis.noaa.gov/pub/FIRE/HMS/GIS/'
    SAVE = '/uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/fire_shapefiles/'
    NAME = 'latest_' + TYPE
    urllib.urlretrieve(URL+NAME+".dbf", SAVE+NAME+".dbf")
    urllib.urlretrieve(URL+NAME+".shp", SAVE+NAME+".shp")
    urllib.urlretrieve(URL+NAME+".shx", SAVE+NAME+".shx")


def download_fire_perimeter_shapefile(active=True):
    """
    Download active fire perimeter shapefiles.
    Original Script from '/uufs/chpc.utah.edu/host/gl/oper/mesowest/fire/get_perim.csh'
    
    Input:
        active - True for downloading the current, active fire perimeters
                 False for the current year
    """
    ## Download zip file
    URL = 'http://rmgsc.cr.usgs.gov/outgoing/GeoMAC/current_year_fire_data/current_year_all_states/'
    if active:
        NAME = 'active_perimeters_dd83.zip'
    else:
        NAME = 'perimeters_dd83.zip'
    SAVE = '/uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/fire_shapefiles/'
    urllib.urlretrieve(URL+NAME, SAVE+NAME)
    ## Unzip file
    zip_ref = zipfile.ZipFile(SAVE+NAME, 'r')
    zip_ref.extractall(SAVE)
    zip_ref.close()
    ## Remove zip file
    os.remove(SAVE+NAME)


if __name__ == "__main__":
    
    f = get_fires()
