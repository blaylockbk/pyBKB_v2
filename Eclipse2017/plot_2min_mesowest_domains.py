# Brian Blaylock
# August 15, 2017

"""
Plot Eclipse Path with MesoWest Solar Radiation
"""
import matplotlib as mpl
mpl.use('Agg')#required for the CRON job. Says "do not open plot in a window"??
import numpy as np
from datetime import datetime, timedelta, date
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2/')
from BB_MesoWest.MesoWest_radius import get_mesowest_radius
from BB_basemap.draw_maps import draw_CONUS_cyl_map, draw_CONUS_HRRR_map
from BB_downloads.HRRR_S3 import get_hrrr_variable

import matplotlib as mpl
mpl.rcParams['figure.subplot.wspace'] = 0.05
mpl.rcParams['figure.subplot.hspace'] = 0.05

# Read Eclipse path file
# Names: 'year', 'month', 'day', 'hour', 'min', 'NorthLatitude', 'NorthLongitude', 'SouthLatitude', 'SouthLongitude', 'CenterLatitude', 'CenterLongitude', 'MS_Ratio', 'Sun_Alt', 'Sun_Azm', 'Path_Width', 'Central_Duration'
E = np.genfromtxt('eclipsePath.csv', dtype=None, delimiter=',', names=True)


# Eclipse Datetimes
DATES = [datetime(E['year'][i], E['month'][i], E['day'][i], E['hour'][i], E['min'][i]) for i in range(len(E['year']))]
num = len(DATES)

# Eclipse Path
# North totality bound
Nlat = [int(i[0:2]) + float(i[3:7])/60 for i in E['NorthLatitude']]
Nlon = [-int(i[0:3]) - float(i[4:8])/60 for i in E['NorthLongitude']]
# South totality bound
Slat = [int(i[0:2]) + float(i[3:7])/60 for i in E['SouthLatitude']]
Slon = [-int(i[0:3]) - float(i[4:8])/60 for i in E['SouthLongitude']]
# Center totality bound
Clat = [int(i[0:2]) + float(i[3:7])/60 for i in E['CenterLatitude']]
Clon = [-int(i[0:3]) - float(i[4:8])/60 for i in E['CenterLongitude']]

# Draw CONUS Map
f = plt.figure(1, figsize=[16, 4])
ax1 = f.add_subplot(131)
m = draw_CONUS_HRRR_map()
m.drawmapboundary(fill_color='#323232')
m.drawstates()
m.drawcountries()
m.drawcoastlines()

Nx, Ny = m(Nlon, Nlat)
Sx, Sy = m(Slon, Slat)
Cx, Cy = m(Clon, Clat)

plt.plot(Nx, Ny)
plt.plot(Sx, Sy)
plt.plot(Cx, Cy)

# Draw WEST Map
plt.figure(2)
bot_left_lat  = 26
bot_left_lon  = -127
top_right_lat = 50
top_right_lon = -100
#
mW = Basemap(resolution='i', projection='cyl', area_thresh=2000, \
             llcrnrlon=bot_left_lon, llcrnrlat=bot_left_lat, \
             urcrnrlon=top_right_lon, urcrnrlat=top_right_lat)
mW.drawmapboundary(fill_color='#323232')
mW.drawstates()
mW.drawcountries()
mW.drawcoastlines()

NxW, NyW = mW(Nlon, Nlat)
SxW, SyW = mW(Slon, Slat)
CxW, CyW = mW(Clon, Clat)

plt.plot(NxW, NyW)
plt.plot(SxW, SyW)
plt.plot(CxW, CyW)

# Draw EAST Map
plt.figure(3)
bot_left_lat  = 25
bot_left_lon  = -100
top_right_lat = 50
top_right_lon = -65
#
mE = Basemap(resolution='i', projection='cyl', area_thresh=2000, \
             llcrnrlon=bot_left_lon, llcrnrlat=bot_left_lat, \
             urcrnrlon=top_right_lon, urcrnrlat=top_right_lat)
mE.drawmapboundary(fill_color='#323232')
mE.drawstates()
mE.drawcountries()
mE.drawcoastlines()

NxE, NyE = mE(Nlon, Nlat)
SxE, SyE = mE(Slon, Slat)
CxE, CyE = mE(Clon, Clat)

plt.plot(NxE, NyE)
plt.plot(SxE, SyE)
plt.plot(CxE, CyE)

# Draw UT/ID Map
plt.figure(4)
bot_left_lat  = 38.5
bot_left_lon  = -116
top_right_lat = 45.5
top_right_lon = -107
#
mU = Basemap(resolution='i', projection='cyl', area_thresh=2000, \
             llcrnrlon=bot_left_lon, llcrnrlat=bot_left_lat, \
             urcrnrlon=top_right_lon, urcrnrlat=top_right_lat)
mU.drawmapboundary(fill_color='#323232')
mU.drawstates()
mU.drawcountries()
mU.drawcoastlines()

