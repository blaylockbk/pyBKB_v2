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


def get_fires(DATE=datetime.utcnow(),
              min_size=1000, max_size=3000000,
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
        min_size - The minimum fire size in acres.
        max_size - The maximum fire size in acres (hurricanes sometimes shown in the list).
        AK       - False: do not include fires from Alaska (default)
                   True:  include fires from Alaska
        HI       - False: do not include fires from Hawaii (default)
                   True:  include fires from Hawaii
        verbose  - True: print some stuff to the screen (default)
                   False: do not print some stuff
    """
    # Build URL and make request
    URL = 'https://fsapps.nwcg.gov/afm/data/lg_fire/lg_fire_info_%s.txt' % DATE.strftime('%Y-%m-%d')
    text = urllib2.urlopen(URL)
    if verbose:
        print 'Got fire data from Active Fire Mapping Program: %s' % URL       

    # Initialize the return dictionary
    return_this = {'DATE Requested':DATE,
                   'URL':URL,
                   'FIRES':{}}

    # Fill the FIRES key with a dictionary of each fire information
    for i, line in enumerate(text):
        F = line.split('\t')
        if i==0 or int(F[7]) < min_size or int(F[7]) > max_size:
            continue # Skip header, small fires, and large fires
        if AK is False and F[6] == 'Alaska':
            continue # Skip Alaska
        if HI is False and F[6] == 'Hawaii':
            continue # Skip Hawaii

        return_this['FIRES'][F[0]] = {'incident number': F[1],
                                      'cause': F[2],
                                      'report date': datetime.strptime(F[3], '%d-%b-%y') if F[3] != 'Not Reported' else 'Not Reported',
                                      'start date': datetime.strptime(F[4], '%d-%b-%y') if F[4] != 'Not Reported' else 'Not Reported',
                                      'IMT Type': int(F[5]) if F[5] != '' else 'Not Reported',
                                      'state': F[6],
                                      'area': int(F[7]),
                                      'percent contained': F[8],
                                      'expected containment': datetime.strptime(F[9], '%d-%b-%y')  if F[9] != 'Not Reported' else 'Not Reported',
                                      'latitude': float(F[10]),
                                      'longitude': float(F[11]),
                                      'is MesoWest': False} # MesoWest station ID if you want to include the observed data in plot
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
    if verbose:
        print 'Got incident data from InciWeb: %s' % URL   

    # Parse the xml data
    tree = ET.parse(xml)

    # Refer to the 'channel' branch and get all items
    items = [i for i in tree.find('channel') if i.tag == 'item']

    # Initialize the 
    return_this = {}

    for i in items:
        if len(return_this.keys()) >= limit_num:
            continue
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
    
    get_fires()