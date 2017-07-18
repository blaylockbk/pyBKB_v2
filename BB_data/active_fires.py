# Brian Blaylock
# June 27, 2017                                  Wildfire season in full swing

"""
Functions for getting data on active fires
"""

from datetime import datetime, timedelta
import urllib2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, HourLocator

def get_fires(DATE=datetime.now(), min_size=1000, AK=False, HI=False):
    """
    Returns a dictionary of fires and information from this webpage:
    https://fsapps.nwcg.gov/afm/data/lg_fire/lg_fire_info_2016-06-01.txt
    Modify the date as needed.
    column names:
      0  INAME - Incident Name
      1  INUM
      2  CAUSE
      3  REP_DATE - reported date
      4  START_DATE - start date
      5  IMT_TYPE
      6  STATE
      7  AREA - fire area in acres
      8  P_CNT - Percent Contained
      9  EXP_CTN - Expected Containment
      10 LAT - latitude
      11 LONG - longitude
      12 COUNTY

    Input:
        date - a python datetime object. Defaults to the current date.
        min_size - the minimum fire size to include in the dictionary
        AK - Include fires from Alaska (default False)
        HI - Include fires from Hawaii (default False)

    Return:
        a dictionary of the data for each fire. Fire name is each key.
    """

    # Conver date for URL request
    date = datetime.strftime(DATE, '%Y-%m-%d')
    url = 'https://fsapps.nwcg.gov/afm/data/lg_fire/lg_fire_info_%s.txt' % date
    text = urllib2.urlopen(url)
    fires = np.genfromtxt(text, names=True, dtype=None, delimiter='\t')

    return_this = {'DATE':DATE, 'URL':url}

    for F in range(0, len(fires)):
        line = fires[F]

        # Skip small acreage and Alaska and Hawaii
        if line[7] < min_size:
            continue
        elif AK is False and line[6] == 'Alaska':
            continue
        elif HI is False and line[6] == 'Hawaii':
            continue

        else:
            return_this[line[0]] = {'incident number': line[1],
                                    'cause': line[2],
                                    'report date': datetime.strptime(line[3], '%d-%b-%y') if line[3] != 'Not Reported' else 'Not Reported',
                                    'start date': datetime.strptime(line[4], '%d-%b-%y') if line[4] != 'Not Reported' else 'Not Reported',
                                    'IMT_TYPE': line[5],
                                    'state': line[6],
                                    'area': line[7],
                                    'percent contained': line[8],
                                    'expected containment': datetime.strptime(line[9], '%d-%b-%y')  if line[9] != 'Not Reported' else 'Not Reported',
                                    'latitude': float(line[10]),
                                    'longitude': float(line[11]),
                                   }
    return return_this


if __name__ == "__main__":
    F = get_fires()

    # =======================================
    # Plot fire size over time
    date = datetime(2016, 6, 15)
    eDate = datetime(2016, 11, 15)
    fire = 'PIONEER'
    size = []
    dates = []
    containment = []
    while date < eDate:
        try:
            F = get_fires(DATE=date)
            if fire in F.keys():
                size.append(F[fire]['area'])
                dates.append(date)
                if F[fire]['percent contained'] != 'Not Reported':
                    containment.append(float(F[fire]['percent contained']))
                else:
                    containment.append(np.nan)
            print date
        except:
            size.append(np.nan)
            dates.append(date)
            containment.append(np.nan)
        date += timedelta(days=1)
        
    fig, ax1 = plt.subplots()
    ax1.bar(dates, containment, 1, color='r', zorder=1)
    # Make the y-axis label, ticks and tick labels match the line color.
    ax1.set_ylabel('Percent Contained (%)')
    ax2 = ax1.twinx()
    ax2.set_ylabel('Burned Acres')
    ax2.plot(dates, size, 'darkorange', linewidth=4, zorder=2)
    fig.tight_layout()
    plt.title(fire)
    dateFmt = DateFormatter('%b %d\n%Y')
    ax2.xaxis.set_major_formatter(dateFmt)
    plt.show()