NxU, NyU = mU(Nlon, Nlat)
SxU, SyU = mU(Slon, Slat)
CxU, CyU = mU(Clon, Clat)

plt.plot(NxU, NyU)
plt.plot(SxU, SyU)
plt.plot(CxU, CyU)


within = 4
SAVEDIR = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/PhD/Eclipse20170821/'
days_till_eclipse = (date(2017, 8, 21) - date.today()).days

for i in range(num):
           
    attime = DATES[i] - timedelta(days=days_till_eclipse)
    print 'request mesowest', attime, '    (%s/%s)' % (i, num)
    a = get_mesowest_radius(attime, within, extra='&status=active',
                            variables='solar_radiation',
                            verbose=True)

    x, y = m(a['LON'], a['LAT'])
    xW, yW = mW(a['LON'], a['LAT'])
    xE, yE = mE(a['LON'], a['LAT'])
    xU, yU = mE(a['LON'], a['LAT'])

    # Plot CONUS
    plt.figure(1)
    Epoint = plt.scatter(Cx[i], Cy[i], c='r', s=90)
    MWpoints = plt.scatter(x, y,
                           c=a['solar_radiation'],
                           cmap='magma',
                           vmin=100, vmax=1000,
                           linewidths=0)
    if i == 0:
        cb = plt.colorbar(orientation='horizontal', pad=.01, shrink=.85, extend='both')
        cb.set_label(r'Solar Radiation (W m$\mathregular{^{-2}}$)')
        
    plt.title('Eclipse: %s\nMesoWest: %s' % (DATES[i], attime))
    plt.savefig(SAVEDIR+'CONUS/CONUS_%s.png' % attime.strftime('%Y-%m-%d_%H%M'), bbox_inches='tight')
    Epoint.remove()
    MWpoints.remove()

    # Plot WEST
    plt.figure(2)
    Epoint = plt.scatter(CxW[i], CyW[i], c='r', s=100)
    MWpoints = plt.scatter(xW, yW,
                           c=a['solar_radiation'],
                           cmap='magma',
                           vmin=100, vmax=1000,
                           linewidths=0)
    if i == 0:
        cb = plt.colorbar(orientation='horizontal', pad=.01, shrink=.85, extend='both')
        cb.set_label(r'Solar Radiation (W m$\mathregular{^{-2}}$)')
        
    plt.title('Eclipse: %s\nMesoWest: %s' % (DATES[i], attime))
    plt.savefig(SAVEDIR+'WEST/WEST_%s.png' % attime.strftime('%Y-%m-%d_%H%M'), bbox_inches='tight')
    Epoint.remove()
    MWpoints.remove()

    # Plot EAST
    plt.figure(3)
    Epoint = plt.scatter(CxE[i], CyE[i], c='r', s=100)
    MWpoints = plt.scatter(xE, yE,
                           c=a['solar_radiation'],
                           cmap='magma',
                           vmin=100, vmax=1000,
                           linewidths=0)
    if i == 0:
        cb = plt.colorbar(orientation='horizontal', pad=.01, shrink=.85, extend='both')
        cb.set_label(r'Solar Radiation (W m$\mathregular{^{-2}}$)')
        
    plt.title('Eclipse: %s\nMesoWest: %s' % (DATES[i], attime))
    plt.savefig(SAVEDIR+'EAST/EAST_%s.png' % attime.strftime('%Y-%m-%d_%H%M'), bbox_inches='tight')
    Epoint.remove()
    MWpoints.remove()

    # Plot UT/ID
    plt.figure(4)
    Epoint = plt.scatter(CxU[i], CyU[i], c='r', s=800)
    MWpoints = plt.scatter(xU, yU,
                           c=a['solar_radiation'],
                           cmap='magma',
                           vmin=100, vmax=1000,
                           linewidths=0)
    if i == 0:
        cb = plt.colorbar(orientation='horizontal', pad=.01, shrink=.8, extend='both')
        cb.set_label(r'Solar Radiation (W m$\mathregular{^{-2}}$)')
        
    plt.title('Eclipse: %s\nMesoWest: %s' % (DATES[i], attime))
    plt.savefig(SAVEDIR+'UTID/UTID_%s.png' % attime.strftime('%Y-%m-%d_%H%M'), bbox_inches='tight')
    Epoint.remove()
    MWpoints.remove()


# Create animated gifs of the files on the eclipse day
if DATES[0].day == 21:
    import os
    os.system('convert -delay 40 '+SAVEDIR+'UTID/*2017-08-21*.png '+SAVEDIR+'UTID/Animated.gif')
    os.system('convert -delay 40 '+SAVEDIR+'EAST/*2017-08-21*.png '+SAVEDIR+'EAST/Animated.gif')
    os.system('convert -delay 40 '+SAVEDIR+'WEST/*2017-08-21*.png '+SAVEDIR+'WEST/Animated.gif')
    os.system('convert -delay 40 '+SAVEDIR+'CONUS/*2017-08-21*.png '+SAVEDIR+'CONUS/Animated.gif')
